import csv
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def rank_baseline():
    # Read queries
    queries = []
    with open("test_queries.csv", "r", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            queries.append({
                "query_id": row["query_id"],
                "query_text": row["query_text"]
            })

    # Read destinations
    destinations = []
    with open("destinations.csv", "r", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            text = f"{row['category']} {row['description']} {row['top_attractions'].replace('|', ' ')}"
            destinations.append({
                "destination": row["destination"],
                "text": text
            })

    # TF-IDF Vectorization
    dest_texts = [d["text"] for d in destinations]
    query_texts = [q["query_text"] for q in queries]
    
    vectorizer = TfidfVectorizer(stop_words='english')
    # Fit on both destinations and queries to ensure vocabulary covers both
    all_texts = dest_texts + query_texts
    vectorizer.fit(all_texts)
    
    dest_tfidf = vectorizer.transform(dest_texts)
    query_tfidf = vectorizer.transform(query_texts)
    
    # Compute similarity
    sim_matrix = cosine_similarity(query_tfidf, dest_tfidf)
    
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
            
    with open("baseline_rankings.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["query_id", "destination", "rank", "similarity_score"])
        writer.writeheader()
        writer.writerows(results)

if __name__ == "__main__":
    rank_baseline()
    print("Created baseline_rankings.csv")
