#!/usr/bin/env python3
"""Ingest Day 5 + Day 6 pipeline outputs into Postgres.

Reads:
- private_data/40_model_cache/taste_profile.json
- private_data/30_recommendations/ai_outputs/embedding_candidates_day5.json (for similarity / neighbors / styles)
- private_data/40_model_cache/llm_candidate_judgments/*.json (50 judgment files)

Writes:
- 1 row into taste_profiles (get_or_create by cache_key)
- 1 row into recommendations (always new)
- 50 rows into recommendation_items (ranked by fit_score DESC, similarity DESC)

Ensures demo user (user_id=1) exists.

Idempotent on taste_profiles.cache_key; recommendations are append-only by design.
"""

from __future__ import annotations

import json
import sys
from datetime import date
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "backend"))

from app.database import SessionLocal  # noqa: E402
from app.models import (  # noqa: E402
    User,
    TasteProfile,
    Recommendation,
    RecommendationItem,
)
from app.utils import get_password_hash  # noqa: E402


TASTE_PROFILE_CACHE = REPO_ROOT / "private_data" / "40_model_cache" / "taste_profile.json"
CANDIDATES_FILE = REPO_ROOT / "private_data" / "30_recommendations" / "ai_outputs" / "embedding_candidates_day5.json"
JUDGMENTS_DIR = REPO_ROOT / "private_data" / "40_model_cache" / "llm_candidate_judgments"
CATALOG_INDEX_FILE = REPO_ROOT / "private_data" / "10_intermediate" / "catalog_indexes" / "album_by_id.json"

DEMO_USER_ID = 1
DEMO_USER_DEFAULTS = {
    "user_name": "demo",
    "password": "demo",
    "location": "local",
    "age": 0,
    "gender": "unspecified",
    "constellation": "unspecified",
    "play_count": 0,
    "join_time": date.today(),
}


def ensure_demo_user(db) -> User:
    user = db.query(User).filter(User.id == DEMO_USER_ID).first()
    if user is not None:
        print(f"  demo user exists: id={user.id}, name={user.user_name}")
        return user

    user = User(
        id=DEMO_USER_ID,
        **{
            **DEMO_USER_DEFAULTS,
            "password": get_password_hash(DEMO_USER_DEFAULTS["password"]),
        },
    )
    db.add(user)
    db.flush()
    print(f"  created demo user: id={user.id}, name={user.user_name}")
    return user


def get_or_create_taste_profile(db, payload: dict, user_id: int) -> TasteProfile:
    cache_key = payload["cache_key"]
    existing = db.query(TasteProfile).filter(TasteProfile.cache_key == cache_key).first()
    if existing is not None:
        print(f"  taste_profile exists: id={existing.id}, cache_key={cache_key}")
        return existing

    profile = TasteProfile(
        user_id=user_id,
        profile_text=payload["profile_text"],
        inputs_hash=payload["inputs_hash"],
        cache_key=cache_key,
        model=payload["model"],
        prompt_version=payload["prompt_version"],
        input_tokens=payload["usage"]["input_tokens"],
        output_tokens=payload["usage"]["output_tokens"],
    )
    db.add(profile)
    db.flush()
    print(f"  created taste_profile: id={profile.id}, cache_key={cache_key}")
    return profile


def build_candidate_lookup(candidates_payload: dict) -> dict[str, dict]:
    return {c["candidateId"]: c for c in candidates_payload["candidates"]}


def load_judgments(judgments_dir: Path) -> list[dict]:
    judgments = []
    for path in sorted(judgments_dir.glob("*.json")):
        with path.open("r", encoding="utf-8") as f:
            judgments.append(json.load(f))
    return judgments


def assemble_items(judgments: list[dict], candidate_lookup: dict[str, dict]) -> list[dict]:
    items = []
    for j in judgments:
        cid = j["candidate_id"]
        cand = candidate_lookup.get(cid)
        if cand is None:
            # judgment exists but candidate missing from current Day 5 output — skip
            continue
        items.append({
            "judgment": j,
            "candidate": cand,
            "fit_score": j.get("fit_score") if isinstance(j.get("fit_score"), (int, float)) else None,
            "similarity_score": cand.get("similarityScore", 0.0),
        })

    # Sort by fit_score DESC (nulls last), then similarity DESC as tiebreaker
    items.sort(
        key=lambda x: (
            -(x["fit_score"] if x["fit_score"] is not None else -1.0),
            -x["similarity_score"],
        )
    )
    for rank, item in enumerate(items, start=1):
        item["rank"] = rank
    return items


def load_catalog_index() -> dict:
    if not CATALOG_INDEX_FILE.exists():
        print(f"  warning: catalog index not found at {CATALOG_INDEX_FILE}; engagement fields will be null")
        return {}
    with CATALOG_INDEX_FILE.open("r", encoding="utf-8") as f:
        return json.load(f)


def insert_recommendation(
    db,
    user_id: int,
    taste_profile: TasteProfile,
    items: list[dict],
    candidates_payload: dict,
    top_n: int = 20,
) -> Recommendation:
    judge_models = {item["judgment"].get("model") for item in items if item["judgment"].get("model")}
    judge_model = next(iter(judge_models)) if judge_models else "unknown"

    catalog = load_catalog_index()

    rec = Recommendation(
        user_id=user_id,
        taste_profile_id=taste_profile.id,
        generation_method="embedding_centroid+llm_judge_v1",
        embedding_model="BAAI/bge-m3",
        judge_model=judge_model,
        top_n=top_n,
        notes=f"Ingested from Day 5/6 pipeline output ({len(items)} judged items)",
    )
    db.add(rec)
    db.flush()
    print(f"  created recommendation: id={rec.id}, judge_model={judge_model}, items={len(items)}")

    for item in items:
        judgment = item["judgment"]
        cand = item["candidate"]
        album_id_str = str(cand.get("albumId"))
        cat_entry = catalog.get(album_id_str) or {}
        ri = RecommendationItem(
            recommendation_id=rec.id,
            album_id=album_id_str,
            artist_name=cand.get("artistName") or "",
            album_name=cand.get("albumName") or "",
            rank=item["rank"],
            similarity_score=item["similarity_score"],
            fit_score=item["fit_score"],
            reason=judgment.get("reason"),
            risk=judgment.get("risk"),
            nearest_neighbors_json=json.dumps(cand.get("nearestRatedNeighbors") or [], ensure_ascii=False),
            styles_json=json.dumps(cand.get("styles") or [], ensure_ascii=False),
            judge_cache_key=judgment.get("cache_key"),
            play_count=cat_entry.get("playCount"),
            collects=cat_entry.get("collects"),
            recommends=cat_entry.get("recommends"),
        )
        db.add(ri)
    db.flush()
    print(f"  inserted {len(items)} recommendation_items")
    return rec


def main() -> None:
    print(f"Loading taste profile from {TASTE_PROFILE_CACHE}")
    with TASTE_PROFILE_CACHE.open("r", encoding="utf-8") as f:
        taste_payload = json.load(f)

    print(f"Loading candidates from {CANDIDATES_FILE}")
    with CANDIDATES_FILE.open("r", encoding="utf-8") as f:
        candidates_payload = json.load(f)
    candidate_lookup = build_candidate_lookup(candidates_payload)
    print(f"  candidate lookup built: {len(candidate_lookup)} entries")

    print(f"Loading judgments from {JUDGMENTS_DIR}")
    judgments = load_judgments(JUDGMENTS_DIR)
    print(f"  loaded {len(judgments)} judgments")

    items = assemble_items(judgments, candidate_lookup)
    print(f"  assembled {len(items)} ranked items")

    db = SessionLocal()
    try:
        print("Ensuring demo user...")
        user = ensure_demo_user(db)

        print("Get-or-create taste profile...")
        taste = get_or_create_taste_profile(db, taste_payload, user.id)

        print("Inserting recommendation + items...")
        rec = insert_recommendation(db, user.id, taste, items, candidates_payload)

        db.commit()
        print(f"\nIngest complete. Recommendation id={rec.id} now in DB.")
        print(f"  user: {user.user_name} (id={user.id})")
        print(f"  taste_profile id: {taste.id}")
        print(f"  recommendation_items: {len(items)} rows")
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
