import sqlite3
import bcrypt
from datetime import datetime

def hash_pw(pw: str) -> str:
    salt = bcrypt.gensalt(rounds=12)
    return bcrypt.hashpw(pw.encode('utf-8'), salt).decode('utf-8')

conn = sqlite3.connect('vibetrip.db')
cursor = conn.cursor()

# Accounts to seed
demo_tourists = [
    {
        "name": "Aarav Sharma",
        "email": "tourist.demo@vibetrip.com",
        "password": "DemoTourist2026!",
        "role": "tourist",
        "home_city": "Mumbai",
        "bio": "Solo backpacker & travel photographer exploring serene peaks and lively coastal towns.",
        "interest_tags": "trekking,cafes,sunsets,photography,backpacking",
        "visibility": "public"
    },
    {
        "name": "Priya Sen",
        "email": "priya.tourist@vibetrip.com",
        "password": "DemoTourist2026!",
        "role": "tourist",
        "home_city": "Bengaluru",
        "bio": "Culture buff, foodie, and architecture enthusiast seeking authentic hidden spots across India.",
        "interest_tags": "food,heritage,culture,museums,wellness",
        "visibility": "public"
    }
]

demo_locals = [
    {
        "name": "Rohan D'Souza",
        "email": "rohan.goa@vibetrip.com",
        "password": "DemoLocal2026!",
        "role": "local",
        "home_city": "Goa",
        "bio": "Born and raised in North Goa. Surfer, coastal trail guide, and advocate for sustainable beach tourism.",
        "interest_tags": "surfing,hidden_beaches,seafood,kayaking,nightlife",
        "visibility": "public",
        "submissions": [
            {
                "destination": "Goa",
                "name": "Kakolem Secret Lagoon Beach",
                "category": "viewpoint",
                "latitude": 15.088,
                "longitude": 73.962,
                "description": "Hidden cove surrounded by cliffs with a freshwater waterfall emptying directly onto the beach.",
                "contact_info": "@rohan_goa_trails",
                "source": "local_community",
                "status": "approved",
                "crowd_hint": "Very quiet on weekdays, magical sunset photography."
            },
            {
                "destination": "Goa",
                "name": "Assagao Forest Heritage Bakery",
                "category": "cafe",
                "latitude": 15.590,
                "longitude": 73.778,
                "description": "Artisanal sourdough and organic poi bread baked in an old Portuguese clay oven amidst lush canopy.",
                "contact_info": "+91 98221 44552",
                "source": "local_community",
                "status": "pending",
                "crowd_hint": "Moderate morning rush, serene outdoor seating."
            }
        ]
    },
    {
        "name": "Sunita Negi",
        "email": "sunita.manali@vibetrip.com",
        "password": "DemoLocal2026!",
        "role": "local",
        "home_city": "Manali",
        "bio": "Certified mountain climber, Kullu native, and Old Manali herbal cafe curator.",
        "interest_tags": "trekking,camping,apple_orchards,himalayas,bouldering",
        "visibility": "public",
        "submissions": [
            {
                "destination": "Manali",
                "name": "Jogini Upper Ridge Secret Camp",
                "category": "viewpoint",
                "latitude": 32.268,
                "longitude": 77.195,
                "description": "Panoramic perch above Jogini Falls offering a 360-degree vista of Rohtang peaks and cedar forests.",
                "contact_info": "@sunita_himalayan_guide",
                "source": "local_community",
                "status": "approved",
                "crowd_hint": "Almost no tourists beyond the lower waterfall cascade."
            },
            {
                "destination": "Manali",
                "name": "Old Vashisht Hot Spring Herbal Tea House",
                "category": "experience",
                "latitude": 32.261,
                "longitude": 77.189,
                "description": "Traditional wooden house serving warm rhododendron tea and home-cooked Siddu by sulphur springs.",
                "contact_info": "+91 94180 88219",
                "source": "local_community",
                "status": "pending",
                "crowd_hint": "Cozy and quiet before 11 AM."
            }
        ]
    },
    {
        "name": "Vikram Rawat",
        "email": "vikram.rishikesh@vibetrip.com",
        "password": "DemoLocal2026!",
        "role": "local",
        "home_city": "Rishikesh",
        "bio": "Whitewater rafting instructor, bungee jump master, and Ganga sunrise meditation guide.",
        "interest_tags": "rafting,cliff_jumping,bungee,kayaking,meditation",
        "visibility": "public",
        "submissions": [
            {
                "destination": "Rishikesh",
                "name": "Neer Gaddu Hidden Upper Cascade",
                "category": "viewpoint",
                "latitude": 30.138,
                "longitude": 78.339,
                "description": "A secluded natural limestone pool 45 minutes hike above the commercial waterfall tier.",
                "contact_info": "@vikram_ganga_adventures",
                "source": "local_community",
                "status": "approved",
                "crowd_hint": "Pristine emerald water, best early morning before 9 AM."
            },
            {
                "destination": "Rishikesh",
                "name": "Tapovan Cliff Sunset Lookout",
                "category": "viewpoint",
                "latitude": 30.133,
                "longitude": 78.324,
                "description": "Dramatic vantage point overlooking the Lakshman Jhula suspension bridge and river rapids.",
                "contact_info": "+91 97580 31245",
                "source": "local_community",
                "status": "pending",
                "crowd_hint": "Great acoustic spot for evening Ganga breeze."
            }
        ]
    },
    {
        "name": "Amina Khan",
        "email": "amina.jaipur@vibetrip.com",
        "password": "DemoLocal2026!",
        "role": "local",
        "home_city": "Jaipur",
        "bio": "Heritage architect, block-print textile artisan, and Old Pink City street food historian.",
        "interest_tags": "heritage,street_food,handicrafts,architecture,walks",
        "visibility": "public",
        "submissions": [
            {
                "destination": "Jaipur",
                "name": "Panna Meena Kund Sunrise Stepwell View",
                "category": "viewpoint",
                "latitude": 26.985,
                "longitude": 75.856,
                "description": "16th-century geometric stepwell with stunning morning light and peaceful quiet away from Amer Fort.",
                "contact_info": "@amina_pinkcity_walks",
                "source": "local_community",
                "status": "approved",
                "crowd_hint": "Arrive at sunrise for golden hour reflection photography."
            },
            {
                "destination": "Jaipur",
                "name": "Ghat Ki Guni Heritage Garden Chai Corner",
                "category": "cafe",
                "latitude": 26.892,
                "longitude": 75.845,
                "description": "Clay kulhad masala chai served beside restored Mughal-Rajput terraced pavilions and stone jali screens.",
                "contact_info": "+91 98290 77123",
                "source": "local_community",
                "status": "pending",
                "crowd_hint": "Breezy and peaceful late afternoons."
            }
        ]
    }
]

print("Seeding Demo Accounts...")

# Process Tourists
for t in demo_tourists:
    pw_hash = hash_pw(t["password"])
    cursor.execute("SELECT id FROM users WHERE email = ?", (t["email"],))
    row = cursor.fetchone()
    if row:
        user_id = row[0]
        cursor.execute("UPDATE users SET password_hash = ?, role = ?, is_demo = 1 WHERE id = ?", (pw_hash, t["role"], user_id))
    else:
        cursor.execute(
            "INSERT INTO users (name, email, password_hash, role, is_active, is_demo, created_at) VALUES (?, ?, ?, ?, 1, 1, ?)",
            (t["name"], t["email"], pw_hash, t["role"], datetime.utcnow().isoformat())
        )
        user_id = cursor.lastrowid
    
    # Update profile
    cursor.execute("SELECT user_id FROM traveler_profiles WHERE user_id = ?", (user_id,))
    if cursor.fetchone():
        cursor.execute(
            "UPDATE traveler_profiles SET home_city = ?, bio = ?, interest_tags = ?, visibility = ? WHERE user_id = ?",
            (t["home_city"], t["bio"], t["interest_tags"], t["visibility"], user_id)
        )
    else:
        cursor.execute(
            "INSERT INTO traveler_profiles (user_id, home_city, bio, interest_tags, visibility) VALUES (?, ?, ?, ?, ?)",
            (user_id, t["home_city"], t["bio"], t["interest_tags"], t["visibility"])
        )
    print(f"  [Tourist] {t['name']} ({t['email']}) seeded successfully.")

# Process Locals and their submissions
for l in demo_locals:
    pw_hash = hash_pw(l["password"])
    cursor.execute("SELECT id FROM users WHERE email = ?", (l["email"],))
    row = cursor.fetchone()
    if row:
        user_id = row[0]
        cursor.execute("UPDATE users SET password_hash = ?, role = ?, is_demo = 1 WHERE id = ?", (pw_hash, l["role"], user_id))
    else:
        cursor.execute(
            "INSERT INTO users (name, email, password_hash, role, is_active, is_demo, created_at) VALUES (?, ?, ?, ?, 1, 1, ?)",
            (l["name"], l["email"], pw_hash, l["role"], datetime.utcnow().isoformat())
        )
        user_id = cursor.lastrowid

    # Update profile
    cursor.execute("SELECT user_id FROM traveler_profiles WHERE user_id = ?", (user_id,))
    if cursor.fetchone():
        cursor.execute(
            "UPDATE traveler_profiles SET home_city = ?, bio = ?, interest_tags = ?, visibility = ? WHERE user_id = ?",
            (l["home_city"], l["bio"], l["interest_tags"], l["visibility"], user_id)
        )
    else:
        cursor.execute(
            "INSERT INTO traveler_profiles (user_id, home_city, bio, interest_tags, visibility) VALUES (?, ?, ?, ?, ?)",
            (user_id, l["home_city"], l["bio"], l["interest_tags"], l["visibility"])
        )

    # Submissions
    for s in l["submissions"]:
        cursor.execute("SELECT id FROM local_places WHERE name = ? AND destination = ?", (s["name"], s["destination"]))
        existing_sub = cursor.fetchone()
        if existing_sub:
            cursor.execute(
                "UPDATE local_places SET submitted_by = ?, status = ?, crowd_hint = ?, contact_info = ?, description = ? WHERE id = ?",
                (user_id, s["status"], s["crowd_hint"], s["contact_info"], s["description"], existing_sub[0])
            )
        else:
            cursor.execute(
                """INSERT INTO local_places (destination, name, category, latitude, longitude, description, contact_info, source, osm_id, status, submitted_by, crowd_hint)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (s["destination"], s["name"], s["category"], s["latitude"], s["longitude"], s["description"], s["contact_info"], s["source"], "demo_sub", s["status"], user_id, s["crowd_hint"])
            )
    print(f"  [Local] {l['name']} ({l['email']}) seeded with {len(l['submissions'])} local submissions.")

conn.commit()
conn.close()
print("All demo accounts and local submissions committed.")
