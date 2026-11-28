#!/usr/bin/env python3
"""DEEPDELL private digital cards for executives, referral partners and affiliate partners.

PRIVATE BY DESIGN. Cards are written OUTSIDE the website folder (default ~/deepdell-private-cards/<name>/)
and are never part of deepdell.com. Do not copy them into this repository. The QR code carries the person's
contact details (vCard), so it works offline with no page to host.

  python3 tools/digital_card.py --name "Full Name" --title "Partnerships Lead" --role referral \
      --phone "+971 50 000 0000" --email name@example.com --city "Dubai, UAE" \
      [--whatsapp ...] [--linkedin URL] [--website https://deepdell.com] [--code PARTNER01] \
      [--qr contact|website|referral] [--lang en|ar] [--name-ar "..."] [--title-ar "..."] [--out DIR]

Roles: executive, referral, affiliate.  Needs: pip install segno ; node + playwright for PNG/PDF.
Writes: card.html (mobile card), card-front.png, card-back.png, card.pdf (print, 3.5 x 2 in), contact.vcf, qr.svg, qr.png
"""
import argparse, base64, os, re, subprocess, sys, html, json
import segno

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROLES = {'executive': ('Executive', 'تنفيذي'), 'referral': ('Referral Partner', 'شريك إحالة'), 'affiliate': ('Affiliate Partner', 'شريك تسويق بالعمولة')}
LABELS = {'en': dict(save='Save contact', call='Call', loc='City', mail='Email', wa='WhatsApp', web='Website', scan='Scan to save my contact', code='Partner code', private='Private card', tag='Deep technology. Clear impact.'),
          'ar': dict(save='حفظ جهة الاتصال', call='اتصال', loc='المدينة', mail='بريد', wa='واتساب', web='الموقع', scan='امسح الرمز لحفظ جهة الاتصال', code='رمز الشريك', private='بطاقة خاصة', tag='تقنية عميقة. أثر واضح.')}


def esc(s): return html.escape(s or '', quote=True)
def vesc(s): return re.sub(r'([,;\\])', r'\\\1', (s or '').replace('\n', ' '))
def slug(s): return re.sub(r'[^a-z0-9]+', '-', s.lower()).strip('-') or 'card'


def digits(p): return re.sub(r'\D', '', p or '')


def vcard(a):
    first, _, last = a.name.strip().rpartition(' ')
    L = ['BEGIN:VCARD', 'VERSION:3.0', 'N:%s;%s;;;' % (vesc(last or a.name), vesc(first)), 'FN:%s' % vesc(a.name), 'ORG:DEEPDELL',
         'TITLE:%s' % vesc(a.title), 'ROLE:%s' % vesc(ROLES[a.role][0])]
    if a.phone: L.append('TEL;TYPE=CELL,VOICE:%s' % a.phone.replace(' ', ''))
    if a.whatsapp and digits(a.whatsapp) != digits(a.phone): L.append('TEL;TYPE=CELL:%s' % a.whatsapp.replace(' ', ''))
    if a.email: L.append('EMAIL;TYPE=INTERNET,WORK:%s' % a.email)
    L.append('URL:%s' % a.website)
    if a.linkedin: L.append('URL:%s' % a.linkedin)
    if a.city: L.append('ADR;TYPE=WORK:;;;%s;;;' % vesc(a.city))
    note = '%s at DEEPDELL' % ROLES[a.role][0]
    if a.code: note += ' | Partner code: %s' % a.code
    L += ['NOTE:%s' % vesc(note), 'END:VCARD']
    return '\r\n'.join(L) + '\r\n'


def qr_payload(a):
    if a.qr == 'website': return a.website
    if a.qr == 'referral':
        sep = '&' if '?' in a.website else '?'
        return '%s%sref=%s&utm_source=partner&utm_medium=referral&utm_campaign=%s' % (a.website, sep, a.code, slug(a.name))
    return vcard(a)


def logo_uri():
    p = os.path.join(ROOT, 'assets', 'deepdell-guideline-icon.svg')
    return 'data:image/svg+xml;base64,' + base64.b64encode(open(p, 'rb').read()).decode()


CSS = """
:root{--bg:#030a14;--navy:#011434;--panel:#071526;--cyan:#24e4f2;--text:#f5f9ff;--muted:#9eb0c5;--line:rgba(137,249,253,.22)}
*{box-sizing:border-box}html,body{margin:0}
body{font-family:Manrope,Inter,Arial,sans-serif;background:var(--bg);color:var(--text);-webkit-font-smoothing:antialiased}
.sheet{display:flex;flex-direction:column;align-items:center;gap:22px;padding:24px}
.card{width:525px;height:300px;border-radius:14px;position:relative;overflow:hidden;border:1px solid var(--line);
  background:radial-gradient(circle at 85% 8%,rgba(36,228,242,.22),transparent 42%),linear-gradient(150deg,#06214a,#011434 60%,#020b1c)}
.card .logo{position:absolute;left:26px;top:24px;display:flex;align-items:center;gap:9px;font-weight:800;font-size:17px;letter-spacing:-.02em}
.card .logo img{width:30px;height:30px}
.card .badge{position:absolute;right:24px;top:26px;font:600 9px/1 'DM Mono',ui-monospace,monospace;letter-spacing:.14em;color:var(--cyan);border:1px solid var(--line);padding:6px 9px;border-radius:99px;text-transform:uppercase}
.front .who{position:absolute;left:26px;right:26px;top:92px}
.front h1{font-size:27px;line-height:1.08;margin:0 0 6px;letter-spacing:-.03em}
.front .title{font-size:13px;color:var(--cyan);font-weight:700;margin:0 0 3px}
.front .alt{font-size:12px;color:var(--muted);margin:0}
.front .contacts{position:absolute;left:26px;right:26px;bottom:22px;display:grid;gap:5px;font-size:11.5px;color:#d5e3ef}
.front .contacts span{display:flex;gap:8px;align-items:baseline}
.front .contacts b{font:600 8.5px/1 'DM Mono',ui-monospace,monospace;letter-spacing:.12em;color:var(--cyan);width:48px;flex:none;white-space:nowrap;text-transform:uppercase}
.back{display:flex;align-items:center;justify-content:center;flex-direction:column;gap:9px}
.back .qr{width:158px;height:158px;margin-top:34px;background:#fff;border-radius:10px;padding:9px}
.back .qr img{width:100%;height:100%;display:block}
.back .scan{font-size:11px;color:var(--muted);letter-spacing:.02em}
.back .code{font:600 10px/1 'DM Mono',ui-monospace,monospace;color:var(--cyan);letter-spacing:.12em;text-transform:uppercase}
.back .logo{top:20px}.back .badge{top:22px}
.foot{position:absolute;left:0;right:0;bottom:12px;text-align:center;font:500 8.5px/1 'DM Mono',ui-monospace,monospace;letter-spacing:.14em;color:#6f869d;text-transform:uppercase}
[dir=rtl] .card .logo{left:auto;right:26px}[dir=rtl] .card .badge{right:auto;left:24px}
[dir=rtl] .front .who,[dir=rtl] .front .contacts{text-align:right}
[dir=rtl] .front .contacts span{flex-direction:row-reverse;justify-content:flex-end}
.m{max-width:420px;margin:0 auto;padding:18px 16px 40px}
.m .card{width:100%;height:auto;aspect-ratio:525/300}
.actions{display:grid;grid-template-columns:1fr 1fr;gap:10px;margin:18px 0}
.actions a{display:flex;justify-content:center;align-items:center;min-height:48px;border-radius:10px;border:1px solid var(--line);color:#fff;text-decoration:none;font-weight:700;font-size:14px;background:rgba(7,21,38,.9)}
.actions a.primary{grid-column:1/-1;background:linear-gradient(100deg,#2ae1ef,#4b83ff);color:#03101d;border:0}
.note{text-align:center;font-size:12px;color:var(--muted)}
@page{size:3.5in 2in;margin:0}
@media print{body{background:none}.sheet{padding:0;gap:0}.card{width:3.5in;height:2in;border-radius:0;border:0;page-break-after:always;zoom:.6667}.m,.actions,.note{display:none}}
"""


def card_faces(a, qr_data):
    L = LABELS[a.lang]; rtl = a.lang == 'ar'
    role = ROLES[a.role][1 if rtl else 0]
    name = a.name_ar if (rtl and a.name_ar) else a.name
    title = a.title_ar if (rtl and a.title_ar) else a.title
    alt = (a.name if rtl and a.name_ar else a.name_ar) or ''
    rows = []
    if a.phone: rows.append((L['call'], a.phone))
    if a.email: rows.append((L['mail'], a.email))
    if a.whatsapp and digits(a.whatsapp) != digits(a.phone): rows.append((L['wa'], a.whatsapp))
    rows.append((L['web'], re.sub(r'^https?://', '', a.website).rstrip('/')))
    if a.city: rows.append((L['loc'], a.city))
    contacts = ''.join('<span><b>%s</b><span dir="ltr">%s</span></span>' % (esc(k), esc(v)) for k, v in rows[:5])
    front = ('<div class="card front"><div class="logo"><img src="%s" alt="">DEEPDELL</div><div class="badge">%s</div>'
             '<div class="who"><h1>%s</h1><p class="title">%s</p>%s</div><div class="contacts">%s</div></div>'
             % (logo_uri(), esc(role), esc(name), esc(title), '<p class="alt">%s</p>' % esc(alt) if alt else '', contacts))
    code = '<div class="code">%s: %s</div>' % (esc(L['code']), esc(a.code)) if a.code else ''
    back = ('<div class="card back"><div class="logo"><img src="%s" alt="">DEEPDELL</div><div class="badge">%s</div>'
            '<div class="qr"><img src="%s" alt="QR code"></div><div class="scan">%s</div>%s<div class="foot">%s</div></div>'
            % (logo_uri(), esc(role), qr_data, esc(L['scan'] if a.qr == 'contact' else a.website), code, esc(L['tag'])))
    return front, back


def page(a, front, back, vcf_uri, mobile):
    L = LABELS[a.lang]; rtl = a.lang == 'ar'
    tel = 'tel:' + a.phone.replace(' ', '') if a.phone else '#'
    wa = 'https://wa.me/' + digits(a.whatsapp or a.phone) if (a.whatsapp or a.phone) else '#'
    actions = ('<div class="actions"><a class="primary" href="%s" download="%s.vcf">%s</a><a href="%s">%s</a><a href="mailto:%s">%s</a><a href="%s" rel="noopener">%s</a><a href="%s" rel="noopener">%s</a></div>'
               % (vcf_uri, slug(a.name), esc(L['save']), tel, esc(L['call']), esc(a.email), esc(L['mail']), wa, esc(L['wa']), esc(a.website), esc(L['web'])))
    body = '<div class="m">%s%s%s<p class="note">%s</p></div>' % (front, actions, back, esc(L['private'])) if mobile else '<div class="sheet">%s%s</div>' % (front, back)
    return ('<!doctype html><html lang="%s" dir="%s"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
            '<meta name="robots" content="noindex,nofollow,noarchive"><title>%s | DEEPDELL</title><style>%s</style></head><body>%s</body></html>'
            % (a.lang, 'rtl' if rtl else 'ltr', esc(a.name), CSS, body))


def render(outdir, files):
    js = r"""
const { chromium } = require('playwright'); const path = require('path');
(async () => { const [dir] = process.argv.slice(2); const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: 600, height: 380 }, deviceScaleFactor: 3 });
  await p.goto('file://' + path.join(dir, 'sheet.html')); await p.waitForTimeout(300);
  const cards = await p.$$('.card');
  await cards[0].screenshot({ path: path.join(dir, 'card-front.png') }); await cards[1].screenshot({ path: path.join(dir, 'card-back.png') });
  await p.pdf({ path: path.join(dir, 'card.pdf'), width: '3.5in', height: '2in', printBackground: true, preferCSSPageSize: true });
  await b.close(); })();
"""
    jp = os.path.join(outdir, '.render.js'); open(jp, 'w').write(js)
    env = dict(os.environ); env.setdefault('NODE_PATH', subprocess.run(['npm', 'root', '-g'], capture_output=True, text=True).stdout.strip())
    r = subprocess.run(['node', jp, outdir], capture_output=True, text=True, env=env); os.remove(jp)
    if r.returncode: print('render warning:', r.stderr[:300])
    try: os.remove(os.path.join(outdir, 'sheet.html'))
    except OSError: pass


def main():
    ap = argparse.ArgumentParser(description='Create a private DEEPDELL digital card')
    ap.add_argument('--name', required=True); ap.add_argument('--title', required=True)
    ap.add_argument('--role', choices=list(ROLES), required=True)
    ap.add_argument('--phone', required=True); ap.add_argument('--email', required=True)
    ap.add_argument('--whatsapp', default=''); ap.add_argument('--city', default=''); ap.add_argument('--linkedin', default='')
    ap.add_argument('--website', default='https://deepdell.com'); ap.add_argument('--code', default='')
    ap.add_argument('--qr', choices=['contact', 'website', 'referral'], default='contact')
    ap.add_argument('--lang', choices=['en', 'ar'], default='en'); ap.add_argument('--name-ar', default=''); ap.add_argument('--title-ar', default='')
    ap.add_argument('--out', default='')
    a = ap.parse_args()
    if a.qr == 'referral' and not a.code: sys.exit('--qr referral needs --code')
    if not re.match(r'^\+?[0-9 ()-]{7,20}$', a.phone): sys.exit('phone must include the country code, for example +971 50 000 0000')
    if not re.match(r'^[^@\s]+@[^@\s]+\.[^@\s]+$', a.email): sys.exit('email looks invalid')
    base = a.out or os.path.join(os.path.expanduser('~'), 'deepdell-private-cards', slug(a.name))
    if os.path.realpath(base).startswith(os.path.realpath(ROOT) + os.sep): sys.exit('refusing to write cards inside the website repository (they would be published)')
    os.makedirs(base, exist_ok=True)
    payload = qr_payload(a)
    q = segno.make(payload, error='m')
    q.save(os.path.join(base, 'qr.svg'), scale=8, border=2, dark='#011434'); q.save(os.path.join(base, 'qr.png'), scale=12, border=2, dark='#011434')
    qr_uri = 'data:image/png;base64,' + base64.b64encode(open(os.path.join(base, 'qr.png'), 'rb').read()).decode()
    vc = vcard(a); open(os.path.join(base, 'contact.vcf'), 'w', encoding='utf-8', newline='').write(vc)
    vuri = 'data:text/vcard;charset=utf-8;base64,' + base64.b64encode(vc.encode()).decode()
    front, back = card_faces(a, qr_uri)
    open(os.path.join(base, 'card.html'), 'w', encoding='utf-8').write(page(a, front, back, vuri, True))
    open(os.path.join(base, 'sheet.html'), 'w', encoding='utf-8').write(page(a, front, back, vuri, False))
    render(base, None)
    print(json.dumps({'folder': base, 'files': sorted(os.listdir(base)), 'qr': a.qr, 'qr_bytes': len(payload)}))


if __name__ == '__main__':
    main()
