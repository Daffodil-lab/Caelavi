#!/usr/bin/env python3
"""Build a clean installable ZIP after the local static checks pass."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile


ROOT = Path(__file__).resolve().parents[1]
PAYLOAD = ("About", "LoadFolders.xml", "1.6", "Patches", "Languages", "Textures", "README.md", "LICENSE")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--game-data", type=Path, help="validate against this RimWorld Data directory")
    parser.add_argument("--output", type=Path, default=ROOT / "dist" / "Caelavi-alpha.zip")
    args = parser.parse_args()
    command = [sys.executable, str(ROOT / "tools" / "validate.py")]
    if args.game_data:
        command.extend(("--game-data", str(args.game_data)))
    if subprocess.call(command) != 0:
        return 1
    files = []
    for entry in PAYLOAD:
        path = ROOT / entry
        if path.is_file():
            files.append(path)
        elif path.is_dir():
            files.extend(item for item in path.rglob("*") if item.is_file() and item.suffix != ".pdb")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with ZipFile(args.output, "w", ZIP_DEFLATED) as archive:
        for path in sorted(files):
            archive.write(path, Path("Caelavi") / path.relative_to(ROOT))
    print(f"Created {args.output} ({len(files)} files)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
