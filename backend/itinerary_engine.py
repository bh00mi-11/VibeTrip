import math
from typing import List, Dict, Any, Tuple

def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Returns approximate distance in kilometers between two coords."""
    R = 6371.0 # Earth radius in km
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

def recommend_transit(
    dist_km: float,
    terrain_category: str = "",
    vibe_scores: Dict[str, float] = None,
    destination_name: str = "",
    time_slot_label: str = "Morning"
) -> Dict[str, Any]:
    """
    Synthesizes transit & commute recommendations combining:
    1. PyTorch Deep Choice Neural Network (Multinomial Mode Choice with Softmax & LeakyReLU)
    2. Localized pricing, duration, and rental facility alternatives
    """
    vibe = vibe_scores or {}
    
    # Run PyTorch Deep Neural Network prediction
    dl_prediction = None
    try:
        from .deep_transit_model import predict_deep_transit_choice
        dl_prediction = predict_deep_transit_choice(
            dist_km=dist_km,
            destination_name=destination_name,
            terrain_category=terrain_category,
            vibe_scores=vibe,
            time_slot_label=time_slot_label
        )
    except Exception:
        try:
            from backend.deep_transit_model import predict_deep_transit_choice
            dl_prediction = predict_deep_transit_choice(
                dist_km=dist_km,
                destination_name=destination_name,
                terrain_category=terrain_category,
                vibe_scores=vibe,
                time_slot_label=time_slot_label
            )
        except Exception as e:
            dl_prediction = None
    adv = vibe.get("adventure", 50.0)
    peace = vibe.get("peacefulness", 50.0)
    nature = vibe.get("nature", 50.0)
    
    is_hill_or_mountain = any(k in (terrain_category or "").lower() or k in (destination_name or "").lower() 
                              for k in ["hill", "mountain", "manali", "rishikesh", "darjeeling", "ooty", "munnar", "shimla", "ladakh", "leh", "kodaikanal", "nainital"])

    if dist_km <= 1.5:
        primary_mode = "Scenic Walking Corridor" if nature > 55 or peace > 55 else "Local Auto / E-Rickshaw"
        primary_icon = "walking" if "Walking" in primary_mode else "rickshaw"
        est_time = f"{max(5, int(dist_km * 14))} mins walk" if "Walking" in primary_mode else "4 - 8 mins"
        est_cost = "Free (Pedestrian)" if "Walking" in primary_mode else "₹30 - ₹60"
        alternatives = [
            {"mode": "Bicycle Rental", "cost": "₹60 - ₹100/hr", "time": "5 mins", "provider": "Pedal Station / Local Hub"},
            {"mode": "E-Rickshaw", "cost": "₹20 - ₹40", "time": "6 mins", "provider": "Stand outside attraction"}
        ]
        rental_tip = "Gentle walking corridor with picturesque viewpoints and street stalls along the route."
    elif dist_km <= 5.0:
        if is_hill_or_mountain:
            primary_mode = "Shared Mountain Jeep / Local Taxi"
            primary_icon = "jeep"
            est_time = f"{int(dist_km * 3.5 + 4)} - {int(dist_km * 4.5 + 8)} mins"
            est_cost = "₹60 - ₹120 (Shared) / ₹250 (Private)"
            alternatives = [
                {"mode": "Self-Drive Scooty Rental", "cost": "₹500 - ₹800/day", "time": f"{int(dist_km * 3.5)} mins", "provider": "Royal Brothers / Local Hub"},
                {"mode": "State Hill Bus", "cost": "₹20 - ₹35", "time": f"{int(dist_km * 5 + 10)} mins", "provider": "Local Bus Depot"}
            ]
            rental_tip = "Scenic uphill roads; shared jeeps are frequent, economical, and stop directly at the gates."
        else:
            primary_mode = "Auto-Rickshaw / E-Cab"
            primary_icon = "rickshaw"
            est_time = f"{int(dist_km * 3 + 4)} - {int(dist_km * 4 + 6)} mins"
            est_cost = f"₹{int(40 + dist_km * 16)} - ₹{int(60 + dist_km * 22)}"
            alternatives = [
                {"mode": "App Cab (Uber / Ola)", "cost": f"₹{int(90 + dist_km * 20)} - ₹{int(120 + dist_km * 26)}", "time": f"{int(dist_km * 3.2)} mins", "provider": "Uber / Ola / Rapido"},
                {"mode": "Self-Drive Scooty / Bike", "cost": "₹450 - ₹700/day", "time": f"{int(dist_km * 2.8)} mins", "provider": "RentMyBike / Local Vendors"}
            ]
            rental_tip = "Auto stands are easily accessible near the exit; digital meters or app-based booking recommended."
    elif dist_km <= 16.0:
        if is_hill_or_mountain:
            primary_mode = "Private Hill Taxi / 4x4 Gypsy"
            primary_icon = "taxi"
            est_time = f"{int(dist_km * 3.5 + 10)} - {int(dist_km * 4.5 + 15)} mins"
            est_cost = f"₹{int(450 + dist_km * 35)} - ₹{int(600 + dist_km * 45)}"
            alternatives = [
                {"mode": "Royal Enfield / Cruiser Rental", "cost": "₹900 - ₹1500/day", "time": f"{int(dist_km * 3.2)} mins", "provider": "Royal Brothers / Himalayan Rides"},
                {"mode": "Shared Sumo / Bolero", "cost": f"₹{int(70 + dist_km * 8)} - ₹{int(110 + dist_km * 10)}", "time": f"{int(dist_km * 4.2)} mins", "provider": "Central Taxi Union"}
            ]
            rental_tip = "Pre-negotiate round-trip with waiting time or book via the government-authorized taxi union kiosk."
        else:
            primary_mode = "App Cab (Sedan / Prime)"
            primary_icon = "taxi"
            est_time = f"{int(dist_km * 2.5 + 8)} - {int(dist_km * 3.5 + 12)} mins"
            est_cost = f"₹{int(180 + dist_km * 18)} - ₹{int(250 + dist_km * 24)}"
            alternatives = [
                {"mode": "City Bus / Rapid Metro", "cost": "₹25 - ₹50", "time": f"{int(dist_km * 4 + 10)} mins", "provider": "State Transport Corporation"},
                {"mode": "Self-Drive Car (Zoomcar)", "cost": "₹1400 - ₹2200/day", "time": f"{int(dist_km * 2.4)} mins", "provider": "Zoomcar / Revv"}
            ]
            rental_tip = "Comfortable highway commute; AC cabs are recommended during peak afternoon heat."
    else:
        # Day excursion / outstation (> 16 km)
        primary_mode = "Dedicated Day Cab Hire / Tourist Coach"
        primary_icon = "bus"
        est_time = f"{int(dist_km * 2.2 + 15)} - {int(dist_km * 2.8 + 25)} mins"
        est_cost = f"₹{int(800 + dist_km * 18)} - ₹{int(1200 + dist_km * 24)} (Half/Full Day)"
        alternatives = [
            {"mode": "AC Tourist Coach / State Express", "cost": f"₹{int(150 + dist_km * 6)} - ₹{int(250 + dist_km * 8)}", "time": f"{int(dist_km * 2.6 + 10)} mins", "provider": "State Tourism (ITDC / State RTDC)"},
            {"mode": "Self-Drive Rental Car", "cost": "₹1800 - ₹3000/day", "time": f"{int(dist_km * 2.1)} mins", "provider": "Zoomcar / Local Fleet"}
        ]
        rental_tip = "Book a dedicated driver with multi-stop waiting allowance for stress-free sightseeing."

    res = {
        "distance_km": round(dist_km, 1),
        "primary_mode": (dl_prediction["chosen_mode"] if dl_prediction else primary_mode),
        "mode_icon": (dl_prediction["mode_icon"] if dl_prediction else primary_icon),
        "est_commute_time": (f"{dl_prediction['est_time_mins']} mins" if dl_prediction else est_time),
        "est_price_range": (dl_prediction["est_price_range"] if dl_prediction else est_cost),
        "transit_tip": (dl_prediction["ai_rationale"] if dl_prediction else rental_tip),
        "alternatives": alternatives
    }
    if dl_prediction:
        res["dl_choice_confidence"] = dl_prediction["confidence_score"]
        res["dl_probability_distribution"] = dl_prediction["probability_distribution"]
        res["dl_architecture"] = dl_prediction["dl_architecture"]
        res["eco_rating"] = dl_prediction["eco_rating"]
        res["comfort_rating"] = dl_prediction["comfort_rating"]
    return res

def build_itinerary(
    destination_name: str,
    meta: Dict[str, Any],
    vibe_scores: Dict[str, float],
    local_places: List[Dict[str, Any]],
    days: int = 3,
    user_vibes: Dict[str, float] = None
) -> Dict[str, Any]:
    days = max(1, min(7, days))
    user_vibes = user_vibes or vibe_scores

    # 1. Best season note & crowd tip
    best_time = meta.get("best_time") or "Year-round"
    crowd_val = vibe_scores.get("crowd_match", 50.0)
    if crowd_val < 35:
        crowd_tip = "High tourist density: major spots get crowded. We recommend starting your days before 8:30 AM to beat tour buses."
    elif crowd_val > 65:
        crowd_tip = "Gentle crowds and relaxed foot traffic: ideal for unhurried exploration and spontaneous walk-ins."
    else:
        crowd_tip = "Moderate crowds: weekend afternoons see peak foot traffic, while mornings remain calm and pleasant."

    # 2. Extract attractions from meta
    raw_attractions = meta.get("top_attractions", "") or ""
    attraction_names = [a.strip() for a in raw_attractions.split("|") if a.strip()]

    # Separate places into food/cafe vs activities/viewpoints/attractions
    food_places = [p for p in local_places if p.get("category") in ("cafe", "food", "market")]
    sight_places = [p for p in local_places if p.get("category") not in ("cafe", "food", "market")]

    # Sort sights based on vibe preferences
    peace_pref = user_vibes.get("peacefulness", 50.0)
    adv_pref = user_vibes.get("adventure", 50.0)

    if adv_pref > 60:
        # Prioritize activity and outdoor spots
        sight_places.sort(key=lambda p: 0 if p.get("category") in ("activity", "viewpoint") else 1)
    elif peace_pref > 60:
        # Prioritize viewpoints and quiet spots
        sight_places.sort(key=lambda p: 0 if p.get("category") in ("viewpoint", "stay") else 1)

    # Base coords for fallback clustering
    base_lat = meta.get("latitude") or 20.0
    base_lon = meta.get("longitude") or 78.0

    # Group sights geographically across days
    # Combine attractions into sight objects
    combined_sights = []
    for att in attraction_names:
        combined_sights.append({
            "name": att,
            "category": "attraction",
            "source": "curated",
            "latitude": base_lat,
            "longitude": base_lon,
            "description": f"Iconic highlight of {destination_name}."
        })
    for p in sight_places:
        combined_sights.append(p)

    # Deduplicate sights by name
    seen_names = set()
    unique_sights = []
    for s in combined_sights:
        n = s["name"].lower()
        if n not in seen_names:
            seen_names.add(n)
            unique_sights.append(s)

    # Sort geographically by distance from centroid or by latitude to naturally cluster
    unique_sights.sort(key=lambda s: (s.get("latitude") or base_lat) + (s.get("longitude") or base_lon))

    day_plans = []
    total_sights = len(unique_sights)
    sight_idx = 0
    food_idx = 0

    for d in range(1, days + 1):
        # 2-3 main stops per day
        day_stops = []
        for _ in range(2):
            if sight_idx < total_sights:
                day_stops.append(unique_sights[sight_idx])
                sight_idx += 1
            else:
                day_stops.append({
                    "name": f"Local Heritage Walk & Old Quarter",
                    "category": "walk",
                    "source": "curated",
                    "latitude": base_lat,
                    "longitude": base_lon,
                    "description": "Scenic stroll through artisanal neighborhoods."
                })

        # Add a 3rd sight if available
        if sight_idx < total_sights and (d == 1 or len(day_stops) < 3):
            day_stops.append(unique_sights[sight_idx])
            sight_idx += 1

        # Pick 1 food/cafe stop for this day
        if food_places:
            food_stop = food_places[food_idx % len(food_places)]
            food_idx += 1
        else:
            food_stop = {
                "name": f"Traditional Regional Cuisine Tasting",
                "category": "food",
                "source": "curated",
                "latitude": base_lat,
                "longitude": base_lon,
                "description": "Sample signature authentic dishes in a beloved local eatery."
            }

        # Build morning, afternoon, evening slots
        morning_stop = day_stops[0]
        afternoon_stop = food_stop
        evening_stop = day_stops[1] if len(day_stops) > 1 else day_stops[0]
        extra_stop = day_stops[2] if len(day_stops) > 2 else None

        # Proximity / distance calculation
        m_lat = morning_stop.get("latitude") or base_lat
        m_lon = morning_stop.get("longitude") or base_lon
        f_lat = afternoon_stop.get("latitude") or base_lat
        f_lon = afternoon_stop.get("longitude") or base_lon
        e_lat = evening_stop.get("latitude") or base_lat
        e_lon = evening_stop.get("longitude") or base_lon

        d1 = haversine_distance(m_lat, m_lon, f_lat, f_lon)
        d2 = haversine_distance(f_lat, f_lon, e_lat, e_lon)
        if d1 < 0.2: d1 = 1.2
        if d2 < 0.2: d2 = 1.8

        # Vibe-aware notes
        morning_note = "Arrive early around 8:30 AM to enjoy calm atmospheres and avoid lines." if crowd_val < 45 else "Great morning spot for photography and leisurely exploration."
        evening_note = "Perfect tranquil spot for unwinding as dusk settles." if peace_pref > 60 else "Vibrant evening buzz with lively local ambiance."

        morning_transit = {
            "distance_km": 0.0,
            "primary_mode": "Starting Point (Hotel / Base)",
            "mode_icon": "start",
            "est_commute_time": "Departure",
            "est_price_range": "₹0",
            "transit_tip": "Start from hotel or central city area; pre-book transport if early morning.",
            "alternatives": []
        }
        afternoon_transit = recommend_transit(d1, meta.get("category", ""), user_vibes, destination_name)
        evening_transit = recommend_transit(d2, meta.get("category", ""), user_vibes, destination_name)

        slots = [
            {
                "time_slot": "Morning (09:00 - 12:30)",
                "place_name": morning_stop["name"],
                "category": morning_stop.get("category", "attraction"),
                "source": morning_stop.get("source", "curated"),
                "tip": morning_note,
                "est_distance": "Start point",
                "transit": morning_transit
            },
            {
                "time_slot": "Afternoon (13:00 - 15:30)",
                "place_name": afternoon_stop["name"],
                "category": afternoon_stop.get("category", "food"),
                "source": afternoon_stop.get("source", "curated"),
                "tip": "Rest and savor local specialties.",
                "est_distance": f"~{d1:.1f} km from morning stop",
                "transit": afternoon_transit
            },
            {
                "time_slot": "Late Afternoon & Evening (16:00 - 19:30)",
                "place_name": evening_stop["name"],
                "category": evening_stop.get("category", "attraction"),
                "source": evening_stop.get("source", "curated"),
                "tip": evening_note,
                "est_distance": f"~{d2:.1f} km from afternoon stop",
                "transit": evening_transit
            }
        ]

        if extra_stop:
            m_lat = morning_stop.get("latitude") or base_lat
            m_lon = morning_stop.get("longitude") or base_lon
            ex_lat = extra_stop.get("latitude") or base_lat
            ex_lon = extra_stop.get("longitude") or base_lon
            extra_dist = haversine_distance(m_lat, m_lon, ex_lat, ex_lon)
            if extra_dist < 0.3:
                # Add natural inter-attraction spread based on day and destination
                extra_dist = 2.4 + (d * 1.3)
            
            extra_transit = recommend_transit(extra_dist, meta.get("category", ""), user_vibes, destination_name, time_slot_label="Midday")
            slots.insert(1, {
                "time_slot": "Mid-day Highlights (11:30 - 13:00)",
                "place_name": extra_stop["name"],
                "category": extra_stop.get("category", "attraction"),
                "source": extra_stop.get("source", "curated"),
                "tip": "Nearby highlight along the day route.",
                "est_distance": f"~{extra_dist:.1f} km from morning stop",
                "transit": extra_transit
            })

        # Calculate estimated daily commute budget
        daily_km = round(sum(s.get("transit", {}).get("distance_km", 0.0) for s in slots), 1)

        day_plans.append({
            "day": d,
            "theme": f"Day {d}: " + ("Historical & Visual Wonders" if d == 1 else "Hidden Gems & Cultural Immersion" if d == 2 else "Panoramic Vistas & Farewell Walks"),
            "daily_commute_km": daily_km,
            "slots": slots
        })

    # Curate local rental & transit hubs based on destination terrain
    is_hill = any(k in (meta.get("category") or "").lower() or k in destination_name.lower() 
                  for k in ["hill", "mountain", "manali", "rishikesh", "darjeeling", "ooty", "munnar", "shimla", "ladakh", "leh"])
    
    transit_facilities = {
        "rental_hubs": [
            {
                "type": "Private Sightseeing Cab (Sedan / SUV / Outstation)",
                "provider": "Uber / Ola Local Sightseeing Cab" if not is_hill else "Central Taxi Union & Uber Intercity",
                "rate": "₹1800 - ₹3200 / day (8 hrs / 80 km)",
                "highlights": "Dedicated driver, AC, toll/parking included upon confirmation.",
                "contact_type": "Uber / Ola App & Taxi Kiosk",
                "phone": "Book via Uber / Ola App or Stand",
                "category_tag": "cab",
                "primary_action_label": "Book via Uber",
                "primary_action_url": f"https://m.uber.com/looking?drop[0]={{\"addressLine1\":\"{destination_name}\"}}",
                "secondary_action_label": "Open Ola Cabs",
                "secondary_action_url": "https://www.olacabs.com/"
            },
            {
                "type": "Self-Drive Scooty & Motorbike Rental",
                "provider": "Royal Brothers Bike Rentals",
                "rate": "₹500 - ₹900 / day",
                "highlights": "Helmet included, zero security deposit with valid DL, fuel extra.",
                "contact_type": "Direct Hub & Online Booking",
                "phone": "+91 90195 95595",
                "category_tag": "bike",
                "primary_action_label": "Book on Royal Brothers",
                "primary_action_url": "https://www.royalbrothers.com/",
                "secondary_action_label": "Find Local Bike Rentals on Google Maps",
                "secondary_action_url": f"https://www.google.com/maps/search/bike+scooter+rental+near+{destination_name.replace(' ', '+')}"
            },
            {
                "type": "Eco Commute & Bicycle Rentals",
                "provider": "Local Pedal & Cycle Station",
                "rate": "₹150 - ₹300 / day (₹50/hr)",
                "highlights": "Geared mountain bikes or city cruisers for local sightseeing lanes.",
                "contact_type": "Walk-in & Rental Stalls",
                "phone": "Walk-in registration at site",
                "category_tag": "bicycle",
                "primary_action_label": "Find Bicycle Stands on Google Maps",
                "primary_action_url": f"https://www.google.com/maps/search/bicycle+cycle+rental+near+{destination_name.replace(' ', '+')}",
                "secondary_action_label": "Explore Yulu / Local Hubs",
                "secondary_action_url": "https://www.yulu.bike/"
            },
            {
                "type": "Certified Local Tour & Trek Guides",
                "provider": f"Verified Tourism Guides Registry ({destination_name})",
                "rate": "₹2500 - ₹4500 / day",
                "highlights": "Government / ASI accredited guides, safety trained, with instant direct UPI payout settlements.",
                "contact_type": "Direct Certified Guide Booking",
                "phone": "Direct UPI & Phone Verified",
                "category_tag": "guide",
                "primary_action_label": "Find Guides in Nearby & OSM Places",
                "primary_action_url": f"https://www.google.com/maps/search/tourist+guides+near+{destination_name.replace(' ', '+')}",
                "secondary_action_label": "Explore Govt Tourism Registry",
                "secondary_action_url": "https://tourism.gov.in/"
            }
        ],
        "local_transit_advisory": (
            "Mountain roads can have narrow stretches and one-way evening restrictions. Shared 4x4 jeeps or prepaid union taxis offer the safest transit."
            if is_hill else
            "App cabs (Uber/Ola) and metered auto-rickshaws are readily available. For visiting multiple sights across the day, hiring a continuous day cab saves 30-40% compared to multiple individual bookings."
        )
    }

    return {
        "destination": destination_name,
        "days": days,
        "best_time_to_visit": best_time,
        "crowd_tip": crowd_tip,
        "transit_facilities": transit_facilities,
        "vibe_focus": {
            "nature": round(user_vibes.get("nature", 50.0), 1),
            "adventure": round(user_vibes.get("adventure", 50.0), 1),
            "peacefulness": round(user_vibes.get("peacefulness", 50.0), 1),
            "crowd_match": round(user_vibes.get("crowd_match", 50.0), 1),
            "visual_atmosphere": round(user_vibes.get("visual_atmosphere", 50.0), 1)
        },
        "days_itinerary": day_plans
    }
