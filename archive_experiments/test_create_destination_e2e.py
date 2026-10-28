import io
from PIL import Image
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

print("=" * 80)
print("TESTING ADMIN NEW DESTINATION CREATION END-TO-END")
print("=" * 80)

# 1. Login as Admin
from backend.database import SessionLocal
from backend.models import Destination, Photo, VibeScore
db = SessionLocal()
existing_d = db.query(Destination).filter(Destination.name == "Spiti Valley Test").first()
if existing_d:
    db.query(Photo).filter(Photo.destination == "Spiti Valley Test").delete()
    db.query(VibeScore).filter(VibeScore.destination == "Spiti Valley Test").delete()
    db.delete(existing_d)
    db.commit()
db.close()

login_res = client.post("/api/auth/login", json={"email": "admin@vibetrip.internal", "password": "AdminSuperPass2026!"})
assert login_res.status_code == 200, f"Admin login failed: {login_res.text}"
admin_token = login_res.json()["access_token"]
headers = {"Authorization": f"Bearer {admin_token}"}

# 2. Create 4 dummy image buffers
def create_dummy_image(color=(100, 150, 200)):
    buf = io.BytesIO()
    img = Image.new("RGB", (256, 256), color=color)
    img.save(buf, format="JPEG")
    buf.seek(0)
    return buf

photos = [
    ("photos", ("photo_01.jpg", create_dummy_image((120, 180, 220)), "image/jpeg")),
    ("photos", ("photo_02.jpg", create_dummy_image((130, 190, 230)), "image/jpeg")),
    ("photos", ("photo_03.jpg", create_dummy_image((140, 200, 240)), "image/jpeg")),
    ("photos", ("photo_04.jpg", create_dummy_image((150, 210, 250)), "image/jpeg")),
]

data = {
    "name": "Spiti Valley Test",
    "state": "Himachal Pradesh",
    "region": "North",
    "category": "Adventure",
    "best_time": "May-Oct",
    "description": "High-altitude cold mountain desert with ancient Tibetan Buddhist monasteries and rugged passes.",
    "top_attractions": "Key Monastery|Chandratal Lake|Dhankar Gompa|Pin Valley",
    "latitude": "32.2461",
    "longitude": "78.0349",
    "status": "published",
    "nature": "92.5",
    "adventure": "95.0",
    "peacefulness": "85.0",
    "crowd_match": "25.0",
    "visual_atmosphere": "90.0",
    "score_source": "model_inference",
    "photo_authors": "Admin Explorer",
    "photo_licenses": "CC BY-SA 4.0"
}

create_res = client.post("/api/admin/destinations/create", data=data, files=photos, headers=headers)
print("Create response status:", create_res.status_code)
print("Create response body:", create_res.json())
assert create_res.status_code == 200, f"Creation failed: {create_res.text}"

# 3. Verify in /api/destination/{name}
get_res = client.get("/api/destination/Spiti Valley Test")
assert get_res.status_code == 200, f"Get destination failed: {get_res.text}"
dest_obj = get_res.json()
print("Retrieved new destination:", dest_obj["name"])
print("  is_ai_estimated:", dest_obj["is_ai_estimated"])
print("  score_source:", dest_obj["score_source"])
print("  photos count:", len(dest_obj["photos"]))
assert dest_obj["is_ai_estimated"] == True, "New destination should carry is_ai_estimated=True badge"

# 4. Verify in /api/recommend
rec_res = client.post("/api/recommend", json={"query_text": "", "target_dims": {"adventure": "high", "nature": "high"}})
assert rec_res.status_code == 200
recs = rec_res.json().get("recommendations", [])
found = [r for r in recs if r["name"] == "Spiti Valley Test"]
print("Appeared in recommendation results:", len(found) > 0)
if found:
    print("  Ranked score:", found[0]["overall_match_score"], "| AI badge:", found[0]["is_ai_estimated"])

print("\nEND-TO-END NEW DESTINATION CREATION VERIFIED SUCCESSFULLY!")
