import csv
import torch
import numpy as np
import json
from transformers import CLIPProcessor, CLIPModel
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

def run_no_vibe_layer():
    print("Loading queries...")
    queries = []
    with open("test_queries.csv", "r", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            queries.append({
                "query_id": row["query_id"],
                "query_text": row["query_text"]
            })
            
    print("Loading destinations...")
    destinations = []
    with open("fused_destinations.csv", "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        next(reader)
        for row in reader:
            destinations.append(row[0])
            
    dest_fused = np.load("fused_embeddings.npy") # (50, 896)
    
    print("Loading models...")
    st_model = SentenceTransformer('all-MiniLM-L6-v2')
    clip_model_name = "openai/clip-vit-base-patch32"
    clip_model = CLIPModel.from_pretrained(clip_model_name)
    processor = CLIPProcessor.from_pretrained(clip_model_name)
    device = "cuda" if torch.cuda.is_available() else "cpu"
    clip_model.to(device)
    
    query_texts = [q["query_text"] for q in queries]
    
    # 1. Text embedding (ST)
    st_embeddings = st_model.encode(query_texts)
    
    # 2. Text embedding (CLIP)
    text_inputs = processor(text=query_texts, return_tensors="pt", padding=True, truncation=True)
    text_inputs = {k: v.to(device) for k, v in text_inputs.items()}
    with torch.no_grad():
        text_features = clip_model.get_text_features(**text_inputs)
        if hasattr(text_features, "text_embeds"):
            text_features = text_features.text_embeds
        elif hasattr(text_features, "pooler_output"):
            text_features = text_features.pooler_output
        elif isinstance(text_features, tuple) and not isinstance(text_features, torch.Tensor):
            text_features = text_features[0]
        if text_features.shape[-1] != clip_model.config.projection_dim:
            text_features = clip_model.text_projection(text_features)
        text_features = text_features.cpu().numpy()
        
    norms = np.linalg.norm(text_features, axis=1, keepdims=True)
    clip_embeddings = text_features / np.where(norms > 0, norms, 1)
    
    # Concatenate
    q_fused = np.concatenate([st_embeddings, clip_embeddings], axis=1) # (Q, 896)
    
    print("Ranking...")
    sim_matrix = cosine_similarity(q_fused, dest_fused)
    
    results = []
    for q_idx, q in enumerate(queries):
        sims = sim_matrix[q_idx]
        scored_dests = [(destinations[d_idx], sims[d_idx]) for d_idx in range(len(destinations))]
        scored_dests.sort(key=lambda x: x[1], reverse=True)
        
        for rank, (dest_name, score) in enumerate(scored_dests, start=1):
            results.append({
                "query_id": q["query_id"],
                "destination": dest_name,
                "rank": rank,
                "similarity_score": score
            })
            
    with open("ablation_no_vibe_rankings.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["query_id", "destination", "rank", "similarity_score"])
        writer.writeheader()
        writer.writerows(results)
        
    print("Created ablation_no_vibe_rankings.csv")

if __name__ == "__main__":
    run_no_vibe_layer()
