const { chromium } = require('playwright');
(async () => {
  const views = process.argv.slice(2);
  const b = await chromium.launch({ args: ['--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader','--ignore-gpu-blocklist'] });
  for (const v of views) {
    const p = await b.newPage({ viewport: { width: 2560, height: 1440 } });
    const errs = []; p.on('console', m => { if (m.type()==='error') errs.push(m.text()); }); p.on('pageerror', e => errs.push(e.message));
    const [vv,q]=v.split('+'); await p.goto(`http://localhost:8765/index.html?view=${vv}${q?'&'+q:''}`);
    await p.waitForFunction('window.DONE===true', null, { timeout: 300000 }).catch(e=>errs.push('timeout'));
    await p.screenshot({ path: `out_${v.replace(/[+=&]/g,'_')}.png` });
    console.log(v, errs.slice(0,5).join(' | '));
    await p.close();
  }
  await b.close();
})();
