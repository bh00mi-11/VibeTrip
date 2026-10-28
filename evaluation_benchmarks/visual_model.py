import csv
import os
import torch
from pathlib import Path
from PIL import Image
from transformers import CLIPProcessor, CLIPModel
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

def run_visual_model():
    print("Loading CLIP model...")
    model_name = "openai/clip-vit-base-patch32"
    model = CLIPModel.from_pretrained(model_name)
    processor = CLIPProcessor.from_pretrained(model_name)
    
    device = "cuda" if torch.cuda.is_available() else "cpu"
    model.to(device)
    
    # 1. Load queries
    queries = []
    with open("test_queries.csv", "r", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            queries.append({
                "query_id": row["query_id"],
                "query_text": row["query_text"]
            })
            
    # Load destinations from destinations.csv to ensure we get all of them
    destinations = []
    with open("destinations.csv", "r", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            destinations.append(row["destination"])
            
    # 2. Encode all destinations
    print("Encoding images per destination...")
    dest_embeddings_mean = []
    dest_all_image_embeddings = [] # List of lists of individual embeddings
    images_dir = Path("images")
    
    for dest in destinations:
        dest_folder = images_dir / dest
        if not dest_folder.exists():
            dest_embeddings_mean.append(np.zeros(model.config.projection_dim))
            dest_all_image_embeddings.append([np.zeros(model.config.projection_dim)])
            continue
            
        image_files = list(dest_folder.glob("*.jpg")) + list(dest_folder.glob("*.jpeg")) + list(dest_folder.glob("*.png"))
        if not image_files:
            dest_embeddings_mean.append(np.zeros(model.config.projection_dim))
            dest_all_image_embeddings.append([np.zeros(model.config.projection_dim)])
            continue
            
        imgs = []
        for img_path in image_files:
            try:
                img = Image.open(img_path).convert("RGB")
                imgs.append(img)
            except Exception as e:
                pass
                
        if not imgs:
            dest_embeddings_mean.append(np.zeros(model.config.projection_dim))
            dest_all_image_embeddings.append([np.zeros(model.config.projection_dim)])
            continue
            
        inputs = processor(images=imgs, return_tensors="pt", padding=True)
        inputs = {k: v.to(device) for k, v in inputs.items()}
        
        with torch.no_grad():
            img_features = model.get_image_features(pixel_values=inputs["pixel_values"])
            if hasattr(img_features, "image_embeds"):
                img_features = img_features.image_embeds
            elif hasattr(img_features, "pooler_output"):
                img_features = img_features.pooler_output
            elif isinstance(img_features, tuple) and not isinstance(img_features, torch.Tensor):
                img_features = img_features[0]
                
            if img_features.shape[-1] != model.config.projection_dim:
                img_features = model.visual_projection(img_features)
                
        img_features_np = img_features.cpu().numpy()
        
        # Mean pooling
        avg_feature = img_features_np.mean(axis=0)
        norm = np.linalg.norm(avg_feature)
        if norm > 0:
            avg_feature = avg_feature / norm
        dest_embeddings_mean.append(avg_feature)
        
        # Keep individual embeddings for max pooling
        individual_norms = np.linalg.norm(img_features_np, axis=1, keepdims=True)
        img_features_normalized = img_features_np / np.where(individual_norms > 0, individual_norms, 1)
        dest_all_image_embeddings.append(img_features_normalized)
        
    dest_embeddings_mean = np.array(dest_embeddings_mean)
    
    # 3. Encode queries
    print("Encoding queries...")
    query_texts = [q["query_text"] for q in queries]
    text_inputs = processor(text=query_texts, return_tensors="pt", padding=True, truncation=True)
    text_inputs = {k: v.to(device) for k, v in text_inputs.items()}
    
    with torch.no_grad():
        text_features = model.get_text_features(**text_inputs)
        if hasattr(text_features, "text_embeds"):
            text_features = text_features.text_embeds
        elif hasattr(text_features, "pooler_output"):
            text_features = text_features.pooler_output
        elif isinstance(text_features, tuple) and not isinstance(text_features, torch.Tensor):
            text_features = text_features[0]
            
        if text_features.shape[-1] != model.config.projection_dim:
            text_features = model.text_projection(text_features)
            
        text_features = text_features.cpu().numpy()
        
    # L2 Normalize text features
    norms = np.linalg.norm(text_features, axis=1, keepdims=True)
    text_features = text_features / np.where(norms > 0, norms, 1)
    
    # 4. Compute cosine similarity and rank (MEAN POOLING)
    print("Ranking (Mean Pooling)...")
    sim_matrix_mean = cosine_similarity(text_features, dest_embeddings_mean)
    
    results_mean = []
    for q_idx, q in enumerate(queries):
        sims = sim_matrix_mean[q_idx]
        scored_dests = [(destinations[d_idx], sims[d_idx]) for d_idx in range(len(destinations))]
        scored_dests.sort(key=lambda x: x[1], reverse=True)
        
        for rank, (dest_name, score) in enumerate(scored_dests, start=1):
            results_mean.append({
                "query_id": q["query_id"],
                "destination": dest_name,
                "rank": rank,
                "similarity_score": score
            })
            
    with open("visual_rankings.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["query_id", "destination", "rank", "similarity_score"])
        writer.writeheader()
        writer.writerows(results_mean)
        
    # 5. Compute cosine similarity and rank (MAX POOLING)
    print("Ranking (Max Pooling)...")
    results_max = []
    for q_idx, q in enumerate(queries):
        q_feat = text_features[q_idx].reshape(1, -1)
        scored_dests = []
        for d_idx, d_name in enumerate(destinations):
            d_img_features = dest_all_image_embeddings[d_idx]
            sims = cosine_similarity(q_feat, d_img_features)[0] # sims with all images of this destination
            max_sim = np.max(sims)
            scored_dests.append((d_name, max_sim))
            
        scored_dests.sort(key=lambda x: x[1], reverse=True)
        for rank, (dest_name, score) in enumerate(scored_dests, start=1):
            results_max.append({
                "query_id": q["query_id"],
                "destination": dest_name,
                "rank": rank,
                "similarity_score": score
            })
            
    with open("visual_rankings_maxpool.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["query_id", "destination", "rank", "similarity_score"])
        writer.writeheader()
        writer.writerows(results_max)
        
    print("Created visual_rankings.csv and visual_rankings_maxpool.csv")

if __name__ == "__main__":
    run_visual_model()
