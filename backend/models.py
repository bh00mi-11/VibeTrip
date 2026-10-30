from datetime import datetime
from sqlalchemy import (
    create_engine, Column, Integer, String, Float, Boolean,
    DateTime, Text, ForeignKey
)
from sqlalchemy.orm import declarative_base, sessionmaker, relationship

Base = declarative_base()

class Destination(Base):
    __tablename__ = "destinations"

    name = Column(String, primary_key=True)
    state = Column(String, nullable=True)
    region = Column(String, nullable=True)
    category = Column(String, nullable=True)
    best_time = Column(String, nullable=True)
    description = Column(Text, nullable=True)
    top_attractions = Column(Text, nullable=True)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    status = Column(String, default="published") # published / draft
    source = Column(String, default="dataset")   # dataset / admin
    created_by = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    photos = relationship("Photo", back_populates="destination_rel", cascade="all, delete-orphan")
    vibe_score = relationship("VibeScore", back_populates="destination_rel", uselist=False, cascade="all, delete-orphan")
    local_places = relationship("LocalPlace", back_populates="destination_rel", cascade="all, delete-orphan")

class Photo(Base):
    __tablename__ = "photos"

    id = Column(Integer, primary_key=True, autoincrement=True)
    destination = Column(String, ForeignKey("destinations.name"), nullable=False)
    filename = Column(String, nullable=False)
    attraction = Column(String, nullable=True)
    author = Column(Text, nullable=True)
    license = Column(String, nullable=True)
    source_url = Column(Text, nullable=True)
    uploaded_by = Column(String, nullable=True)

    destination_rel = relationship("Destination", back_populates="photos")

class VibeScore(Base):
    __tablename__ = "vibe_scores"

    destination = Column(String, ForeignKey("destinations.name"), primary_key=True)
    
    # 5 predicted scores
    nature = Column(Float, nullable=False)
    adventure = Column(Float, nullable=False)
    peacefulness = Column(Float, nullable=False)
    crowd_match = Column(Float, nullable=False)
    visual_atmosphere = Column(Float, nullable=False)

    # 5 hand-labeled scores (nullable for admin-added places)
    gt_nature = Column(Float, nullable=True)
    gt_adventure = Column(Float, nullable=True)
    gt_peacefulness = Column(Float, nullable=True)
    gt_crowd_match = Column(Float, nullable=True)
    gt_visual_atmosphere = Column(Float, nullable=True)

    score_source = Column(String, default="model_oof") # model_oof / model_inference / admin_override

    destination_rel = relationship("Destination", back_populates="vibe_score")

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False, index=True)
    password_hash = Column(String, nullable=False)
    role = Column(String, default="tourist") # tourist / local / admin
    is_active = Column(Boolean, default=True)
    is_demo = Column(Boolean, default=False)
    is_verified = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    profile = relationship("TravelerProfile", back_populates="user_rel", uselist=False, cascade="all, delete-orphan")
    trips = relationship("Trip", back_populates="user_rel", cascade="all, delete-orphan")
    buddy_interests = relationship("BuddyInterest", back_populates="user_rel", cascade="all, delete-orphan")

class TravelerProfile(Base):
    __tablename__ = "traveler_profiles"

    user_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
    home_city = Column(String, nullable=True)
    bio = Column(Text, nullable=True)
    interest_tags = Column(String, nullable=True) # comma-separated
    visibility = Column(String, default="destination_only") # public / destination_only / hidden
    contact_info = Column(String, nullable=True) # shown after connection accepted (e.g. email or IG)

    user_rel = relationship("User", back_populates="profile")

class Trip(Base):
    __tablename__ = "trips"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    destination = Column(String, nullable=False)
    itinerary_json = Column(Text, nullable=False)
    share_token = Column(String, unique=True, nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    user_rel = relationship("User", back_populates="trips")

class LocalPlace(Base):
    __tablename__ = "local_places"

    id = Column(Integer, primary_key=True, autoincrement=True)
    destination = Column(String, ForeignKey("destinations.name"), nullable=False, index=True)
    name = Column(String, nullable=False)
    category = Column(String, nullable=False) # cafe / market / food / viewpoint / activity / attraction / guide / stay
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    description = Column(Text, nullable=True)
    contact_info = Column(String, nullable=True)
    source = Column(String, default="osm") # osm / admin / local_user
    osm_id = Column(String, nullable=True)
    status = Column(String, default="approved") # pending / approved / rejected
    rejection_reason = Column(Text, nullable=True)
    submitted_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    crowd_hint = Column(String, nullable=True)

    destination_rel = relationship("Destination", back_populates="local_places")

class BuddyInterest(Base):
    __tablename__ = "buddy_interests"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    destination = Column(String, nullable=False, index=True)
    travel_start = Column(String, nullable=True) # YYYY-MM-DD
    travel_end = Column(String, nullable=True)   # YYYY-MM-DD
    # 5 numbers
    pref_nature = Column(Float, default=50.0)
    pref_adventure = Column(Float, default=50.0)
    pref_peacefulness = Column(Float, default=50.0)
    pref_crowd_match = Column(Float, default=50.0)
    pref_visual_atmosphere = Column(Float, default=50.0)
    interest_tags = Column(String, nullable=True)
    note = Column(Text, nullable=True)
    active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    user_rel = relationship("User", back_populates="buddy_interests")

class BuddyRequest(Base):
    __tablename__ = "buddy_requests"

    id = Column(Integer, primary_key=True, autoincrement=True)
    from_user = Column(Integer, ForeignKey("users.id"), nullable=False)
    to_user = Column(Integer, ForeignKey("users.id"), nullable=False)
    destination = Column(String, nullable=False)
    message = Column(Text, nullable=True)
    status = Column(String, default="pending") # pending / accepted / declined
    created_at = Column(DateTime, default=datetime.utcnow)

class Report(Base):
    __tablename__ = "reports"

    id = Column(Integer, primary_key=True, autoincrement=True)
    reporter_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    target_user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    reason = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class UserBlock(Base):
    __tablename__ = "user_blocks"

    id = Column(Integer, primary_key=True, autoincrement=True)
    blocker_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    blocked_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
