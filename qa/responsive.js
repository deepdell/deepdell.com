/* DEEPDELL pre-deploy responsive, UI/UX and brand check.
 *
 *   node qa/responsive.js            # key pages on every device, other pages on 3 sizes
 *   node qa/responsive.js --quick    # key pages on 6 devices (fast, for iterating)
 *
 * Serves the repo locally, drives Chromium through a matrix of real device profiles (phones, foldable, tablets,
 * laptops, desktop, large monitor and TV, portrait and landscape, plus Arabic RTL) and fails on layout problems.
 * Screenshots go to qa/out/ for review. Exit code 1 on any FAIL.
 */
const { chromium, devices } = require('playwright');
const http = require('http'), fs = require('fs'), path = require('path');
const ROOT = path.resolve(__dirname, '..'), OUT = path.join(__dirname, 'out');
fs.mkdirSync(OUT, { recursive: true });
const quick = process.argv.includes('--quick');

const MIME = { '.html': 'text/html', '.js': 'text/javascript', '.css': 'text/css', '.svg': 'image/svg+xml', '.xml': 'text/xml', '.json': 'application/json', '.png': 'image/png', '.jpg': 'image/jpeg', '.webp': 'image/webp', '.woff2': 'font/woff2', '.txt': 'text/plain' };
const server = http.createServer((q, r) => {
  let p = decodeURIComponent(q.url.split('?')[0]); if (p.endsWith('/')) p += 'index.html';
  fs.readFile(path.join(ROOT, p), (e, b) => { if (e) { r.writeHead(404); r.end('not found'); return; } r.writeHead(200, { 'content-type': MIME[path.extname(p)] || 'application/octet-stream' }); r.end(b); });
});

const D = n => devices[n] ? { name: n, ...devices[n] } : null;
const custom = (name, w, h, touch = false) => ({ name, viewport: { width: w, height: h }, deviceScaleFactor: 1, isMobile: touch, hasTouch: touch, userAgent: devices['Desktop Chrome'].userAgent });
const MATRIX = [
  custom('Galaxy Z Fold folded 280', 280, 653, true), custom('Small phone 320', 320, 568, true), D('iPhone SE'), D('iPhone 13'), D('iPhone 14 Pro Max'),
  D('Pixel 7'), D('Galaxy S9+'), D('iPhone 13 landscape'), D('Galaxy S9+ landscape'),
  D('iPad Mini'), D('iPad (gen 7)'), D('iPad Pro 11'), D('iPad Pro 11 landscape'), D('Galaxy Tab S4'),
  custom('Laptop 1280x720', 1280, 720), custom('Laptop 1366x768', 1366, 768), custom('Desktop 1440x900', 1440, 900), custom('Full HD 1920x1080', 1920, 1080),
  custom('QHD monitor 2560x1440', 2560, 1440), custom('TV 4K 3840x2160', 3840, 2160),
].filter(Boolean);
const QUICK = ['Small phone 320', 'iPhone SE', 'Pixel 7', 'iPad Mini', 'Laptop 1366x768', 'Full HD 1920x1080'];
const THIN = ['Small phone 320', 'iPad Mini', 'Desktop 1440x900'];
const KEY = ['/', '/services.html', '/pricing.html', '/tools.html', '/arcade.html', '/contact.html', '/blog/', '/blog/utm-tracking-guide-for-online-stores.html', '/ar/', '/ar/pricing.html'];
const ALL = fs.readdirSync(ROOT).filter(f => f.endsWith('.html')).map(f => '/' + f).concat(fs.readdirSync(path.join(ROOT, 'blog')).filter(f => f.endsWith('.html') && f !== 'index.html').map(f => '/blog/' + f));
const OTHER = ALL.filter(p => !KEY.includes(p) && p !== '/index.html' && p !== '/data.html');

const lum = ([r, g, b]) => { const f = v => { v /= 255; return v <= .03928 ? v / 12.92 : ((v + .055) / 1.055) ** 2.4; }; return .2126 * f(r) + .7152 * f(g) + .0722 * f(b); };

async function inspect(page, touch) {
  return page.evaluate(({ touch }) => {
    const vw = document.documentElement.clientWidth, res = { fail: [], warn: [] };
    const vis = el => { const s = getComputedStyle(el), r = el.getBoundingClientRect(); return s.display !== 'none' && s.visibility !== 'hidden' && +s.opacity > 0 && r.width > 0 && r.height > 0 && !el.closest('[hidden],[aria-hidden="true"]'); };
    const desc = el => el.tagName.toLowerCase() + (el.id ? '#' + el.id : '') + (typeof el.className === 'string' && el.className ? '.' + el.className.trim().split(/\s+/).slice(0, 2).join('.') : '');
    // 1. horizontal overflow
    if (document.documentElement.scrollWidth > vw + 1) {
      const off = [...document.querySelectorAll('body *')].filter(e => { const r = e.getBoundingClientRect(); return vis(e) && r.right > vw + 1 && getComputedStyle(e).position !== 'fixed' && !e.closest('.nav-submenu,.lang-menu,.fx-net,.noise'); }).slice(0, 3).map(desc);
      res.fail.push('horizontal scroll: page is ' + document.documentElement.scrollWidth + 'px wide in a ' + vw + 'px viewport (' + off.join(', ') + ')');
    }
    // 2. viewport and document basics
    if (!document.querySelector('meta[name="viewport"]')) res.fail.push('missing viewport meta');
    if (document.querySelectorAll('h1').length !== 1) res.fail.push('page has ' + document.querySelectorAll('h1').length + ' H1 elements');
    if (!document.querySelector('main')) res.fail.push('missing <main> landmark');
    if (!document.documentElement.lang) res.fail.push('missing html lang');
    // 3. header: brand, menu and CTA must not collide, and a menu must be reachable
    const hdr = document.querySelector('.site-header');
    if (hdr) {
      const parts = [...hdr.children].filter(vis).map(e => [desc(e), e.getBoundingClientRect()]);
      for (let i = 0; i < parts.length; i++) for (let j = i + 1; j < parts.length; j++) {
        const a = parts[i][1], b = parts[j][1], ox = Math.min(a.right, b.right) - Math.max(a.left, b.left), oy = Math.min(a.bottom, b.bottom) - Math.max(a.top, b.top);
        if (ox > 2 && oy > 2) res.fail.push('header overlap: ' + parts[i][0] + ' and ' + parts[j][0]);
      }
      parts.forEach(([n, r]) => { if (r.right > vw + 1 || r.left < -1) res.fail.push('header item off-screen: ' + n); });
      const nav = hdr.querySelector('.nav'), menu = hdr.querySelector('.menu');
      if (nav && getComputedStyle(nav).display === 'none' && !(menu && vis(menu))) res.fail.push('navigation hidden and no menu button');
    }
    // 4. tap targets
    const targets = [...document.querySelectorAll('button, [role="button"], input:not([type="hidden"]):not([type="checkbox"]):not([type="radio"]), select, textarea, .btn, .nav a, .header-cta, .menu, summary')].filter(vis);
    const small = targets.filter(e => { const r = e.getBoundingClientRect(); return !e.closest('.sr-only') && (r.width < 24 || r.height < 24); });
    if (small.length) res.fail.push(small.length + ' controls smaller than 24x24px (WCAG 2.2): ' + small.slice(0, 3).map(desc).join(', '));
    if (touch) { const m = targets.filter(e => { const r = e.getBoundingClientRect(); return r.height < 40 && !e.closest('.nav') && !e.matches('select,input,textarea'); }); if (m.length > 3) res.warn.push(m.length + ' touch controls under 40px tall'); }
    // 5. images
    const bad = [...document.images].filter(i => vis(i) && (!i.complete || i.naturalWidth === 0) && !i.loading).map(i => i.getAttribute('src'));
    if (bad.length) res.fail.push('broken images: ' + bad.slice(0, 3).join(', '));
    const noalt = [...document.images].filter(i => !i.hasAttribute('alt')).length; if (noalt) res.fail.push(noalt + ' images without alt attribute');
    const wide = [...document.images].filter(i => vis(i) && i.getBoundingClientRect().right > vw + 1); if (wide.length) res.fail.push('image wider than viewport: ' + desc(wide[0]));
    // 6. text readability
    const texts = [...document.querySelectorAll('p, li, td, th, label, a, span, h1, h2, h3, h4, button, small')].filter(e => vis(e) && [...e.childNodes].some(n => n.nodeType === 3 && n.textContent.trim().length > 2));
    const tiny = texts.filter(e => parseFloat(getComputedStyle(e).fontSize) < 10); if (tiny.length > 12) res.warn.push(tiny.length + ' text elements under 10px');
    const clip = texts.filter(e => { const s = getComputedStyle(e); return (s.overflow === 'hidden') && e.scrollWidth > e.clientWidth + 2 && s.textOverflow !== 'ellipsis' && !e.closest('.marquee,.ticker,.fx-net'); });
    if (clip.length) res.fail.push('text clipped by its container: ' + clip.slice(0, 3).map(desc).join(', '));
    // 7. contrast of body text against a solid background
    const bgOf = el => { for (let e = el; e; e = e.parentElement) { const s = getComputedStyle(e); if (s.backgroundImage !== 'none') return null; const m = s.backgroundColor.match(/[\d.]+/g); if (m && (m.length < 4 || +m[3] > .9)) return m.slice(0, 3).map(Number); } return [3, 10, 20]; };
    const lm = c => { const f = v => { v /= 255; return v <= .03928 ? v / 12.92 : ((v + .055) / 1.055) ** 2.4; }; return .2126 * f(c[0]) + .7152 * f(c[1]) + .0722 * f(c[2]); };
    let low = [];
    texts.slice(0, 400).forEach(e => { const bg = bgOf(e); if (!bg) return; const s = getComputedStyle(e); if (s.webkitTextFillColor === 'rgba(0, 0, 0, 0)' || s.color.includes('rgba(') && /,\s*0\)/.test(s.color)) return; const m = s.color.match(/[\d.]+/g).slice(0, 3).map(Number); const a = lm(m), b = lm(bg), r = (Math.max(a, b) + .05) / (Math.min(a, b) + .05); if (r < 3) low.push(desc(e) + ' ' + r.toFixed(1) + ':1'); });
    if (low.length) res.fail.push(low.length + ' text elements below 3:1 contrast: ' + low.slice(0, 3).join('; '));
    // 8. brand
    const body = getComputedStyle(document.body);
    if (!/Manrope/i.test(body.fontFamily)) res.fail.push('brand body font Manrope not applied (' + body.fontFamily.slice(0, 40) + ')');
    const mono = document.querySelector('.section-kicker, .card-code, .eyebrow'); if (mono && document.documentElement.lang !== 'ar' && !/DM Mono/i.test(getComputedStyle(mono).fontFamily)) res.fail.push('brand mono font DM Mono not applied');
    if (getComputedStyle(document.documentElement).getPropertyValue('--cyan').trim().toLowerCase() !== '#24e4f2') res.fail.push('brand cyan token --cyan changed');
    if (!document.querySelector('.brand img, .brand svg')) res.fail.push('brand logo missing from header');
    const meta = document.querySelector('meta[name="theme-color"]'); if (!meta) res.warn.push('no theme-color meta');
    // 9. forms and controls have names
    const unl = [...document.querySelectorAll('input:not([type="hidden"]):not([type="submit"]), select, textarea')].filter(e => vis(e) && !e.labels?.length && !e.getAttribute('aria-label') && !e.getAttribute('aria-labelledby') && !e.getAttribute('placeholder'));
    if (unl.length) res.fail.push(unl.length + ' form fields without a label: ' + desc(unl[0]));
    const noname = [...document.querySelectorAll('button, a')].filter(e => vis(e) && !e.textContent.trim() && !e.getAttribute('aria-label') && !e.getAttribute('title') && !e.querySelector('img[alt]:not([alt=""])'));
    if (noname.length) res.warn.push(noname.length + ' buttons or links without an accessible name');
    return res;
  }, { touch });
}

(async () => {
  await new Promise(r => server.listen(0, r)); const base = 'http://localhost:' + server.address().port;
  const browser = await chromium.launch();
  const fails = [], warns = new Map(); let runs = 0;
  const plan = [];
  const keyDevices = quick ? MATRIX.filter(d => QUICK.includes(d.name)) : MATRIX;
  KEY.concat(['/index.html'].slice(0, 0)).forEach(p => keyDevices.forEach(d => plan.push([p, d, true])));
  if (!quick) OTHER.forEach(p => MATRIX.filter(d => THIN.includes(d.name)).forEach(d => plan.push([p, d, false])));
  const byDevice = new Map(); plan.forEach(x => { const k = x[1].name; (byDevice.get(k) || byDevice.set(k, []).get(k)).push(x); });
  for (const [name, items] of byDevice) {
    const d = items[0][1]; const { name: _n, ...opts } = d;
    const ctx = await browser.newContext({ ...opts, reducedMotion: 'reduce' });
    await ctx.addInitScript(() => { try { localStorage.setItem('dd-signup-dismissed', '1'); localStorage.setItem('dd-consent', 'rejected'); } catch (e) {} });
    for (const [p, , shot] of items) {
      const page = await ctx.newPage(); const errs = [];
      page.on('pageerror', e => errs.push('JS error: ' + e.message));
      page.on('response', r => { if (r.status() >= 400 && r.url().startsWith(base)) errs.push(r.status() + ' ' + r.url().replace(base, '')); });
      try {
        await page.goto(base + p, { waitUntil: 'load', timeout: 30000 }); await page.waitForTimeout(350);
        await page.evaluate(() => { document.querySelectorAll('.deepdell-consent,#dd-signup').forEach(e => e.remove()); document.querySelectorAll('.reveal-item').forEach(e => e.classList.add('visible')); });
        const r = await inspect(page, !!opts.hasTouch); runs++;
        r.fail.concat(errs).forEach(m => fails.push(`${name} ${p}: ${m}`)); r.warn.forEach(m => { const k = `${p}: ${m}`; warns.set(k, (warns.get(k) || []).concat(name)); });
        if (shot && !quick) await page.screenshot({ path: path.join(OUT, `${name.replace(/[^a-z0-9]+/gi, '_')}__${p.replace(/[^a-z0-9]+/gi, '_') || 'home'}.png`), fullPage: false });
      } catch (e) { fails.push(`${name} ${p}: could not load (${e.message.split('\n')[0]})`); }
      await page.close();
    }
    await ctx.close();
  }
  await browser.close(); server.close();
  const uniq = [...new Set(fails)];
  console.log(`\nRESPONSIVE / UI / BRAND CHECK: ${runs} page-device combinations across ${byDevice.size} devices`);
  [...warns].slice(0, 25).forEach(([k, v]) => console.log('  WARN ', k, `(${v.length} devices)`));
  uniq.slice(0, 80).forEach(f => console.log('  FAIL ', f)); if (uniq.length > 80) console.log(`  ... and ${uniq.length - 80} more`);
  console.log(`\n${uniq.length ? uniq.length + ' failures' : 'all clear'}, ${warns.size} warnings. Screenshots: qa/out/`);
  process.exit(uniq.length ? 1 : 0);
})();
