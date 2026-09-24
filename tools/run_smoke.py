#!/usr/bin/env python3
"""Run a RimWorld 1.6 mod-load smoke check with isolated user data.

The script never reads or writes the player's normal ModsConfig or saves.
It links this checkout into the game's Mods directory only while --run is active.
"""

from __future__ import annotations

import argparse
import json
import os
import plistlib
import re
import signal
import subprocess
import sys
import tempfile
import time
import uuid
import xml.etree.ElementTree as ET
from contextlib import contextmanager
from pathlib import Path


CORE_ID = "ludeon.rimworld"
BIOTECH_ID = "ludeon.rimworld.biotech"
HARMONY_ID = "brrainz.harmony"
VEF_ID = "oskarpotocki.vanillafactionsexpanded.core"
ACTIVE_IDS = (HARMONY_ID, CORE_ID, BIOTECH_ID, VEF_ID)
ERROR_LINE = re.compile(
    r"(?:^|\b)(?:error|exception|failed|could not|cannot resolve|"
    r"missing reference|duplicate def|xml error|config error|"
    r"type load exception)(?:\b|:)",
    re.IGNORECASE,
)
STACK_LINE = re.compile(r"^\s*(?:at |--- |in |\[Ref |\(wrapper )")
KNOWN_HOST_NOISE = (
    "[S_API FAIL] SteamAPI_Init() failed; no appID found.",
    "[Steamworks.NET] SteamAPI.Init() failed.",
    "Fallback handler could not load library ",
    "Failed Allocations. Bucket layout:",
)
ALLOCATOR_BUCKET = re.compile(r"^\s*\d+B: .*Failed count: \d+\s*$")


def metadata(directory: Path) -> tuple[str, str]:
    about = directory / "About" / "About.xml"
    if not about.is_file():
        raise ValueError(f"About.xml がありません: {about}")
    root = ET.parse(about).getroot()
    package_id = (root.findtext("packageId") or "").strip()
    if not package_id:
        raise ValueError(f"packageId がありません: {about}")
    return package_id, (root.findtext("name") or "").strip()


def require_package(directory: Path, expected: str) -> None:
    actual, _ = metadata(directory)
    if actual.casefold() != expected.casefold():
        raise ValueError(f"packageId が異なります: {directory}: {actual} != {expected}")


def locate_app(explicit: Path | None) -> Path:
    steam = Path.home() / "Library/Application Support/Steam/steamapps/common/RimWorld"
    candidates = [explicit] if explicit else [
        Path(os.environ["RIMWORLD_APP"]) if "RIMWORLD_APP" in os.environ else None,
        steam / "RimWorldMac.app",
        Path("/Applications/RimWorldMac.app"),
    ]
    for candidate in candidates:
        if candidate and (candidate / "Contents/MacOS/RimWorld by Ludeon Studios").is_file():
            return candidate.resolve()
    raise ValueError("RimWorldMac.app が見つかりません。--game-app で指定してください")


def locate_workshop_mod(explicit: Path | None, env: str, option: str,
                        workshop_id: str, package_id: str) -> Path:
    workshop = Path.home() / "Library/Application Support/Steam/steamapps/workshop/content/294100"
    candidates = [explicit] if explicit else [
        Path(os.environ[env]) if env in os.environ else None,
        workshop / workshop_id,
    ]
    if not explicit and workshop.is_dir():
        candidates.extend(p for p in workshop.iterdir() if p.is_dir() and p.name != workshop_id)
    for candidate in candidates:
        if candidate is None or not (candidate / "About/About.xml").is_file():
            continue
        try:
            require_package(candidate, package_id)
        except (ValueError, ET.ParseError):
            continue
        supported = ET.parse(candidate / "About/About.xml").getroot().find("supportedVersions")
        if supported is not None and "1.6" not in [(li.text or "").strip() for li in supported]:
            continue
        return candidate.resolve()
    raise ValueError(f"RimWorld 1.6対応の {package_id} が見つかりません。{option} で指定してください")


def game_is_running(executable: Path) -> bool:
    result = subprocess.run(["ps", "-axo", "pid=,command="], capture_output=True,
                            text=True, check=True)
    for row in result.stdout.splitlines():
        parts = row.strip().split(None, 1)
        if len(parts) != 2 or not parts[0].isdigit() or int(parts[0]) == os.getpid():
            continue
        command = parts[1]
        if str(executable) in command or "RimWorldMac.app/Contents/MacOS/RimWorld by Ludeon Studios" in command:
            return True
    return False


def conflicts(mods_dir: Path, package_id: str, checkout: Path) -> list[Path]:
    found = []
    for item in mods_dir.iterdir():
        if not item.is_dir() or item.resolve() == checkout.resolve():
            continue
        try:
            other_id, _ = metadata(item)
        except (ValueError, ET.ParseError, OSError):
            continue
        if other_id.casefold() == package_id.casefold():
            found.append(item)
    return found


def legacy_link(link: Path) -> bool:
    if not link.is_symlink():
        return False
    target = link.resolve()
    return target.name == "Caelavi" and target.parent.name == "RIM"


def mods_config(path: Path, version: str, package_id: str) -> None:
    root = ET.Element("ModsConfigData")
    ET.SubElement(root, "version").text = version
    active = ET.SubElement(root, "activeMods")
    for mod_id in (*ACTIVE_IDS, package_id):
        ET.SubElement(active, "li").text = mod_id
    expansions = ET.SubElement(root, "knownExpansions")
    ET.SubElement(expansions, "li").text = BIOTECH_ID
    path.parent.mkdir(parents=True, exist_ok=True)
    ET.ElementTree(root).write(path, encoding="utf-8", xml_declaration=True)


def extract_errors(log: Path, output: Path) -> list[str]:
    if not log.is_file():
        output.write_text("Player.log was not created.\n", encoding="utf-8")
        return []
    lines = log.read_text(encoding="utf-8", errors="replace").splitlines()
    hits: list[str] = []
    for index, line in enumerate(lines):
        if not ERROR_LINE.search(line):
            continue
        if line.lstrip().startswith(KNOWN_HOST_NOISE) or ALLOCATOR_BUCKET.match(line):
            continue
        # Unity stack traces immediately after an error provide the useful source.
        block = [f"{index + 1}: {line}"]
        for next_line in lines[index + 1:index + 7]:
            if STACK_LINE.match(next_line):
                block.append(next_line)
            else:
                break
        hits.append("\n".join(block))
    output.write_text("\n\n".join(hits) + ("\n" if hits else ""), encoding="utf-8")
    return hits


def wait_for_isolated_data(log: Path, save_root: Path, process: subprocess.Popen[bytes],
                           seconds: int = 45) -> bool:
    """Fail closed if the game did not acknowledge -savedatafolder."""
    deadline = time.monotonic() + seconds
    while time.monotonic() < deadline:
        if log.is_file():
            content = log.read_text(encoding="utf-8", errors="replace")
            if f"Save data folder overridden to {save_root}" in content:
                return True
        if process.poll() is not None:
            return False
        time.sleep(0.5)
    return False


@contextmanager
def temporary_mod_link(mods_dir: Path, checkout: Path, package_id: str,
                       run_root: Path, hide_conflicting: bool,
                       dependencies: tuple[tuple[Path, str], ...]):
    existing = conflicts(mods_dir, package_id, checkout)
    if existing and (not hide_conflicting or any(not legacy_link(p) for p in existing)):
        joined = ", ".join(str(p) for p in existing)
        raise ValueError(f"同じ packageId の既存MODがあります: {joined}. "
                         "旧RIM/Caelavi symlink に限り --hide-conflicting-symlink で一時退避できます")
    moved: list[tuple[Path, Path]] = []
    created_links: list[tuple[Path, Path]] = []
    try:
        for index, link in enumerate(existing):
            backup = run_root / f"hidden-legacy-link-{index}"
            link.rename(backup)
            moved.append((link, backup))
            print(f"旧symlinkを一時退避: {link} -> {backup}")
        for index, (target, mod_id) in enumerate((*dependencies, (checkout, package_id))):
            other_installs = conflicts(mods_dir, mod_id, target)
            if other_installs:
                raise ValueError(f"別版の {mod_id} がゲームのModsにあります: {other_installs}")
            if any(item.is_dir() and item.resolve() == target.resolve() for item in mods_dir.iterdir()):
                continue
            link = mods_dir / f"Caelavi-Smoke-{index}-{uuid.uuid4().hex[:12]}"
            link.symlink_to(target, target_is_directory=True)
            created_links.append((link, target))
        yield
    finally:
        for link, target in reversed(created_links):
            if link.is_symlink() and link.resolve() == target.resolve():
                link.unlink()
        for original, backup in reversed(moved):
            if backup.is_symlink() and not original.exists() and not original.is_symlink():
                backup.rename(original)
                print(f"旧symlinkを復元: {original}")
            elif backup.exists() or backup.is_symlink():
                print(f"要手動復元: {backup} -> {original}", file=sys.stderr)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run", action="store_true", help="RimWorldを起動して指定秒数後に終了")
    parser.add_argument("--game-app", type=Path, help="RimWorldMac.app のパス")
    parser.add_argument("--vef-dir", type=Path, help="VEF のインストール先")
    parser.add_argument("--harmony-dir", type=Path, help="Harmony のインストール先")
    parser.add_argument("--mod-dir", type=Path, default=Path(__file__).resolve().parents[1],
                        help="今回のCaelaviチェックアウト")
    parser.add_argument("--output-dir", type=Path, help="新規の隔離データ保存先。既存パスは不可")
    parser.add_argument("--seconds", type=int, default=180, help="起動を維持する秒数 (既定: 180)")
    parser.add_argument("--hide-conflicting-symlink", action="store_true",
                        help="旧RIM/Caelavi symlink に限り実行中だけ退避")
    args = parser.parse_args()
    if args.seconds < 15:
        parser.error("--seconds は 15 以上にしてください")

    checkout = args.mod_dir.resolve()
    package_id, mod_name = metadata(checkout)
    app = locate_app(args.game_app)
    executable = app / "Contents/MacOS/RimWorld by Ludeon Studios"
    mods_dir = app / "Mods"
    require_package(app / "Data/Core", CORE_ID)
    require_package(app / "Data/Biotech", BIOTECH_ID)
    harmony = locate_workshop_mod(args.harmony_dir, "RIMWORLD_HARMONY_DIR",
                                  "--harmony-dir", "2009463077", HARMONY_ID)
    vef = locate_workshop_mod(args.vef_dir, "RIMWORLD_VEF_DIR", "--vef-dir",
                              "2023507013", VEF_ID)
    with (app / "Contents/Info.plist").open("rb") as stream:
        version = str(plistlib.load(stream).get("CFBundleShortVersionString", "1.6"))
    if not version.startswith("1.6"):
        raise ValueError(f"RimWorld 1.6 ではありません: {version}")
    if game_is_running(executable):
        raise ValueError("RimWorldが既に起動しています。終了してから隔離検証してください")
    if not mods_dir.is_dir():
        raise ValueError(f"Modsディレクトリがありません: {mods_dir}")

    run_root = (args.output_dir.expanduser().resolve() if args.output_dir else
                Path(tempfile.gettempdir()) / f"caelavi-smoke-{uuid.uuid4().hex[:12]}")
    if run_root.exists():
        raise ValueError(f"隔離先が既に存在します: {run_root}")
    run_root.mkdir(parents=True)
    save_root = run_root / "SaveData"
    config = save_root / "Config/ModsConfig.xml"
    mods_config(config, version, package_id)
    manifest = {
        "game_app": str(app), "game_version": version,
        "mod_dir": str(checkout), "mod_name": mod_name, "package_id": package_id,
        "harmony": str(harmony), "vef": str(vef),
        "active_mods": [*ACTIVE_IDS, package_id], "save_data": str(save_root),
        "launched": False,
    }
    manifest_path = run_root / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"隔離データ: {run_root}")
    print(f"最小ModsConfig: {config}")
    if not args.run:
        print("準備のみ。ゲームは起動していません。--run でロード確認します")
        return 0

    log = run_root / "Player.log"
    command = [str(executable), f"-savedatafolder={save_root}", "-logFile", str(log),
               "-screen-fullscreen", "0", "-screen-width", "1280", "-screen-height", "800"]
    process = None
    isolation_confirmed = False

    def interrupt(_signum: int, _frame: object) -> None:
        raise KeyboardInterrupt

    previous = signal.signal(signal.SIGTERM, interrupt)
    try:
        with temporary_mod_link(mods_dir, checkout, package_id, run_root,
                                args.hide_conflicting_symlink,
                                ((harmony, HARMONY_ID), (vef, VEF_ID))):
            try:
                manifest["launched"] = True
                manifest["command"] = command
                manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
                print("RimWorldを起動します。期限後にこのプロセスを終了します")
                process = subprocess.Popen(command, cwd=app)
                started = time.monotonic()
                isolation_confirmed = wait_for_isolated_data(log, save_root, process)
                if not isolation_confirmed:
                    print("保存先の隔離確認がPlayer.logに現れません。ゲームを停止します", file=sys.stderr)
                else:
                    try:
                        process.wait(timeout=max(1, args.seconds - (time.monotonic() - started)))
                    except subprocess.TimeoutExpired:
                        pass
            finally:
                if process and process.poll() is None:
                    process.terminate()
                    try:
                        process.wait(timeout=15)
                    except subprocess.TimeoutExpired:
                        process.kill()
                        process.wait(timeout=15)
    except KeyboardInterrupt:
        print("中断を受けたためゲームを終了してsymlinkを復元します", file=sys.stderr)
        return 130
    finally:
        signal.signal(signal.SIGTERM, previous)

    hits = extract_errors(log, run_root / "errors.txt")
    print(f"Player.log: {log}")
    print(f"抽出したエラー行: {len(hits)} (errors.txt)")
    if not log.exists() or not isolation_confirmed:
        return 2
    return 1 if hits else 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (OSError, ValueError, ET.ParseError) as exc:
        print(f"smoke check error: {exc}", file=sys.stderr)
        sys.exit(2)
