# Knowbase

A growing shelf of technical field manuals — static, hand-written HTML books, each built the same way: understand the parts, then understand how they talk to each other.

**Live site:** [knowbase.xyz](https://knowbase.xyz)

## Books on the shelf

| Book | Status | Path |
|---|---|---|
| Anatomy of a Motorcycle | 150 of 150 · Complete | [`books/anatomy-of-a-motorcycle/`](books/anatomy-of-a-motorcycle/) |
| The Language of Editing | Written · locked, shown as Coming soon | [`books/davinci-resolve-editing/`](books/davinci-resolve-editing/) |

## Structure

```
index.html              Library landing page (the shelf)
styles.css               Shared stylesheet for every page in the site
reader-aids.js            Bookmarks, continue-reading, reading bar, outline, text controls, share row (localStorage only)
favicon.svg               Site favicon
assets/                   1200x630 social-share images (og-site/og-motorcycle/og-editing.png)
books/
  <book-slug>/
    index.html            Book landing page + full table of contents
    chapter-N-M.html       Individual chapters (Part N, Section M)
    diagrams/              SVG/WebP figures referenced by chapters
    cover.webp | cover.svg Book cover art
```

Every page is static HTML with a shared stylesheet — no build step, no framework, no dependencies.

## Diagrams

Diagrams are generated from Python so they share one design system (theme-aware colours, legible type,
draw-in animation hooks). Rebuild with:

```bash
python tools/flagship_motorcycle.py
python tools/flagship_batch2.py
```

`tools/dg.py` is the kit; every figure is a function that returns a `Fig`. On the site, `reader-aids.js` inlines
any SVG whose root is `class="dg"` so it picks up the site's fonts, dark mode and scroll-triggered animation.

## Locked books

`_redirects` serves `/books/davinci-resolve-editing/*` and `/books/sony-a6700-manual/*` as `coming-soon.html`
on Netlify. To release a book, delete its lines from `_redirects`, restore its card on the landing page and add its
pages back to `sitemap.xml`.

## Author photo

Save a square-ish portrait (600px+) as `assets/author.jpg`. It appears automatically on the landing page and in both books.

## Running locally

Any static file server works, since the site uses root-relative paths (`/styles.css`, `/reader-aids.js`) that require a real origin — opening files directly via `file://` will not resolve them correctly.

```bash
python -m http.server 8000
```

Then open `http://localhost:8000`.

## Deployment

The site deploys from this repository via Netlify, publishing from the repo root with no build command.

## Author

Written and curated by Jitendra Kulkarni.
