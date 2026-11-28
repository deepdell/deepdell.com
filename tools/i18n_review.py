#!/usr/bin/env python3
"""Translation review workflow: export a spreadsheet for a native speaker, import their corrections.

  python3 tools/i18n_review.py export ar ms id      # writes docs/translation-review/<lang>.csv
  python3 tools/i18n_review.py import ar path.csv   # applies the 'suggested' column to i18n/ar.json
  python3 tools/i18n_build.py                       # then rebuild the site

CSV columns: id, page, english, current, suggested, notes
The reviewer only fills in 'suggested' (and optionally 'notes') for rows that need a change.
Rows are ordered by importance: homepage first, then pricing, services and the tools.
"""
import csv, html, json, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, 'docs', 'translation-review')
ORDER = ['index', 'pricing', 'services', 'shopify-plus', 'ai', 'data', 'automation', 'support', 'industries', 'contact', 'tools',
         'utm-builder', 'ad-calculator', 'profit-calculator', 'discount-calculator', 'seo-preview', 'qr-generator', 'schema-generator',
         'ai-files-generator', 'agentic-check', 'commerce-calculator', 'game', 'contact-card', 'privacy']
norm = lambda s: re.sub(r'\s+', ' ', html.unescape(s)).strip()


def page_texts():
    out = {}
    for name in ORDER:
        p = os.path.join(ROOT, name + '.html')
        if os.path.exists(p):
            t = open(p, encoding='utf-8').read()
            t = re.sub(r'<script[^>]*>.*?</script>', lambda m: m.group(0) if 'ld+json' in m.group(0) else ' ', t, flags=re.S)
            out[name] = norm(t)
    return out


def export(langs):
    en = json.load(open(os.path.join(ROOT, 'i18n', 'en.json'), encoding='utf-8'))
    keys = en['static'] + en['dynamic']
    pages = page_texts()
    os.makedirs(OUT, exist_ok=True)
    for lang in langs:
        d = {norm(k): v for k, v in json.load(open(os.path.join(ROOT, 'i18n', lang + '.json'), encoding='utf-8')).items()}
        rows = []
        for k in keys:
            cur = d.get(norm(k))
            if not cur or norm(cur) == norm(k):
                continue  # brand names, file names and untranslated items need no review
            where = [n for n, t in pages.items() if norm(k) in t]
            rank = ORDER.index(where[0]) if where else len(ORDER)
            rows.append((rank, ', '.join(where[:3]) + (' …' if len(where) > 3 else '') if where else 'cookie banner / scripts', k, cur))
        rows.sort(key=lambda r: r[0])
        path = os.path.join(OUT, lang + '.csv')
        with open(path, 'w', encoding='utf-8-sig', newline='') as f:
            w = csv.writer(f, quoting=csv.QUOTE_ALL)
            w.writerow(['id', 'page', 'english', 'current', 'suggested', 'notes'])
            for i, (_, pg, k, cur) in enumerate(rows, 1):
                w.writerow([i, pg, k, cur, '', ''])
        print(f'{lang}: {len(rows)} rows -> {os.path.relpath(path, ROOT)}')


def import_(lang, path):
    p = os.path.join(ROOT, 'i18n', lang + '.json')
    d = json.load(open(p, encoding='utf-8'))
    by = {norm(k): k for k in d}
    n = 0
    with open(path, encoding='utf-8-sig', newline='') as f:
        for r in csv.DictReader(f):
            s = (r.get('suggested') or '').strip()
            if not s:
                continue
            k = by.get(norm(r['english']))
            if k is None:
                print('skipped (english text not found):', r['english'][:60])
                continue
            d[k] = s
            n += 1
    json.dump(d, open(p, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print(f'{lang}: applied {n} corrections. Now run: python3 tools/i18n_build.py')


if __name__ == '__main__':
    a = sys.argv[1:]
    if len(a) >= 2 and a[0] == 'export':
        export(a[1:])
    elif len(a) == 3 and a[0] == 'import':
        import_(a[1], a[2])
    else:
        print(__doc__)
