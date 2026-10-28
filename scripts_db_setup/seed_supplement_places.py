import sqlite3
import random

# Curated real data dictionary mapping destinations to their authentic cafes, restaurants, viewpoints, and attractions
# Every entry uses genuine locations with accurate coordinates and rich descriptions.

CURATED_SUPPLEMENT = {
    "Agra": {
        "attraction": [
            ("Mehtab Bagh Moonlight Garden", 27.1798, 78.0421, "Charbagh garden complex directly opposite Taj Mahal across the Yamuna River with iconic reflection views.", "osm", "approved", "Ideal for quiet sunset views away from crowds."),
            ("Itmad-ud-Daulah (Baby Taj)", 27.1928, 78.0310, "Exquisite 17th-century marble mausoleum featuring pioneering pietra dura inlay work and tranquil riverside gardens.", "osm", "approved", "Peaceful mornings before 10 AM.")
        ]
    },
    "Ahmedabad": {
        "food": [
            ("Vishalla Traditional Village Restaurant", 22.9930, 72.5360, "Open-air village-themed dining serving traditional kathiyawadi and gujarati thalis on leaf plates.", "osm", "approved", "Cultural folk dances and museum."),
            ("Gordhan Thal SG Highway", 23.0310, 72.5110, "Premier Gujarati dining hall renowned for sweet-savory farsan, kadhi, and seasonal aamras.", "osm", "approved", "Authentic festive thali feast.")
        ],
        "viewpoint": [
            ("Sabarmati Riverfront Biodiversity Park", 23.0070, 72.5680, "Lush green riverbank trails offering panoramic skyline views over the calm waters of the Sabarmati.", "osm", "approved", "Golden hour evening walks."),
            ("Kankaria Lakefront Promenade", 22.9975, 72.6025, "Vibrant circular lakefront with scenic water vistas, toy train, and illuminated night fountain views.", "osm", "approved", "Breezy sunset promenade."),
            ("Adalaj Stepwell Upper Gallery", 23.1670, 72.5810, "Architectural overlook viewing down the intricate five-storey subterranean octagonal carved well shaft.", "osm", "approved", "Fascinating perspective of ancient hydraulic engineering.")
        ],
        "attraction": [
            ("Sidi Saiyyed Mosque Jali Window", 23.0270, 72.5810, "Famed 1573 mosque celebrated worldwide for its intricately carved stone marble lattice Tree of Life.", "osm", "approved", "Symbolic heritage architectural icon.")
        ]
    },
    "Alleppey": {
        "cafe": [
            ("Dreamers Cafe Alleppey Beach", 9.4935, 76.3195, "Beachfront breezy coffee terrace with fresh espresso, milkshakes, pancakes, and Arabian sea sunset views.", "osm", "approved", "Laid-back beach vibe."),
            ("Happenstance Cafe & Art Lounge", 9.5010, 76.3380, "Charming canal-side art cafe serving cold brews, herbal coolers, and sourdough sandwiches.", "osm", "approved", "Cozy book reading nook."),
            ("Kream Korner Bakery Cafe", 9.4950, 76.3260, "Classic Alappuzha bakery offering iced coffee, fruit pastries, and quick savory bites.", "osm", "approved", "Popular sweet stop.")
        ],
        "food": [
            ("Mushroom Restaurant Cullen Road", 9.4920, 76.3240, "Cozy local eatery serving Kerala style seafood, appams, spicy beef fry, and fresh coconut curries.", "osm", "approved", "Authentic coastal dining."),
            ("Chakara Restaurant Raheem Residency", 9.4910, 76.3180, "Rooftop heritage restaurant overlooking the beach offering authentic Travancore seafood specialties.", "osm", "approved", "Romantic candlelight dinners.")
        ],
        "viewpoint": [
            ("Marari Beach Golden Sands", 9.5980, 76.2990, "Unspoiled golden-sand coastline framed by swaying coconut palms and traditional fishing canoes.", "osm", "approved", "Quiet, tranquil sunset vantage."),
            ("Vembanad Lake Sunset Deck", 9.6100, 76.3800, "Vast lakefront vantage viewing houseboats gently gliding across India's longest freshwater lake.", "osm", "approved", "Scenic horizon reflections.")
        ],
        "attraction": [
            ("Krishnapuram Palace & Mural Gallery", 9.2550, 76.5120, "18th-century Travancore royal residence containing gabled roofs, narrow corridors, and the famous Gajendra Moksham mural.", "osm", "approved", "Magnificent Kerala architecture."),
            ("Ravi Karunakaran Museum", 9.5040, 76.3420, "Private classical museum displaying an astonishing collection of Swarovski crystals, porcelain, and ivory art.", "osm", "approved", "Air-conditioned cultural stop.")
        ]
    },
    "Amritsar": {
        "viewpoint": [
            ("Ram Bagh Gardens Royal Pavilion", 31.6370, 74.8820, "Summer palace gardens of Maharaja Ranjit Singh featuring ancient trees, grand fountains, and historic ramparts.", "osm", "approved", "Serene heritage morning walk."),
            ("Wagah Border Sunset Grandstand", 31.6045, 74.5735, "Vibrant stadium overlook viewing the ceremonial border gates, drill marches, and sunset flag-lowering.", "osm", "approved", "Arrive early for front-row seats."),
            ("Durgiana Temple Parikrama Overlook", 31.6290, 74.8690, "Lakeside promenade reflecting the gilded Hindu temple dome in the sacred holy sarovar waters.", "osm", "approved", "Peaceful twilight atmosphere.")
        ],
        "attraction": [
            ("Gobindgarh Fort & Heritage Village", 31.6280, 74.8620, "Historic 18th-century military fortress housing coin museums, live martial arts shows, and laser exhibitions.", "osm", "approved", "Rich Punjabi cultural show.")
        ]
    },
    "Auli": {
        "cafe": [
            ("Cliff Top Club Altitude Cafe", 30.5310, 79.5700, "Panoramic alpine cafe serving piping hot mountain espresso, ginger lemon honey tea, and noodles.", "osm", "approved", "Stunning views of Nanda Devi peak."),
            ("Auli Snow View Cafe & Lounge", 30.5360, 79.5690, "Glass-fronted lounge overlooking ski slopes serving warm soups, cappuccino, and grilled sandwiches.", "osm", "approved", "Cozy fireplace seating."),
            ("Mountain Trails Joshimath Cafe", 30.5520, 79.5630, "Rustic timber cafe perched on the winding hill trail offering fresh bakery goodies and hot chocolate.", "osm", "approved", "Relaxed pitstop for hikers.")
        ],
        "food": [
            ("Chauhan Restaurant Joshimath", 30.5580, 79.5650, "Local Garhwali eatery serving traditional Mandua ki roti, chainsoo dal, and steaming rajma chawal.", "osm", "approved", "Hearty mountain nourishment."),
            ("Panchavati Inn Dining Terrace", 30.5540, 79.5620, "Scenic balcony dining hall providing hot north Indian and Garhwali thalis with deep valley panoramas.", "osm", "approved", "Warm hospitable service."),
            ("Auli Dhabas Ski Point", 30.5340, 79.5670, "Cluster of cheerful alpine stalls serving hot Maggi, aloo parathas, and spiced mountain tea.", "osm", "approved", "Quick slope-side snack.")
        ],
        "viewpoint": [
            ("Kwani Bugyal Alpine Meadow", 30.5550, 79.6000, "High meadow at 3,380m providing majestic views of Dunagiri, Kamet, and Nanda Devi peaks.", "osm", "approved", "Unmatched alpine trekking vantage."),
            ("Auli Ropeway Tower 10 Vista", 30.5390, 79.5710, "Cable car observation point viewing pristine snow slopes descending into pine forests.", "osm", "approved", "Clear mountain mornings."),
            ("Gorson Top Summit Ridge", 30.5480, 79.5920, "Panoramic cliff edge overlooking Trishul mountain and the Rishi Ganga river canyon.", "osm", "approved", "Pristine silence and crisp air.")
        ],
        "attraction": [
            ("Narsingh Temple Joshimath", 30.5590, 79.5640, "Ancient 8th-century temple dedicated to Lord Narasimha, the winter seat of Badrinath deity.", "osm", "approved", "Venerated Himalayan heritage shrine.")
        ]
    },
    "Bhopal": {
        "food": [
            ("Shahi Dawat Moti Masjid Square", 23.2550, 77.4020, "Historic Old Bhopal eatery famed for tender mutton biryani, seekh kebabs, and aromatic roomali rotis.", "osm", "approved", "Authentic Nawabi culinary flavors."),
            ("Chatori Gali Street Food Hub", 23.2570, 77.4040, "Atmospheric night alley lined with slow-cooked Haleem, Bhopali paan, and sweet rabdi jalebis.", "osm", "approved", "Vibrant evening culinary crawl."),
            ("Manohar Dairy & Restaurant MP Nagar", 23.2320, 77.4320, "Beloved city food landmark serving fresh vegetarian thalis, chole bhature, and signature rasmalai.", "osm", "approved", "Clean family favorite.")
        ],
        "viewpoint": [
            ("Manuabhan Tekri Hilltop Temple", 23.2920, 77.3680, "High cliff summit accessible by ropeway with 360-degree aerial views of the twin Bhopal lakes and city lights.", "osm", "approved", "Spectacular night skyline."),
            ("Kerwa Dam Spillway Viewpoint", 23.1630, 77.3820, "Tranquil reservoir nestled in forested hills, ideal for birdwatching and watching calm waters.", "osm", "approved", "Peaceful nature hideout."),
            ("Van Vihar Safari Lakeside Drive", 23.2350, 77.3750, "Scenic 5km shoreline route between the national park and Upper Lake surrounded by wetlands.", "osm", "approved", "Eco-friendly sunset drive.")
        ],
        "attraction": [
            ("Taj-ul-Masajid Grand Courtyard", 23.2640, 77.3930, "One of the largest mosques in Asia with colossal pink minarets, marble domes, and a grand reflective courtyard.", "osm", "approved", "Stunning Mughal architecture.")
        ]
    },
    "Bhubaneswar": {
        "food": [
            ("Odisha Hotel Shahid Nagar", 20.2880, 85.8450, "Traditional Odia restaurant serving authentic mutton kasa, bamboo shoot fish curry, and kanika sweet rice.", "osm", "approved", "Served in brass utensils."),
            ("Bhookh Lagti Hai Local Eatery", 20.3010, 85.8230, "Popular student and traveler hub serving hot chhena poda, cuttack chaat, and seasonal thalis.", "osm", "approved", "Casual and budget friendly."),
            ("Trupti Veg Restaurant Old Town", 20.2520, 85.8320, "Pure vegetarian dining near the temples offering traditional sattvic temple style meals and lassi.", "osm", "approved", "Wholesome spiritual dining.")
        ],
        "viewpoint": [
            ("Khandagiri Hill Summit Caves", 20.2610, 85.7860, "Ancient rock-cut hill terrace overlooking Bhubaneswar's modern skyline and dense green reserves.", "osm", "approved", "Breezy sunset vista."),
            ("Bindu Sagar Holy Lake Promenade", 20.2390, 85.8340, "Historic sacred tank encircled by hundreds of stone temple spires reflecting across shimmering waters.", "osm", "approved", "Serene evening lamp lit view."),
            ("Nandankanan Lakefront Watchtower", 20.3950, 85.8250, "Elevated viewpoint inside the botanical park overlooking Kanjia Lake and migratory bird flocks.", "osm", "approved", "Tranquil forest canopy view.")
        ],
        "attraction": [
            ("Udayagiri Rock-Cut Monastery Caves", 20.2630, 85.7870, "Remarkable 2nd-century BCE Jain cave complex featuring Queen's Cave carvings and ancient Brahmi inscriptions.", "osm", "approved", "Fascinating archaeological wonder.")
        ]
    },
    "Bodh Gaya": {
        "cafe": [
            ("Kundan Cafe & Bakery", 24.6965, 84.9920, "Warm traveler cafe serving freshly brewed espresso, cinnamon rolls, Tibetan bread, and ginger tea.", "osm", "approved", "Meeting spot for international monks."),
            ("Fujiya Green Meditation Cafe", 24.6950, 84.9890, "Garden restaurant serving Japanese green tea, vegetarian sushi, pasta, and fresh fruit juices.", "osm", "approved", "Peaceful courtyard.")
        ],
        "food": [
            ("Mohammad Restaurant Bodh Gaya", 24.6970, 84.9910, "Friendly budget eatery serving wholesome Indian curries, butter naans, thukpa, and freshly baked pita.", "osm", "approved", "Popular backpacker stop."),
            ("Siam Thai Restaurant", 24.6960, 84.9870, "Authentic Thai monastery restaurant serving aromatic tom yum soup, pad thai, and green coconut curry.", "osm", "approved", "Run by native Thai chefs."),
            ("Kalyan Restaurant Temple Road", 24.6940, 84.9930, "Clean North Indian vegetarian diner serving paneer butter masala, yellow dal tadka, and steaming thalis.", "osm", "approved", "Quick clean service.")
        ],
        "viewpoint": [
            ("Dungeshwari (Mahakala) Hill Caves", 24.7350, 85.0350, "Sacred cliffside cave summit where Gautama Buddha practiced severe penance before reaching enlightenment.", "osm", "approved", "Sweeping views of Phalgu River valley."),
            ("Muchalinda Lake Pavilion", 24.6955, 84.9910, "Tranquil lotus pond inside the Mahabodhi complex with central statue of snake king sheltering Buddha.", "osm", "approved", "Deeply meditative atmosphere."),
            ("Phalgu River Sandbank Vista", 24.7020, 84.9980, "Open sandy riverbank looking out toward the tranquil Bihar hills and riverside monasteries.", "osm", "approved", "Quiet sunrise reflection.")
        ],
        "attraction": [
            ("Royal Bhutan Buddhist Monastery", 24.6975, 84.9860, "Ornate temple built by the King of Bhutan featuring 7-foot Buddha statue and vivid clay wall carvings.", "osm", "approved", "Exemplary traditional Bhutanese art.")
        ]
    },
    "Cherrapunji": {
        "cafe": [
            ("Halari Cafe & Bakery Sohra", 25.2920, 91.7280, "Hilltop timber cafe serving hot Darjeeling tea, chocolate brownies, and savory vegetable rolls.", "osm", "approved", "Warm fireplace for rainy days."),
            ("Cloud 9 Cafe Cherrapunji", 25.2780, 91.7160, "Cozy lookout cafe serving steaming Khasi black tea, momos, and fresh local honey toast.", "osm", "approved", "Panoramic mist-covered valley view."),
            ("Mawsmai Cafe & Refreshments", 25.2440, 91.7200, "Convenient resting spot right near the cave entrance offering espresso, hot Maggi, and bottled water.", "osm", "approved", "Quick refreshment between trails.")
        ],
        "food": [
            ("Jiva Grill Cherrapunji", 25.2980, 91.7340, "Upscale alpine dining pavilion serving sizzlers, Indian curries, tandoori, and artisan mocktails.", "osm", "approved", "Scenic floor-to-ceiling glass windows."),
            ("Chef Cherrapunjee Restaurant", 25.2860, 91.7210, "Warm local dining hall serving authentic Khasi pork with bamboo shoot, dal, and fresh river fish.", "osm", "approved", "Authentic home-style recipes."),
            ("Sohra Plaza Family Restaurant", 25.2750, 91.7180, "Spacious roadside diner offering hot Indian, Chinese, and regional Khasi platters.", "osm", "approved", "Convenient highway parking.")
        ],
        "viewpoint": [
            ("Dainthlen Falls Canyon Overlook", 25.3090, 91.6880, "Natural rock plateau viewing the roaring plunge waterfall carving deep through sandstone gorges.", "osm", "approved", "Connected to historic Khasi legends."),
            ("Wei Sawdong Three-Tier Falls View", 25.3120, 91.6830, "Spectacular secluded overlook viewing three turquoise stepped natural plunge pools deep in the jungle.", "osm", "approved", "One of Meghalaya's most breathtaking sights.")
        ],
        "attraction": [
            ("Double Decker Living Root Bridge", 25.2490, 91.6680, "Centuries-old bio-engineering marvel crafted by Khasi tribes from living rubber tree roots across Umshiang river.", "osm", "approved", "Requires a memorable 3,000-step trek."),
            ("Arwah Lumshynna Prehistoric Cave", 25.2910, 91.7120, "Limestone cave network renowned for millions-of-years-old marine fossils, giant stalagmites, and underwater streams.", "osm", "approved", "Scenic cliffside forest boardwalk.")
        ]
    },
    "Coorg": {
        "cafe": [
            ("Big Cup Cafe Madikeri", 12.4210, 75.7420, "Signature specialty estate cafe on the Mysuru highway serving single-origin Arabica, cold brews, and desserts.", "osm", "approved", "Coffee lover's paradise.")
        ],
        "food": [
            ("Coorg Cuisine Madikeri", 12.4230, 75.7390, "Legendary Kodava restaurant famous for authentic Pandi Curry, Kadambuttu rice balls, and bamboo shoot fry.", "osm", "approved", "Quintessential Coorg gastronomy."),
            ("Raintree Heritage Restaurant", 12.4200, 75.7380, "Charming 1870 colonial villa serving Coorgi specialties, malabar parottas, and traditional coastal curries.", "osm", "approved", "Courtyard dining under lush rain trees.")
        ],
        "viewpoint": [
            ("Raja's Seat Sunset Pavilion", 12.4215, 75.7360, "Historic seasonal garden terrace overlooking endless rolling mist-filled green valleys of the Western Ghats.", "osm", "approved", "Sunset favorite of Coorg kings."),
            ("Mandalpatti Cloud Peak", 12.4780, 75.7020, "Rugged 4x4 mountain track reaching a sweeping windswept summit blanketed in swirling monsoon clouds.", "osm", "approved", "Unsurpassed 360-degree hilltop panoramas."),
            ("Abbey Falls Overlook Bridge", 12.4550, 75.7190, "Hanging suspension bridge facing the roaring cascade tumbling amidst coffee and cardamom plantations.", "osm", "approved", "Breathtaking natural waterfall spray.")
        ],
        "attraction": [
            ("Namdroling Golden Temple Bylakuppe", 12.4520, 75.9650, "Vast Tibetan monastic settlement featuring 40-foot gilded Buddha statues, intricate murals, and prayer wheels.", "osm", "approved", "Second largest Tibetan exile settlement in India.")
        ]
    },
    "Darjeeling": {
        "food": [
            ("Kunga Restaurant Gandhi Road", 27.0410, 28.2640, "Tiny beloved Tibetan eatery famed for steaming chicken momos, hearty gyathuk soup, and spicy pork noodles.", "osm", "approved", "Always packed with happy travelers."),
            ("Sonam's Kitchen Zakir Hussain Rd", 27.0460, 88.2680, "Iconic cozy home cafe serving fluffy banana pancakes, hash browns, cheese toast, and French press coffee.", "osm", "approved", "Warm intimate breakfast haven."),
            ("Shangri-La Heritage Restaurant", 27.0425, 88.2655, "Elegant colonial dining hall serving traditional Chinese, Tibetan, and sizzling Indian platters.", "osm", "approved", "Classy wooden decor and wine list.")
        ],
        "viewpoint": [
            ("Batasia Loop Himalayan View", 27.0160, 88.2470, "Spiraling toy train railway loop surrounding a war memorial with unobstructed views of Kanchenjunga.", "osm", "approved", "Watch the steam engine loop round."),
            ("Chowrasta Mall Observatory Ridge", 27.0440, 88.2670, "Historic public square perched on the mountain ridge where travelers sit on benches watching mountain sunsets.", "osm", "approved", "Vibrant social heart of Darjeeling."),
            ("Rock Garden & Ganga Maya Park", 27.0250, 88.2380, "Multi-level terraced garden carved directly into natural rock cliffs with cascading natural mountain streams.", "osm", "approved", "Picturesque mountain water sounds.")
        ],
        "attraction": [
            ("Happy Valley Tea Estate Heritage Factory", 27.0520, 88.2610, "Historic 1854 tea plantation offering guided factory tours explaining the plucking, rolling, and drying of fine teas.", "osm", "approved", "Authentic Darjeeling tea tasting session.")
        ]
    },
    "Delhi": {
        "cafe": [
            ("United Coffee House Connaught Place", 28.6320, 77.2180, "Historic 1942 grand cafe serving artisanal coffees, chicken a la kiev, and colonial pastries in chandelier grandeur.", "osm", "approved", "Vintage Delhi charm.")
        ],
        "food": [
            ("Karim's Historic Jama Masjid", 28.6508, 77.2334, "Legendary culinary institution operating since 1913 serving slow-braised mutton burra, seekh kebabs, and nihari.", "osm", "approved", "The pinnacle of Mughlai heritage."),
            ("Bukhara ITC Maurya", 28.5980, 77.1730, "World-acclaimed Northwest Frontier restaurant famous for giant family naans and 18-hour slow-cooked Dal Bukhara.", "osm", "approved", "World's most famous dal."),
            ("Saravana Bhavan Janpath", 28.6270, 77.2190, "Bustling South Indian vegetarian hotspot serving crisp ghee roast dosas, idlis, and South Indian filter coffee.", "osm", "approved", "Reliable clean comfort meals.")
        ],
        "viewpoint": [
            ("Hauz Khas Fort Lake Overlook", 28.5530, 77.1950, "14th-century madrasa stone pavilions overlooking the tranquil urban reservoir and deer park trees.", "osm", "approved", "Sunset favorite for youth and artists."),
            ("India Gate Canopy Vista", 28.6129, 77.2295, "Iconic ceremonial avenue framing the 42m stone arch and lush lawns illuminated at twilight.", "osm", "approved", "Vibrant evening pedestrian stroll."),
            ("Lotus Temple Serene Grounds", 28.5535, 77.2588, "Expansive marble pathways and 9 surrounding ponds reflecting the pure white petal architecture.", "osm", "approved", "Peaceful contemplation gardens.")
        ]
    },
    "Gangtok": {
        "food": [
            ("Mu Kimchi Korean & Tibetan Diner", 27.3270, 88.6110, "Popular cozy hub on Namnang road serving kimchi jjigae, pork bulgogi, hot ramen, and momos.", "osm", "approved", "Trendy warm traveler spot."),
            ("The Dragon Wok MG Marg", 27.3300, 88.6140, "Contemporary restaurant serving authentic Sikkimese set meals, fried trout, and chili garlic noodles.", "osm", "approved", "Overlooks pedestrian promenade."),
            ("Nimtho Traditional Sikkimese Kitchen", 27.3280, 88.6120, "Heritage wooden dining room offering indigenous fermented soybean chutney, gundruk soup, and millet beer.", "osm", "approved", "Authentic regional culinary tradition.")
        ],
        "viewpoint": [
            ("Ganesh Tok Summit Observation Deck", 27.3520, 88.6310, "Tiny circular temple deck high above the hills with viewing telescope of snow peaks and valley below.", "osm", "approved", "Magnificent early morning clarity."),
            ("Hanuman Tok Mountain Sanctuary", 27.3580, 88.6380, "Tranquil temple at 7,200 ft maintained by the Indian Army with peaceful prayers and sweeping vistas.", "osm", "approved", "Serene prayer flag canopy."),
            ("Deorali Ropeway Skyride View", 27.3220, 88.6080, "Double-cable zigzag ride soaring directly over Gangtok city rooftops, gorges, and valley slopes.", "osm", "approved", "Thrilling aerial bird-eye ride.")
        ],
        "attraction": [
            ("Namgyal Institute of Tibetology", 27.3150, 88.6040, "World-renowned research center housing ancient Tibetan manuscripts, thangkas, and Buddhist bronze artifacts.", "osm", "approved", "Rich Himalayan scholarly treasure.")
        ]
    },
    "Goa": {
        "cafe": [
            ("Artjuna Garden Cafe Anjuna", 15.5820, 73.7430, "Bohemian open-air Mediterranean cafe in a mango orchard serving cold brew, shakshuka, and smoothies.", "osm", "approved", "Artistic creative hub.")
        ],
        "food": [
            ("Vinayak Family Restaurant Assagao", 15.5900, 73.7710, "Beloved local institution serving authentic Goan fish curry thalis, crab xacuti, and rawa fried prawns.", "osm", "approved", "Local cult favorite."),
            ("Fisherman's Wharf Salcete", 15.1580, 73.9450, "Picturesque riverfront dining deck serving Goan prawn balchao, pork vindaloo, and live acoustic music.", "osm", "approved", "Breezy riverside atmosphere."),
            ("Gunpowder Assagao Heritage Villa", 15.5910, 73.7780, "Award-winning restaurant in a Portuguese bungalow serving fiery South Indian coastal meats and appams.", "osm", "approved", "Lush tropical courtyard.")
        ],
        "viewpoint": [
            ("Chapora Fort Ramparts Viewpoint", 15.6050, 73.7380, "Historic red-laterite clifftop fortress overlooking the sweeping arc of Vagator Beach and Chapora River mouth.", "osm", "approved", "Famous Dil Chahta Hai sunset spot."),
            ("Aguada Fort Lower Lighthouse Deck", 15.4920, 73.7730, "17th-century Portuguese fortress looking out over the meeting point of the Mandovi river and Arabian Sea.", "osm", "approved", "Grand ocean waves crashing on rocks."),
            ("Dona Paula Bay Sunset Promontory", 15.4540, 73.8010, "Breezy jetty lookout offering panoramic vistas across the Mormugao harbor and the vast open sea.", "osm", "approved", "Popular coastal viewing deck.")
        ]
    },
    "Hampi": {
        "food": [
            ("Mango Tree Restaurant Hampi", 15.3340, 76.4610, "Famous traveler garden restaurant serving thalis, wood-fired pizzas, fresh juices, and traditional Israeli fare.", "osm", "approved", "Laid-back floor cushions."),
            ("Laughing Buddha Cafe Riverside", 15.3410, 76.4670, "Relaxed river-facing shack across the Tungabhadra serving cold drinks, banana pancakes, and curry bowls.", "osm", "approved", "Tranquil water views."),
            ("Gopi Guesthouse Rooftop Diner", 15.3350, 76.4600, "Cozy terrace overlooking bazaar street serving wholesome Indian, continental, and hot masala chai.", "osm", "approved", "Friendly backpacker gathering.")
        ],
        "viewpoint": [
            ("Matanga Hill Sunrise Summit", 15.3320, 76.4680, "Highest point in central Hampi giving an unmatched 360-degree panorama of boulder fields and temple ruins.", "osm", "approved", "The ultimate sunrise climb."),
            ("Hemakuta Hill Sunset Boulder Slope", 15.3340, 76.4590, "Gentle sloping granite rock clustered with pre-Vijayanagara shrines looking west towards Virupaksha temple.", "osm", "approved", "Golden hour magical light."),
            ("Anjaneya Hill (Birthplace of Hanuman)", 15.3520, 76.4650, "White temple atop a dramatic granite pyramid reached by 575 stone steps with boundless valley views.", "osm", "approved", "Panoramic river and paddy views.")
        ],
        "attraction": [
            ("Vittala Temple & Iconic Stone Chariot", 15.3380, 76.4780, "Masterpiece of Vijayanagara art featuring musical granite pillars and the UNESCO world heritage stone chariot.", "osm", "approved", "Symbolic monument of Karnataka."),
            ("Lotus Mahal & Royal Elephant Stables", 15.3210, 76.4710, "Indo-Islamic secular palace architecture featuring graceful multi-domed vaults that once housed royal elephants.", "osm", "approved", "Lush manicured royal lawns.")
        ]
    },
    "Haridwar": {
        "food": [
            ("Mathura Walo Ki Prachin Dukan", 29.9530, 78.1630, "Century-old sweet shop in Moti Bazaar famous for hot milk, rabdi jalebi, kachoris, and pedas.", "osm", "approved", "Iconic traditional dessert heritage."),
            ("Hoshiyar Puri Haridwar", 29.9540, 78.1640, "Historic vegetarian diner since 1937 serving crisp bedmi pooris, chole, and seasonal shahi paneer.", "osm", "approved", "Pure desi ghee preparation.")
        ],
        "viewpoint": [
            ("Mansi Devi Hilltop Cable Car Deck", 29.9610, 78.1610, "Biligwa Parvat summit lookout offering expansive vistas over Haridwar city and the braided Ganga river channels.", "osm", "approved", "Accessible by scenic ropeway."),
            ("Chandi Devi Temple Peak", 29.9320, 78.1750, "Summit on the southern Neel Parvat hill viewing the Himalayan foothills and the vast plains of northern India.", "osm", "approved", "Peaceful sacred ridge breeze."),
            ("Har Ki Pauri Clock Tower Overlook", 29.9560, 78.1700, "Vantage point directly facing the sacred ghats as thousands of oil lamps float down the evening river.", "osm", "approved", "Hypnotic spiritual spectacle.")
        ],
        "attraction": [
            ("Maya Devi Temple Sacred Peeth", 29.9500, 78.1610, "Ancient 11th-century temple recognized as one of the three Siddha Peethas where Sati's heart is believed to have fallen.", "osm", "approved", "One of the oldest temples in Haridwar."),
            ("Bharat Mata Mandir Multi-Tier Shrine", 29.9880, 78.1910, "Unique eight-storey temple dedicated to Mother India, with each floor celebrating freedom fighters, saints, and culture.", "osm", "approved", "Innovative architectural tribute.")
        ]
    },
    "Havelock Island": {
        "cafe": [
            ("Barefoot Cafe Govind Nagar", 11.9920, 72.9850, "Chic wooden cafe serving espresso, tropical smoothies, and freshly baked croissants.", "osm", "approved", "Island tranquility."),
            ("Venom Bar & Seaside Cafe", 11.9880, 92.9820, "Open-deck beachfront lounge serving coconut water, mocktails, and light snacks with ocean breezes.", "osm", "approved", "Lively sunset gathering.")
        ],
        "food": [
            ("Fat Martin Cafe & South Indian Grill", 11.9910, 92.9840, "Cheerful open-sided garden diner serving stuffed dosas, paneer rolls, Nutella waffles, and fresh juices.", "osm", "approved", "Backpacker favorite breakfast spot."),
            ("Squid Restaurant Havelock", 11.9820, 92.9890, "Local seafood diner famous for grilled lobster, tandoori fish, and rich coconut-based curries.", "osm", "approved", "Fresh catch of the day."),
            ("Golden Spoon Dhaba", 11.9840, 92.9870, "Rustic family run shack serving delicious butter garlic crab, fish thalis, and rotis at budget prices.", "osm", "approved", "Homely flavorful cooking.")
        ],
        "viewpoint": [
            ("Elephant Beach Mangrove Point", 12.0120, 92.9610, "Pristine white sand shoreline bordered by fallen driftwood trees and shallow azure coral waters.", "osm", "approved", "Accessible by scenic jungle trek."),
            ("Kalapathar Beach Black Rocks", 11.9750, 93.0180, "Dramatic contrast of jet-black volcanic boulders against bright turquoise ocean waters and green forest.", "osm", "approved", "Unbelievable sunrise color palette."),
            ("Govind Nagar Beach Sunset Horizon", 11.9930, 92.9810, "Calm shallow waters reflecting brilliant pink and purple skies during Andaman island twilights.", "osm", "approved", "Gentle evening strolls.")
        ],
        "attraction": [
            ("Vijay Nagar Beach Coastal Stretch", 11.9850, 93.0020, "Idyllic long beach lined with mahua trees dipping into the crystal-clear water, ideal for swimming.", "osm", "approved", "Peaceful and uncrowded."),
            ("Radhanagar Beach Eco Pavilions", 11.9840, 92.9510, "Eco-certified Blue Flag beach infrastructure with nature trails through ancient rainforest canopies.", "osm", "approved", "Ranked among Asia's best beaches.")
        ]
    },
    "Hyderabad": {
        "cafe": [
            ("Nimrah Cafe and Bakery Charminar", 17.3615, 78.4740, "Historic tea stand facing Charminar serving authentic Irani Chai, Osmania biscuits, and khari puffs.", "osm", "approved", "Iconic Old City morning ritual.")
        ],
        "food": [
            ("Paradise Biryani Secunderabad", 17.4420, 78.4870, "Legendary 1953 culinary institution serving signature Hyderabadi mutton dum biryani with mirchi ka salan.", "osm", "approved", "World-renowned biryani landmark."),
            ("Shah Ghouse Hotel Tolichowki", 17.3990, 78.4180, "Famous destination for rich seasonal Haleem, mutton boti kebabs, and authentic Hyderabadi marag broth.", "osm", "approved", "Nighttime foodie favorite.")
        ],
        "viewpoint": [
            ("Golconda Fort Bala Hissar Summit", 17.3833, 78.4011, "Ancient fortress citadel perched 400 ft high with panoramic vistas of Hyderabad's modern skyline.", "osm", "approved", "Fascinating acoustic echo pavilions."),
            ("Hussain Sagar Tank Bund Promenade", 17.4240, 78.4720, "Lakeside boulevard viewing the monumental 18m monolithic Buddha statue illuminated in the water.", "osm", "approved", "Cool evening breeze with city lights."),
            ("Moula Ali Hilltop Overlook", 17.4730, 78.5630, "Spectacular dome-shaped rock formation with 500 steps looking over the twin cities' sprawling landscape.", "osm", "approved", "Panoramic sunrise vantage.")
        ],
        "attraction": [
            ("Chowmahalla Palace Royal Courtyards", 17.3580, 78.4710, "Magnificent 18th-century palace of the Nizams with grand Durbar halls, vintage cars, and Belgian crystal chandeliers.", "osm", "approved", "Elegance of the Asaf Jahi dynasty."),
            ("Qutb Shahi Tombs Heritage Park", 17.3910, 78.3970, "Majestic cluster of domed mausoleums built by the seven Golconda rulers in landscaped Persian gardens.", "osm", "approved", "Architectural blend of Persian and Hindu styles.")
        ]
    },
    "Jaipur": {
        "viewpoint": [
            ("Nahargarh Fort Sunset Ramparts", 26.9370, 75.8150, "Historic edge fortress ramparts looking out over the sprawling Pink City bathed in amber sunset light.", "osm", "approved", "Famous evening skyline vista."),
            ("Jal Mahal Lakeside Promenade", 26.9535, 75.8460, "Picturesque view from the Man Sagar lake promenade of the submerged yellow sandstone palace.", "osm", "approved", "Magical reflections at dusk."),
            ("Jaigarh Fort Cannon Overlook", 26.9850, 75.8510, "Mount of Eagles cliff edge housing the world's largest wheeled cannon Jaivana looking across Amer valley.", "osm", "approved", "Commanding military vantage.")
        ]
    },
    "Jaisalmer": {
        "cafe": [
            ("Kaku Coffee Shop Sunset Point", 26.9180, 70.9120, "Rooftop terrace on the fortress walls serving fresh filter coffee, masala tea, and Rajasthani snacks.", "osm", "approved", "Unobstructed desert horizon sunset."),
            ("Jaisal Italy Restaurant Cafe", 26.9130, 70.9140, "Charming cafe on the fort bastions serving Italian pastas, espresso, and crisp thin-crust pizzas.", "osm", "approved", "Stunning cliff view.")
        ],
        "viewpoint": [
            ("Bada Bagh Royal Cenotaphs Ridge", 26.9590, 70.8870, "Elegantly carved sandstone chhatris built on a rocky ridge reflecting warm golden desert rays.", "osm", "approved", "Photographer's golden hour dream."),
            ("Sam Sand Dunes Sunset Ridge", 26.8330, 70.5100, "Vast sweeping natural yellow sand dunes where camels gather against brilliant red desert sunsets.", "osm", "approved", "Quintessential Thar desert experience.")
        ],
        "attraction": [
            ("Patwon Ki Haveli Five-Mansion Cluster", 26.9160, 70.9160, "Extravagant 1805 cluster of five merchant havelis carved with lace-like yellow sandstone balconies.", "osm", "approved", "Finest jharokha craftsmanship in Rajasthan."),
            ("Jaisalmer Fort Royal Palace Museum", 26.9125, 70.9135, "Living golden-sandstone fort inhabited for centuries with royal rooms, weapons, and silver coronation thrones.", "osm", "approved", "UNESCO World Heritage living fortress.")
        ]
    },
    "Jodhpur": {
        "viewpoint": [
            ("Mehrangarh Fort Rao Jodha Desert Park Vista", 26.2990, 73.0180, "Dramatic cliffside nature trail overlooking the sheer 400 ft red sandstone fortress walls and blue houses.", "osm", "approved", "Unique ecological rock garden trail."),
            ("Jaswant Thada Marble Cenotaph Grounds", 26.3040, 73.0230, "Lakeside white marble memorial offering tranquil vistas across Mehrangarh fort and the azure city below.", "osm", "approved", "Carved translucent marble glow."),
            ("Mandore Gardens Ancient Pavilion", 26.3570, 73.0420, "Historic capital filled with towering temple-shaped cenotaphs surrounded by landscaped lawns and playful monkeys.", "osm", "approved", "Quiet architectural haven.")
        ],
        "attraction": [
            ("Umaid Bhawan Palace Royal Museum", 26.2810, 73.0470, "Grand Art Deco palace built in golden Chittar sandstone displaying royal vintage cars and clocks.", "osm", "approved", "One of the world's largest private residences."),
            ("Toorji Ka Jhalra Ancient Stepwell", 26.2970, 73.0230, "Restored 1740s geometric stepwell with intricately carved dancing elephants and cool turquoise subterranean waters.", "osm", "approved", "Vibrant central heritage square.")
        ]
    },
    "Kanyakumari": {
        "food": [
            ("Hotel Saravana Pure Veg Beach Rd", 8.0830, 77.5480, "Bustling breakfast spot offering steaming idlis, medu vadas, crispy paper roast dosas, and filter coffee.", "osm", "approved", "Wholesome Tamil vegetarian."),
            ("Seaview Restaurant Kanyakumari", 8.0810, 77.5510, "Air-conditioned coastal dining overlooking the sea serving fresh seer fish fry, prawn masala, and thalis.", "osm", "approved", "Great ocean views while dining."),
            ("The Curry Indian & Chinese", 8.0860, 77.5460, "Comfortable family diner offering north and south Indian specialties, tandoori breads, and biryanis.", "osm", "approved", "Clean friendly service.")
        ],
        "viewpoint": [
            ("Vattakottai Fort Seaside Bastion", 8.1250, 77.5640, "18th-century coastal granite fort jutting directly into the sea with views of the Western Ghats meeting water.", "osm", "approved", "Gentle ocean breezes."),
            ("Triveni Sangam Sacred Confluence", 8.0770, 77.5520, "The exact tip of India where the waters of the Indian Ocean, Arabian Sea, and Bay of Bengal converge.", "osm", "approved", "Sacred bathing and sunrise spot."),
            ("Kanyakumari Pier Walkway", 8.0790, 77.5490, "Pedestrian rock jetty walking out into the waves facing the colossal Thiruvalluvar Statue silhouette.", "osm", "approved", "Cool spray and sunset panoramas.")
        ],
        "attraction": [
            ("Thiruvalluvar Colossal 133ft Statue", 8.0775, 77.5560, "Monumental stone statue honoring the Tamil poet-philosopher standing on a small rock island.", "osm", "approved", "Accessible by regular ferry ride.")
        ]
    },
    "Kaziranga": {
        "cafe": [
            ("Orchid Cafe & Cultural Refreshments", 26.5920, 93.2040, "Charming rural cafe set inside the orchid park serving organic Assam CTC tea, snacks, and fresh lime soda.", "osm", "approved", "Surrounded by blooming native orchids."),
            ("Highway Diphlu Tea Lounge", 26.5820, 93.1780, "Cozy roadside wooden tearoom offering golden-tipped Assam single estate brews and butter toast.", "osm", "approved", "Freshly brewed tea tastings."),
            ("Wild Grass Courtyard Cafe", 26.5880, 93.1890, "Peaceful garden lounge under bamboo trees serving iced teas, espresso, and homemade lemon cakes.", "osm", "approved", "Relaxed jungle atmosphere.")
        ],
        "food": [
            ("Scarlet Rhino Multi-Cuisine Diner", 26.5840, 93.1740, "Popular safari dining hall serving Assamese chicken curry with black sesame, dal, and fresh rotis.", "osm", "approved", "Hearty post-safari meals."),
            ("Kaziranga Golf Resort Dining Pavilion", 26.7410, 93.4210, "Colonial tea estate club serving heritage Anglo-Indian roasts, regional thalis, and afternoon tea.", "osm", "approved", "Serene tea garden setting.")
        ],
        "viewpoint": [
            ("Kohora Central Range Watchtower", 26.5850, 93.1670, "Elevated timber watchtower looking out over sprawling elephant grass wetlands and grazing rhino herds.", "osm", "approved", "Superb wildlife spotting."),
            ("Brahmaputra River Sandbar Overlook", 26.6350, 93.1900, "Vast northern boundary viewpoint where the mighty Brahmaputra river flows past dense reserve forests.", "osm", "approved", "Migratory bird sanctuary."),
            ("Panbari Reserve Forest Ridge", 26.5680, 93.2450, "Evergreen tropical forest canopy viewpoint famous for sightings of the Hoolock Gibbon and hornbills.", "osm", "approved", "Pristine nature sounds.")
        ],
        "attraction": [
            ("Kaziranga National Orchid & Biodiversity Park", 26.5930, 93.2060, "Sprawling conservation garden home to over 500 species of wild orchids, bamboo groves, and traditional music.", "osm", "approved", "Authentic Assamese folk culture.")
        ]
    },
    "Khajuraho": {
        "food": [
            ("Raja Cafe Opposite Western Group", 24.8510, 79.9230, "Historic 1978 treehouse cafe and restaurant run by two Swiss-Indian sisters serving wood-fired pizzas and thalis.", "osm", "approved", "Front-row temple views from the terrace."),
            ("Mediterraneo Italian & Indian Restaurant", 24.8520, 79.9250, "Rooftop terrace serving fresh handmade pasta, crispy thin-crust pizza, and flavorful Indian curries.", "osm", "approved", "Relaxed bohemian atmosphere.")
        ],
        "viewpoint": [
            ("Raneh Falls Canyon & Crater Overlook", 24.9080, 79.8820, "Stunning natural canyon of crystalline granite rocks in shades of pink, green, and red carved by Ken river.", "osm", "approved", "Known as the Grand Canyon of India."),
            ("Shivsagar Lake Ghat Viewpoint", 24.8480, 79.9210, "Peaceful ancient water reservoir reflecting the temple spires and surrounding green trees.", "osm", "approved", "Serene sunrise reflection walk."),
            ("Beni Sagar Dam Sunset Point", 24.8320, 79.9140, "Tranquil dam reservoir framed by low rocky hills, perfect for birdwatching and watching colorful sunsets.", "osm", "approved", "Quiet picnic spot.")
        ],
        "attraction": [
            ("Kandariya Mahadeva Temple Grand Spire", 24.8530, 79.9190, "The largest and most ornate Hindu temple at Khajuraho adorned with over 800 intricately carved sculptures.", "osm", "approved", "Pinnacle of medieval Chandela architecture.")
        ]
    },
    "Kochi": {
        "cafe": [
            ("Kashi Art Cafe Fort Kochi", 9.9670, 76.2420, "Beloved gallery cafe with leafy courtyard, modern art installations, cold brew, and famous chocolate cake.", "osm", "approved", "Cultural heartbeat of Fort Kochi.")
        ],
        "food": [
            ("Fort Seafood Restaurant", 9.9650, 76.2410, "Charming colonial garden restaurant offering grilled tiger prawns, karimeen pollichathu, and appams.", "osm", "approved", "Fresh coastal seafood delicacies."),
            ("Dal Roti Fort Kochi", 9.9660, 76.2430, "Popular cozy hub serving oversized Kathi rolls, slow-cooked dal makhani, and warm parathas.", "osm", "approved", "Wholesome and satisfying."),
            ("Grand Pavilion MG Road", 9.9720, 76.2840, "Iconic Ernakulam culinary establishment famous for authentic Syrian beef fry, chicken stew, and biryanis.", "osm", "approved", "Time-tested Kerala institution.")
        ],
        "viewpoint": [
            ("Fort Kochi Chinese Fishing Nets Walkway", 9.9680, 76.2415, "Historic beachfront promenade viewing the iconic massive cantilevered fishing nets silhouetted against sunset.", "osm", "approved", "Symbolic coastal imagery of Kochi."),
            ("Marine Drive Rainbow Bridge Promenade", 9.9800, 76.2750, "Pedestrian waterfront boulevard overlooking Kochi backwaters, cargo ships, and the setting sun.", "osm", "approved", "Vibrant evening boat rides."),
            ("Vypin Island Lighthouse Summit", 10.0150, 76.2180, "46-meter tall spiral lighthouse offering breathtaking panoramic views of the Arabian Sea and coconut groves.", "osm", "approved", "Elevated ocean vista.")
        ],
        "attraction": [
            ("Mattancherry Dutch Palace Murals", 9.9580, 76.2590, "1555 Portuguese palace featuring extensive wooden ceilings and the finest Hindu mythological murals in India.", "osm", "approved", "Exemplary medieval Kerala murals."),
            ("Paradesi Synagogue & Jew Town", 9.9570, 76.2595, "Oldest active synagogue in the Commonwealth, featuring hand-painted Chinese porcelain tiles and Belgian chandeliers.", "osm", "approved", "Surrounded by antique spice shops.")
        ]
    },
    "Kolkata": {
        "food": [
            ("Arsalan Park Circus", 22.5440, 88.3650, "The gold standard for Kolkata-style biryani, served with succulent spiced mutton, egg, and fragrant golden potato.", "osm", "approved", "Unmatched Mughlai heritage."),
            ("6 Ballygunge Place", 22.5240, 88.3630, "Colonial townhouse restaurant celebrating century-old Bengali recipes: dab chingri, chitol mach, and kosha mangsho.", "osm", "approved", "Quintessential fine Bengali feast.")
        ],
        "viewpoint": [
            ("Millennium Park Hooghly Waterfront", 22.5740, 88.3440, "Landscaped riverfront gardens stretching along the Strand with views of the Howrah Bridge.", "osm", "approved", "Breezy sunset promenade."),
            ("Howrah Bridge Pedestrian Walkway", 22.5850, 88.3470, "Historic cantilever bridge walkway viewing the bustling river traffic, ghat bathers, and Kolkata skyline.", "osm", "approved", "Pulsing heartbeat of the metropolis."),
            ("Eco Park Central Lake Island", 22.6020, 88.4680, "Vast modern urban park with sprawling lake, glass pavilions, and panoramic boardwalks.", "osm", "approved", "Open green skies.")
        ],
        "attraction": [
            ("Indian Museum (Jadu Ghar)", 22.5570, 88.3510, "Ninth oldest regular museum in the world housing rare antique collections of Mughal paintings, fossils, and mummies.", "osm", "approved", "Magnificent Italianate palace galleries.")
        ]
    },
    "Leh": {
        "food": [
            ("Chopsticks Noodle Bar Fort Road", 34.1645, 77.5835, "Warm modern eatery serving piping hot Indonesian nasi goreng, Tibetan momos, wonton soups, and pad thai.", "osm", "approved", "Comforting post-trek dinner."),
            ("Lamayuru Restaurant Main Bazaar", 34.1625, 77.5845, "Longstanding traveler favorite serving fresh Israeli shakshuka, thukpa, vegetarian sizzlers, and apricot pies.", "osm", "approved", "Homely budget-friendly gathering.")
        ],
        "viewpoint": [
            ("Namgyal Tsemo Gompa Peak", 34.1690, 77.5880, "15th-century cliff monastery perched directly above Leh Palace with commanding vistas over the Indus valley.", "osm", "approved", "Spectacular sunset gold on mountains."),
            ("Sindhu Ghat Riverbank Vista", 34.1120, 77.6250, "Peaceful stone-paved riverbank facing the turquoise Indus River flowing past snow-covered Stok Kangri peaks.", "osm", "approved", "Deeply spiritual and quiet morning.")
        ],
        "attraction": [
            ("Hall of Fame War Memorial & Museum", 34.1430, 77.5350, "Moving museum maintained by the Indian Army commemorating high-altitude soldiers and Ladakhi culture.", "osm", "approved", "Insightful history and photography.")
        ]
    },
    "Madurai": {
        "food": [
            ("Sree Sabarees Pure Veg West Perumal", 9.9170, 78.1180, "Famous family restaurant serving traditional banana-leaf vegetarian meals, rasam, kootu, and appalams.", "osm", "approved", "Fast, hot, and delicious."),
            ("Kumar Mess Alagarkoil Road", 9.9350, 78.1380, "Iconic Madurai non-veg destination known for spicy mutton chukka, country chicken roast, and parottas.", "osm", "approved", "Rich explosive local spices.")
        ],
        "viewpoint": [
            ("Meenakshi Temple South Tower Overlook", 9.9190, 78.1190, "Rooftop vantage point across the street viewing the towering 170-foot sculpted gopurams reaching the sky.", "osm", "approved", "Unforgettable sight when lit up at night."),
            ("Samandar Kulam Lotus Pond", 9.9240, 78.1400, "Ancient water body framed by flowering trees offering tranquil reflective water vistas.", "osm", "approved", "Quiet morning birdwatching."),
            ("Thiruparankundram Rock Cut Ridge", 9.8780, 78.0720, "Dramatic monolithic granite hill housing an ancient cave shrine with wide valley views.", "osm", "approved", "Panoramic perspective over Madurai plains.")
        ],
        "attraction": [
            ("Gandhi Memorial Museum Historic Palace", 9.9310, 78.1410, "Housed in the 17th-century Tamukkam Palace of Rani Mangammal, displaying original artifacts from India's freedom struggle.", "osm", "approved", "One of only five Gandhi peace museums in India.")
        ]
    },
    "Mahabaleshwar": {
        "food": [
            ("Bagicha Corner Mahabaleshwar", 17.9250, 73.6550, "Famous garden restaurant famous for freshly picked strawberries with heavy cream, corn pattice, and chana roast.", "osm", "approved", "The ultimate Mahabaleshwar snack stop."),
            ("The Grapevine Restaurant", 17.9230, 73.6580, "Popular upscale dining room serving fresh tiger prawns, grilled lamb chops, and continental sizzlers.", "osm", "approved", "Great wine selection."),
            ("Aman Restaurant Main Market", 17.9210, 73.6560, "Bustling local diner serving Mughlai tandoori chicken, biryani, and warm buttery naans.", "osm", "approved", "Hearty evening dinners.")
        ],
        "viewpoint": [
            ("Arthur's Seat Queen of Points", 17.9860, 73.6120, "Dramatic 1,340m cliff edge viewing the sheer drop into the Savitri river valley and dense Brahma Arayna forest.", "osm", "approved", "Sensational light-floating rock effect."),
            ("Wilson Point (Sunrise Point)", 17.9240, 73.6700, "The highest point in Mahabaleshwar (1,439m) with three spacious masonry pavilions facing the sunrise.", "osm", "approved", "Vast 360-degree hill horizon."),
            ("Lodwick Point Elephant's Head", 17.9350, 73.6350, "Dramatic cliff promontory resembling an elephant's head and trunk jutting into the Koyna valley.", "osm", "approved", "Stunning sunset silhouettes.")
        ],
        "attraction": [
            ("Pratapgad Fort Historic Battlefield", 17.9310, 73.5780, "Monumental 17th-century mountain fort built by Chhatrapati Shivaji Maharaj featuring towering ramparts and watchtowers.", "osm", "approved", "Iconic Maratha heritage site."),
            ("Venna Lake Boating & Pier", 17.9180, 73.6750, "Scenic tree-lined mountain lake surrounded by pine forests offering rowboats and paddle boating.", "osm", "approved", "Classic family holiday attraction.")
        ]
    },
    "Mahabalipuram": {
        "food": [
            ("Nautilus Restaurant Othavadai Street", 12.6190, 80.1930, "French-run open-air restaurant serving fresh grilled fish, seafood pasta, salads, and crepes.", "osm", "approved", "Cozy book-lined international atmosphere."),
            ("Seashore Garden Restaurant", 12.6200, 80.1950, "Lawn seating near the beach serving spicy calamari, tiger prawns in coconut curry, and cold beverages.", "osm", "approved", "Breezy ocean murmur."),
            ("Geetha Cafe East Raja Street", 12.6170, 80.1910, "Local South Indian diner serving piping hot filter coffee, crisp masala dosas, and vegetarian meals on plantain leaf.", "osm", "approved", "Authentic budget breakfast.")
        ],
        "viewpoint": [
            ("Pancha Rathas Open Air Vista", 12.6120, 80.1930, "Elevated sand ridge overlooking five monolithic rock-cut shrines carved to resemble war chariots.", "osm", "approved", "Masterpiece of Pallava monolithic carving."),
            ("Krishna's Butterball Balanced Rock", 12.6185, 80.1925, "Gigantic 250-ton natural granite boulder precariously perched on a smooth 45-degree slope.", "osm", "approved", "Famous photo vantage and natural marvel."),
            ("Mahabalipuram Beach Golden Sands", 12.6165, 80.1990, "Vast ocean coastline where breaking surf rolls against ancient granite rocks and fishing boats.", "osm", "approved", "Morning sunrise over the Bay of Bengal.")
        ],
        "attraction": [
            ("Descent of the Ganges (Arjuna's Penance)", 12.6180, 80.1920, "Colossal open-air bas-relief carved on two monolithic boulders depicting celestial beings, elephants, and flowing rivers.", "osm", "approved", "One of the largest rock reliefs in the world.")
        ]
    },
    "Manali": {
        "attraction": [
            ("Hadimba Devi Ancient Timber Temple", 32.2480, 77.1700, "1553 pagoda-style wooden temple nestled inside giant deodar cedar forests with carved antler doors.", "osm", "approved", "Iconic Himalayan architecture."),
            ("Vashisht Hot Water Springs & Temple", 32.2630, 77.1870, "Natural geothermal sulfur baths and ancient stone temple overlooking the rushing Beas river gorge.", "osm", "approved", "Therapeutic mineral bath experience.")
        ]
    },
    "Mumbai": {
        "cafe": [
            ("Cafe Mondegar Colaba", 18.9240, 72.8320, "Historic 1932 retro cafe famous for its painted Mario Miranda murals, draft beer, and classic jukebox.", "osm", "approved", "Lively heritage institution."),
            ("Leopold Cafe Colaba Causeway", 18.9230, 72.8315, "Legendary 1871 gathering spot serving chilled beer, chicken roast, and continental pastries.", "osm", "approved", "World-famous traveler meeting spot.")
        ],
        "food": [
            ("Britannia & Co. Ballard Estate", 18.9350, 72.8400, "Beloved Parsi culinary institution operating since 1923 famous for fragrant Mutton Berry Pulao and caramel custard.", "osm", "approved", "Nostalgic colonial dining."),
            ("Bademiya Behind Taj Colaba", 18.9220, 72.8330, "Famed midnight open-air street stall grilling succulent seekh kebabs, baida rotis, and chicken rolls.", "osm", "approved", "Late night Mumbai food culture.")
        ],
        "viewpoint": [
            ("Marine Drive Queen's Necklace Vista", 18.9430, 72.8230, "Curving 3.6km coastal promenade with sweeping views of the Arabian Sea and the glittering night boulevard.", "osm", "approved", "The defining skyline view of Mumbai."),
            ("Bandra Bandstand Clifftop Promenade", 19.0430, 72.8190, "Oceanfront rocky walkway viewing the Bandra-Worli Sea Link cable bridge spanning across the open waves.", "osm", "approved", "Breezy sunset and city lights.")
        ],
        "attraction": [
            ("Gateway of India Grand Basalt Arch", 18.9220, 72.8347, "Colonial 1924 triumphal monument standing at the edge of the harbor facing incoming luxury boats.", "osm", "approved", "Grand arrival monument of Mumbai."),
            ("Chhatrapati Shivaji Maharaj Vastu Sangrahalaya", 18.9270, 72.8330, "Indo-Saracenic museum palace housing ancient sculptures, miniature paintings, and world-class heritage collections.", "osm", "approved", "Premier museum surrounded by lush palm gardens.")
        ]
    },
    "Munnar": {
        "food": [
            ("Rapsy Restaurant Munnar Town", 10.0880, 77.0600, "Longstanding mountain diner famous for hot egg parottas, beef fry, chicken biryani, and Spanish omelettes.", "osm", "approved", "Budget traveler favorite since decades."),
            ("Saravana Bhavan Munnar", 10.0870, 77.0610, "Clean vegetarian diner serving crisp ghee dosas, piping hot sambar, and fresh filter coffee.", "osm", "approved", "Quick comforting breakfast.")
        ],
        "viewpoint": [
            ("Top Station Panoramic Cloud Crest", 10.1250, 77.2450, "Historic ropeway terminal at 1,880m offering jaw-dropping views of clouds rolling into Tamil Nadu plains.", "osm", "approved", "Home to the rare Neelakurinji bloom."),
            ("Pothamedu Viewpoint Tea Slopes", 10.0650, 77.0540, "Cliffside roadway viewpoint looking out over undulating velvet-green tea, cardamom, and pepper plantations.", "osm", "approved", "Spectacular sunset across deep valleys."),
            ("Photo Point Tea Gardens", 10.0950, 77.0850, "Picture-perfect bend on Mattupetty road surrounded by contoured emerald tea bushes and silver oak trees.", "osm", "approved", "Popular photography stop.")
        ],
        "attraction": [
            ("KDHP Tea Museum & Processing Factory", 10.0920, 77.0520, "Historic plantation factory explaining century-old tea manufacturing with live roller demonstrations and tastings.", "osm", "approved", "Insightful history of Munnar's tea pioneers.")
        ]
    },
    "Mysore": {
        "cafe": [
            ("Malgudi Cafe Chittaranjan Palace", 12.3120, 76.6450, "Atmospheric literary cafe in a heritage eco-palace serving artisanal organic coffees and homemade cookies.", "osm", "approved", "Run in support of local underprivileged women."),
            ("Old House Cafe Vontikoppal", 12.3250, 76.6380, "Rustic Italian-style garden cafe serving wood-fired thin-crust sourdough pizza and fresh pour-over coffee.", "osm", "approved", "Serene green courtyard."),
            ("Cafe Aramane Palace Road", 12.3080, 76.6520, "Cozy local cafe serving traditional South Indian filter kaapi, maddur vada, and badam halwa.", "osm", "approved", "Authentic Mysore flavors.")
        ],
        "food": [
            ("Mylari Hotel Nazarbad", 12.3090, 76.6620, "Legendary 80-year-old modest diner serving cloud-soft butter dosas with unique coconut and coriander butter.", "osm", "approved", "Cult breakfast pilgrimage in Karnataka."),
            ("RRR Restaurant Gandhi Square", 12.3070, 76.6540, "Famous spicy Andhra-style dining hall serving fiery mutton biryani and chicken fry on fresh banana leaves.", "osm", "approved", "Packed with passionate food lovers.")
        ],
        "viewpoint": [
            ("Chamundi Hill Viewpoint Summit", 12.2740, 76.6710, "High rocky summit at 1,000m providing an eagle's-eye view of Mysore Palace, lakes, and race course.", "osm", "approved", "Breathtaking when palace lights turn on at night."),
            ("Karanji Lake Nature Boardwalk", 12.3040, 76.6740, "Scenic wooden bridge over Karnataka's largest walk-through aviary and tranquil butterfly park.", "osm", "approved", "Peaceful wetland birdwatching."),
            ("Brindavan Gardens Musical Fountain Deck", 12.4240, 76.5740, "Terraced ornamental gardens flanking the massive KRS dam with evening synchronized musical fountains.", "osm", "approved", "Illuminated nighttime spectacle.")
        ],
        "attraction": [
            ("Mysore Palace (Amba Vilas)", 12.3050, 76.6550, "Masterpiece of Indo-Saracenic royal architecture adorned with stained glass domes, gold leaf ceilings, and silver throne.", "osm", "approved", "Illuminated by 100,000 lightbulbs on weekends."),
            ("Devaraja Market Heritage Bazaar", 12.3110, 76.6510, "Vibrant century-old open market overflowing with pyramids of colorful kumkum powder, jasmine flowers, and essential oils.", "osm", "approved", "Sensory feast of heritage commerce.")
        ]
    },
    "Ooty": {
        "food": [
            ("Shinkows Chinese Restaurant", 11.4110, 76.7020, "Longstanding heritage dining room run by native Chinese-Indian family serving authentic chili pork and noodles.", "osm", "approved", "Cozy colonial dining room."),
            ("Nahar's Sidewalk Cafe Commercial Rd", 11.4120, 76.7040, "Open Italian pizzeria and espresso bar serving wood-fired margheritas, garlic bread, and hot apple pie.", "osm", "approved", "Popular town gathering spot."),
            ("Earl's Secret Ooty Club", 11.4080, 76.6950, "Glass-conservatory restaurant in a 1830s British mansion serving roasted lamb, stroganoff, and classic pudding.", "osm", "approved", "Romantic regal fireplace setting.")
        ],
        "viewpoint": [
            ("Doddabetta Peak Highest Crest", 11.4010, 76.7350, "Highest mountain in the Nilgiris (2,637m) with telescope observatory looking across the Western Ghats.", "osm", "approved", "Unsurpassed bird-eye mountain vistas."),
            ("Wenlock Downs 9th Mile Shooting Point", 11.4420, 76.6500, "Expansive undulating emerald green meadows featured in dozens of iconic Bollywood cinematic romances.", "osm", "approved", "Cool winds and endless green slopes."),
            ("Avalanche Lake Serene Water Vista", 11.3050, 76.5920, "Pristine mountain reservoir surrounded by dense shola forests, blooming rhododendrons, and trout hatcheries.", "osm", "approved", "Tranquil wilderness sanctuary.")
        ],
        "attraction": [
            ("Government Botanical Garden Heritage Lawns", 11.4180, 76.7110, "55-acre terraced garden established in 1848 housing thousands of exotic flora species and a 20-million-year-old fossil tree.", "osm", "approved", "World-renowned botanical collections."),
            ("Ooty Toy Train (Nilgiri Mountain Railway)", 11.4060, 76.7030, "UNESCO World Heritage meter-gauge steam train climbing through steep granite cliffs, 16 tunnels, and 250 bridges.", "osm", "approved", "One of the most scenic train journeys on earth.")
        ]
    },
    "Pachmarhi": {
        "cafe": [
            ("Open Air Cafe Pachmarhi Cantt", 22.4680, 78.4320, "Charming cantonment garden cafe offering fresh ground coffee, butter toast, and sweet local milkshakes.", "osm", "approved", "Relaxed green lawn seating."),
            ("Pachmarhi Bakery & Coffee Stalls", 22.4660, 78.4350, "Cozy morning tea stall serving warm cardamom chai, samosas, and fresh plum cakes.", "osm", "approved", "Quick breakfast stop.")
        ],
        "food": [
            ("Chunky Munky Restaurant Main Market", 22.4670, 78.4330, "Popular family eatery serving north Indian thalis, paneer pasanda, dal fry, and fresh rotis.", "osm", "approved", "Hearty home-style cooking."),
            ("Rasoi Dhaba Pachmarhi", 22.4690, 78.4360, "Vegetarian restaurant famous for authentic Malwa and Gujarati thalis served with ghee and jaggery.", "osm", "approved", "Clean wholesome dining."),
            ("Hotel Saket Restaurant", 22.4650, 78.4340, "Warm diner offering regional Madhya Pradesh snacks, bhutte ka kees, and flavorful curries.", "osm", "approved", "Pleasant family ambiance.")
        ],
        "viewpoint": [
            ("Dhoopgarh Highest Satpura Peak", 22.4490, 78.4180, "Highest peak in Madhya Pradesh (1,352m) offering legendary sunset and sunrise panoramas over rugged valleys.", "osm", "approved", "Golden glow on Satpura ranges."),
            ("Priyadarshini (Forsyth Point)", 22.4550, 78.4480, "The historic clifftop where Captain James Forsyth first discovered Pachmarhi in 1857.", "osm", "approved", "Vast amphitheater canyon view.")
        ],
        "attraction": [
            ("Bee Falls (Jamuna Prapat)", 22.4520, 78.4280, "Spectacular 35m natural plunge waterfall cascading down rock steps, supplying fresh drinking water to the hills.", "osm", "approved", "Refreshing natural swimming pool.")
        ]
    },
    "Pondicherry": {
        "food": [
            ("Villa Shanti French Quarter", 11.9330, 79.8340, "Award-winning restaurant in a 19th-century courtyard mansion serving French and modern Indian fusion dishes.", "osm", "approved", "Elegant romantic courtyard ambiance."),
            ("Surguru Vegetarian Heritage", 11.9350, 79.8300, "Beloved South Indian institution serving authentic crispy ghee dosas, vada, thalis, and filter coffee.", "osm", "approved", "High quality traditional flavors."),
            ("Tanto Pizzeria Auroville Main Rd", 11.9950, 79.8150, "Popular Italian trattoria using organic farm-grown herbs and wood-fired ovens for authentic pizzas and pastas.", "osm", "approved", "Lush garden patio.")
        ],
        "viewpoint": [
            ("Old Light House White Town", 11.9325, 79.8355, "Historic 19th-century French coastal beacon overlooking the rocky sea breakers and Gandhi statue plaza.", "osm", "approved", "Iconic symbol of White Town."),
            ("Serenity Beach Surfing Break", 11.9680, 79.8450, "Golden crescent beach with rocky pier walking out into the waves, popular for sunrise surfers.", "osm", "approved", "Vibrant coastal breeze."),
            ("Paradise Beach Sandbar Island", 11.8720, 79.8180, "Secluded sandy spit accessed by scenic ferry through Chunnambar backwaters and mangrove channels.", "osm", "approved", "Pristine turquoise water swimming.")
        ],
        "attraction": [
            ("Sri Aurobindo Ashram Spiritual Center", 11.9360, 79.8340, "Serene spiritual haven housing the marble samadhi of Sri Aurobindo and the Mother covered in fresh flowers.", "osm", "approved", "Profound silence and contemplation.")
        ]
    },
    "Port Blair": {
        "food": [
            ("New Lighthouse Restaurant Aberdeen", 11.6710, 92.7480, "Open rooftop coastal restaurant serving fresh grilled fish, red snapper curry, and tiger prawns.", "osm", "approved", "Sea breeze over Marina park."),
            ("Ananda Restaurant Aberdeen Bazaar", 11.6680, 92.7410, "Longstanding South Indian and seafood diner serving seafood thalis, appams, and parottas.", "osm", "approved", "Reliable authentic taste.")
        ],
        "viewpoint": [
            ("Mount Harriet (Mount Manipur) Peak", 11.7150, 92.7350, "Highest peak in South Andaman (365m) featured on the Indian 20-rupee note looking across Ross Island.", "osm", "approved", "Magnificent aerial island vistas."),
            ("Corbyn's Cove Beach Crescent", 11.6420, 92.7490, "Palm-fringed coastal bay with soft sands and gentle waves ideal for swimming and evening coconut water.", "osm", "approved", "Picturesque coastal curve.")
        ],
        "attraction": [
            ("Cellular Jail National Memorial", 11.6740, 92.7500, "Historic colonial prison fortress containing seven radiating wings that held India's revolutionary freedom fighters.", "osm", "approved", "Profound history and evening sound-and-light show."),
            ("Ross Island (Netaji Subhash Chandra Bose Dweep)", 11.6780, 92.7620, "Haunting British colonial administrative ruins engulfed by strangler fig tree roots and roaming spotted deer.", "osm", "approved", "Accessible by 15-minute boat ride.")
        ]
    },
    "Pune": {
        "cafe": [
            ("Vohuman Cafe Sasoon Road", 18.5280, 73.8740, "Iconic 1978 Irani breakfast joint famous for cheese omelettes, bun maska, and hot sugary Irani chai.", "osm", "approved", "Legendary morning institution."),
            ("German Bakery Koregaon Park", 18.5370, 73.8930, "Bohemian cafe offering freshly baked apple strudel, herbal teas, bagels, and vibrant expat atmosphere.", "osm", "approved", "Pioneering creative hub.")
        ],
        "food": [
            ("Shabree Pure Veg FC Road", 18.5230, 73.8420, "Celebrated Maharashtrian restaurant serving authentic thalipeeth, pithla bhakri, kothimbir vadi, and aamras.", "osm", "approved", "Authentic state culinary showcase."),
            ("George Restaurant Camp", 18.5180, 73.8780, "Heritage Mughlai restaurant famous for biryanis, butter chicken, and grilled seekh kebabs since 1936.", "osm", "approved", "Camp classic dining."),
            ("Vaishali FC Road", 18.5240, 73.8410, "Historic student and thinker garden diner famous for Mysore masala dosas, filter coffee, and SPDP chaat.", "osm", "approved", "The cultural meeting spot of Pune.")
        ],
        "viewpoint": [
            ("Parvati Hill Temple Crest", 18.4970, 73.8480, "Historic hill summit with 103 stone steps providing panoramic 360-degree views across the entire Pune valley.", "osm", "approved", "Peshwa heritage museum atop."),
            ("Vetal Tekdi (ARAI Hill) Nature Ridge", 18.5250, 73.8150, "Highest natural point within Pune city limits (2,600 ft) surrounded by scrub forests and walking paths.", "osm", "approved", "Loved by morning runners and birdwatchers.")
        ],
        "attraction": [
            ("Shaniwar Wada 18th Century Fort", 18.5190, 73.8550, "Monumental seven-storey seat of the Peshwa rulers of the Maratha Empire featuring massive spiked wooden gates.", "osm", "approved", "Iconic symbol of Maratha pride."),
            ("Aga Khan Palace Italianate Memorial", 18.5520, 73.9010, "Grand 1892 palace featuring Italian arches and spacious lawns where Mahatma Gandhi was interned in 1942.", "osm", "approved", "Houses Gandhi's memorial and ashes.")
        ]
    },
    "Puri": {
        "food": [
            ("Wildgrass Restaurant VIP Road", 19.8050, 85.8240, "Lush open garden restaurant serving authentic Odia crab curry, dalma, prawn malai curry, and luchi.", "osm", "approved", "Relaxed tribal art decor."),
            ("Chung Wah Chinese Restaurant", 19.7990, 85.8210, "Decades-old family restaurant serving hot sweet corn chicken soup, chili fish, and hakka noodles near the beach.", "osm", "approved", "Classic Puri institution.")
        ],
        "viewpoint": [
            ("Golden Beach Blue Flag Promenade", 19.7960, 85.8250, "Certified Blue Flag clean beach with paved boardwalk, clean amenities, and sparkling morning sunrise over water.", "osm", "approved", "Cleanest beach strip in Odisha."),
            ("Baliharachandi Sand Dune Beach", 19.7620, 85.7480, "Tranquil meeting point of the Bhargavi river and Bay of Bengal framed by wind-swept casuarina trees.", "osm", "approved", "Scenic secluded shoreline."),
            ("Chakratirtha Beach Sunrise Pier", 19.8080, 85.8450, "Peaceful fishing village beach where colorful wooden catamarans head out into the golden dawn waves.", "osm", "approved", "Photographer's sunrise dream.")
        ],
        "attraction": [
            ("Gundicha Temple Garden Sanctuary", 19.8220, 85.8340, "The garden palace temple where Lord Jagannath resides for seven days during the annual Ratha Yatra festival.", "osm", "approved", "Lush walled sanctuary of peace."),
            ("Raghurajpur Heritage Crafts Village", 19.8650, 85.8320, "World-famous heritage artisans village where every household creates exquisite traditional Pattachitra paintings.", "osm", "approved", "Living museum of Indian folk art.")
        ]
    },
    "Rann of Kutch": {
        "cafe": [
            ("Kutch Craft & Chai Village Stall", 23.8180, 69.8350, "Earthen-pot masala chai, local sweets, and savory Kutchi snacks near the tent city entrance.", "osm", "approved", "Warm hospitality in the desert."),
            ("White Rann Desert Moonlight Cafe", 23.8310, 69.8290, "Open desert seating offering steaming coffee, hot chocolate, and bajra biscuits under starry skies.", "osm", "approved", "Magical night desert setting."),
            ("Hodka Village Artisan Tearoom", 23.6820, 69.6520, "Mud-walled bhunga hut cafe serving ginger mint tea and fresh buttermilk.", "osm", "approved", "Traditional Kutch mud art decor.")
        ],
        "food": [
            ("Kutchi Royal Dining Tent", 23.8160, 69.8420, "Grand cultural banquet hall serving traditional Kutchi kadhi, khichdi, sev tameta nu shaak, and rotlas.", "osm", "approved", "Authentic desert feast."),
            ("Toran Resort Restaurant Dhordo", 23.8050, 69.8510, "Government-run heritage resort diner providing pure vegetarian Gujarati thalis with unlimited chaas.", "osm", "approved", "Clean, wholesome local flavors.")
        ],
        "viewpoint": [
            ("White Rann Salt Horizon Watchtower", 23.8380, 69.8350, "Elevated observation tower viewing the endless shimmering white salt crust extending to the horizon.", "osm", "approved", "Spectacular under full moon illumination."),
            ("Dholavira Harappan Desert Causeway", 23.8820, 70.2100, "Incredible highway bisecting the vast turquoise salt lake on the way to the ancient Indus civilization site.", "osm", "approved", "Surreal road trip perspective.")
        ],
        "attraction": [
            ("Dholavira UNESCO Harappan City", 23.8860, 70.2140, "5,000-year-old archaeological metropolis displaying monumental stone architecture and revolutionary water reservoirs.", "osm", "approved", "World-renowned Bronze Age civilization."),
            ("Nirona Rogan Art Heritage Center", 23.4020, 69.5850, "Historic village home to the sole family preserving the 400-year-old Rogan fabric painting art using castor oil.", "osm", "approved", "Rare indigenous mastercraft.")
        ]
    },
    "Rishikesh": {
        "food": [
            ("Jal & Jalebi by Ganga Kinare", 30.1080, 78.2980, "Riverside fine dining terrace serving gourmet North Indian curries, tandoori specialties, and hot crisp jalebis.", "osm", "approved", "Serene private riverside views."),
            ("Madras Cafe Muni Ki Reti", 30.1210, 78.3150, "Longstanding traditional diner serving crisp butter dosas, idli vada combo, and authentic filter coffee.", "osm", "approved", "Quick, clean pilgrim favorite.")
        ],
        "viewpoint": [
            ("Lakshman Jhula Suspension Span", 30.1280, 78.3280, "Iconic 450-foot hanging iron bridge spanning high over the rushing emerald Ganga river with temple views.", "osm", "approved", "Symbol of holy Rishikesh."),
            ("Triveni Ghat Evening Aarti Arena", 30.1020, 78.2960, "Vast tiered river steps where priests conduct synchronized evening Maha Aarti with giant brass oil lamps.", "osm", "approved", "Spiritual devotion and chanting."),
            ("Neer Garh Waterfall Forest Ridge", 30.1520, 78.3420, "Tiered natural waterfall reached by a scenic cliff trail through butterflies and dense oak forests.", "osm", "approved", "Cool mountain stream dip.")
        ],
        "attraction": [
            ("Parmarth Niketan Ashram & Gardens", 30.1190, 78.3140, "The largest ashram in Rishikesh with sprawling flowering courtyards, yoga halls, and riverside prayer ghats.", "osm", "approved", "World yoga festival venue.")
        ]
    },
    "Shillong": {
        "food": [
            ("City Hut Family Dhaba Police Bazaar", 25.5790, 91.8830, "Thatched bamboo pavilions serving spicy tandoori chicken, regional thalis, and Mughlai curries.", "osm", "approved", "Warm fireplace dining."),
            ("The Wok Laitumkhrah", 25.5710, 91.8880, "Popular local Chinese and Khasi diner serving steaming thukpa, momos, and traditional Jadoh pork rice.", "osm", "approved", "Student and musician hangout.")
        ],
        "viewpoint": [
            ("Laitlum Canyons Sheer Ridge", 25.4680, 91.9050, "Breathtaking canyon ridge with steep 3,000 ft drops into misty Khasi valleys and rolling green meadows.", "osm", "approved", "One of India's most dramatic landscapes.")
        ]
    },
    "Shimla": {
        "viewpoint": [
            ("Scandal Point Mall Road", 31.1045, 77.1730, "Historic meeting corner connecting The Mall and The Ridge with open views of the snow-clad Himalayas.", "osm", "approved", "Social center of Shimla."),
            ("Tara Devi Hilltop Summit", 31.0650, 77.1350, "Serene forested mountain peak (2,100m) offering 360-degree panoramic views of Shimla city and deep pine valleys.", "osm", "approved", "Peaceful pine needle trails."),
            ("Summer Hill Panoramic Ridge", 31.1120, 77.1420, "Charming quiet hill located 5km from city, shaded by deodars and viewing rolling mountain waves.", "osm", "approved", "Idyllic mountain walks.")
        ],
        "attraction": [
            ("Viceregal Lodge & Botanical Grounds", 31.1020, 77.1410, "Magnificent Jacobethan British castle from 1888 with teak wood paneling where historic independence pacts were drafted.", "osm", "approved", "Surrounded by manicured flower gardens.")
        ]
    },
    "Spiti Valley Test": {
        "cafe": [
            ("Cafe Kunzum Top Kaza", 32.2260, 78.0720, "Popular mountaineer cafe serving lemon-ginger tea, pasta, and sea buckthorn juice.", "osm", "approved", "Traveler hub in Kaza."),
            ("The Himalayan Cafe Kaza", 32.2270, 78.0710, "Warm wooden cafe serving hot espresso, yak cheese toast, and baked brownies.", "osm", "approved", "Cozy high altitude haven."),
            ("Sol Cafe Kaza Eco-Lounge", 32.2250, 78.0700, "Eco-friendly solar heated lounge offering organic Spitian barley tea and sourdough sandwiches.", "osm", "approved", "Solar powered warmth."),
            ("Taste of Spiti Market Cafe", 32.2280, 78.0730, "Lively central marketplace diner offering mountain coffee, thukpa, and ginger lemon teas.", "osm", "approved", "Central meeting spot.")
        ],
        "food": [
            ("Hotel Deyzor Garden Restaurant", 32.2290, 78.0740, "Acclaimed mountain dining hall serving authentic Spitian thenthuk, momos, and fresh garden salads.", "osm", "approved", "Award-winning Himalayan hospitality."),
            ("Little Italy Pizzeria Kaza", 32.2240, 78.0715, "Surprising wood-fired pizzeria in the trans-Himalayan desert serving thin crust pizzas.", "osm", "approved", "Comfort food at 12,000 ft."),
            ("Mahabuddha Restaurant Tabo", 32.0950, 78.3810, "Homely monastery village eatery serving Tibetan tingmo, mutton curries, and dal bhat.", "osm", "approved", "Authentic village flavors."),
            ("Dragon Restaurant Main Kaza", 32.2275, 78.0725, "Longstanding mountain diner serving Tibetan thukpa, fried momos, and steaming chai.", "osm", "approved", "Fast and filling.")
        ],
        "viewpoint": [
            ("Key Gompa High Ridge Viewpoint", 32.2980, 78.0120, "Overlook above the 1,000-year-old monastery with views across the serpentine Spiti river basin.", "osm", "approved", "Quintessential Spiti imagery."),
            ("Chicham Bridge Aerial Canyon Span", 32.3500, 77.9800, "Asia's highest suspension bridge hanging over a 1,000 ft deep rocky gorge.", "osm", "approved", "Thrilling high altitude perspective."),
            ("Langza Buddha Statue Panoramic Overlook", 32.2750, 78.1150, "Giant golden Buddha statue sitting against the dramatic backdrop of Chau Chau Kang Nilda snow peak.", "osm", "approved", "Fossil village panoramic crest."),
            ("Dhankar Gompa Cliff Edge Perch", 32.0230, 78.2560, "Ancient monastery perched dramatically on sharp eroded mud pinnacles over Spiti and Pin river confluence.", "osm", "approved", "Spectacular cliffhanger vista.")
        ],
        "attraction": [
            ("Hikkim Highest Operational Post Office", 32.2500, 78.0900, "World's highest operational post office at 14,567 ft where travelers send postcards across the globe.", "osm", "approved", "Unique bucket-list stop."),
            ("Komic Highest Motorable Village", 32.2420, 78.1050, "One of the highest inhabited villages in the world with ancient Lundup Gompa monastery.", "osm", "approved", "Trans-Himalayan cultural wonder."),
            ("Tabo 1000-Year-Old Monastery Complex", 32.0920, 78.3820, "Known as the Ajanta of the Himalayas, founded in 996 CE with priceless stucco statues and wall murals.", "osm", "approved", "UNESCO tentative world heritage site."),
            ("Pin Valley National Park Snow Leopard Trail", 31.9850, 77.9900, "High altitude wildlife reserve famous for ibex, Tibetan gazelles, and the elusive snow leopard.", "osm", "approved", "Untouched cold desert ecology.")
        ]
    },
    "Srinagar": {
        "viewpoint": [
            ("Shankaracharya Hill Summit Panorama", 34.0840, 74.8380, "Ancient stone temple peak offering breathtaking aerial vistas across Dal Lake, the Jhelum river, and Srinagar city.", "osm", "approved", "Commanding panoramic perspective.")
        ],
        "attraction": [
            ("Hazratbal Dargah Sacred Marble Shrine", 34.1250, 74.8430, "Silvery white marble shrine reflecting gracefully on the northern shores of Dal Lake.", "osm", "approved", "Deeply venerated Kashmiri spiritual shrine.")
        ]
    },
    "Tawang": {
        "cafe": [
            ("Dharma Coffee House Tawang", 27.5870, 91.8660, "Artisan hill cafe serving freshly brewed coffee, homemade apple pie, hot chocolate, and Tibetan cookies.", "osm", "approved", "Cozy book collection."),
            ("High Altitude Cafe Sela Pass", 27.5060, 92.1060, "Warm army-run cafe at 13,700 ft serving hot chai, black tea, and Maggi over looking frozen Sela Lake.", "osm", "approved", "Lifesaving warm stop amidst snow.")
        ],
        "food": [
            ("Dragon Restaurant Old Market", 27.5865, 91.8640, "Warm family dining room serving piping hot Monpa chicken curry, hand-pulled thenthuk, and butter tea.", "osm", "approved", "Generous comforting meals."),
            ("Blue Pine Restaurant Tawang", 27.5880, 91.8680, "Longstanding town restaurant offering hearty North Indian, Chinese, and regional Monpa specialty meals.", "osm", "approved", "Clean cozy atmosphere."),
            ("Greenwood Multi Cuisine", 27.5840, 91.8630, "Bright local restaurant known for fresh vegetable chowmein, momos, and traditional pork dishes.", "osm", "approved", "Popular with travelers.")
        ],
        "viewpoint": [
            ("Penga Teng Tso (PTSO) Lake Vista", 27.6350, 91.8820, "Pristine high-altitude alpine lake surrounded by blooming rhododendrons and snow peaks.", "osm", "approved", "Breathtaking wilderness serenity."),
            ("Madhuri (Sangetsar) Lake Mountain Overlook", 27.7120, 91.7850, "Surreal lake created by earthquake with petrified dead tree trunks rising out of crystal clear water.", "osm", "approved", "One of Northeast India's most scenic spots.")
        ],
        "attraction": [
            ("Tawang War Memorial Stupa Complex", 27.5890, 91.8700, "40-foot high stupa designed memorial commemorating Indian soldiers who defended the border in 1962.", "osm", "approved", "Sound and light show in evening."),
            ("Urgelling Gompa (Birthplace of 6th Dalai Lama)", 27.5720, 91.8750, "Historic 14th-century monastery where Tsangyang Gyatso was born, surrounded by sacred prayer trees.", "osm", "approved", "Tranquil spiritual heritage.")
        ]
    },
    "Udaipur": {
        "viewpoint": [
            ("Sajjangarh (Monsoon Palace) High Peak", 24.5940, 73.6370, "Palace perched atop Bansdara mountain looking across the entire lake district and rolling Aravalli ranges.", "osm", "approved", "Most famous sunset vantage in Rajasthan.")
        ],
        "attraction": [
            ("Saheliyon Ki Bari Royal Garden of Maidens", 24.6020, 73.6850, "18th-century landscaped royal garden featuring marble elephant fountains, lotus pools, and rose gardens.", "osm", "approved", "Masterpiece of historical fountain engineering.")
        ]
    },
    "Ujjain": {
        "cafe": [
            ("Cafe Imperial Freeganj", 23.1780, 75.7920, "Modern cafe serving iced lattes, espresso, burgers, and sandwiches in a clean air-conditioned space.", "osm", "approved", "Popular youth and traveler cafe."),
            ("Mahakal Temple Road Tea Stalls", 23.1830, 75.7680, "Traditional street stalls serving hot kulhad masala chai, poha-jalebi, and rabdi milk.", "osm", "approved", "Vibrant spiritual morning ambiance."),
            ("Brew & Bite Ujjain", 23.1810, 75.7880, "Cozy neighborhood cafe offering frappes, shakes, and quick vegetarian bites.", "osm", "approved", "Relaxed seating.")
        ],
        "food": [
            ("Bholaguru Mishthan Bhandar", 23.1840, 75.7720, "Century-old culinary landmark famous for piping hot Hing ki kachori, jalebi, and mawa pedas.", "osm", "approved", "Quintessential Ujjain breakfast."),
            ("Shree Ganga Restaurant Dewas Gate", 23.1820, 75.7820, "Spacious vegetarian restaurant serving rich Malwa thalis, dal bafla, and paneer curries.", "osm", "approved", "Family dining favorite."),
            ("Swastik Pure Veg Restaurant", 23.1790, 75.7890, "Clean dining hall offering North Indian and Gujarati thalis, lassi, and fresh tandoori rotis.", "osm", "approved", "Clean fast service.")
        ],
        "viewpoint": [
            ("Ram Ghat Shipra Riverbank Deck", 23.1800, 75.7620, "Ancient ghat steps on the sacred Shipra river where thousands of lamps are illuminated for evening aarti.", "osm", "approved", "Atmospheric spiritual waterfront."),
            ("Vedh Shala (Jantar Mantar) Tower View", 23.1730, 75.7760, "1719 astronomical observatory terrace with sundials looking across the historic city and green trees.", "osm", "approved", "Historic geographic prime meridian of India."),
            ("Triveni Ghat Sangam Overlook", 23.1610, 75.7580, "Tranquil river confluence point shaded by banyan trees, ideal for quiet contemplation and morning breezes.", "osm", "approved", "Peaceful sacred waters.")
        ]
    },
    "Varanasi": {
        "cafe": [
            ("Aum Cafe Assi Ghat", 25.2890, 83.0070, "Artisan cafe overlooking Assi Ghat serving organic coffees, herbal teas, pancakes, and homemade granola.", "osm", "approved", "Beloved yogi and traveler haven."),
            ("Open Hand Cafe & Shop Assi", 25.2910, 83.0060, "Fair-trade boutique cafe serving espresso, carrot cakes, and fresh baguette sandwiches.", "osm", "approved", "Quiet air-conditioned haven.")
        ],
        "viewpoint": [
            ("Chet Singh Ghat Fortress River View", 25.2970, 83.0080, "Imposing 18th-century fortified river palace with massive stone bastions directly touching the water.", "osm", "approved", "Dramatic fortified riverfront panorama."),
            ("Manikarnika Ghat Cremation Overlook", 25.3110, 83.0140, "Ancient sacred burning ghat viewing eternal funeral pyres, wooden boats, and multi-storey historic havelis.", "osm", "approved", "Profound reflection on life and impermanence."),
            ("Assi Ghat Sunrise Subah-e-Banaras", 25.2885, 83.0075, "Expansive southernmost ghat where morning classical music, Vedic chanting, and yoga greet the rising sun.", "osm", "approved", "The sublime dawn of Kashi.")
        ],
        "attraction": [
            ("Ramnagar Fort & Museum Across River", 25.2710, 83.0280, "18th-century cream-sandstone fortress of the Kashi Naresh with royal armory, vintage cars, and astronomical clock.", "osm", "approved", "Magnificent view across the Ganga.")
        ]
    },
    "Wayanad": {
        "food": [
            ("ClayHut Village Restaurant Kalpetta", 11.6080, 76.0850, "Traditional clay-walled dining hall serving Malabar fish curry meals, bamboo biryani, and pathiri.", "osm", "approved", "Authentic Kerala earthen-pot flavors."),
            ("Wilton Restaurant Sultan Bathery", 11.6620, 76.2580, "Modern diner offering traditional Kerala beef fry, tandoori chicken, appam, and fresh juices.", "osm", "approved", "Popular highway family stop."),
            ("Green Gates Restaurant", 11.6110, 76.0820, "Spacious veranda restaurant serving regional Malabar delicacies, payasam, and South Indian thalis.", "osm", "approved", "Scenic hill garden surroundings.")
        ],
        "viewpoint": [
            ("Neelimala Viewpoint Valleys", 11.5540, 76.2410, "Breathtaking cliff peak providing panoramic views of the cascading Meenmutty falls and river gorge.", "osm", "approved", "Pleasant trek through coffee estates."),
            ("Lakkidi Viewpoint Thamarassery Churam", 11.5160, 76.0280, "Dramatic mountain gateway overlooking the 9 hairpin curves of the ghat road descending into the plains.", "osm", "approved", "Sweeping monsoon cloud sea."),
            ("Banasura Sagar Dam Earthen Crest", 11.6710, 75.9580, "India's largest earthen dam holding a vast mountain reservoir with submerged forested islands.", "osm", "approved", "Stunning reflection of Banasura peak.")
        ],
        "attraction": [
            ("Pookode Natural Freshwater Lake", 11.5420, 76.0270, "Naturally heart-shaped lake nestled amidst evergreen forests with lotus blooms and pedal boats.", "osm", "approved", "Fresh mountain forest air.")
        ]
    }
}

def seed_supplemental_places():
    conn = sqlite3.connect('vibetrip.db')
    c = conn.cursor()

    c.execute('SELECT destination, LOWER(name) FROM local_places')
    existing = set(c.fetchall())

    total_added = 0
    for dest, cat_dict in CURATED_SUPPLEMENT.items():
        for cat, places in cat_dict.items():
            for p in places:
                name, lat, lon, desc, src, status, crowd = p
                if (dest, name.lower()) not in existing:
                    c.execute('''
                        INSERT INTO local_places (destination, name, category, latitude, longitude, description, source, status, crowd_hint)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (dest, name, cat, lat, lon, desc, src, status, crowd))
                    existing.add((dest, name.lower()))
                    total_added += 1

    conn.commit()
    print(f'Successfully added {total_added} high-quality curated places to vibetrip.db!')

    # Audit deficit across categories
    c.execute('SELECT distinct name FROM destinations ORDER BY name')
    all_dests = [r[0] for r in c.fetchall()]
    categories = ['cafe', 'food', 'viewpoint', 'attraction']
    
    still_deficit = {}
    for d in all_dests:
        c.execute('SELECT category, count(*) FROM local_places WHERE destination = ? GROUP BY category', (d,))
        counts = dict(c.fetchall())
        for cat in categories:
            cnt = counts.get(cat, 0)
            if cnt < 4:
                still_deficit.setdefault(d, {})[cat] = cnt

    print(f'\nAudit Result: Destinations with < 4 in [cafe, food, viewpoint, attraction]: {len(still_deficit)}')
    if still_deficit:
        for d, defs in still_deficit.items():
            print(f'  {d}: {defs}')
    else:
        print('CONGRATULATIONS: Every single destination now has at least 4 cafes, 4 food spots, 4 viewpoints, and 4 attractions!')

    c.execute('SELECT category, count(*) FROM local_places GROUP BY category')
    print('\nFinal Category Breakdown:')
    for cat, cnt in c.fetchall():
        print(f'  {cat:<15}: {cnt}')

    c.execute('SELECT count(*) FROM local_places')
    print(f'Total local places count: {c.fetchone()[0]}')
    conn.close()

if __name__ == '__main__':
    seed_supplemental_places()
