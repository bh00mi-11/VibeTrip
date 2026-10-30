import os
import json
import joblib
import numpy as np
import pandas as pd
import torch
from PIL import Image
from transformers import CLIPProcessor, CLIPModel

print("==================================================")
print("             EXPLAINABILITY CHECKS                ")
print("==================================================\n")

# -------------------------------------------------------------
# (a) Max error between sum of per-photo contributions and total image contribution
# -------------------------------------------------------------
with open('backend/ml_artifacts/decompositions.json', 'r', encoding='utf-8') as f:
    decomps = json.load(f)['decompositions']

with open('backend/ml_artifacts/per_photo_decompositions.json', 'r', encoding='utf-8') as f:
    per_photo = json.load(f)

dims = ["nature", "adventure", "peacefulness", "crowd_match", "visual_atmosphere"]
max_photo_sum_err = 0.0
worst_photo_case = None

for dest, dim_map in decomps.items():
    dest_photos = per_photo.get(dest, {})
    for d in dims:
        total_img_contrib = dim_map[d]["image_contribution"]
        dim_photo_data = dest_photos.get(d, {})
        photos = dim_photo_data.get("photos", [])
        if photos:
            sum_photo_contrib = sum(p.get("contribution", 0.0) for p in photos)
            err = abs(total_img_contrib - sum_photo_contrib)
            if err > max_photo_sum_err:
                max_photo_sum_err = err
                worst_photo_case = {
                    "destination": dest,
                    "dimension": d,
                    "total_image_contribution": total_img_contrib,
                    "sum_photo_contributions": sum_photo_contrib,
                    "abs_difference": err
                }

print("(a) Max error between sum of per-photo contributions and total image contribution:")
print(f"    Maximum error across 50 destinations x 5 dimensions: {max_photo_sum_err:.6f}")
if worst_photo_case:
    print(f"    Worst case destination: {worst_photo_case['destination']} ({worst_photo_case['dimension']})")
    print(f"    - total_image_contribution: {worst_photo_case['total_image_contribution']:.4f}")
    print(f"    - sum_photo_contributions:  {worst_photo_case['sum_photo_contributions']:.4f}")
    print(f"    - absolute difference:      {worst_photo_case['abs_difference']:.6f}")

# -------------------------------------------------------------
# (b) Cosine similarity between recomputed CLIP image embedding (mean pooled, normalized) and stored fused_embeddings.npy image columns
# -------------------------------------------------------------
fused_embeddings = np.load('fused_embeddings.npy') # (50, 896) -> 384 text, 512 image
stored_img_embeddings = fused_embeddings[:, 384:] # (50, 512)

fused_dest_df = pd.read_csv('evaluation_benchmarks/fused_destinations.csv')
dest_names = fused_dest_df['destination'].tolist()

device = "cuda" if torch.cuda.is_available() else "cpu"
model_name = "openai/clip-vit-base-patch32"
vis_model = CLIPModel.from_pretrained(model_name)
processor = CLIPProcessor.from_pretrained(model_name)
vis_model.to(device)
vis_model.eval()

recomputed_cosines = []

for idx, dest in enumerate(dest_names):
    dest_dir = os.path.join("images", dest)
    if not os.path.exists(dest_dir):
        continue
    image_files = [f for f in os.listdir(dest_dir) if f.lower().endswith(('.jpg', '.jpeg', '.png', '.webp'))]
    imgs = []
    for f in sorted(image_files):
        img_p = os.path.join(dest_dir, f)
        try:
            imgs.append(Image.open(img_p).convert("RGB"))
        except Exception:
            pass
            
    if not imgs:
        continue
        
    inputs = processor(images=imgs, return_tensors="pt", padding=True)
    inputs = {k: v.to(device) for k, v in inputs.items()}
    
    with torch.no_grad():
        img_features = vis_model.get_image_features(pixel_values=inputs["pixel_values"])
        if hasattr(img_features, "image_embeds"):
            img_features = img_features.image_embeds
        elif hasattr(img_features, "pooler_output"):
            img_features = img_features.pooler_output
        elif isinstance(img_features, tuple) and not isinstance(img_features, torch.Tensor):
            img_features = img_features[0]
        if img_features.shape[-1] != vis_model.config.projection_dim:
            img_features = vis_model.visual_projection(img_features)
            
    img_features_np = img_features.cpu().numpy()
    avg_feature = img_features_np.mean(axis=0)
    norm = np.linalg.norm(avg_feature)
    if norm > 0:
        avg_feature = avg_feature / norm
        
    stored_vec = stored_img_embeddings[idx]
    stored_norm = np.linalg.norm(stored_vec)
    if stored_norm > 0:
        stored_vec = stored_vec / stored_norm
        
    cos_sim = float(np.dot(avg_feature, stored_vec))
    recomputed_cosines.append(cos_sim)

min_cos = min(recomputed_cosines) if recomputed_cosines else 0.0
mean_cos = sum(recomputed_cosines) / len(recomputed_cosines) if recomputed_cosines else 0.0
print(f"\n(b) Cosine similarity between recomputed CLIP image embeddings and stored fused_embeddings.npy image columns:")
print(f"    Min cosine similarity over 50 destinations:  {min_cos:.8f}")
print(f"    Mean cosine similarity over 50 destinations: {mean_cos:.8f}")
print(f"    Total destinations evaluated: {len(recomputed_cosines)} of {len(dest_names)}")

# -------------------------------------------------------------
# (c) Max prediction error when decomposition is done in float64 vs float32
# -------------------------------------------------------------
max_recon_error_f64 = 0.0
max_recon_error_f32 = 0.0
max_diff_f64_f32 = 0.0

for d in dims:
    model_path = f"vibe_model_{d}.joblib" if os.path.exists(f"vibe_model_{d}.joblib") else os.path.join("models", f"vibe_model_{d}.joblib")
    if not os.path.exists(model_path):
        continue
    ridge_model = joblib.load(model_path)
    
    # 1. In float64
    coef_64 = ridge_model.coef_.astype(np.float64)
    intercept_64 = np.float64(ridge_model.intercept_)
    X_64 = fused_embeddings.astype(np.float64)
    
    pred_standard = ridge_model.predict(X_64)
    recon_64 = intercept_64 + X_64 @ coef_64
    err_64 = np.max(np.abs(pred_standard - recon_64))
    if err_64 > max_recon_error_f64:
        max_recon_error_f64 = err_64

    # 2. In float32
    coef_32 = ridge_model.coef_.astype(np.float32)
    intercept_32 = np.float32(ridge_model.intercept_)
    X_32 = fused_embeddings.astype(np.float32)
    recon_32 = intercept_32 + X_32 @ coef_32
    err_32 = np.max(np.abs(pred_standard - recon_32))
    if err_32 > max_recon_error_f32:
        max_recon_error_f32 = err_32
        
    diff_f = np.max(np.abs(recon_64 - recon_32))
    if diff_f > max_diff_f64_f32:
        max_diff_f64_f32 = diff_f

print(f"\n(c) Max prediction decomposition reconstruction error:")
print(f"    Max error in float64: {max_recon_error_f64:.10e}")
print(f"    Max error in float32: {max_recon_error_f32:.10e}")
print(f"    Float64 vs Float32 evaluation gap: {max_diff_f64_f32:.10e}")
print("==================================================")
