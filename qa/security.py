#!/usr/bin/env python3
"""DEEPDELL pre-deploy security check (static, no network needed).

  python3 qa/security.py            # check the repository as it will be published
  python3 qa/security.py --live     # also check the live site's HTTPS, headers and exposed files

Exit code 1 when any FAIL is found. WARN items are advice. No scan can promise a site is "unhackable":
this blocks the common mistakes (secrets, unsafe scripts, exposed files, weak form or Worker rules).
"""
import os, re, sys, glob, json, subprocess
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
fails, warns, passes = [], [], []
def fail(m): fails.append(m)
def warn(m): warns.append(m)
def ok(m): passes.append(m)

SKIP_DIRS = ('.git', 'node_modules', 'qa/out')
def files(*pats):
    out = []
    for p in pats:
        out += [f for f in glob.glob(p, recursive=True) if os.path.isfile(f) and not f.startswith(SKIP_DIRS)]
    return sorted(set(out))
def read(f):
    try: return open(f, encoding='utf-8', errors='ignore').read()
    except Exception: return ''

HTML = files('*.html', '*/*.html')
CODE = files('*.js', 'worker/*.js', 'blog/*.js', 'assets/*.js')
ALL_TEXT = HTML + CODE + files('*.toml', '*.json', '*.md', '*.txt', '*.xml', '.github/workflows/*.yml')

# 1. secrets
SECRETS = [(r'AKIA[0-9A-Z]{16}', 'AWS access key'), (r'-----BEGIN (RSA |EC |OPENSSH |)PRIVATE KEY-----', 'private key'),
           (r'sk-[A-Za-z0-9]{32,}', 'API secret key'), (r'ghp_[A-Za-z0-9]{30,}', 'GitHub token'), (r'xox[baprs]-[A-Za-z0-9-]{10,}', 'Slack token'),
           (r'(?i)(api[_-]?key|secret|password|token)\s*[:=]\s*["\'][A-Za-z0-9_\-]{20,}["\']', 'hard-coded credential')]
hits = []
for f in ALL_TEXT:
    t = read(f)
    for rx, name in SECRETS:
        for m in re.finditer(rx, t):
            hits.append('%s: %s' % (f, name))
if hits: [fail('secret in source: ' + h) for h in sorted(set(hits))]
else: ok('no secrets found in %d text files' % len(ALL_TEXT))

# 2. sensitive or junk files that would be published
bad = [f for f in glob.glob('**/*', recursive=True) if os.path.isfile(f) and not f.startswith(SKIP_DIRS) and
       re.search(r'(^|/)(\.env.*|.*\.(bak|orig|swp|sql|pem|key|map|log)|\.DS_Store|id_rsa.*|credentials.*\.json)$', f)]
if bad: [fail('sensitive/junk file would be published: ' + f) for f in bad]
else: ok('no sensitive or backup files in the published tree')

# 2b. private digital cards must never be published
cards = [f for f in glob.glob('**/*', recursive=True) if os.path.isfile(f) and not f.startswith(SKIP_DIRS) and
         (re.search(r'(^|/)(card-front|card-back)\.png$|deepdell-private-cards|(^|/)cards?/', f) or (f.endswith('.vcf') and os.path.basename(f) not in ('contact.vcf',)))]
if cards: [fail('private digital card file inside the website tree: ' + f) for f in cards]
else: ok('no private digital cards in the published tree')

# 3. external hosts: scripts and styles must come from an allow-list
ALLOW_SCRIPT = {'www.googletagmanager.com', 'analytics.ahrefs.com', 'cdnjs.cloudflare.com'}
ALLOW_STYLE = {'fonts.googleapis.com', 'fonts.gstatic.com'}
ext = set()
for f in HTML:
    t = read(f)
    for m in re.finditer(r'<script[^>]+src="(https?://([^/"]+)[^"]*)"', t):
        if m.group(2) not in ALLOW_SCRIPT: ext.add('script %s in %s' % (m.group(1), f))
    for m in re.finditer(r'<link[^>]+rel="stylesheet"[^>]+href="(https?://([^/"]+)[^"]*)"', t):
        if m.group(2) not in ALLOW_STYLE: ext.add('stylesheet %s in %s' % (m.group(1), f))
    for m in re.finditer(r'<(iframe|object|embed)\b', t): ext.add('<%s> in %s' % (m.group(1), f))
if ext: [fail('unapproved third-party resource: ' + x) for x in sorted(ext)]
else: ok('only allow-listed third-party scripts and styles are loaded')
missing_sri = [f for f in HTML for m in re.finditer(r'<script[^>]+src="https://cdnjs[^>]+>', read(f)) if 'integrity=' not in m.group(0)]
if missing_sri: warn('cdnjs script without integrity hash in: ' + ', '.join(sorted(set(missing_sri))))

# 4. links and markup
nb = set()
for f in HTML:
    for m in re.finditer(r'<a\b[^>]*target="_blank"[^>]*>', read(f)):
        if not re.search(r'rel="[^"]*noopener', m.group(0)): nb.add(f)
if nb: [fail('target=_blank without rel=noopener in ' + f) for f in sorted(nb)]
else: ok('all target=_blank links use rel=noopener')
mixed = sorted({f for f in HTML + CODE for m in re.finditer(r'(?:src|href|action)="http://(?!localhost)', read(f))})
if mixed: [fail('insecure http:// resource in ' + f) for f in mixed]
else: ok('no mixed-content (http://) resources')
inline = sorted({f for f in HTML if re.search(r'\son(click|load|error|mouseover|submit|focus)=', read(f))})
if inline: [warn('inline event handlers (blocks a strict Content-Security-Policy) in ' + f) for f in inline]
else: ok('no inline event handlers')
js_url = sorted({f for f in HTML if re.search(r'href="javascript:', read(f), flags=re.I)})
if js_url: [fail('javascript: URL in ' + f) for f in js_url]

# 5. dangerous JavaScript sinks
SINK = re.compile(r'(\beval\s*\(|new Function\s*\(|document\.write\s*\(|\.insertAdjacentHTML\s*\(|\.outerHTML\s*=|setTimeout\s*\(\s*["\'`])')
for f in CODE + HTML:
    t = read(f)
    for m in SINK.finditer(t): fail('unsafe JS sink in %s: %s' % (f, m.group(0).strip()))
SAFE_INNER = re.compile(r"innerHTML\s*=\s*(''|\"\"|svg\(\)|'<i></i><i></i><i></i>')")
for f in CODE:
    t = read(f)
    for m in re.finditer(r'\.innerHTML\s*=\s*[^;\n]{0,200}', t):
        if SAFE_INNER.search(m.group(0)): continue
        full = re.match(r'\.innerHTML\s*=\s*(`[^`]*`|(?:\s*\+?\s*(?:\'[^\'\n]*\'|"[^"\n]*"))+)\s*;', t[m.start():m.start() + 6000])
        if full and '${' not in full.group(1): continue  # a fixed string with nothing inserted
        if re.search(r'\$\{[^}]*(value|location|search|hash|param|dataset|textContent)', m.group(0)): fail('innerHTML built from user-controlled data in %s: %s' % (f, m.group(0)[:80]))
        else: warn('innerHTML assignment to review in %s: %s' % (f, m.group(0)[:70]))
if not any(m.startswith('unsafe') for m in fails): ok('no eval, document.write or insertAdjacentHTML')

# 6. forms
for f in HTML:
    for form in re.finditer(r'<form\b[^>]*>(.*?)</form>', read(f), flags=re.S):
        body = form.group(0)
        if 'type="password"' in body: fail('password field in ' + f)
        action = re.search(r'action="([^"]+)"', body)
        if action and not action.group(1).startswith('https://'): fail('form posts to a non-HTTPS action in %s' % f)
        if re.search(r'<input[^>]+(email|name)', body) and not re.search(r'honeypot|hp_|botcheck|name="website"|aria-hidden="true"[^>]*tabindex="-1"|tabindex="-1"[^>]*aria-hidden', body + read('script.js')) and 'tl-field' not in body:
            warn('lead form without visible honeypot markup in ' + f)
ok('forms checked (no password fields, HTTPS only)')

# 7. Worker
w = read('worker/contact.js')
if w:
    if re.search(r'Access-Control-Allow-Origin["\']?\s*[:,]\s*["\']\*', w): fail('Worker allows any origin (CORS *)')
    else: ok('Worker does not use wildcard CORS')
    if not re.search(r'(?i)allowed.?origins?|ALLOWED', w): fail('Worker has no origin allow-list')
    else: ok('Worker checks an origin allow-list')
    if not re.search(r'(?i)rate.?limit', w + read('wrangler.toml')): fail('Worker has no rate limiting')
    else: ok('Worker uses rate limiting')
    if re.search(r'\beval\(|new Function', w): fail('Worker uses eval')
    if re.search(r'(?i)console\.(log|info)\([^)]*(email|phone|body)', w): warn('Worker may log personal data')
else: warn('worker/contact.js not found')
wt = read('wrangler.toml')
if re.search(r'(?i)(secret|token|key)\s*=\s*"[^"]{12,}"', wt): fail('wrangler.toml contains a credential')

# 8. security metadata and CI hygiene
for f in ('security.txt', 'robots.txt'):
    (ok if os.path.exists(f) else warn)('%s %s' % (f, 'present' if os.path.exists(f) else 'missing'))
if os.path.exists('CNAME'): ok('CNAME present')
for f in HTML:
    t = read(f)
    if '<meta name="referrer"' not in t and f != '404.html': warn('no referrer policy meta in ' + f)
for wf in files('.github/workflows/*.yml'):
    t = read(wf)
    if re.search(r'pull_request_target', t): fail('%s uses pull_request_target (privilege escalation risk)' % wf)
    if re.search(r'(?m)^permissions:', t) is None: warn('%s has no explicit permissions block' % wf)
    for m in re.finditer(r'uses:\s*([^@\s]+)@([^\s#]+)', t):
        if not re.fullmatch(r'[0-9a-f]{40}', m.group(2)) and not m.group(1).startswith('actions/'): warn('%s: action %s is not pinned to a commit' % (wf, m.group(1)))

# 9. dependencies
for pkg in files('package.json', 'qa/package.json'):
    if os.path.exists(os.path.join(os.path.dirname(pkg) or '.', 'package-lock.json')):
        r = subprocess.run(['npm', 'audit', '--audit-level=high', '--omit=dev'], cwd=os.path.dirname(pkg) or '.', capture_output=True, text=True)
        (ok if r.returncode == 0 else fail)('npm audit %s' % pkg)

# 10. live site
if '--live' in sys.argv:
    import urllib.request, urllib.error, ssl
    def get(u, method='GET'):
        req = urllib.request.Request(u, method=method, headers={'User-Agent': 'deepdell-security-check'})
        try: return urllib.request.urlopen(req, timeout=20)
        except urllib.error.HTTPError as e: return e
        except Exception as e: return None
    r = get('https://deepdell.com/')
    if not r: fail('live: https://deepdell.com/ not reachable')
    else:
        h = {k.lower(): v for k, v in r.headers.items()}
        ok('live: HTTPS works (status %s)' % r.status)
        for hd, why in (('strict-transport-security', 'HSTS'), ('x-content-type-options', 'nosniff'), ('content-security-policy', 'CSP'), ('referrer-policy', 'referrer policy'),
                        ('permissions-policy', 'permissions policy'), ('x-frame-options', 'clickjacking protection')):
            (ok if hd in h else warn)('live header %s %s' % (why, 'present' if hd in h else 'missing (needs the Cloudflare proxy and a response header rule)'))
    for path in ('.env', '.git/config', 'wrangler.toml', 'worker/contact.js.map', 'package.json'):
        rr = get('https://deepdell.com/' + path)
        if rr and rr.status == 200 and path in ('.env', '.git/config'): fail('live: /%s is exposed' % path)
    rr = get('http://deepdell.com/')
    ok('live: http redirects to https') if rr and rr.geturl().startswith('https://') else warn('live: http does not redirect to https')

print('\nSECURITY CHECK')
for m in passes: print('  PASS ', m)
for m in warns: print('  WARN ', m)
for m in fails: print('  FAIL ', m)
print('\n%d passed, %d warnings, %d failures' % (len(passes), len(warns), len(fails)))
sys.exit(1 if fails else 0)
