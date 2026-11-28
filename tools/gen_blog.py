#!/usr/bin/env python3
"""DEEPDELL blog generator: markdown posts in, SEO-ready static pages out.

  python3 tools/gen_blog.py            # build /blog/, blog/rss.xml, blog/posts.json and print the SEO check
  python3 tools/gen_blog.py --strict   # exit with an error if any post has a blocking SEO problem
  python3 tools/i18n_build.py          # then rebuild the sitemap (it reads blog/posts.json)

Write posts in blog/posts/<slug>.md. Front matter (YAML between --- lines):
  title, description, date (YYYY-MM-DD), updated (optional), category, tags [..], keywords [..],
  faq: [{q: .., a: ..}]  (optional, becomes FAQ schema), draft: true (optional, not published)
The blog is English only. Needs: pip install markdown pyyaml
"""
import os, re, sys, json, html, glob, datetime
import yaml, markdown
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gen_pages import page_from_template, e, ROOT, SITE

POSTS_DIR = os.path.join(ROOT, 'blog', 'posts')
OUT = os.path.join(ROOT, 'blog')
IMG = SITE + '/assets/og-image.jpg'
VER = re.search(r'script\.js\?v=([0-9a-z]+)', open(os.path.join(ROOT, 'data.html'), encoding='utf-8').read()).group(1)
strict = '--strict' in sys.argv


def slugify(t):
    return re.sub(r'[^a-z0-9]+', '-', t.lower()).strip('-')


def load():
    posts = []
    for f in sorted(glob.glob(os.path.join(POSTS_DIR, '*.md'))):
        raw = open(f, encoding='utf-8').read()
        m = re.match(r'---\n(.*?)\n---\n(.*)', raw, flags=re.S)
        if not m:
            print('SKIP (no front matter):', f); continue
        meta = yaml.safe_load(m.group(1)) or {}
        if meta.get('draft'):
            print('draft, not published:', os.path.basename(f)); continue
        body = m.group(2).strip()
        slug = os.path.splitext(os.path.basename(f))[0]
        d = lambda v: v if isinstance(v, datetime.date) else datetime.date.fromisoformat(str(v))
        meta['date'] = d(meta['date']); meta['updated'] = d(meta.get('updated', meta['date']))
        text = markdown.markdown(body, extensions=['tables', 'fenced_code', 'sane_lists'])
        heads = []

        def add_id(mm):
            i = slugify(re.sub(r'<[^>]+>', '', mm.group(2)))
            heads.append((i, html.unescape(re.sub(r'<[^>]+>', '', mm.group(2)))))
            return '<h2 id="%s">%s</h2>' % (i, mm.group(2))
        text = re.sub(r'<h(2)>(.*?)</h2>', add_id, text)
        text = re.sub(r'<a href="(https?://[^"]+)"', r'<a href="\1" rel="noopener" target="_blank"', text)
        text = text.replace('<table>', '<div class="post-table"><table>').replace('</table>', '</table></div>')
        plain = html.unescape(re.sub(r'<[^>]+>', ' ', text))
        words = len(plain.split())
        posts.append(dict(slug=slug, meta=meta, body=body, html=text, heads=heads, words=words, read=max(1, round(words / 220)),
                          url='%s/blog/%s.html' % (SITE, slug)))
    posts.sort(key=lambda p: p['meta']['date'], reverse=True)
    return posts


def check(p):
    """SEO check. Returns (blocking, advice)."""
    m, bad, tip = p['meta'], [], []
    t, d = m.get('title', ''), m.get('description', '')
    if not 30 <= len(t) <= 60: (bad if len(t) > 65 or len(t) < 20 else tip).append('title is %d characters (aim for 30-60)' % len(t))
    if not 110 <= len(d) <= 160: (bad if len(d) > 170 or len(d) < 80 else tip).append('description is %d characters (aim for 110-160)' % len(d))
    if p['words'] < 600: tip.append('only %d words (comprehensive posts are usually 900+)' % p['words'])
    if len(p['heads']) < 3: tip.append('fewer than 3 H2 sections')
    if re.search(r'^# ', p['body'], flags=re.M): bad.append('the body has an H1: the title is the only H1')
    internal = len(re.findall(r'\]\((?!https?://|#)', p['body']))
    if internal < 2: tip.append('%d internal links (add 2 or more to services, tools or other posts)' % internal)
    if not m.get('keywords'): tip.append('no keywords listed')
    if not m.get('faq'): tip.append('no FAQ block (FAQ schema helps AI and search answers)')
    first = (m.get('keywords') or [''])[0].lower()
    if first and first not in t.lower(): tip.append('main keyword "%s" is not in the title' % first)
    if first and first not in re.sub(r'\s+', ' ', p['body'][:600].lower()): tip.append('main keyword is not in the first paragraph')
    if re.search(r'!\[\]\(', p['body']): bad.append('image without alt text')
    return bad, tip


def related(p, posts):
    s = set(p['meta'].get('tags') or []) | {p['meta'].get('category')}
    sc = sorted((o for o in posts if o is not p), key=lambda o: -len(s & (set(o['meta'].get('tags') or []) | {o['meta'].get('category')})))
    return sc[:3]


def card(p):
    m = p['meta']
    return ('<article class="page-card post-card"><span class="card-code">%s · %s</span><h3><a href="/blog/%s.html">%s</a></h3><p>%s</p>'
            '<a class="text-link" href="/blog/%s.html">Read the guide <span class="cta-arrow" aria-hidden="true"></span></a></article>'
            % (e(m['category'].upper()), p['meta']['date'].strftime('%d %b %Y').upper(), p['slug'], e(m['title']), e(m['description']), p['slug']))


def cta():
    return ('<div class="cta-strip"><div><h2>Want this done for your store?</h2><p>We build the tracking, automation and dashboards behind this advice.</p></div>'
            '<a class="btn primary" href="/contact.html">Talk to DEEPDELL <span class="cta-arrow" aria-hidden="true"></span></a></div>')


def finish(out, extra_ld=''):
    out = re.sub(r'\n*<!-- i18n:head -->.*?<!-- /i18n:head -->\n*', '\n', out, flags=re.S)
    out = re.sub(r'<!-- i18n:switch -->.*?<!-- /i18n:switch -->', '', out, flags=re.S)
    out = re.sub(r'<meta property="og:type" content="[^"]*">', '<meta property="og:type" content="article">', out)
    out = out.replace('</head>', extra_ld + '</head>', 1)
    return out.replace('<head>', '<head><base href="/">', 1)


def build_post(p, posts):
    m = p['meta']
    toc = ''
    if len(p['heads']) >= 3:
        toc = '<nav class="post-toc" aria-label="Contents"><strong>In this guide</strong><ol>%s</ol></nav>' % ''.join('<li><a href="/blog/%s.html#%s">%s</a></li>' % (p['slug'], i, e(t)) for i, t in p['heads'])
    faq = ''
    if m.get('faq'):
        faq = '<section class="post-faq"><h2 id="faq">Frequently asked questions</h2>%s</section>' % ''.join('<h3>%s</h3><p>%s</p>' % (e(f['q']), e(f['a'])) for f in m['faq'])
    rel = related(p, posts)
    relh = '<section class="post-related"><h2>Keep reading</h2><div class="page-grid">%s</div></section>' % ''.join(card(o) for o in rel) if rel else ''
    tags = ''.join('<span>%s</span>' % e(t) for t in (m.get('tags') or []))
    upd = ' · Updated %s' % m['updated'].strftime('%d %b %Y') if m['updated'] != m['date'] else ''
    main = ('<main><article class="post"><header class="post-head"><div class="breadcrumbs"><a href="/">DEEPDELL</a><span>/</span><a href="/blog/">Blog</a><span>/</span><span>%s</span></div>'
            '<span class="card-code">%s</span><h1>%s</h1><p class="post-lead">%s</p>'
            '<p class="post-meta"><time datetime="%s">%s</time>%s · %d min read · By DEEPDELL</p></header>'
            '%s<div class="post-body">%s</div>%s<div class="post-tags">%s</div>%s</article>%s</main>'
            % (e(m['title']), e(m['category'].upper()), e(m['title']), e(m['description']), m['date'].isoformat(), m['date'].strftime('%d %b %Y'), e(upd), p['read'],
               toc, p['html'], faq, tags, cta(), relh))
    ld = {"@context": "https://schema.org", "@type": "BlogPosting", "headline": m['title'], "description": m['description'], "url": p['url'],
          "mainEntityOfPage": {"@type": "WebPage", "@id": p['url']}, "datePublished": m['date'].isoformat(), "dateModified": m['updated'].isoformat(),
          "author": {"@type": "Organization", "name": "DEEPDELL", "url": SITE + "/"}, "publisher": {"@id": SITE + "/#organization"},
          "image": IMG, "inLanguage": "en", "articleSection": m['category'], "keywords": ', '.join(m.get('keywords') or []), "wordCount": p['words']}
    bc = {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": 1, "name": "DEEPDELL", "item": SITE + "/"},
        {"@type": "ListItem", "position": 2, "name": "Blog", "item": SITE + "/blog/"},
        {"@type": "ListItem", "position": 3, "name": m['title']}]}
    extra = ''
    if m.get('faq'):
        fq = {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
            {"@type": "Question", "name": f['q'], "acceptedAnswer": {"@type": "Answer", "text": f['a']}} for f in m['faq']]}
        extra = '<script type="application/ld+json">%s</script>' % json.dumps(fq, ensure_ascii=False, separators=(',', ':'))
    title = m['title'] + ' | DEEPDELL'
    out = page_from_template(title, m['description'], p['url'], main, [ld, bc])
    open(os.path.join(OUT, p['slug'] + '.html'), 'w', encoding='utf-8').write(finish(out, extra))


def build_index(posts):
    cats = sorted({p['meta']['category'] for p in posts})
    chips = ''.join('<a class="chip" href="/blog/#cat-%s">%s</a>' % (slugify(c), e(c)) for c in cats)
    sections = ''.join('<section class="section-pad" id="cat-%s"><div class="section-kicker">%s</div><div class="page-grid">%s</div></section>'
                       % (slugify(c), e(c.upper()), ''.join(card(p) for p in posts if p['meta']['category'] == c)) for c in cats)
    main = ('<main><section class="page-hero section-pad"><div><div class="breadcrumbs"><a href="/">DEEPDELL</a><span>/</span><span>Blog</span></div>'
            '<h1>E-commerce <em>growth guides.</em></h1><p>Practical, plain-English guides on Shopify, tracking, automation, SEO and AI for online stores. <a class="text-link" href="/blog/rss.xml">RSS feed</a></p>'
            '<div class="chips">%s</div></div></section>%s</main>' % (chips, sections))
    url = SITE + '/blog/'
    desc = 'Practical guides on Shopify, e-commerce tracking, automation, SEO and AI for online stores, from the DEEPDELL engineering team.'
    ld = {"@context": "https://schema.org", "@type": "Blog", "name": "DEEPDELL Blog", "url": url, "description": desc, "publisher": {"@id": SITE + "/#organization"},
          "blogPost": [{"@type": "BlogPosting", "headline": p['meta']['title'], "url": p['url'], "datePublished": p['meta']['date'].isoformat()} for p in posts]}
    bc = {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": 1, "name": "DEEPDELL", "item": SITE + "/"}, {"@type": "ListItem", "position": 2, "name": "Blog"}]}
    out = page_from_template('E-commerce Growth Guides: DEEPDELL Blog', desc, url, main, [ld, bc])
    alt = '<link rel="alternate" type="application/rss+xml" title="DEEPDELL Blog" href="/blog/rss.xml">'
    open(os.path.join(OUT, 'index.html'), 'w', encoding='utf-8').write(finish(out, alt))


def build_feeds(posts):
    items = ''.join('<item><title>%s</title><link>%s</link><guid>%s</guid><pubDate>%s</pubDate><category>%s</category><description>%s</description></item>'
                    % (e(p['meta']['title']), p['url'], p['url'], datetime.datetime.combine(p['meta']['date'], datetime.time(9)).strftime('%a, %d %b %Y %H:%M:%S +0000'),
                       e(p['meta']['category']), e(p['meta']['description'])) for p in posts)
    rss = ('<?xml version="1.0" encoding="UTF-8"?>\n<rss version="2.0"><channel><title>DEEPDELL Blog</title><link>%s/blog/</link>'
           '<description>Practical e-commerce, tracking, automation and AI guides.</description><language>en</language>%s</channel></rss>\n' % (SITE, items))
    open(os.path.join(OUT, 'rss.xml'), 'w', encoding='utf-8').write(rss)
    json.dump([dict(slug=p['slug'], url=p['url'], title=p['meta']['title'], date=p['meta']['date'].isoformat(), updated=p['meta']['updated'].isoformat(),
                    category=p['meta']['category']) for p in posts], open(os.path.join(OUT, 'posts.json'), 'w', encoding='utf-8'), indent=1)


if __name__ == '__main__':
    os.makedirs(POSTS_DIR, exist_ok=True)
    posts = load()
    for old in glob.glob(os.path.join(OUT, '*.html')):
        os.remove(old)
    blocked = 0
    for p in posts:
        build_post(p, posts)
        bad, tip = check(p)
        print('%-44s %4d words  %s' % (p['slug'], p['words'], 'OK' if not bad and not tip else ''))
        for b in bad: print('   BLOCKING:', b)
        for t in tip: print('   advice:  ', t)
        blocked += len(bad)
    build_index(posts); build_feeds(posts)
    print('%d post(s) built -> blog/' % len(posts))
    if strict and blocked: sys.exit(1)
