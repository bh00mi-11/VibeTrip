import csv
import torch
import numpy as np
from pathlib import Path
from PIL import Image
from transformers import CLIPProcessor, CLIPModel
from sentence_transformers import SentenceTransformer

def build_fused():
    destinations = []
    texts = []
    with open("destinations.csv", "r", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            destinations.append(row["destination"])
            text = f"{row['category']} {row['description']} {row['top_attractions'].replace('|', ' ')}"
            texts.append(text)
            
    print("Loading Text model...")
    text_model = SentenceTransformer('all-MiniLM-L6-v2')
    text_embeddings = text_model.encode(texts)
    
    print("Loading Vision model...")
    model_name = "openai/clip-vit-base-patch32"
    vis_model = CLIPModel.from_pretrained(model_name)
    processor = CLIPProcessor.from_pretrained(model_name)
    device = "cuda" if torch.cuda.is_available() else "cpu"
    vis_model.to(device)
    
    images_dir = Path("images")
    vis_embeddings = []
    
    print("Encoding Images...")
    for dest in destinations:
        dest_folder = images_dir / dest
        image_files = list(dest_folder.glob("*.jpg")) + list(dest_folder.glob("*.jpeg")) + list(dest_folder.glob("*.png"))
        
        imgs = []
        for img_path in image_files:
            try:
                imgs.append(Image.open(img_path).convert("RGB"))
            except Exception:
                pass
                
        if not imgs:
            vis_embeddings.append(np.zeros(vis_model.config.projection_dim))
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
            
        vis_embeddings.append(avg_feature)
        
    vis_embeddings = np.array(vis_embeddings)
    
    print("Concatenating and saving...")
    fused = np.concatenate([text_embeddings, vis_embeddings], axis=1)
    np.save("fused_embeddings.npy", fused)
    
    with open("fused_destinations.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["destination"])
        for d in destinations:
            writer.writerow([d])
            
    print("Saved fused_embeddings.npy and fused_destinations.csv")

if __name__ == "__main__":
    build_fused()
