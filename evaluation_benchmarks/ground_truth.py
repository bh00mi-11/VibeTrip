import csv
import json

def score_relevance(destination_row, target_dims):
    """
    Computes a simple weighted average relevance score based on target_dims.
    'high' means we want the dimension score to be as close to 100 as possible.
    'low' means we want the dimension score to be as close to 0 as possible.
    """
    score = 0
    total_weight = 0
    
    for dim, direction in target_dims.items():
        if dim not in destination_row:
            continue
        try:
            val = float(destination_row[dim])
        except ValueError:
            val = 50.0  # fallback
            
        if direction == "high":
            score += val
        elif direction == "low":
            score += (100.0 - val)
            
        total_weight += 1
        
    return score / total_weight if total_weight > 0 else 0


def generate_ground_truth():
    queries = []
    with open("test_queries.csv", "r", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            queries.append({
                "query_id": row["query_id"],
                "target_dims": json.loads(row["target_dims_json"])
            })

    destinations = []
    with open("vibe_labels_final.csv", "r", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            destinations.append(row)
            
    results = []
    for q in queries:
        scored_dests = []
        for dest in destinations:
            rel = score_relevance(dest, q["target_dims"])
            scored_dests.append((dest["destination"], rel))
            
        # Sort by relevance desc
        scored_dests.sort(key=lambda x: x[1], reverse=True)
        
        # Mark top 10 as relevant (is_relevant=1)
        for i, (dest_name, rel) in enumerate(scored_dests):
            is_relevant = 1 if i < 10 else 0
            results.append({
                "query_id": q["query_id"],
                "destination": dest_name,
                "relevance_score": rel,
                "is_relevant": is_relevant
            })
            
    with open("ground_truth.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["query_id", "destination", "relevance_score", "is_relevant"])
        writer.writeheader()
        writer.writerows(results)

if __name__ == "__main__":
    generate_ground_truth()
    print("Created ground_truth.csv")
