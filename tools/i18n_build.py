#!/usr/bin/env python3
"""Generate the translated site from the English pages.

  python3 tools/i18n_extract.py   # refresh i18n/en.json after editing English pages
  python3 tools/i18n_build.py     # regenerate /fr/, /de/, ... and update shared head/switcher

English pages at the repository root are the source of truth. Each language folder
(/fr/, /ar/, ...) is generated output: do not edit it by hand, edit i18n/<lang>.json
and re-run this script. Missing translations fall back to English.
"""
import re, json, glob, html, os, shutil

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = 'https://deepdell.com'
LANGS = {  # code: (native name, og:locale, text direction)
    'en': ('English', 'en_GB', 'ltr'),
    'fr': ('Français', 'fr_FR', 'ltr'),
    'de': ('Deutsch', 'de_DE', 'ltr'),
    'es': ('Español', 'es_ES', 'ltr'),
    'it': ('Italiano', 'it_IT', 'ltr'),
    'ar': ('العربية', 'ar_AR', 'rtl'),
    'ms': ('Bahasa Melayu (Malaysia)', 'ms_MY', 'ltr'),
    'id': ('Bahasa Indonesia', 'id_ID', 'ltr'),
}
TARGETS = [c for c in LANGS if c != 'en']
LANG_CURRENCY = {'fr': 'EUR', 'de': 'EUR', 'es': 'EUR', 'it': 'EUR', 'ar': 'AED', 'ms': 'MYR', 'id': 'IDR'}  # default price currency per language
HREFLANG = {'ms': 'ms-MY'}  # region-targeted versions; others are language-only
REGION = {'ms': {'locale': 'ms-MY', 'currency': 'MYR'}}  # number and currency formatting in tools
PAGES = sorted(os.path.basename(p) for p in glob.glob(os.path.join(ROOT, '*.html')) if not p.endswith('404.html'))
ATTRS = ('title', 'alt', 'aria-label', 'placeholder')
META = ('description', 'og:title', 'og:description', 'og:image:alt', 'twitter:title', 'twitter:description')
VER = '20261126g'


def page_url(lang, page):
    tail = '' if page == 'index.html' else page
    return f'{SITE}/{tail}' if lang == 'en' else f'{SITE}/{lang}/{tail}'


def norm(s):
    return re.sub(r'\s+', ' ', s).strip()


def make_tr(d):
    def tr(text):
        key = norm(html.unescape(text))
        return d.get(key)
    return tr


def translate_text(src, tr):
    """Translate text between tags, leaving <script>, <style> and comments untouched."""
    out, depth = [], 0
    for part in re.split(r'(<!--.*?-->|<[^>]*>)', src, flags=re.S):
        if part.startswith('<'):
            m = re.match(r'<(/?)(script|style)\b', part, re.I)
            if m:
                depth += -1 if m.group(1) else 1
            out.append(part)
            continue
        t = tr(part) if depth == 0 and part.strip() else None
        if t is None:
            out.append(part)
        else:
            lead = part[:len(part) - len(part.lstrip())]
            trail = part[len(part.rstrip()):]
            out.append(lead + html.escape(t, quote=False) + trail)
    return ''.join(out)


def translate_attrs(src, tr):
    def fix_tag(m):
        tag = m.group(0)
        if tag.startswith(('<script', '<style', '<!')):
            return tag
        for a in ATTRS:
            def rep(am):
                t = tr(am.group(2))
                return am.group(0) if t is None else f'{am.group(1)}="{html.escape(t)}"'
            tag = re.sub(r'(\s%s)="([^"]*)"' % a, rep, tag)
        return tag
    src = re.sub(r'<[a-zA-Z][^>]*>', fix_tag, src)
    for name in META:
        def rep(m):
            t = tr(m.group(2))
            return m.group(0) if t is None else f'{m.group(1)}{html.escape(t)}"'
        src = re.sub(r'(<meta (?:name|property)="%s" content=")([^"]*)"' % re.escape(name), rep, src)
    src = re.sub(r'<title>(.*?)</title>', lambda m: '<title>%s</title>' % html.escape(tr(m.group(1)) or html.unescape(m.group(1)), quote=False), src, flags=re.S)
    return src


def translate_jsonld(src, tr, lang, page):
    def fix(m):
        data = json.loads(m.group(2))
        def walk(o):
            if isinstance(o, dict):
                for k, v in list(o.items()):
                    if k in ('name', 'description', 'serviceType', 'slogan') and isinstance(v, str):
                        o[k] = tr(v) or v
                    elif k in ('serviceType', 'knowsAbout') and isinstance(v, list):
                        o[k] = [tr(x) or x if isinstance(x, str) else x for x in v]
                    elif k == 'item' and isinstance(v, str) and v == SITE + '/':
                        o[k] = page_url(lang, 'index.html')
                    elif k == 'url' and isinstance(v, str) and v == page_url('en', page) and page != 'index.html':
                        o[k] = page_url(lang, page)
                    else:
                        walk(v)
                if o.get('@type') in ('WebPage', 'Service', 'WebApplication', 'ContactPage', 'BreadcrumbList', 'ItemList'):
                    o.setdefault('inLanguage', lang)
            elif isinstance(o, list):
                for x in o:
                    walk(x)
        walk(data)
        return m.group(1) + json.dumps(data, ensure_ascii=False, separators=(',', ':')) + m.group(3)
    return re.sub(r'(<script type="application/ld\+json"[^>]*>)(.*?)(</script>)', fix, src, flags=re.S)


ARABIC = re.compile(r'[\u0600-\u06FF\u0750-\u077F\uFB50-\uFDFF\uFE70-\uFEFF]')


def isolate_latin(src):
    """On right-to-left pages, wrap English-only body text in <bdi> so its punctuation stays put."""
    head, sep, body = src.partition('<body')
    if not sep:
        return src
    out, depth, skip = [], 0, 0
    for part in re.split(r'(<!--.*?-->|<[^>]*>)', body, flags=re.S):
        if part.startswith('<'):
            m = re.match(r'<(/?)(script|style|textarea|option|title|svg)\b', part, re.I)
            if m:
                skip += -1 if m.group(1) else 1
            out.append(part)
            continue
        if skip == 0 and re.search(r'[A-Za-z]{2}', part) and not ARABIC.search(part) and not part.lstrip().startswith('{'):
            lead = part[:len(part) - len(part.lstrip())]
            trail = part[len(part.rstrip()):]
            out.append(f'{lead}<bdi>{part.strip()}</bdi>{trail}')
        else:
            out.append(part)
    return head + sep + ''.join(out)


def localise_paths(src, lang):
    """Pages live one folder deeper: make shared files absolute, keep page links relative."""
    def rep(m):
        attr, url = m.group(1), m.group(2)
        if re.match(r'(https?:|mailto:|tel:|#|data:|javascript:)', url):
            return m.group(0)
        if url == '/':
            return f'{attr}="/{lang}/"'
        if url.startswith('/'):
            base = url.split('?')[0].split('#')[0]
            if base.endswith('.html') and os.path.exists(os.path.join(ROOT, base.lstrip('/'))):
                return f'{attr}="/{lang}{url}"'
            return m.group(0)
        base = url.split('?')[0].split('#')[0]
        if base.endswith('.html'):
            return m.group(0)  # relative page link resolves inside /<lang>/
        return f'{attr}="/{url}"'
    return re.sub(r'\b(href|src)="([^"]*)"', rep, src)


def head_block(page, lang):
    links = [f'<link rel="alternate" hreflang="{HREFLANG.get(c, c)}" href="{page_url(c, page)}">' for c in LANGS]
    links.append(f'<link rel="alternate" hreflang="x-default" href="{page_url("en", page)}">')
    if LANGS[lang][2] == 'rtl':
        links.append('<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin><link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans+Arabic:wght@400;500;600;700&display=swap">')
    return '<!-- i18n:head -->' + ''.join(links) + '<!-- /i18n:head -->'


def switcher(page, lang):
    items = ''.join(
        f'<a href="{"/" if c == "en" else "/" + c + "/"}{"" if page == "index.html" else page}" hreflang="{HREFLANG.get(c, c)}" lang="{c}"'
        f'{" aria-current=\"true\"" if c == lang else ""}>{LANGS[c][0]}</a>' for c in LANGS)
    return (f'<!-- i18n:switch --><details class="lang-switch"><summary aria-label="Language: {LANGS[lang][0]}">'
            f'<span aria-hidden="true">{lang.upper()}</span></summary><div class="lang-menu" role="list">{items}</div></details><!-- /i18n:switch -->')


def apply_shared(src, page, lang, alternates=True):
    src = re.sub(r'<!-- i18n:head -->.*?<!-- /i18n:head -->', '', src, flags=re.S)
    src = re.sub(r'<!-- i18n:switch -->.*?<!-- /i18n:switch -->', '', src, flags=re.S)
    src = re.sub(r'<script src="/?i18n/[a-z]+\.js[^"]*"></script>\n?', '', src)
    if alternates:
        src = src.replace('</head>', head_block(page, lang) + '\n</head>', 1)
    src = src.replace('<div class="header-tools">', '<div class="header-tools">' + switcher(page, lang), 1)
    if lang != 'en':
        src = re.sub(r'(<script src="/?script\.js)', rf'<script src="/i18n/{lang}.js?v={VER}"></script>\n\1', src, count=1)
    return src


def amt_class(text):
    n = len(text)
    return 'amt' + (' amt-xl' if n >= 10 else ' amt-l' if n >= 7 else '')


def apply_currency(src, code):
    """Pre-render the pricing page in a language's default currency (the picker still lets visitors change it)."""
    def one(m):
        tag, cls, attr, text = m
        prices = json.loads(html.unescape(attr))
        val = prices.get(code, text)
        if cls.startswith('amt'):
            cls = amt_class(val)
        return '<%s class="%s" data-p="%s">%s</%s>' % (tag, cls, attr, html.escape(val, quote=False), tag)
    src = re.sub(r'<(span|strong)( class="[^"]*")? data-p="([^"]+)">([^<]*)</\1>', lambda m: one((m.group(1), (m.group(2) or ' class=""')[8:-1], m.group(3), m.group(4))), src)
    src = re.sub(r'<option value="USD" selected>', '<option value="USD">', src)
    return src.replace('<option value="%s">' % code, '<option value="%s" selected>' % code)


def build_page(page, lang, d):
    src = open(os.path.join(ROOT, page), encoding='utf-8').read()
    tr = make_tr(d)
    src = translate_jsonld(src, tr, lang, page)
    src = translate_attrs(src, tr)
    src = translate_text(src, tr)
    src = localise_paths(src, lang)
    name, locale, direction = LANGS[lang]
    if direction == 'rtl':
        src = isolate_latin(src)
    src = re.sub(r'<html lang="en"', f'<html lang="{lang}" dir="{direction}"', src, count=1)
    src = re.sub(r'<link rel="canonical" href="[^"]*">', f'<link rel="canonical" href="{page_url(lang, page)}">', src)
    src = re.sub(r'<meta property="og:url" content="[^"]*">', f'<meta property="og:url" content="{page_url(lang, page)}">', src)
    src = re.sub(r'<meta property="og:locale" content="[^"]*">', f'<meta property="og:locale" content="{locale}">', src)
    if page == 'pricing.html' and lang in LANG_CURRENCY:
        src = apply_currency(src, LANG_CURRENCY[lang])
    return apply_shared(src, page, lang)


def runtime_js(lang, d, dynamic):
    table = {k: d[k] for k in dynamic if k in d}
    # Short shared UI strings that scripts also create (buttons, labels) come from the static set.
    for k, v in d.items():
        if k not in table and len(k) <= 40:
            table[k] = v
    return ('/* Generated by tools/i18n_build.py: runtime strings for text created by scripts. */\n'
            f'window.DD_LANG={json.dumps(lang)};'
            + ''.join(f'window.DD_{k.upper()}={json.dumps(v)};' for k, v in REGION.get(lang, {}).items())
            + f'window.DD_I18N={json.dumps(table, ensure_ascii=False, separators=(",", ":"))};\n')


def sitemap():
    rows = []
    for page in PAGES:
        alts = ''.join(f'<xhtml:link rel="alternate" hreflang="{HREFLANG.get(c, c)}" href="{page_url(c, page)}"/>' for c in LANGS)
        alts += f'<xhtml:link rel="alternate" hreflang="x-default" href="{page_url("en", page)}"/>'
        for c in LANGS:
            rows.append(f'  <url><loc>{page_url(c, page)}</loc><lastmod>2026-11-26</lastmod>{alts}</url>')
    xml = ('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" '
           'xmlns:xhtml="http://www.w3.org/1999/xhtml">\n' + '\n'.join(rows) + '\n</urlset>\n')
    open(os.path.join(ROOT, 'sitemap.xml'), 'w', encoding='utf-8').write(xml)
    open(os.path.join(ROOT, 'sitemap.txt'), 'w', encoding='utf-8').write(
        '\n'.join(page_url(c, p) for p in PAGES for c in LANGS) + '\n')


def main():
    en = json.load(open(os.path.join(ROOT, 'i18n', 'en.json'), encoding='utf-8'))
    report = []
    for page in PAGES + ['404.html']:  # English: shared head + switcher only
        p = os.path.join(ROOT, page)
        with open(p, encoding='utf-8') as fh:
            src = fh.read()
        with open(p, 'w', encoding='utf-8') as fh:
            fh.write(apply_shared(src, page if page != '404.html' else 'index.html', 'en', alternates=page != '404.html'))
    for lang in TARGETS:
        path = os.path.join(ROOT, 'i18n', f'{lang}.json')
        d = json.load(open(path, encoding='utf-8')) if os.path.exists(path) else {}
        d = {norm(k): v for k, v in d.items() if v}
        out = os.path.join(ROOT, lang)
        shutil.rmtree(out, ignore_errors=True)
        os.makedirs(out)
        for page in PAGES:
            open(os.path.join(out, page), 'w', encoding='utf-8').write(build_page(page, lang, d))
        open(os.path.join(ROOT, 'i18n', f'{lang}.js'), 'w', encoding='utf-8').write(runtime_js(lang, d, en['dynamic']))
        missing = [s for s in en['static'] + en['dynamic'] if norm(s) not in d]
        report.append(f'{lang}: {len(d)} translations, {len(missing)} source strings untranslated')
    sitemap()
    print('\n'.join(report))


if __name__ == '__main__':
    main()
