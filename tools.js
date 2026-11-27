/* DEEPDELL free tools. Everything runs in the visitor's browser: nothing is sent, stored on a server or tracked. */
(function () {
  const root = document.documentElement;
  const box = document.querySelector('[data-tool]');
  if (!box) return;
  const kind = box.getAttribute('data-tool');
  const lang = root.lang || 'en';
  const LOC = lang === 'ar' ? 'ar-u-nu-latn' : lang;
  const $ = (s, r) => (r || box).querySelector(s);
  const $$ = (s, r) => [...(r || box).querySelectorAll(s)];
  const f = box.querySelector('form');
  const val = n => { const e = f.elements[n]; if (!e) return NaN; const v = parseFloat(String(e.value).replace(',', '.')); return isFinite(v) ? v : NaN; };
  const txt = n => (f.elements[n] ? String(f.elements[n].value).trim() : '');
  const out = (k, v) => { $$('[data-out="' + k + '"]').forEach(e => { e.textContent = v; }); };
  const show = (sel, on) => $$(sel).forEach(e => { e.hidden = !on; });
  const nf = (d, o) => new Intl.NumberFormat(LOC, Object.assign({ maximumFractionDigits: d }, o || {}));
  const pct = v => isFinite(v) ? nf(1).format(v * 100) + '%' : '—';
  const times = v => isFinite(v) ? nf(2, { minimumFractionDigits: 2 }).format(v) + '×' : '—';
  const ZERO = ['IDR', 'PKR'];
  const money = (v, cur) => isFinite(v) ? new Intl.NumberFormat(LOC, { style: 'currency', currency: cur, maximumFractionDigits: ZERO.includes(cur) ? 0 : 2, minimumFractionDigits: ZERO.includes(cur) ? 0 : 2 }).format(v) : '—';
  const plain = (v, d) => isFinite(v) ? nf(d == null ? 0 : d).format(v) : '—';
  const raf = fn => { let q = 0; return () => { if (q) return; q = 1; requestAnimationFrame(() => { q = 0; fn(); }); }; };

  /* currency selector shared with the pricing page */
  const sel = f.elements.cur;
  if (sel) {
    const L = { fr: 'EUR', de: 'EUR', es: 'EUR', it: 'EUR', ar: 'AED', ms: 'MYR', id: 'IDR' };
    let c = null;
    try { c = localStorage.getItem('dd-currency'); } catch (e) { }
    if (!c || ![...sel.options].some(o => o.value === c)) c = L[lang] || 'USD';
    sel.value = c;
    sel.addEventListener('change', () => { try { localStorage.setItem('dd-currency', sel.value); } catch (e) { } });
  }

  /* copy helper with a visible "Copied" state */
  function copy(text, btn) {
    const done = () => {
      const a = btn.querySelector('.b1'), b = btn.querySelector('.b2');
      if (a && b) { a.hidden = true; b.hidden = false; setTimeout(() => { a.hidden = false; b.hidden = true; }, 1800); }
    };
    if (navigator.clipboard && navigator.clipboard.writeText) { navigator.clipboard.writeText(text).then(done, () => fallback()); } else fallback();
    function fallback() {
      const t = document.createElement('textarea'); t.value = text; t.style.position = 'fixed'; t.style.opacity = '0';
      document.body.appendChild(t); t.select(); try { document.execCommand('copy'); done(); } catch (e) { } t.remove();
    }
  }

  const tools = {
    /* ───────── UTM link builder ───────── */
    utm() {
      const run = () => {
        const raw = txt('url');
        let u = null, bad = false;
        if (raw) { try { u = new URL(/^https?:\/\//i.test(raw) ? raw : 'https://' + raw); if (!/\./.test(u.hostname)) throw 0; } catch (e) { bad = true; } }
        show('[data-msg="url"]', bad);
        const src = txt('source'), med = txt('medium'), cam = txt('campaign');
        if (!u || bad || !src || !med || !cam) { out('link', ''); $('.tl-out').classList.add('is-empty'); $('[data-copy]').disabled = true; return; }
        [['utm_source', src], ['utm_medium', med], ['utm_campaign', cam], ['utm_term', txt('term')], ['utm_content', txt('content')]].forEach(([k, v]) => { if (v) u.searchParams.set(k, v); else u.searchParams.delete(k); });
        out('link', u.toString()); $('.tl-out').classList.remove('is-empty'); $('[data-copy]').disabled = false;
      };
      f.addEventListener('input', run);
      $$('[data-preset]').forEach(b => b.addEventListener('click', () => { const [s, m] = b.dataset.preset.split('|'); f.elements.source.value = s; f.elements.medium.value = m; run(); }));
      $('[data-copy]').addEventListener('click', e => copy($('[data-out="link"]').textContent, e.currentTarget));
      f.addEventListener('reset', () => setTimeout(run, 0));
      run();
    },

    /* ───────── ad performance ───────── */
    ad() {
      const run = () => {
        const cur = sel.value, spend = val('spend'), rev = val('revenue'), orders = val('orders'), gm = val('margin') / 100, imp = val('impressions'), clk = val('clicks');
        const ready = spend > 0 && rev >= 0;
        show('[data-state="empty"]', !ready); show('[data-state="ready"]', ready);
        if (!ready) return;
        const roas = rev / spend, be = gm > 0 ? 1 / gm : NaN, profit = rev * (isFinite(gm) ? gm : 0) - spend;
        out('roas', times(roas)); out('be', times(be));
        out('cpa', orders > 0 ? money(spend / orders, cur) : '—'); out('aov', orders > 0 ? money(rev / orders, cur) : '—');
        out('profit', isFinite(gm) ? money(profit, cur) : '—');
        out('ctr', imp > 0 && clk >= 0 ? pct(clk / imp) : '—'); out('cpc', clk > 0 ? money(spend / clk, cur) : '—');
        out('cpm', imp > 0 ? money(spend / imp * 1000, cur) : '—'); out('cvr', clk > 0 && orders >= 0 ? pct(orders / clk) : '—');
        let v = 'mid';
        if (isFinite(be)) v = roas > be * 1.05 ? 'good' : roas < be * 0.95 ? 'bad' : 'mid';
        $$('[data-verdict]').forEach(e => { e.hidden = e.dataset.verdict !== v || !isFinite(be); });
        const pr = $('[data-out="profit"]'); if (pr) { pr.classList.toggle('good', profit > 0); pr.classList.toggle('bad', profit < 0); }
      };
      f.addEventListener('input', run); f.addEventListener('change', run); f.addEventListener('reset', () => setTimeout(run, 0)); run();
    },

    /* ───────── profit and pricing ───────── */
    profit() {
      const run = () => {
        const cur = sel.value, p = val('price'), c = val('cost') || 0, s = val('ship') || 0, a = (val('platform') || 0) / 100, b = (val('payment') || 0) / 100, fx = val('fixed') || 0, d = val('ads') || 0, t = (val('target') || 0) / 100;
        const ready = p > 0;
        show('[data-state="empty"]', !ready); show('[data-state="ready"]', ready);
        if (!ready) return;
        const fees = p * (a + b) + fx, profit = p - c - s - fees - d, base = c + s + fx + d;
        out('profit', money(profit, cur)); out('margin', pct(profit / p)); out('markup', c > 0 ? pct((p - c) / c) : '—'); out('fees', money(fees + d, cur));
        out('be', 1 - a - b > 0 ? money(base / (1 - a - b), cur) : '—');
        out('goal', 1 - a - b - t > 0 ? money(base / (1 - a - b - t), cur) : '—');
        const v = profit > 0.005 ? 'good' : profit < -0.005 ? 'bad' : 'mid';
        $$('[data-verdict]').forEach(e => { e.hidden = e.dataset.verdict !== v; });
        const pr = $('[data-out="profit"]'); if (pr) { pr.classList.toggle('good', profit > 0); pr.classList.toggle('bad', profit < 0); }
      };
      f.addEventListener('input', run); f.addEventListener('change', run); f.addEventListener('reset', () => setTimeout(run, 0)); run();
    },

    /* ───────── SEO and social preview ───────── */
    seo() {
      const cv = document.createElement('canvas').getContext('2d');
      const measure = (t, size, w) => { cv.font = (w || 400) + ' ' + size + 'px Arial, Helvetica, sans-serif'; return cv.measureText(t).width; };
      function clip(t, size, max, w) { // trim to a pixel width, like a search result
        if (measure(t, size, w) <= max) return t;
        let lo = 0, hi = t.length; while (lo < hi) { const m = (lo + hi + 1) >> 1; if (measure(t.slice(0, m).trimEnd() + '…', size, w) <= max) lo = m; else hi = m - 1; }
        return t.slice(0, lo).trimEnd() + '…';
      }
      const status = (el, n, lo, hi) => { const k = n === 0 ? 'none' : n < lo ? 'short' : n > hi ? 'long' : 'good'; el.dataset.s = k; $$('[data-st]', el).forEach(x => { x.hidden = x.dataset.st !== k; }); };
      const run = () => {
        const title = txt('title'), desc = txt('desc'), addr = txt('url'), site = txt('site'), img = txt('image');
        let host = '', path = '';
        try { const u = new URL(/^https?:\/\//i.test(addr) ? addr : 'https://' + (addr || 'example.com')); host = u.hostname.replace(/^www\./, ''); path = u.pathname.replace(/\/$/, '').split('/').filter(Boolean).join(' › '); } catch (e) { host = 'example.com'; }
        const t = title || $('[data-ph="title"]').textContent, d = desc || $('[data-ph="desc"]').textContent;
        const mobile = $('[data-device].on').dataset.device === 'mobile';
        const tw = mobile ? 330 : 600, dw = mobile ? 330 : 600;
        out('site', site || host); out('crumb', host + (path ? ' › ' + path : ''));
        out('gtitle', mobile ? clipMulti(t, 20, tw, 2) : clip(t, 20, tw, 400));
        out('gdesc', mobile ? clipMulti(d, 14, dw, 3) : clipMulti(d, 14, dw, 2));
        out('tcount', String(title.length)); out('dcount', String(desc.length));
        status($('[data-field="title"]'), title.length, 30, 60); status($('[data-field="desc"]'), desc.length, 70, 160);
        out('otitle', t); out('odesc', d); out('ohost', host);
        const card = $('.og-card'), im = $('.og-img');
        const ok = /^https?:\/\//i.test(img);
        im.hidden = !ok; if (ok) { if (im.getAttribute('src') !== img) im.setAttribute('src', img); } else im.removeAttribute('src');
      };
      function clipMulti(t, size, max, lines) { // approximate multi-line clamp by pixel width
        const words = t.split(/\s+/), rows = []; let cur = '';
        for (const w of words) { const n = cur ? cur + ' ' + w : w; if (measure(n, size) <= max) cur = n; else { rows.push(cur); cur = w; } }
        rows.push(cur); const fit = r => measure(r, size) <= max ? r : clip(r, size, max);
        if (rows.length <= lines) return rows.map(fit).join(' ');
        const keep = rows.slice(0, lines); keep[lines - 1] = clip(keep[lines - 1] + ' ' + rows.slice(lines).join(' '), size, max); return keep.join(' ');
      }
      f.addEventListener('input', raf(run)); f.addEventListener('reset', () => setTimeout(run, 0));
      $$('[data-device]').forEach(b => b.addEventListener('click', () => { $$('[data-device]').forEach(x => { x.classList.toggle('on', x === b); x.setAttribute('aria-pressed', String(x === b)); }); box.classList.toggle('is-mobile', b.dataset.device === 'mobile'); run(); }));
      const im = $('.og-img'); im.addEventListener('error', () => { im.hidden = true; });
      run();
    }
  };
  if (tools[kind]) tools[kind]();
})();
