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
    chosen, seen = [], set()
    queries = [(a, f"{a} {dest}" if dest.lower() not in a.lower() else a) for a in attractions]
    queries.append(("general", f"{dest} India"))
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
    existing = set()
    try:
        with open("photos_manifest.csv", "r", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                existing.add(row["destination"])
    except FileNotFoundError:
        pass

    manifest = []
    total_dests = len(rows)
    for row in rows:
        dest = row["destination"]
        if dest in existing:
            continue
            
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
                # Verify file opens
                Image.open(folder / fname).verify()
            except Exception as e:
                saved -= 1
                print(f"  skipped {page['title']}: {e}")
                if (folder / fname).exists():
                    (folder / fname).unlink()
                continue
            manifest.append({
                "destination": dest, "file": f"images/{dest}/{fname}", "attraction": tag,
                "commons_title": page["title"], "author": meta(info, "Artist"),
                "license": meta(info, "LicenseShortName"), "source_url": info.get("descriptionurl", ""),
            })
            time.sleep(0.5)
        flag = "" if saved >= MIN_PHOTOS else "   <-- BELOW MINIMUM, add photos manually"
        print(f"{dest}: {saved} photos{flag}")
        
    if manifest:
        with open("photos_manifest.csv", "a", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=list(manifest[0].keys()))
            if not existing:
                w.writeheader()
            w.writerows(manifest)
            
    print(f"\nDone. Downloaded {len(manifest)} new photos. Total destinations in dataset: {total_dests}.")

    # Count final stats
    try:
        final_manifest_rows = list(csv.DictReader(open("photos_manifest.csv", "r", encoding="utf-8")))
        total_images = len(final_manifest_rows)
        dests_in_manifest = set(r["destination"] for r in final_manifest_rows)
        
        counts = {d: 0 for d in dests_in_manifest}
        for r in final_manifest_rows:
            counts[r["destination"]] += 1
            
        below_min = [d for d, c in counts.items() if c < MIN_PHOTOS]
        
        print("\n--- Summary ---")
        print(f"Total destinations processed: {len(dests_in_manifest)} (out of {total_dests} in destinations.csv)")
        print(f"Total images: {total_images}")
        if below_min:
            print(f"Destinations below minimum photos ({MIN_PHOTOS}): {', '.join(below_min)}")
        else:
            print("All destinations have at least the minimum required photos.")
    except Exception as e:
        print(f"Could not compute final stats: {e}")

if __name__ == "__main__":
    main()
