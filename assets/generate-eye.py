"""Encode render-eye.cjs frames into a README-safe GIF. Requires Pillow."""
from pathlib import Path
from PIL import Image
ROOT = Path(__file__).resolve().parent
paths = sorted((ROOT / '.eye-frames').glob('*.png'))
if len(paths) != 180:
    raise SystemExit('Run node assets/render-eye.cjs first (expected 180 PNGs).')
frames = [Image.open(p).convert('RGB') for p in paths]
samples = frames[::10]
atlas = Image.new('RGB', (800, 400 * len(samples)))
for i, sample in enumerate(samples):
    atlas.paste(sample, (0, 400 * i))
palette = atlas.quantize(colors=128)
encoded = [f.quantize(palette=palette, dither=Image.Dither.NONE) for f in frames]
encoded[0].save(ROOT / 'ascii-eye.gif', save_all=True, append_images=encoded[1:],
                duration=[100] * 179 + [700], loop=0, optimize=True, disposal=1)
print(f'Created ascii-eye.gif: {(ROOT / "ascii-eye.gif").stat().st_size:,} bytes')
import runpy
runpy.run_path(str(ROOT / 'build-eye-header.py'), run_name='__main__')
for f in frames:
    f.close()
for p in paths:
    p.unlink()
(ROOT / '.eye-frames').rmdir()
