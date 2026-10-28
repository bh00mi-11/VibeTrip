import sqlite3
import datetime
default_pw = "$2b$10$oeiCI5CXcFhoRpRi.BR0Ke.eaoHI67G4BkuBPGwb4ldpQM2iUS4l2"

# 33 certified guides for remaining destinations
guides_remaining = [
    ("Mohd. Tariq Qureshi", "tariq.agra@vibetrip.pro", "Agra", "Mughal Empire Architectural Historian & Taj Mahal Moonlight specialist.", "taj_mahal,mughal,monuments", "9837011221@upi", "INR 2,800/day", "ASI-AGR-4012"),
    ("Chirag Patel", "chirag.ahmedabad@vibetrip.pro", "Ahmedabad", "UNESCO Heritage Walled City Pol Specialist & Stepwell Expert.", "walled_city,heritage_walk,stepwells", "9825022334@upi", "INR 2,600/day", "GUJ-AHM-1190"),
    ("Sardar Harpreet Singh", "harpreet.amritsar@vibetrip.pro", "Amritsar", "Golden Temple Langar volunteer & Wagah Border cultural guide.", "golden_temple,wagah,punjabi_food", "9814033445@upi", "INR 2,400/day", "PB-ASR-8841"),
    ("Rana Shailendra Bisht", "shailendra.auli@vibetrip.pro", "Auli", "High-altitude Garhwal Skiing Instructor & Nanda Devi panoramic trekker.", "skiing,cable_car,nanda_devi", "9412044556@upi", "INR 3,800/day", "UTT-AUL-7723"),
    ("Farhan Siddiqui", "farhan.bhopal@vibetrip.pro", "Bhopal", "Upper Lake environmentalist & Sanchi Stupa UNESCO art interpreter.", "sanchi,upper_lake,bhimbetka", "9425055667@upi", "INR 2,500/day", "MP-BHO-3318"),
    ("Debashis Mohapatra", "debashis.bhubaneswar@vibetrip.pro", "Bhubaneswar", "Kalinga Temple Architecture & Udayagiri Caves archaeologist.", "kalinga_art,temples,dhauli", "9437066778@upi", "INR 2,700/day", "ASI-BBSR-5521"),
    ("Bhante Rahul Anand", "rahul.bodhgaya@vibetrip.pro", "Bodh Gaya", "Mahabodhi Temple Buddhist Meditation Master & Silk Route scholar.", "mahabodhi,meditation,buddhism", "9431077889@upi", "INR 2,600/day", "BHR-BDG-9901"),
    ("Bahun Khongwir", "bahun.cherrapunji@vibetrip.pro", "Cherrapunji", "Sohra Living Root Bridges trekker & Seven Sisters waterfall explorer.", "living_roots,caves,waterfalls", "9436088990@upi", "INR 3,500/day", "MEG-SOH-6612"),
    ("Biddappa Muthappa", "biddappa.coorg@vibetrip.pro", "Coorg", "Kodava Plantation Botanist & Tadiandamol Western Ghats naturalist.", "coffee,tadiandamol,kodava_culture", "9448099112@upi", "INR 3,200/day", "KAR-CRG-2287"),
    ("Devendra Nath Kaushik", "devendra.delhi@vibetrip.pro", "Delhi", "Mughal Red Fort & Lutyens Architectural Heritage Walk Leader.", "old_delhi,qutub,chandni_chowk", "9810011223@upi", "INR 3,000/day", "DEL-HER-9943"),
    ("Pandit Rameshwar Sharma", "rameshwar.haridwar@vibetrip.pro", "Haridwar", "Har Ki Pauri Ganga Aarti coordinator & Vedic astrological guide.", "ganga_aarti,mansa_devi,ashrams", "9410022334@upi", "INR 2,400/day", "UTT-HWD-5519"),
    ("Rohan Fernandez", "rohan.havelock@vibetrip.pro", "Havelock Island", "Radhanagar PADI Master Scuba Diver & Coral Bio-Preserve Naturalist.", "scuba,coral_reefs,radhanagar", "9434033445@upi", "INR 4,200/day", "AND-HAV-8832"),
    ("Syed Muzaffar Ali", "muzaffar.hyderabad@vibetrip.pro", "Hyderabad", "Nizam Dynasty Charminar & Golconda acoustic fortress historian.", "golconda,charminar,qutb_shahi", "9849044556@upi", "INR 2,900/day", "TEL-HYD-7704"),
    ("Thakur Bhati Sumer Singh", "sumer.jaisalmer@vibetrip.pro", "Jaisalmer", "Sam Sand Dunes camel caravan master & Golden Fort haveli specialist.", "sam_dunes,desert_fort,patwon", "9829055667@upi", "INR 3,200/day", "RAJ-JAI-3391"),
    ("Murugan Nadar", "murugan.kanyakumari@vibetrip.pro", "Kanyakumari", "Three Seas Confluence navigator & Vivekananda Rock memorial historian.", "confluence,vivekananda,sunsets", "9443066778@upi", "INR 2,500/day", "TN-KAN-1182"),
    ("Captain Xavier D'Cruz", "xavier.kochi@vibetrip.pro", "Kochi", "Fort Kochi spice route sailor & Chinese fishing nets maritime guide.", "fort_kochi,mattancherry,spices", "9447077889@upi", "INR 3,000/day", "KER-KOC-4410"),
    ("Subrata Banerjee", "subrata.kolkata@vibetrip.pro", "Kolkata", "Colonial Heritage & Hooghly River ghats literature walk lead.", "victoria_memorial,howrah,kolkata_arts", "9830088990@upi", "INR 2,800/day", "WB-KOL-7751"),
    ("Sundara Ramanathan", "sundara.madurai@vibetrip.pro", "Madurai", "Meenakshi Amman Temple Dravidian architecture & sculpture scholar.", "meenakshi_temple,nayak_palace,sculptures", "9442099112@upi", "INR 2,600/day", "TN-MAD-9932"),
    ("Nitin More", "nitin.mahabaleshwar@vibetrip.pro", "Mahabaleshwar", "Sahyadri Strawberry belt botanist & Pratapgad Shivaji fort guide.", "strawberry_farms,pratapgad,viewpoints", "9822011223@upi", "INR 2,800/day", "MH-MHB-5541"),
    ("Arulmozhi Varman", "arulmozhi.mahabalipuram@vibetrip.pro", "Mahabalipuram", "UNESCO Shore Temple monolith carver & Pallava cave relief expert.", "shore_temple,pancha_rathas,sculpture", "9444022334@upi", "INR 3,000/day", "ASI-MHB-8819"),
    ("Rishi Kulkarni", "rishi.mumbai@vibetrip.pro", "Mumbai", "Art Deco Marine Drive & Victorian Fort architectural specialist.", "art_deco,marine_drive,colaba", "9820033445@upi", "INR 3,500/day", "MH-MUM-6623"),
    ("Prashanth Urs", "prashanth.mysore@vibetrip.pro", "Mysore", "Wodeyar Palace royal historian & Devaraja silk and spice curator.", "mysore_palace,chamundi,silk_sandalwood", "9845044556@upi", "INR 2,700/day", "KAR-MYS-3312"),
    ("Jaganathan Bellie", "jagan.ooty@vibetrip.pro", "Ooty", "Nilgiri Mountain Railway historian & Toda tribal culture naturalist.", "toy_train,doddabetta,tea_factory", "9443055667@upi", "INR 3,000/day", "TN-OOT-4421"),
    ("Dharmendra Chouhan", "dharmendra.pachmarhi@vibetrip.pro", "Pachmarhi", "Satpura Tiger Reserve ravine trekker & Pandav Caves guide.", "satpura,dhoopgarh,pandav_caves", "9424066778@upi", "INR 2,800/day", "MP-PAC-7711"),
    ("Pierre Coumar", "pierre.pondicherry@vibetrip.pro", "Pondicherry", "French Quarter heritage preservationist & Auroville eco guide.", "white_town,auroville,french_heritage", "9443077889@upi", "INR 3,200/day", "PDY-WHI-9921"),
    ("Alok Biswas", "alok.portblair@vibetrip.pro", "Port Blair", "Cellular Jail national memorial historian & Ross Island cruiser.", "cellular_jail,ross_island,chidiya_tapu", "9434088990@upi", "INR 3,400/day", "AND-PTB-2204"),
    ("Tanmay Deshpande", "tanmay.pune@vibetrip.pro", "Pune", "Maratha Empire Sinhagad trek lead & Shaniwar Wada historian.", "sinhagad,shaniwar_wada,agakhan", "9823099112@upi", "INR 2,800/day", "MH-PUN-1142"),
    ("Kishore Vaghela", "kishore.kutch@vibetrip.pro", "Rann of Kutch", "White Desert salt flats naturalist & Rogan art village ambassador.", "white_rann,dhordo,kala_dungar", "9825011223@upi", "INR 3,500/day", "GUJ-RAN-8891"),
    ("Daphishisha Lyngdoh", "daphi.shillong@vibetrip.pro", "Shillong", "Khasi Hills indigenous music specialist & Elephant Falls naturalist.", "ward_lake,shillong_peak,khasi_culture", "9436022334@upi", "INR 3,000/day", "MEG-SHL-5510"),
    ("Tsering Bodh", "tsering.spiti@vibetrip.pro", "Spiti Valley Test", "High Altitude Key Monastery & Chandratal glacial trek master.", "key_monastery,kaza,chandratal", "9418033445@upi", "INR 4,500/day", "HP-SPI-7782"),
    ("Rawat Mahendra Sisodia", "mahendra.udaipur@vibetrip.pro", "Udaipur", "Lake Pichola boat captain & City Palace Mewar royal court historian.", "city_palace,pichola,jagmandir", "9829044556@upi", "INR 3,500/day", "RAJ-UDA-4402"),
    ("Pandit Girish Trivedi", "girish.ujjain@vibetrip.pro", "Ujjain", "Mahakaleshwar Jyotirlinga Bhasma Aarti & Shipra ghat Sanskritist.", "mahakaleshwar,shipra,jyotirlinga", "9425055667@upi", "INR 2,500/day", "MP-UJJ-9931"),
    ("Manoj Kurup", "manoj.wayanad@vibetrip.pro", "Wayanad", "Edakkal prehistoric cave carver & Chembra Heart Lake trek lead.", "edakkal,chembra_peak,bamboo_forest", "9447066778@upi", "INR 3,200/day", "KER-WAY-3392")
]

conn = sqlite3.connect("vibetrip.db")
cursor = conn.cursor()
now_iso = datetime.datetime.now(datetime.timezone.utc).isoformat()

print(f"Seeding {len(guides_remaining)} additional certified guides for 100% destination coverage...")

added_count = 0
for name, email, city, bio, tags, upi, rate, license in guides_remaining:
    cursor.execute("SELECT id FROM users WHERE email = ?", (email,))
    row = cursor.fetchone()
    if row:
        uid = row[0]
        cursor.execute("UPDATE users SET name=?, role='guide', is_active=1, is_demo=1 WHERE id=?", (name, uid))
    else:
        cursor.execute("INSERT INTO users (name, email, password_hash, role, is_active, is_demo, created_at) VALUES (?, ?, ?, 'guide', 1, 1, ?)",
                       (name, email, default_pw, now_iso))
        uid = cursor.lastrowid
    
    contact_payout = f"Direct UPI: {upi} | Daily Rate: {rate} | License: {license}"
    cursor.execute("SELECT user_id FROM traveler_profiles WHERE user_id = ?", (uid,))
    if cursor.fetchone():
        cursor.execute("UPDATE traveler_profiles SET home_city=?, bio=?, interest_tags=?, visibility='public', contact_info=? WHERE user_id=?",
                       (city, f"{bio} [Licensed Guide - Direct Payout Enabled]", tags, contact_payout, uid))
    else:
        cursor.execute("INSERT INTO traveler_profiles (user_id, home_city, bio, interest_tags, visibility, contact_info) VALUES (?, ?, ?, ?, 'public', ?)",
                       (uid, city, f"{bio} [Licensed Guide - Direct Payout Enabled]", tags, contact_payout))
    added_count += 1

conn.commit()
conn.close()
print(f"Successfully configured and seeded {added_count} certified guides into database.")
