# Blog guide

The blog lives at https://deepdell.com/blog/ and is generated from markdown files.

## Ask for a post
Tell Claude in this repository, for example:
- "Plan 10 blog topics for Shopify Plus merchants"
- "Write a post about abandoned cart automation"
- "Audit the blog for SEO"
- "Update the UTM post and republish"

Claude follows `.claude/skills/blog/SKILL.md`: writes `blog/posts/<slug>.md`, builds, runs the SEO check, and deploys to `main` when you say "Deploy".

## What every post gets automatically
Canonical URL, title and description tags, Open Graph and Twitter tags, BlogPosting + Breadcrumb + FAQ structured data, a table of contents, reading time, related posts, internal call to action, RSS feed (`/blog/rss.xml`), sitemap entry, and a quality check (title and description length, word count, headings, internal links, keyword placement, FAQ).

## Write one yourself
Create `blog/posts/my-topic.md`:

```
---
title: "Your title (30-60 characters)"
description: "110-160 characters that make people click."
date: 2026-12-01
category: Analytics
tags: [tag one, tag two]
keywords: [main keyword, second keyword]
faq:
  - q: "Question?"
    a: "Short answer."
---
Opening paragraph with the main keyword.

## First section
...
```

Then run `python3 tools/gen_blog.py` and `python3 tools/i18n_build.py`. Set `draft: true` to keep a post unpublished.

## After publishing
Submit `https://deepdell.com/sitemap.xml` in Google Search Console and request indexing for new URLs.
