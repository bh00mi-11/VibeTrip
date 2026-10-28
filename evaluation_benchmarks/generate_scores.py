import csv

# Scores map: destination -> (nature, adventure, peacefulness, crowd_match, visual_atmosphere)
scores_map = {
    "Agra": (10, 10, 20, 10, 100),
    "Jaipur": (40, 20, 40, 30, 80),
    "Udaipur": (50, 20, 60, 40, 90),
    "Jodhpur": (40, 20, 50, 50, 80),
    "Jaisalmer": (70, 50, 60, 50, 80),
    "Delhi": (10, 10, 10, 10, 70),
    "Varanasi": (30, 10, 20, 10, 90),
    "Amritsar": (20, 10, 60, 30, 80),
    "Rishikesh": (80, 90, 60, 40, 80),
    "Haridwar": (50, 10, 30, 20, 70),
    "Manali": (90, 80, 60, 30, 90),
    "Shimla": (70, 30, 50, 20, 70),
    "Leh": (100, 90, 90, 70, 100),
    "Srinagar": (80, 30, 70, 40, 90),
    "Darjeeling": (80, 30, 70, 40, 80),
    "Kolkata": (10, 10, 20, 20, 50),
    "Gangtok": (80, 50, 70, 70, 80),
    "Shillong": (90, 40, 80, 90, 80),
    "Khajuraho": (40, 10, 70, 70, 80),
    "Mumbai": (20, 10, 20, 10, 60),
    "Goa": (70, 50, 40, 10, 80),
    "Hampi": (60, 40, 80, 60, 90),
    "Mysore": (40, 10, 60, 40, 70),
    "Coorg": (90, 40, 80, 60, 80),
    "Hyderabad": (20, 10, 30, 20, 60),
    "Kochi": (40, 10, 60, 50, 70),
    "Munnar": (100, 30, 90, 50, 90),
    "Alleppey": (90, 10, 90, 40, 90),
    "Ooty": (80, 30, 60, 30, 70),
    "Madurai": (10, 10, 30, 30, 70),
    "Pondicherry": (50, 20, 70, 50, 80),
    "Havelock Island": (100, 90, 90, 90, 100),
    "Port Blair": (80, 40, 70, 70, 70),
    "Pune": (20, 10, 30, 30, 50),
    "Ahmedabad": (10, 10, 30, 30, 60),
    "Rann of Kutch": (90, 40, 90, 60, 90),
    "Mahabaleshwar": (80, 30, 60, 40, 70),
    "Bhopal": (40, 10, 60, 60, 60),
    "Ujjain": (20, 10, 50, 40, 60),
    "Pachmarhi": (90, 50, 80, 70, 80),
    "Puri": (60, 20, 50, 30, 70),
    "Bhubaneswar": (30, 10, 50, 50, 60),
    "Bodh Gaya": (30, 10, 80, 60, 70),
    "Tawang": (90, 60, 90, 90, 90),
    "Kaziranga": (100, 60, 80, 60, 80),
    "Cherrapunji": (100, 50, 80, 70, 90),
    "Kanyakumari": (70, 10, 60, 30, 80),
    "Mahabalipuram": (50, 10, 60, 50, 80),
    "Wayanad": (100, 50, 80, 70, 90),
    "Auli": (100, 90, 90, 80, 90)
}

def main():
    destinations_file = "destinations.csv"
    output_file = "vibe_labels_scored.csv"
    
    rows_to_write = []
    
    # Read destinations to keep exact order and spelling
    with open(destinations_file, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            dest = row.get("destination")
            if not dest:
                continue
            
            if dest in scores_map:
                n, a, p, c, v = scores_map[dest]
                rows_to_write.append({
                    "destination": dest,
                    "nature": n,
                    "adventure": a,
                    "peacefulness": p,
                    "crowd_match": c,
                    "visual_atmosphere": v,
                    "draft_by_ai": "TRUE"
                })
            else:
                rows_to_write.append({
                    "destination": dest,
                    "nature": "",
                    "adventure": "",
                    "peacefulness": "",
                    "crowd_match": "",
                    "visual_atmosphere": "",
                    "draft_by_ai": "TRUE"
                })
                
    # Write vibe_labels.csv
    with open(output_file, "w", newline="", encoding="utf-8") as f:
        fieldnames = ["destination", "nature", "adventure", "peacefulness", "crowd_match", "visual_atmosphere", "draft_by_ai"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows_to_write)
            
if __name__ == "__main__":
    main()
