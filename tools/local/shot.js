// usage (needs playwright): node tools/local/shot.js URL OUT.png [width]
const { chromium } = require('playwright');
(async () => {
  const [url, out, w] = process.argv.slice(2);
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: parseInt(w || '1366'), height: 900 } });
  const errs = [];
  p.on('requestfailed', r => errs.push('FAIL ' + r.url()));
  p.on('response', r => { if (r.status() >= 400) errs.push(r.status() + ' ' + r.url()); });
  await p.goto(url, { waitUntil: 'networkidle', timeout: 60000 }).catch(e => errs.push('goto ' + e.message));
  await p.screenshot({ path: out, fullPage: true });
  console.log(errs.filter(e => !e.includes('gstatic') && !e.includes('facebook')).slice(0, 15).join('\n') || 'no local errors');
  await b.close();
})();
