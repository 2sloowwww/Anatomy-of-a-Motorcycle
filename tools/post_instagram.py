"""Post the next diagram from social/instagram-queue.csv to Instagram (Instagram Graph API).

Run by .github/workflows/instagram.yml once a day. Standard library only.

  python tools/post_instagram.py             # post the next unposted item
  python tools/post_instagram.py --dry-run   # show what would be posted, change nothing
  python tools/post_instagram.py --count 2   # post two this run

Environment (GitHub repository secrets):
  IG_USER_ID       the Instagram professional account's numeric id
  IG_ACCESS_TOKEN  a long-lived / system-user token with instagram_content_publish
Optional:
  IG_GRAPH_BASE    defaults to https://graph.facebook.com/v21.0 (tests point it at a mock)

Safety:
  * exits quietly (success) if the secrets are not set yet, so the workflow can be committed first
  * does nothing if the file social/PAUSED exists
  * confirms the image is already live on the site before asking Instagram to fetch it
  * records every success in social/posted.json straight away, so a crash can never double-post
"""
import csv
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
QUEUE = ROOT / "social" / "instagram-queue.csv"
POSTED = ROOT / "social" / "posted.json"
PAUSED = ROOT / "social" / "PAUSED"
BASE = os.environ.get("IG_GRAPH_BASE", "https://graph.facebook.com/v21.0").rstrip("/")
MAX_CAPTION = 2200
UA = "knowbase-poster/1.0"


def log(msg):
    print(msg, flush=True)


def http(method, url, data=None, timeout=60):
    body = urllib.parse.urlencode(data).encode() if data is not None else None
    req = urllib.request.Request(url, data=body, method=method, headers={"User-Agent": UA})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status, r.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode("utf-8", "replace")
    except (urllib.error.URLError, OSError, ValueError) as e:
        raise RuntimeError("Network problem talking to %s: %s" % (urllib.parse.urlparse(url).netloc, e))


def api(method, path, token, params=None):
    data = dict(params or {})
    data["access_token"] = token
    if method == "GET":
        status, text = http("GET", "%s/%s?%s" % (BASE, urllib.parse.quote(path), urllib.parse.urlencode(data)))
    else:
        status, text = http("POST", "%s/%s" % (BASE, urllib.parse.quote(path)), data)
    try:
        payload = json.loads(text)
    except ValueError:
        payload = {"raw": text[:300]}
    if status >= 400 or "error" in payload:
        err = payload.get("error", payload)
        # never echo the token back into logs
        raise RuntimeError("Instagram API error (%s): %s" % (status, json.dumps(err)[:400]))
    return payload


def load_posted():
    try:
        return json.loads(POSTED.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return []


def save_posted(items):
    POSTED.write_text(json.dumps(items, indent=2) + "\n", encoding="utf-8")


def image_is_live(url):
    status, _ = http("GET", url, timeout=30)
    return status == 200


def publish(user_id, token, item):
    caption = item["caption"][:MAX_CAPTION]
    created = api("POST", "%s/media" % user_id, token, {"image_url": item["image_url"], "caption": caption})
    creation_id = created["id"]
    for _ in range(30):  # wait for Instagram to finish fetching the image
        st = api("GET", creation_id, token, {"fields": "status_code"}).get("status_code")
        if st == "FINISHED":
            break
        if st in ("ERROR", "EXPIRED"):
            raise RuntimeError("Instagram could not process the image (status %s)" % st)
        time.sleep(2)
    else:
        raise RuntimeError("Timed out waiting for Instagram to process the image")
    return api("POST", "%s/media_publish" % user_id, token, {"creation_id": creation_id})["id"]


def main(argv):
    dry = "--dry-run" in argv
    count = int(argv[argv.index("--count") + 1]) if "--count" in argv else 1
    user_id = os.environ.get("IG_USER_ID", "").strip()
    token = os.environ.get("IG_ACCESS_TOKEN", "").strip()

    if PAUSED.exists():
        log("Paused (social/PAUSED exists) — nothing posted.")
        return 0
    if not dry and not (user_id and token):
        log("IG_USER_ID / IG_ACCESS_TOKEN are not set yet — nothing posted. See README > Instagram posting.")
        return 0
    if not QUEUE.exists():
        log("No queue found. Run: python tools/build_marketing.py queue")
        return 1

    posted = load_posted()
    done = {p["id"] for p in posted}
    with QUEUE.open(encoding="utf-8", newline="") as fh:
        todo = [r for r in csv.DictReader(fh) if r["id"] not in done]
    log("%d posted, %d left in the queue." % (len(done), len(todo)))
    if not todo:
        log("Queue is empty — generate more with tools/build_marketing.py queue.")
        return 0

    for item in todo[:count]:
        log("Next: %s" % item["chapter"])
        if dry:
            log("  image  : %s" % item["image_url"])
            log("  caption: %s" % item["caption"].splitlines()[0])
            continue
        if not image_is_live(item["image_url"]):
            log("  Image is not live on the site yet (%s). Deploy first; will retry next run." % item["image_url"])
            return 1
        media_id = publish(user_id, token, item)
        posted.append({"id": item["id"], "chapter": item["chapter"], "media_id": media_id,
                       "posted_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())})
        save_posted(posted)
        log("  Posted (media id %s)." % media_id)
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main(sys.argv[1:]))
    except RuntimeError as e:
        log("FAILED: %s" % e)
        sys.exit(1)
