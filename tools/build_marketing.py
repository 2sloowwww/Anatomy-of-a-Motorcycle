"""Knowbase marketing automation.

One command turns the book into promotion assets, so nothing is made by hand:

  python tools/build_marketing.py cards    # write the card HTML (share image, Instagram, Pinterest)
  python tools/build_marketing.py render   # screenshot every card (needs Node; first run does `npm install`)
  python tools/build_marketing.py meta     # point each chapter's og:image / twitter:image at its own card
  python tools/build_marketing.py seo      # short titles, chapter structured data, real sitemap dates
  python tools/build_marketing.py posts    # captions + a posting calendar (marketing-out/calendar.csv)
  python tools/build_marketing.py queue    # publish Instagram images + social/instagram-queue.csv for the daily poster
  python tools/build_marketing.py all      # everything above, in order

Outputs
  assets/share/<book>/chapter-N-M.jpg   1200x630 link-preview image per chapter  (published with the site)
  marketing-out/instagram/*.jpg         1080x1350 post per diagram              (local only, git-ignored)
  marketing-out/pinterest/*.jpg         1000x1500 pin per diagram               (local only, git-ignored)
  marketing-out/calendar.csv            one row per post: date, channel, image, caption, tracked link

Re-running is cheap: unchanged cards are skipped. Pass --force to render everything again.
"""
import csv
import datetime
import hashlib
import html
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SITE = "https://knowbase.xyz"
OUT = ROOT / "marketing-out"
CARDS = OUT / "_cards"
SHARE = ROOT / "assets" / "share"

# Only books that are public. Locked books never get promotion assets until they are added here.
BOOKS = {
    "anatomy-of-a-motorcycle": {
        "short": "motorcycle",
        "name": "Anatomy of a Motorcycle",
        "tags": "#motorcycle #motorcycles #motorcyclelife #howitworks #learntoride #motorcycleengineering",
    },
}

SIZES = {"og": (1200, 630), "instagram": (1080, 1350), "pinterest": (1000, 1500)}


# ----------------------------------------------------------------------------- reading the book
def clean(s):
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", "", s))).strip()


def trim(text, n):
    if len(text) <= n:
        return text
    cut = text[:n].rsplit(" ", 1)[0].rstrip(",;:—-")
    return cut + "…"


def first_sentences(text, limit):
    parts = re.split(r"(?<=[.!?])\s+", text)
    out = ""
    for p in parts:
        if len(out) + len(p) + 1 > limit and out:
            break
        out = (out + " " + p).strip()
    return out if len(out) <= limit else trim(out, limit)


def best_hook(lede):
    """Lede minus leading recap sentences ('Chapter 11.2 covered...'), which make weak openers on social."""
    parts = re.split(r"(?<=[.!?])\s+", lede)
    keep = list(parts)
    while len(keep) > 1 and re.match(r"(Chapter \d+\.\d+|In the (last|previous) chapter|Last chapter)", keep[0]):
        keep.pop(0)
    return " ".join(keep)


def chapter_key(p):
    m = re.search(r"chapter-(\d+)-(\d+)", p.name)
    return (int(m.group(1)), int(m.group(2)))


def read_chapters(slug):
    chapters = []
    for p in sorted((ROOT / "books" / slug).glob("chapter-*.html"), key=chapter_key):
        t = p.read_text(encoding="utf-8")
        code = re.search(r'class="tb-numeral">([^<]+)<', t)
        h1 = re.search(r"<h1>(.*?)</h1>", t, re.S)
        if not (code and h1):
            continue
        lede = re.search(r'<p class="lede">(.*?)</p>', t, re.S)
        img = re.search(r'<img[^>]*src="(diagrams/[^"]+)"[^>]*class="diagram-img"', t) or \
              re.search(r'<img[^>]*class="diagram-img"[^>]*src="(diagrams/[^"]+)"', t)
        alt = re.search(r'<img[^>]*src="%s"[^>]*alt="([^"]*)"' % re.escape(img.group(1)), t) if img else None
        chapters.append({
            "slug": slug, "file": p, "id": p.stem, "code": clean(code.group(1)), "title": clean(h1.group(1)),
            "lede": best_hook(clean(lede.group(1))) if lede else "", "diagram": img.group(1) if img else None,
            "alt": clean(alt.group(1)) if alt else "",
            "new_style": bool(img and (ROOT / "books" / slug / img.group(1)).suffix == ".svg" and
                              'class="dg' in (ROOT / "books" / slug / img.group(1)).read_text(encoding="utf-8", errors="ignore")[:400]),
        })
    return chapters


# ----------------------------------------------------------------------------- card HTML
BASE_CSS = """
*{box-sizing:border-box;margin:0;padding:0}
:root{--paper:#EEE8DA;--deep:#E2D9C3;--ink:#22252B;--soft:#5A5748;--faint:#8C876F;--sig:#AE3527;--blu:#33505E}
html,body{width:%(w)dpx;height:%(h)dpx;overflow:hidden}
body{background:var(--paper);color:var(--ink);font-family:'Source Serif 4',Georgia,serif;position:relative;
  background-image:linear-gradient(rgba(51,80,94,.07) 1px,transparent 1px),linear-gradient(90deg,rgba(51,80,94,.07) 1px,transparent 1px);background-size:40px 40px}
.frame{position:absolute;inset:%(m)dpx;border:2px solid var(--ink)}
.corner{position:absolute;width:26px;height:26px;border:4px solid var(--sig)}
.tl{top:-4px;left:-4px;border-right:0;border-bottom:0}.tr{top:-4px;right:-4px;border-left:0;border-bottom:0}
.bl{bottom:-4px;left:-4px;border-right:0;border-top:0}.br{bottom:-4px;right:-4px;border-left:0;border-top:0}
.kicker{font:600 %(k)dpx 'JetBrains Mono',Consolas,monospace;letter-spacing:.14em;text-transform:uppercase;color:var(--sig)}
h1{font:900 %(t)dpx/.96 'Big Shoulders Display','Arial Narrow',sans-serif;text-transform:uppercase;letter-spacing:.005em;color:var(--ink)}
.lede{font:400 %(l)dpx/1.4 'Source Serif 4',Georgia,serif;color:var(--soft)}
.fig{background:var(--deep);border:2px solid var(--ink);display:flex;align-items:center;justify-content:center;overflow:hidden}
.fig img{width:100%%;height:100%%;object-fit:contain;display:block}
.grid-fill{background:repeating-linear-gradient(45deg,rgba(51,80,94,.10) 0 2px,transparent 2px 14px)}
.foot{position:absolute;left:%(m)dpx;right:%(m)dpx;bottom:%(m)dpx;display:flex;justify-content:space-between;align-items:center;
  font:600 %(f)dpx 'JetBrains Mono',Consolas,monospace;letter-spacing:.1em;text-transform:uppercase;color:var(--soft);
  border-top:2px solid var(--ink);padding:%(fp)dpx %(fx)dpx;background:var(--paper)}
.stack{position:absolute;left:%(sx)dpx;right:%(sx)dpx;top:%(sy)dpx;bottom:%(sb)dpx;display:flex;flex-direction:column;justify-content:space-between}
.cta{display:inline-flex;align-items:center;gap:14px;align-self:flex-start;background:var(--ink);color:var(--paper);
  font:700 %(c)dpx 'JetBrains Mono',Consolas,monospace;letter-spacing:.1em;text-transform:uppercase;padding:%(cp)dpx %(cx)dpx}
.cta i{color:#F2B8AE;font-style:normal}
.foot b{color:var(--ink);font-family:'Big Shoulders Display','Arial Narrow',sans-serif;font-weight:900;font-size:%(fb)dpx;letter-spacing:.06em}
.foot b i{color:var(--sig);font-style:normal}
"""

FONTS = ('<link rel="preconnect" href="https://fonts.googleapis.com">'
         '<link href="https://fonts.googleapis.com/css2?family=Big+Shoulders+Display:wght@800;900&family=JetBrains+Mono:wght@500;600;700'
         '&family=Source+Serif+4:opsz,wght@8..60,400;8..60,600&display=swap" rel="stylesheet">')


def fig_src(ch, base_dir):
    p = (ROOT / "books" / ch["slug"] / ch["diagram"]).resolve()
    return Path(__import__("os").path.relpath(p, base_dir.resolve())).as_posix()


def card_html(kind, ch, book):
    w, h = SIZES[kind]
    base_dir = CARDS / kind
    foot_brand = '<b>KNOW<i>BASE</i></b>'
    where = "knowbase.xyz"
    if kind == "og":
        css = BASE_CSS % dict(w=w, h=h, m=22, k=17, t=76, l=24, f=15, fp=14, fx=30, fb=24, sx=0, sy=0, sb=0, c=0, cp=0, cx=0)
        fig = ('<div class="fig" style="position:absolute;right:44px;top:44px;width:560px;height:%dpx"><img src="%s" alt=""></div>' % (h - 44 - 100 - 30, fig_src(ch, base_dir))
               if ch["diagram"] else '<div class="fig grid-fill" style="position:absolute;right:44px;top:44px;width:560px;height:%dpx"></div>' % (h - 44 - 100 - 30))
        body = ('<div style="position:absolute;left:56px;top:56px;width:520px">'
                '<div class="kicker">Chapter %s · %s</div>'
                '<h1 style="margin-top:20px;font-size:%dpx">%s</h1>'
                '<p class="lede" style="margin-top:24px">%s</p></div>'
                % (html.escape(ch["code"]), html.escape(book["name"]), 76 if len(ch["title"]) < 26 else 58,
                   html.escape(ch["title"]), html.escape(first_sentences(ch["lede"], 150))))
        foot = '<div class="foot">%s<span>Free to read · %s</span></div>' % (foot_brand, where)
        inner = body + fig + foot
    elif kind == "instagram":
        css = BASE_CSS % dict(w=w, h=h, m=28, k=22, t=104, l=34, f=20, fp=20, fx=36, fb=34, sx=70, sy=64, sb=140, c=24, cp=18, cx=28)
        inner = ('<div class="stack"><div>'
                 '<div class="kicker">Chapter %s · %s</div>'
                 '<h1 style="margin-top:22px;font-size:%dpx">%s</h1></div>'
                 '<div class="fig" style="aspect-ratio:900/560;width:100%%"><img src="%s" alt=""></div>'
                 '<p class="lede">%s</p>'
                 '<div class="cta">Read the full chapter, free <i>&rarr;</i></div></div>'
                 '<div class="foot">%s<span>%s</span></div>'
                 % (html.escape(ch["code"]), html.escape(book["name"]), 112 if len(ch["title"]) < 20 else 86, html.escape(ch["title"]),
                    fig_src(ch, base_dir), html.escape(first_sentences(ch["lede"], 190)), foot_brand, where))
    else:  # pinterest
        css = BASE_CSS % dict(w=w, h=h, m=26, k=21, t=112, l=36, f=19, fp=20, fx=34, fb=32, sx=64, sy=62, sb=130, c=24, cp=18, cx=28)
        inner = ('<div class="stack"><div>'
                 '<div class="kicker">%s</div>'
                 '<h1 style="margin-top:24px;font-size:%dpx">%s</h1></div>'
                 '<div class="fig" style="aspect-ratio:900/560;width:100%%"><img src="%s" alt=""></div>'
                 '<p class="lede">%s</p>'
                 '<div class="cta">Read it free on Knowbase <i>&rarr;</i></div></div>'
                 '<div class="foot">%s<span>%s</span></div>'
                 % (html.escape(book["name"]), 112 if len(ch["title"]) < 18 else 84, html.escape(ch["title"]),
                    fig_src(ch, base_dir), html.escape(first_sentences(ch["lede"], 260)), foot_brand, where))
    return ('<!DOCTYPE html><html><head><meta charset="utf-8">%s<style>%s</style></head><body>'
            '<div class="frame"><span class="corner tl"></span><span class="corner tr"></span><span class="corner bl"></span><span class="corner br"></span></div>'
            '%s</body></html>' % (FONTS, css, inner))


def write_if_changed(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists() and path.read_text(encoding="utf-8") == text:
        return False
    path.write_text(text, encoding="utf-8")
    return True


def manifest_for(chapters_by_book):
    items = []
    for slug, chapters in chapters_by_book.items():
        book = BOOKS[slug]
        for ch in chapters:
            kinds = ["og"] + (["instagram", "pinterest"] if ch["diagram"] and ch["diagram"].endswith(".svg") else [])
            for kind in kinds:
                html_path = CARDS / kind / ("%s-%s.html" % (book["short"], ch["id"]))
                if kind == "og":
                    out = SHARE / book["short"] / (ch["id"] + ".jpg")
                else:
                    out = OUT / kind / ("%s-%s.jpg" % (book["short"], ch["id"]))
                items.append({"kind": kind, "chapter": ch, "html": html_path, "out": out})
    return items


# ----------------------------------------------------------------------------- commands
def load_all():
    return {slug: read_chapters(slug) for slug in BOOKS}


def cmd_cards():
    data = load_all()
    n = 0
    for it in manifest_for(data):
        book = BOOKS[it["chapter"]["slug"]]
        n += write_if_changed(it["html"], card_html(it["kind"], it["chapter"], book))
    total = len(manifest_for(data))
    print("cards: %d written, %d unchanged" % (n, total - n))


def cmd_render(force=False):
    data = load_all()
    jobs = []
    for it in manifest_for(data):
        w, h = SIZES[it["kind"]]
        if not it["html"].exists():
            continue
        out = it["out"]
        if not force and out.exists() and out.stat().st_mtime >= it["html"].stat().st_mtime:
            continue
        jobs.append({"html": str(it["html"]), "out": str(out), "w": w, "h": h})
    if not jobs:
        print("render: everything is up to date")
        return
    tooldir = ROOT / "tools" / "render"
    if not (tooldir / "node_modules" / "puppeteer-core").exists():
        print("render: installing puppeteer-core (one time)…")
        subprocess.run(["npm", "install", "--no-audit", "--no-fund"], cwd=tooldir, check=True, shell=True)
    jobfile = OUT / "_jobs.json"
    jobfile.parent.mkdir(parents=True, exist_ok=True)
    jobfile.write_text(json.dumps(jobs), encoding="utf-8")
    subprocess.run(["node", "render.js", str(jobfile)], cwd=tooldir, check=True)


def git_dates(path):
    """(first commit date, last commit date) of a file as YYYY-MM-DD; falls back to today if untracked."""
    rel = str(path.relative_to(ROOT)).replace("\\", "/")
    out = subprocess.run(["git", "log", "--format=%aI", "--", rel], cwd=ROOT, capture_output=True, text=True).stdout.split()
    today = datetime.date.today().isoformat()
    return (out[-1][:10], out[0][:10]) if out else (today, today)


def seo_title(ch, book):
    """Short, keyword-first <title>: chapter name first, brand after, never past ~60 characters."""
    for tail in (" — " + book["name"], " | Knowbase", ""):
        t = ch["title"] + tail
        if len(t) <= 60:
            return t
    return trim(ch["title"], 60)


def cmd_seo():
    data = load_all()
    changed = 0
    for slug, chapters in data.items():
        book = BOOKS[slug]
        book_url = "%s/books/%s/index.html" % (SITE, slug)
        for ch in chapters:
            t = ch["file"].read_text(encoding="utf-8")
            first, last = git_dates(ch["file"])
            url = "%s/books/%s/%s.html" % (SITE, slug, ch["id"])
            desc = re.search(r'<meta name="description" content="([^"]*)"', t)
            img = SHARE / book["short"] / (ch["id"] + ".jpg")
            ld = {
                "@context": "https://schema.org",
                "@graph": [
                    {"@type": "Article", "headline": ch["title"], "description": html.unescape(desc.group(1)) if desc else "",
                     "url": url, "mainEntityOfPage": url, "inLanguage": "en", "isAccessibleForFree": True,
                     "datePublished": first, "dateModified": last,
                     "image": ("%s/assets/share/%s/%s.jpg" % (SITE, book["short"], ch["id"])) if img.exists() else None,
                     "author": {"@type": "Person", "name": "Jitendra Kulkarni"},
                     "publisher": {"@type": "Organization", "name": "Knowbase", "url": SITE + "/"},
                     "isPartOf": {"@type": "Book", "name": book["name"], "url": book_url}},
                    {"@type": "BreadcrumbList", "itemListElement": [
                        {"@type": "ListItem", "position": 1, "name": "Knowbase", "item": SITE + "/"},
                        {"@type": "ListItem", "position": 2, "name": book["name"], "item": book_url},
                        {"@type": "ListItem", "position": 3, "name": "%s %s" % (ch["code"], ch["title"]), "item": url}]},
                ],
            }
            ld["@graph"][0] = {k: v for k, v in ld["@graph"][0].items() if v is not None}
            block = '<script type="application/ld+json" id="kb-ld">%s</script>' % json.dumps(ld, ensure_ascii=False, separators=(",", ":"))
            new = re.sub(r"<title>.*?</title>", lambda m: "<title>%s</title>" % html.escape(seo_title(ch, book), quote=False), t, count=1, flags=re.S)
            if 'id="kb-ld"' in new:
                new = re.sub(r'<script type="application/ld\+json" id="kb-ld">.*?</script>', lambda m: block, new, count=1, flags=re.S)
            else:
                new = new.replace('<link rel="preconnect"', block + chr(10) + '<link rel="preconnect"', 1)
            if new != t:
                ch["file"].write_text(new, encoding="utf-8")
                changed += 1
    # sitemap: real last-modified dates (search engines ignore a sitemap where every page says "today")
    sm = ROOT / "sitemap.xml"
    text = sm.read_text(encoding="utf-8")

    def fix(m):
        loc = m.group(1)
        rel = loc.replace(SITE + "/", "") or "index.html"
        path = ROOT / (rel if rel else "index.html")
        if not path.exists():
            return m.group(0)
        return "<loc>%s</loc><lastmod>%s</lastmod>" % (loc, git_dates(path)[1])
    text2 = re.sub(r"<loc>([^<]*)</loc><lastmod>[^<]*</lastmod>", fix, text)
    if text2 != text:
        sm.write_text(text2, encoding="utf-8")
    print("seo: %d chapter pages updated (titles + structured data); sitemap lastmod refreshed" % changed)


def cmd_meta():
    data = load_all()
    changed = 0
    for slug, chapters in data.items():
        book = BOOKS[slug]
        for ch in chapters:
            img = SHARE / book["short"] / (ch["id"] + ".jpg")
            if not img.exists():
                continue
            url = "%s/assets/share/%s/%s.jpg" % (SITE, book["short"], ch["id"])
            t = ch["file"].read_text(encoding="utf-8")
            new = re.sub(r'(<meta property="og:image" content=")[^"]*(")', lambda m: m.group(1) + url + m.group(2), t)
            new = re.sub(r'(<meta name="twitter:image" content=")[^"]*(")', lambda m: m.group(1) + url + m.group(2), new)
            if "og:image:alt" not in new:
                alt = html.escape("%s — %s, a free chapter of %s" % (ch["code"], ch["title"], book["name"]), quote=True)
                new = new.replace('<meta property="og:image:height" content="630">',
                                  '<meta property="og:image:height" content="630">\n<meta property="og:image:alt" content="%s">' % alt, 1)
            if new != t:
                ch["file"].write_text(new, encoding="utf-8")
                changed += 1
    print("meta: %d chapter pages updated" % changed)


def hook_line(ch):
    return first_sentences(ch["lede"], 200) or ch["title"]


def caption(ch, book, channel):
    url = "%s/books/%s/%s.html?utm_source=%s&utm_medium=social&utm_campaign=diagram" % (SITE, ch["slug"], ch["id"], channel)
    if channel == "instagram":
        text = "%s\n\n%s\n\nThe full chapter is free — link in bio (knowbase.xyz).\n\n%s" % (ch["title"].upper(), hook_line(ch), book["tags"])
    else:
        text = "%s — %s" % (ch["title"], hook_line(ch))
    return text, url


def ordered_pool(data):
    """Drawn diagrams only. Flagship (redrawn) ones first, then a stable shuffle so topics alternate."""
    pool = [(slug, ch) for slug, chs in data.items() for ch in chs if ch["diagram"] and ch["diagram"].endswith(".svg")]
    pool.sort(key=lambda sc: (not sc[1]["new_style"], hashlib.md5(sc[1]["id"].encode()).hexdigest() if not sc[1]["new_style"] else sc[1]["id"]))
    return pool


def cmd_queue():
    """Publish the Instagram images and write the queue the daily poster works through (social/)."""
    import shutil
    data = load_all()
    dest = ROOT / "assets" / "social" / "instagram"
    dest.mkdir(parents=True, exist_ok=True)
    qdir = ROOT / "social"
    qdir.mkdir(exist_ok=True)
    rows = []
    for slug, ch in ordered_pool(data):
        book = BOOKS[slug]
        name = "%s-%s.jpg" % (book["short"], ch["id"])
        src = OUT / "instagram" / name
        if not src.exists():
            continue
        if not (dest / name).exists() or (dest / name).stat().st_mtime < src.stat().st_mtime:
            shutil.copy2(src, dest / name)
        text, _ = caption(ch, book, "instagram")
        rows.append({"id": ch["id"], "chapter": "%s %s" % (ch["code"], ch["title"]),
                     "image_url": "%s/assets/social/instagram/%s" % (SITE, name), "caption": text})
    with (qdir / "instagram-queue.csv").open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=["id", "chapter", "image_url", "caption"])
        w.writeheader()
        w.writerows(rows)
    posted = qdir / "posted.json"
    if not posted.exists():
        posted.write_text("[]" + chr(10), encoding="utf-8")
    print("queue: %d Instagram posts -> social/instagram-queue.csv (images in assets/social/instagram/)" % len(rows))


def cmd_posts(start=None, per_day=1):
    data = load_all()
    start = start or (datetime.date.today() + datetime.timedelta(days=1))
    rows = []
    pool = ordered_pool(data)
    day = start
    for i, (slug, ch) in enumerate(pool):
        book = BOOKS[slug]
        for channel in ("instagram", "pinterest"):
            img = OUT / channel / ("%s-%s.jpg" % (book["short"], ch["id"]))
            text, url = caption(ch, book, channel)
            rows.append({"date": day.isoformat(), "channel": channel, "chapter": "%s %s" % (ch["code"], ch["title"]),
                         "image": str(img.relative_to(ROOT)).replace("\\", "/"), "caption": text, "link": url,
                         "image_ready": "yes" if img.exists() else "no"})
        if (i + 1) % per_day == 0:
            day += datetime.timedelta(days=1)
    OUT.mkdir(parents=True, exist_ok=True)
    path = OUT / "calendar.csv"
    with path.open("w", newline="", encoding="utf-8-sig") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    print("posts: %d rows over %d days -> %s" % (len(rows), (day - start).days, path.relative_to(ROOT)))
    print("       captions are drafts: read a few and adjust to your voice before posting")


def main(argv):
    force = "--force" in argv
    args = [a for a in argv if not a.startswith("--")]
    cmd = args[0] if args else "all"
    if cmd in ("cards", "all"):
        cmd_cards()
    if cmd in ("render", "all"):
        cmd_render(force)
    if cmd in ("meta", "all"):
        cmd_meta()
    if cmd in ("seo", "all"):
        cmd_seo()
    if cmd in ("posts", "all"):
        cmd_posts()
    if cmd in ("queue", "all"):
        cmd_queue()
    if cmd not in ("cards", "render", "meta", "seo", "posts", "queue", "all"):
        print(__doc__)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
