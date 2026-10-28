import sys
import json
from fastapi.testclient import TestClient
from backend.main import app
from backend.database import SessionLocal
from backend.models import User, LocalPlace, Destination, Photo, VibeScore

client = TestClient(app)

print("=" * 80)
print("VIBETRIP COMPREHENSIVE SMOKE & SECURITY ACCESS TEST SUITE")
print("=" * 80)

# Helper function to print test result
def check(test_name, condition, details=""):
    status = "PASS" if condition else "FAIL"
    print(f"[{status}] {test_name}")
    if details:
        print(f"       Details: {details}")
    if not condition:
        sys.exit(1)

# 1. Test /api/recommend & explanation logic
print("\n--- 1. Recommendation API & Explanation ---")
res = client.post("/api/recommend", json={
    "query_text": "",
    "target_dims": {"nature": "high", "visual_atmosphere": "high", "crowd_match": "low"}
})
check("POST /api/recommend returns 200", res.status_code == 200)
recs = res.json().get("recommendations", [])
check("Returns 10 ranked recommendations", len(recs) == 10)
top_rec = recs[0]
check("Recommendation contains overall_match_score", "overall_match_score" in top_rec)
check("Explanation includes must-have/possible mismatch", "Possible mismatch:" in top_rec["explanation"] or "Why this matches:" in top_rec["explanation"])
print("Example Top Recommendation:", json.dumps({
    "name": top_rec["name"],
    "score": round(top_rec["overall_match_score"], 1),
    "explanation_snippet": top_rec["explanation"][:120] + "..."
}, indent=2))

# 2. Test /api/destination/{name}
print("\n--- 2. Destination Details API ---")
res = client.get("/api/destination/Agra")
check("GET /api/destination/Agra returns 200", res.status_code == 200)
dest_data = res.json()
check("Contains vibe scores and photos", len(dest_data["photos"]) > 0 and "nature" in dest_data["scores"])
print("Destination Sample:", json.dumps({
    "name": dest_data["name"],
    "state": dest_data["state"],
    "photos_count": len(dest_data["photos"]),
    "scores": dest_data["scores"]
}, indent=2))

# 3. Test /api/trip-plan for 3 distinct destinations
print("\n--- 3. Itinerary Generation (3 Distinct Destinations) ---")
for d_name in ["Agra", "Manali", "Goa"]:
    res = client.post("/api/trip-plan", json={"destination": d_name, "days": 3})
    check(f"POST /api/trip-plan for {d_name} returns 200", res.status_code == 200)
    plan = res.json()
    check(f"{d_name} plan has 3 days", len(plan["days_itinerary"]) == 3)
    day1_stop = plan["days_itinerary"][0]["slots"][0]["place_name"]
    print(f"  {d_name}: Best time: {plan['best_time_to_visit']} | Crowd tip: {plan['crowd_tip'][:60]}... | Day 1 start: {day1_stop}")

# 4. Auth & Role Tests
print("\n--- 4. Authentication, Roles & Security Rules ---")

# (a) Tourist signup & login
res = client.post("/api/auth/signup", json={
    "name": "Test Tourist User",
    "email": "tourist.test@example.com",
    "password": "TouristPassword123!",
    "role": "tourist",
    "home_city": "Chennai"
})
if res.status_code == 400 and "already exists" in res.text:
    res = client.post("/api/auth/login", json={"email": "tourist.test@example.com", "password": "TouristPassword123!"})
check("Tourist login/signup returns 200 with JWT", res.status_code == 200)
tourist_token = res.json()["access_token"]
tourist_id = res.json()["user"]["id"]

# (b) Local signup & login
res = client.post("/api/auth/signup", json={
    "name": "Test Local Host",
    "email": "local.host@example.com",
    "password": "LocalPassword123!",
    "role": "local",
    "home_city": "Agra"
})
if res.status_code == 400 and "already exists" in res.text:
    res = client.post("/api/auth/login", json={"email": "local.host@example.com", "password": "LocalPassword123!"})
check("Local login/signup returns 200 with JWT", res.status_code == 200)
local_token = res.json()["access_token"]
local_id = res.json()["user"]["id"]

# (c) Admin login
res = client.post("/api/auth/login", json={"email": "admin@vibetrip.internal", "password": "AdminSuperPass2026!"})
check("Admin login returns 200 with JWT", res.status_code == 200)
admin_token = res.json()["access_token"]

# ACCESS RULE 1: Tourist calling an admin endpoint MUST GET 403
res = client.get("/api/admin/stats", headers={"Authorization": f"Bearer {tourist_token}"})
check("Rule 1: Tourist calling admin endpoint gets 403 Forbidden", res.status_code == 403)

# ACCESS RULE 2: Local submission is invisible to public until approved
print("\n--- 5. Contributor Workflow & Visibility ---")
res = client.post("/api/local/submissions", headers={"Authorization": f"Bearer {local_token}"}, json={
    "destination": "Agra",
    "name": "Secret Sunrise Rooftop View",
    "category": "viewpoint",
    "latitude": 27.174,
    "longitude": 78.041,
    "description": "Hidden unobstructed view of the Taj Mahal at dawn."
})
check("Local user can submit a place (status: pending)", res.status_code == 200 and res.json()["status"] == "pending")
submitted_place_id = res.json()["id"]

# Check public local-experiences list: MUST NOT show pending place
res = client.get("/api/local-experiences/Agra")
experiences = res.json().get("experiences", [])
check("Rule 2: Pending local submission is invisible to public", not any(p["id"] == submitted_place_id for p in experiences))

# Admin approves submission
res = client.post(f"/api/admin/submissions/{submitted_place_id}/review", headers={"Authorization": f"Bearer {admin_token}"}, json={
    "action": "approve"
})
check("Admin can review and approve submission", res.status_code == 200 and res.json()["status"] == "approved")

# Now check public list: MUST appear with source label
res = client.get("/api/local-experiences/Agra")
approved_exps = res.json().get("experiences", [])
check("Approved place is now visible publicly with 'Added by a local' badge", any(p["id"] == submitted_place_id and p["source_label"] == "Added by a local" for p in approved_exps))

# ACCESS RULE 3: Another user's email NEVER appears before a connection request is accepted
print("\n--- 6. Traveler Matching & Privacy (Rule 3) ---")
res = client.get("/api/buddy-matches/Manali", headers={"Authorization": f"Bearer {tourist_token}"})
check("GET /api/buddy-matches/Manali returns 200", res.status_code == 200)
travelers = res.json().get("travelers", [])
check("Found discoverable travelers for Manali", len(travelers) > 0)
check("Rule 3: User email is NEVER exposed in buddy match cards", not any("email" in t for t in travelers))
print("Sample Traveler Card (Privacy Preserved):", json.dumps({
    "name": travelers[0]["name"],
    "is_demo": travelers[0]["is_demo"],
    "compatibility": travelers[0]["compatibility"],
    "breakdown": travelers[0]["breakdown"]
}, indent=2))

# ACCESS RULE 4: Blocked user never appears in matches
print("\n--- 7. Blocking & Safety (Rule 4) ---")
target_id = travelers[0]["user_id"]
res = client.post("/api/users/block", headers={"Authorization": f"Bearer {tourist_token}"}, json={
    "target_user_id": target_id,
    "reason": "Test blocking functionality"
})
check("User can block another traveler", res.status_code == 200)

res = client.get("/api/buddy-matches/Manali", headers={"Authorization": f"Bearer {tourist_token}"})
filtered_travelers = res.json().get("travelers", [])
check("Rule 4: Blocked user never appears in traveler matches", not any(t["user_id"] == target_id for t in filtered_travelers))

print("\n" + "=" * 80)
print("ALL SMOKE TESTS AND SECURITY ACCESS RULES PASSED SUCCESSFULLY!")
print("=" * 80)
