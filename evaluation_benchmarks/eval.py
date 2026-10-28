import csv
import math
from collections import defaultdict

def compute_metrics(ground_truth_file, predictions_file):
    # Load ground truth
    # gt_map[query_id] = set of relevant destinations
    gt_map = defaultdict(set)
    with open(ground_truth_file, "r", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            if int(row["is_relevant"]) == 1:
                gt_map[row["query_id"]].add(row["destination"])

    # Load predictions
    # pred_map[query_id] = list of destinations ordered by rank
    pred_map = defaultdict(list)
    with open(predictions_file, "r", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            pred_map[row["query_id"]].append(row["destination"])

    metrics_list = []
    for q_id, relevant_dests in gt_map.items():
        preds = pred_map.get(q_id, [])
        
        # Calculate Precision & Recall @ K
        def calc_pr_re(k):
            top_k = set(preds[:k])
            hits = len(top_k.intersection(relevant_dests))
            precision = hits / k if k > 0 else 0.0
            recall = hits / len(relevant_dests) if len(relevant_dests) > 0 else 0.0
            return precision, recall

        p5, r5 = calc_pr_re(5)
        p10, r10 = calc_pr_re(10)

        # Calculate NDCG @ K
        def calc_ndcg(k):
            dcg = 0.0
            for i, dest in enumerate(preds[:k]):
                if dest in relevant_dests:
                    dcg += 1.0 / math.log2(i + 2) # i is 0-indexed, so i+2 starts at 2
            
            idcg = 0.0
            for i in range(min(k, len(relevant_dests))):
                idcg += 1.0 / math.log2(i + 2)
                
            return dcg / idcg if idcg > 0 else 0.0

        ndcg5 = calc_ndcg(5)
        ndcg10 = calc_ndcg(10)

        metrics_list.append({
            "query_id": q_id,
            "P@5": p5, "P@10": p10,
            "R@5": r5, "R@10": r10,
            "NDCG@5": ndcg5, "NDCG@10": ndcg10
        })

    # Averages
    if len(metrics_list) > 0:
        avg_metrics = {
            "query_id": "AVERAGE",
            "P@5": sum(m["P@5"] for m in metrics_list) / len(metrics_list),
            "P@10": sum(m["P@10"] for m in metrics_list) / len(metrics_list),
            "R@5": sum(m["R@5"] for m in metrics_list) / len(metrics_list),
            "R@10": sum(m["R@10"] for m in metrics_list) / len(metrics_list),
            "NDCG@5": sum(m["NDCG@5"] for m in metrics_list) / len(metrics_list),
            "NDCG@10": sum(m["NDCG@10"] for m in metrics_list) / len(metrics_list),
        }
        metrics_list.append(avg_metrics)

    with open("eval_results.csv", "w", newline="", encoding="utf-8") as f:
        fieldnames = ["query_id", "P@5", "P@10", "R@5", "R@10", "NDCG@5", "NDCG@10"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(metrics_list)

    print(f"{'Query ID':<10} | {'P@5':<5} | {'P@10':<5} | {'R@5':<5} | {'R@10':<5} | {'NDCG@5':<7} | {'NDCG@10':<7}")
    print("-" * 65)
    for m in metrics_list:
        print(f"{m['query_id']:<10} | {m['P@5']:.3f} | {m['P@10']:.3f} | {m['R@5']:.3f} | {m['R@10']:.3f} | {m['NDCG@5']:.3f} | {m['NDCG@10']:.3f}")

if __name__ == "__main__":
    compute_metrics("ground_truth.csv", "baseline_rankings.csv")
    print("\nCreated eval_results.csv")
