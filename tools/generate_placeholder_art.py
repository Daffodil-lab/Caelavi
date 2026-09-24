#!/usr/bin/env python3
"""Draw original, intentionally temporary Caelavi pawn textures.

Run from any directory with Python 3 and Pillow 10 or newer:
    python3 tools/generate_placeholder_art.py

No source image, game asset, external repository, or font is read. The PNGs are
generated solely from the coordinates below. In particular, the palette and
silhouettes are debug art, not a decision about Caelavi appearance.
"""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
TEXTURES = ROOT / "Textures" / "Caelavi" / "Pawn"
UI_TEXTURES = ROOT / "Textures" / "Caelavi" / "UI"
PREVIEW = ROOT / "docs" / "placeholder-art-preview.png"
SIZE = 256
SCALE = 4
PX = SIZE * SCALE
DIRECTIONS = ("south", "east", "north")
PARTS = (
    "Body", "Head", "WingLeft", "WingRight", "WingLeftDeployed",
    "WingRightDeployed", "Tail", "TempleLeft", "TempleRight", "Crest",
)

# High contrast is deliberate: the colors help distinguish pieces during alpha
# debugging and do not specify skin, plumage, sex, age, or a finished uniform.
INK = "#243641"
BODY = "#526d78"
BODY_LIGHT = "#6e8d95"
BODY_DARK = "#405764"
HEAD = "#91abb0"
HEAD_LIGHT = "#b0c5c3"
FEATHER = "#dea957"
FEATHER_LIGHT = "#efc87d"
FEATHER_DARK = "#ad7840"
LEFT_MARK = "#c24d75"  # anatomical left debug mark
RIGHT_MARK = "#3f83bd"  # anatomical right debug mark


def canvas() -> Image.Image:
    return Image.new("RGBA", (PX, PX), (0, 0, 0, 0))


def coords(points):
    return [(round(x * SCALE), round(y * SCALE)) for x, y in points]


def ellipse(draw, box, fill, outline=INK, width=2):
    draw.ellipse(
        tuple(round(v * SCALE) for v in box),
        fill=fill,
        outline=outline,
        width=round(width * SCALE) if outline else 1,
    )


def line(draw, points, fill, width=2, joint="curve"):
    draw.line(coords(points), fill=fill, width=round(width * SCALE), joint=joint)


def polygon(draw, points, fill, outline=INK, width=2):
    pts = coords(points)
    draw.polygon(pts, fill=fill)
    if outline:
        draw.line(pts + [pts[0]], fill=outline, width=round(width * SCALE), joint="curve")


def cubic(p0, p1, p2, p3, steps=18):
    result = []
    for i in range(1, steps + 1):
        t = i / steps
        q = 1 - t
        result.append((
            q**3 * p0[0] + 3 * q**2 * t * p1[0] + 3 * q * t**2 * p2[0] + t**3 * p3[0],
            q**3 * p0[1] + 3 * q**2 * t * p1[1] + 3 * q * t**2 * p2[1] + t**3 * p3[1],
        ))
    return result


def path(draw, start, segments, fill, outline=INK, width=2):
    """Fill a closed polygon whose curved edges are sampled cubic Beziers."""
    points = [start]
    at = start
    for segment in segments:
        if len(segment) == 2:
            at = segment
            points.append(at)
        else:
            c1, c2, end = segment
            points.extend(cubic(at, c1, c2, end))
            at = end
    polygon(draw, points, fill, outline, width)


def feather(draw, root, tip, breadth, fill=FEATHER, outline=INK, side=1):
    """A simple pointed feather defined by a root and an independent tip."""
    x0, y0 = root
    x1, y1 = tip
    dx, dy = x1 - x0, y1 - y0
    length = max((dx * dx + dy * dy) ** .5, 1)
    nx, ny = -dy / length * side, dx / length * side
    path(draw, root, [
        ((x0 + dx * .22 + nx * breadth * .8, y0 + dy * .22 + ny * breadth * .8),
         (x0 + dx * .62 + nx * breadth, y0 + dy * .62 + ny * breadth), tip),
        ((x0 + dx * .65 - nx * breadth * .35, y0 + dy * .65 - ny * breadth * .35),
         (x0 + dx * .22 - nx * breadth * .15, y0 + dy * .22 - ny * breadth * .15), root),
    ], fill, outline, 1.7)
    line(draw, [root, (x0 + dx * .8, y0 + dy * .8)], FEATHER_DARK, 1)


def body(direction):
    im = canvas()
    d = ImageDraw.Draw(im)
    if direction in ("south", "north"):
        # Sleeves and hands sit under the central torso.
        for side in (-1, 1):
            x = 128 + side * 44
            ellipse(d, (x - 14, 102, x + 14, 180), BODY_DARK)
            ellipse(d, (x - 11, 169, x + 11, 187), BODY_LIGHT)
        path(d, (99, 78), [
            ((82, 86), (76, 108), (80, 135)),
            ((83, 171), (91, 204), (98, 214)),
            ((117, 224), (139, 224), (158, 214)),
            ((165, 204), (173, 171), (176, 135)),
            ((180, 108), (174, 86), (157, 78)),
            ((139, 72), (117, 72), (99, 78)),
        ], BODY)
        path(d, (105, 82), [
            ((112, 98), (144, 98), (151, 82)),
            ((140, 72), (116, 72), (105, 82)),
        ], BODY_LIGHT, None)
        if direction == "south":
            path(d, (94, 124), [
                ((107, 117), (149, 117), (162, 124)),
                ((158, 151), (147, 170), (128, 174)),
                ((109, 170), (98, 151), (94, 124)),
            ], BODY_LIGHT, None)
            line(d, [(128, 175), (128, 212)], BODY_DARK, 2)
        else:
            line(d, [(128, 99), (128, 199)], BODY_DARK, 2)
            line(d, [(104, 178), (128, 187), (152, 178)], BODY_LIGHT, 2)
    else:  # east, with west supplied by Graphic_Multi's east mirror
        ellipse(d, (101, 106, 126, 182), BODY_DARK)
        ellipse(d, (103, 173, 124, 189), BODY_LIGHT)
        path(d, (111, 79), [
            ((99, 78), (89, 94), (90, 121)),
            ((92, 171), (104, 206), (110, 216)),
            ((125, 223), (143, 220), (154, 214)),
            ((162, 202), (162, 167), (162, 125)),
            ((162, 99), (152, 83), (142, 78)),
            ((132, 72), (120, 75), (111, 79)),
        ], BODY)
        path(d, (144, 105), [
            ((154, 115), (159, 141), (154, 169)),
            ((144, 172), (137, 167), (135, 155)),
            ((139, 133), (141, 117), (144, 105)),
        ], BODY_LIGHT, None)
        ellipse(d, (135, 158, 155, 186), BODY_LIGHT)
        line(d, [(153, 180), (152, 201)], BODY_DARK, 2)
    return im


def head(direction):
    im = canvas()
    d = ImageDraw.Draw(im)
    if direction in ("south", "north"):
        path(d, (128, 91), [
            ((105, 90), (91, 103), (91, 123)),
            ((90, 148), (104, 165), (128, 169)),
            ((152, 165), (166, 148), (165, 123)),
            ((165, 103), (151, 90), (128, 91)),
        ], HEAD)
        path(d, (102, 119), [
            ((101, 104), (114, 100), (128, 100)),
            ((142, 100), (155, 104), (154, 119)),
            ((142, 112), (114, 112), (102, 119)),
        ], HEAD_LIGHT, None)
        if direction == "south":
            ellipse(d, (110, 128, 115, 133), INK, None)
            ellipse(d, (141, 128, 146, 133), INK, None)
            line(d, [(118, 149), (128, 152), (138, 149)], BODY_DARK, 1.5)
        else:
            line(d, [(115, 103), (109, 143)], BODY_LIGHT, 1.5)
            line(d, [(141, 103), (147, 143)], BODY_LIGHT, 1.5)
    else:
        path(d, (127, 91), [
            ((103, 89), (92, 107), (95, 129)),
            ((98, 154), (112, 168), (136, 168)),
            ((153, 164), (170, 148), (166, 132)),
            ((159, 126), (153, 124), (158, 117)),
            ((155, 100), (144, 91), (127, 91)),
        ], HEAD)
        path(d, (113, 102), [
            ((129, 96), (146, 105), (151, 117)),
            ((138, 113), (124, 113), (104, 121)),
            ((103, 114), (106, 106), (113, 102)),
        ], HEAD_LIGHT, None)
        ellipse(d, (143, 128, 148, 134), INK, None)
        line(d, [(145, 150), (155, 150)], BODY_DARK, 1.5)
    return im


def tail(direction):
    im = canvas()
    d = ImageDraw.Draw(im)
    if direction == "east":
        for root, tip, w in [((98, 189), (43, 231), 9), ((102, 192), (63, 238), 9), ((107, 195), (78, 243), 8)]:
            feather(d, root, tip, w)
        ellipse(d, (97, 186, 113, 202), FEATHER_DARK)
    elif direction == "north":
        for root, tip, w in [((115, 189), (99, 240), 7), ((126, 190), (126, 248), 8), ((137, 189), (153, 240), 7)]:
            feather(d, root, tip, w)
    else:
        for root, tip, w in [((118, 192), (96, 235), 7), ((128, 193), (128, 244), 8), ((138, 192), (160, 235), 7)]:
            feather(d, root, tip, w)
    return im


def wing(direction, side, deployed):
    """side is anatomical Left/Right, not the viewer's left/right."""
    im = canvas()
    d = ImageDraw.Draw(im)
    mark = LEFT_MARK if side == "Left" else RIGHT_MARK
    if direction == "south":
        sign = 1 if side == "Left" else -1
    elif direction == "north":
        sign = -1 if side == "Left" else 1
    else:
        sign = 1 if side == "Left" else -1
    root = (128 + sign * (41 if direction != "east" else 29), 107)

    if direction == "east":
        if deployed:
            target = (root[0] + sign * 65, 45 if side == "Left" else 59)
            tips = [(target[0] + sign * i * 7, target[1] - 16 + i * 18) for i in range(3)]
        else:
            target = (root[0] + sign * 34, 162)
            tips = [(target[0] + sign * i * 6, target[1] + i * 15) for i in range(3)]
    elif deployed:
        target = (root[0] + sign * 60, 49)
        tips = [(target[0] + sign * i * 8, target[1] - 12 + i * 15) for i in range(3)]
    else:
        target = (root[0] + sign * 36, 165)
        tips = [(target[0] + sign * i * 7, target[1] + i * 12) for i in range(3)]

    for i, tip in enumerate(reversed(tips)):
        feather(d, root, tip, 11 - i, FEATHER_DARK if i == 0 else FEATHER, side=sign)
    # Long upper contour and patch at the actual shoulder make the piece legible.
    polygon(d, [root, (root[0] + sign * 14, root[1] - 8), target,
                (root[0] + sign * 24, root[1] + (14 if deployed else 35))], FEATHER)
    ellipse(d, (root[0] - 8, root[1] - 8, root[0] + 8, root[1] + 8), mark)
    return im


def temple(direction, side):
    im = canvas()
    d = ImageDraw.Draw(im)
    if direction == "south":
        sign = 1 if side == "Left" else -1
    elif direction == "north":
        sign = -1 if side == "Left" else 1
    else:
        sign = 1 if side == "Left" else -1
    root = (128 + sign * (36 if direction != "east" else 30), 120)
    for offset, length in [(-6, 25), (3, 31), (11, 23)]:
        tip = (root[0] + sign * length, root[1] + offset)
        feather(d, root, tip, 5, FEATHER_LIGHT, side=sign)
    return im


def crest(direction):
    im = canvas()
    d = ImageDraw.Draw(im)
    x = 129 if direction == "east" else 128
    for root, tip in [((x - 8, 98), (x - 15, 63)), ((x, 96), (x + 2, 54)),
                      ((x + 8, 99), (x + 18, 66))]:
        feather(d, root, tip, 6, FEATHER_LIGHT, side=1)
    return im


def make_part(part, direction):
    if part == "Body":
        return body(direction)
    if part == "Head":
        return head(direction)
    if part == "Tail":
        return tail(direction)
    if part.startswith("Wing"):
        return wing(direction, "Left" if "Left" in part else "Right", "Deployed" in part)
    if part.startswith("Temple"):
        return temple(direction, "Left" if "Left" in part else "Right")
    if part == "Crest":
        return crest(direction)
    raise ValueError(part)


def composite(direction, deployed, images):
    work = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    wing_mode = "Deployed" if deployed else ""
    # Exact game draw-order must be checked in game. This is an asset preview.
    for part in ("Tail", f"WingLeft{wing_mode}", f"WingRight{wing_mode}", "Body"):
        work.alpha_composite(images[(part, direction)])
    shift = -56
    for part in ("Head", "TempleLeft", "TempleRight", "Crest"):
        work.alpha_composite(images[(part, direction)], (0, shift))
    return work


def preview(images):
    board = Image.new("RGB", (3 * 340, 2 * 355 + 60), "#e9eceb")
    d = ImageDraw.Draw(board)
    font = ImageFont.load_default()
    d.text((20, 16), "CAELAVI / ALPHA PLACEHOLDER ART / NOT FINAL DESIGN", fill="#263841", font=font)
    for row, deployed in enumerate((False, True)):
        for col, direction in enumerate(DIRECTIONS):
            x, y = col * 340 + 42, row * 355 + 75
            # Checker is preview-only; each real asset remains transparent.
            for yy in range(0, 256, 16):
                for xx in range(0, 256, 16):
                    color = "#f8faf9" if (xx + yy) // 16 % 2 == 0 else "#dce3e1"
                    d.rectangle((x + xx, y + yy, x + xx + 15, y + yy + 15), fill=color)
            figure = composite(direction, deployed, images)
            board.paste(figure, (x, y), figure)
            d.text((x, y - 20), f"{direction.upper()} / {'DEPLOYED' if deployed else 'FOLDED'}", fill="#263841", font=font)
    PREVIEW.parent.mkdir(parents=True, exist_ok=True)
    board.save(PREVIEW)


def gene_icon():
    """A separate legible pictogram for the temporary morphology GeneDef."""
    im = canvas()
    d = ImageDraw.Draw(im)
    for sign, color in ((-1, RIGHT_MARK), (1, LEFT_MARK)):
        polygon(d, [(128 + sign * 25, 130), (128 + sign * 81, 72),
                    (128 + sign * 96, 105), (128 + sign * 54, 157)], FEATHER)
        line(d, [(128 + sign * 44, 130), (128 + sign * 76, 103)], color, 7)
    polygon(d, [(111, 155), (128, 205), (145, 155)], FEATHER)
    ellipse(d, (88, 100, 168, 178), BODY)
    ellipse(d, (104, 64, 152, 121), HEAD)
    for tip in ((113, 36), (128, 26), (143, 36)):
        line(d, [(128, 70), tip], FEATHER_LIGHT, 8)
    UI_TEXTURES.mkdir(parents=True, exist_ok=True)
    im.resize((128, 128), Image.Resampling.LANCZOS).save(
        UI_TEXTURES / "GeneMorphology.png", optimize=True
    )


def main():
    TEXTURES.mkdir(parents=True, exist_ok=True)
    images = {}
    for part in PARTS:
        for direction in DIRECTIONS:
            image = make_part(part, direction).resize((SIZE, SIZE), Image.Resampling.LANCZOS)
            if image.getbbox() is None:
                raise RuntimeError(f"empty texture: {part}_{direction}")
            output = TEXTURES / f"{part}_{direction}.png"
            image.save(output, optimize=True)
            images[(part, direction)] = image
    preview(images)
    gene_icon()
    print(f"Generated {len(images)} transparent placeholder textures in {TEXTURES}")
    print(f"Gene icon: {UI_TEXTURES / 'GeneMorphology.png'}")
    print(f"Preview: {PREVIEW}")


if __name__ == "__main__":
    main()
