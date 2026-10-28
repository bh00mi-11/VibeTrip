import csv
import json

def score_relevance(destination_row, target_dims):
    score = 0
    total_weight = 0
    for dim, direction in target_dims.items():
        if dim not in destination_row:
            continue
        try:
            val = float(destination_row[dim])
        except ValueError:
            val = 50.0
            
        if direction == "high":
            score += val
        elif direction == "low":
            score += (100.0 - val)
            
        total_weight += 1
        
    return score / total_weight if total_weight > 0 else 0

def rank_fusion():
    queries = []
    with open("test_queries.csv", "r", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            queries.append({
                "query_id": row["query_id"],
                "target_dims": json.loads(row["target_dims_json"])
            })

    destinations = []
    with open("predicted_vibe_scores.csv", "r", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            destinations.append(row)
            
    results = []
    for q in queries:
        scored_dests = []
        for dest in destinations:
            rel = score_relevance(dest, q["target_dims"])
            scored_dests.append((dest["destination"], rel))
            
        scored_dests.sort(key=lambda x: x[1], reverse=True)
        
        for rank, (dest_name, score) in enumerate(scored_dests, start=1):
            results.append({
                "query_id": q["query_id"],
                "destination": dest_name,
                "rank": rank,
                "similarity_score": score
            })
            
    with open("fusion_rankings.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["query_id", "destination", "rank", "similarity_score"])
        writer.writeheader()
        writer.writerows(results)
        
    print("Created fusion_rankings.csv")

if __name__ == "__main__":
    rank_fusion()
