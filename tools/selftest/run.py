#!/usr/bin/env python3
"""Build and run the temporary Caelavi runtime MOD in isolated RimWorld data.

Only this script adds the self-test to ModsConfig. It uses Core's -quicktest to
create a new game, waits for the assembly's RESULT line, then stops the game.
"""

from __future__ import annotations

import argparse
import json
import os
import plistlib
import signal
import subprocess
import sys
import tempfile
import time
import uuid
from pathlib import Path
from xml.etree import ElementTree as ET


TOOLS = Path(__file__).resolve().parents[1]
ROOT = TOOLS.parent
SELFTEST = Path(__file__).resolve().parent
sys.path.insert(0, str(TOOLS))
import run_smoke as smoke  # noqa: E402


def write_config(path: Path, version: str, caelavi_id: str, test_id: str) -> None:
    root = ET.Element("ModsConfigData")
    ET.SubElement(root, "version").text = version
    active = ET.SubElement(root, "activeMods")
    for mod_id in (*smoke.ACTIVE_IDS, caelavi_id, test_id):
        ET.SubElement(active, "li").text = mod_id
    expansions = ET.SubElement(root, "knownExpansions")
    ET.SubElement(expansions, "li").text = smoke.BIOTECH_ID
    path.parent.mkdir(parents=True, exist_ok=True)
    ET.ElementTree(root).write(path, encoding="utf-8", xml_declaration=True)


def has_result(log: Path) -> bool:
    if not log.is_file():
        return False
    return "[CaelaviSelfTest] RESULT " in log.read_text(encoding="utf-8", errors="replace")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--game-app", type=Path, help="RimWorldMac.app path")
    parser.add_argument("--harmony-dir", type=Path, help="Harmony install directory")
    parser.add_argument("--vef-dir", type=Path, help="VEF install directory")
    parser.add_argument("--output-dir", type=Path, help="new isolated output directory")
    parser.add_argument("--seconds", type=int, default=600,
                        help="maximum game runtime; stop sooner after RESULT (default 600)")
    parser.add_argument("--hide-conflicting-symlink", action="store_true",
                        help="temporarily hide only the old RIM/Caelavi symlink")
    parser.add_argument("--skip-build", action="store_true", help="reuse the existing self-test DLL")
    args = parser.parse_args()
    if args.seconds < 60:
        parser.error("--seconds must be at least 60")

    app = smoke.locate_app(args.game_app)
    executable = app / "Contents/MacOS/RimWorld by Ludeon Studios"
    mods_dir = app / "Mods"
    smoke.require_package(app / "Data/Core", smoke.CORE_ID)
    smoke.require_package(app / "Data/Biotech", smoke.BIOTECH_ID)
    harmony = smoke.locate_workshop_mod(args.harmony_dir, "RIMWORLD_HARMONY_DIR",
                                        "--harmony-dir", "2009463077", smoke.HARMONY_ID)
    vef = smoke.locate_workshop_mod(args.vef_dir, "RIMWORLD_VEF_DIR",
                                    "--vef-dir", "2023507013", smoke.VEF_ID)
    caelavi_id, _ = smoke.metadata(ROOT)
    test_mod = SELFTEST / "Mod"
    test_id, _ = smoke.metadata(test_mod)
    if smoke.game_is_running(executable):
        raise ValueError("RimWorld is already running; the isolated test will not start")
    if not args.skip_build:
        subprocess.run(["sh", str(SELFTEST / "build.sh")], cwd=ROOT, check=True)
    if not (test_mod / "Assemblies/Caelavi.SelfTest.dll").is_file():
        raise ValueError("self-test DLL missing; run sh tools/selftest/build.sh")
    with (app / "Contents/Info.plist").open("rb") as stream:
        version = str(plistlib.load(stream).get("CFBundleShortVersionString", "1.6"))
    if not version.startswith("1.6"):
        raise ValueError(f"RimWorld 1.6 required: {version}")

    run_root = (args.output_dir.expanduser().resolve() if args.output_dir else
                Path(tempfile.gettempdir()) / f"caelavi-selftest-{uuid.uuid4().hex[:12]}")
    if run_root.exists():
        raise ValueError(f"isolated output directory already exists: {run_root}")
    run_root.mkdir(parents=True)
    save_root = run_root / "SaveData"
    write_config(save_root / "Config/ModsConfig.xml", version, caelavi_id, test_id)
    log = run_root / "Player.log"
    command = [str(executable), f"-savedatafolder={save_root}", "-logFile", str(log),
               "-quicktest", "-caelavi-selftest", "-screen-fullscreen", "0",
               "-screen-width", "1280", "-screen-height", "800"]
    manifest = {
        "game_app": str(app), "game_version": version,
        "active_mods": [*smoke.ACTIVE_IDS, caelavi_id, test_id],
        "caelavi_dir": str(ROOT), "selftest_dir": str(test_mod),
        "harmony": str(harmony), "vef": str(vef),
        "save_data": str(save_root), "command": command,
    }
    (run_root / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Isolated output: {run_root}", flush=True)
    process: subprocess.Popen[bytes] | None = None
    isolated = False

    def interrupt(_signum: int, _frame: object) -> None:
        raise KeyboardInterrupt

    previous = signal.signal(signal.SIGTERM, interrupt)
    try:
        with smoke.temporary_mod_link(
            mods_dir, ROOT, caelavi_id, run_root, args.hide_conflicting_symlink,
            ((harmony, smoke.HARMONY_ID), (vef, smoke.VEF_ID), (test_mod, test_id)),
        ):
            try:
                process = subprocess.Popen(command, cwd=app)
                started = time.monotonic()
                isolated = smoke.wait_for_isolated_data(log, save_root, process)
                if isolated:
                    while time.monotonic() - started < args.seconds:
                        if has_result(log) or process.poll() is not None:
                            break
                        time.sleep(1)
                else:
                    print("Save data isolation was not acknowledged; stopping game", file=sys.stderr)
            finally:
                if process is not None and process.poll() is None:
                    process.terminate()
                    try:
                        process.wait(timeout=15)
                    except subprocess.TimeoutExpired:
                        process.kill()
                        process.wait(timeout=15)
    except KeyboardInterrupt:
        print("Interrupted; game stopped and temporary links restored", file=sys.stderr)
        return 130
    finally:
        signal.signal(signal.SIGTERM, previous)

    lines = log.read_text(encoding="utf-8", errors="replace").splitlines() if log.is_file() else []
    checks = [line for line in lines if "[CaelaviSelfTest]" in line]
    (run_root / "selftest-results.txt").write_text(
        "\n".join(checks) + ("\n" if checks else ""), encoding="utf-8")
    errors = smoke.extract_errors(log, run_root / "errors.txt")
    result = next((line for line in checks if "[CaelaviSelfTest] RESULT " in line), "")
    print(f"Self-test result: {result or 'MISSING'}")
    print(f"Checks: {run_root / 'selftest-results.txt'}")
    print(f"Other errors: {len(errors)} in {run_root / 'errors.txt'}")
    return 0 if isolated and "[CaelaviSelfTest] RESULT PASS " in result and not errors else 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (OSError, ValueError, ET.ParseError, subprocess.CalledProcessError) as exc:
        print(f"self-test error: {exc}", file=sys.stderr)
        sys.exit(2)
