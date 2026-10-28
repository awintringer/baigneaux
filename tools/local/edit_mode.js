// Open a page in WebSiCo edit mode (super-user password "local"), report JS errors, take a screenshot.
// usage: node tools/local/edit_mode.js [page.html] [out.png] [width]
const { chromium } = require('playwright');
(async () => {
  const [pg = '', out = '/tmp/edit.png', w = '1366'] = process.argv.slice(2);
  const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: parseInt(w), height: 900 } });
  const errs = [];
  p.on('pageerror', e => errs.push('PAGEERROR ' + e.message.slice(0, 300)));
  p.on('console', m => { if (m.type() === 'error') errs.push('CONSOLE ' + m.text().slice(0, 300)); });
  p.on('dialog', d => { errs.push('DIALOG ' + d.message().slice(0, 200)); d.dismiss(); });
  await p.goto('http://127.0.0.1:8080/' + pg + '?mode=1', { waitUntil: 'networkidle' });
  if (await p.$('#ws_turlut12')) { await p.fill('#ws_turlut12', 'local'); await Promise.all([p.waitForNavigation({ waitUntil: 'networkidle' }), p.click('button[name=enter]')]); }
  await p.waitForTimeout(1500);
  const info = await p.evaluate(() => ({ editables: document.querySelectorAll('.ws_editable_container').length, title: document.title, bodyLen: document.body.innerText.length }));
  await p.screenshot({ path: out });
  console.log(JSON.stringify(info)); console.log(errs.filter(e => !/gstatic|facebook/.test(e)).slice(0, 15).join('\n') || 'no errors');
  await b.close();
})();
