import csv

new_destinations = [
    ["Port Blair", "Andaman and Nicobar Islands", "Islands", "Coastal", "Oct-May", "Cellular Jail|Ross Island|Corbyn's Cove|Chidiya Tapu", "Capital of the Andaman Islands known for its colonial history.", "images/Port Blair", "5", "8"],
    ["Pune", "Maharashtra", "West", "City", "Oct-Mar", "Shaniwar Wada|Aga Khan Palace|Dagdusheth Halwai Ganpati Temple|Sinhagad Fort", "Cultural capital of Maharashtra with a mix of history and modern life.", "images/Pune", "5", "8"],
    ["Ahmedabad", "Gujarat", "West", "Heritage", "Oct-Mar", "Sabarmati Ashram|Adalaj Stepwell|Kankaria Lake|Jama Masjid Ahmedabad", "India's first UNESCO World Heritage City.", "images/Ahmedabad", "5", "8"],
    ["Rann of Kutch", "Gujarat", "West", "Desert", "Nov-Feb", "Great Rann of Kutch|Kala Dungar|Mandvi Beach|Dholavira", "Vast white salt desert famous for the Rann Utsav.", "images/Rann of Kutch", "5", "8"],
    ["Mahabaleshwar", "Maharashtra", "West", "Hill Station", "Oct-Jun", "Pratapgad Fort|Venna Lake|Elephant's Head Point|Arthur's Seat Mahabaleshwar", "A picturesque hill station in the Western Ghats known for strawberries.", "images/Mahabaleshwar", "5", "8"],
    ["Bhopal", "Madhya Pradesh", "Central", "Lakes/Heritage", "Oct-Mar", "Upper Lake Bhopal|Taj-ul-Masajid|Sanchi Stupa|Bhimbetka rock shelters", "The City of Lakes with deep historical roots.", "images/Bhopal", "5", "8"],
    ["Ujjain", "Madhya Pradesh", "Central", "Spiritual", "Oct-Mar", "Mahakaleshwar Jyotirlinga|Kal Bhairav Temple|Ram Ghat Ujjain|Harsiddhi Temple", "Ancient city on the banks of the Kshipra River.", "images/Ujjain", "5", "8"],
    ["Pachmarhi", "Madhya Pradesh", "Central", "Hill Station", "Oct-Jun", "Bee Falls|Jata Shankar Caves|Dhoopgarh|Pandav Caves", "The Queen of Satpura known for waterfalls and ancient caves.", "images/Pachmarhi", "5", "8"],
    ["Puri", "Odisha", "East", "Spiritual/Beach", "Oct-Mar", "Jagannath Temple Puri|Puri Beach|Chilika Lake|Konark Sun Temple", "Holy city and coastal destination on the Bay of Bengal.", "images/Puri", "5", "8"],
    ["Bhubaneswar", "Odisha", "East", "Heritage", "Oct-Mar", "Lingaraja Temple|Udayagiri and Khandagiri Caves|Nandankanan Zoological Park|Muktesvara Temple", "The Temple City of India.", "images/Bhubaneswar", "5", "8"],
    ["Bodh Gaya", "Bihar", "East", "Spiritual", "Oct-Mar", "Mahabodhi Temple|Bodhi Tree|Great Buddha Statue Bodhgaya|Vishnupad Temple", "Sacred Buddhist pilgrimage site where Gautama Buddha attained enlightenment.", "images/Bodh Gaya", "5", "8"],
    ["Tawang", "Arunachal Pradesh", "Northeast", "Mountains", "Mar-Jun and Sep-Oct", "Tawang Monastery|Sela Pass|Madhuri Lake|Nuranang Falls", "High-altitude town known for its large Buddhist monastery.", "images/Tawang", "5", "8"],
    ["Kaziranga", "Assam", "Northeast", "Nature", "Nov-Apr", "Kaziranga National Park|Orchid And Biodiversity Park|Majuli|Kakochang Waterfalls", "Home to the world's largest population of one-horned rhinoceroses.", "images/Kaziranga", "5", "8"],
    ["Cherrapunji", "Meghalaya", "Northeast", "Nature", "Oct-May", "Nohkalikai Falls|Double Decker Living Root Bridge|Mawsmai Cave|Seven Sisters Falls", "One of the wettest places on earth with stunning waterfalls.", "images/Cherrapunji", "5", "8"],
    ["Kanyakumari", "Tamil Nadu", "South", "Coastal", "Oct-Mar", "Vivekananda Rock Memorial|Thiruvalluvar Statue|Kanyakumari Beach|Padmanabhapuram Palace", "The southernmost tip of the Indian subcontinent.", "images/Kanyakumari", "5", "8"],
    ["Mahabalipuram", "Tamil Nadu", "South", "Heritage", "Oct-Mar", "Shore Temple|Pancha Rathas|Descent of the Ganges|Krishna's Butterball", "Ancient port city known for rock-cut monuments.", "images/Mahabalipuram", "5", "8"],
    ["Wayanad", "Kerala", "South", "Nature", "Oct-May", "Edakkal Caves|Chembra Peak|Banasura Sagar Dam|Soochipara Falls", "Lush green district with waterfalls and spice plantations.", "images/Wayanad", "5", "8"],
    ["Auli", "Uttarakhand", "North", "Mountains", "Nov-Mar", "Auli Ski Resort|Gurso Bugyal|Kwani Bugyal|Trishul Peak", "Premier ski destination in India with panoramic Himalayan views.", "images/Auli", "5", "8"]
]

with open("destinations.csv", "a", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerows(new_destinations)
