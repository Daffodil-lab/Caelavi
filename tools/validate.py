#!/usr/bin/env python3
"""Static checks for the standalone Caelavi mod (RimWorld 1.6).

The game itself remains the authority for Def loading and runtime behaviour.
"""

from __future__ import annotations

import argparse
import struct
import sys
from collections import defaultdict
from pathlib import Path
from xml.etree import ElementTree as ET


ROOT = Path(__file__).resolve().parents[1]
XML_DIRS = (ROOT / "About", ROOT / "1.6" / "Defs", ROOT / "Patches", ROOT / "Languages")
PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"


def xml_files() -> list[Path]:
    files = [ROOT / "LoadFolders.xml"]
    for directory in XML_DIRS:
        if directory.exists():
            files.extend(directory.rglob("*.xml"))
    return sorted(files)


def parse_xml(path: Path, errors: list[str]) -> ET.Element | None:
    if not path.is_file():
        errors.append(f"missing XML: {path.relative_to(ROOT)}")
        return None
    try:
        return ET.parse(path).getroot()
    except ET.ParseError as exc:
        errors.append(f"invalid XML: {path.relative_to(ROOT)}: {exc}")
        return None


def named_parents(game_data: Path | None, errors: list[str]) -> set[str]:
    if game_data is None:
        return set()
    if not game_data.is_dir():
        errors.append(f"game Data directory does not exist: {game_data}")
        return set()
    names: set[str] = set()
    for content in ("Core", "Biotech"):
        defs_dir = game_data / content / "Defs"
        if not defs_dir.is_dir():
            errors.append(f"missing game Defs: {defs_dir}")
            continue
        for path in defs_dir.rglob("*.xml"):
            try:
                root = ET.parse(path).getroot()
            except ET.ParseError as exc:
                errors.append(f"invalid game XML: {path}: {exc}")
                continue
            names.update(node.attrib["Name"] for node in root.iter() if "Name" in node.attrib)
    return names


def check_about(roots: dict[Path, ET.Element], errors: list[str]) -> None:
    about = roots.get(ROOT / "About" / "About.xml")
    if about is None:
        errors.append("About/About.xml is required")
        return
    package_id = about.findtext("packageId", "").strip()
    if not package_id:
        errors.append("About.xml has no packageId")
    versions = [li.text.strip() for li in about.findall("./supportedVersions/li") if li.text]
    if "1.6" not in versions:
        errors.append("About.xml must list RimWorld 1.6")
    dependencies = {
        li.findtext("packageId", "").strip().lower()
        for li in about.findall("./modDependencies/li")
    }
    for required in ("brrainz.harmony", "ludeon.rimworld.biotech",
                     "oskarpotocki.vanillafactionsexpanded.core"):
        if required not in dependencies:
            errors.append(f"About.xml is missing dependency {required}")


def check_load_folders(roots: dict[Path, ET.Element], errors: list[str]) -> None:
    root = roots.get(ROOT / "LoadFolders.xml")
    if root is None:
        return
    for folder in root.findall(".//li"):
        if not folder.text:
            continue
        value = folder.text.strip()
        if value.startswith("/"):
            continue
        if not (ROOT / value).is_dir():
            errors.append(f"LoadFolders.xml refers to missing folder: {value}")


def check_defs(
    roots: dict[Path, ET.Element], game_data: Path | None, errors: list[str]
) -> int:
    defs = defaultdict(list)
    nodes = {}
    names: set[str] = set()
    parent_refs: list[tuple[Path, str]] = []
    count = 0
    for path, root in roots.items():
        if root.tag != "Defs":
            continue
        for node in root:
            count += 1
            def_name = node.findtext("defName", "").strip()
            if def_name:
                defs[(node.tag, def_name)].append(path)
                nodes[(node.tag, def_name)] = node
            if "Name" in node.attrib:
                names.add(node.attrib["Name"])
            if "ParentName" in node.attrib:
                parent_refs.append((path, node.attrib["ParentName"]))
    for (kind, def_name), paths in defs.items():
        if len(paths) > 1:
            locations = ", ".join(str(path.relative_to(ROOT)) for path in paths)
            errors.append(f"duplicate {kind} {def_name}: {locations}")
    local_refs = (
        ("PawnKindDef", "race", "ThingDef"),
    )
    for source_kind, tag, target_kind in local_refs:
        for (kind, def_name), node in nodes.items():
            if kind != source_kind:
                continue
            target = node.findtext(tag, "").strip()
            if target.startswith("CA_") and (target_kind, target) not in nodes:
                errors.append(f"{source_kind} {def_name} refers to missing {target_kind} {target}")
    for (kind, def_name), node in nodes.items():
        if kind == "GeneDef":
            body_type = node.findtext("bodyType", "").strip()
            if body_type.startswith("CA_"):
                errors.append(f"GeneDef {def_name} bodyType is an enum, not a BodyTypeDef: {body_type}")
            for head in node.findall("./forcedHeadTypes/li"):
                target = (head.text or "").strip()
                if target.startswith("CA_") and ("HeadTypeDef", target) not in nodes:
                    errors.append(f"GeneDef {def_name} refers to missing HeadTypeDef {target}")
        elif kind == "XenotypeDef":
            for gene in node.findall("./genes/li"):
                target = (gene.text or "").strip()
                if target.startswith("CA_") and ("GeneDef", target) not in nodes:
                    errors.append(f"XenotypeDef {def_name} refers to missing GeneDef {target}")
        elif kind == "PawnKindDef":
            chances = node.find("./xenotypeSet/xenotypeChances")
            if chances is not None:
                for chance in chances:
                    if chance.tag.startswith("CA_") and ("XenotypeDef", chance.tag) not in nodes:
                        errors.append(f"PawnKindDef {def_name} refers to missing XenotypeDef {chance.tag}")
    if game_data is not None:
        names.update(named_parents(game_data, errors))
        for path, parent in parent_refs:
            if parent not in names:
                errors.append(f"unknown ParentName {parent}: {path.relative_to(ROOT)}")
    return count


def check_textures(roots: dict[Path, ET.Element], errors: list[str]) -> int:
    textures = ROOT / "Textures"
    pngs = list(textures.rglob("*.png")) if textures.is_dir() else []
    for path in pngs:
        with path.open("rb") as file:
            header = file.read(26)
        relative = path.relative_to(ROOT)
        if len(header) < 26 or not header.startswith(PNG_SIGNATURE) or header[12:16] != b"IHDR":
            errors.append(f"invalid PNG header: {relative}")
            continue
        width, height, bit_depth, colour_type = struct.unpack(">IIBB", header[16:26])
        if width == 0 or height == 0 or bit_depth != 8 or colour_type not in (4, 6):
            errors.append(f"expected 8-bit PNG with alpha: {relative}")
    for path, root in roots.items():
        for node in root.iter("texPath"):
            value = (node.text or "").strip()
            if not value.startswith("Caelavi/"):
                continue
            base = textures / value
            candidates = [base.with_suffix(".png")]
            candidates.extend(base.parent / f"{base.name}_{direction}.png" for direction in ("south", "east", "north"))
            if not any(candidate.exists() for candidate in candidates):
                errors.append(f"missing Caelavi texture {value}: {path.relative_to(ROOT)}")
    return len(pngs)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--game-data", type=Path, help="RimWorldMac.app/Data or equivalent")
    args = parser.parse_args()
    errors: list[str] = []
    roots = {}
    for path in xml_files():
        root = parse_xml(path, errors)
        if root is not None:
            roots[path] = root
    check_about(roots, errors)
    check_load_folders(roots, errors)
    defs_count = check_defs(roots, args.game_data, errors)
    png_count = check_textures(roots, errors)
    if (ROOT / "Source" / "Caelavi.csproj").exists() and not (ROOT / "1.6" / "Assemblies" / "Caelavi.dll").is_file():
        errors.append("Source exists but 1.6/Assemblies/Caelavi.dll has not been built")
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print(f"PASS: {len(roots)} XML files, {defs_count} Defs, {png_count} transparent PNG files")
    if args.game_data is None:
        print("ParentName references against Core/Biotech were not checked (--game-data omitted).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
