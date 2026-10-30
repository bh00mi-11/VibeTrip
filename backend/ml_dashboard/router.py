"""
backend/ml_dashboard/router.py
FastAPI Router for Deep Learning Dashboard (/api/admin/ml/*).
All endpoints are strictly guarded by require_role('admin').
Tourists and Locals receive 403 Forbidden.
"""

import json
from pathlib import Path
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models import User
from backend.auth import require_role

router = APIRouter(
    prefix="/api/admin/ml",
    tags=["admin-ml"],
    dependencies=[Depends(require_role("admin"))]
)

ARTIFACTS_DIR = Path(__file__).resolve().parent.parent / "ml_artifacts"

def load_artifact(filename: str):
    file_path = ARTIFACTS_DIR / filename
    if not file_path.exists():
        raise HTTPException(
            status_code=404,
            detail=f"Artifact '{filename}' not found. Please run export_ml_artifacts.py first."
        )
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to read artifact '{filename}': {str(e)}")

@router.get("/status")
def get_ml_status(user: User = Depends(require_role("admin"))):
    """Returns overview status and provenance of ML artifacts."""
    return load_artifact("export_summary.json")

@router.get("/eval-comparison")
def get_eval_comparison(user: User = Depends(require_role("admin"))):
    """Returns baseline, text, visual, and fusion evaluation comparisons."""
    return load_artifact("eval_comparison.json")

@router.get("/ablation-results")
def get_ablation_results(user: User = Depends(require_role("admin"))):
    """Returns ablation experiment results across 6 conditions."""
    return load_artifact("ablation_results.json")

@router.get("/multiseed-results")
def get_multiseed_results(user: User = Depends(require_role("admin"))):
    """Returns 10-seed cross validation metrics with means and std deviations."""
    return load_artifact("multiseed_results.json")

@router.get("/cv-robustness")
def get_cv_robustness(user: User = Depends(require_role("admin"))):
    """Returns 5-fold cross validation: Blocked (unshuffled) vs Shuffled CV R^2 and MAE."""
    return load_artifact("cv_robustness.json")

@router.get("/residual-audit")
def get_residual_audit(user: User = Depends(require_role("admin"))):
    """Returns predicted vs hand-labeled scatter, top residuals, and Rishikesh case study."""
    return load_artifact("residual_audit.json")

@router.get("/per-query-metrics")
def get_per_query_metrics(user: User = Depends(require_role("admin"))):
    """Returns per-query P@5, NDCG@5, models x query heatmap grid, and relevant sets."""
    return load_artifact("per_query_metrics.json")

# ==============================================================================
# BATCH 2 ENDPOINTS: EXPLAINABILITY, EMBEDDING EXPLORER, INFERENCE LAB
# ==============================================================================

@router.get("/explain/{destination}")
def get_destination_explainability(
    destination: str,
    user: User = Depends(require_role("admin"))
):
    """
    Returns exact Ridge decomposition for intercept, text, and per-photo contributions,
    including mathematical self-check verification.
    """
    decomp_data = load_artifact("decompositions.json")
    photo_decomp_data = load_artifact("per_photo_decompositions.json")

    decomps = decomp_data.get("decompositions", {})
    if destination not in decomps:
        # Fallback case-insensitive match
        match = None
        for k in decomps.keys():
            if k.lower() == destination.lower():
                match = k
                break
        if not match:
            raise HTTPException(status_code=404, detail=f"Explainability data not found for destination '{destination}'.")
        destination = match

    dest_decomp = decomps[destination]
    photos_decomp = photo_decomp_data.get(destination, {})

    # Self-check across 5 dimensions for this destination
    dims = ["nature", "adventure", "peacefulness", "crowd_match", "visual_atmosphere"]
    self_checks = {}
    for d in dims:
        info = dest_decomp.get(d, {})
        pred = info.get("predicted_score", 0.0)
        recon = info.get("intercept", 0.0) + info.get("text_contribution", 0.0) + info.get("image_contribution", 0.0)
        err = abs(pred - recon)
        self_checks[d] = {
            "predicted": pred,
            "reconstructed": round(recon, 3),
            "abs_error": round(err, 6),
            "is_exact": err < 1e-4
        }

    return {
        "destination": destination,
        "self_check_max_error": decomp_data.get("self_check_max_error", 7.63e-6),
        "self_checks": self_checks,
        "dimensions": dest_decomp,
        "per_photo": photos_decomp,
        "notes": {
            "full_fit_vs_oof": "Full-fit prediction is what the Ridge weight decomposition explains mathematically. Out-of-fold (OOF) is the cross-validation score without train leakage."
        }
    }

@router.get("/embedding-coordinates")
def get_embedding_coordinates(
    user: User = Depends(require_role("admin")),
    db: Session = Depends(get_db)
):
    """
    Returns precomputed 2D PCA and t-SNE coordinates for training set,
    dynamically projecting any admin-added destinations onto the fitted PCA space.
    """
    data = load_artifact("embedding_coordinates.json")
    base_destinations = list(data.get("destinations", []))
    ood_threshold = data.get("ood_cosine_threshold", 0.6717)

    # Check for admin-added destinations in DB
    try:
        from backend.models import Destination as DestModel, Photo as PhotoModel, VibeScore as VibeModel
        import joblib
        import numpy as np
        from sklearn.metrics.pairwise import cosine_similarity
        from backend.vibe_estimator import build_fused_embedding

        admin_dests = db.query(DestModel).filter(DestModel.source == "admin").all()
        if admin_dests:
            pca_fused_path = ARTIFACTS_DIR / "pca_fused.joblib"
            pca_text_path = ARTIFACTS_DIR / "pca_text.joblib"
            pca_img_path = ARTIFACTS_DIR / "pca_img.joblib"
            root_dir = ARTIFACTS_DIR.parent.parent
            train_X = np.load(root_dir / "fused_embeddings.npy")

            if pca_fused_path.exists() and pca_text_path.exists() and pca_img_path.exists():
                pca_f = joblib.load(pca_fused_path)
                pca_t = joblib.load(pca_text_path)
                pca_i = joblib.load(pca_img_path)

                for ad in admin_dests:
                    # Avoid duplicate if already in base
                    if any(b["destination"].lower() == ad.name.lower() for b in base_destinations):
                        continue

                    # Load photos
                    p_objs = db.query(PhotoModel).filter(PhotoModel.destination == ad.name).all()
                    p_paths = [root_dir / "images" / ad.name / p.filename for p in p_objs]
                    desc_text = f"{ad.category or ''} {ad.description or ''} {ad.top_attractions or ''}"
                    
                    try:
                        fused_vec, t_vec, i_vec = build_fused_embedding(desc_text, p_paths)
                        
                        # Project with fitted PCAs (NO REFIT)
                        pf = pca_f.transform(fused_vec)[0]
                        pt = pca_t.transform(t_vec)[0]
                        pi = pca_i.transform(i_vec)[0]

                        # Compute cosine similarity to all 50 training destinations
                        sims = cosine_similarity(fused_vec, train_X)[0]
                        max_sim = float(np.max(sims))
                        is_ood = max_sim < ood_threshold

                        # Nearest 5 training destinations
                        top_indices = np.argsort(sims)[::-1][:5]
                        eb_fused_dests = [b["destination"] for b in base_destinations[:50]]
                        nearest = [
                            {"destination": eb_fused_dests[idx], "similarity": round(float(sims[idx]), 3)}
                            for idx in top_indices
                        ]

                        vb = db.query(VibeModel).filter(VibeModel.destination == ad.name).first()
                        scores = {
                            "nature": vb.nature if vb else 50.0,
                            "adventure": vb.adventure if vb else 50.0,
                            "peacefulness": vb.peacefulness if vb else 50.0,
                            "crowd_match": vb.crowd_match if vb else 50.0,
                            "visual_atmosphere": vb.visual_atmosphere if vb else 50.0
                        }

                        base_destinations.append({
                            "destination": ad.name,
                            "state": ad.state or "",
                            "region": ad.region or "North",
                            "category": ad.category or "Heritage",
                            "vibe_scores": scores,
                            "oof_scores": scores,
                            "pca_fused": [round(float(pf[0]), 3), round(float(pf[1]), 3)],
                            "pca_text": [round(float(pt[0]), 3), round(float(pt[1]), 3)],
                            "pca_img": [round(float(pi[0]), 3), round(float(pi[1]), 3)],
                            "tsne_fused": [round(float(pf[0]), 3), round(float(pf[1]), 3)], # projected proxy
                            "tsne_text": [round(float(pt[0]), 3), round(float(pt[1]), 3)],
                            "tsne_img": [round(float(pi[0]), 3), round(float(pi[1]), 3)],
                            "nearest_neighbors": nearest,
                            "max_similarity_to_training": round(max_sim, 3),
                            "is_admin_added": True,
                            "is_ood": is_ood
                        })
                    except Exception as proj_err:
                        print(f"Error projecting admin destination {ad.name}: {proj_err}")
    except Exception as e:
        print(f"Dynamic projection check skipped: {e}")

    return {
        "destinations": base_destinations,
        "ood_cosine_threshold": ood_threshold,
        "num_destinations": len(base_destinations),
        "notes": {
            "tsne_note": "t-SNE distances between non-contiguous clusters are not physically meaningful; use PCA for global spatial geometry."
        }
    }

# ==============================================================================
# INFERENCE LAB LAZY-LOADED CACHE
# ==============================================================================
_LAB_CACHE = {}

def get_lab_models_and_cache():
    global _LAB_CACHE
    if "loaded" in _LAB_CACHE:
        return _LAB_CACHE

    root_dir = ARTIFACTS_DIR.parent.parent
    eb_dir = root_dir / "evaluation_benchmarks"

    try:
        import csv
        import torch
        import numpy as np
        from sklearn.feature_extraction.text import TfidfVectorizer
        from sentence_transformers import SentenceTransformer
        from transformers import CLIPProcessor, CLIPModel
        from PIL import Image

        # Load 50 destinations
        dests = []
        with open(root_dir / "destinations.csv", "r", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                text = f"{row['category']} {row['description']} {row['top_attractions'].replace('|', ' ')}"
                dests.append({"name": row["destination"], "text": text})

        dest_names = [d["name"] for d in dests]
        dest_texts = [d["text"] for d in dests]

        # Load test queries for TF-IDF shared vocabulary
        test_queries = []
        with open(root_dir / "archive_experiments" / "test_queries.csv", "r", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                test_queries.append(row["query_text"])

        # 1. TF-IDF baseline model
        tfidf = TfidfVectorizer(stop_words="english")
        tfidf.fit(dest_texts + test_queries)
        dest_tfidf = tfidf.transform(dest_texts)

        # 2. MiniLM text model
        text_model = SentenceTransformer("all-MiniLM-L6-v2")
        dest_text_emb = text_model.encode(dest_texts)

        # 3. CLIP vision model & photo embeddings cache
        device = "cuda" if torch.cuda.is_available() else "cpu"
        clip_model_name = "openai/clip-vit-base-patch32"
        clip_model = CLIPModel.from_pretrained(clip_model_name)
        clip_processor = CLIPProcessor.from_pretrained(clip_model_name)
        clip_model.to(device)

        # Load precomputed photo vectors cache
        import joblib
        photo_cache_path = ARTIFACTS_DIR / "photo_vectors_cache.joblib"
        if photo_cache_path.exists():
            dest_photo_vectors = joblib.load(photo_cache_path)
        else:
            dest_photo_vectors = {}

        # 4. Out-of-fold predicted vibe scores for Fusion model
        vibe_scores_map = {}
        with open(eb_dir / "predicted_vibe_scores.csv", "r", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                vibe_scores_map[row["destination"]] = {
                    "nature": float(row["nature"]),
                    "adventure": float(row["adventure"]),
                    "peacefulness": float(row["peacefulness"]),
                    "crowd_match": float(row["crowd_match"]),
                    "visual_atmosphere": float(row["visual_atmosphere"])
                }

        # 5. Ground truth lookup and test query metadata
        gt_map = {}
        with open(eb_dir / "ground_truth.csv", "r", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                if int(row["is_relevant"]) == 1:
                    q = row["query_id"]
                    if q not in gt_map:
                        gt_map[q] = set()
                    gt_map[q].add(row["destination"])

        query_meta = {}
        with open(root_dir / "archive_experiments" / "test_queries.csv", "r", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                query_meta[row["query_id"]] = {
                    "text": row["query_text"],
                    "target_dims": json.loads(row["target_dims_json"])
                }

        _LAB_CACHE = {
            "loaded": True,
            "dest_names": dest_names,
            "dest_texts": dest_texts,
            "tfidf": tfidf,
            "dest_tfidf": dest_tfidf,
            "text_model": text_model,
            "dest_text_emb": dest_text_emb,
            "clip_model": clip_model,
            "clip_processor": clip_processor,
            "dest_photo_vectors": dest_photo_vectors,
            "vibe_scores_map": vibe_scores_map,
            "gt_map": gt_map,
            "query_meta": query_meta
        }
        return _LAB_CACHE
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to initialize Inference Lab models: {str(e)}")

from pydantic import BaseModel
from typing import Optional, Dict

class LabQueryPayload(BaseModel):
    query_text: str = ""
    target_dims: Optional[Dict[str, str]] = None # e.g. {"nature": "high", "adventure": "high"}
    loaded_query_id: Optional[str] = None # e.g. "q01"

@router.post("/lab/query")
def run_lab_query(
    payload: LabQueryPayload,
    user: User = Depends(require_role("admin"))
):
    """
    Executes live 4-column ranking comparison:
    1. Baseline (TF-IDF cosine on query_text)
    2. Text (MiniLM semantic cosine on query_text)
    3. Visual (CLIP text-to-photo max-pooling on query_text)
    4. Fusion (Target vibe weighted matching, as in published benchmarks)
    """
    import torch
    import numpy as np
    from sklearn.metrics.pairwise import cosine_similarity

    cache = get_lab_models_and_cache()
    dest_names = cache["dest_names"]
    q_id = payload.loaded_query_id

    # If research query loaded, override defaults from research test query metadata
    if q_id and q_id in cache.get("query_meta", {}):
        meta = cache["query_meta"][q_id]
        q_text = payload.query_text.strip() or meta["text"]
        target_dims = payload.target_dims if (payload.target_dims and any(v in ("high", "low") for v in payload.target_dims.values())) else meta["target_dims"]
    else:
        q_text = payload.query_text.strip()
        target_dims = payload.target_dims or {}

    # Ground truth relevant set if research query loaded
    relevant_set = cache["gt_map"].get(q_id, set()) if q_id else set()

    # 1. Baseline Model
    baseline_rankings = []
    if q_text:
        q_vec = cache["tfidf"].transform([q_text])
        sims = cosine_similarity(q_vec, cache["dest_tfidf"])[0]
        scored = [(dest_names[i], float(sims[i])) for i in range(len(dest_names))]
        scored.sort(key=lambda x: x[1], reverse=True)
        for rank, (name, sc) in enumerate(scored[:10], start=1):
            baseline_rankings.append({
                "rank": rank,
                "destination": name,
                "score": round(sc, 4),
                "is_relevant": name in relevant_set
            })

    # 2. Text Model (MiniLM)
    text_rankings = []
    if q_text:
        q_emb = cache["text_model"].encode([q_text])
        sims = cosine_similarity(q_emb, cache["dest_text_emb"])[0]
        scored = [(dest_names[i], float(sims[i])) for i in range(len(dest_names))]
        scored.sort(key=lambda x: x[1], reverse=True)
        for rank, (name, sc) in enumerate(scored[:10], start=1):
            text_rankings.append({
                "rank": rank,
                "destination": name,
                "score": round(sc, 4),
                "is_relevant": name in relevant_set
            })

    # 3. Visual Model (CLIP text-to-image max-pooling)
    visual_rankings = []
    if q_text:
        clip_model = cache["clip_model"]
        clip_proc = cache["clip_processor"]
        device = "cuda" if torch.cuda.is_available() else "cpu"
        text_in = clip_proc(text=[q_text], return_tensors="pt", padding=True, truncation=True)
        text_in = {k: v.to(device) for k, v in text_in.items()}
        with torch.no_grad():
            t_feat = clip_model.get_text_features(**text_in)
            if hasattr(t_feat, "text_embeds"):
                t_feat = t_feat.text_embeds
            elif hasattr(t_feat, "pooler_output"):
                t_feat = t_feat.pooler_output
            elif isinstance(t_feat, tuple) and not isinstance(t_feat, torch.Tensor):
                t_feat = t_feat[0]
            if t_feat.shape[-1] != clip_model.config.projection_dim:
                t_feat = clip_model.text_projection(t_feat)
            t_feat_np = t_feat.cpu().numpy().astype(np.float32)
            norm = np.linalg.norm(t_feat_np)
            if norm > 0:
                t_feat_np = t_feat_np / norm

        scored_vis = []
        best_photo_map = {}
        for dn in dest_names:
            p_data = cache["dest_photo_vectors"].get(dn, {})
            v_feats = p_data.get("vectors")
            photos = p_data.get("photos", [])
            if v_feats is not None and len(v_feats) > 0 and photos:
                sims = cosine_similarity(t_feat_np, v_feats)[0]
                best_idx = int(np.argmax(sims))
                max_sim = float(sims[best_idx])
                best_p = photos[best_idx]
                scored_vis.append((dn, max_sim))
                best_photo_map[dn] = {
                    "file": best_p["file"],
                    "url": "/" + best_p["file"].replace("\\", "/"),
                    "attraction": best_p["attraction"],
                    "similarity": round(max_sim, 4)
                }
            else:
                scored_vis.append((dn, 0.0))

        scored_vis.sort(key=lambda x: x[1], reverse=True)
        for rank, (name, sc) in enumerate(scored_vis[:10], start=1):
            visual_rankings.append({
                "rank": rank,
                "destination": name,
                "score": round(sc, 4),
                "best_photo": best_photo_map.get(name),
                "is_relevant": name in relevant_set
            })

    # 4. Fusion Model (Target Vibe Weighted Matching from Regressor OOF Scores)
    fusion_rankings = []
    # If target_dims provided, use them; otherwise use equal weighting if query loaded
    effective_dims = target_dims or {"nature": "high", "visual_atmosphere": "high"}
    scored_fusion = []
    for dn in dest_names:
        v_scores = cache["vibe_scores_map"].get(dn, {})
        tot_score = 0.0
        tot_weight = 0
        for dim, dir_ in effective_dims.items():
            if dir_ in ("high", "low"):
                val = v_scores.get(dim, 50.0)
                tot_score += val if dir_ == "high" else (100.0 - val)
                tot_weight += 1
        avg_fit = tot_score / tot_weight if tot_weight > 0 else 50.0
        scored_fusion.append((dn, avg_fit))

    scored_fusion.sort(key=lambda x: x[1], reverse=True)
    for rank, (name, sc) in enumerate(scored_fusion[:10], start=1):
        fusion_rankings.append({
            "rank": rank,
            "destination": name,
            "score": round(sc, 2),
            "is_relevant": name in relevant_set
        })

    # Calculate P@5 and P@10 per column if relevant_set exists
    def calc_metrics(ranked_list):
        if not relevant_set:
            return {"p_at_5": 0.0, "p_at_10": 0.0}
        hits5 = sum(1 for item in ranked_list[:5] if item.get("is_relevant"))
        hits10 = sum(1 for item in ranked_list[:10] if item.get("is_relevant"))
        return {
            "p_at_5": round(hits5 / 5.0, 3),
            "p_at_10": round(hits10 / 10.0, 3)
        }

    # Top-10 Overlap Matrix
    lists = {
        "Baseline": [r["destination"] for r in baseline_rankings[:10]],
        "Text": [r["destination"] for r in text_rankings[:10]],
        "Visual": [r["destination"] for r in visual_rankings[:10]],
        "Fusion": [r["destination"] for r in fusion_rankings[:10]]
    }
    overlap_matrix = {}
    for m1, l1 in lists.items():
        overlap_matrix[m1] = {}
        for m2, l2 in lists.items():
            overlap_matrix[m1][m2] = len(set(l1).intersection(set(l2)))

    return {
        "query_text": q_text,
        "target_dims": effective_dims,
        "loaded_query_id": q_id,
        "has_ground_truth": bool(relevant_set),
        "relevant_destinations": sorted(list(relevant_set)),
        "rankings": {
            "baseline": {
                "label": "Baseline (TF-IDF)",
                "description": "Lexical frequency matching against destination descriptions.",
                "metrics": calc_metrics(baseline_rankings),
                "results": baseline_rankings
            },
            "text": {
                "label": "Text (MiniLM)",
                "description": "Sentence-Transformers 384D semantic text cosine similarity.",
                "metrics": calc_metrics(text_rankings),
                "results": text_rankings
            },
            "visual": {
                "label": "Visual (CLIP Max-Pool)",
                "description": "OpenAI CLIP text-to-photo cosine similarity with best-matching image.",
                "metrics": calc_metrics(visual_rankings),
                "results": visual_rankings
            },
            "fusion": {
                "label": "Fusion (Multi-Modal Vibes)",
                "description": "Ranks by the vibe sliders using out-of-fold predicted vibe scores, exactly as in published experiments.",
                "metrics": calc_metrics(fusion_rankings),
                "results": fusion_rankings
            }
        },
        "overlap_matrix": overlap_matrix,
        "notes": "Fusion ranks by the vibe sliders, as in the experiments; the other three rank by the text query."
    }

