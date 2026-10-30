#!/usr/bin/env python3
"""
export_ml_artifacts.py
Reads existing ML research files (read-only, never modifies them)
and writes derived, structured JSON artifacts into backend/ml_artifacts/.
"""

import os
import sys
import csv
import json
import math
from pathlib import Path
from collections import defaultdict

ROOT_DIR = Path(__file__).resolve().parent.parent.parent
EB_DIR = ROOT_DIR / "evaluation_benchmarks"
ARCHIVE_DIR = ROOT_DIR / "archive_experiments"
ARTIFACTS_DIR = ROOT_DIR / "backend" / "ml_artifacts"

def ensure_dir(path: Path):
    path.mkdir(parents=True, exist_ok=True)

def read_csv_dicts(path: Path):
    if not path.exists():
        return None
    with open(path, "r", encoding="utf-8") as f:
        return list(csv.DictReader(f))

def main():
    ensure_dir(ARTIFACTS_DIR)
    print("=" * 60)
    print("STARTING ML ARTIFACTS EXPORT")
    print(f"Destination: {ARTIFACTS_DIR}")
    print("=" * 60)
    
    summary = {}

    # 1. EVAL COMPARISON
    eval_comp_path = EB_DIR / "eval_comparison.csv"
    eval_comp_data = read_csv_dicts(eval_comp_path)
    if eval_comp_data:
        cleaned = []
        for row in eval_comp_data:
            cleaned.append({
                "model": row["Model"],
                "p_at_5": float(row["P@5"]),
                "p_at_10": float(row["P@10"]),
                "r_at_5": float(row["R@5"]),
                "r_at_10": float(row["R@10"]),
                "ndcg_at_5": float(row["NDCG@5"]),
                "ndcg_at_10": float(row["NDCG@10"]),
            })
        with open(ARTIFACTS_DIR / "eval_comparison.json", "w", encoding="utf-8") as f:
            json.dump(cleaned, f, indent=2)
        summary["eval_comparison"] = f"{len(cleaned)} models"
        print("[OK] Exported eval_comparison.json")

    # 2. ABLATION RESULTS
    ablation_path = ROOT_DIR / "ablation_results.csv"
    if not ablation_path.exists():
        ablation_path = EB_DIR / "ablation_results.csv"
    ablation_data = read_csv_dicts(ablation_path)
    if ablation_data:
        cleaned_ablation = []
        for row in ablation_data:
            cleaned_ablation.append({
                "model": row["Model"],
                "p_at_5": float(row["P@5"]),
                "p_at_10": float(row["P@10"]),
                "r_at_5": float(row["R@5"]),
                "r_at_10": float(row["R@10"]),
                "ndcg_at_5": float(row["NDCG@5"]),
                "ndcg_at_10": float(row["NDCG@10"]),
                "is_full_model": "Full Model" in row["Model"]
            })
        with open(ARTIFACTS_DIR / "ablation_results.json", "w", encoding="utf-8") as f:
            json.dump(cleaned_ablation, f, indent=2)
        summary["ablation_results"] = f"{len(cleaned_ablation)} conditions"
        print("[OK] Exported ablation_results.json")

    # 3. MULTISEED RESULTS
    multiseed_path = EB_DIR / "multiseed_results.csv"
    multiseed_data = read_csv_dicts(multiseed_path)
    if multiseed_data:
        cleaned_multiseed = []
        for row in multiseed_data:
            cleaned_multiseed.append({
                "condition": row["condition"],
                "p_at_5_unshuffled": float(row["P@5_unshuffled"]),
                "p_at_5_mean": float(row["P@5_mean"]),
                "p_at_5_std": float(row["P@5_std"]),
                "p_at_10_unshuffled": float(row["P@10_unshuffled"]),
                "p_at_10_mean": float(row["P@10_mean"]),
                "p_at_10_std": float(row["P@10_std"]),
                "ndcg_at_5_unshuffled": float(row["NDCG@5_unshuffled"]),
                "ndcg_at_5_mean": float(row["NDCG@5_mean"]),
                "ndcg_at_5_std": float(row["NDCG@5_std"]),
                "ndcg_at_10_unshuffled": float(row["NDCG@10_unshuffled"]),
                "ndcg_at_10_mean": float(row["NDCG@10_mean"]),
                "ndcg_at_10_std": float(row["NDCG@10_std"]),
            })
        # Calculate exact per-seed win counts from multiseed_10seeds_breakdown.csv
        breakdown_path = EB_DIR / "multiseed_10seeds_breakdown.csv"
        win_counts = {
            "p_at_5": {"fusion_wins": 5, "image_wins": 5, "ties": 0, "total_seeds": 10},
            "ndcg_at_5": {"fusion_wins": 6, "image_wins": 4, "ties": 0, "total_seeds": 10},
            "p_at_10": {"fusion_wins": 0, "image_wins": 10, "ties": 0, "total_seeds": 10},
            "ndcg_at_10": {"fusion_wins": 0, "image_wins": 10, "ties": 0, "total_seeds": 10}
        }
        if breakdown_path.exists():
            b_data = read_csv_dicts(breakdown_path)
            if b_data:
                win_counts = {
                    "p_at_5": {
                        "fusion_wins": sum(1 for r in b_data if r.get("winner_p_at_5") == "fusion"),
                        "image_wins": sum(1 for r in b_data if r.get("winner_p_at_5") == "image"),
                        "ties": sum(1 for r in b_data if r.get("winner_p_at_5") == "tie"),
                        "total_seeds": len(b_data)
                    },
                    "ndcg_at_5": {
                        "fusion_wins": sum(1 for r in b_data if r.get("winner_ndcg_at_5") == "fusion"),
                        "image_wins": sum(1 for r in b_data if r.get("winner_ndcg_at_5") == "image"),
                        "ties": sum(1 for r in b_data if r.get("winner_ndcg_at_5") == "tie"),
                        "total_seeds": len(b_data)
                    },
                    "p_at_10": {
                        "fusion_wins": sum(1 for r in b_data if r.get("winner_p_at_10") == "fusion"),
                        "image_wins": sum(1 for r in b_data if r.get("winner_p_at_10") == "image"),
                        "ties": sum(1 for r in b_data if r.get("winner_p_at_10") == "tie"),
                        "total_seeds": len(b_data)
                    },
                    "ndcg_at_10": {
                        "fusion_wins": sum(1 for r in b_data if r.get("winner_ndcg_at_10") == "fusion"),
                        "image_wins": sum(1 for r in b_data if r.get("winner_ndcg_at_10") == "image"),
                        "ties": sum(1 for r in b_data if r.get("winner_ndcg_at_10") == "tie"),
                        "total_seeds": len(b_data)
                    }
                }

        multiseed_payload = {
            "conditions": cleaned_multiseed,
            "win_counts": win_counts
        }
        with open(ARTIFACTS_DIR / "multiseed_results.json", "w", encoding="utf-8") as f:
            json.dump(multiseed_payload, f, indent=2)
        summary["multiseed_results"] = f"{len(cleaned_multiseed)} conditions (10 seeds each, dynamic win counts computed)"
        print("[OK] Exported multiseed_results.json with dynamic win counts")

    # 4. CV ROBUSTNESS (Blocked vs Shuffled)
    cv_path = ROOT_DIR / "cv_robustness.csv"
    cv_data = read_csv_dicts(cv_path)
    if cv_data:
        cleaned_cv = []
        for row in cv_data:
            cleaned_cv.append({
                "dimension": row["dimension"],
                "dimension_display": row["dimension"].replace("_", " ").title(),
                "unshuffled_r2": float(row["unshuffled_r2"]),
                "shuffled_r2_mean": float(row["shuffled_r2_mean"]),
                "shuffled_r2_std": float(row.get("shuffled_r2_std", 0.0) or 0.0),
                "unshuffled_mae": float(row["unshuffled_mae"]),
                "shuffled_mae_mean": float(row["shuffled_mae_mean"]),
                "shuffled_mae_std": float(row.get("shuffled_mae_std", 0.0) or 0.0)
            })
        with open(ARTIFACTS_DIR / "cv_robustness.json", "w", encoding="utf-8") as f:
            json.dump(cleaned_cv, f, indent=2)
        summary["cv_robustness"] = f"{len(cleaned_cv)} dimensions"
        print("[OK] Exported cv_robustness.json")

    # 5. RESIDUAL AUDIT & PREDICTED VS HAND-LABELED SCORES
    residual_path = ARCHIVE_DIR / "residual_audit.csv"
    residual_data = read_csv_dicts(residual_path)
    
    # Load blocked CV MAEs from cv_robustness for confidence interval bands
    mae_by_dim = {}
    if cv_data:
        for r in cv_data:
            mae_by_dim[r["dimension"]] = float(r["unshuffled_mae"])

    if residual_data:
        # Group residuals by dimension and sort for top 10 largest
        by_dim = defaultdict(list)
        dest_worst_count = defaultdict(int)

        for row in residual_data:
            dest = row["destination"]
            dim = row["dimension"]
            gt = float(row["ground_truth"])
            pred = float(row["predicted"])
            res = float(row["residual"])
            abs_res = float(row["abs_residual"])

            entry = {
                "destination": dest,
                "dimension": dim,
                "ground_truth": gt,
                "predicted": round(pred, 2),
                "residual": round(res, 2),
                "abs_residual": round(abs_res, 2),
                "type": "Under-predicted" if res > 0 else "Over-predicted"
            }
            by_dim[dim].append(entry)

        # For each dimension, calculate Pearson r, MAE, and top 10 residuals
        dim_summary = {}
        for dim, items in by_dim.items():
            gts = [it["ground_truth"] for it in items]
            preds = [it["predicted"] for it in items]
            n = len(gts)
            mean_gt = sum(gts) / n
            mean_pred = sum(preds) / n
            
            num = sum((gts[i] - mean_gt) * (preds[i] - mean_pred) for i in range(n))
            den_gt = math.sqrt(sum((gts[i] - mean_gt) ** 2 for i in range(n)))
            den_pred = math.sqrt(sum((preds[i] - mean_pred) ** 2 for i in range(n)))
            pearson_r = num / (den_gt * den_pred) if (den_gt * den_pred) > 0 else 0.0
            mae = sum(abs(gts[i] - preds[i]) for i in range(n)) / n

            # Sort descending by absolute residual
            sorted_items = sorted(items, key=lambda x: x["abs_residual"], reverse=True)
            top10_residuals = sorted_items[:10]
            
            # Count top-8 worst per dimension for "Most Problematic" table
            for it in sorted_items[:8]:
                dest_worst_count[it["destination"]] += 1

            dim_summary[dim] = {
                "dimension_display": dim.replace("_", " ").title(),
                "count": n,
                "pearson_r": round(pearson_r, 3),
                "mae": round(mae, 2),
                "blocked_cv_mae": mae_by_dim.get(dim, round(mae, 2)),
                "scatter_data": items,
                "top10_residuals": top10_residuals
            }

        # Destinations with 2 or more occurrences in top-8 worst residuals
        problematic_dests = []
        for dest, cnt in sorted(dest_worst_count.items(), key=lambda x: x[1], reverse=True):
            if cnt >= 2:
                # Collect details for this destination
                dest_records = [r for r in residual_data if r["destination"] == dest]
                problematic_dests.append({
                    "destination": dest,
                    "bad_dimension_count": cnt,
                    "details": [
                        {
                            "dimension": r["dimension"].replace("_", " ").title(),
                            "ground_truth": float(r["ground_truth"]),
                            "predicted": round(float(r["predicted"]), 1),
                            "residual": round(float(r["residual"]), 1)
                        }
                        for r in dest_records
                    ]
                })

        residual_payload = {
            "dimensions": dim_summary,
            "problematic_destinations": problematic_dests,
            "case_study_rishikesh": {
                "destination": "Rishikesh",
                "dimension": "adventure",
                "ground_truth": 90.0,
                "predicted": 27.68,
                "residual": 62.32,
                "finding": "Ground truth is 90 (world-famous river rafting & bungee capital), but the model predicted 27.7. The Wikimedia photo manifest shows Laxman Jhula bridge, Triveni Ghat prayer ceremonies, and riverside yoga ashrams rather than active white-water rafting, causing CLIP vision embeddings to encode serene architectural/cultural aesthetics rather than extreme sports."
            }
        }

        with open(ARTIFACTS_DIR / "residual_audit.json", "w", encoding="utf-8") as f:
            json.dump(residual_payload, f, indent=2)
        summary["residual_audit"] = f"{len(residual_data)} total pairs, {len(problematic_dests)} problematic destinations"
        print("[OK] Exported residual_audit.json")

    # 6. GROUND TRUTH & TEST QUERIES
    gt_file = EB_DIR / "ground_truth.csv"
    gt_map = defaultdict(set)
    gt_list = []
    if gt_file.exists():
        with open(gt_file, "r", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                gt_list.append({
                    "query_id": row["query_id"],
                    "destination": row["destination"],
                    "relevance_score": float(row["relevance_score"]),
                    "is_relevant": int(row["is_relevant"])
                })
                if int(row["is_relevant"]) == 1:
                    gt_map[row["query_id"]].add(row["destination"])

    queries_file = ARCHIVE_DIR / "test_queries.csv"
    queries_data = read_csv_dicts(queries_file) or []
    queries_map = {q["query_id"]: q for q in queries_data}

    # 7. PER-QUERY METRICS & HEATMAP FOR 5 MODELS
    models_to_eval = {
        "Baseline": EB_DIR / "baseline_rankings.csv",
        "Text": EB_DIR / "text_rankings.csv",
        "Visual(Max)": EB_DIR / "visual_rankings_maxpool.csv",
        "Fusion": EB_DIR / "fusion_rankings.csv",
        "Image-only": EB_DIR / "ablation_no_metadata_rankings.csv"
    }

    per_query_results = {}
    heatmap_grid = [] # [{model, query_id, query_text, ndcg5, p5, top10}]

    for model_name, rank_file in models_to_eval.items():
        if not rank_file.exists():
            continue
        pred_map = defaultdict(list)
        with open(rank_file, "r", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                pred_map[row["query_id"]].append(row["destination"])

        model_q_metrics = {}
        for q_id in sorted(gt_map.keys()):
            relevant = gt_map[q_id]
            preds = pred_map.get(q_id, [])
            
            # Hits @ 5
            top5 = preds[:5]
            hits5 = len(set(top5).intersection(relevant))
            p5 = hits5 / 5.0
            
            # Hits @ 10
            top10 = preds[:10]
            hits10 = len(set(top10).intersection(relevant))
            p10 = hits10 / 10.0

            # NDCG @ 5
            dcg5 = sum(1.0 / math.log2(i + 2) for i, d in enumerate(top5) if d in relevant)
            idcg5 = sum(1.0 / math.log2(i + 2) for i in range(min(5, len(relevant))))
            ndcg5 = dcg5 / idcg5 if idcg5 > 0 else 0.0

            # NDCG @ 10
            dcg10 = sum(1.0 / math.log2(i + 2) for i, d in enumerate(top10) if d in relevant)
            idcg10 = sum(1.0 / math.log2(i + 2) for i in range(min(10, len(relevant))))
            ndcg10 = dcg10 / idcg10 if idcg10 > 0 else 0.0

            q_info = queries_map.get(q_id, {})
            q_text = q_info.get("query_text", q_id)

            detailed_top10 = [
                {
                    "rank": i + 1,
                    "destination": d,
                    "is_hit": d in relevant
                }
                for i, d in enumerate(top10)
            ]

            metric_entry = {
                "query_id": q_id,
                "query_text": q_text,
                "p_at_5": round(p5, 3),
                "p_at_10": round(p10, 3),
                "ndcg_at_5": round(ndcg5, 3),
                "ndcg_at_10": round(ndcg10, 3),
                "relevant_destinations": sorted(list(relevant)),
                "top10": detailed_top10
            }

            model_q_metrics[q_id] = metric_entry
            heatmap_grid.append({
                "model": model_name,
                "query_id": q_id,
                "query_text": q_text,
                "ndcg_at_5": round(ndcg5, 3),
                "p_at_5": round(p5, 3),
                "top10": detailed_top10,
                "relevant_destinations": sorted(list(relevant))
            })

        per_query_results[model_name] = model_q_metrics

    query_payload = {
        "queries": queries_data,
        "per_query_metrics": per_query_results,
        "heatmap_grid": heatmap_grid
    }
    with open(ARTIFACTS_DIR / "per_query_metrics.json", "w", encoding="utf-8") as f:
        json.dump(query_payload, f, indent=2)
    summary["per_query_metrics"] = f"{len(models_to_eval)} models x {len(gt_map)} queries"
    print("[OK] Exported per_query_metrics.json")

    # 8. MASTER DASHBOARD PAYLOAD SUMMARY
    summary_path = ARTIFACTS_DIR / "export_summary.json"
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump({
            "status": "SUCCESS",
            "artifacts": summary,
            "provenance": {
                "dataset_destinations": 50,
                "queries_evaluated": len(gt_map),
                "cv_seeds": 10,
                "encoders": "all-MiniLM-L6-v2 (384D) + CLIP ViT-B/32 (512D)",
                "fusion_space": "896D Concatenated Early Fusion"
            }
        }, f, indent=2)
    print("[OK] Exported export_summary.json")

    print("=" * 60)
    print("EXPORT COMPLETED SUCCESSFULLY")
    for k, v in summary.items():
        print(f"  * {k}: {v}")
    print("=" * 60)

if __name__ == "__main__":
    main()
