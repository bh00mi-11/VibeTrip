"""
Deep Learning Module: Multi-Modal Transit Choice Neural Network (Deep Choice MLP)
Architecture:
  - Input Layer: Context Features (Distance, Terrain Encoding, Nature Vibe, Adventure Vibe, Peace Vibe, Crowd Vibe, Visual Vibe)
  - Hidden Layers:
      Linear(11 -> 64) -> BatchNorm1d -> LeakyReLU(0.2) -> Dropout(0.25)
      Linear(64 -> 32) -> BatchNorm1d -> LeakyReLU(0.2) -> Dropout(0.15)
  - Output Layer:
      Linear(32 -> 5) -> Softmax (Predicts probabilities over 5 discrete transit modes)

Transit Classes:
  0: Scenic Walking Corridor
  1: Eco-Mobility (Bicycle / E-Rickshaw)
  2: Local Auto-Rickshaw / Micro-Transit
  3: App Cab / Shared Mountain Jeep
  4: Dedicated Private Cab / Tourist Coach
"""

import os
import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np
from pathlib import Path
from typing import Dict, Any, List

CLASSES = [
    "Scenic Walking Corridor",
    "Eco-Mobility (Bicycle / E-Rickshaw)",
    "Local Auto-Rickshaw / Micro-Transit",
    "App Cab / Shared Mountain Jeep",
    "Dedicated Private Cab / Tourist Coach"
]

MODE_DETAILS = {
    0: {
        "icon": "walking",
        "speed_kmh": 4.5,
        "base_fare": 0,
        "per_km": 0,
        "eco_score": 100,
        "comfort_score": 70,
        "recommendation": "Zero emissions, scenic pedestrian stroll recommended."
    },
    1: {
        "icon": "bicycle",
        "speed_kmh": 14.0,
        "base_fare": 20,
        "per_km": 15,
        "eco_score": 90,
        "comfort_score": 75,
        "recommendation": "Great for heritage lanes and avoiding traffic bottlenecks."
    },
    2: {
        "icon": "rickshaw",
        "speed_kmh": 22.0,
        "base_fare": 35,
        "per_km": 18,
        "eco_score": 60,
        "comfort_score": 75,
        "recommendation": "Quick, economical point-to-point urban commute."
    },
    3: {
        "icon": "taxi",
        "speed_kmh": 32.0,
        "base_fare": 90,
        "per_km": 24,
        "eco_score": 45,
        "comfort_score": 90,
        "recommendation": "Comfortable AC travel or sturdy hill transit for slopes."
    },
    4: {
        "icon": "coach",
        "speed_kmh": 40.0,
        "base_fare": 350,
        "per_km": 28,
        "eco_score": 50,
        "comfort_score": 95,
        "recommendation": "Continuous dedicated vehicle with multi-stop waiting allowance."
    }
}

class DeepTransitChoiceModel(nn.Module):
    def __init__(self, input_dim: int = 11, num_classes: int = 5):
        super(DeepTransitChoiceModel, self).__init__()
        self.fc1 = nn.Linear(input_dim, 64)
        self.bn1 = nn.BatchNorm1d(64)
        self.act1 = nn.LeakyReLU(0.2)
        self.drop1 = nn.Dropout(0.25)
        
        self.fc2 = nn.Linear(64, 32)
        self.bn2 = nn.BatchNorm1d(32)
        self.act2 = nn.LeakyReLU(0.2)
        self.drop2 = nn.Dropout(0.15)
        
        self.classifier = nn.Linear(32, num_classes)
        
    def forward(self, x):
        # x: [Batch, 11]
        h = self.drop1(self.act1(self.bn1(self.fc1(x))))
        h = self.drop2(self.act2(self.bn2(self.fc2(h))))
        logits = self.classifier(h)
        probs = F.softmax(logits, dim=-1)
        return probs

_GLOBAL_DL_TRANSIT_MODEL = None
_MODEL_WEIGHTS_PATH = Path(__file__).resolve().parent / "deep_transit_weights.pt"

def _generate_synthetic_training_dataset(num_samples: int = 2500):
    """
    Synthesizes diverse real-world multimodal transit choice pairs according to
    transportation science utility formulas (Discrete Choice Theory / McFadden RUM).
    Features (11):
      [0]: distance_km (log-scaled)
      [1]: is_hill (0 or 1)
      [2]: is_coastal (0 or 1)
      [3]: is_metro (0 or 1)
      [4]: nature_score / 100
      [5]: adventure_score / 100
      [6]: peacefulness_score / 100
      [7]: crowd_match_score / 100
      [8]: visual_score / 100
      [9]: time_of_day (0=morning, 1=afternoon, 2=evening)
      [10]: group_size_norm (1 to 4 normalized)
    """
    np.random.seed(42)
    distances = np.random.exponential(scale=4.5, size=num_samples) + 0.2
    distances = np.clip(distances, 0.2, 45.0)
    
    is_hill = np.random.binomial(1, 0.35, size=num_samples)
    is_coastal = np.random.binomial(1, 0.20, size=num_samples)
    is_metro = np.random.binomial(1, 0.40, size=num_samples)
    
    nature = np.random.uniform(10, 100, size=num_samples) / 100.0
    adventure = np.random.uniform(10, 100, size=num_samples) / 100.0
    peace = np.random.uniform(10, 100, size=num_samples) / 100.0
    crowd = np.random.uniform(10, 100, size=num_samples) / 100.0
    visual = np.random.uniform(10, 100, size=num_samples) / 100.0
    
    time_of_day = np.random.choice([0.0, 0.5, 1.0], size=num_samples)
    group_size = np.random.choice([0.25, 0.5, 0.75, 1.0], size=num_samples)
    
    X = np.stack([
        np.log1p(distances),
        is_hill,
        is_coastal,
        is_metro,
        nature,
        adventure,
        peace,
        crowd,
        visual,
        time_of_day,
        group_size
    ], axis=1).astype(np.float32)
    
    # Transportation utility values
    # U_walking: high if dist small, nature high, peace high
    u_walk = 3.5 - 2.8 * distances + 1.2 * nature + 0.9 * peace - 1.0 * is_hill
    # U_eco: bicycle/e-rickshaw for 1-4km flat terrain
    u_eco = 1.8 - 0.7 * np.abs(distances - 2.5) + 0.8 * adventure - 1.2 * is_hill
    # U_auto: 2-8km in metro/plains
    u_auto = 2.0 - 0.4 * np.abs(distances - 4.5) + 0.8 * is_metro - 1.5 * is_hill
    # U_cab: 5-20km, hill friendly, comfort
    u_cab = 0.5 + 0.15 * distances + 1.2 * is_hill + 0.8 * (1.0 - crowd)
    # U_tourist_coach: > 18km or large group
    u_coach = -2.5 + 0.22 * distances + 1.5 * group_size + 0.7 * is_hill
    
    utilities = np.stack([u_walk, u_eco, u_auto, u_cab, u_coach], axis=1)
    # Add Gumbel noise for Multinomial Logit choice
    noise = np.random.gumbel(0, 0.4, size=utilities.shape)
    Y = np.argmax(utilities + noise, axis=1).astype(np.int64)
    
    return torch.tensor(X), torch.tensor(Y)

def get_trained_dl_transit_model():
    """Returns the trained PyTorch Deep Choice Model singleton."""
    global _GLOBAL_DL_TRANSIT_MODEL
    if _GLOBAL_DL_TRANSIT_MODEL is not None:
        return _GLOBAL_DL_TRANSIT_MODEL
        
    model = DeepTransitChoiceModel(input_dim=11, num_classes=5)
    
    if _MODEL_WEIGHTS_PATH.exists():
        model.load_state_dict(torch.load(_MODEL_WEIGHTS_PATH, map_location=torch.device('cpu')))
    else:
        # Train and persist model weights
        X_train, Y_train = _generate_synthetic_training_dataset(num_samples=3000)
        optimizer = torch.optim.AdamW(model.parameters(), lr=0.008, weight_decay=1e-4)
        criterion = nn.CrossEntropyLoss()
        
        model.train()
        for epoch in range(40):
            optimizer.zero_grad()
            # Feed without batch norm issues
            outputs = model.classifier(model.drop2(model.act2(model.bn2(model.fc2(model.drop1(model.act1(model.bn1(model.fc1(X_train)))))))))
            loss = criterion(outputs, Y_train)
            loss.backward()
            optimizer.step()
            
        torch.save(model.state_dict(), _MODEL_WEIGHTS_PATH)
        
    model.eval()
    _GLOBAL_DL_TRANSIT_MODEL = model
    return _GLOBAL_DL_TRANSIT_MODEL

def predict_deep_transit_choice(
    dist_km: float,
    destination_name: str,
    terrain_category: str = "",
    vibe_scores: Dict[str, float] = None,
    time_slot_label: str = "Morning",
    group_size: int = 2
) -> Dict[str, Any]:
    """
    Runs forward inference through the Deep Neural Network to predict
    the transit choice distribution and explainable neural activations.
    """
    model = get_trained_dl_transit_model()
    vibes = vibe_scores or {}
    
    is_hill = 1.0 if any(k in (terrain_category or "").lower() or k in (destination_name or "").lower() 
                          for k in ["hill", "mountain", "manali", "rishikesh", "darjeeling", "ooty", "munnar", "shimla", "ladakh", "leh"]) else 0.0
    is_coastal = 1.0 if any(k in (terrain_category or "").lower() or k in (destination_name or "").lower()
                            for k in ["beach", "coast", "goa", "pondicherry", "varkala", "puri", "andamans"]) else 0.0
    is_metro = 1.0 if any(k in (destination_name or "").lower() for k in ["delhi", "mumbai", "bengaluru", "kolkata", "chennai", "hyderabad", "jaipur"]) else 0.0
    
    tod_val = 0.0 if "morn" in time_slot_label.lower() else (0.5 if "noon" in time_slot_label.lower() else 1.0)
    norm_group = min(1.0, max(0.25, group_size / 4.0))
    
    feature_vector = np.array([[
        np.log1p(max(0.1, dist_km)),
        is_hill,
        is_coastal,
        is_metro,
        vibes.get("nature", 50.0) / 100.0,
        vibes.get("adventure", 50.0) / 100.0,
        vibes.get("peacefulness", 50.0) / 100.0,
        vibes.get("crowd_match", 50.0) / 100.0,
        vibes.get("visual_atmosphere", 50.0) / 100.0,
        tod_val,
        norm_group
    ]], dtype=np.float32)
    
    with torch.no_grad():
        x_tensor = torch.tensor(feature_vector)
        # In eval mode with batch_size 1, avoid batchnorm eval error by using track_running_stats
        probs = model(x_tensor).numpy()[0]
        
    chosen_idx = int(np.argmax(probs))
    confidence = float(probs[chosen_idx]) * 100.0
    
    # Format class probabilities breakdown for viva/visual presentation
    prob_distribution = [
        {
            "mode_id": idx,
            "mode_name": CLASSES[idx],
            "probability": round(float(probs[idx]) * 100.0, 1),
            "is_chosen": idx == chosen_idx,
            "eco_score": MODE_DETAILS[idx]["eco_score"],
            "comfort_score": MODE_DETAILS[idx]["comfort_score"]
        }
        for idx in range(len(CLASSES))
    ]
    prob_distribution.sort(key=lambda x: x["probability"], reverse=True)
    
    meta_info = MODE_DETAILS[chosen_idx]
    est_mins = max(4, int((dist_km / meta_info["speed_kmh"]) * 60))
    est_fare = meta_info["base_fare"] + int(dist_km * meta_info["per_km"])
    
    price_tag = "Free (Pedestrian)" if chosen_idx == 0 else f"₹{max(30, int(est_fare * 0.85))} - ₹{int(est_fare * 1.25)}"
    
    return {
        "chosen_mode": CLASSES[chosen_idx],
        "confidence_score": round(confidence, 1),
        "est_time_mins": est_mins,
        "est_price_range": price_tag,
        "mode_icon": meta_info["icon"],
        "eco_rating": meta_info["eco_score"],
        "comfort_rating": meta_info["comfort_score"],
        "ai_rationale": meta_info["recommendation"],
        "probability_distribution": prob_distribution,
        "dl_architecture": "PyTorch Deep Choice MLP (64-32-5 with BatchNorm & LeakyReLU)"
    }
