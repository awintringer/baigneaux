// Responsive audit of every page of the local instance.
// usage: node tools/local/responsive_check.js [widths=1366,1024,820,390] > report.json
const { chromium } = require('playwright');
const fs = require('fs'), path = require('path');
(async () => {
  const widths = (process.argv[2] || '1366,1024,820,390').split(',').map(Number);
  const site = path.join(__dirname, '..', '..', 'site', 'pages');
  const urls = fs.readdirSync(site).map(f => JSON.parse(fs.readFileSync(path.join(site, f))).row[2]).filter(Boolean);
  const b = await chromium.launch(); const report = [];
  for (const w of widths) {
    const ctx = await b.newContext({ viewport: { width: w, height: 900 }, isMobile: false });
    const p = await ctx.newPage(); const bad = [];
    p.on('response', r => { if (r.status() >= 400 && !/gstatic|facebook|google/.test(r.url())) bad.push(r.status() + ' ' + r.url()); });
    for (const u of urls) {
      bad.length = 0;
      await p.goto(`http://127.0.0.1:8080/${u === 'home' ? '' : u + '.html'}`, { waitUntil: 'networkidle', timeout: 60000 }).catch(() => {});
      let r; try { r = await p.evaluate(() => {
        const vw = innerWidth, out = { docW: document.documentElement.scrollWidth, overflow: [], brokenImg: [], wideImg: [] };
        const inScroller = e => { for (let a = e.parentElement; a; a = a.parentElement) { const s = getComputedStyle(a); if (/(auto|scroll|hidden)/.test(s.overflowX)) return true; } return false; };
        document.querySelectorAll('body *').forEach(e => {
          const rc = e.getBoundingClientRect();
          if (rc.width && rc.right > vw + 2 && !inScroller(e) && getComputedStyle(e).position !== 'fixed') {
            if (!e.children.length || e.tagName === 'IMG') out.overflow.push((e.tagName + '.' + [...e.classList].join('.')).slice(0, 60) + ' r=' + Math.round(rc.right) + ' "' + (e.textContent || e.getAttribute('src') || '').trim().slice(0, 40) + '"');
          }
        });
        document.querySelectorAll('img').forEach(i => { if (i.complete && i.naturalWidth === 0 && i.getAttribute('src')) out.brokenImg.push(i.getAttribute('src')); });
        return out;
      }); } catch (e) { report.push({ w, page: u, error: e.message.slice(0, 80) }); continue; }
      const issue = r.docW > w + 2 || r.overflow.length || r.brokenImg.length || bad.length;
      if (issue) report.push({ w, page: u, docW: r.docW, overflow: r.overflow.slice(0, 6), nOverflow: r.overflow.length, brokenImg: r.brokenImg, http: [...bad].slice(0, 5) });
    }
    await ctx.close();
  }
  console.log(JSON.stringify(report, null, 1)); await b.close();
})();
