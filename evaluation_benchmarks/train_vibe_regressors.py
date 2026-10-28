import csv
import numpy as np
import joblib
from sklearn.linear_model import Ridge
from sklearn.model_selection import cross_val_predict
from sklearn.metrics import r2_score, mean_absolute_error

def train():
    destinations = []
    with open("fused_destinations.csv", "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        next(reader)
        for row in reader:
            destinations.append(row[0])
            
    X = np.load("fused_embeddings.npy")
    
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
    
    print(f"{'Dimension':<20} | {'CV R²':<10} | {'CV MAE':<10}")
    print("-" * 45)
    
    for d in dims:
        y = Y[d]
        model = Ridge(alpha=1.0)
        
        preds = cross_val_predict(model, X, y, cv=5)
        
        r2 = r2_score(y, preds)
        mae = mean_absolute_error(y, preds)
        print(f"{d:<20} | {r2:<10.3f} | {mae:<10.3f}")
        
        for i, dest in enumerate(destinations):
            predictions_out[dest][d] = np.clip(preds[i], 0, 100)
            
        model.fit(X, y)
        joblib.dump(model, f"vibe_model_{d}.joblib")
        
    with open("predicted_vibe_scores.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["destination"] + dims)
        writer.writeheader()
        for dest in destinations:
            row = {"destination": dest}
            row.update(predictions_out[dest])
            writer.writerow(row)
            
    print("\nSaved predicted_vibe_scores.csv and models.")

if __name__ == "__main__":
    train()
