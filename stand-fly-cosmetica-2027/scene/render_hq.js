const { chromium } = require('playwright');
(async () => {
  const views = process.argv.slice(2);
  const b = await chromium.launch({ args: ['--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader','--ignore-gpu-blocklist'] });
  for (const v of views) {
    const p = await b.newPage({ viewport: { width: 4096, height: 2304 } });
    const errs=[]; p.on('pageerror', e => errs.push(e.message));
    await p.goto(`http://localhost:8765/index.html?view=${v}&w=4096&h=2304`);
    await p.waitForFunction('window.DONE===true', null, { timeout: 600000 });
    await p.screenshot({ path: `hq_${v}.png` });
    console.log(v, errs.join('|')); await p.close();
  }
  await b.close();
})();
