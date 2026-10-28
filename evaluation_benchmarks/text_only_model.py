import csv
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

def run_text_only_model():
    print("Loading SentenceTransformer model...")
    model = SentenceTransformer('all-MiniLM-L6-v2')
    
    # 1. Load queries
    queries = []
    with open("test_queries.csv", "r", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            queries.append({
                "query_id": row["query_id"],
                "query_text": row["query_text"]
            })
            
    # 2. Load destinations
    destinations = []
    with open("destinations.csv", "r", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            text = f"{row['category']} {row['description']} {row['top_attractions'].replace('|', ' ')}"
            destinations.append({
                "destination": row["destination"],
                "text": text
            })
            
    # 3. Embed text
    print("Encoding queries and destinations...")
    query_texts = [q["query_text"] for q in queries]
    dest_texts = [d["text"] for d in destinations]
    
    query_embeddings = model.encode(query_texts)
    dest_embeddings = model.encode(dest_texts)
    
    # 4. Compute cosine similarity and rank
    print("Ranking...")
    sim_matrix = cosine_similarity(query_embeddings, dest_embeddings)
    
    results = []
    for q_idx, q in enumerate(queries):
        sims = sim_matrix[q_idx]
        scored_dests = [(destinations[d_idx]["destination"], sims[d_idx]) for d_idx in range(len(destinations))]
        scored_dests.sort(key=lambda x: x[1], reverse=True)
        
        for rank, (dest_name, score) in enumerate(scored_dests, start=1):
            results.append({
                "query_id": q["query_id"],
                "destination": dest_name,
                "rank": rank,
                "similarity_score": score
            })
            
    with open("text_rankings.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["query_id", "destination", "rank", "similarity_score"])
        writer.writeheader()
        writer.writerows(results)
        
    print("Created text_rankings.csv")

if __name__ == "__main__":
    run_text_only_model()
