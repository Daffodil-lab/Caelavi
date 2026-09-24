#!/usr/bin/env python3
"""Make an original transparent debug sprite for the Caelavi living egg.

Run: python3 tools/generate_egg_placeholder.py
Requires Pillow 10 or newer. No source image or game texture is read.
"""

from __future__ import annotations

import math
from pathlib import Path

from PIL import Image, ImageDraw


ROOT = Path(__file__).resolve().parents[1]
DEST = ROOT / "Textures" / "Caelavi" / "Items" / "EggAlpha.png"
SCALE = 4
SIZE = 128


def egg_outline(cx: float, top: float, height: float, radius: float):
    right = []
    left = []
    for i in range(49):
        t = i / 48
        # Narrow top, broad lower half. This is deliberately plain test art.
        width = radius * math.sin(math.pi * t) ** 0.78 * (0.76 + 0.44 * t)
        y = top + height * t
        right.append((round((cx + width) * SCALE), round(y * SCALE)))
        left.append((round((cx - width) * SCALE), round(y * SCALE)))
    return right + list(reversed(left))


def main() -> None:
    image = Image.new("RGBA", (SIZE * SCALE, SIZE * SCALE), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    draw.ellipse((35*SCALE, 105*SCALE, 96*SCALE, 116*SCALE), fill=(35, 55, 63, 70))
    draw.polygon(egg_outline(64, 18, 91, 38), fill=(52, 77, 88, 255))
    draw.polygon(egg_outline(64, 21, 85, 35), fill=(225, 209, 173, 255))
    draw.polygon(egg_outline(61, 27, 72, 28), fill=(243, 231, 200, 255))
    draw.ellipse((49*SCALE, 39*SCALE, 57*SCALE, 49*SCALE), fill=(255, 250, 227, 170))
    for x, y, r in ((84, 71, 2), (77, 86, 2), (88, 91, 1), (50, 79, 1)):
        draw.ellipse(((x-r)*SCALE, (y-r)*SCALE, (x+r)*SCALE, (y+r)*SCALE),
                     fill=(171, 150, 112, 115))
    DEST.parent.mkdir(parents=True, exist_ok=True)
    image.resize((SIZE, SIZE), Image.Resampling.LANCZOS).save(DEST)
    print(DEST)


if __name__ == "__main__":
    main()
