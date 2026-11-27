#!/usr/bin/env python3
"""Generate pricing.html and support.html (English sources) from tools/pricing.json.

  python3 tools/gen_pages.py       # rewrite pricing.html and support.html
  python3 tools/i18n_extract.py    # refresh i18n/en.json
  python3 tools/i18n_build.py      # rebuild the translated pages

Prices live only in tools/pricing.json; the page and its structured data are both generated from it.
Language folders are generated, so translate new strings in i18n/<lang>.json, never in /fr/ etc.
"""
import re, json, os, html

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = 'https://deepdell.com'
P = json.load(open(os.path.join(ROOT, 'tools', 'pricing.json'), encoding='utf-8'))
CUR = P['currencies']
SYM = CUR['USD']['symbol']


def nice(x):
    """Round a converted amount to a friendly price point (e.g. 283 -> 279, 806850 -> 799,000)."""
    def r(v, step): return int(v / step + 0.5) * step
    if x < 50: return max(5, r(x, 5))
    if x < 1000: return r(x, 10) - 1
    if x < 10000: return r(x, 100) - 1
    if x < 100000: return r(x, 500) - 1
    return r(x, 50000) - 1000


def fmt(amount, c):
    sep = c.get('thousands', ',')
    return c['symbol'] + f"{amount:,}".replace(',', sep)


def local_prices(usd):
    out = {}
    for code, c in CUR.items():
        out[code] = fmt(usd if code == 'USD' else nice(usd * c['rate'] * c['ppp']), c)
    return out


def price_attr(usd):
    return html.escape(json.dumps(local_prices(usd), ensure_ascii=False, separators=(',', ':')), quote=True)
e = lambda s: html.escape(s, quote=False)


def page_from_template(title, desc, url, main, schema):
    s = open(os.path.join(ROOT, 'data.html'), encoding='utf-8').read()
    s = re.sub(r'<title>.*?</title>', lambda m: '<title>' + e(title) + '</title>', s, flags=re.S)
    for tag, val in (('name="description"', desc), ('property="og:title"', title), ('property="og:description"', desc),
                     ('name="twitter:title"', title), ('name="twitter:description"', desc)):
        s = re.sub(r'(<meta %s content=")[^"]*"' % tag, lambda m: m.group(1) + html.escape(val) + '"', s)
    s = re.sub(r'(<meta property="og:url" content=")[^"]*"', lambda m: m.group(1) + url + '"', s)
    s = re.sub(r'<link rel="canonical" href="[^"]*">', '<link rel="canonical" href="%s">' % url, s)
    blocks = iter(schema)
    s = re.sub(r'(<script type="application/ld\+json"[^>]*>)(.*?)(</script>)',
               lambda m: m.group(1) + json.dumps(next(blocks), ensure_ascii=False, separators=(',', ':')) + m.group(3), s, flags=re.S)
    return re.sub(r'<main>.*?</main>', lambda m: main, s, flags=re.S)


def breadcrumb(name):
    return {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": 1, "name": "DEEPDELL", "item": SITE + "/"},
        {"@type": "ListItem", "position": 2, "name": name}]}


# ───────────────────────── pricing ─────────────────────────
def pricing():
    cards = []
    for p in P['plans']:
        cls = 'plan' + (' featured' if p.get('badge') else '') + (' custom' if p['price'] is None else '')
        badge = '<span class="plan-badge">%s</span>' % e(p['badge']) if p.get('badge') else ''
        if p['price'] is None:
            price = '<div class="plan-price"><span class="amt amt-text">%s</span></div>' % e(p['price_label'])
        else:
            price = '<div class="plan-price"><span class="from">from</span><span class="amt" data-p="%s">%s%d</span><small>/ month</small></div>' % (price_attr(p['price']), SYM, p['price'])
        feats = ''.join('<li>%s</li>' % e(f) for f in p['features'])
        btn = 'btn primary' if p.get('badge') else 'btn ghost'
        cards.append('<article class="%s">%s<h3>%s</h3><p class="plan-for">%s</p>%s<ul>%s</ul><a class="%s" href="contact.html">%s <span class="cta-arrow" aria-hidden="true"></span></a></article>'
                     % (cls, badge, e(p['name']), e(p['for']), price, feats, btn, e(p['cta'])))
    svc = []
    for s in P['services']:
        unit = '<small>%s</small>' % e(s['unit']) if s.get('unit') else ''
        svc.append('<article class="page-card"><h3>%s</h3><p>%s</p><p class="price-line"><span class="from">from</span> <strong data-p="%s">%s%d</strong> %s</p></article>'
                   % (e(s['name']), e(s['text']), price_attr(s['price']), SYM, s['price'], unit))
    faq = [
        ("Can I cancel at any time?", "Yes. Plans run month to month with no contract."),
        ("What counts as a support hour?", "Fixes, consultation calls, configuration, monitoring and building automations all count."),
        ("What if I need more hours?", "Extra hours can be added at a discounted rate, or you can upgrade your plan at any time."),
        ("Which platforms do you support?", "Shopify, Amazon, eBay, Walmart, HubSpot, Google Ads, Meta, Snapchat, Google Analytics and custom APIs. Ask if yours is not listed."),
        ("Do you offer local currency billing?", "Yes. Prices are shown in your local currency, adjusted to local purchasing power, and billed in that currency. Use the selector above to change it."),
        ("Is there a free call?", "Yes. The first 20-minute discovery call is free."),
    ]
    faqs = ''.join('<article class="page-card"><h3>%s</h3><p>%s</p></article>' % (e(q), e(a)) for q, a in faq)
    main = '''<main>
<section class="page-hero section-pad">
<div><div class="breadcrumbs"><a href="/">DEEPDELL</a><span>/</span><span>Pricing</span></div><h1>Plans that grow <em>with your store.</em></h1><p>Start small, upgrade when you need to and cancel at any time. Every plan includes expert e-commerce technical support.</p></div></section>
<section class="section-pad"><div class="section-kicker">01 / MONTHLY PLANS</div><div class="section-heading"><h2>Simple pricing. <span>Real engineers.</span></h2><p>Pick the support level that fits today. Move up or down whenever your needs change.</p></div>
<div class="cur-bar"><label class="cur-pick"><span>Show prices in</span><select id="dd-cur" aria-label="Show prices in">%s</select></label><p class="cur-note">Prices are adjusted to your region's purchasing power.</p></div>
<div class="plans">%s</div>
<p class="plan-note">Save %d%% with annual billing. Prices exclude taxes.</p></section>
<section class="section-pad"><div class="section-kicker">02 / PAY AS YOU GO</div><div class="section-heading"><h2>Need something once? <span>Pay only for that.</span></h2><p>No plan required. Book a consultation or order a utility on its own.</p></div><div class="page-grid">%s</div></section>
<section class="section-pad"><div class="section-kicker">03 / QUESTIONS</div><div class="section-heading"><h2>Questions, <span>answered.</span></h2></div><div class="page-grid">%s</div>
<div class="cta-strip"><div><h2>Not sure which plan fits?</h2><p>Book a free discovery call and we will recommend the right option for your store.</p></div><a class="btn primary" href="contact.html">Book a free call <span class="cta-arrow" aria-hidden="true"></span></a></div></section></main>''' % (
        ''.join('<option value="%s"%s>%s</option>' % (k, ' selected' if k == 'USD' else '', e(c['label'])) for k, c in CUR.items()),
        ''.join(cards), P['annual_discount_percent'], ''.join(svc), faqs)
    offers = [{"@type": "Offer", "name": p['name'], "price": str(p['price']), "priceCurrency": "USD",
               "priceSpecification": {"@type": "UnitPriceSpecification", "price": str(p['price']), "priceCurrency": "USD", "unitText": "MONTH"}}
              for p in P['plans'] if p['price'] is not None]
    title = 'Pricing: E-commerce Support & Automation Plans | DEEPDELL'
    desc = 'Budget-friendly monthly plans for e-commerce technical support, dashboards and automation, plus pay-as-you-go consultations and custom utilities.'
    url = SITE + '/pricing.html'
    svc_ld = {"@context": "https://schema.org", "@type": "Service", "name": "E-commerce Technical Support Plans", "url": url,
              "provider": {"@id": SITE + "/#organization"}, "description": desc,
              "hasOfferCatalog": {"@type": "OfferCatalog", "name": "Monthly support plans", "itemListElement": offers}}
    open(os.path.join(ROOT, 'pricing.html'), 'w', encoding='utf-8').write(
        page_from_template(title, desc, url, main, [svc_ld, breadcrumb('Pricing')]))


# ───────────────────────── support & operations ─────────────────────────
CATALOG = [
    ("01 / STORE", "Store setup & migration", "New stores, replatforming, product and customer data imports, domains and email."),
    ("02 / STOREFRONT", "Theme & storefront fixes", "Layout bugs, speed problems, mobile issues, cart and checkout customisation."),
    ("03 / APPS", "Apps & integrations", "Choosing, configuring and debugging apps, APIs, webhooks and connectors."),
    ("04 / OPERATIONS", "Orders, inventory & pricing", "Stock sync across channels, price updates, order routing and reconciliation."),
    ("05 / MARKETPLACES", "Marketplaces & feeds", "Listings and product feeds for Amazon, eBay, Walmart and Google Merchant Center."),
    ("06 / ADS", "Ads & tracking", "Pixels, conversion tracking and audiences for Google, Meta and Snapchat, plus analytics set-up."),
    ("07 / CRM", "CRM & email", "HubSpot and email platform set-up, lead flows and customer segments."),
    ("08 / PAYMENTS", "Payments, shipping & tax", "Gateways, carriers, rates, tax rules and new markets."),
    ("09 / REPORTING", "Reporting & dashboards", "One dashboard across platforms, scheduled reports and profit views."),
    ("10 / AUTOMATION", "AI & automation", "AI agents, scheduled flows and tools that remove daily manual work."),
    ("11 / GROWTH", "Speed, SEO & conversion", "Performance, technical SEO, structured data and conversion improvements."),
    ("12 / SECURITY", "Security & backups", "Access control, backups, monitoring and safe release processes."),
]


def support():
    card = lambda c, h, t: '<article class="page-card"><span class="card-code">%s</span><h3>%s</h3><p>%s</p></article>' % (e(c), e(h), e(t))
    ways = [("01 / CONSULT", "Ask an engineer", "Book a call to diagnose a problem, review a setup or plan a project."),
            ("02 / AUTOMATE", "Get a custom utility", "We build a focused tool or automation for the task you repeat every day."),
            ("03 / MAINTAIN", "Keep it running", "A monthly plan covers fixes, monitoring and improvements.")]
    main = '''<main>
<section class="page-hero section-pad">
<div><div class="breadcrumbs"><a href="/">DEEPDELL</a><span>/</span><span>Support &amp; Operations</span></div><h1>Every e-commerce task, <em>one technical team.</em></h1><p>From a quick fix to a full automation, consult an engineer or have a custom utility built. Here is what we cover.</p></div></section>
<section class="section-pad"><div class="section-kicker">01 / HOW TO WORK WITH US</div><div class="section-heading"><h2>Consult, automate <span>or maintain.</span></h2><p>Use us for one question, one tool or ongoing support. Whatever suits your budget.</p></div><div class="page-grid">%s</div></section>
<section class="section-pad"><div class="section-kicker">02 / WHAT WE COVER</div><div class="section-heading"><h2>Everything behind <span>your online store.</span></h2><p>If it keeps your e-commerce operation running, we can advise on it, fix it or automate it.</p></div><div class="page-grid">%s</div>
<div class="cta-strip"><div><h2>Not sure what you need?</h2><p>Book a free discovery call and we will point you to the right option.</p></div><a class="btn primary" href="pricing.html">See pricing <span class="cta-arrow" aria-hidden="true"></span></a></div></section></main>''' % (
        ''.join(card(*w) for w in ways), ''.join(card(*c) for c in CATALOG))
    title = 'E-commerce Technical Support & Operations | DEEPDELL'
    desc = 'Consultation, technical support and custom utilities for every part of e-commerce operations: stores, marketplaces, ads, CRM, payments, reporting and automation.'
    url = SITE + '/support.html'
    svc_ld = {"@context": "https://schema.org", "@type": "Service", "name": "E-commerce Technical Support & Operations", "url": url,
              "serviceType": "E-commerce consultation, technical support and custom utilities", "provider": {"@id": SITE + "/#organization"}, "description": desc}
    open(os.path.join(ROOT, 'support.html'), 'w', encoding='utf-8').write(
        page_from_template(title, desc, url, main, [svc_ld, breadcrumb('Support & Operations')]))


if __name__ == '__main__':
    pricing()
    support()
    print('pricing.html and support.html written')
