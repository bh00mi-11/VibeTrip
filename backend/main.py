import os
import glob
import uuid
import secrets
from typing import Dict, Optional, List, Any
from pathlib import Path
from PIL import Image

from fastapi import FastAPI, HTTPException, Depends, UploadFile, File, Form, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_, desc

import sys
from pathlib import Path

# Ensure project root is in sys.path
_root_dir = str(Path(__file__).resolve().parent.parent)
if _root_dir not in sys.path:
    sys.path.insert(0, _root_dir)

try:
    from .database import get_db, engine
    from .models import (
        Base, Destination, Photo, VibeScore, User, TravelerProfile,
        Trip, LocalPlace, BuddyInterest, BuddyRequest, Report, UserBlock
    )
    from .auth import (
        hash_password, verify_password, create_access_token,
        get_current_user, get_optional_user, require_role, sanitize_text
    )
    from .itinerary_engine import build_itinerary
    from .matcher import compute_compatibility
    from .overpass_service import query_osm_places
except (ImportError, ValueError):
    from backend.database import get_db, engine
    from backend.models import (
        Base, Destination, Photo, VibeScore, User, TravelerProfile,
        Trip, LocalPlace, BuddyInterest, BuddyRequest, Report, UserBlock
    )
    from backend.auth import (
        hash_password, verify_password, create_access_token,
        get_current_user, get_optional_user, require_role, sanitize_text
    )
    from backend.itinerary_engine import build_itinerary
    from backend.matcher import compute_compatibility
    from backend.overpass_service import query_osm_places

# Initialize DB tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="VibeTrip Multi-User API")

try:
    from .ml_dashboard.router import router as ml_router
except (ImportError, ValueError):
    from backend.ml_dashboard.router import router as ml_router

app.include_router(ml_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount images directory
images_dir = Path(__file__).resolve().parent.parent / "images"
os.makedirs(images_dir, exist_ok=True)
app.mount("/images", StaticFiles(directory=str(images_dir)), name="images")



# Mount modern React web app build
frontend_react_dist = Path(__file__).resolve().parent.parent / "frontend-react" / "dist"
if frontend_react_dist.exists():
    app.mount("/react", StaticFiles(directory=str(frontend_react_dist), html=True), name="frontend_react")

from fastapi.responses import RedirectResponse

@app.get("/")
def root():
    return RedirectResponse(url="/react/")

# In-memory simple rate limiting for login attempts
_LOGIN_ATTEMPTS = {} # ip -> [timestamps]

def check_login_rate_limit(client_ip: str):
    import time
    now = time.time()
    attempts = [t for t in _LOGIN_ATTEMPTS.get(client_ip, []) if now - t < 60]
    if len(attempts) >= 10:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many failed login attempts. Please wait 1 minute before trying again."
        )
    attempts.append(now)
    _LOGIN_ATTEMPTS[client_ip] = attempts


# ==============================================================================
# 1. AUTH & USER PROFILE ENDPOINTS
# ==============================================================================

class SignupRequest(BaseModel):
    name: str
    email: str
    password: str
    role: str # tourist, local, or guide
    home_city: Optional[str] = ""
    bio: Optional[str] = ""
    interest_tags: Optional[str] = ""
    contact_info: Optional[str] = ""
    license_number: Optional[str] = ""
    upi_id: Optional[str] = ""
    daily_rate: Optional[str] = ""

class LoginRequest(BaseModel):
    email: str
    password: str

@app.post("/api/auth/signup")
def signup(req: SignupRequest, db: Session = Depends(get_db)):
    if len(req.password) < 8:
        raise HTTPException(status_code=400, detail="Password must be at least 8 characters long.")
    
    clean_role = req.role.strip().lower()
    if clean_role not in ("tourist", "local", "guide"):
        raise HTTPException(status_code=400, detail="Role must be 'tourist', 'local', or 'guide'. Admin cannot be created via signup.")
    
    clean_email = req.email.strip().lower()
    existing = db.query(User).filter(User.email == clean_email).first()
    if existing:
        raise HTTPException(status_code=400, detail="An account with this email address already exists.")

    new_user = User(
        name=sanitize_text(req.name),
        email=clean_email,
        password_hash=hash_password(req.password),
        role=clean_role,
        is_active=True,
        is_demo=False
    )
    db.add(new_user)
    db.flush()

    # Build formatted contact & payout string for guides if provided
    contact_payout = sanitize_text(req.contact_info)
    if clean_role == "guide":
        upi = req.upi_id.strip() if req.upi_id else "direct.upi@vibetrip"
        rate = req.daily_rate.strip() if req.daily_rate else "INR 3,000/day"
        lic = req.license_number.strip() if req.license_number else "VERIFIED-GUIDE"
        contact_payout = f"Direct UPI: {upi} | Daily Rate: {rate} | License: {lic}"

    guide_bio = sanitize_text(req.bio)
    if clean_role == "guide" and "[Licensed Guide" not in guide_bio:
        guide_bio = f"{guide_bio} [Licensed Guide - Direct Payout Enabled]" if guide_bio else "Certified Tour & Trek Guide [Licensed Guide - Direct Payout Enabled]"

    profile = TravelerProfile(
        user_id=new_user.id,
        home_city=sanitize_text(req.home_city),
        bio=guide_bio,
        interest_tags=sanitize_text(req.interest_tags),
        visibility="destination_only" if clean_role != "guide" else "public",
        contact_info=contact_payout
    )
    db.add(profile)
    db.commit()

    token = create_access_token({"sub": new_user.id, "role": new_user.role, "name": new_user.name})
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "id": new_user.id,
            "name": new_user.name,
            "role": new_user.role,
            "is_demo": False
        }
    }

@app.post("/api/auth/login")
def login(req: LoginRequest, request: Request, db: Session = Depends(get_db)):
    client_ip = request.client.host if request.client else "unknown"
    check_login_rate_limit(client_ip)

    generic_error = "Invalid email or password."
    clean_email = req.email.strip().lower()
    user = db.query(User).filter(User.email == clean_email).first()
    
    if not user or not verify_password(req.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=generic_error)

    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Account is deactivated. Please contact support.")

    token = create_access_token({"sub": user.id, "role": user.role, "name": user.name})
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "name": user.name,
            "role": user.role,
            "is_demo": user.is_demo
        }
    }

@app.get("/api/auth/me")
def get_me(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    prof = db.query(TravelerProfile).filter(TravelerProfile.user_id == user.id).first()
    return {
        "id": user.id,
        "name": user.name,
        "email": user.email, # only returned to the user themselves
        "role": user.role,
        "is_demo": user.is_demo,
        "profile": {
            "home_city": prof.home_city if prof else "",
            "bio": prof.bio if prof else "",
            "interest_tags": prof.interest_tags if prof else "",
            "visibility": prof.visibility if prof else "destination_only",
            "contact_info": prof.contact_info if prof else ""
        }
    }

class ProfileUpdateRequest(BaseModel):
    name: Optional[str] = None
    home_city: Optional[str] = None
    bio: Optional[str] = None
    interest_tags: Optional[str] = None
    visibility: Optional[str] = None # public, destination_only, hidden
    contact_info: Optional[str] = None

@app.put("/api/auth/profile")
def update_profile(req: ProfileUpdateRequest, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if req.name is not None and req.name.strip():
        user.name = sanitize_text(req.name)
    prof = db.query(TravelerProfile).filter(TravelerProfile.user_id == user.id).first()
    if not prof:
        prof = TravelerProfile(user_id=user.id)
        db.add(prof)
    if req.home_city is not None:
        prof.home_city = sanitize_text(req.home_city)
    if req.bio is not None:
        prof.bio = sanitize_text(req.bio)
    if req.interest_tags is not None:
        prof.interest_tags = sanitize_text(req.interest_tags)
    if req.visibility is not None and req.visibility in ("public", "destination_only", "hidden"):
        prof.visibility = req.visibility
    if req.contact_info is not None:
        prof.contact_info = sanitize_text(req.contact_info)
    db.commit()
    return {"message": "Profile updated successfully"}


# ==============================================================================
# 2. CORE VIBETRIP RECOMMENDATION & DESTINATIONS
# ==============================================================================

class RecommendRequest(BaseModel):
    query_text: Optional[str] = ""
    target_dims: Dict[str, str]

def generate_explanation(dest_scores: Dict[str, float], target_dims: Dict[str, str]) -> str:
    diffs = []
    for dim, dir_ in target_dims.items():
        if dim not in dest_scores: continue
        val = dest_scores[dim]
        if dir_ == "high":
            match_score = val
        elif dir_ == "low":
            match_score = 100.0 - val
        else: # medium
            match_score = max(0.0, 100.0 - 2.0 * abs(val - 50.0))
        diffs.append((dim, match_score, dir_, val))
        
    diffs.sort(key=lambda x: x[1], reverse=True)
    top_matches = diffs[:2]
    
    explanation = "Why this matches: "
    reasons = []
    for dim, score, dir_, val in top_matches:
        if score > 70:
            reasons.append(f"Strongly aligns with your desire for {dir_} {dim} (score: {val:.1f}/100).")
        elif score > 50:
            reasons.append(f"Moderately fits your {dir_} {dim} preference (score: {val:.1f}/100).")
            
    explanation += " ".join(reasons) if reasons else "It has a balanced profile overall."
    
    weak_mismatches = []
    for dim, score, dir_, val in diffs:
        if dir_ == "high" and val < 60:
            weak_mismatches.append((dim, score, dir_, val, f"{dim.replace('_', ' ').capitalize()} was marked as high, but this destination scores {val:.1f}/100."))
        elif dir_ == "low" and val > 60:
            weak_mismatches.append((dim, score, dir_, val, f"You wanted low {dim.replace('_', ' ')}, but this destination scores {val:.1f}/100 here."))
        elif dir_ == "medium" and abs(val - 50.0) > 30:
            weak_mismatches.append((dim, score, dir_, val, f"You preferred moderate {dim.replace('_', ' ')}, but this destination scores {val:.1f}/100."))
            
    weak_mismatches.sort(key=lambda x: x[1])
    
    mismatch_text = []
    if len(weak_mismatches) > 0:
        for m in weak_mismatches[:2]:
            mismatch_text.append(m[4])
    else:
        biggest_mismatch = diffs[-1] if len(diffs) > 2 else None
        if biggest_mismatch and biggest_mismatch[1] < 40:
            dim, score, dir_, val = biggest_mismatch
            mismatch_text.append(f"The {dim.replace('_', ' ')} is {val:.1f}/100, which might not perfectly fit your '{dir_}' requirement.")
            
    if mismatch_text:
        explanation += "<br><br><strong>Possible mismatch:</strong> " + " ".join(mismatch_text)
        
    return explanation

# Precomputed TF-IDF vectorizer and destination corpus matrix
_tfidf_vectorizer = None
_tfidf_matrix = None
_tfidf_dest_names = []

def get_tfidf_similarity(query_text: str, dests: list) -> Dict[str, float]:
    global _tfidf_vectorizer, _tfidf_matrix, _tfidf_dest_names
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
    
    current_names = [d.name for d in dests]
    if _tfidf_matrix is None or _tfidf_dest_names != current_names:
        corpus = [
            f"{d.name} {d.name} {d.state or ''} {d.category or ''} {d.description or ''} {(d.top_attractions or '').replace('|', ' ')}"
            for d in dests
        ]
        _tfidf_vectorizer = TfidfVectorizer(ngram_range=(1, 2), stop_words='english')
        _tfidf_matrix = _tfidf_vectorizer.fit_transform(corpus)
        _tfidf_dest_names = current_names
        
    try:
        q_vec = _tfidf_vectorizer.transform([query_text])
        sims = cosine_similarity(q_vec, _tfidf_matrix)[0]
        max_sim = max(sims) if len(sims) > 0 and max(sims) > 0 else 1.0
        
        scores = {}
        for idx, d in enumerate(dests):
            # Scale relative to max so top matching keywords reach ~100%
            raw = float(sims[idx])
            scores[d.name] = (raw / max_sim) * 100.0 if raw > 0 else 0.0
        return scores
    except Exception as e:
        print(f"TF-IDF scoring error: {e}")
@app.post("/api/recommend")
def recommend(req: RecommendRequest, db: Session = Depends(get_db)):
    target_dims = req.target_dims or {"nature": "high", "visual_atmosphere": "high"}
    query_text = (req.query_text or "").strip()
    
    # Query published destinations with vibe scores
    dests = db.query(Destination).filter(Destination.status == "published").all()
    results = []

    # Fast semantic & keyword similarity
    query_sims = get_tfidf_similarity(query_text, dests) if query_text else {}

    for d in dests:
        vb = d.vibe_score
        if not vb:
            continue
        scores = {
            "nature": vb.nature,
            "adventure": vb.adventure,
            "peacefulness": vb.peacefulness,
            "crowd_match": vb.crowd_match,
            "visual_atmosphere": vb.visual_atmosphere
        }

        total_score = 0.0
        total_weight = 0.0
        penalty = 0.0

        for dim, dir_ in target_dims.items():
            val = scores.get(dim, 50.0)
            if dir_ == "high":
                w = 2.5
                dim_score = val
                # Penalize severe deficiency if user explicitly requested high
                if val < 45.0:
                    penalty += (45.0 - val) * 0.75
            elif dir_ == "low":
                w = 2.5
                dim_score = 100.0 - val
                # Penalize severe excess if user explicitly requested low
                if val > 55.0:
                    penalty += (val - 55.0) * 0.75
            elif dir_ == "medium":
                w = 1.0
                dim_score = max(0.0, 100.0 - 1.5 * abs(val - 50.0))
            else:
                w = 1.0
                dim_score = 50.0

            total_score += w * dim_score
            total_weight += w

        base_fit = total_score / total_weight if total_weight > 0 else 50.0
        vibe_score = max(0.0, min(100.0, base_fit - penalty))

        # Combine with text semantic similarity if query_text was entered
        if query_text and d.name in query_sims:
            text_sim = query_sims[d.name]
            # 50% vibe profile + 50% semantic text relevance
            overall_score = 0.50 * vibe_score + 0.50 * text_sim
        else:
            overall_score = vibe_score

        # Primary photo
        p_obj = db.query(Photo).filter(Photo.destination == d.name).first()
        photo_filename = p_obj.filename if p_obj else "photo_01.jpg"
        photo_url = f"/images/{d.name}/{photo_filename}"

        base_explanation = generate_explanation(scores, target_dims)
        if query_text and d.name in query_sims and query_sims[d.name] > 40:
            text_note = f"<strong>Keywords match:</strong> '{query_text}' matches highlights & activities in {d.name} ({query_sims[d.name]:.0f}% semantic alignment).<br>"
            explanation = text_note + base_explanation
        else:
            explanation = base_explanation

        results.append({
            "name": d.name,
            "state": d.state or "",
            "region": d.region or "",
            "category": d.category or "",
            "overall_match_score": overall_score,
            "scores": scores,
            "photo_url": photo_url,
            "score_source": vb.score_source,
            "is_ai_estimated": vb.score_source in ("model_inference", "admin_override"),
            "explanation": explanation
        })

    results.sort(key=lambda x: x["overall_match_score"], reverse=True)
    return {"recommendations": results[:10]}


@app.post("/api/search-by-image")
async def search_by_image(
    photo: UploadFile = File(...),
    query_text: Optional[str] = Form(""),
    db: Session = Depends(get_db)
):
    """
    Multimodal visual search: Tourist uploads a travel photo (scenery, moodboard, aesthetic).
    The system extracts CLIP ViT-B/32 visual embeddings, estimates the 5D vibe scores,
    and returns matching destinations along with the estimated vibe scores.
    """
    content = await photo.read()
    if len(content) > 10 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="Photo exceeds 10 MB size limit.")

    temp_dir = Path(__file__).resolve().parent.parent / "images" / "_temp_searches"
    os.makedirs(temp_dir, exist_ok=True)
    temp_filename = f"search_{uuid.uuid4().hex[:8]}.jpg"
    temp_path = temp_dir / temp_filename

    with open(temp_path, "wb") as f:
        f.write(content)

    try:
        with Image.open(temp_path) as img:
            img = img.convert("RGB")
            img.save(temp_path, "JPEG", quality=90)
    except Exception as e:
        if temp_path.exists():
            temp_path.unlink()
        raise HTTPException(status_code=400, detail=f"Invalid image format: {e}")

    try:
        from .vibe_estimator import estimate_image_vibe_scores
        vibe_result = estimate_image_vibe_scores([str(temp_path)], text_hint=query_text or "")
        inferred_scores = vibe_result["scores"]
        recommended_vibes = vibe_result["recommended_vibes"]

        # Now perform recommendation matching against destinations using the inferred vibe profile
        dests = db.query(Destination).filter(Destination.status == "published").all()
        query_sims = get_tfidf_similarity(query_text, dests) if query_text else {}
        results = []

        for d in dests:
            vb = d.vibe_score
            if not vb:
                continue
            scores = {
                "nature": vb.nature,
                "adventure": vb.adventure,
                "peacefulness": vb.peacefulness,
                "crowd_match": vb.crowd_match,
                "visual_atmosphere": vb.visual_atmosphere
            }

            # Euclidean similarity in 5D vibe space: 100 - (distance / max_dist) * 100
            sq_diffs = sum((scores[k] - inferred_scores.get(k, 50.0)) ** 2 for k in scores)
            dist = sq_diffs ** 0.5
            # Max possible distance across 5 dimensions [0, 100] is sqrt(5 * 100^2) ≈ 223.6
            vibe_sim = max(0.0, 100.0 - (dist / 223.6) * 100.0)

            if query_text and d.name in query_sims:
                text_sim = query_sims[d.name]
                overall_score = 0.65 * vibe_sim + 0.35 * text_sim
            else:
                overall_score = vibe_sim

            p_obj = db.query(Photo).filter(Photo.destination == d.name).first()
            photo_filename = p_obj.filename if p_obj else "photo_01.jpg"
            photo_url = f"/images/{d.name}/{photo_filename}"

            base_explanation = f"<strong>Visual Vibe Match:</strong> Matches {vibe_sim:.1f}% of the uploaded photo's visual aesthetics."
            results.append({
                "name": d.name,
                "state": d.state or "",
                "region": d.region or "",
                "category": d.category or "",
                "overall_match_score": round(overall_score, 1),
                "scores": scores,
                "photo_url": photo_url,
                "score_source": vb.score_source,
                "is_ai_estimated": vb.score_source in ("model_inference", "admin_override"),
                "explanation": base_explanation
            })

        results.sort(key=lambda x: x["overall_match_score"], reverse=True)

        return {
            "inferred_vibes": inferred_scores,
            "recommended_sliders": recommended_vibes,
            "recommendations": results[:10]
        }
    finally:
        # Clean up temporary search photo
        try:
            if temp_path.exists():
                temp_path.unlink()
        except Exception:
            pass


@app.get("/api/destination/{name}")
def get_destination(name: str, db: Session = Depends(get_db)):
    d = db.query(Destination).filter(Destination.name == name).first()
    if not d:
        raise HTTPException(status_code=404, detail="Destination not found.")

    vb = d.vibe_score
    scores = {}
    score_source = "model_oof"
    if vb:
        scores = {
            "nature": vb.nature,
            "adventure": vb.adventure,
            "peacefulness": vb.peacefulness,
            "crowd_match": vb.crowd_match,
            "visual_atmosphere": vb.visual_atmosphere
        }
        score_source = vb.score_source

    photos = db.query(Photo).filter(Photo.destination == name).all()
    photo_list = []
    seen_files = set()
    for p in photos:
        if p.filename in seen_files:
            continue
        seen_files.add(p.filename)
        photo_list.append({
            "url": f"/images/{name}/{p.filename}",
            "attraction": p.attraction or "",
            "author": p.author or "",
            "license": p.license or "",
            "source_url": p.source_url or ""
        })

    return {
        "name": d.name,
        "state": d.state or "",
        "region": d.region or "",
        "category": d.category or "",
        "description": d.description or "",
        "top_attractions": d.top_attractions or "",
        "best_time_to_visit": d.best_time or "",
        "latitude": d.latitude,
        "longitude": d.longitude,
        "status": d.status,
        "source": d.source,
        "score_source": score_source,
        "is_ai_estimated": score_source in ("model_inference", "admin_override"),
        "photos": photo_list,
        "scores": scores
    }


# ==============================================================================
# 3. ITINERARY GENERATOR & SAVED TRIPS
# ==============================================================================

class TripPlanRequest(BaseModel):
    destination: str
    days: Optional[int] = 3
    vibe_preferences: Optional[Dict[str, float]] = None

@app.post("/api/trip-plan")
def create_trip_plan(req: TripPlanRequest, db: Session = Depends(get_db)):
    d = db.query(Destination).filter(Destination.name == req.destination).first()
    if not d:
        raise HTTPException(status_code=404, detail="Destination not found.")

    vb = d.vibe_score
    scores = {
        "nature": vb.nature if vb else 50.0,
        "adventure": vb.adventure if vb else 50.0,
        "peacefulness": vb.peacefulness if vb else 50.0,
        "crowd_match": vb.crowd_match if vb else 50.0,
        "visual_atmosphere": vb.visual_atmosphere if vb else 50.0,
    }

    approved_places = db.query(LocalPlace).filter(
        LocalPlace.destination == d.name,
        LocalPlace.status == "approved"
    ).all()

    places_dicts = [
        {
            "id": p.id,
            "name": p.name,
            "category": p.category,
            "latitude": p.latitude,
            "longitude": p.longitude,
            "description": p.description,
            "source": p.source,
            "crowd_hint": p.crowd_hint
        }
        for p in approved_places
    ]

    meta = {
        "best_time": d.best_time,
        "top_attractions": d.top_attractions,
        "latitude": d.latitude,
        "longitude": d.longitude
    }

    plan = build_itinerary(
        destination_name=d.name,
        meta=meta,
        vibe_scores=scores,
        local_places=places_dicts,
        days=req.days or 3,
        user_vibes=req.vibe_preferences or scores
    )
    return plan

class SaveTripRequest(BaseModel):
    destination: str
    itinerary: Dict[str, Any]

@app.post("/api/trips/save")
def save_trip(req: SaveTripRequest, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    import json
    share_token = secrets.token_urlsafe(16)
    trip = Trip(
        user_id=user.id,
        destination=req.destination,
        itinerary_json=json.dumps(req.itinerary),
        share_token=share_token
    )
    db.add(trip)
    db.commit()
    return {
        "message": "Trip saved successfully",
        "trip_id": trip.id,
        "share_token": share_token,
        "share_url": f"/app/share.html?token={share_token}"
    }

@app.get("/api/trips/my")
def get_my_trips(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    import json
    trips = db.query(Trip).filter(Trip.user_id == user.id).order_by(desc(Trip.created_at)).all()
    results = []
    for t in trips:
        results.append({
            "id": t.id,
            "destination": t.destination,
            "share_token": t.share_token,
            "created_at": t.created_at.strftime("%Y-%m-%d %H:%M"),
            "itinerary": json.loads(t.itinerary_json)
        })
    return {"trips": results}

@app.get("/api/trips/shared/{token}")
def get_shared_trip(token: str, db: Session = Depends(get_db)):
    import json
    trip = db.query(Trip).filter(Trip.share_token == token).first()
    if not trip:
        raise HTTPException(status_code=404, detail="Shared trip not found.")
    owner = db.query(User).filter(User.id == trip.user_id).first()
    return {
        "trip_id": trip.id,
        "destination": trip.destination,
        "created_by": owner.name if owner else "Traveler",
        "created_at": trip.created_at.strftime("%Y-%m-%d"),
        "itinerary": json.loads(trip.itinerary_json)
    }


# ==============================================================================
# 4. NEARBY & LOCAL EXPERIENCES
# ==============================================================================

@app.get("/api/local-experiences/{destination}")
def get_local_experiences(
    destination: str,
    category: Optional[str] = None,
    sort_vibe: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(LocalPlace).filter(
        LocalPlace.destination == destination,
        LocalPlace.status == "approved"
    )
    if category and category.lower() != "all":
        query = query.filter(LocalPlace.category == category.lower())

    places = query.all()
    
    # Optional sorting by vibe preference dimension
    if sort_vibe in ("peacefulness", "nature"):
        places.sort(key=lambda p: 0 if p.category in ("viewpoint", "cafe", "activity") else 1)
    elif sort_vibe == "adventure":
        places.sort(key=lambda p: 0 if p.category in ("activity", "attraction") else 1)

    results = []
    for p in places:
        # Determine clean source badge
        if p.source == "osm":
            source_label = "OpenStreetMap"
        elif p.source == "admin":
            source_label = "Added by admin"
        else:
            source_label = "Added by a local"

        results.append({
            "id": p.id,
            "name": p.name,
            "category": p.category,
            "latitude": p.latitude,
            "longitude": p.longitude,
            "description": p.description or "",
            "contact_info": p.contact_info or "",
            "source": p.source,
            "source_label": source_label,
            "crowd_hint": p.crowd_hint or ""
        })

    # Include certified professional guides if filtering by 'guide' or 'all'
    if not category or category.lower() in ("all", "guide", "activity"):
        guides = db.query(User).join(TravelerProfile).filter(
            User.role == "guide",
            User.is_active == True,
            TravelerProfile.home_city.ilike(f"%{destination}%")
        ).all()

        for g in guides:
            prof = g.profile
            payout_info = prof.contact_info if prof else ""
            if g.is_demo:
                guide_label = "Demo Guide"
            elif g.is_verified:
                guide_label = "Verified Guide"
            else:
                guide_label = "Registered Guide"

            results.append({
                "id": 90000 + g.id,
                "name": f"{g.name} ({guide_label})",
                "category": "guide",
                "latitude": None,
                "longitude": None,
                "description": prof.bio if prof else "Local mountain / heritage guide.",
                "contact_info": payout_info,
                "source": "admin" if g.is_verified else "local_user",
                "source_label": guide_label,
                "is_verified": bool(g.is_verified),
                "is_demo": bool(g.is_demo),
                "crowd_hint": "Direct Payout & Verification Active" if g.is_verified else ("Demo Guide Profile" if g.is_demo else "Verification Pending")
            })

    return {
        "destination": destination,
        "total": len(results),
        "experiences": results
    }

@app.get("/api/locals/{destination}")
def get_locals_for_destination(
    destination: str,
    user: Optional[User] = Depends(get_optional_user),
    db: Session = Depends(get_db)
):
    """Retrieve community locals / hosts living in or representing this destination."""
    locals_query = db.query(User).join(TravelerProfile).filter(
        User.role == "local",
        User.is_active == True,
        TravelerProfile.home_city.ilike(f"%{destination}%")
    )
    
    current_user_id = user.id if user else None
    if current_user_id:
        locals_query = locals_query.filter(User.id != current_user_id)
        blocked_ids = [
            b.blocked_id for b in db.query(UserBlock).filter(UserBlock.blocker_id == current_user_id).all()
        ] + [
            b.blocker_id for b in db.query(UserBlock).filter(UserBlock.blocked_id == current_user_id).all()
        ]
        if blocked_ids:
            locals_query = locals_query.filter(User.id.notin_(blocked_ids))

    local_users = locals_query.all()
    
    # Check if there are any submitted local places by these locals to count
    results = []
    for u in local_users:
        prof = u.profile
        conn_status = None
        if current_user_id:
            req = db.query(BuddyRequest).filter(
                ((BuddyRequest.from_user == current_user_id) & (BuddyRequest.to_user == u.id)) |
                ((BuddyRequest.from_user == u.id) & (BuddyRequest.to_user == current_user_id))
            ).first()
            if req:
                conn_status = req.status

        # Count spots shared by this local
        spots_count = db.query(LocalPlace).filter(LocalPlace.submitted_by == u.id).count()

        results.append({
            "user_id": u.id,
            "name": u.name,
            "home_city": prof.home_city if prof else destination,
            "bio": prof.bio if prof else f"Resident & local insider of {destination}.",
            "interest_tags": prof.interest_tags if prof else "",
            "role": "local",
            "is_demo": u.is_demo,
            "spots_shared": spots_count,
            "connection_status": conn_status
        })

    return {
        "destination": destination,
        "count": len(results),
        "locals": results
    }


# ==============================================================================
# 5. TRAVELER MATCHING & BUDDY INTERESTS
# ==============================================================================

class BuddyInterestRequest(BaseModel):
    destination: str
    travel_start: Optional[str] = ""
    travel_end: Optional[str] = ""
    pref_nature: Optional[float] = 50.0
    pref_adventure: Optional[float] = 50.0
    pref_peacefulness: Optional[float] = 50.0
    pref_crowd_match: Optional[float] = 50.0
    pref_visual_atmosphere: Optional[float] = 50.0
    interest_tags: Optional[str] = ""
    note: Optional[str] = ""

@app.post("/api/interests/post")
def post_interest(req: BuddyInterestRequest, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    interest = BuddyInterest(
        user_id=user.id,
        destination=req.destination,
        travel_start=req.travel_start,
        travel_end=req.travel_end,
        pref_nature=req.pref_nature or 50.0,
        pref_adventure=req.pref_adventure or 50.0,
        pref_peacefulness=req.pref_peacefulness or 50.0,
        pref_crowd_match=req.pref_crowd_match or 50.0,
        pref_visual_atmosphere=req.pref_visual_atmosphere or 50.0,
        interest_tags=sanitize_text(req.interest_tags),
        note=sanitize_text(req.note),
        active=True
    )
    db.add(interest)
    db.commit()
    return {"message": "Travel interest posted successfully", "interest_id": interest.id}

@app.get("/api/interests/my")
def get_my_interests(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    interests = db.query(BuddyInterest).filter(BuddyInterest.user_id == user.id).all()
    results = []
    for i in interests:
        results.append({
            "id": i.id,
            "destination": i.destination,
            "travel_start": i.travel_start,
            "travel_end": i.travel_end,
            "active": i.active,
            "interest_tags": i.interest_tags,
            "note": i.note,
            "vibes": {
                "nature": i.pref_nature,
                "adventure": i.pref_adventure,
                "peacefulness": i.pref_peacefulness,
                "crowd_match": i.pref_crowd_match,
                "visual_atmosphere": i.pref_visual_atmosphere
            }
        })
    return {"interests": results}

@app.patch("/api/interests/{interest_id}/toggle")
def toggle_interest(interest_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    interest = db.query(BuddyInterest).filter(BuddyInterest.id == interest_id, BuddyInterest.user_id == user.id).first()
    if not interest:
        raise HTTPException(status_code=404, detail="Interest not found.")
    interest.active = not interest.active
    db.commit()
    return {"message": f"Interest is now {'active' if interest.active else 'paused'}", "active": interest.active}

@app.delete("/api/interests/{interest_id}")
def delete_interest(interest_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    interest = db.query(BuddyInterest).filter(BuddyInterest.id == interest_id, BuddyInterest.user_id == user.id).first()
    if not interest:
        raise HTTPException(status_code=404, detail="Interest not found.")
    db.delete(interest)
    db.commit()
    return {"message": "Interest deleted successfully"}

@app.get("/api/buddy-matches/{destination}")
@app.get("/api/buddies/{destination}")
def get_travelers_for_destination(
    destination: str,
    user: Optional[User] = Depends(get_optional_user),
    db: Session = Depends(get_db)
):
    # Query all active interests for this destination
    query = db.query(BuddyInterest).join(User).filter(
        BuddyInterest.destination == destination,
        BuddyInterest.active == True,
        User.is_active == True
    )

    # Exclude current user if logged in
    current_user_id = user.id if user else None
    if current_user_id:
        query = query.filter(BuddyInterest.user_id != current_user_id)

        # Exclude blocked users
        blocked_ids = [
            b.blocked_id for b in db.query(UserBlock).filter(UserBlock.blocker_id == current_user_id).all()
        ] + [
            b.blocker_id for b in db.query(UserBlock).filter(UserBlock.blocked_id == current_user_id).all()
        ]
        if blocked_ids:
            query = query.filter(BuddyInterest.user_id.notin_(blocked_ids))

    interests = query.all()
    header_count = len(interests)

    # User's reference vibes
    user_interest = db.query(BuddyInterest).filter(
        BuddyInterest.user_id == current_user_id,
        BuddyInterest.destination == destination,
        BuddyInterest.active == True
    ).first() if current_user_id else None

    user_vibes = {
        "nature": user_interest.pref_nature if user_interest else 60.0,
        "adventure": user_interest.pref_adventure if user_interest else 60.0,
        "peacefulness": user_interest.pref_peacefulness if user_interest else 60.0,
        "crowd_match": user_interest.pref_crowd_match if user_interest else 50.0,
        "visual_atmosphere": user_interest.pref_visual_atmosphere if user_interest else 70.0,
    }
    user_tags = [t.strip() for t in (user_interest.interest_tags or "").split(",") if t.strip()] if user_interest else []

    travelers = []
    for bi in interests:
        u = bi.user_rel
        prof = u.profile

        # Visibility filter
        if prof and prof.visibility == "hidden":
            continue

        buddy_vibes = {
            "nature": bi.pref_nature,
            "adventure": bi.pref_adventure,
            "peacefulness": bi.pref_peacefulness,
            "crowd_match": bi.pref_crowd_match,
            "visual_atmosphere": bi.pref_visual_atmosphere
        }
        buddy_tags = [t.strip() for t in (bi.interest_tags or "").split(",") if t.strip()]

        compat = compute_compatibility(
            user_vibes=user_vibes,
            buddy_vibes=buddy_vibes,
            user_tags=user_tags,
            buddy_tags=buddy_tags,
            user_start=user_interest.travel_start if user_interest else None,
            user_end=user_interest.travel_end if user_interest else None,
            buddy_start=bi.travel_start,
            buddy_end=bi.travel_end
        )

        # Check existing connection request status
        conn_status = None
        if current_user_id:
            req = db.query(BuddyRequest).filter(
                ((BuddyRequest.from_user == current_user_id) & (BuddyRequest.to_user == u.id)) |
                ((BuddyRequest.from_user == u.id) & (BuddyRequest.to_user == current_user_id))
            ).first()
            if req:
                conn_status = req.status

        # NEVER return email or password hash
        travelers.append({
            "user_id": u.id,
            "name": u.name,
            "role": u.role,
            "home_city": prof.home_city if prof else "",
            "bio": prof.bio if prof else "",
            "is_demo": u.is_demo,
            "destination": bi.destination,
            "travel_start": bi.travel_start,
            "travel_end": bi.travel_end,
            "interest_tags": bi.interest_tags,
            "note": bi.note,
            "compatibility": compat["compatibility_score"],
            "compatibility_score": compat["compatibility_score"],
            "breakdown": compat["breakdown"],
            "connection_status": conn_status
        })

    travelers.sort(key=lambda x: x["compatibility"], reverse=True)

    return {
        "destination": destination,
        "count": header_count,
        "travelers": travelers,
        "buddies": travelers
    }


# ==============================================================================
# 6. CONNECTION REQUESTS, CONTACT SHARING, REPORTS & BLOCKS
# ==============================================================================

class ConnectionRequestPayload(BaseModel):
    to_user_id: int
    destination: str
    message: Optional[str] = "Hi! Saw you're visiting too, would love to connect."

@app.post("/api/connections/send")
def send_connection_request(req: ConnectionRequestPayload, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if req.to_user_id == user.id:
        raise HTTPException(status_code=400, detail="Cannot send a connection request to yourself.")
    
    target_user = db.query(User).filter(User.id == req.to_user_id).first()
    if not target_user:
        raise HTTPException(status_code=404, detail="Target user not found.")

    existing = db.query(BuddyRequest).filter(
        BuddyRequest.from_user == user.id,
        BuddyRequest.to_user == req.to_user_id,
        BuddyRequest.destination == req.destination
    ).first()
    if existing:
        return {"message": "Request already sent", "request_id": existing.id, "status": existing.status}

    new_req = BuddyRequest(
        from_user=user.id,
        to_user=req.to_user_id,
        destination=req.destination,
        message=sanitize_text(req.message),
        status="pending"
    )
    db.add(new_req)
    db.commit()
    return {"message": "Connection request sent!", "request_id": new_req.id}

@app.get("/api/connections/inbox")
def get_inbox(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    incoming = db.query(BuddyRequest).filter(BuddyRequest.to_user == user.id).order_by(desc(BuddyRequest.created_at)).all()
    outgoing = db.query(BuddyRequest).filter(BuddyRequest.from_user == user.id).order_by(desc(BuddyRequest.created_at)).all()

    def format_item(r, is_incoming):
        other_user_id = r.from_user if is_incoming else r.to_user
        other_u = db.query(User).filter(User.id == other_user_id).first()
        other_prof = other_u.profile if other_u else None

        # Contact info ONLY revealed if status == 'accepted'
        contact_revealed = ""
        if r.status == "accepted" and other_prof and other_prof.contact_info:
            contact_revealed = other_prof.contact_info

        return {
            "id": r.id,
            "other_user_id": other_user_id,
            "other_user_name": other_u.name if other_u else "Traveler",
            "is_demo": other_u.is_demo if other_u else False,
            "destination": r.destination,
            "message": r.message,
            "status": r.status,
            "contact_revealed": contact_revealed,
            "created_at": r.created_at.strftime("%Y-%m-%d %H:%M")
        }

    return {
        "incoming": [format_item(r, True) for r in incoming],
        "outgoing": [format_item(r, False) for r in outgoing]
    }

@app.post("/api/connections/{request_id}/respond")
def respond_connection(
    request_id: int,
    action: str, # accept / decline
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    req = db.query(BuddyRequest).filter(BuddyRequest.id == request_id, BuddyRequest.to_user == user.id).first()
    if not req:
        raise HTTPException(status_code=404, detail="Request not found.")

    if action == "accept":
        req.status = "accepted"
    elif action == "decline":
        req.status = "declined"
    else:
        raise HTTPException(status_code=400, detail="Action must be 'accept' or 'decline'.")

    db.commit()
    return {"message": f"Connection request {req.status}", "status": req.status}

class ReportBlockRequest(BaseModel):
    target_user_id: int
    reason: str

@app.post("/api/users/report")
def report_user(req: ReportBlockRequest, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if req.target_user_id == user.id:
        raise HTTPException(status_code=400, detail="Cannot report yourself.")
    rep = Report(
        reporter_id=user.id,
        target_user_id=req.target_user_id,
        reason=sanitize_text(req.reason)
    )
    db.add(rep)
    db.commit()
    return {"message": "Report submitted. An administrator will review this profile."}

@app.post("/api/users/block")
def block_user(req: ReportBlockRequest, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if req.target_user_id == user.id:
        raise HTTPException(status_code=400, detail="Cannot block yourself.")
    existing = db.query(UserBlock).filter(
        UserBlock.blocker_id == user.id,
        UserBlock.blocked_id == req.target_user_id
    ).first()
    if not existing:
        b = UserBlock(blocker_id=user.id, blocked_id=req.target_user_id)
        db.add(b)
        db.commit()
    return {"message": "User blocked. You will no longer see or match with each other."}


# ==============================================================================
# 7. LOCAL CONTRIBUTOR ENDPOINTS
# ==============================================================================

class LocalPlaceSubmission(BaseModel):
    destination: str
    name: str
    category: str # cafe/market/food/viewpoint/activity/attraction/guide/stay
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    address: Optional[str] = None
    description: Optional[str] = ""
    contact_info: Optional[str] = ""

@app.post("/api/local/submissions")
@app.post("/api/contribute/submit")
def submit_local_place(
    req: LocalPlaceSubmission,
    user: User = Depends(require_role("tourist", "local", "guide", "admin")),
    db: Session = Depends(get_db)
):
    lat = req.latitude
    lon = req.longitude
    if (lat is None or lon is None) and req.address:
        # Attempt quick geocode
        from .seed_db import geocode_destination
        lat, lon = geocode_destination(req.address, req.destination)

    place = LocalPlace(
        destination=req.destination,
        name=sanitize_text(req.name),
        category=req.category.lower(),
        latitude=lat,
        longitude=lon,
        description=sanitize_text(req.description),
        contact_info=sanitize_text(req.contact_info),
        source="local_user",
        status="pending", # Pending admin approval
        submitted_by=user.id
    )
    db.add(place)
    db.commit()
    return {
        "message": "Submission received and placed in review queue.",
        "id": place.id,
        "status": place.status
    }

@app.get("/api/local/my-submissions")
@app.get("/api/contribute/my")
def get_my_submissions(
    user: User = Depends(require_role("tourist", "local", "guide", "admin")),
    db: Session = Depends(get_db)
):
    places = db.query(LocalPlace).filter(LocalPlace.submitted_by == user.id).all()
    results = []
    for p in places:
        results.append({
            "id": p.id,
            "destination": p.destination,
            "name": p.name,
            "category": p.category,
            "description": p.description,
            "status": p.status,
            "rejection_reason": p.rejection_reason,
            "source": p.source
        })
    return {"submissions": results}

@app.delete("/api/local/submissions/{place_id}")
def withdraw_submission(
    place_id: int,
    user: User = Depends(require_role("local", "admin")),
    db: Session = Depends(get_db)
):
    place = db.query(LocalPlace).filter(LocalPlace.id == place_id, LocalPlace.submitted_by == user.id).first()
    if not place:
        raise HTTPException(status_code=404, detail="Submission not found.")
    db.delete(place)
    db.commit()
    return {"message": "Submission withdrawn successfully"}


# ==============================================================================
# 8. ADMIN PANEL ENDPOINTS (/admin, admin role only)
# ==============================================================================

@app.get("/api/admin/stats")
def get_admin_stats(user: User = Depends(require_role("admin")), db: Session = Depends(get_db)):
    users_by_role = {
        "tourist": db.query(User).filter(User.role == "tourist").count(),
        "local": db.query(User).filter(User.role == "local").count(),
        "guide": db.query(User).filter(User.role == "guide").count(),
        "admin": db.query(User).filter(User.role == "admin").count(),
    }
    dest_count = db.query(Destination).count()
    pending_submissions = db.query(LocalPlace).filter(LocalPlace.status == "pending").count()
    interests_count = db.query(BuddyInterest).filter(BuddyInterest.active == True).count()
    reports_count = db.query(Report).count()

    return {
        "users_by_role": users_by_role,
        "total_destinations": dest_count,
        "pending_submissions": pending_submissions,
        "active_interests": interests_count,
        "total_reports": reports_count
    }

@app.get("/api/admin/users")
def get_admin_users(role: Optional[str] = None, user: User = Depends(require_role("admin")), db: Session = Depends(get_db)):
    q = db.query(User)
    if role:
        q = q.filter(User.role == role)
    users = q.all()
    results = []
    for u in users:
        prof = u.profile
        results.append({
            "id": u.id,
            "name": u.name,
            "email": u.email,
            "role": u.role,
            "home_city": prof.home_city if prof else "",
            "bio": prof.bio if prof else "",
            "interest_tags": prof.interest_tags if prof else "",
            "contact_info": prof.contact_info if prof else "",
            "is_active": u.is_active,
            "is_demo": u.is_demo,
            "is_verified": bool(u.is_verified),
            "created_at": u.created_at.strftime("%Y-%m-%d")
        })
    return {"users": results}

@app.patch("/api/admin/users/{user_id}/toggle-active")
def toggle_user_active(user_id: int, user: User = Depends(require_role("admin")), db: Session = Depends(get_db)):
    u = db.query(User).filter(User.id == user_id).first()
    if not u:
        raise HTTPException(status_code=404, detail="User not found.")
    if u.role == "admin" and u.id == user.id:
        raise HTTPException(status_code=400, detail="Cannot deactivate your own admin account.")
    u.is_active = not u.is_active
    db.commit()
    return {"message": f"User is now {'active' if u.is_active else 'deactivated'}", "is_active": u.is_active}

@app.patch("/api/admin/users/{user_id}/toggle-verify")
def toggle_user_verify(user_id: int, user: User = Depends(require_role("admin")), db: Session = Depends(get_db)):
    u = db.query(User).filter(User.id == user_id).first()
    if not u:
        raise HTTPException(status_code=404, detail="User not found.")
    u.is_verified = not bool(u.is_verified)
    db.commit()
    return {"message": f"User verification status is now {u.is_verified}", "is_verified": u.is_verified}

@app.get("/api/admin/reports")
def get_admin_reports(user: User = Depends(require_role("admin")), db: Session = Depends(get_db)):
    reports = db.query(Report).all()
    results = []
    for r in reports:
        reporter = db.query(User).filter(User.id == r.reporter_id).first()
        target = db.query(User).filter(User.id == r.target_user_id).first()
        results.append({
            "id": r.id,
            "reporter_name": reporter.name if reporter else "Unknown",
            "target_user_id": r.target_user_id,
            "target_user_name": target.name if target else "Unknown",
            "target_is_active": target.is_active if target else False,
            "reason": r.reason,
            "created_at": r.created_at.strftime("%Y-%m-%d %H:%M")
        })
    return {"reports": results}

@app.get("/api/admin/submissions/pending")
def get_pending_submissions(user: User = Depends(require_role("admin")), db: Session = Depends(get_db)):
    places = db.query(LocalPlace).filter(LocalPlace.status == "pending").all()
    results = []
    for p in places:
        sub_user = db.query(User).filter(User.id == p.submitted_by).first()
        results.append({
            "id": p.id,
            "destination": p.destination,
            "name": p.name,
            "category": p.category,
            "latitude": p.latitude,
            "longitude": p.longitude,
            "description": p.description,
            "contact_info": p.contact_info,
            "submitted_by_name": sub_user.name if sub_user else "Local user",
            "submitted_by_role": sub_user.role if sub_user else ""
        })
    return {"pending_submissions": results}

class SubmissionReviewRequest(BaseModel):
    action: str # approve / reject
    rejection_reason: Optional[str] = ""

@app.post("/api/admin/submissions/{place_id}/review")
def review_submission(
    place_id: int,
    req: SubmissionReviewRequest,
    user: User = Depends(require_role("admin")),
    db: Session = Depends(get_db)
):
    place = db.query(LocalPlace).filter(LocalPlace.id == place_id).first()
    if not place:
        raise HTTPException(status_code=404, detail="Submission not found.")

    if req.action == "approve":
        place.status = "approved"
        place.rejection_reason = None
    elif req.action == "reject":
        place.status = "rejected"
        place.rejection_reason = sanitize_text(req.rejection_reason)
    else:
        raise HTTPException(status_code=400, detail="Action must be 'approve' or 'reject'.")

    db.commit()
    return {"message": f"Place {place.status}", "status": place.status}

# Add destination with photos, geocoding & vibe estimation
@app.post("/api/admin/destinations/estimate-vibe")
async def admin_estimate_vibe(
    name: str = Form(...),
    category: str = Form(...),
    description: str = Form(...),
    top_attractions: str = Form(...),
    photos: List[UploadFile] = File(...),
    user: User = Depends(require_role("admin"))
):
    if len(photos) < 4:
        raise HTTPException(status_code=400, detail="At least 4 photos are required for AI vibe estimation.")

    # Save photos to temporary scratch directory for embedding
    temp_dir = Path(__file__).resolve().parent.parent / "images" / "_temp" / sanitize_text(name)
    os.makedirs(temp_dir, exist_ok=True)
    saved_paths = []

    for idx, p in enumerate(photos):
        content = await p.read()
        if len(content) > 5 * 1024 * 1024:
            raise HTTPException(status_code=400, detail=f"Photo {p.filename} exceeds 5 MB size limit.")
        
        file_path = temp_dir / f"temp_{idx}.jpg"
        with open(file_path, "wb") as f:
            f.write(content)
        # Re-encode with Pillow
        try:
            with Image.open(file_path) as img:
                img = img.convert("RGB")
                img.save(file_path, "JPEG", quality=90)
            saved_paths.append(str(file_path))
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Invalid image file {p.filename}: {e}")

    # Build fused embedding & run inference
    from .vibe_estimator import estimate_vibe_scores
    text_input = f"{category} {description} {top_attractions.replace('|', ' ')}"
    estimated = estimate_vibe_scores(text_input, saved_paths)

    return {
        "destination": name,
        "estimated_vibe_scores": estimated
    }

@app.post("/api/admin/destinations/create")
async def admin_create_destination(
    name: str = Form(...),
    state: str = Form(""),
    region: str = Form(""),
    category: str = Form(""),
    best_time: str = Form(""),
    description: str = Form(""),
    top_attractions: str = Form(""),
    latitude: Optional[float] = Form(None),
    longitude: Optional[float] = Form(None),
    status: str = Form("published"),
    # 5 Vibe scores
    nature: float = Form(50.0),
    adventure: float = Form(50.0),
    peacefulness: float = Form(50.0),
    crowd_match: float = Form(50.0),
    visual_atmosphere: float = Form(50.0),
    score_source: str = Form("model_inference"), # model_inference or admin_override
    # Photo details
    photos: List[UploadFile] = File(...),
    photo_authors: Optional[str] = Form("Admin Upload"),
    photo_licenses: Optional[str] = Form("CC BY-SA 4.0"),
    user: User = Depends(require_role("admin")),
    db: Session = Depends(get_db)
):
    clean_name = sanitize_text(name)
    existing = db.query(Destination).filter(Destination.name == clean_name).first()
    if existing:
        raise HTTPException(status_code=400, detail=f"Destination '{clean_name}' already exists.")

    if len(photos) < 4:
        raise HTTPException(status_code=400, detail="At least 4 photos are required.")

    # Geocode if lat/lon not provided
    lat = latitude
    lon = longitude
    if lat is None or lon is None:
        try:
            from scripts_db_setup.seed_db import geocode_destination
            lat, lon = geocode_destination(clean_name, state)
        except Exception:
            lat, lon = None, None
        if lat is None or lon is None:
            lat, lon = 20.5937, 78.9629

    # Save destination folder
    dest_img_dir = images_dir / clean_name
    os.makedirs(dest_img_dir, exist_ok=True)

    dest_obj = Destination(
        name=clean_name,
        state=sanitize_text(state),
        region=sanitize_text(region),
        category=sanitize_text(category),
        best_time=sanitize_text(best_time),
        description=sanitize_text(description),
        top_attractions=sanitize_text(top_attractions),
        latitude=lat,
        longitude=lon,
        status=status,
        source="admin",
        created_by=user.name
    )
    db.add(dest_obj)
    db.flush()

    # Save photos
    for idx, p in enumerate(photos):
        content = await p.read()
        filename = f"photo_{idx+1:02d}.jpg"
        save_path = dest_img_dir / filename

        with open(save_path, "wb") as f:
            f.write(content)
        # Re-encode with Pillow
        with Image.open(save_path) as img:
            img = img.convert("RGB")
            img.save(save_path, "JPEG", quality=90)

        author = photo_authors[idx] if idx < len(photo_authors) else "Admin Upload"
        lic = photo_licenses[idx] if idx < len(photo_licenses) else "CC BY-SA"

        photo_obj = Photo(
            destination=clean_name,
            filename=filename,
            attraction=clean_name,
            author=sanitize_text(author),
            license=sanitize_text(lic),
            uploaded_by="admin"
        )
        db.add(photo_obj)

    # Save Vibe Score
    vibe_obj = VibeScore(
        destination=clean_name,
        nature=nature,
        adventure=adventure,
        peacefulness=peacefulness,
        crowd_match=crowd_match,
        visual_atmosphere=visual_atmosphere,
        score_source=score_source
    )
    db.add(vibe_obj)
    db.commit()

    # Automatically query Overpass for nearby places
    try:
        osm_places = query_osm_places(lat, lon, clean_name, radius_m=8000, limit=20)
        for op in osm_places:
            lp = LocalPlace(
                destination=clean_name,
                name=op["name"],
                category=op["category"],
                latitude=op["latitude"],
                longitude=op["longitude"],
                description=op["description"],
                source="osm",
                osm_id=op["osm_id"],
                status="approved",
                crowd_hint=op.get("crowd_hint")
            )
            db.add(lp)
        db.commit()
    except Exception as e:
        print(f"Overpass query for new destination {clean_name} skipped: {e}")

    return {
        "message": f"Destination '{clean_name}' created successfully with AI-estimated vibe scores.",
        "destination": clean_name,
        "is_ai_estimated": True
    }

class AdminLocalPlaceCreate(BaseModel):
    destination: str
    name: str
    category: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    description: Optional[str] = ""
    contact_info: Optional[str] = ""

@app.post("/api/admin/local-places/create")
def admin_create_local_place(
    req: AdminLocalPlaceCreate,
    user: User = Depends(require_role("admin")),
    db: Session = Depends(get_db)
):
    lp = LocalPlace(
        destination=req.destination,
        name=sanitize_text(req.name),
        category=req.category.lower(),
        latitude=req.latitude,
        longitude=req.longitude,
        description=sanitize_text(req.description),
        contact_info=sanitize_text(req.contact_info),
        source="admin",
        status="approved" # auto-approved for admin
    )
    db.add(lp)
    db.commit()
    return {"message": "Local place created and approved.", "id": lp.id}

@app.delete("/api/admin/local-places/{place_id}")
def admin_delete_local_place(
    place_id: int,
    user: User = Depends(require_role("admin")),
    db: Session = Depends(get_db)
):
    lp = db.query(LocalPlace).filter(LocalPlace.id == place_id).first()
    if not lp:
        raise HTTPException(status_code=404, detail="Place not found.")
    db.delete(lp)
    db.commit()
    return {"message": "Place deleted successfully."}

# ==============================================================================
# DEEP LEARNING MODEL INTELLIGENCE & BENCHMARK CENTER ENDPOINT
# ==============================================================================

@app.get("/api/admin/dl-benchmarks")
def get_dl_benchmarks(user: User = Depends(require_role("admin"))):
    """
    Returns empirical evaluation results, ablation comparisons,
    cross-validation metrics, and multi-modal architecture metadata.
    """
    import csv
    from pathlib import Path

    root_dir = Path(__file__).resolve().parent.parent
    
    # 1. Ablation benchmark comparisons
    ablation_data = []
    ablation_path = root_dir / "ablation_results.csv"
    if ablation_path.exists():
        with open(ablation_path, "r", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                ablation_data.append({
                    "model_name": row["Model"],
                    "p_at_5": round(float(row["P@5"]), 3),
                    "p_at_10": round(float(row["P@10"]), 3),
                    "r_at_5": round(float(row["R@5"]), 3),
                    "r_at_10": round(float(row["R@10"]), 3),
                    "ndcg_at_5": round(float(row["NDCG@5"]), 3),
                    "ndcg_at_10": round(float(row["NDCG@10"]), 3),
                    "is_full_fusion": "Full Model" in row["Model"]
                })

    # 2. 5-Fold Cross Validation Robustness
    cv_data = []
    cv_path = root_dir / "cv_robustness.csv"
    if cv_path.exists():
        with open(cv_path, "r", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                cv_data.append({
                    "dimension": row["dimension"].replace("_", " ").title(),
                    "r2_score": round(float(row["unshuffled_r2"]), 3),
                    "shuffled_r2_mean": round(float(row["shuffled_r2_mean"]), 3),
                    "mae_score": round(float(row["unshuffled_mae"]), 2),
                    "shuffled_mae_mean": round(float(row["shuffled_mae_mean"]), 2)
                })

    # 3. Model Architecture Metadata
    architecture = {
        "text_encoder": {
            "name": "Sentence-Transformers all-MiniLM-L6-v2",
            "type": "Transformer (all-MiniLM-L6-v2)",
            "embedding_dim": 384,
            "pooling": "Mean Pooling"
        },
        "vision_encoder": {
            "name": "OpenAI CLIP ViT-Base-Patch32",
            "type": "Vision Transformer (ViT)",
            "embedding_dim": 512,
            "image_resolution": "224x224 RGB"
        },
        "fused_space": {
            "name": "Early-Fusion Latent Embedding",
            "total_dim": 896,
            "composition": "384 (Text) + 512 (Visual CLIP)",
            "downstream_regressors": "5 Independent L2 Ridge Estimators"
        },
        "transit_choice_nn": {
            "name": "Multi-Modal Discrete Choice MLP",
            "framework": "PyTorch 2.1+",
            "input_dim": 11,
            "hidden_dims": [64, 32],
            "activation": "LeakyReLU(0.2) + BatchNorm1d",
            "loss_function": "Categorical Cross-Entropy (AdamW)"
        }
    }

    return {
        "ablation_benchmarks": ablation_data,
        "cross_validation_metrics": cv_data,
        "model_architecture": architecture
    }
