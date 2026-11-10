"""Full-width character texture matching the user's supplied ASCII reference."""
import math
from PIL import Image, ImageDraw, ImageFont


def render(iris_frames, openings, palette):
    palette = palette.copy()
    # Reserve a separate amber ramp for the character-built outer eyelid.
    for i in range(64):
        amount = i / 63
        palette[(128 + i) * 3:(129 + i) * 3] = [
            round(76 + 131 * amount), round(49 + 97 * amount), round(27 + 46 * amount)]
    try:
        font = ImageFont.truetype('C:/Windows/Fonts/consola.ttf', 9)
    except OSError:
        font = ImageFont.load_default()
    ramp = '.,:;i+tfjxXYUJQ0OZmwqpdbkhao*#MW&8%B@$'
    height = iris_frames[0].height + 30
    output = []
    for number, (iris, opening) in enumerate(zip(iris_frames, openings)):
        frame = Image.new('P', (656, height), 0)
        frame.putpalette(palette)
        draw = ImageDraw.Draw(frame)
        boundary = [height - 1 - (height - 9) * opening * max(0, 1 - ((x - 327.5) / 327.5) ** 2) ** .72 for x in range(656)]
        for row, y in enumerate(range(5, height, 8)):
            for column in range(120):
                x = round(3 + column * 5.46)
                if x >= 654 or y - boundary[x] < -2:
                    continue
                # Reserve the iris area so two different character grids do
                # not overlap and blur its original radial fibers.
                if math.hypot(x - 328, y - height) < 127:
                    continue
                edge = y - boundary[x]
                texture = (math.sin(column * 127.1 + row * 311.7 + 5.31) * 43758.5453) % 1
                power = .19 + .43 * texture
                shade = 24 + 29 * texture + 14 * (1 - abs(x - 328) / 328)
                if edge < 9:
                    power, shade = .29 + .46 * texture, 33 + 39 * texture
                # Fine vessels are represented by brighter glyphs, never lines.
                for branch in range(3):
                    side = min(x, 655 - x)
                    vein = height - 2 - opening * (8 + side / 205 * (29 + branch * 19) + 4 * math.sin(side / 24 + branch))
                    if side < 205 and abs(y - vein) < 2:
                        power, shade = min(.93, power + .15), shade + 13
                shade *= .95 + .05 * math.sin(number * .14 + column * .2)
                char = ramp[min(len(ramp) - 1, int(power * (len(ramp) - 1)))]
                color = 128 + round(15 + 39 * texture) if edge < 9 else min(104, round(shade))
                draw.text((x, y), char, fill=color, font=font, anchor='mm')
        # Preserve the original detailed, moving ASCII iris at the center.
        frame.paste(iris, (0, 30), iris.point(lambda p: 255 if p else 0, mode='L'))
        # A sparse row of warm glyphs traces the silhouette, without a smooth
        # stroke or a second parallel contour. It follows the same blink.
        if opening >= .03:
            for column, x in enumerate(range(5, 652, 6)):
                texture = (math.sin(column * 127.1 + 5.31) * 43758.5453) % 1
                char = 'YXVUj+*#'[min(7, int(texture * 8))]
                draw.text((x, round(boundary[x]) + 1), char,
                          fill=128 + round(10 + 37 * texture), font=font, anchor='mm')
        clip = [(x, round(y) - 3) for x, y in enumerate(boundary)]
        ImageDraw.Draw(frame).polygon([(0, 0), (655, 0)] + clip[::-1], fill=0)
        if opening < .03:
            draw = ImageDraw.Draw(frame)
            for x in range(4, 654, 6):
                draw.text((x, height - 3), '_', fill=143, font=font, anchor='mm')
        output.append(frame)
    return output
