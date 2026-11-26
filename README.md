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
