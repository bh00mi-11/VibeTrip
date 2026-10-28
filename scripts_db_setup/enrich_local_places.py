import os
import sys
import time
import requests
import sqlite3
from typing import List, Dict, Any

DB_PATH = "vibetrip.db"
HEADERS = {"User-Agent": "VibeTripPlacesEnricher/2.0 (academic-vit-project; contact: manis@example.com)"}

# Pre-curated real verified spots for destinations that return sparse Nominatim results
CURATED_VERIFIED_PLACES = {
    "Auli": [
        {"name": "Auli Chair Lift & Ropeway", "category": "activity", "lat": 30.5285, "lon": 79.5694, "desc": "Famous high-altitude cable car offering panoramic views of Nanda Devi."},
        {"name": "Gurso Bugyal Viewpoint", "category": "viewpoint", "lat": 30.5401, "lon": 79.5850, "desc": "Sprawling alpine meadow with unobstructed views of Trishul and Dronagiri peaks."},
        {"name": "Cliff Top Club Restaurant", "category": "food", "lat": 30.5312, "lon": 79.5702, "desc": "High-altitude dining serving hearty Garhwali dishes and hot chai."},
        {"name": "Auli Artificial Lake Cafe", "category": "cafe", "lat": 30.5330, "lon": 79.5680, "desc": "Serene lakeside spot nestled between snow slopes with mountain views."},
        {"name": "Chattrakund Sweet Water Lake", "category": "attraction", "lat": 30.5450, "lon": 79.5900, "desc": "Pristine natural pond set inside dense oak forests."}
    ],
    "Cherrapunji": [
        {"name": "Nohkalikai Falls Viewpoint", "category": "viewpoint", "lat": 25.2758, "lon": 91.6853, "desc": "Spectacular viewing terrace overlooking India's tallest plunge waterfall."},
        {"name": "Orange Roots Restaurant", "category": "food", "lat": 25.2810, "lon": 91.7150, "desc": "Beloved local pure-veg restaurant known for authentic Khasi thalis and dosas."},
        {"name": "Avron Cafe Cherrapunjee", "category": "cafe", "lat": 25.2950, "lon": 91.7300, "desc": "Cozy hill cafe serving hot coffee, waffles, and bakery specialties."},
        {"name": "Mawsmai Cave Walkway", "category": "activity", "lat": 25.2442, "lon": 91.7198, "desc": "Lit limestone caves famous for stalactites and natural formations."},
        {"name": "Seven Sisters Falls View", "category": "viewpoint", "lat": 25.2450, "lon": 91.7250, "desc": "Seven-segmented waterfall cascading down deep limestone cliffs."}
    ],
    "Kaziranga": [
        {"name": "Bagori Safari Entry Point", "category": "activity", "lat": 26.5810, "lon": 93.1850, "desc": "Western range gateway famous for close sightings of the Great One-Horned Rhinoceros."},
        {"name": "Mai-Hang Ethnic Kitchen", "category": "food", "lat": 26.5870, "lon": 93.1720, "desc": "Authentic Assamese dining offering duck curry, pitika, and regional bamboo delicacies."},
        {"name": "Kaziranga Orchid Park & Folk Cultural Centre", "category": "attraction", "lat": 26.5920, "lon": 93.2050, "desc": "Showcase of indigenous wild orchids, traditional music, and herbal gardens."},
        {"name": "Wild Grass Resort Restaurant", "category": "food", "lat": 26.5890, "lon": 93.1900, "desc": "Rustic jungle dining pavilion surrounded by lush rural tea greenery."},
        {"name": "Diphlu River Viewpoint", "category": "viewpoint", "lat": 26.5750, "lon": 93.1600, "desc": "Tranquil riverfront spot popular for birdwatching and sunset reflections."}
    ],
    "Havelock Island": [
        {"name": "Radhanagar Sunset Point", "category": "viewpoint", "lat": 11.9842, "lon": 92.9515, "desc": "World-famous turquoise beach vantage point renowned for breathtaking sunsets."},
        {"name": "Something Different - A Beachside Cafe", "category": "cafe", "lat": 11.9950, "lon": 92.9800, "desc": "Colorful coastal bistro serving wood-fired pizzas, mocktails, and fresh seafood."},
        {"name": "Full Moon Cafe Havelock", "category": "cafe", "lat": 11.9800, "lon": 92.9900, "desc": "Laid-back beach shack cafe offering fresh fruit juices and coastal salads."},
        {"name": "Nemo Reef Diving & Snorkel Spot", "category": "activity", "lat": 12.0100, "lon": 93.0100, "desc": "Calm coral reef haven suitable for beginners and underwater photography."},
        {"name": "Anju Coco Resto", "category": "food", "lat": 11.9850, "lon": 92.9850, "desc": "High-rated island restaurant serving grilled seafood, curries, and tropical fruit shakes."}
    ],
    "Rann of Kutch": [
        {"name": "White Rann Salt Desert Sunset Viewpoint", "category": "viewpoint", "lat": 23.8340, "lon": 69.8320, "desc": "Vast shimmering white horizon best experienced during twilight and full moon."},
        {"name": "Kalo Dungar (Black Hill) Summit", "category": "viewpoint", "lat": 23.9312, "lon": 69.8169, "desc": "Highest point in Kutch overlooking the border and the panoramic salt flats."},
        {"name": "Dhordo Tent City Dining Hall", "category": "food", "lat": 23.8150, "lon": 69.8450, "desc": "Grand cultural dining space serving authentic Kutchi thalis and hot bajra rotlas."},
        {"name": "Hodka Artisanal Craft Village", "category": "market", "lat": 23.6800, "lon": 69.6500, "desc": "Traditional village market famous for mirror-work embroidery, quilts, and leathercraft."},
        {"name": "Kutch Chhayado Traditional Cafe", "category": "cafe", "lat": 23.8200, "lon": 69.8300, "desc": "Earthen-pot masala chai, local sweets, and savory Kutchi snacks."}
    ],
    "Tawang": [
        {"name": "Tawang Monastery Prayer Hall", "category": "attraction", "lat": 27.5861, "lon": 91.8594, "desc": "The largest Buddhist monastery in India, founded in 1680 with grand Himalayan views."},
        {"name": "Woodland Restaurant Tawang", "category": "food", "lat": 27.5875, "lon": 91.8650, "desc": "Popular town eatery serving hot Tibetan thukpa, momos, and traditional butter tea."},
        {"name": "Orange Restaurant & Lounge", "category": "food", "lat": 27.5850, "lon": 91.8620, "desc": "Warm mountain cafe offering Chinese, Indian, and regional Monpa dishes."},
        {"name": "Sela Pass Memorial & Lake Viewpoint", "category": "viewpoint", "lat": 27.5050, "lon": 92.1050, "desc": "High-altitude pass at 13,700 ft with pristine frozen lake views."},
        {"name": "Tawang War Memorial", "category": "attraction", "lat": 27.5890, "lon": 91.8700, "desc": "Historic stupa-shaped memorial set amidst landscaped gardens and flags."}
    ],
    "Alleppey": [
        {"name": "Cafe Catamaran Alleppey", "category": "cafe", "lat": 9.4930, "lon": 76.3190, "desc": "Seaside beach cafe with rooftop views serving espresso, pizzas, and shakes."},
        {"name": "Thaff Restaurant Alappuzha", "category": "food", "lat": 9.4980, "lon": 76.3350, "desc": "Historic city restaurant famous for authentic Kerala biryani and appam with stew."},
        {"name": "Halais Restaurant", "category": "food", "lat": 9.5020, "lon": 76.3400, "desc": "Traditional Syrian Christian & Malabar fish curry and parotta meals."},
        {"name": "Punnamada Backwater Jetty", "category": "activity", "lat": 9.5250, "lon": 76.3600, "desc": "Starting hub for tranquil shikara cruises through narrow coconut canals."},
        {"name": "Alappuzha Lighthouse Viewpoint", "category": "viewpoint", "lat": 9.4920, "lon": 76.3180, "desc": "Historical spiral lighthouse with panoramic aerial views of the Arabian Sea."}
    ],
    "Bodh Gaya": [
        {"name": "Mahabodhi Temple Meditation Park", "category": "viewpoint", "lat": 24.6959, "lon": 84.9914, "desc": "Peaceful sacred garden adjacent to the sacred Bodhi Tree."},
        {"name": "Sujata Cafe & Bakery", "category": "cafe", "lat": 24.6980, "lon": 84.9930, "desc": "Beloved gathering hub for international travelers serving herbal teas and fresh bread."},
        {"name": "Tirupati South Indian Restaurant", "category": "food", "lat": 24.6940, "lon": 84.9900, "desc": "Fresh vegetarian South Indian meals, filter coffee, and clean thalis."},
        {"name": "Be Happy Cafe Bodh Gaya", "category": "cafe", "lat": 24.6970, "lon": 84.9950, "desc": "Organic coffee, thin-crust pizzas, and apple pies in a serene courtyard."},
        {"name": "Great Buddha Statue Complex", "category": "attraction", "lat": 24.6985, "lon": 84.9820, "desc": "Magnificent 80-foot stone Buddha statue surrounded by meditation gardens."}
    ],
    "Spiti Valley Test": [
        {"name": "Key Gompa High Ridge Viewpoint", "category": "viewpoint", "lat": 32.2980, "lon": 78.0120, "desc": "Overlook above the ancient monastery with breathtaking views of the Spiti River basin."},
        {"name": "Cafe Kunzum Top Kaza", "category": "cafe", "lat": 32.2260, "lon": 78.0720, "desc": "Popular mountaineer cafe serving lemon-ginger tea, pasta, and sea buckthorn juice."},
        {"name": "The Himalayan Cafe Kaza", "category": "food", "lat": 32.2270, "lon": 78.0710, "desc": "Authentic Spitian and Tibetan cuisine: thenthuk, tingmo, and mutton curries."},
        {"name": "Chicham Bridge Aerial Span", "category": "viewpoint", "lat": 32.3500, "lon": 77.9800, "desc": "Asia's highest suspension bridge over a sheer 1,000 ft deep rocky gorge."},
        {"name": "Hikkim Highest Post Office", "category": "attraction", "lat": 32.2500, "lon": 78.0900, "desc": "World's highest operational post office at 14,567 ft where travelers send postcards."}
    ]
}

def enrich_destination_places(conn, dest_name, lat, lon):
    c = conn.cursor()
    
    # Check current categories
    c.execute("SELECT DISTINCT category FROM local_places WHERE destination = ?", (dest_name,))
    existing_cats = set(r[0] for r in c.fetchall())
    c.execute("SELECT name FROM local_places WHERE destination = ?", (dest_name,))
    seen_names = set(r[0].lower() for r in c.fetchall())

    added = 0

    # 1. First add curated places if destination is in curated table
    if dest_name in CURATED_VERIFIED_PLACES:
        for p in CURATED_VERIFIED_PLACES[dest_name]:
            if p["name"].lower() not in seen_names:
                seen_names.add(p["name"].lower())
                c.execute("""
                    INSERT INTO local_places (destination, name, category, latitude, longitude, description, source, status, crowd_hint)
                    VALUES (?, ?, ?, ?, ?, ?, 'admin', 'approved', ?)
                """, (dest_name, p["name"], p["category"], p["lat"], p["lon"], p["desc"], "Great spot across morning and evening."))
                added += 1

    # 2. For missing categories (food, viewpoint, attraction, market, cafe), query Nominatim
    needed_queries = []
    if "food" not in existing_cats:
        needed_queries.append(("food", f"restaurant, {dest_name}, India"))
    if "viewpoint" not in existing_cats:
        needed_queries.append(("viewpoint", f"viewpoint, {dest_name}, India"))
    if "attraction" not in existing_cats:
        needed_queries.append(("attraction", f"attraction, {dest_name}, India"))
    if "cafe" not in existing_cats:
        needed_queries.append(("cafe", f"cafe, {dest_name}, India"))

    nom_url = "https://nominatim.openstreetmap.org/search"
    for cat_type, q_str in needed_queries:
        try:
            r = requests.get(nom_url, params={"q": q_str, "format": "json", "limit": 4}, headers=HEADERS, timeout=5)
            if r.status_code == 200:
                for item in r.json():
                    raw = item.get("name") or item.get("display_name", "").split(",")[0]
                    nm = raw.strip() if raw else ""
                    if not nm or len(nm) < 2 or nm.lower() in seen_names or dest_name.lower() == nm.lower():
                        continue
                    seen_names.add(nm.lower())
                    p_lat = float(item.get("lat"))
                    p_lon = float(item.get("lon"))
                    osm_id = str(item.get("osm_id", ""))
                    c.execute("""
                        INSERT INTO local_places (destination, name, category, latitude, longitude, description, source, osm_id, status, crowd_hint)
                        VALUES (?, ?, ?, ?, ?, ?, 'osm', ?, 'approved', ?)
                    """, (
                        dest_name, nm, cat_type, p_lat, p_lon,
                        f"Real {cat_type} in {dest_name} from OpenStreetMap.",
                        osm_id, "Relaxed early in the morning." if cat_type in ("viewpoint", "attraction") else None
                    ))
                    added += 1
            time.sleep(0.3)
        except Exception as e:
            pass

    conn.commit()
    return added

def main():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT name, latitude, longitude FROM destinations")
    destinations = c.fetchall()

    print(f"Enriching local places for {len(destinations)} destinations...")
    total_added = 0
    for name, lat, lon in destinations:
        n_added = enrich_destination_places(conn, name, lat, lon)
        if n_added > 0:
            print(f"  + Added {n_added} places for {name}")
            total_added += n_added

    print(f"\nDone! Total new places added: {total_added}")
    
    # Audit final state
    c.execute("SELECT category, COUNT(*) FROM local_places GROUP BY category")
    print("\nUpdated Categories Breakdown:")
    for cat, count in c.fetchall():
        print(f"  {cat}: {count}")

    c.execute("""
        SELECT d.name, COUNT(lp.id)
        FROM destinations d
        LEFT JOIN local_places lp ON d.name = lp.destination
        GROUP BY d.name
        HAVING COUNT(lp.id) < 5
    """)
    under_5 = c.fetchall()
    print(f"\nDestinations with < 5 places: {len(under_5)}")
    for d, cnt in under_5:
        print(f"  {d}: {cnt}")

    conn.close()

if __name__ == "__main__":
    main()
