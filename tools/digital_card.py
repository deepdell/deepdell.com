#!/usr/bin/env python3
"""DEEPDELL private digital cards for executives, referral partners and affiliate partners.

ONE bilingual card (English + Arabic or Malay on the same card), made to share on WhatsApp or social status
and to keep on a phone. It carries a QR code that saves the person's contact details.

PRIVATE BY DESIGN. Files are written OUTSIDE the website folder (default ~/deepdell-private-cards/<name>/)
and are never part of deepdell.com. The generator refuses to write inside the repository.

  python3 tools/digital_card.py --name "Full Name" --title "Partnerships Lead" --role referral \
      --phone "+971 50 000 0000" --email name@example.com --second ar --name-ar "..." --title-ar "..."
  python3 tools/digital_card.py ... --second ms --title-ms "..."

Optional: --city, --whatsapp, --linkedin, --website, --code, --qr contact|website|referral, --out DIR
Needs: pip install segno ; node + playwright for the PNG.
Writes: card.png (1080x1920 status/story size), card.html (mobile card with Save, Call, WhatsApp, Email, Share),
        contact.vcf, qr.png, qr.svg
"""
import argparse, base64, os, re, subprocess, sys, html, json
import segno

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROLES = {'executive': {'en': 'Executive', 'ar': 'تنفيذي', 'ms': 'Eksekutif'},
         'referral': {'en': 'Referral Partner', 'ar': 'شريك إحالة', 'ms': 'Rakan Rujukan'},
         'affiliate': {'en': 'Affiliate Partner', 'ar': 'شريك تسويق بالعمولة', 'ms': 'Rakan Affiliate'}}
T = {'en': dict(save='Save contact', call='Call', mail='Email', wa='WhatsApp', web='Website', share='Share', scan='Scan to save my contact', code='Partner code',
                tag='Deep technology. Clear impact.', hint='Private card'),
     'ms': dict(save='Simpan kenalan', call='Telefon', mail='E-mel', wa='WhatsApp', web='Laman web', share='Kongsi', scan='Imbas untuk simpan kenalan saya', code='Kod rakan kongsi',
                tag='Teknologi mendalam. Impak jelas.', hint='Kad persendirian'),
     'ar': dict(save='حفظ جهة الاتصال', call='اتصال', mail='بريد', wa='واتساب', web='الموقع', share='مشاركة', scan='امسح الرمز لحفظ جهة الاتصال', code='رمز الشريك',
                tag='تقنية عميقة. أثر واضح.', hint='بطاقة خاصة')}


def esc(s): return html.escape(s or '', quote=True)
def vesc(s): return re.sub(r'([,;\\])', r'\\\1', (s or '').replace('\n', ' '))
def slug(s): return re.sub(r'[^a-z0-9]+', '-', s.lower()).strip('-') or 'card'
def digits(p): return re.sub(r'\D', '', p or '')


def vcard(a):
    first, _, last = a.name.strip().rpartition(' ')
    L = ['BEGIN:VCARD', 'VERSION:3.0', 'N:%s;%s;;;' % (vesc(last or a.name), vesc(first)), 'FN:%s' % vesc(a.name), 'ORG:DEEPDELL',
         'TITLE:%s' % vesc(a.title), 'ROLE:%s' % vesc(ROLES[a.role]['en'])]
    if a.phone: L.append('TEL;TYPE=CELL,VOICE:%s' % a.phone.replace(' ', ''))
    if a.whatsapp and digits(a.whatsapp) != digits(a.phone): L.append('TEL;TYPE=CELL:%s' % a.whatsapp.replace(' ', ''))
    if a.email: L.append('EMAIL;TYPE=INTERNET,WORK:%s' % a.email)
    L.append('URL:%s' % a.website)
    if a.linkedin: L.append('URL:%s' % a.linkedin)
    if a.city: L.append('ADR;TYPE=WORK:;;;%s;;;' % vesc(a.city))
    note = '%s at DEEPDELL' % ROLES[a.role]['en']
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
    return 'data:image/svg+xml;base64,' + base64.b64encode(open(os.path.join(ROOT, 'assets', 'deepdell-guideline-icon.svg'), 'rb').read()).decode()


# Sizes use cqw (1% of the card width) so one design fits the 1080x1920 image and any phone screen.
CSS = """
:root{--bg:#030a14;--cyan:#24e4f2;--text:#f5f9ff;--muted:#9eb0c5;--line:rgba(137,249,253,.22)}
*{box-sizing:border-box}html,body{margin:0}
body{font-family:Manrope,Inter,Arial,sans-serif;background:var(--bg);color:var(--text);-webkit-font-smoothing:antialiased}
.dcard{container-type:inline-size;width:100%;max-width:440px;aspect-ratio:9/16;margin:0 auto;position:relative;overflow:hidden;
  background:radial-gradient(circle at 90% 4%,rgba(36,228,242,.26),transparent 38%),radial-gradient(circle at 5% 96%,rgba(75,131,255,.18),transparent 40%),linear-gradient(165deg,#06214a,#011434 55%,#020b1c);
  display:flex;flex-direction:column;align-items:center;text-align:center;padding:7cqw 7cqw 5.5cqw;gap:0}
.top{display:flex;flex-direction:column;align-items:center;gap:2.6cqw}
.logo{display:flex;align-items:center;gap:2.4cqw;font-weight:800;font-size:5.4cqw;letter-spacing:-.02em}
.logo img{width:8.4cqw;height:8.4cqw}
.badge{font:600 2.7cqw/1 'DM Mono',ui-monospace,monospace;letter-spacing:.14em;color:var(--cyan);border:1px solid var(--line);padding:1.9cqw 3.4cqw;border-radius:99px;text-transform:uppercase;white-space:nowrap}
.id{margin-top:8cqw;width:100%}
.id h1{font-size:8.6cqw;line-height:1.1;margin:0;letter-spacing:-.03em;font-weight:800}
.id .n2{font-size:7.4cqw;line-height:1.25;margin:1.2cqw 0 0;font-weight:700;color:#e8f3fb}
.id .t1{font-size:4.2cqw;font-weight:700;color:var(--cyan);margin:3.2cqw 0 0}
.id .t2{font-size:3.9cqw;color:var(--muted);margin:.9cqw 0 0;font-weight:600}
.id .city{font:500 3cqw/1 'DM Mono',ui-monospace,monospace;letter-spacing:.08em;color:#7f93a8;margin:2.6cqw 0 0}
.rows{margin-top:7cqw;width:100%;display:grid;gap:3.6cqw}
.row{display:flex;flex-direction:column;align-items:center;gap:.7cqw}
.row b{font:600 2.45cqw/1 'DM Mono',ui-monospace,monospace;letter-spacing:.12em;color:var(--cyan);text-transform:uppercase}
.row span{font-size:4.8cqw;color:#e6eff7;font-weight:600;direction:ltr;overflow-wrap:anywhere}
.qrbox{margin-top:auto;display:flex;flex-direction:column;align-items:center;gap:1.8cqw;padding-top:4cqw}
.qr{width:40cqw;height:40cqw;background:#fff;border-radius:2.6cqw;padding:2cqw}
.qr img{width:100%;height:100%;display:block}
.scan{font-size:3cqw;color:var(--muted);line-height:1.35}
.code{font:600 2.7cqw/1 'DM Mono',ui-monospace,monospace;letter-spacing:.1em;color:var(--cyan);text-transform:uppercase;border:1px solid var(--line);border-radius:99px;padding:1.5cqw 3cqw}
.foot{margin-top:3.4cqw;font:500 2.3cqw/1.5 'DM Mono',ui-monospace,monospace;letter-spacing:.12em;color:#6f869d;text-transform:uppercase}
.m{max-width:440px;margin:0 auto;padding:14px 14px 44px}
.actions{display:grid;grid-template-columns:1fr 1fr;gap:10px;margin:16px 0 8px}
.actions a,.actions button{display:flex;flex-direction:column;justify-content:center;align-items:center;min-height:52px;border-radius:12px;border:1px solid var(--line);color:#fff;text-decoration:none;
  font:700 14px/1.25 Manrope,Inter,Arial,sans-serif;background:rgba(7,21,38,.9);cursor:pointer;padding:8px}
.actions small{font-weight:600;font-size:12px;color:var(--muted)}
.actions .primary{grid-column:1/-1;background:linear-gradient(100deg,#2ae1ef,#4b83ff);color:#03101d;border:0}
.actions .primary small{color:#03304a}
.note{text-align:center;font-size:12px;color:var(--muted);margin:10px 0 0}
"""


def card_html(a, qr_uri):
    s = a.second; E, S = T['en'], T[s]
    rtl2 = s == 'ar'
    name2 = a.name_ar if rtl2 else ''
    title2 = a.title_ar if rtl2 else a.title_ms
    lab = lambda k: '%s · %s' % (E[k], S[k])
    rows = []
    if a.phone: rows.append((lab('call'), a.phone))
    if a.email: rows.append((lab('mail'), a.email))
    if a.whatsapp and digits(a.whatsapp) != digits(a.phone): rows.append((lab('wa'), a.whatsapp))
    rows.append((lab('web'), re.sub(r'^https?://', '', a.website).rstrip('/')))
    rowh = ''.join('<div class="row"><b>%s</b><span>%s</span></div>' % (esc(k), esc(v)) for k, v in rows)
    badge = '%s · %s' % (ROLES[a.role]['en'], ROLES[a.role][s])
    scan = lab('scan') if a.qr == 'contact' else re.sub(r'^https?://', '', a.website)
    code = '<div class="code">%s · %s: %s</div>' % (esc(E['code']), esc(S['code']), esc(a.code)) if a.code else ''
    n2 = '<p class="n2" dir="rtl" lang="ar">%s</p>' % esc(name2) if name2 else ''
    city = '<p class="city">%s</p>' % esc(a.city) if a.city else ''
    scanline = '<div class="scan">%s<br><span dir="%s" lang="%s">%s</span></div>' % (esc(E['scan']), 'rtl' if rtl2 else 'ltr', s, esc(S['scan'])) if a.qr == 'contact' else '<div class="scan">%s</div>' % esc(scan)
    return ('<div class="dcard"><div class="top"><div class="logo"><img src="%s" alt="">DEEPDELL</div><div class="badge">%s</div></div>'
            '<div class="id"><h1>%s</h1>%s<p class="t1">%s</p><p class="t2" dir="%s" lang="%s">%s</p>%s</div>'
            '<div class="rows">%s</div>'
            '<div class="qrbox"><div class="qr"><img src="%s" alt="QR code to save contact"></div>%s%s</div>'
            '<div class="foot">%s<br><span dir="%s" lang="%s">%s</span></div></div>'
            % (logo_uri(), esc(badge), esc(a.name), n2, esc(a.title), 'rtl' if rtl2 else 'ltr', s, esc(title2), city, rowh, qr_uri, scanline, code,
               esc(E['tag']), 'rtl' if rtl2 else 'ltr', s, esc(S['tag'])))


def build_page(a, card, vcf_uri, mobile):
    E, S = T['en'], T[a.second]
    both = lambda k: '%s<small>%s</small>' % (esc(E[k]), esc(S[k]))
    tel = 'tel:' + a.phone.replace(' ', '')
    wa = 'https://wa.me/' + digits(a.whatsapp or a.phone)
    actions = ('<div class="actions"><a class="primary" href="%s" download="%s.vcf">%s</a><a href="%s">%s</a><a href="%s" rel="noopener">%s</a>'
               '<a href="mailto:%s">%s</a><a href="%s" rel="noopener">%s</a><button type="button" id="share" hidden style="grid-column:1/-1">%s</button></div>'
               % (vcf_uri, slug(a.name), both('save'), tel, both('call'), wa, both('wa'), esc(a.email), both('mail'), esc(a.website), both('web'), both('share')))
    js = ("<script>var b=document.getElementById('share');if(navigator.share){b.hidden=false;b.onclick=function(){navigator.share({title:%s,text:%s,url:%s}).catch(function(){})}}</script>"
          % (json.dumps(a.name + ' · DEEPDELL'), json.dumps(a.name + ', ' + a.title + ' · DEEPDELL'), json.dumps(a.website)))
    body = '<div class="m">%s%s<p class="note">%s · %s</p></div>%s' % (card, actions, esc(E['hint']), esc(S['hint']), js) if mobile else card
    return ('<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
            '<meta name="robots" content="noindex,nofollow,noarchive"><meta name="theme-color" content="#011434"><title>%s | DEEPDELL</title><style>%s</style></head><body>%s</body></html>'
            % (esc(a.name), CSS, body))


def render(outdir):
    js = r"""
const { chromium } = require('playwright'); const path = require('path');
(async () => { const [dir] = process.argv.slice(2); const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: 360, height: 640 }, deviceScaleFactor: 3 });
  await p.goto('file://' + path.join(dir, 'sheet.html')); await p.waitForTimeout(300);
  await (await p.$('.dcard')).screenshot({ path: path.join(dir, 'card.png') });
  await b.close(); })();
"""
    jp = os.path.join(outdir, '.render.js'); open(jp, 'w').write(js)
    env = dict(os.environ); env.setdefault('NODE_PATH', subprocess.run(['npm', 'root', '-g'], capture_output=True, text=True).stdout.strip())
    r = subprocess.run(['node', jp, outdir], capture_output=True, text=True, env=env); os.remove(jp)
    if r.returncode: print('render warning:', r.stderr[:300])
    try: os.remove(os.path.join(outdir, 'sheet.html'))
    except OSError: pass


def main():
    ap = argparse.ArgumentParser(description='Create a private bilingual DEEPDELL digital card')
    ap.add_argument('--name', required=True); ap.add_argument('--title', required=True)
    ap.add_argument('--role', choices=list(ROLES), required=True)
    ap.add_argument('--phone', required=True); ap.add_argument('--email', required=True)
    ap.add_argument('--second', choices=['ar', 'ms'], required=True, help='second language next to English: Arabic or Malay')
    ap.add_argument('--name-ar', default=''); ap.add_argument('--title-ar', default=''); ap.add_argument('--title-ms', default='')
    ap.add_argument('--whatsapp', default=''); ap.add_argument('--city', default=''); ap.add_argument('--linkedin', default='')
    ap.add_argument('--website', default='https://deepdell.com'); ap.add_argument('--code', default='')
    ap.add_argument('--qr', choices=['contact', 'website', 'referral'], default='contact')
    ap.add_argument('--out', default='')
    a = ap.parse_args()
    if a.second == 'ar' and not (a.name_ar and a.title_ar): sys.exit('Arabic needs --name-ar and --title-ar')
    if a.second == 'ms' and not a.title_ms: sys.exit('Malay needs --title-ms')
    if a.qr == 'referral' and not a.code: sys.exit('--qr referral needs --code')
    if not re.match(r'^\+?[0-9 ()-]{7,20}$', a.phone): sys.exit('phone must include the country code, for example +971 50 000 0000')
    if not re.match(r'^[^@\s]+@[^@\s]+\.[^@\s]+$', a.email): sys.exit('email looks invalid')
    base = a.out or os.path.join(os.path.expanduser('~'), 'deepdell-private-cards', slug(a.name))
    if os.path.realpath(base).startswith(os.path.realpath(ROOT) + os.sep): sys.exit('refusing to write cards inside the website repository (they would be published)')
    os.makedirs(base, exist_ok=True)
    for old in ('card-front.png', 'card-back.png', 'card.pdf'):
        try: os.remove(os.path.join(base, old))
        except OSError: pass
    q = segno.make(qr_payload(a), error='m')
    q.save(os.path.join(base, 'qr.svg'), scale=8, border=2, dark='#011434'); q.save(os.path.join(base, 'qr.png'), scale=12, border=2, dark='#011434')
    qr_uri = 'data:image/png;base64,' + base64.b64encode(open(os.path.join(base, 'qr.png'), 'rb').read()).decode()
    vc = vcard(a); open(os.path.join(base, 'contact.vcf'), 'w', encoding='utf-8', newline='').write(vc)
    vuri = 'data:text/vcard;charset=utf-8;base64,' + base64.b64encode(vc.encode()).decode()
    card = card_html(a, qr_uri)
    open(os.path.join(base, 'card.html'), 'w', encoding='utf-8').write(build_page(a, card, vuri, True))
    open(os.path.join(base, 'sheet.html'), 'w', encoding='utf-8').write(build_page(a, card, vuri, False))
    render(base)
    print(json.dumps({'folder': base, 'files': sorted(os.listdir(base)), 'qr': a.qr}))


if __name__ == '__main__':
    main()
