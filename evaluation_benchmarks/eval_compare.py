import csv
import math
from collections import defaultdict

def evaluate_rankings(ground_truth_file, predictions_file):
    # Load ground truth
    gt_map = defaultdict(set)
    with open(ground_truth_file, "r", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            if int(row["is_relevant"]) == 1:
                gt_map[row["query_id"]].add(row["destination"])

    # Load predictions
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
                    dcg += 1.0 / math.log2(i + 2)
            
            idcg = 0.0
            for i in range(min(k, len(relevant_dests))):
                idcg += 1.0 / math.log2(i + 2)
                
            return dcg / idcg if idcg > 0 else 0.0

        metrics_list.append({
            "P@5": p5, "P@10": p10,
            "R@5": r5, "R@10": r10,
            "NDCG@5": calc_ndcg(5), "NDCG@10": calc_ndcg(10)
        })

    # Averages
    if len(metrics_list) > 0:
        return {
            "P@5": sum(m["P@5"] for m in metrics_list) / len(metrics_list),
            "P@10": sum(m["P@10"] for m in metrics_list) / len(metrics_list),
            "R@5": sum(m["R@5"] for m in metrics_list) / len(metrics_list),
            "R@10": sum(m["R@10"] for m in metrics_list) / len(metrics_list),
            "NDCG@5": sum(m["NDCG@5"] for m in metrics_list) / len(metrics_list),
            "NDCG@10": sum(m["NDCG@10"] for m in metrics_list) / len(metrics_list),
        }
    return None

def main():
    gt_file = "ground_truth.csv"
    models = {
        "Full Model (Fusion)": "fusion_rankings.csv",
        "Remove Image (Text)": "text_rankings.csv",
        "Remove Text (Visual)": "visual_rankings_maxpool.csv",
        "Remove Vibe Layer": "ablation_no_vibe_rankings.csv",
        "Remove Metadata": "ablation_no_metadata_rankings.csv",
        "Baseline (no DL)": "baseline_rankings.csv"
    }
    
    results = []
    
    for model_name, pred_file in models.items():
        try:
            avg_metrics = evaluate_rankings(gt_file, pred_file)
            if avg_metrics:
                avg_metrics["Model"] = model_name
                results.append(avg_metrics)
            else:
                print(f"Warning: No metrics computed for {model_name}")
        except FileNotFoundError:
            print(f"Warning: {pred_file} not found. Skipping {model_name}.")
            
    # Write comparison CSV
    if results:
        with open("ablation_results.csv", "w", newline="", encoding="utf-8") as f:
            fieldnames = ["Model", "P@5", "P@10", "R@5", "R@10", "NDCG@5", "NDCG@10"]
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)
            
        # Print table
        print(f"{'Model':<10} | {'P@5':<5} | {'P@10':<5} | {'R@5':<5} | {'R@10':<5} | {'NDCG@5':<7} | {'NDCG@10':<7}")
        print("-" * 65)
        for m in results:
            print(f"{m['Model']:<10} | {m['P@5']:.3f} | {m['P@10']:.3f} | {m['R@5']:.3f} | {m['R@10']:.3f} | {m['NDCG@5']:.3f} | {m['NDCG@10']:.3f}")
            
if __name__ == "__main__":
    main()
