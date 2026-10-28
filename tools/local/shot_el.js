// Screenshot of the region spanning two text markers. usage: node shot_el.js URL OUT.png WIDTH "start text" "end text"
const { chromium } = require('playwright');
(async () => {
  const [url, out, w, a, z] = process.argv.slice(2);
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: parseInt(w), height: 900 }, hasTouch: parseInt(w) < 800, isMobile: parseInt(w) < 800 });
  await p.goto(url, { waitUntil: 'networkidle' });
  const box = await p.evaluate(([a, z]) => {
    const find = t => [...document.querySelectorAll('body *')].filter(e => e.children.length === 0 && e.textContent.includes(t))[0];
    const ea = find(a), ez = find(z) || ea; if (!ea) return null;
    const ra = ea.getBoundingClientRect(), rz = ez.getBoundingClientRect();
    return { y: ra.top + scrollY - 20, h: rz.bottom - ra.top + 60 };
  }, [a, z]);
  if (!box) { console.log('marker not found'); process.exit(1); }
  await p.screenshot({ path: out, fullPage: true, clip: { x: 0, y: Math.max(0, box.y), width: parseInt(w), height: Math.min(box.h, 2400) } });
  const info = await p.evaluate(() => [...document.querySelectorAll('.wssystemcontainer.H')].filter(r => r.querySelector(':scope > div > .carte_actu, :scope > div > .carte_evenement'))
      .map(r => ({ client: r.clientWidth, scroll: r.scrollWidth, cards: r.querySelectorAll(':scope > div > .wscontainer').length, docOverflow: document.documentElement.scrollWidth > innerWidth })));
  console.log(JSON.stringify(info));
  await b.close();
})();
