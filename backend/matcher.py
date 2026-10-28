from datetime import datetime
from typing import List, Dict, Optional, Set, Any

def parse_date(date_str: Optional[str]) -> Optional[datetime]:
    if not date_str:
        return None
    try:
        return datetime.strptime(date_str, "%Y-%m-%d")
    except Exception:
        return None

def compute_vibe_similarity(user_vibes: Dict[str, float], buddy_vibes: Dict[str, float]) -> float:
    """Cosine-like or normalized Euclidean similarity in [0, 1]."""
    dims = ["nature", "adventure", "peacefulness", "crowd_match", "visual_atmosphere"]
    diff_sq = sum((user_vibes.get(d, 50.0) - buddy_vibes.get(d, 50.0))**2 for d in dims)
    # max possible distance across 5 dims is sqrt(5 * 100^2) = 223.6
    dist = diff_sq ** 0.5
    sim = max(0.0, 1.0 - (dist / 150.0))
    return sim

def compute_tag_jaccard(tags1: List[str], tags2: List[str]) -> float:
    s1 = set(t.strip().lower() for t in tags1 if t.strip())
    s2 = set(t.strip().lower() for t in tags2 if t.strip())
    if not s1 or not s2:
        return 0.5 # default neutral baseline if tags not provided
    inter = len(s1.intersection(s2))
    union = len(s1.union(s2))
    return inter / union if union > 0 else 0.0

def compute_date_overlap(start1: Optional[datetime], end1: Optional[datetime],
                         start2: Optional[datetime], end2: Optional[datetime]) -> float:
    # If no dates set, assume flexible timing
    if not start1 or not end1 or not start2 or not end2:
        return 0.7 # flexible baseline

    # Check for direct overlap
    latest_start = max(start1, start2)
    earliest_end = min(end1, end2)
    if latest_start <= earliest_end:
        overlap_days = (earliest_end - latest_start).days + 1
        return min(1.0, 0.7 + (overlap_days / 10.0) * 0.3)

    # Gap between trips
    gap_days = (start2 - end1).days if start2 > end1 else (start1 - end2).days
    if gap_days <= 14:
        return max(0.2, 0.7 - (gap_days / 14.0) * 0.5)

    return 0.1 # over 2 weeks apart

def compute_compatibility(
    user_vibes: Dict[str, float],
    buddy_vibes: Dict[str, float],
    user_tags: List[str],
    buddy_tags: List[str],
    user_start: Optional[str],
    user_end: Optional[str],
    buddy_start: Optional[str],
    buddy_end: Optional[str]
) -> Dict[str, Any]:
    vibe_sim = compute_vibe_similarity(user_vibes, buddy_vibes)
    tag_sim = compute_tag_jaccard(user_tags, buddy_tags)
    date_sim = compute_date_overlap(
        parse_date(user_start), parse_date(user_end),
        parse_date(buddy_start), parse_date(buddy_end)
    )

    total_score = (0.5 * vibe_sim) + (0.3 * tag_sim) + (0.2 * date_sim)
    compat_pct = int(round(total_score * 100))

    breakdown = [
        f"Vibe Alignment: {int(vibe_sim * 100)}% match",
        f"Interests & Tags: {int(tag_sim * 100)}% shared",
        f"Travel Timing: {int(date_sim * 100)}% sync"
    ]

    return {
        "compatibility_score": compat_pct,
        "vibe_similarity": round(vibe_sim, 2),
        "tag_overlap": round(tag_sim, 2),
        "date_overlap": round(date_sim, 2),
        "breakdown": breakdown
    }
