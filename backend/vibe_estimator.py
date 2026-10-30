import os
import joblib
import torch
import numpy as np
from pathlib import Path
from PIL import Image
from transformers import CLIPProcessor, CLIPModel
from sentence_transformers import SentenceTransformer

# Lazy-loaded singleton models
_TEXT_MODEL = None
_CLIP_MODEL = None
_CLIP_PROCESSOR = None
_VIBE_REGRESSORS = {}

DIMS = ["nature", "adventure", "peacefulness", "crowd_match", "visual_atmosphere"]
ROOT_DIR = Path(__file__).resolve().parent.parent

def get_text_model():
    global _TEXT_MODEL
    if _TEXT_MODEL is None:
        _TEXT_MODEL = SentenceTransformer("all-MiniLM-L6-v2")
    return _TEXT_MODEL

def get_vision_model():
    global _CLIP_MODEL, _CLIP_PROCESSOR
    if _CLIP_MODEL is None:
        model_name = "openai/clip-vit-base-patch32"
        _CLIP_MODEL = CLIPModel.from_pretrained(model_name)
        _CLIP_PROCESSOR = CLIPProcessor.from_pretrained(model_name)
        device = "cuda" if torch.cuda.is_available() else "cpu"
        _CLIP_MODEL.to(device)
    return _CLIP_MODEL, _CLIP_PROCESSOR

def get_regressors():
    global _VIBE_REGRESSORS
    if not _VIBE_REGRESSORS:
        for dim in DIMS:
            model_path = ROOT_DIR / f"vibe_model_{dim}.joblib"
            if model_path.exists():
                _VIBE_REGRESSORS[dim] = joblib.load(model_path)
            else:
                raise FileNotFoundError(f"Model file {model_path} not found.")
    return _VIBE_REGRESSORS

def estimate_vibe_scores(text_input: str, image_paths: list) -> dict:
    """
    Builds fused embedding exactly as build_fused_embeddings.py does:
    1. sentence-transformer embedding of text (384-d)
    2. averaged CLIP embedding of photos (512-d)
    3. concatenate into 896-d vector
    4. run the 5 saved Ridge regressors and clip [0, 100]
    """
    text_model = get_text_model()
    text_emb = text_model.encode([text_input]) # (1, 384)

    vis_model, processor = get_vision_model()
    device = "cuda" if torch.cuda.is_available() else "cpu"

    imgs = []
    for p in image_paths:
        try:
            imgs.append(Image.open(p).convert("RGB"))
        except Exception as e:
            print(f"Error loading image {p}: {e}")

    if not imgs:
        vis_emb = np.zeros((1, vis_model.config.projection_dim))
    else:
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
        vis_emb = avg_feature.reshape(1, -1)

    fused_emb = np.concatenate([text_emb, vis_emb], axis=1) # (1, 896)

    regressors = get_regressors()
    scores = {}
    for dim in DIMS:
        reg = regressors[dim]
        pred = float(reg.predict(fused_emb)[0])
        scores[dim] = round(float(np.clip(pred, 0.0, 100.0)), 2)

    return scores

def build_fused_embedding(text_input: str, image_paths: list):
    """Returns (fused_emb, text_emb, vis_emb) for embedding projection and OOD calculation."""
    text_model = get_text_model()
    text_emb = text_model.encode([text_input]) # (1, 384)

    vis_model, processor = get_vision_model()
    device = "cuda" if torch.cuda.is_available() else "cpu"

    imgs = []
    for p in image_paths:
        try:
            imgs.append(Image.open(p).convert("RGB"))
        except Exception as e:
            print(f"Error loading image {p}: {e}")

    if not imgs:
        vis_emb = np.zeros((1, vis_model.config.projection_dim))
    else:
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
        vis_emb = avg_feature.reshape(1, -1)

    fused_emb = np.concatenate([text_emb, vis_emb], axis=1)
    return fused_emb, text_emb, vis_emb


def estimate_image_vibe_scores(image_paths: list, text_hint: str = "") -> dict:
    """
    Given one or more user-uploaded images (and optional text query hint),
    uses CLIP ViT-B/32 image encoder + Sentence-BERT to build the 896D fused representation
    and predict the 5-dimensional vibe scores.
    Also computes the recommended target level ('high', 'medium', 'low') for each dimension.
    """
    scores = estimate_vibe_scores(text_hint, image_paths)
    
    # Map raw 0-100 scores to target slider levels for matching
    slider_levels = {}
    for dim, val in scores.items():
        if val >= 65.0:
            slider_levels[dim] = "high"
        elif val <= 38.0:
            slider_levels[dim] = "low"
        else:
            slider_levels[dim] = "medium"
            
    return {
        "scores": scores,
        "recommended_vibes": slider_levels
    }
