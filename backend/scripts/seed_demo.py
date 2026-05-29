#!/usr/bin/env python3
"""Idempotent demo data loader.

Reads backend/sample_data/demo_seed.json (no private_data/ dependency) and
populates the Postgres DB so a fresh clone can run the full app.

Run order in the script matches FK dependencies. Each insert skips when the
PK already exists, so the script is safe to re-run after a partial failure
or after schema-only changes.
"""

from __future__ import annotations

import json
import sys
from datetime import date, datetime
from pathlib import Path
from typing import Optional

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "backend"))

from sqlalchemy import insert  # noqa: E402

from app.database import SessionLocal  # noqa: E402
from app import models  # noqa: E402
from app.utils import get_password_hash  # noqa: E402

SEED_FILE = REPO / "backend" / "sample_data" / "demo_seed.json"


def _parse_date(value) -> Optional[date]:
    if not value:
        return None
    if isinstance(value, date):
        return value
    if isinstance(value, str):
        # try ISO first
        try:
            return date.fromisoformat(value[:10])
        except ValueError:
            return None
    return None


def upsert_users(db, rows: list[dict]) -> int:
    n = 0
    for r in rows:
        existing = db.query(models.User).filter(models.User.id == r["id"]).first()
        if existing:
            continue
        db.add(models.User(
            id=r["id"],
            user_name=r["user_name"],
            password=get_password_hash(r["password"]),
            location=r.get("location") or "local",
            age=r.get("age") or 0,
            gender=r.get("gender") or "unspecified",
            constellation=r.get("constellation") or "unspecified",
            play_count=r.get("play_count") or 0,
            join_time=_parse_date(r.get("join_time")) or date.today(),
        ))
        n += 1
    db.flush()
    return n


def upsert_artists(db, rows: list[dict]) -> int:
    n = 0
    for r in rows:
        if db.query(models.Artist).filter(models.Artist.artist_id == r["artist_id"]).first():
            continue
        db.add(models.Artist(
            artist_id=r["artist_id"],
            name=r.get("name") or "",
            region=r.get("region") or "Unknown",
        ))
        n += 1
    db.flush()
    return n


def upsert_genres(db, rows: list[dict]) -> int:
    n = 0
    for r in rows:
        if db.query(models.Genre).filter(models.Genre.id == r["id"]).first():
            continue
        db.add(models.Genre(
            id=r["id"],
            name=r.get("name") or "",
            info=r.get("info") or "",
            info_zh=r.get("info_zh"),
            info_en=r.get("info_en"),
            category_id=r.get("category_id"),
        ))
        n += 1
    db.flush()
    return n


def upsert_genre_categories(db, rows: list[dict]) -> int:
    n = 0
    for r in rows:
        if db.query(models.GenreCategory).filter(models.GenreCategory.id == r["id"]).first():
            continue
        db.add(models.GenreCategory(
            id=r["id"],
            name=r.get("name") or "",
            info=r.get("info"),
            info_zh=r.get("info_zh"),
            info_en=r.get("info_en"),
        ))
        n += 1
    db.flush()
    return n


def upsert_albums(db, rows: list[dict]) -> int:
    n = 0
    for r in rows:
        if db.query(models.Album).filter(models.Album.album_id == r["album_id"]).first():
            continue
        db.add(models.Album(
            album_id=r["album_id"],
            name=r.get("name") or "",
            artist_id=r["artist_id"],
            album_lan=(r.get("album_lan") or "")[:10],
            release_date=_parse_date(r.get("release_date")) or date(1970, 1, 1),
            album_category=(r.get("album_category") or "")[:20],
            record_label=(r.get("record_label") or "")[:50],
        ))
        n += 1
    db.flush()
    return n


def upsert_album_meta(db, rows: list[dict]) -> int:
    n = 0
    for r in rows:
        if db.query(models.AlbumMeta).filter(models.AlbumMeta.album_id == r["album_id"]).first():
            continue
        db.add(models.AlbumMeta(
            album_id=r["album_id"],
            info=r.get("info") or "",
            pic_address=r.get("pic_address") or "",
        ))
        n += 1
    db.flush()
    return n


def upsert_songs(db, rows: list[dict]) -> int:
    n = 0
    for r in rows:
        if db.query(models.Song).filter(models.Song.song_id == r["song_id"]).first():
            continue
        db.add(models.Song(
            song_id=r["song_id"],
            name=r.get("name") or "",
            order=int(r.get("order") or 0),
            album_id=r["album_id"],
        ))
        n += 1
    db.flush()
    return n


def upsert_links(db, rows: list[dict], table, fk_cols: tuple[str, str]) -> int:
    n = 0
    a_col, b_col = fk_cols
    for r in rows:
        # SELECT to check existence
        stmt = table.select().where(
            (table.c[a_col] == r[a_col]) & (table.c[b_col] == r[b_col])
        )
        existing = db.execute(stmt).first()
        if existing:
            continue
        db.execute(insert(table).values({a_col: r[a_col], b_col: r[b_col]}))
        n += 1
    db.flush()
    return n


def upsert_taste_profile(db, row: dict) -> models.TasteProfile:
    if row is None:
        return None
    existing = db.query(models.TasteProfile).filter(models.TasteProfile.id == row["id"]).first()
    if existing:
        return existing
    tp = models.TasteProfile(
        id=row["id"],
        user_id=row["user_id"],
        profile_text=row["profile_text"],
        inputs_hash=row["inputs_hash"],
        cache_key=row["cache_key"],
        model=row["model"],
        prompt_version=row["prompt_version"],
        input_tokens=row.get("input_tokens") or 0,
        output_tokens=row.get("output_tokens") or 0,
    )
    db.add(tp)
    db.flush()
    return tp


def upsert_recommendation(db, row: dict) -> Optional[models.Recommendation]:
    if row is None:
        return None
    existing = db.query(models.Recommendation).filter(models.Recommendation.id == row["id"]).first()
    if existing:
        return existing
    rec = models.Recommendation(
        id=row["id"],
        user_id=row["user_id"],
        taste_profile_id=row["taste_profile_id"],
        generation_method=row["generation_method"],
        embedding_model=row["embedding_model"],
        judge_model=row["judge_model"],
        top_n=row["top_n"],
        notes=row.get("notes"),
    )
    db.add(rec)
    db.flush()
    return rec


def upsert_recommendation_items(db, rows: list[dict]) -> int:
    n = 0
    for r in rows:
        if db.query(models.RecommendationItem).filter(models.RecommendationItem.id == r["id"]).first():
            continue
        db.add(models.RecommendationItem(
            id=r["id"],
            recommendation_id=r["recommendation_id"],
            album_id=r["album_id"],
            artist_name=r["artist_name"],
            album_name=r["album_name"],
            rank=r["rank"],
            similarity_score=r["similarity_score"],
            fit_score=r.get("fit_score"),
            reason=r.get("reason"),
            risk=r.get("risk"),
            nearest_neighbors_json=r.get("nearest_neighbors_json"),
            styles_json=r.get("styles_json"),
            judge_cache_key=r.get("judge_cache_key"),
            play_count=r.get("play_count"),
            collects=r.get("collects"),
            recommends=r.get("recommends"),
        ))
        n += 1
    db.flush()
    return n


def upsert_album_comments(db, rows: list[dict]) -> int:
    n = 0
    for r in rows:
        existing = (
            db.query(models.AlbumComment)
            .filter(
                models.AlbumComment.album_id == r["album_id"],
                models.AlbumComment.user_id == r["user_id"],
            )
            .first()
        )
        if existing:
            continue
        db.add(models.AlbumComment(
            album_id=r["album_id"],
            comment=r["comment"][:255],
            user_id=r["user_id"],
            star=int(r.get("star") or 3),
            num_like=int(r.get("num_like") or 0),
        ))
        n += 1
    db.flush()
    return n


def upsert_song_comments(db, rows: list[dict]) -> int:
    n = 0
    for r in rows:
        existing = (
            db.query(models.SongComment)
            .filter(
                models.SongComment.song_id == r["song_id"],
                models.SongComment.user_id == r["user_id"],
            )
            .first()
        )
        if existing:
            continue
        db.add(models.SongComment(
            song_id=r["song_id"],
            comment=r["comment"][:255],
            user_id=r["user_id"],
            star=int(r.get("star") or 3),
            num_like=int(r.get("num_like") or 0),
        ))
        n += 1
    db.flush()
    return n


def main() -> int:
    if not SEED_FILE.exists():
        print(f"ERROR: seed file not found at {SEED_FILE}")
        return 1

    print(f"loading seed from {SEED_FILE}")
    with SEED_FILE.open("r", encoding="utf-8") as f:
        data = json.load(f)

    db = SessionLocal()
    try:
        counts = {}
        counts["users"] = upsert_users(db, data.get("users") or [])
        counts["artists"] = upsert_artists(db, data.get("artists") or [])
        counts["genre_categories"] = upsert_genre_categories(db, data.get("genre_categories") or [])
        counts["genres"] = upsert_genres(db, data.get("genres") or [])
        # Insert albums BEFORE songs (Song FK) and BEFORE links
        counts["albums"] = upsert_albums(db, data.get("albums") or [])
        # Many-to-many link tables (no PK except composite)
        counts["album_genre_link"] = upsert_links(
            db, data.get("album_genre_link") or [], models.album_genre_link, ("album_id", "genre_id")
        )
        counts["artist_genre_link"] = upsert_links(
            db, data.get("artist_genre_link") or [], models.artist_genre_link, ("artist_id", "genre_id")
        )
        counts["songs"] = upsert_songs(db, data.get("songs") or [])
        counts["album_meta"] = upsert_album_meta(db, data.get("album_meta") or [])

        tp = upsert_taste_profile(db, data.get("taste_profile"))
        counts["taste_profile"] = 1 if tp else 0
        rec = upsert_recommendation(db, data.get("recommendation"))
        counts["recommendation"] = 1 if rec else 0
        counts["recommendation_items"] = upsert_recommendation_items(db, data.get("recommendation_items") or [])
        counts["album_comments"] = upsert_album_comments(db, data.get("album_comments") or [])
        counts["song_comments"] = upsert_song_comments(db, data.get("song_comments") or [])

        db.commit()
    except Exception:
        db.rollback()
        raise

    print("\nseed complete (counts = new rows inserted; 0 means already present):")
    for k, v in counts.items():
        print(f"  {k}: +{v}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
