import time
import requests
from typing import List, Dict, Any

def query_osm_places(lat: float, lon: float, destination_name: str, radius_m: int = 8000, limit: int = 25) -> List[Dict[str, Any]]:
    """
    Fast and targeted place discovery using OpenStreetMap Nominatim search.
    Queries 2 high-yield categories per destination to ensure rapid coverage without rate-limit stalling.
    """
    if not lat or not lon:
        return []

    headers = {"User-Agent": "VibeTripAcademic/1.0 (academic-vit-project)"}
    places = []
    seen_names = set()

    # Query 2 high-yield categories per destination
    categories = [
        ("cafe", f"cafe, {destination_name}, India"),
        ("attraction", f"attraction, {destination_name}, India")
    ]
    nom_url = "https://nominatim.openstreetmap.org/search"
    for cat_type, search_q in categories:
        if len(places) >= limit:
            break
        try:
            r = requests.get(nom_url, params={"q": search_q, "format": "json", "limit": 6}, headers=headers, timeout=4)
            if r.status_code == 200:
                for item in r.json():
                    raw = item.get("name") or item.get("display_name", "").split(",")[0]
                    nm = raw.strip() if raw else ""
                    if not nm or len(nm) < 2 or nm.lower() in seen_names or destination_name.lower() == nm.lower():
                        continue
                    seen_names.add(nm.lower())
                    places.append({
                        "name": nm,
                        "category": cat_type,
                        "latitude": float(item.get("lat")),
                        "longitude": float(item.get("lon")),
                        "description": f"Verified {cat_type} in {destination_name} (from OpenStreetMap).",
                        "source": "osm",
                        "osm_id": str(item.get("osm_id", "")),
                        "status": "approved",
                        "crowd_hint": "Early visits recommended to avoid peak tour crowds." if cat_type == "attraction" else None
                    })
            time.sleep(0.15)
        except Exception:
            pass

    return places[:limit]
