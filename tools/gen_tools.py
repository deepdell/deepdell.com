#!/usr/bin/env python3
"""Generate the free tools pages (English sources): tools.html and the four calculators/generators.

  python3 tools/gen_tools.py       # rewrite the tool pages
  python3 tools/i18n_extract.py    # refresh i18n/en.json
  python3 tools/i18n_build.py      # rebuild the translated pages

All tools run in the visitor's browser (tools.js): no server, no storage, no tracking.
Every visible sentence is in the generated HTML, so the translation pipeline picks it up.
"""
import os, re, json, html, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gen_pages import page_from_template, breadcrumb, CUR, e, ROOT, SITE

VER = re.search(r'script\.js\?v=([0-9a-z]+)', open(os.path.join(ROOT, 'data.html'), encoding='utf-8').read()).group(1)


def hero(crumb, a, b, lead):
    return ('<section class="page-hero section-pad"><div><div class="breadcrumbs"><a href="/">DEEPDELL</a><span>/</span><span>%s</span></div>'
            '<h1>%s <em>%s</em></h1><p>%s</p></div></section>') % (e(crumb), e(a), e(b), e(lead))


def field(name, label, hint=None, ph=None, kind='number', extra=''):
    h = '<small class="tl-h">%s</small>' % e(hint) if hint else ''
    p = ' placeholder="%s"' % html.escape(ph) if ph else ''
    if kind == 'number':
        attrs = 'type="number" inputmode="decimal" step="any" min="0"'
    elif kind == 'textarea':
        return '<label class="tl-field"><span class="tl-l">%s</span><textarea name="%s" rows="3"%s%s></textarea>%s</label>' % (e(label), name, p, extra, h)
    else:
        attrs = 'type="text" inputmode="%s" autocomplete="off"' % kind
    return '<label class="tl-field"><span class="tl-l">%s</span><input %s name="%s"%s%s>%s</label>' % (e(label), attrs, name, p, extra, h)


def currency():
    opts = ''.join('<option value="%s">%s</option>' % (k, e(c['label'])) for k, c in CUR.items())
    return '<label class="tl-field"><span class="tl-l">Currency</span><select name="cur">%s</select></label>' % opts


def kpi(key, label, big=False):
    return '<div class="kpi%s"><span>%s</span><strong data-out="%s">—</strong></div>' % (' kpi-big' if big else '', e(label), key)


def verdicts(good, mid, bad):
    return ''.join('<p class="verdict %s" data-verdict="%s" hidden>%s</p>' % (k, k, e(t)) for k, t in (('good', good), ('mid', mid), ('bad', bad)))


def card(left, right, title_l):
    return ('<div class="tool-grid"><form class="tool-card" novalidate autocomplete="off"><h3 class="tl-title">%s</h3>%s'
            '<button class="btn ghost tl-reset" type="reset">Reset</button></form><div class="tool-card tool-result">%s</div></div>') % (e(title_l), left, right)


def cta():
    return ('<div class="cta-strip"><div><h2>Want this done automatically?</h2><p>We build dashboards and automations around your exact process, across every platform you use.</p></div>'
            '<a class="btn primary" href="automation.html">Explore dashboards &amp; automation <span class="cta-arrow" aria-hidden="true"></span></a></div>'
            '<p class="tl-more"><a class="text-link" href="#signup" data-su-open>Get news &amp; offers</a></p>')


def page(slug, title, desc, crumb, main, name, kind_ld='WebApplication'):
    url = '%s/%s.html' % (SITE, slug)
    ld = {"@context": "https://schema.org", "@type": kind_ld, "name": name, "url": url, "description": desc,
          "applicationCategory": "BusinessApplication", "operatingSystem": "Any (web browser)", "isAccessibleForFree": True,
          "offers": {"@type": "Offer", "price": "0", "priceCurrency": "USD"}, "publisher": {"@id": SITE + "/#organization"}}
    out = page_from_template(title, desc, url, main, [ld, breadcrumb(crumb)])
    out = out.replace('<script src="script.js?v=%s"></script>' % VER, '<script src="script.js?v=%s"></script>' % VER + ('<script src="assets/qrcode.js"></script>' if slug == 'qr-generator' else '') + '<script src="tools.js?v=%s"></script>' % VER)
    open(os.path.join(ROOT, slug + '.html'), 'w', encoding='utf-8').write(out)


# ───────────────────────── UTM link builder ─────────────────────────
def utm():
    presets = ''.join('<button class="chip" type="button" data-preset="%s">%s</button>' % (v, e(n)) for n, v in
                      (('Google Ads', 'google|cpc'), ('Meta Ads', 'facebook|paid_social'), ('Instagram', 'instagram|social'), ('Snapchat Ads', 'snapchat|paid_social'), ('Newsletter', 'newsletter|email')))
    left = ('<p class="tl-sub">Quick start</p><div class="chips">%s</div>' % presets
            + field('url', 'Website URL', None, 'https://yourwebsite.com', 'url')
            + field('source', 'Campaign source', 'Where the traffic comes from, for example google or newsletter.', 'google', 'text')
            + field('medium', 'Campaign medium', 'The type of channel, for example cpc, email or social.', 'cpc', 'text')
            + field('campaign', 'Campaign name', 'Your campaign, for example spring_sale.', 'spring_sale', 'text')
            + field('term', 'Campaign term (optional)', 'The paid keyword.', None, 'text')
            + field('content', 'Campaign content (optional)', 'Tells similar links or ads apart.', None, 'text'))
    right = ('<h3 class="tl-title">Your campaign link</h3><div class="tl-out is-empty"><code data-out="link"></code>'
             '<p class="tl-empty">Fill in the website, source, medium and campaign to build your link.</p></div>'
             '<p class="tl-msg" data-msg="url" hidden>Enter a full website address that starts with https://</p>'
             '<button class="btn primary" type="button" data-copy disabled><span class="b1">Copy link</span><span class="b2" hidden>Copied</span></button>'
             '<p class="tl-note">Tip: use lowercase letters and no spaces so your reports stay clean.</p>')
    main = '<main>' + hero('UTM Link Builder', 'Build trackable', 'campaign links.', 'Add UTM parameters to any web address so your analytics shows exactly which channel, campaign and ad brought each visitor.') \
        + '<section class="section-pad"><div class="tool" data-tool="utm">' + card(left, right, 'Campaign details') + '</div>' + cta() + '</section></main>'
    page('utm-builder', 'UTM Link Builder: Free Campaign URL Generator | DEEPDELL',
         'Free UTM link builder. Create trackable campaign links for Google Analytics in seconds. Nothing is stored or sent anywhere.', 'UTM Link Builder', main, 'UTM Link Builder')


# ───────────────────────── ad performance ─────────────────────────
def ad():
    left = (currency() + field('spend', 'Ad spend', None, '1000') + field('revenue', 'Revenue from ads', None, '4000') + field('orders', 'Orders from ads', None, '80')
            + field('margin', 'Gross margin (%)', 'The share of revenue left after product cost.', '40')
            + '<p class="tl-sub">Optional: traffic</p>' + field('impressions', 'Impressions', None, '200000') + field('clicks', 'Clicks', None, '3000'))
    right = ('<h3 class="tl-title">Your results</h3><p class="tl-empty" data-state="empty">Enter your numbers to see the results.</p><div data-state="ready" hidden>'
             + verdicts('Your ads are profitable at this margin.', 'Your ads are about break-even at this margin.', 'Your ads are losing money at this margin.')
             + '<div class="kpis">' + kpi('roas', 'ROAS', True) + kpi('be', 'Break-even ROAS', True) + kpi('profit', 'Profit after ads', True) + kpi('cpa', 'Cost per order') + kpi('aov', 'Average order value')
             + kpi('cvr', 'Conversion rate') + kpi('ctr', 'Click-through rate') + kpi('cpc', 'Cost per click') + kpi('cpm', 'Cost per 1,000 views') + '</div>'
             + '<p class="tl-note">ROAS is revenue divided by ad spend. Break-even ROAS is the minimum you need to cover product costs.</p></div>')
    main = '<main>' + hero('Ad Performance Calculator', 'Do your ads', 'really make money?', 'Enter your ad spend and results to see ROAS, cost per order and the break-even point for your margin.') \
        + '<section class="section-pad"><div class="tool" data-tool="ad">' + card(left, right, 'Your numbers') + '</div>' + cta() + '</section></main>'
    page('ad-calculator', 'Ad Performance Calculator: ROAS, CPA and Break-even | DEEPDELL',
         'Free ad calculator. Work out ROAS, break-even ROAS, cost per order, click-through rate, cost per click and profit after ad spend.', 'Ad Performance Calculator', main, 'Ad Performance Calculator')


# ───────────────────────── profit and pricing ─────────────────────────
def profit():
    left = (currency() + field('price', 'Selling price', None, '49') + field('cost', 'Product cost', None, '18') + field('ship', 'Shipping cost you pay', None, '4')
            + field('platform', 'Platform or marketplace fee (%)', None, '10') + field('payment', 'Payment fee (%)', None, '2.9') + field('fixed', 'Fixed fee per order', None, '0.30')
            + field('ads', 'Advertising cost per order', None, '6') + field('target', 'Target margin (%)', None, '30', 'number', ' value="30"'))
    right = ('<h3 class="tl-title">Your results</h3><p class="tl-empty" data-state="empty">Enter your price and costs to see the results.</p><div data-state="ready" hidden>'
             + verdicts('You earn a profit on each order.', 'You break even on each order.', 'You lose money on each order.')
             + '<div class="kpis">' + kpi('profit', 'Profit per order', True) + kpi('margin', 'Profit margin', True) + kpi('markup', 'Markup on product cost', True)
             + kpi('fees', 'Total fees and ad cost') + kpi('be', 'Break-even price') + kpi('goal', 'Price for your target margin') + '</div>'
             + '<p class="tl-note">Fees change often, so check the current rates for your platform and payment provider.</p></div>')
    main = '<main>' + hero('Profit & Pricing Calculator', 'Know your real', 'profit per order.', 'Add your costs and fees to see what each sale really earns, and the price you need to reach your target margin.') \
        + '<section class="section-pad"><div class="tool" data-tool="profit">' + card(left, right, 'Price and costs') + '</div>' + cta() + '</section></main>'
    page('profit-calculator', 'Profit & Pricing Calculator for Online Stores | DEEPDELL',
         'Free profit calculator for e-commerce. See profit per order after fees, shipping and ads, plus your break-even price and the price for your target margin.', 'Profit & Pricing Calculator', main, 'Profit & Pricing Calculator')


# ───────────────────────── SEO and social preview ─────────────────────────
def seo():
    def count(key, hint):
        return ('<div class="tl-count" data-field="%s"><span><b data-out="%s">0</b> <span>characters</span></span><em data-st="none">%s</em><em data-st="short" hidden>Too short</em>'
                '<em data-st="good" hidden>Good length</em><em data-st="long" hidden>May be cut off</em></div>') % (key, 'tcount' if key == 'title' else 'dcount', e(hint))
    left = (field('title', 'Page title', None, 'Free Profit Calculator for Online Stores', 'text') + count('title', 'Aim for about 30 to 60 characters.')
            + field('desc', 'Meta description', None, 'Work out your real profit per order after fees, shipping and ads.', 'textarea') + count('desc', 'Aim for about 70 to 160 characters.')
            + field('url', 'Page address', None, 'https://yourwebsite.com/page', 'url') + field('site', 'Site name (optional)', None, None, 'text')
            + field('image', 'Social image address (optional)', None, 'https://yourwebsite.com/image.jpg', 'url')
            + '<span hidden data-ph="title">Your page title appears here</span><span hidden data-ph="desc">Your meta description appears here. Write a clear summary that makes people want to click.</span>')
    right = ('<h3 class="tl-title">Google result</h3><div class="seg" role="group"><button type="button" class="on" data-device="desktop" aria-pressed="true">Computer</button>'
             '<button type="button" data-device="mobile" aria-pressed="false">Phone</button></div>'
             '<div class="g-card"><div class="g-site"><span class="g-fav" aria-hidden="true"></span><div><b data-out="site"></b><small data-out="crumb"></small></div></div>'
             '<div class="g-title" data-out="gtitle"></div><div class="g-desc" data-out="gdesc"></div></div>'
             '<h3 class="tl-title tl-gap">Social share card</h3><div class="og-card"><img class="og-img" alt="" hidden><div class="og-body"><small data-out="ohost"></small>'
             '<b data-out="otitle"></b><span data-out="odesc"></span></div></div>'
             '<p class="tl-note">Search engines may show a different title or description than the one you write.</p>')
    main = '<main>' + hero('SEO & Social Preview', 'See your page', 'before Google does.', 'Type your title and description to preview the Google result and the social share card, with live length guidance.') \
        + '<section class="section-pad"><div class="tool" data-tool="seo">' + card(left, right, 'Your page') + '</div>' + cta() + '</section></main>'
    page('seo-preview', 'SEO & Social Preview: Google Snippet and Share Card Checker | DEEPDELL',
         'Free SEO preview tool. See how your title and description look in Google and on social media, with live length checks.', 'SEO & Social Preview', main, 'SEO & Social Preview')



# ───────────────────────── helpers for the second batch ─────────────────────────
def select(name, label, options, extra=''):
    o = ''.join('<option value="%s">%s</option>' % (v, e(t)) for v, t in options)
    return '<label class="tl-field"><span class="tl-l">%s</span><select name="%s"%s>%s</select></label>' % (e(label), name, extra, o)


def check(name, label, checked=False):
    return '<label class="tl-check"><input type="checkbox" name="%s"%s><span>%s</span></label>' % (name, ' checked' if checked else '', e(label))


def page_js(slug, title, desc, crumb, main, name, extra_script=''):
    page(slug, title, desc, crumb, main, name)
    if extra_script:
        fp = os.path.join(ROOT, slug + '.html')
        t = open(fp, encoding='utf-8').read()
        t = t.replace('<script src="script.js?v=%s"></script>' % VER, '<script src="script.js?v=%s"></script>' % VER + extra_script, 1)
        open(fp, 'w', encoding='utf-8').write(t)


# ───────────────────────── discount calculator ─────────────────────────
def discount():
    left = (field('margin', 'Current gross margin (%)', 'The share of the price left after product cost.', '40') + field('discount', 'Discount (%)', None, '15')
            + field('orders', 'Current orders per month (optional)', None, '200'))
    right = ('<h3 class="tl-title">Your results</h3><p class="tl-empty" data-state="empty">Enter your margin and discount to see the results.</p><div data-state="ready" hidden>'
             + verdicts('This discount still leaves you with a profit.', 'This discount still leaves you with a profit.', 'This discount makes you lose money on every sale.')
             + '<div class="kpis">' + kpi('newmargin', 'Margin after discount', True) + kpi('extra', 'Extra sales needed', True) + kpi('needed', 'Orders needed per month', True)
             + kpi('max', 'Maximum discount before a loss') + '</div>'
             + '<p class="tl-note">This assumes your costs stay the same and the extra sales come from the discount.</p></div>')
    main = '<main>' + hero('Discount Calculator', 'Is your discount', 'worth it?', 'Enter your margin and discount to see how many extra sales you need just to earn the same profit.') \
        + '<section class="section-pad"><div class="tool" data-tool="discount">' + card(left, right, 'Your numbers') + '</div>' + cta() + '</section></main>'
    page('discount-calculator', 'Discount Calculator: How Much Extra Sales Do You Need? | DEEPDELL',
         'Free discount calculator for online stores. See your new margin and how much extra sales volume a promotion needs to keep the same profit.', 'Discount Calculator', main, 'Discount Calculator')


# ───────────────────────── AI and search files ─────────────────────────
def aifiles():
    left = (field('name', 'Business name', None, 'Your Business', 'text') + field('url', 'Website URL', None, 'https://yourwebsite.com', 'url')
            + field('desc', 'One-line description', None, 'We sell sports gear online and ship across Europe.', 'text')
            + field('pages', 'Key pages', 'One per line: title | address | short note (the note is optional).', 'Shop | https://yourwebsite.com/shop | All products', 'textarea', ' rows="5"')
            + field('sitemap', 'Sitemap address (optional)', None, 'https://yourwebsite.com/sitemap.xml', 'url')
            + check('allow', 'Allow AI crawlers such as GPTBot, ClaudeBot and PerplexityBot', True))
    box = lambda key, fname: ('<div class="code-head"><b>%s</b><span class="code-actions"><button class="btn ghost sm" type="button" data-copy="%s"><span class="b1">Copy</span><span class="b2" hidden>Copied</span></button>'
                              '<button class="btn ghost sm" type="button" data-dl="%s"><span>Download</span></button></span></div><pre class="tl-code"><code data-out="%s"></code></pre>') % (fname, key, key, key)
    right = ('<h3 class="tl-title">Your files</h3><p class="tl-empty" data-state="empty">Enter your business name to create your files.</p><div data-state="ready" hidden>'
             + box('llms', 'llms.txt') + box('robots', 'robots.txt')
             + '<p class="tl-note">Upload both files to the root of your website, for example yourwebsite.com/llms.txt.</p></div>')
    main = '<main>' + hero('AI & Search Files Generator', 'Help AI and search', 'understand your site.', 'Create an llms.txt file and a robots.txt file for your website, ready to copy or download.') \
        + '<section class="section-pad"><div class="tool" data-tool="ai">' + card(left, right, 'Your website') + '</div>' + cta() + '</section></main>'
    page('ai-files-generator', 'AI & Search Files Generator: llms.txt and robots.txt | DEEPDELL',
         'Free generator for llms.txt and robots.txt. Help AI assistants and search engines understand your website. Runs in your browser.', 'AI & Search Files Generator', main, 'AI & Search Files Generator')


# ───────────────────────── schema generator ─────────────────────────
def schema():
    curs = [(k, c['label']) for k, c in CUR.items()]
    curs = [(k, k) for k, _ in curs]
    prod = ('<div data-for="product">' + field('pname', 'Product name', None, 'Trail Running Shoes', 'text') + field('pdesc', 'Description', None, 'Lightweight shoes with strong grip for trail running.', 'textarea', ' rows="2"')
            + field('pimage', 'Image address', None, 'https://yourwebsite.com/shoes.jpg', 'url') + field('brand', 'Brand', None, None, 'text') + field('sku', 'SKU', None, None, 'text')
            + field('price', 'Price', None, '89.00') + select('cur', 'Currency', curs)
            + select('avail', 'Availability', [('instock', 'In stock'), ('outofstock', 'Out of stock'), ('preorder', 'Pre-order')]) + field('purl', 'Page address', None, 'https://yourwebsite.com/shoes', 'url') + '</div>')
    faq = ('<div data-for="faq" hidden>' + field('faq', 'Questions and answers', 'Write the question on one line and the answer on the lines below. Leave a blank line between questions.',
           'Do you ship internationally?\nYes, we ship to most countries.\n\nCan I return an item?\nYes, within 30 days.', 'textarea', ' rows="8"') + '</div>')
    org = ('<div data-for="org" hidden>' + field('oname', 'Business name', None, 'Your Business', 'text') + field('ourl', 'Website URL', None, 'https://yourwebsite.com', 'url')
           + field('ologo', 'Logo address', None, 'https://yourwebsite.com/logo.png', 'url') + field('oemail', 'Contact email', None, 'hello@yourwebsite.com', 'text')
           + field('osocial', 'Social profile addresses', 'One address per line.', 'https://www.linkedin.com/company/yourbusiness', 'textarea', ' rows="3"') + '</div>')
    left = select('kind', 'Markup type', [('product', 'Product'), ('faq', 'FAQ'), ('org', 'Organization')]) + prod + faq + org
    right = ('<h3 class="tl-title">Your structured data</h3><p class="tl-empty" data-state="empty">Fill in the details to create your markup.</p><div data-state="ready" hidden>'
             '<div class="code-head"><b>JSON-LD</b><span class="code-actions"><button class="btn ghost sm" type="button" data-copy><span class="b1">Copy</span><span class="b2" hidden>Copied</span></button></span></div>'
             '<pre class="tl-code"><code data-out="code"></code></pre><p class="tl-note">Paste it into the page head or body, then test it with Google\'s Rich Results Test before publishing.</p></div>')
    main = '<main>' + hero('Schema Markup Generator', 'Create structured data', 'for search engines.', 'Generate JSON-LD for products, FAQs and your organization so search engines can show richer results.') \
        + '<section class="section-pad"><div class="tool" data-tool="schema">' + card(left, right, 'Markup details') + '</div>' + cta() + '</section></main>'
    page('schema-generator', 'Schema Markup Generator: Product, FAQ and Organization JSON-LD | DEEPDELL',
         'Free schema markup generator. Create Product, FAQ and Organization structured data (JSON-LD) to copy into your website.', 'Schema Markup Generator', main, 'Schema Markup Generator')


# ───────────────────────── QR code generator ─────────────────────────
def qr():
    left = (field('text', 'Text or web address', None, 'https://yourwebsite.com', 'textarea', ' rows="3"')
            + select('size', 'PNG size', [('s', 'Small'), ('m', 'Medium'), ('l', 'Large')], '')
            + '<div class="row2"><label class="tl-field"><span class="tl-l">QR colour</span><input type="color" name="fg" value="#000000"></label>'
              '<label class="tl-field"><span class="tl-l">Background colour</span><input type="color" name="bg" value="#ffffff"></label></div>'
            + '<small class="tl-h tl-keep">Keep strong contrast between the two colours so phones can scan it.</small>')
    right = ('<h3 class="tl-title">Your QR code</h3><p class="tl-empty" data-state="empty">Type a link or text to create your QR code.</p>'
             '<p class="tl-msg" data-msg="long" hidden>That is too long for a QR code. Try something shorter.</p>'
             '<div data-state="ready" hidden><div class="qr-box"></div>'
             '<p class="tl-msg" data-msg="contrast" hidden>Low contrast: use a dark QR colour on a light background so phones can scan it.</p>'
             '<div class="qr-actions"><button class="btn primary" type="button" data-dl="png" disabled><span>Download PNG</span></button>'
             '<button class="btn ghost" type="button" data-dl="svg" disabled><span>Download SVG</span></button></div>'
             '<p class="tl-note">Always test your QR code with a phone before printing.</p></div>')
    main = '<main>' + hero('QR Code Generator', 'Make a QR code', 'in seconds.', 'Turn any link or text into a QR code you can download for print, packaging and ads.') \
        + '<section class="section-pad"><div class="tool" data-tool="qr">' + card(left, right, 'QR code details') + '</div>' + cta() + '</section></main>'
    page('qr-generator', 'QR Code Generator: Free, Downloadable QR Codes | DEEPDELL',
         'Free QR code generator for links, text and campaigns. Download as PNG or SVG. Nothing is stored or sent anywhere.', 'QR Code Generator', main, 'QR Code Generator')


# ───────────────────────── arcade game ─────────────────────────
def arcade():
    badge = lambda k, n, pts: '<li data-badge="%s"><b>%s</b><span>%s points</span></li>' % (k, e(n), pts)
    labels = ''.join('<span data-s="%s" hidden>%s</span>' % (k, e(v)) for k, v in (
        ('badge_rookie', 'New badge: Rookie Seller'), ('badge_merchant', 'New badge: Merchant'), ('badge_scaleup', 'New badge: Scale-up'), ('badge_unicorn', 'New badge: Unicorn'),
        ('share_a', 'I scored'), ('share_b', 'in DEEPDELL Cart Dash.')))
    game = ('<div class="arcade" data-arcade><div class="ar-hud"><div><span>Score</span><strong data-o="score">0</strong></div><div><span>Combo</span><strong data-o="combo">x1</strong></div>'
            '<div><span>Lives</span><strong data-o="lives">❤❤❤</strong></div><div><span>Best</span><strong data-o="best">0</strong></div></div>'
            '<div class="ar-stage"><canvas width="360" height="520" tabindex="0" role="img" aria-label="Cart Dash game area"></canvas>'
            '<div class="ar-pane" data-pane="start"><h2>Cart Dash</h2><p>Slide your cart to catch 📦 orders and ⭐ reviews. Dodge 💸 refunds and 🐞 bugs. Grab a 🤖 bot to pull orders in.</p>'
            '<button class="btn primary" type="button" data-play="daily"><span>Play today\'s run</span></button>'
            '<button class="btn ghost" type="button" data-play="free"><span>Free play</span></button>'
            '<p class="ar-fine">Daily run #<b data-o="dayno">1</b> is the same for everyone. Day streak: <b data-o="streak">0</b></p></div>'
            '<div class="ar-pane" data-pane="over" hidden><h2>Game over</h2><p class="ar-big" data-o="final">0</p><p class="ar-pill" data-o="newbest" hidden>New personal best!</p>'
            '<p class="ar-pill" data-o="newbadge" hidden></p>'
            '<button class="btn primary" type="button" data-play="free"><span>Play again</span></button>'
            '<button class="btn ghost" type="button" data-o="share"><span class="b1">Share your score</span><span class="b2" hidden>Copied</span></button>'
            '<a class="text-link" href="#signup" data-su-open>Get news &amp; offers</a></div></div>'
            '<p class="ar-fine">Move with your finger, mouse or the arrow keys. Space pauses. Your scores stay in this browser.</p>' + labels + '</div>')
    side = ('<div class="tool-card"><h3 class="tl-title">Badges</h3><ul class="ar-badges">%s</ul>'
            '<p class="tl-note">Faster items and more bugs arrive as you play. Combos multiply your points up to x5.</p></div>'
            % (badge('rookie', 'Rookie Seller', 100) + badge('merchant', 'Merchant', 400) + badge('scaleup', 'Scale-up', 900) + badge('unicorn', 'Unicorn', 1800)))
    main = '<main>' + hero('Cart Dash', 'Catch the orders,', 'dodge the bugs.', 'A quick arcade break. Play the daily run, build a streak and share your score. Takes about a minute.') \
        + '<section class="section-pad"><div class="ar-wrap">' + game + side + '</div>' + cta() + '</section></main>'
    page_js('arcade', 'Cart Dash: Free Daily Arcade Game for E-commerce People | DEEPDELL',
            'Play Cart Dash, a quick browser arcade game. Catch orders, dodge refunds and bugs, keep a daily streak and share your score. Free, no sign-up.', 'Cart Dash', main, 'Cart Dash',
            '<script src="arcade.js?v=%s"></script>' % VER)

# ───────────────────────── hub ─────────────────────────
TOOLS_MKT = [('M01 / TRACKING', 'UTM Link Builder', 'Add campaign tracking to any link so analytics shows exactly where each visitor came from.', 'utm-builder.html'),
             ('M02 / ADVERTISING', 'Ad Performance Calculator', 'Work out ROAS, cost per order and break-even to see if your ads really make money.', 'ad-calculator.html'),
             ('M03 / QR CODES', 'QR Code Generator', 'Turn any link or text into a downloadable QR code for print, packaging and ads.', 'qr-generator.html')]
TOOLS_ECOM = [('E01 / PRICING', 'Profit & Pricing Calculator', 'Find your real profit per order after fees, shipping and ads, and the price you need.', 'profit-calculator.html'),
              ('E02 / PROMOTIONS', 'Discount Calculator', 'See how much extra sales a discount needs just to earn the same profit.', 'discount-calculator.html'),
              ('E03 / BENCHMARK', 'Commerce Calculator', "Benchmark your store's conversion, margin and repeat purchases and see the revenue opportunity.", 'commerce-calculator.html')]
TOOLS_SEARCH = [('S01 / SEO', 'SEO & Social Preview', 'See how your page looks on Google and social media, with live length checks.', 'seo-preview.html'),
                ('S02 / STRUCTURED DATA', 'Schema Markup Generator', 'Create product, FAQ and organization structured data for richer search results.', 'schema-generator.html'),
                ('S03 / AI SEARCH', 'AI & Search Files Generator', 'Create llms.txt and robots.txt files that help AI assistants and search engines understand your site.', 'ai-files-generator.html'),
                ('S04 / AI READINESS', 'Agentic Readiness Checker', 'Check whether AI agents and search engines can discover and understand your website.', 'agentic-check.html')]

TOOLS_PLAY = [('G01 / GAME', 'Cart Dash', 'Catch orders, dodge refunds and bugs, keep a daily streak and share your score.', 'arcade.html')]


def hub():
    cards = lambda items: ''.join('<article class="page-card"><span class="card-code">%s</span><h3>%s</h3><p>%s</p><a class="text-link" href="%s">Open tool <span class="cta-arrow" aria-hidden="true"></span></a></article>'
                                  % (e(c), e(t), e(d), h) for c, t, d, h in items)
    main = ('<main>' + hero('Free Tools', 'Free tools for', 'e-commerce and marketing.', 'Practical calculators and generators you can use right now. No sign-up, no cost, and nothing leaves your browser.')
            + '<section class="section-pad"><div class="section-kicker">01 / MARKETING TOOLS</div><div class="section-heading"><h2>Plan, track and <span>measure campaigns.</span></h2></div><div class="page-grid">%s</div></section>' % cards(TOOLS_MKT)
            + '<section class="section-pad"><div class="section-kicker">02 / E-COMMERCE TOOLS</div><div class="section-heading"><h2>Price, profit and <span>grow smarter.</span></h2></div><div class="page-grid">%s</div></section>' % cards(TOOLS_ECOM)
            + '<section class="section-pad"><div class="section-kicker">03 / SEARCH & AI TOOLS</div><div class="section-heading"><h2>Be found by search <span>and by AI.</span></h2></div><div class="page-grid g4">%s</div></section>' % cards(TOOLS_SEARCH)
            + '<section class="section-pad"><div class="section-kicker">04 / TAKE A BREAK</div><div class="section-heading"><h2>A one-minute <span>arcade break.</span></h2></div><div class="page-grid">%s</div></section>' % cards(TOOLS_PLAY)
            + '<section class="section-pad"><div class="cta-strip"><div><h2>Need a tool built for your own process?</h2><p>We build custom utilities and dashboards around your exact workflow.</p></div>'
              '<a class="btn primary" href="support.html">See custom utilities <span class="cta-arrow" aria-hidden="true"></span></a></div></section></main>')
    url = SITE + '/tools.html'
    desc = 'Free calculators and generators for e-commerce and digital marketing: UTM builder, ad ROAS calculator, profit calculator, SEO preview and more. No sign-up needed.'
    ld = {"@context": "https://schema.org", "@type": "CollectionPage", "name": "Free E-commerce & Marketing Tools", "url": url, "description": desc, "publisher": {"@id": SITE + "/#organization"}}
    out = page_from_template('Free E-commerce & Marketing Tools | DEEPDELL', desc, url, main, [ld, breadcrumb('Free Tools')])
    open(os.path.join(ROOT, 'tools.html'), 'w', encoding='utf-8').write(out)


if __name__ == '__main__':
    hub(); utm(); ad(); profit(); seo(); discount(); aifiles(); schema(); qr(); arcade()
    print('tool pages written: hub + 8 tools + arcade')
