#!/usr/bin/env python3
"""Draw the original temporary wing-guard item icon.

Run with Python 3 and Pillow: python3 tools/generate_wing_guard_icon.py
This script reads no existing art, game asset, or other MOD file. The image is
an alpha-test marker and does not establish the final wearable design.
"""

from pathlib import Path

from PIL import Image, ImageDraw


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "Textures" / "Caelavi" / "Items" / "WingGuardAlpha.png"
SCALE = 4
SIZE = 128


def scale_points(points):
    return [(round(x * SCALE), round(y * SCALE)) for x, y in points]


def plate(draw, points, fill):
    polygon = scale_points(points)
    draw.polygon(polygon, fill=fill)
    draw.line(polygon + [polygon[0]], fill="#223743", width=3 * SCALE, joint="curve")


def main():
    image = Image.new("RGBA", (SIZE * SCALE, SIZE * SCALE), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)

    # Mirrored angular sleeves and a narrow central fastening strap.
    plate(draw, [(14, 39), (39, 23), (54, 49), (44, 94), (26, 82)], "#71909d")
    plate(draw, [(114, 39), (89, 23), (74, 49), (84, 94), (102, 82)], "#71909d")
    plate(draw, [(35, 30), (48, 38), (52, 70), (41, 80), (29, 63)], "#acc0c5")
    plate(draw, [(93, 30), (80, 38), (76, 70), (87, 80), (99, 63)], "#acc0c5")
    draw.rounded_rectangle((50 * SCALE, 54 * SCALE, 78 * SCALE, 70 * SCALE),
                           radius=4 * SCALE, fill="#d6a95d", outline="#283b46",
                           width=3 * SCALE)
    draw.line(scale_points([(23, 65), (40, 71)]), fill="#d6a95d", width=3 * SCALE)
    draw.line(scale_points([(105, 65), (88, 71)]), fill="#d6a95d", width=3 * SCALE)

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    image.resize((SIZE, SIZE), Image.Resampling.LANCZOS).save(OUTPUT)
    print(OUTPUT)


if __name__ == "__main__":
    main()
