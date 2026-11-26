#!/usr/bin/env python3
"""Extract translatable strings from the English pages into i18n/en.json.

static  : visible text, translatable attributes, meta tags and JSON-LD names/descriptions
dynamic : text inside JavaScript string literals (script.js and inline page scripts),
          translated at runtime by script.js for content the scripts create
"""
import re, json, glob, html, os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PAGES = sorted(p for p in glob.glob(os.path.join(ROOT, '*.html')))
ATTRS = ('title', 'alt', 'aria-label', 'placeholder')
META = ('description', 'og:title', 'og:description', 'og:image:alt', 'twitter:title', 'twitter:description')
SKIP = {'DEEPDELL', '→', '↗', '·', '/', '|', '—', '-', '+', '×', '©'}

def wanted(t):
    t = t.strip()
    if not t or t in SKIP or not re.search(r'[A-Za-z]{2}', t): return False
    if re.fullmatch(r'[\w.+-]+@[\w.-]+', t) or re.match(r'https?://', t): return False
    if re.fullmatch(r'[A-Z0-9 ./&:+-]*', t) and len(t) <= 3: return False
    return True

def split_tags(s):
    """Yield text segments of an HTML fragment, skipping <script>/<style> bodies."""
    depth = 0
    for part in re.split(r'(<[^>]*>)', s):
        if part.startswith('<'):
            m = re.match(r'<(/?)(script|style)\b', part, re.I)
            if m: depth += -1 if m.group(1) else 1
            continue
        if depth == 0: yield part

def static_strings(src):
    out = []
    body = re.sub(r'<script\b.*?</script>|<style\b.*?</style>|<!--.*?-->', '', src, flags=re.S | re.I)
    for seg in split_tags(body):
        t = html.unescape(seg).strip()
        if wanted(t): out.append(re.sub(r'\s+', ' ', t))
    for tag in re.findall(r'<[a-zA-Z][^>]*>', body):
        for a in ATTRS:
            m = re.search(r'\s%s="([^"]*)"' % a, tag)
            if m and wanted(html.unescape(m.group(1))): out.append(html.unescape(m.group(1)))
    for name in META:
        m = re.search(r'<meta (?:name|property)="%s" content="([^"]*)"' % re.escape(name), src)
        if m: out.append(html.unescape(m.group(1)))
    m = re.search(r'<title>(.*?)</title>', src, re.S)
    if m: out.append(html.unescape(m.group(1)).strip())
    for blk in re.findall(r'<script type="application/ld\+json"[^>]*>(.*?)</script>', src, re.S):
        def walk(o):
            if isinstance(o, dict):
                for k, v in o.items():
                    if k in ('name', 'description', 'serviceType', 'slogan') and isinstance(v, str) and wanted(v): out.append(v)
                    elif k in ('serviceType', 'knowsAbout') and isinstance(v, list): out.extend(x for x in v if isinstance(x, str))
                    else: walk(v)
            elif isinstance(o, list):
                for x in o: walk(x)
        walk(json.loads(blk))
    return out

LIT = re.compile(r"'((?:[^'\\\n]|\\.)*)'|\"((?:[^\"\\\n]|\\.)*)\"|`((?:[^`\\]|\\.)*)`", re.S)
def js_strings(code):
    out = []
    for m in LIT.finditer(code):
        s = next(g for g in m.groups() if g is not None)
        for piece in re.split(r'\$\{[^}]*\}', s):
            piece = piece.replace("\\'", "'").replace('\\"', '"').replace('\\n', ' ')
            for seg in (split_tags(piece) if '<' in piece else [piece]):
                t = html.unescape(seg).strip()
                if t.startswith('. '): t = t[2:]  # sentence continuation built in code
                if not wanted(t) or len(t) < 3: continue
                if re.search(r'[{};=]|^[.#\[:@]|^\w+\(|\(\)|=>|^(px|em|rem|deg|var|rgba?|translate|matrix|solid|none|auto)\b', t): continue
                if re.fullmatch(r'[a-z0-9_-]+(\s[a-z0-9_-]+)*', t) and not re.search(r'\s', t): continue  # identifiers
                if re.fullmatch(r'[\w-]+(\.[\w-]+)+|/[\w./-]*|[\w-]+:[\w-]+', t): continue
                if re.search(r'\b(querySelector|addEventListener|classList|getElementById)\b', t): continue
                out.append(re.sub(r'\s+', ' ', t))
    return out

static, dynamic = [], []
for p in PAGES:
    src = open(p, encoding='utf-8').read()
    src = re.sub(r'<!-- i18n:(head|switch) -->.*?<!-- /i18n:\1 -->', '', src, flags=re.S)
    static += static_strings(src)
    for code in re.findall(r'<script(?![^>]*ld\+json)(?![^>]*\ssrc=)[^>]*>(.*?)</script>', src, re.S):
        dynamic += js_strings(code)
dynamic += js_strings(open(os.path.join(ROOT, 'script.js'), encoding='utf-8').read())
uniq = lambda xs: list(dict.fromkeys(xs))
# Technical literals that are not visible text
JUNK = {'POST','Content-Type','application/json','Accept','en-US','scoreSub','leadStatus','leadForm','image/png','resetBtn','Escape',
        'IntersectionObserver','0px 0px -30px','section-pad agentic-home','Organization','knowsAbout','WebSite','WebPage','isPartOf',
        'application/ld+json','mailto:','DOMContentLoaded','G-K592HB9G99','O2AUj4tmiR8cKN9efAkM5Q','script[data-deepdell-ga]',
        'script[data-deepdell-ahrefs]','(prefers-reduced-motion: reduce)','(pointer: coarse)','server-status error','DEEPDELL Website Lead',
        'DEEPDELL Website','Web3Forms submission failed.','Contact delivery is not configured.','Magento','sitemap index','well-known security'}
dynamic = [d.lstrip('">').strip() for d in dynamic if d not in JUNK and not d.startswith('i18n runtime')]
EXTRA = ['JAN', 'MAR', 'MAY', 'JUL', 'SEP', 'NOV', 'ACT', 'Agentic checker preview', 'https://yourwebsite.com or yourwebsite.com']
static = uniq(static + EXTRA); dynamic = [d for d in uniq(dynamic) if d not in set(static)]
json.dump({'static': static, 'dynamic': dynamic}, open(os.path.join(ROOT, 'i18n', 'en.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print(f"static: {len(static)} strings, {sum(map(len, static))} chars; dynamic: {len(dynamic)} strings, {sum(map(len, dynamic))} chars")
