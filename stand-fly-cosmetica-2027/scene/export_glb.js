const { chromium } = require('playwright'); const fs = require('fs');
(async () => {
  const b = await chromium.launch({ args: ['--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader'] });
  const p = await b.newPage({ viewport: { width: 640, height: 360 } });
  p.on('pageerror', e => console.log('ERR', e.message));
  await p.goto('http://localhost:8765/index.html?view=front&w=640&h=360&export=1&noao=1');
  await p.waitForFunction('window.EXPORTED===true', null, { timeout: 600000 });
  const err = await p.evaluate(() => window.EXPORT_ERR); if (err) console.log('EXPORT_ERR', err);
  const b64 = await p.evaluate(() => window.GLB);
  fs.writeFileSync('stand.glb', Buffer.from(b64, 'base64')); console.log('glb bytes', fs.statSync('stand.glb').size);
  await b.close();
})();
