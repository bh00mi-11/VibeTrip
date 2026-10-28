import os
import csv
import time
import requests
from datetime import datetime
from sqlalchemy.orm import Session
from backend.database import SessionLocal, engine
from backend.models import Base, Destination, Photo, VibeScore, User, TravelerProfile, LocalPlace, BuddyInterest
from backend.auth import hash_password
from backend.overpass_service import query_osm_places

# Nominatim Geocoder with polite rate limiting and DB caching
def geocode_destination(name: str, state: str) -> tuple:
    url = "https://nominatim.openstreetmap.org/search"
    query = f"{name}, {state}, India"
    headers = {"User-Agent": "VibeTripResearchApp/1.0 (academic-vit-project)"}
    try:
        r = requests.get(url, params={"q": query, "format": "json", "limit": 1}, headers=headers, timeout=10)
        if r.status_code == 200 and r.json():
            data = r.json()[0]
            return float(data["lat"]), float(data["lon"])
    except Exception as e:
        print(f"Geocoding error for {name}: {e}")
    return None, None

def seed_database():
    print("=== Creating Database Tables ===")
    Base.metadata.create_all(bind=engine)
    db: Session = SessionLocal()

    # 1. Load Destinations
    dest_path = "destinations.csv"
    gt_vibe_path = "vibe_labels_final.csv"
    pred_vibe_path = "predicted_vibe_scores.csv"
    photos_path = "photos_manifest.csv"

    gt_scores = {}
    if os.path.exists(gt_vibe_path):
        with open(gt_vibe_path, "r", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                gt_scores[row["destination"]] = {
                    "nature": float(row.get("nature", 50.0)),
                    "adventure": float(row.get("adventure", 50.0)),
                    "peacefulness": float(row.get("peacefulness", 50.0)),
                    "crowd_match": float(row.get("crowd_match", 50.0)),
                    "visual_atmosphere": float(row.get("visual_atmosphere", 50.0))
                }

    pred_scores = {}
    if os.path.exists(pred_vibe_path):
        with open(pred_vibe_path, "r", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                pred_scores[row["destination"]] = {
                    "nature": float(row.get("nature", 50.0)),
                    "adventure": float(row.get("adventure", 50.0)),
                    "peacefulness": float(row.get("peacefulness", 50.0)),
                    "crowd_match": float(row.get("crowd_match", 50.0)),
                    "visual_atmosphere": float(row.get("visual_atmosphere", 50.0))
                }

    print("\n=== Seeding Destinations & Geocoding via Nominatim ===")
    geocoded_count = 0
    failed_geocode = []

    dest_rows = []
    with open(dest_path, "r", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            dest_rows.append(r)

    for r in dest_rows:
        name = r["destination"]
        existing = db.query(Destination).filter(Destination.name == name).first()
        if existing and existing.latitude and existing.longitude:
            geocoded_count += 1
            continue

        lat, lon = geocode_destination(name, r.get("state", ""))
        time.sleep(1.05) # Polite 1 req/sec rate limit for Nominatim

        if lat is not None and lon is not None:
            geocoded_count += 1
        else:
            failed_geocode.append(name)
            # Fallback coarse coordinate by region if geocoder times out
            lat, lon = 20.5937, 78.9629

        dest_obj = Destination(
            name=name,
            state=r.get("state"),
            region=r.get("region"),
            category=r.get("category"),
            best_time=r.get("best_time_to_visit"),
            description=r.get("description"),
            top_attractions=r.get("top_attractions"),
            latitude=lat,
            longitude=lon,
            status="published",
            source="dataset",
            created_at=datetime.utcnow()
        )
        db.merge(dest_obj)
        db.commit()

        # Seed Vibe Scores
        preds = pred_scores.get(name, {"nature": 50.0, "adventure": 50.0, "peacefulness": 50.0, "crowd_match": 50.0, "visual_atmosphere": 50.0})
        gts = gt_scores.get(name, {})
        vibe_obj = VibeScore(
            destination=name,
            nature=preds["nature"],
            adventure=preds["adventure"],
            peacefulness=preds["peacefulness"],
            crowd_match=preds["crowd_match"],
            visual_atmosphere=preds["visual_atmosphere"],
            gt_nature=gts.get("nature"),
            gt_adventure=gts.get("adventure"),
            gt_peacefulness=gts.get("peacefulness"),
            gt_crowd_match=gts.get("crowd_match"),
            gt_visual_atmosphere=gts.get("visual_atmosphere"),
            score_source="model_oof"
        )
        db.merge(vibe_obj)
        db.commit()

    print(f"Destinations geocoded: {geocoded_count}/50")
    if failed_geocode:
        print(f"Destinations that failed Nominatim geocoding: {failed_geocode}")
    else:
        print("All destinations successfully geocoded.")

    # 2. Seed Photos Manifest
    print("\n=== Seeding Photos Manifest ===")
    photo_count = 0
    if os.path.exists(photos_path):
        with open(photos_path, "r", encoding="utf-8") as f:
            for r in csv.DictReader(f):
                dest_name = r.get("destination")
                file_rel = r.get("file", "")
                filename = os.path.basename(file_rel)
                p_obj = Photo(
                    destination=dest_name,
                    filename=filename,
                    attraction=r.get("attraction"),
                    author=r.get("author"),
                    license=r.get("license"),
                    source_url=r.get("source_url"),
                    uploaded_by="dataset"
                )
                db.add(p_obj)
                photo_count += 1
        db.commit()
    print(f"Total photos seeded: {photo_count}")

    # 3. Seed Overpass Local Places for Destinations
    print("\n=== Fetching Real Nearby Places via Overpass API (~8km) ===")
    places_per_dest = {}
    destinations = db.query(Destination).all()
    for d in destinations:
        existing_places = db.query(LocalPlace).filter(LocalPlace.destination == d.name).count()
        if existing_places >= 5:
            places_per_dest[d.name] = existing_places
            continue

        osm_places = query_osm_places(d.latitude, d.longitude, d.name, radius_m=8000, limit=25)
        for p in osm_places:
            lp = LocalPlace(
                destination=d.name,
                name=p["name"],
                category=p["category"],
                latitude=p["latitude"],
                longitude=p["longitude"],
                description=p["description"],
                source="osm",
                osm_id=p["osm_id"],
                status="approved",
                crowd_hint=p.get("crowd_hint")
            )
            db.add(lp)
        db.commit()
        cnt = db.query(LocalPlace).filter(LocalPlace.destination == d.name).count()
        places_per_dest[d.name] = cnt

    fewer_than_5 = [k for k, v in places_per_dest.items() if v < 5]
    print(f"Local places queried. Destinations with fewer than 5 places: {fewer_than_5 if fewer_than_5 else 'None'}")
    for dest, count in list(places_per_dest.items())[:5]:
        print(f"  {dest}: {count} places")

    # 4. Seed ~15 Demo Tourist Profiles
    print("\n=== Seeding Demo Users & Traveler Profiles ===")
    demo_tourists = [
        {"name": "Aarav Sharma", "email": "aarav.demo@vibetrip.internal", "city": "Bengaluru", "dest": "Manali", "tags": "hiking, photography, snow", "bio": "Mountain lover & weekend trekker.", "vibes": (90, 85, 70, 30, 85)},
        {"name": "Tara Sen", "email": "tara.demo@vibetrip.internal", "city": "Chandigarh", "dest": "Manali", "tags": "hiking, photography, winter", "bio": "Solo trekker exploring Solang & Old Manali cafes.", "vibes": (90, 80, 75, 35, 85)},
        {"name": "Dev Kapoor", "email": "dev.demo@vibetrip.internal", "city": "Delhi", "dest": "Agra", "tags": "monuments, architecture, food", "bio": "Heritage lover capturing sunrise at Mehtab Bagh.", "vibes": (40, 20, 60, 50, 85)},
        {"name": "Ananya Sen", "email": "ananya.demo@vibetrip.internal", "city": "Kolkata", "dest": "Darjeeling", "tags": "tea gardens, slow travel, books", "bio": "Seeking quiet misty tea hills & cozy cafes.", "vibes": (85, 40, 90, 20, 80)},
        {"name": "Rohan Mehta", "email": "rohan.demo@vibetrip.internal", "city": "Mumbai", "dest": "Rishikesh", "tags": "rafting, yoga, meditation, river", "bio": "White-water rafting by day, Ganga Aarti by night.", "vibes": (80, 95, 75, 40, 80)},
        {"name": "Pooja Verma", "email": "pooja.demo@vibetrip.internal", "city": "Delhi", "dest": "Goa", "tags": "beaches, sunset, cafe hopping", "bio": "Exploring South Goa's quiet shores & heritage quarters.", "vibes": (70, 60, 75, 50, 85)},
        {"name": "Kabir Das", "email": "kabir.demo@vibetrip.internal", "city": "Hyderabad", "dest": "Hampi", "tags": "history, boulders, cycling, architecture", "bio": "Exploring ancient Vijayanagara ruins with a sketchbook.", "vibes": (60, 75, 80, 35, 90)},
        {"name": "Meera Nair", "email": "meera.demo@vibetrip.internal", "city": "Kochi", "dest": "Munnar", "tags": "waterfalls, wildlife, plantation walks", "bio": "Wildlife photographer chasing misty valleys.", "vibes": (95, 60, 85, 25, 90)},
        {"name": "Vikram Rathore", "email": "vikram.demo@vibetrip.internal", "city": "Jaipur", "dest": "Jaisalmer", "tags": "dunes, stargazing, camel safari", "bio": "Desert night camps and golden sandstone marvels.", "vibes": (70, 80, 85, 30, 95)},
        {"name": "Sneha Kulkarni", "email": "sneha.demo@vibetrip.internal", "city": "Pune", "dest": "Udaipur", "tags": "palaces, boating, rooftop dinners", "bio": "Romantic lakeside architecture and heritage trails.", "vibes": (60, 45, 80, 45, 90)},
        {"name": "Arjun Patel", "email": "arjun.demo@vibetrip.internal", "city": "Ahmedabad", "dest": "Leh", "tags": "motorcycling, passes, high altitude, monks", "bio": "Riding through Khardung La & Pangong Lake.", "vibes": (95, 95, 80, 20, 95)},
        {"name": "Divya Roy", "email": "divya.demo@vibetrip.internal", "city": "Guwahati", "dest": "Shillong", "tags": "living root bridges, waterfalls, music", "bio": "Scotland of the East explorer.", "vibes": (90, 70, 80, 40, 85)},
        {"name": "Ishaan Chawla", "email": "ishaan.demo@vibetrip.internal", "city": "Chandigarh", "dest": "Shimla", "tags": "colonial heritage, pine trails, toy train", "bio": "Cool summer breezes and scenic walks.", "vibes": (80, 50, 75, 55, 75)},
        {"name": "Kavya Reddy", "email": "kavya.demo@vibetrip.internal", "city": "Chennai", "dest": "Ooty", "tags": "botanical gardens, eucalyptus, toy train", "bio": "Nature retreat and Nilgiri tea tasting.", "vibes": (90, 45, 85, 35, 80)},
        {"name": "Tenzin Norbu", "email": "tenzin.demo@vibetrip.internal", "city": "Gangtok", "dest": "Tawang", "tags": "monasteries, passes, high altitude lake", "bio": "Spiritual retreats and snow-clad Himalayan passes.", "vibes": (95, 80, 90, 15, 90)},
        {"name": "Farhan Ali", "email": "farhan.demo@vibetrip.internal", "city": "Lucknow", "dest": "Varanasi", "tags": "ghats, spiritual, morning boat, street food", "bio": "Capturing sunrise boat rides and ancient silk weavers.", "vibes": (40, 40, 60, 80, 85)},
        {"name": "Neha Joshi", "email": "neha.demo@vibetrip.internal", "city": "Dehradun", "dest": "Auli", "tags": "skiing, cable car, Nanda Devi views", "bio": "Winter sports enthusiast looking for skiing buddies.", "vibes": (90, 90, 80, 25, 95)}
    ]

    demo_user_count = 0
    default_pwd_hash = hash_password("DemoUserPass2026!")

    for item in demo_tourists:
        existing_u = db.query(User).filter(User.email == item["email"]).first()
        if existing_u:
            demo_user_count += 1
            existing_int = db.query(BuddyInterest).filter(BuddyInterest.user_id == existing_u.id, BuddyInterest.destination == item["dest"]).first()
            if not existing_int:
                v = item["vibes"]
                interest = BuddyInterest(
                    user_id=existing_u.id,
                    destination=item["dest"],
                    travel_start="2026-11-01",
                    travel_end="2026-11-10",
                    pref_nature=v[0],
                    pref_adventure=v[1],
                    pref_peacefulness=v[2],
                    pref_crowd_match=v[3],
                    pref_visual_atmosphere=v[4],
                    interest_tags=item["tags"],
                    note=f"Heading to {item['dest']} for a photography and exploration trip! Feel free to say hi.",
                    active=True
                )
                db.add(interest)
            continue

        u = User(
            name=item["name"],
            email=item["email"],
            password_hash=default_pwd_hash,
            role="tourist",
            is_active=True,
            is_demo=True,
            created_at=datetime.utcnow()
        )
        db.add(u)
        db.flush()

        prof = TravelerProfile(
            user_id=u.id,
            home_city=item["city"],
            bio=item["bio"],
            interest_tags=item["tags"],
            visibility="destination_only",
            contact_info=f"instagram: @{item['name'].lower().replace(' ', '_')}"
        )
        db.add(prof)

        v = item["vibes"]
        interest = BuddyInterest(
            user_id=u.id,
            destination=item["dest"],
            travel_start="2026-11-01",
            travel_end="2026-11-10",
            pref_nature=v[0],
            pref_adventure=v[1],
            pref_peacefulness=v[2],
            pref_crowd_match=v[3],
            pref_visual_atmosphere=v[4],
            interest_tags=item["tags"],
            note=f"Heading to {item['dest']} for a photography and exploration trip! Feel free to say hi.",
            active=True
        )
        db.add(interest)
        demo_user_count += 1

    db.commit()
    print(f"Demo users created / confirmed: {demo_user_count} (all marked is_demo = true)")
    db.close()
    print("\n=== Seeding Finished Successfully ===")

if __name__ == "__main__":
    seed_database()
