// Usage: node assets/render-eye.cjs [path-to-@napi-rs/canvas]
// Then: python assets/generate-eye.py (requires Pillow).
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const { createCanvas, GlobalFonts } = require(process.argv[2] || '@napi-rs/canvas');
const font = 'C:/Windows/Fonts/consola.ttf';
if (fs.existsSync(font)) GlobalFonts.registerFromPath(font, 'Consolas');
const canvas = createCanvas(800, 400);
const scene = vm.createContext({
  document: { getElementById: () => canvas },
  innerWidth: 800, innerHeight: 400, devicePixelRatio: 1,
  performance: { now: () => 0 },
  addEventListener: () => {}, requestAnimationFrame: () => {},
});
vm.runInContext(fs.readFileSync(path.join(__dirname, 'eye-source.js'), 'utf8'), scene);
const output = path.join(__dirname, '.eye-frames');
fs.mkdirSync(output, { recursive: true });
let previous = 0;
for (let i = 0; i < 180; i++) {
  const elapsed = i / 10;
  // Preserve the opening and blink, then accelerate the long flight into space.
  const time = elapsed <= 5.4 ? elapsed : elapsed <= 12.4
    ? 5.4 + (elapsed - 5.4) * 4 : 33.4 + (elapsed - 12.4);
  const steps = Math.max(1, Math.ceil((time - previous) / .1));
  for (let j = 1; j <= steps; j++) {
    scene.frameTime = previous + (time - previous) * j / steps;
    scene.frameDelta = (time - previous) / steps;
    vm.runInContext('render(frameTime, frameDelta)', scene);
  }
  fs.writeFileSync(path.join(output, `${String(i).padStart(3, '0')}.png`), canvas.toBuffer('image/png'));
  previous = time;
  if (i % 30 === 0) console.log(`Rendered ${i}/180 frames`);
}
console.log('Rendered 180 frames. Run python assets/generate-eye.py to encode.');
