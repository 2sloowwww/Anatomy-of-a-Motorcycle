# Knowbase

A growing shelf of technical field manuals — static, hand-written HTML books, each built the same way: understand the parts, then understand how they talk to each other.

**Live site:** [knowbase.xyz](https://knowbase.xyz)

## Books on the shelf

| Book | Status | Path |
|---|---|---|
| Anatomy of a Motorcycle | 150 of 150 · Complete | [`books/anatomy-of-a-motorcycle/`](books/anatomy-of-a-motorcycle/) |
| The Language of Editing | 34 of 95 · In Progress | [`books/davinci-resolve-editing/`](books/davinci-resolve-editing/) |

## Structure

```
index.html              Library landing page (the shelf)
styles.css               Shared stylesheet for every page in the site
reader-aids.js            Bookmarks, "continue reading," and visited-chapter tracking (localStorage only)
favicon.svg               Site favicon
books/
  <book-slug>/
    index.html            Book landing page + full table of contents
    chapter-N-M.html       Individual chapters (Part N, Section M)
    diagrams/              SVG/WebP figures referenced by chapters
    cover.webp | cover.svg Book cover art
```

Every page is static HTML with a shared stylesheet — no build step, no framework, no dependencies.

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
