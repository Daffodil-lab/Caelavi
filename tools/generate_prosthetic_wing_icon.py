#!/usr/bin/env python3
"""Generate the original temporary prosthetic-wing item icon.

Run with Python 3 and Pillow: python3 tools/generate_prosthetic_wing_icon.py
This reads no game, MOD, or previous art file. Geometry and colours below are
development placeholders and are not the final prosthetic-wing design.
"""

from pathlib import Path

from PIL import Image, ImageDraw


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "Textures" / "Caelavi" / "Items" / "ProstheticWing.png"
SCALE = 4
SIZE = 128


def scaled_points(points):
    return [(round(x * SCALE), round(y * SCALE)) for x, y in points]


def polygon(draw, points, fill, outline="#263a46", width=2):
    path = scaled_points(points)
    draw.polygon(path, fill=fill)
    draw.line(path + [path[0]], fill=outline, width=round(width * SCALE), joint="curve")


def main():
    image = Image.new("RGBA", (SIZE * SCALE, SIZE * SCALE), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)

    # Separate blade shapes read as a folded wing, with a simple joint at left.
    polygon(draw, [(41, 63), (68, 28), (110, 12), (99, 52), (64, 78)], "#9fb6bf")
    polygon(draw, [(42, 70), (78, 49), (116, 42), (96, 77), (56, 91)], "#6e929e")
    polygon(draw, [(45, 75), (81, 72), (107, 84), (77, 101), (51, 95)], "#486f80")

    # Gold ribs and a steel attachment mark make it identifiable at item size.
    draw.line(scaled_points([(51, 71), (91, 35)]), fill="#d4ae69", width=3 * SCALE)
    draw.line(scaled_points([(53, 76), (99, 63)]), fill="#d4ae69", width=3 * SCALE)
    draw.ellipse((25 * SCALE, 55 * SCALE, 57 * SCALE, 87 * SCALE),
                 fill="#aebdc1", outline="#263a46", width=3 * SCALE)
    draw.ellipse((35 * SCALE, 65 * SCALE, 47 * SCALE, 77 * SCALE),
                 fill="#506b77", outline="#263a46", width=2 * SCALE)

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    image.resize((SIZE, SIZE), Image.Resampling.LANCZOS).save(OUTPUT)
    print(OUTPUT)


if __name__ == "__main__":
    main()
