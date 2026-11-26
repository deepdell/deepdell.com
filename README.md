# DEEPDELL

DEEPDELL multi-page brand website built as a lightweight static site for GitHub Pages, with commerce, AI, data, agentic-readiness and interactive utility pages.

## Deployment

Enable **Settings → Pages → Deploy from a branch → main → /(root)** in the repository settings.

The site entry point is `index.html`.
## Styles

All pages load a single stylesheet, `site.css`. It was merged from the former layer files
(`styles`, `responsive`, `brand`, `ux`, `tech`, `premium`, `site-fixes`). Layers that only some
pages used are scoped with zero-specificity selectors such as `:where(html.css-premium)`, and
each page opts in through the classes on its `<html>` element (`css-responsive`, `css-ux`,
`css-tech`, `css-premium`). Bump the `?v=` query on the `site.css` link when you change it.

## Languages

The site is published in English (root) plus French, German, Spanish, Italian, Arabic, Malay and
Indonesian under `/fr/`, `/de/`, `/es/`, `/it/`, `/ar/`, `/ms/` and `/id/`.

- English pages at the repository root are the source of truth.
- `i18n/<lang>.json` maps each English string to its translation. Missing entries fall back to English.
- The language folders are **generated** — never edit them by hand.

After changing English text, regenerate everything:

```bash
python3 tools/i18n_extract.py   # refresh i18n/en.json (lists every translatable string)
python3 tools/i18n_build.py     # rebuild language folders, hreflang tags, switcher and sitemaps
```

The build reports how many strings each language is missing. Text created by scripts (cookie banner,
audit report, game, calculator) is translated in the browser from `i18n/<lang>.js`. Arabic pages are
right-to-left (`dir="rtl"`) and use IBM Plex Sans Arabic.
