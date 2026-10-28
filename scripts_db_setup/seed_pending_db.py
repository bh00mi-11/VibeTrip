import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "vibetrip.db")
print("Connecting to:", DB_PATH)
conn = sqlite3.connect(DB_PATH)
c = conn.cursor()

# Check user table
c.execute("SELECT id, name, role FROM users WHERE role = 'local' LIMIT 1")
local_user = c.fetchone()
if not local_user:
    c.execute("SELECT id, name, role FROM users LIMIT 1")
    local_user = c.fetchone()

user_id = local_user[0] if local_user else None
print(f"Using user_id: {user_id}")

# Insert pending submissions
pending_samples = [
    ("Shillong", "Laitlum Canyons Sunset Point", "viewpoint", 25.4320, 91.8900, "Local guide recommended viewpoint overlooking the deep gorges of Meghalaya, best visited before 5 PM."),
    ("Rishikesh", "Ganga Riverside Organic Cafe", "cafe", 30.1320, 78.3250, "Quiet rooftop cafe right above Laxman Jhula serving vegan meals, fresh kombucha, and mountain views."),
    ("Manali", "Old Manali Woodfired Pizzeria & Bakery", "food", 32.2510, 77.1850, "Historic alpine cafe famous for sourdough pizzas, walnut tarts, and live acoustic music by local artists."),
    ("Goa", "Chorao Island Birdwatching Sanctuary Trail", "attraction", 15.5200, 73.8600, "Secret mangrove boat trail with rare migratory birds, away from crowded tourist beaches."),
    ("Jaipur", "Nahargarh Sunset Cycling & Heritage Trail", "experience", 26.9370, 75.8150, "Early morning cycling group ride through the Aravalli hills up to Nahargarh Fort with sunrise chai.")
]

added = 0
for dest, name, cat, lat, lon, desc in pending_samples:
    c.execute("SELECT id FROM local_places WHERE name = ? AND destination = ?", (name, dest))
    if not c.fetchone():
        c.execute("""
            INSERT INTO local_places (destination, name, category, latitude, longitude, description, status, submitted_by)
            VALUES (?, ?, ?, ?, ?, ?, 'pending', ?)
        """, (dest, name, cat, lat, lon, desc, user_id))
        added += 1

conn.commit()
print(f"Added {added} pending contributor submissions.")

c.execute("SELECT id, destination, name, category, status FROM local_places WHERE status = 'pending'")
pending = c.fetchall()
print("Current pending queue:")
for p in pending:
    print(p)

conn.close()
