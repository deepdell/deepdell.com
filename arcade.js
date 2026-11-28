/* DEEPDELL Cart Dash: a tiny canvas arcade game. No dependencies, no network. Scores stay in this browser. */
(function () {
  var root = document.querySelector('[data-arcade]');
  if (!root) return;
  var cv = root.querySelector('canvas'), ctx = cv.getContext('2d');
  var $ = function (s) { return root.querySelector(s); };
  var W = 360, H = 520, KEY = 'dd-arcade';
  var reduce = window.matchMedia && matchMedia('(prefers-reduced-motion: reduce)').matches;
  var save = { best: 0, streak: 0, last: '', plays: 0, badges: [] };
  try { Object.assign(save, JSON.parse(localStorage.getItem(KEY) || '{}')); } catch (e) {}
  function persist() { try { localStorage.setItem(KEY, JSON.stringify(save)); } catch (e) {} }
  function today() { var d = new Date(); return d.getFullYear() + '-' + ('0' + (d.getMonth() + 1)).slice(-2) + '-' + ('0' + d.getDate()).slice(-2); }
  function dayNo() { return Math.floor((Date.now() - new Date(2026, 0, 1)) / 864e5) + 1; }
  function seeded(str) { var h = 1779033703 ^ str.length; for (var i = 0; i < str.length; i++) { h = Math.imul(h ^ str.charCodeAt(i), 3432918353); h = h << 13 | h >>> 19; }
    var a = h >>> 0; return function () { a |= 0; a = a + 0x6D2B79F5 | 0; var t = Math.imul(a ^ a >>> 15, 1 | a); t = t + Math.imul(t ^ t >>> 7, 61 | t) ^ t; return ((t ^ t >>> 14) >>> 0) / 4294967296; }; }
  var BADGES = [[100, 'rookie'], [400, 'merchant'], [900, 'scaleup'], [1800, 'unicorn']];
  var TYPES = { order: { e: '📦', pts: 10 }, star: { e: '⭐', pts: 30 }, bot: { e: '🤖', pts: 0 }, refund: { e: '💸', bad: 1 }, bug: { e: '🐞', bad: 1 } };

  var s, raf, last, rnd, daily = false, running = false, paused = false, px = W / 2, target = W / 2, keys = {};

  function txt(k) { var n = root.querySelector('[data-s="' + k + '"]'); return n ? n.textContent.trim() : k; }
  function hud() {
    $('[data-o="score"]').textContent = s ? Math.floor(s.score) : 0;
    $('[data-o="lives"]').textContent = s ? '❤'.repeat(Math.max(0, s.lives)) || '–' : '❤❤❤';
    $('[data-o="combo"]').textContent = s ? 'x' + Math.min(5, 1 + Math.floor(s.combo / 4)) : 'x1';
    $('[data-o="best"]').textContent = save.best;
    $('[data-o="streak"]').textContent = save.streak;
  }
  function show(id) { ['start', 'over'].forEach(function (k) { $('[data-pane="' + k + '"]').hidden = k !== id; }); }

  function start(isDaily) {
    daily = !!isDaily; rnd = daily ? seeded(today()) : Math.random;
    s = { score: 0, lives: 3, combo: 0, t: 0, spawn: 0, items: [], fx: [], magnet: 0, shake: 0, caught: 0 };
    px = target = W / 2; running = true; paused = false; last = 0;
    show(null); root.classList.add('is-playing'); hud(); cv.focus({ preventScroll: true });
    cancelAnimationFrame(raf); raf = requestAnimationFrame(loop);
  }
  function pick() {
    var r = rnd(), diff = Math.min(1, s.t / 60);
    if (r < 0.52 - diff * 0.1) return 'order'; if (r < 0.62) return 'star'; if (r < 0.67) return 'bot';
    return r < 0.84 ? 'refund' : 'bug';
  }
  function end() {
    running = false; root.classList.remove('is-playing');
    var sc = Math.floor(s.score), isBest = sc > save.best, td = today(), y = new Date(); y.setDate(y.getDate() - 1);
    var yd = y.getFullYear() + '-' + ('0' + (y.getMonth() + 1)).slice(-2) + '-' + ('0' + y.getDate()).slice(-2);
    if (isBest) save.best = sc;
    if (daily && save.last !== td) { save.streak = save.last === yd ? save.streak + 1 : 1; save.last = td; }
    save.plays++;
    var got = []; BADGES.forEach(function (b) { if (sc >= b[0] && save.badges.indexOf(b[1]) < 0) { save.badges.push(b[1]); got.push(b[1]); } });
    persist(); hud(); badges();
    $('[data-o="final"]').textContent = sc;
    $('[data-o="newbest"]').hidden = !isBest || sc === 0;
    $('[data-o="newbadge"]').textContent = got.length ? txt('badge_' + got[got.length - 1]) : '';
    $('[data-o="newbadge"]').hidden = !got.length;
    $('[data-o="share"]').dataset.score = sc; $('[data-o="share"]').dataset.daily = daily ? '1' : '';
    show('over');
  }
  function badges() {
    BADGES.forEach(function (b) { var n = $('[data-badge="' + b[1] + '"]'); if (n) n.classList.toggle('on', save.badges.indexOf(b[1]) >= 0); });
  }
  function burst(x, y, c) { if (reduce) return; for (var i = 0; i < 8; i++) s.fx.push({ x: x, y: y, vx: (rnd() - .5) * 160, vy: -rnd() * 120, l: .5, c: c }); }

  function update(dt) {
    s.t += dt; var diff = Math.min(1, s.t / 60), speed = 120 + diff * 170;
    var dir = (keys.ArrowRight || keys.d ? 1 : 0) - (keys.ArrowLeft || keys.a ? 1 : 0);
    if (dir) target = Math.max(28, Math.min(W - 28, target + dir * 420 * dt));
    px += (target - px) * Math.min(1, dt * 18);
    s.spawn -= dt;
    if (s.spawn <= 0) { var tp = pick(); s.items.push({ t: tp, x: 22 + rnd() * (W - 44), y: -20, v: speed * (0.85 + rnd() * 0.4) }); s.spawn = Math.max(.34, .85 - diff * .5) * (0.8 + rnd() * .4); }
    if (s.magnet > 0) s.magnet -= dt;
    for (var i = s.items.length - 1; i >= 0; i--) {
      var it = s.items[i], d = TYPES[it.t];
      if (s.magnet > 0 && !d.bad) it.x += (px - it.x) * Math.min(1, dt * 4);
      it.y += it.v * dt;
      if (it.y > H - 62 && it.y < H - 24 && Math.abs(it.x - px) < 36) {
        s.items.splice(i, 1);
        if (d.bad) { s.lives--; s.combo = 0; s.shake = reduce ? 0 : .25; burst(it.x, it.y, '#ff5c7a'); if (navigator.vibrate) try { navigator.vibrate(60); } catch (e) {} }
        else if (it.t === 'bot') { s.magnet = 6; burst(it.x, it.y, '#7cf'); }
        else { s.combo++; s.caught++; s.score += d.pts * Math.min(5, 1 + Math.floor(s.combo / 4)); burst(it.x, it.y, '#37e8ff'); }
        hud();
      } else if (it.y > H + 20) { s.items.splice(i, 1); if (!d.bad && it.t !== 'bot') { s.combo = 0; hud(); } }
    }
    s.fx.forEach(function (p) { p.x += p.vx * dt; p.y += p.vy * dt; p.vy += 300 * dt; p.l -= dt; }); s.fx = s.fx.filter(function (p) { return p.l > 0; });
    if (s.shake > 0) s.shake -= dt;
    if (s.lives <= 0) end();
  }
  function draw() {
    var dpr = Math.min(2, window.devicePixelRatio || 1);
    if (cv.width !== W * dpr) { cv.width = W * dpr; cv.height = H * dpr; }
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0); ctx.clearRect(0, 0, W, H);
    var g = ctx.createLinearGradient(0, 0, 0, H); g.addColorStop(0, '#04122e'); g.addColorStop(1, '#0a2a5c'); ctx.fillStyle = g; ctx.fillRect(0, 0, W, H);
    ctx.fillStyle = 'rgba(55,232,255,.07)'; for (var k = 0; k < 12; k++) ctx.fillRect(0, ((k * 48 + (s ? s.t * 40 : 0)) % H), W, 1);
    if (!s) { ctx.fillStyle = '#fff'; ctx.font = '44px serif'; ctx.textAlign = 'center'; ctx.fillText('🛒', W / 2, H - 40); return; }
    ctx.save(); if (s.shake > 0) ctx.translate((Math.random() - .5) * 8, (Math.random() - .5) * 8);
    if (s.magnet > 0) { ctx.strokeStyle = 'rgba(124,204,255,' + (.3 + .2 * Math.sin(s.t * 12)) + ')'; ctx.lineWidth = 2; ctx.beginPath(); ctx.arc(px, H - 44, 52, 0, 7); ctx.stroke(); }
    ctx.fillStyle = '#fff'; ctx.textAlign = 'center'; ctx.textBaseline = 'middle'; ctx.font = '28px serif';
    s.items.forEach(function (it) { ctx.fillText(TYPES[it.t].e, it.x, it.y); });
    ctx.font = '44px serif'; ctx.fillStyle = '#fff'; ctx.fillText('🛒', px, H - 42);
    s.fx.forEach(function (p) { ctx.globalAlpha = Math.max(0, p.l * 2); ctx.fillStyle = p.c; ctx.fillRect(p.x, p.y, 4, 4); }); ctx.globalAlpha = 1;
    ctx.restore();
  }
  function loop(ts) {
    if (!running) { draw(); return; }
    if (!paused) { var dt = last ? Math.min(.05, (ts - last) / 1000) : 0; last = ts; update(dt); } else last = 0;
    draw(); raf = requestAnimationFrame(loop);
  }

  function pos(e) { var r = cv.getBoundingClientRect(); target = Math.max(28, Math.min(W - 28, (e.clientX - r.left) / r.width * W)); }
  cv.addEventListener('pointermove', pos); cv.addEventListener('pointerdown', function (e) { pos(e); try { cv.setPointerCapture(e.pointerId); } catch (x) {} });
  cv.style.touchAction = 'none';
  window.addEventListener('keydown', function (e) { if (e.key === ' ' && running && document.activeElement === cv) { paused = !paused; e.preventDefault(); return; } keys[e.key] = true; if (running && /^Arrow/.test(e.key) && document.activeElement === cv) e.preventDefault(); });
  window.addEventListener('keyup', function (e) { keys[e.key] = false; });
  document.addEventListener('visibilitychange', function () { if (document.hidden && running) paused = true; });
  root.querySelectorAll('[data-play]').forEach(function (b) { b.addEventListener('click', function () { start(b.dataset.play === 'daily'); }); });
  var sh = $('[data-o="share"]');
  sh.addEventListener('click', function () {
    var line = txt('share_a') + ' ' + sh.dataset.score + ' ' + txt('share_b') + (sh.dataset.daily ? ' #' + dayNo() : '') + ' 🛒 ' + location.origin + location.pathname;
    function ok() { $('.b1', sh).hidden = true; $('.b2', sh).hidden = false; setTimeout(function () { $('.b1', sh).hidden = false; $('.b2', sh).hidden = true; }, 1800); }
    function $(q, el) { return el.querySelector(q); }
    if (navigator.share) { navigator.share({ text: line }).then(ok, function () {}); return; }
    if (navigator.clipboard) navigator.clipboard.writeText(line).then(ok, function () {});
  });
  var dn = $('[data-o="dayno"]'); if (dn) dn.textContent = dayNo();
  hud(); badges(); draw(); show('start');
})();
