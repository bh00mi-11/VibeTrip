"""
Builds dataset/images/<Destination>/photo_01.jpg ... from Wikimedia Commons.

Run from the folder that contains destinations.csv:
    pip install requests pillow
    python download_images.py

Outputs:
    images/<Destination>/photo_XX.jpg   (5-8 photos per destination)
    photos_manifest.csv                 (title, author, licence, source URL per photo)

All photos come from Wikimedia Commons, so each one has its own licence.
Keep photos_manifest.csv with the dataset and credit authors where required.
"""
import csv
import io
import time
from pathlib import Path

import requests
from PIL import Image

API = "https://commons.wikimedia.org/w/api.php"
HEADERS = {"User-Agent": "TravelPartnerDataset/1.0 (student project; contact: bhaktishinde1710@gmail.com)"}
OUT = Path("images")
MIN_PHOTOS, MAX_PHOTOS, PER_QUERY = 5, 8, 2
MIN_WIDTH = 1000
BAD_WORDS = ("map", "logo", "flag", "coat of arms", "diagram", "plan of", "stamp", "poster", "locator", "svg")


def search(query, limit=25):
    params = {
        "action": "query", "format": "json", "generator": "search",
        "gsrsearch": f"{query} filetype:bitmap", "gsrnamespace": 6, "gsrlimit": limit,
        "prop": "imageinfo", "iiprop": "url|size|mime|extmetadata", "iiurlwidth": 1280,
    }
    r = requests.get(API, params=params, headers=HEADERS, timeout=30)
    r.raise_for_status()
    pages = r.json().get("query", {}).get("pages", {})
    return sorted(pages.values(), key=lambda p: p.get("index", 0))


def usable(page):
    info = (page.get("imageinfo") or [{}])[0]
    title = page.get("title", "").lower()
    if info.get("mime") != "image/jpeg":
        return False
    if info.get("width", 0) < MIN_WIDTH or info.get("height", 0) < 600:
        return False
    return not any(w in title for w in BAD_WORDS)


def meta(info, key):
    return (info.get("extmetadata", {}).get(key, {}) or {}).get("value", "")


def download(url, path):
    r = requests.get(url, headers=HEADERS, timeout=60)
    r.raise_for_status()
    img = Image.open(io.BytesIO(r.content)).convert("RGB")
    img.save(path, "JPEG", quality=88)


def collect(dest, attractions):
    """Pick up to MAX_PHOTOS distinct photos, a couple per attraction."""
    chosen, seen = [], set()
    queries = [(a, f"{a} {dest}" if dest.lower() not in a.lower() else a) for a in attractions]
    queries.append(("general", f"{dest} India"))  # fallback to reach the minimum
    for tag, q in queries:
        if len(chosen) >= MAX_PHOTOS:
            break
        if tag == "general" and len(chosen) >= MIN_PHOTOS:
            break
        taken = 0
        for page in search(q):
            if page["title"] in seen or not usable(page):
                continue
            seen.add(page["title"])
            chosen.append((tag, page))
            taken += 1
            if taken >= PER_QUERY or len(chosen) >= MAX_PHOTOS:
                break
        time.sleep(1)
    return chosen


def main():
    rows = list(csv.DictReader(open("destinations.csv", encoding="utf-8")))
    manifest = []
    for row in rows:
        dest = row["destination"]
        folder = OUT / dest
        folder.mkdir(parents=True, exist_ok=True)
        picks = collect(dest, row["top_attractions"].split("|"))
        saved = 0
        for tag, page in picks:
            info = page["imageinfo"][0]
            saved += 1
            fname = f"photo_{saved:02d}.jpg"
            try:
                download(info.get("thumburl") or info["url"], folder / fname)
            except Exception as e:  # skip a bad file, keep going
                saved -= 1
                print(f"  skipped {page['title']}: {e}")
                continue
            manifest.append({
                "destination": dest, "file": f"images/{dest}/{fname}", "attraction": tag,
                "commons_title": page["title"], "author": meta(info, "Artist"),
                "license": meta(info, "LicenseShortName"), "source_url": info.get("descriptionurl", ""),
            })
            time.sleep(0.5)
        flag = "" if saved >= MIN_PHOTOS else "   <-- BELOW MINIMUM, add photos manually"
        print(f"{dest}: {saved} photos{flag}")
    with open("photos_manifest.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(manifest[0].keys()))
        w.writeheader()
        w.writerows(manifest)
    print(f"\nDone. {len(manifest)} photos across {len(rows)} destinations.")


if __name__ == "__main__":
    main()
