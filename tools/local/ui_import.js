// Import a .ws_data through WebSiCo's own admin form. usage: node ui_import.js ARCHIVE [password]
const { chromium } = require('playwright');
(async () => {
  const [archive, pwd = 'local'] = process.argv.slice(2);
  const b = await chromium.launch(); const p = await b.newPage();
  p.on('dialog', d => d.accept());
  await p.goto('http://127.0.0.1:8080/ws_tools.html?mode=1');
  if (await p.$('#ws_turlut12')) {
    await p.fill('#ws_turlut12', pwd);
    await Promise.all([p.waitForNavigation(), p.click('button[name=enter]')]);
  }
  if (!p.url().includes('ws_tools')) await p.goto('http://127.0.0.1:8080/ws_tools.html');
  const input = await p.$('#ws_upload_data');
  if (!input) { console.log('NO UPLOAD FORM; title=', await p.title()); console.log((await p.content()).slice(0, 800)); await b.close(); process.exit(1); }
  await Promise.all([p.waitForNavigation({ timeout: 120000 }), input.setInputFiles(archive)]);
  const body = await p.content();
  console.log('after upload:', p.url(), /UNZIP|DbRestore error|ZIP</.test(body) ? 'ERROR: ' + body.slice(0, 500) : 'ok');
  await b.close();
})();
