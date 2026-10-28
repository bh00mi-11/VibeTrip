import sqlite3
import bcrypt
from datetime import datetime

def hash_pw(pw: str) -> str:
    salt = bcrypt.gensalt(rounds=10) # 10 rounds for speedy bulk insertion
    return bcrypt.hashpw(pw.encode('utf-8'), salt).decode('utf-8')

conn = sqlite3.connect('vibetrip.db')
cursor = conn.cursor()

# Ensure we have our existing users and expand to:
# 20 Tourists
# 20 Locals
# 20 Licensed Guides (with direct payout / UPI / booking fee config)

# 1. 20 Tourists
tourists_data = [
    ("Aarav Sharma", "tourist.demo@vibetrip.com", "Mumbai", "Solo backpacker & photographer exploring serene peaks & coastal towns.", "trekking,cafes,sunsets"),
    ("Priya Sen", "priya.tourist@vibetrip.com", "Bengaluru", "Culture buff, foodie, and architecture enthusiast seeking authentic hidden spots.", "food,heritage,culture"),
    ("Ananya Sen", "ananya.demo@vibetrip.internal", "Kolkata", "Art student & heritage traveler documenting traditional crafts.", "art,history,walks"),
    ("Rohan Mehta", "rohan.demo@vibetrip.internal", "Delhi", "Outdoor enthusiast passionate about high-altitude trekking.", "trekking,camping,mountains"),
    ("Pooja Verma", "pooja.demo@vibetrip.internal", "Pune", "Yoga practitioner and wellness seeker exploring peaceful ashrams.", "yoga,wellness,peace"),
    ("Kabir Das", "kabir.demo@vibetrip.internal", "Jaipur", "Desert explorer and wildlife photographer following bird sanctuaries.", "wildlife,safari,photography"),
    ("Meera Nair", "meera.demo@vibetrip.internal", "Kochi", "Backwaters explorer and coastal spice trail researcher.", "backwaters,food,nature"),
    ("Vikram Rathore", "vikram.demo@vibetrip.internal", "Udaipur", "Fort and palace heritage architecture lover.", "architecture,castles,history"),
    ("Sneha Kulkarni", "sneha.demo@vibetrip.internal", "Mumbai", "Weekend road tripper and cafe reviewer.", "cafes,scenic_drives,views"),
    ("Arjun Patel", "arjun.demo@vibetrip.internal", "Ahmedabad", "Adventure camper exploring river valleys and canyons.", "adventure,camping,rafting"),
    ("Divya Roy", "divya.demo@vibetrip.internal", "Guwahati", "Northeast rainforest and living root bridges explorer.", "rainforest,bridges,monsoon"),
    ("Ishaan Chawla", "ishaan.demo@vibetrip.internal", "Chandigarh", "Mountain biker conquering Himalayan mountain passes.", "biking,himalayas,adrenaline"),
    ("Kavya Reddy", "kavya.demo@vibetrip.internal", "Hyderabad", "Heritage walk organizer and food historian.", "biryani,walks,monuments"),
    ("Tenzin Norbu", "tenzin.demo@vibetrip.internal", "Dharamshala", "High mountain monastery visitor and Buddhist culture writer.", "monasteries,meditation,peace"),
    ("Farhan Ali", "farhan.demo@vibetrip.internal", "Lucknow", "Architectural sketcher exploring Mughal and Awadhi monuments.", "sketches,history,food"),
    ("Neha Joshi", "neha.demo@vibetrip.internal", "Dehradun", "Valley hiker and wild flower enthusiast.", "wildflowers,valleys,hiking"),
    ("Tara Sen", "tara.demo@vibetrip.internal", "Shillong", "Pine forest camper and waterfall photographer.", "waterfalls,clouds,music"),
    ("Dev Kapoor", "dev.demo@vibetrip.internal", "Indore", "Street food fanatic and weekend temple trail traveler.", "food,temples,culture"),
    ("Simran Gill", "simran.tourist@vibetrip.com", "Amritsar", "Heritage culinary explorer and farm retreat visitor.", "culinary,farms,culture"),
    ("Aditya Malhotra", "aditya.tourist@vibetrip.com", "Gurgaon", "Scuba diving certified enthusiast and marine lover.", "scuba,marine,beaches")
]

# 2. 20 Locals (Community Spot contributors)
locals_data = [
    ("Rohan D'Souza", "rohan.goa@vibetrip.com", "Goa", "North Goa surfer & coastal guide sharing hidden coves and cliff paths.", "surfing,coastal,cafes"),
    ("Sunita Negi", "sunita.manali@vibetrip.com", "Manali", "Old Manali local, apple orchard keeper, and forest trail guardian.", "orchards,cedar,himalayas"),
    ("Vikram Rawat", "vikram.rishikesh@vibetrip.com", "Rishikesh", "Tapovan native, rafting pilot, and sacred Ganga ghat guide.", "ganga,rafting,waterfalls"),
    ("Amina Khan", "amina.jaipur@vibetrip.com", "Jaipur", "Pink City textile artisan and hidden stepwell historian.", "stepwells,textiles,bazaars"),
    ("Tsering Angmo", "tsering.leh@vibetrip.com", "Leh Ladakh", "Ladakhi organic farm host and high-altitude pass storyteller.", "ladakh,homestays,monasteries"),
    ("Ganesh Bhatt", "ganesh.varanasi@vibetrip.com", "Varanasi", "Old Ghat boatman and silk weaving quarter insider.", "ghats,morning_boat,silk"),
    ("Deepak Sharma", "deepak.shimla@vibetrip.com", "Shimla", "Heritage pine trail walker and colonial history archivist.", "pine_woods,colonial,heritage"),
    ("Lakshmi Menon", "lakshmi.munnar@vibetrip.com", "Munnar", "Tea plantation resident and secret cardamom forest guide.", "tea_gardens,mist,wildlife"),
    ("Karma Bhutia", "karma.gangtok@vibetrip.com", "Gangtok", "Sikkimese mountain storyteller and orchid sanctuary keeper.", "orchids,kanchenjunga,trails"),
    ("Santosh Pujari", "santosh.hampi@vibetrip.com", "Hampi", "Tungabhadra boulder artist and Vijayanagara ruins custodian.", "boulders,ruins,sunset_hills"),
    ("Biren Borah", "biren.kaziranga@vibetrip.com", "Kaziranga", "Brahmaputra floodplain native and rhino conservationist.", "wildlife,rhinos,river"),
    ("Kishore Varma", "kishore.alleppey@vibetrip.com", "Alleppey", "Backwater canoeist and traditional village fish curry chef.", "canoeing,lagoons,toddy"),
    ("Jitendra Singh", "jitendra.jodhpur@vibetrip.com", "Jodhpur", "Blue City maze runner and Mehrangarh rampart guide.", "blue_city,crafts,rooftops"),
    ("Pema Dorje", "pema.tawang@vibetrip.com", "Tawang", "Monpa tribal historian and high lake naturalist.", "glacier_lakes,monpa,monastery"),
    ("Nandini Shenoy", "nandini.gokarna@vibetrip.com", "Gokarna", "Kudle beach shack host and cliff walk coordinator.", "cliffs,quiet_beaches,tides"),
    ("Suraj Tamang", "suraj.darjeeling@vibetrip.com", "Darjeeling", "Toy train route chronicler and artisan tea taster.", "tea,steam_train,sunrises"),
    ("Mohan Das", "mohan.puri@vibetrip.com", "Puri", "Chilika dolphin boatman and sand art artisan.", "chilika,dolphins,beaches"),
    ("Kailash Chand", "kailash.pushkar@vibetrip.com", "Pushkar", "Sacred lake local and sunset sand dune organizer.", "dunes,sacred_lake,rose_fields"),
    ("Nawazish Sheikh", "nawazish.srinagar@vibetrip.com", "Srinagar", "Dal Lake floating garden cultivator and walnut wood carver.", "shikara,floating_market,carvings"),
    ("Geeta Bai", "geeta.khajuraho@vibetrip.com", "Khajuraho", "Bundelkhand terracotta artist and temple sculpture guide.", "sculptures,art,rural_walks")
]

# 3. 20 Professional Guides (with Direct Money/Payout & License details)
guides_data = [
    ("Captain Rajesh Kadam", "rajesh.guide@vibetrip.pro", "Goa", "Govt. Certified Marine & Island Yacht Captain. 14 years maritime safety experience.", "yacht,scuba,dolphin_safari", "9422011223@upi", "INR 3,500/day", "GOA-MAR-8821"),
    ("Subedar Balwant Singh", "balwant.guide@vibetrip.pro", "Manali", "Retiree Himalayan Mountaineering Institute instructor. Alpine expedition lead.", "ice_climbing,rohtang_pass,survival", "9816044551@upi", "INR 4,000/day", "HMI-ALP-3312"),
    ("Acharya Devendra Shastri", "devendra.guide@vibetrip.pro", "Rishikesh", "Certified Yoga Acharya & Ganga River Rafting License A-Grade.", "whitewater,ashrams,sound_healing", "9760088772@upi", "INR 2,800/day", "UTT-RAFT-1092"),
    ("Maharaj Vikramaditya Rathore", "vikramaditya.guide@vibetrip.pro", "Jaipur", "Rajasthan Tourism Dept Gold Badge Guide & Amber Fort historian.", "royal_palaces,astronomy,stepwells", "9829033441@upi", "INR 3,200/day", "RAJ-TOU-7740"),
    ("Stanzin Phuntsog", "stanzin.guide@vibetrip.pro", "Leh Ladakh", "Chadar Frozen River Trek Specialist & High Altitude Medic.", "chadar_trek,nubra,pangong", "9419177883@upi", "INR 5,000/day", "LAD-TREK-0044"),
    ("Pandit Vinod Tripathi", "vinod.guide@vibetrip.pro", "Varanasi", "Archaeological Survey of India accredited Sanskrit scholar & Ghat guide.", "kashi_vishwanath,subah_banaras", "9450011994@upi", "INR 2,500/day", "ASI-VAR-9912"),
    ("Capt. Arvind Sood", "arvind.guide@vibetrip.pro", "Shimla", "State Forest Dept Botanical Expedition Guide & Snowline trekker.", "snowline,birdwatching,flora", "9817022331@upi", "INR 3,000/day", "HP-FOR-4419"),
    ("George Varghese", "george.guide@vibetrip.pro", "Munnar", "Western Ghats Endemic Birding Naturalist & Tea Trail Leader.", "anamudi,nilgiri_tahr,birding", "9447055662@upi", "INR 3,500/day", "KER-NAT-6601"),
    ("Sonam Wangchuk Lepcha", "sonam.guide@vibetrip.pro", "Gangtok", "Kanchenjunga Biosphere Reserve Mountaineer & Orchid expert.", "rhododendron,base_camp,peaks", "9434088991@upi", "INR 4,500/day", "SIK-BIO-2299"),
    ("K. Ranganath", "ranganath.guide@vibetrip.pro", "Hampi", "UNESCO World Heritage Site Master Guide & Epigraphist.", "virupaksha,vijayanagara,epigraphy", "9845011442@upi", "INR 3,000/day", "ASI-HAM-5520"),
    ("Bipul Hazarika", "bipul.guide@vibetrip.pro", "Kaziranga", "Chief Jeep Safari Tracker & Tiger Reserve Forest Ranger (Retd.).", "elephant_safari,big_five,birds", "9435066773@upi", "INR 4,200/day", "ASM-FOR-8831"),
    ("Capt. Thomas Mathew", "thomas.guide@vibetrip.pro", "Alleppey", "Govt. Licensed Kettuvallam Houseboat Master & Vembanad Lake Navigator.", "houseboat,sunset_cruise,culinary", "9448099114@upi", "INR 4,000/day", "KER-NAV-1188"),
    ("Rawal Bhanwar Singh", "bhanwar.guide@vibetrip.pro", "Jodhpur", "Desert Survivalist & Mehrangarh Museum Trust Certified Guide.", "bap_boulders,bishnoi_safari,forts", "9828055663@upi", "INR 3,200/day", "RAJ-DES-4411"),
    ("Dorjee Khandu", "dorjee.guide@vibetrip.pro", "Tawang", "Sela Pass High-Altitude Survival Guide & Indo-Tibetan Heritage expert.", "sela_pass,madhuri_lake,monasteries", "9436022885@upi", "INR 4,800/day", "ARN-HIG-7733"),
    ("Venkatesh Naik", "venkatesh.guide@vibetrip.pro", "Gokarna", "Arabian Sea Life Guard & Coastal Cliff Trekking Master.", "beach_trek,dolphins,snorkeling", "9844033221@upi", "INR 2,800/day", "KAR-MAR-9902"),
    ("Prem Tamang", "prem.guide@vibetrip.pro", "Darjeeling", "Singalila Ridge & Sandakphu Master Trekker. 200+ summits.", "sandakphu,everest_view,rhododendron", "9434199224@upi", "INR 4,000/day", "WB-TREK-6677"),
    ("Bikram Das", "bikram.guide@vibetrip.pro", "Puri", "Chilika Ramsar Wetland Guide & Irrawaddy Dolphin Sanctuary Pilot.", "chilika_lake,migratory_birds,islands", "9437011445@upi", "INR 3,000/day", "ODI-RAM-3319"),
    ("Rawat Kalu Singh", "kalu.guide@vibetrip.pro", "Pushkar", "Great Thar Desert Camel Expedition Lead & Astronomy Camp Guide.", "camel_caravan,desert_astronomy,dunes", "9829144882@upi", "INR 3,200/day", "RAJ-THAR-5501"),
    ("Mir Ghulam Hassan", "ghulam.guide@vibetrip.pro", "Srinagar", "Kashmir Great Lakes Trek Leader & Alpine Trout Fishing Specialist.", "great_lakes,apharwat_skiing,shikara", "9419033112@upi", "INR 4,500/day", "JK-ALP-8890"),
    ("Virendra Dixit", "virendra.guide@vibetrip.pro", "Khajuraho", "UNESCO Certified Western Group of Temples Scholar & Historian.", "kandariya_mahadev,erotic_art,chandelas", "9425088113@upi", "INR 2,800/day", "ASI-KHA-1104")
]

default_pw = "DemoPass2026!"
pw_hash = hash_pw(default_pw)
now_iso = datetime.utcnow().isoformat()

print("Seeding 20 Tourists...")
for name, email, city, bio, tags in tourists_data:
    cursor.execute("SELECT id FROM users WHERE email = ?", (email,))
    row = cursor.fetchone()
    if row:
        uid = row[0]
        cursor.execute("UPDATE users SET name=?, role='tourist', is_active=1, is_demo=1 WHERE id=?", (name, uid))
    else:
        cursor.execute("INSERT INTO users (name, email, password_hash, role, is_active, is_demo, created_at) VALUES (?, ?, ?, 'tourist', 1, 1, ?)",
                       (name, email, pw_hash, now_iso))
        uid = cursor.lastrowid
    
    cursor.execute("SELECT user_id FROM traveler_profiles WHERE user_id = ?", (uid,))
    if cursor.fetchone():
        cursor.execute("UPDATE traveler_profiles SET home_city=?, bio=?, interest_tags=?, visibility='public' WHERE user_id=?", (city, bio, tags, uid))
    else:
        cursor.execute("INSERT INTO traveler_profiles (user_id, home_city, bio, interest_tags, visibility) VALUES (?, ?, ?, ?, 'public')",
                       (uid, city, bio, tags))

print("Seeding 20 Locals...")
for name, email, city, bio, tags in locals_data:
    cursor.execute("SELECT id FROM users WHERE email = ?", (email,))
    row = cursor.fetchone()
    if row:
        uid = row[0]
        cursor.execute("UPDATE users SET name=?, role='local', is_active=1, is_demo=1 WHERE id=?", (name, uid))
    else:
        cursor.execute("INSERT INTO users (name, email, password_hash, role, is_active, is_demo, created_at) VALUES (?, ?, ?, 'local', 1, 1, ?)",
                       (name, email, pw_hash, now_iso))
        uid = cursor.lastrowid
    
    cursor.execute("SELECT user_id FROM traveler_profiles WHERE user_id = ?", (uid,))
    if cursor.fetchone():
        cursor.execute("UPDATE traveler_profiles SET home_city=?, bio=?, interest_tags=?, visibility='public' WHERE user_id=?", (city, bio, tags, uid))
    else:
        cursor.execute("INSERT INTO traveler_profiles (user_id, home_city, bio, interest_tags, visibility) VALUES (?, ?, ?, ?, 'public')",
                       (uid, city, bio, tags))

print("Seeding 20 Professional Guides with direct payout & license info...")
for name, email, city, bio, tags, upi, rate, license in guides_data:
    cursor.execute("SELECT id FROM users WHERE email = ?", (email,))
    row = cursor.fetchone()
    if row:
        uid = row[0]
        cursor.execute("UPDATE users SET name=?, role='guide', is_active=1, is_demo=1 WHERE id=?", (name, uid))
    else:
        cursor.execute("INSERT INTO users (name, email, password_hash, role, is_active, is_demo, created_at) VALUES (?, ?, ?, 'guide', 1, 1, ?)",
                       (name, email, pw_hash, now_iso))
        uid = cursor.lastrowid
    
    contact_payout = f"Direct UPI: {upi} | Daily Rate: {rate} | License: {license}"
    cursor.execute("SELECT user_id FROM traveler_profiles WHERE user_id = ?", (uid,))
    if cursor.fetchone():
        cursor.execute("UPDATE traveler_profiles SET home_city=?, bio=?, interest_tags=?, visibility='public', contact_info=? WHERE user_id=?",
                       (city, f"{bio} [Licensed Guide - Direct Payout Enabled]", tags, contact_payout, uid))
    else:
        cursor.execute("INSERT INTO traveler_profiles (user_id, home_city, bio, interest_tags, visibility, contact_info) VALUES (?, ?, ?, ?, 'public', ?)",
                       (uid, city, f"{bio} [Licensed Guide - Direct Payout Enabled]", tags, contact_payout))

conn.commit()

# Report totals
cursor.execute("SELECT role, COUNT(*) FROM users GROUP BY role")
print("Updated database user summary:", cursor.fetchall())
conn.close()
