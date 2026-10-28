import sqlite3

conn = sqlite3.connect('vibetrip.db')
c = conn.cursor()

# Set realistic contact info for both demo accounts
c.execute("UPDATE traveler_profiles SET contact_info = '+91 98221 44552 (WhatsApp) | IG: @rohan_goa_trails' WHERE user_id = 23")
c.execute("UPDATE traveler_profiles SET contact_info = '+91 98191 00234 (WhatsApp) | IG: @aarav_travels' WHERE user_id = 21")

# Add Aarav Sharma (Tourist) as active traveler looking for buddies in Goa
c.execute("""
INSERT OR REPLACE INTO buddy_interests 
(id, user_id, destination, travel_start, travel_end, pref_nature, pref_adventure, pref_peacefulness, pref_crowd_match, pref_visual_atmosphere, interest_tags, note, active, created_at)
VALUES 
(101, 21, 'Goa', '2026-11-15', '2026-11-25', 80.0, 85.0, 70.0, 60.0, 85.0, 'scuba, beach trekking, sunset photography', 'Solo traveler visiting Goa for water sports and exploring secluded beaches.', 1, datetime('now'))
""")

# Also add Rohan D'Souza (Local) in Goa so tourists can see and connect with him
c.execute("""
INSERT OR REPLACE INTO buddy_interests 
(id, user_id, destination, travel_start, travel_end, pref_nature, pref_adventure, pref_peacefulness, pref_crowd_match, pref_visual_atmosphere, interest_tags, note, active, created_at)
VALUES 
(102, 23, 'Goa', '2026-11-01', '2026-12-31', 85.0, 90.0, 75.0, 50.0, 90.0, 'surfing, hidden beaches, kayaking', 'Goa local host & guide available for coastal treks and surfing lessons.', 1, datetime('now'))
""")

# Add a pending connection request from Aarav Sharma (Tourist, ID 21) to Rohan D'Souza (Goa Local, ID 23)
c.execute("""
INSERT OR REPLACE INTO buddy_requests 
(id, from_user, to_user, destination, message, status, created_at)
VALUES 
(1, 21, 23, 'Goa', 'Hey Rohan! Saw you are a local guide in Goa. Would love to join you on a coastal kayak or secret beach hike when I visit next month!', 'pending', datetime('now'))
""")

conn.commit()
conn.close()
print("Successfully seeded Goa demo buddy request & contact details!")
