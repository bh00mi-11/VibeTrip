import csv
import numpy as np
import json
from sklearn.linear_model import Ridge
from sklearn.model_selection import cross_val_predict

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

def run_no_metadata():
    destinations = []
    with open("fused_destinations.csv", "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        next(reader)
        for row in reader:
            destinations.append(row[0])
            
    fused_X = np.load("fused_embeddings.npy")
    # Drop text/metadata part (first 384 dims) and keep only image part
    X = fused_X[:, 384:]
    
    dims = ["nature", "adventure", "peacefulness", "crowd_match", "visual_atmosphere"]
    gt_scores = {}
    with open("vibe_labels_final.csv", "r", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            gt_scores[row["destination"]] = {d: float(row[d]) for d in dims}
            
    Y = {d: [] for d in dims}
    for dest in destinations:
        for d in dims:
            Y[d].append(gt_scores[dest][d])
            
    for d in dims:
        Y[d] = np.array(Y[d])
        
    predictions_out = {dest: {} for dest in destinations}
    
    for d in dims:
        y = Y[d]
        model = Ridge(alpha=1.0)
        preds = cross_val_predict(model, X, y, cv=5)
        for i, dest in enumerate(destinations):
            predictions_out[dest][d] = np.clip(preds[i], 0, 100)
            
    # Write predictions out
    pred_list = []
    for dest in destinations:
        row = {"destination": dest}
        row.update(predictions_out[dest])
        pred_list.append(row)
        
    queries = []
    with open("test_queries.csv", "r", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            queries.append({
                "query_id": row["query_id"],
                "target_dims": json.loads(row["target_dims_json"])
            })

    results = []
    for q in queries:
        scored_dests = []
        for dest_row in pred_list:
            rel = score_relevance(dest_row, q["target_dims"])
            scored_dests.append((dest_row["destination"], rel))
            
        scored_dests.sort(key=lambda x: x[1], reverse=True)
        
        for rank, (dest_name, score) in enumerate(scored_dests, start=1):
            results.append({
                "query_id": q["query_id"],
                "destination": dest_name,
                "rank": rank,
                "similarity_score": score
            })
            
    with open("ablation_no_metadata_rankings.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["query_id", "destination", "rank", "similarity_score"])
        writer.writeheader()
        writer.writerows(results)
        
    print("Created ablation_no_metadata_rankings.csv")

if __name__ == "__main__":
    run_no_metadata()
