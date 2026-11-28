---
name: blog
description: Manage the DEEPDELL blog. Use when the user asks to write, plan, update, audit or publish a blog post, or asks for a content plan or SEO check of the blog.
---
# DEEPDELL blog management

The blog is English-only static HTML generated from markdown by `tools/gen_blog.py`. Posts live in `blog/posts/<slug>.md`. Never edit `blog/*.html`, `blog/rss.xml` or `blog/posts.json` by hand.

## Requests you can handle
- **Plan:** propose 10 topics with main keyword, search intent, target page to link to, and priority. Group them in clusters around the services (Shopify Plus, AI agents, automation, data/BI, integrations) and the free tools.
- **Write:** one post per request. Follow the checklist below.
- **Update:** change the body, set `updated:` to today, rebuild.
- **Audit:** run `python3 tools/gen_blog.py` and report the advice lines; fix them when asked.
- **Publish:** build, commit on a branch, deploy to `main` only when the user says to.

## Writing rules
- Skills and general expertise only. Never name specific client projects, and never invent statistics, quotes, case studies, awards or customer results.
- Plain English, short sentences, no filler. Claims must be generic and true. If a figure is needed, say it is an example or leave it out.
- Title 30-60 characters with the main keyword near the start. Description 110-160 characters. Body has no H1.
- At least 900 words for a comprehensive guide, 4+ H2 sections, one table or list where useful, a short checklist at the end.
- Main keyword in the title, the first paragraph and one H2. Add secondary keywords naturally.
- 3+ internal links using root paths such as `/utm-builder.html`, `/services.html`, `/pricing.html`, `/contact.html`, and other posts as `/blog/<slug>.html`. Link the matching free tool when one exists (see `tools.html`).
- 2 or more outside links to primary sources only when they add value (they get `rel=noopener` automatically).
- Add a `faq` block of 3 questions with direct 1-2 sentence answers (feeds FAQ schema and AI answers).
- Front matter: title, description, date (today), category, tags, keywords (main keyword first), faq.

## Build and check
```
pip install markdown pyyaml        # first time only
python3 tools/gen_blog.py          # builds pages, RSS, posts.json and prints the SEO check
python3 tools/i18n_build.py        # refreshes sitemap.xml and sitemap.txt
```
Fix every BLOCKING line. Treat `advice` lines as a to-do list. Then bump the asset version only if script.js or site.css changed.

## After publishing
Add the post URL to `llms.txt` under "Primary pages" and tell the user to submit `https://deepdell.com/sitemap.xml` in Google Search Console and request indexing for the new URL.
