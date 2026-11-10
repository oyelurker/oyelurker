"""Render README-safe ASCII eye GIFs. Run: python assets/generate-eye.py

Inspired by the supplied canvas eye's amber iris and procedural ASCII texture.
The center is deliberately reserved for the independently updating WakaTime SVG.
Requires Pillow. No network access or credentials needed.
"""
from pathlib import Path
import math
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent
WIDTH, HEIGHT, STRIP = 1000, 560, 180
BG = (13, 17, 23)
RAMP = ".,:;i+tfjxXYUJQ0OZmwqpdbkhao*#MW&8%B@$"
def load_font():
    for name in ("C:/Windows/Fonts/consola.ttf", "DejaVuSansMono.ttf", "Courier New.ttf"):
        try:
            return ImageFont.truetype(name, 12)
        except OSError:
            pass
    return ImageFont.load_default(size=12)


FONT = load_font()


def noise(x, y):
    return (math.sin(x * 127.1 + y * 311.7 + 5.31) * 43758.5453) % 1


def frame(phase):
    im = Image.new("RGB", (WIDTH, HEIGHT), BG)
    draw = ImageDraw.Draw(im)
    for y in range(6, HEIGHT, 12):
        if STRIP <= y < HEIGHT - STRIP:
            continue
        for x in range(7, WIDTH - 7, 7):
            u = (x - WIDTH / 2) / 477
            if abs(u) >= 1:
                continue
            opening = 234 * max(0, 1 - u * u) ** .72
            center = HEIGHT / 2 + 13 * u
            dy = y - center
            edge = abs(dy) - opening
            texture = noise(x, y)
            radius = math.hypot(x - 500, y - 280)
            angle = math.atan2(y - 280, x - 500)
            if edge > 26:
                continue
            if edge > 5:
                # A sparse second contour suggests the eyelid crease.
                if abs(edge - 20) > 5 or texture < .25:
                    continue
                col, power = (91, 69, 58), .24 + .15 * texture
            elif edge > -8:
                col, power = (193, 143, 93), .56 + .35 * texture
            elif radius < 197:
                rn = radius / 197
                fibers = (.5 + .5 * math.sin(angle * 119 + rn * 24))
                fibers *= .5 + .5 * noise(round(angle * 250), round(rn * 19))
                shimmer = .94 + .06 * math.sin(phase + angle * 4 + rn * 13)
                power = (.38 + .58 * fibers) * shimmer
                rim = min(1, max(.12, (1 - rn) * 9))
                col = tuple(int(v * power * rim) for v in (225, 154, 68))
                if radius < 79:
                    col, power = (23, 30, 38), .08
                if math.hypot(x - 549, y - 143) < 17:
                    col, power = (220, 226, 226), .96
            else:
                shade = .30 + .18 * texture + .21 * (1 - abs(u))
                col = tuple(int(v * shade) for v in (148, 174, 195))
                power = .17 + .27 * texture
            char = RAMP[min(len(RAMP) - 1, int(power * (len(RAMP) - 1)))]
            draw.text((x, y), char, font=FONT, fill=col, anchor="mm")
    return im


def main():
    frames = [frame(i * math.tau / 24) for i in range(24)]
    # A shared palette prevents color flicker and preserves the dark background.
    palette = frames[0].quantize(colors=96)
    for name, box in [
        ("ascii-eye-top.gif", (0, 0, WIDTH, STRIP)),
        ("ascii-eye-bottom.gif", (0, HEIGHT - STRIP, WIDTH, HEIGHT)),
    ]:
        strips = [f.crop(box).quantize(palette=palette, dither=Image.Dither.NONE) for f in frames]
        strips[0].save(ROOT / name, save_all=True, append_images=strips[1:],
                       duration=100, loop=0, optimize=True, disposal=1)
    print("Generated two 1000 x 180 ASCII eye GIFs (24 frames, 2.4-second loop).")


if __name__ == "__main__":
    main()
