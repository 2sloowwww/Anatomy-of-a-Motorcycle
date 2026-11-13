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

## Marketing automation

`tools/build_marketing.py` turns the book into promotion assets so none of it is made by hand:

```bash
python tools/build_marketing.py all      # cards -> render -> meta -> posts
python tools/build_marketing.py posts    # only rebuild the captions + calendar
```

- A 1200x630 link-preview image per chapter goes to `assets/share/<book>/` (published) and each chapter's
  `og:image` / `twitter:image` is pointed at it.
- An Instagram post (1080x1350) and Pinterest pin (1000x1500) per diagram go to `marketing-out/` (git-ignored).
- `marketing-out/calendar.csv` lists one post per day with caption, tracked link (UTM) and image path.
- Rendering uses the Edge/Chrome already installed (set `BROWSER_PATH` to override) and installs `puppeteer-core`
  into `tools/render/` on first run. Unchanged cards are skipped; add `--force` to redo everything.
- Only books listed in `BOOKS` inside the script get assets, so locked books stay out until you add them.

### Instagram posting (automatic, one diagram a day)

`.github/workflows/instagram.yml` runs `tools/post_instagram.py` daily. It posts the next unposted item from
`social/instagram-queue.csv`, records it in `social/posted.json` (so nothing posts twice), and checks the image is
live on the site first. Refresh the queue and its public images with `python tools/build_marketing.py queue`.

One-time setup (needs your own accounts, so it can't be done for you):
1. Switch the Instagram account to **Professional** (Creator or Business) and link it to a Facebook Page.
2. At developers.facebook.com create an app, add **Instagram Graph API**, and generate a long-lived or
   system-user access token with `instagram_content_publish`. Note the Instagram account's numeric id.
3. In the GitHub repo: Settings → Secrets and variables → Actions → add `IG_ACCESS_TOKEN` and `IG_USER_ID`.
4. Deploy (so the images under `assets/social/instagram/` are live), then run the workflow once from the Actions tab
   with **Dry run** ticked, then once without.

Pause any time by adding an empty file `social/PAUSED`. Captions say "link in bio", so keep knowbase.xyz in the bio.
User tokens expire (about 60 days) unless they are system-user tokens — if posts start failing, replace the secret.

Email signups are collected by Netlify Forms (`knowbase-signup`); analytics switch on by setting `PLAUSIBLE_DOMAIN`
in `reader-aids.js`.

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
