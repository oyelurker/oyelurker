"""Mask the outer eye and tint its animated upper iris to the WakaTime blues.

Run after rendering ascii-eye.gif: python assets/build-eye-header.py
Pillow is the only dependency. Geometry follows eye-source.js.
"""
import math
from pathlib import Path
from PIL import Image, ImageChops, ImageDraw, ImageFont, GifImagePlugin

ROOT = Path(__file__).resolve().parent


def ease(x):
    x = max(0, min(1, x))
    return x * x * (3 - 2 * x)


def lid(u, opening):
    s = u / .78
    cu = max(0, 1 - ((s + .12) / (.88 if s < -.12 else 1.12)) ** 2) ** .8
    cl = max(0, 1 - (s - .08) ** 2) ** .9
    lower = .03 * cl + (.2 * cl - .03 * cl) * (.35 + .65 * opening)
    return lower + (-.3 * cu - lower) * opening, lower


def main():
    source = Image.open(ROOT / 'ascii-eye.gif')
    indices = list(range(8, 55)) + list(range(33, 8, -1))
    # Exact activity-grid colors, with interpolated shades for antialiased glyphs.
    stops = [(13, 17, 23), (54, 82, 108), (82, 125, 164), (137, 175, 203), (211, 226, 237)]
    palette = [13, 17, 23]
    for i in range(1, 128):
        p = (i - 1) / 126 * 4
        n = min(3, int(p))
        palette.extend(round(stops[n][c] + (stops[n + 1][c] - stops[n][c]) * (p - n)) for c in range(3))
    palette += [0] * (768 - len(palette))
    output = []
    openings = []
    for index in indices:
        t = index / 10
        z = 1 + .05 * ease(t / 5.4) + .004 * math.sin(t * .9)
        blink = 0
        if 4 <= t <= 4.36:
            d = t - 4
            blink = ease(d / .09) if d < .09 else 1 if d < .12 else 1 - ease((d - .12) / .24)
        opening_progress = ease((t - .9) / 2.4)
        opening = min(1, opening_progress * (1 + .035 * math.sin(math.pi * opening_progress))) * (1 - .985 * blink)
        openings.append(opening)
        gx = .022 * math.sin(t * 1.8) + .012 * math.sin(t * 3.1)
        gy = .011 * math.sin(t * 1.4) - .03 * blink
        # Mask out sclera, skin, and both outer corners. Keep only the iris.
        iris = Image.new('L', (800, 400))
        cx, cy, radius = 400 + gx * z * 400, 200 + gy * z * 400, .27 * z * 400
        ImageDraw.Draw(iris).ellipse((cx - radius, cy - radius, cx + radius, cy + radius), fill=255)
        aperture = Image.new('L', (800, 400))
        upper, lower = [], []
        for x in range(800):
            u = (x - 400) / (400 * z)
            a, b = lid(u, opening)
            upper.append((x, 200 + (a - .055 * (u / .78)) * z * 400))
            lower.append((x, 200 + (b - .055 * (u / .78)) * z * 400))
        ImageDraw.Draw(aperture).polygon(upper + lower[::-1], fill=255)
        mask = ImageChops.multiply(iris, aperture).crop((72, 12, 728, 200))
        source.seek(index)
        rgb = source.convert('RGB').crop((72, 12, 728, 200))
        pixels = []
        for (r, g, b), visible in zip(rgb.getdata(), mask.getdata()):
            brightness = max(r, g, b)
            pixels.append(0 if not visible or brightness < 12 else 1 + min(126, round((brightness / 255) ** .8 * 126)))
        frame = Image.new('P', rgb.size)
        frame.putpalette(palette)
        frame.putdata(pixels)
        output.append(frame)
    # Trim empty space above the iris while preserving full-width graph alignment.
    top = max(0, min(f.getbbox()[1] for f in output if f.getbbox()) - 8)
    output = [f.crop((0, top, 656, 188)) for f in output]
    # Build the entire upper eye from characters, matching the reference.
    import runpy
    render = runpy.run_path(str(ROOT / 'ascii-eye-field.py'))['render']
    output = render(output, openings, palette)
    # Write complete frames: fully transparent blink frames must retain a valid
    # full-size image descriptor rather than an empty optimized bounding box.
    with (ROOT / 'ascii-eye-header.gif').open('wb') as file:
        chunks, _ = GifImagePlugin.getheader(output[0], info={'loop': 0, 'transparency': 0})
        for chunk in chunks:
            file.write(chunk)
        for frame in output:
            for chunk in GifImagePlugin.getdata(frame, duration=100, transparency=0, disposal=2):
                file.write(chunk)
        file.write(b';')
    print('Created full-width textured ASCII upper eye with synchronized opening and blinking.')


if __name__ == '__main__':
    main()
