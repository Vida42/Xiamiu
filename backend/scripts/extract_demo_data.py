#!/usr/bin/env python3
"""Extract a small, public-safe demo dataset from private_data into a single
committed JSON file at backend/sample_data/demo_seed.json.

Composition (per Day 10 plan):
- 3 albums from the current top-20 recommendation_items
- 10 rated albums from private_data/10_intermediate/structured_ratings/all_ratings_scan.json
  (only entries with a successfully matched albumLookup; disjoint from recs)
- 2 catalog-only fillers from private_data/10_intermediate/catalog_indexes/album_by_id.json
  (disjoint from the above 13)
- For each of the 15 albums: its artist + 2-3 representative songs +
  any styles/genres referenced
- The current taste_profile row, with profile_text passed through verbatim
  for Day 10 step D to translate by hand
- 1 recommendation set + 3 recommendation_items rows with engagement counts
  (play_count / collects / recommends) denormalized inline

Determinism: random.seed(42). Re-running can shift picks if upstream private
data changes; the committed demo_seed.json remains authoritative.

This script reads private_data/. The committed JSON is what the demo loader
uses; the loader has no private_data/ dependency.
"""

from __future__ import annotations

import json
import random
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "backend"))

from app.database import SessionLocal  # noqa: E402
from app import models  # noqa: E402

PRIVATE = REPO / "private_data"
SAMPLE_OUT = REPO / "backend" / "sample_data" / "demo_seed.json"

CATALOG_PATH = PRIVATE / "10_intermediate" / "catalog_indexes" / "album_by_id.json"
SONGS_BY_ALBUM_TRACK_PATH = PRIVATE / "10_intermediate" / "catalog_indexes" / "songs_by_album_track.json"
RATINGS_PATH = PRIVATE / "10_intermediate" / "structured_ratings" / "all_ratings_scan.json"
# Richer source for album-level fields (cover, company) — the catalog index strips these out.
FORMATTED_ALBUMS_PATH = Path("/Users/mugen/Project/xiamiu_resources/2025/formatted results/formatted_albums_no_songs.json")

DEMO_USER_ID = 1
SEED = 42
N_RECS = 3
N_RATED = 10
N_FILLERS = 2
SONGS_PER_ALBUM = 3  # how many songs per album we keep in demo


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def pick_recommendation_items(db) -> List[models.RecommendationItem]:
    rng = random.Random(SEED)
    top20 = (
        db.query(models.RecommendationItem)
        .order_by(models.RecommendationItem.rank)
        .limit(20)
        .all()
    )
    chosen = rng.sample(top20, N_RECS)
    chosen.sort(key=lambda x: x.rank)
    return chosen


def group_rated_albums(ratings: List[dict]) -> Dict[str, List[dict]]:
    """Group rating entries by matched album_id."""
    grouped: Dict[str, List[dict]] = defaultdict(list)
    for r in ratings:
        al = (r.get("albumLookup") or {})
        matched = al.get("matchedAlbum")
        if not matched:
            continue
        aid = matched.get("albumId") or matched.get("album_id")
        if not aid:
            continue
        grouped[str(aid)].append(r)
    return grouped


def pick_rated_albums(grouped: Dict[str, List[dict]], excluded: set) -> List[Tuple[str, List[dict]]]:
    rng = random.Random(SEED + 1)
    eligible = []
    for aid, rs in grouped.items():
        if aid in excluded:
            continue
        stars = [r.get("rating") for r in rs if r.get("rating")]
        if len(stars) >= 2 and (sum(stars) / len(stars)) >= 3.0:
            eligible.append((aid, rs))
    if len(eligible) < N_RATED:
        raise RuntimeError(f"only {len(eligible)} eligible rated albums; need {N_RATED}")
    picks = rng.sample(eligible, N_RATED)
    return picks


def pick_fillers(catalog: dict, excluded: set) -> List[str]:
    rng = random.Random(SEED + 2)
    candidates = [aid for aid in catalog.keys() if aid not in excluded]
    return rng.sample(candidates, N_FILLERS)


def collect_songs_for_album(songs_idx: dict, album_id: str, n: int) -> List[dict]:
    """Pull up to n songs for a given album from the album+track index."""
    matches = []
    prefix = f"{album_id}::"
    for key, entries in songs_idx.items():
        if not str(key).startswith(prefix):
            continue
        if not entries:
            continue
        # entries is a list (multi-disc collisions); pick the first
        matches.append(entries[0])
    matches.sort(key=lambda s: (s.get("cdSerial", 0), s.get("track", 0)))
    return matches[:n]


def make_album_row(catalog_entry: dict, formatted_entry: Optional[dict] = None) -> dict:
    """Build a row matching the Album SQL model.

    Uses the richer `formatted_albums_no_songs.json` entry when available
    (for `company` → record_label); falls back to the catalog index.
    """
    source = formatted_entry or catalog_entry
    return {
        "album_id": str(catalog_entry["albumId"]),
        "name": source.get("albumName") or catalog_entry.get("albumName") or "",
        "artist_id": str(catalog_entry.get("artistId") or ""),
        "album_lan": (catalog_entry.get("language") or "")[:10],
        "release_date": source.get("publishTime") or catalog_entry.get("publishTime") or None,
        "album_category": (catalog_entry.get("albumCategory") or "")[:20],
        "record_label": (source.get("company") or catalog_entry.get("recordLabel") or "")[:50],
        "listen_date": None,
    }


def make_album_meta_row(album_id: str, formatted_entry: Optional[dict]) -> Optional[dict]:
    """Build an AlbumMeta row carrying the cover URL.

    Skips when no `albumLogo` is present (the AlbumMeta model requires
    pic_address; we'd rather omit the row than write an empty string).
    """
    if not formatted_entry:
        return None
    pic = formatted_entry.get("albumLogo") or ""
    if not pic:
        return None
    return {
        "album_id": album_id,
        "info": "",  # description is Chinese prose; left blank for the demo
        "pic_address": pic,
    }


def make_artist_row(catalog_entry: dict) -> Optional[dict]:
    aid = catalog_entry.get("artistId")
    if aid is None:
        return None
    return {
        "artist_id": str(aid),
        "name": catalog_entry.get("artistName") or "",
        "region": "Unknown",  # not present in catalog_entry; will be filled if needed
    }


def make_song_row(song_entry: dict) -> dict:
    return {
        "song_id": str(song_entry["songId"]),
        "name": song_entry.get("songName") or "",
        "order": int(song_entry.get("track") or 0),
        "album_id": str(song_entry.get("albumId") or ""),
    }


def make_genre_rows(catalog_entries: List[dict]) -> Tuple[List[dict], List[dict], List[dict]]:
    """Return (genre_rows, album_genre_links, artist_genre_links).

    Genre ids are derived from styleId; names from styleName. Dedup'd.
    """
    genres: Dict[int, str] = {}
    alb_links: List[dict] = []
    art_links: List[dict] = []
    for entry in catalog_entries:
        aid = str(entry["albumId"])
        artist_id = str(entry.get("artistId") or "")
        for s in entry.get("styles") or []:
            gid = s.get("styleId")
            gname = s.get("styleName")
            if gid is None or gname is None:
                continue
            genres[gid] = gname
            alb_links.append({"album_id": aid, "genre_id": gid})
            if artist_id:
                art_links.append({"artist_id": artist_id, "genre_id": gid})
    genre_rows = [
        {"id": gid, "name": gname, "info": "", "category_id": 0}
        for gid, gname in sorted(genres.items())
    ]
    # dedup links
    seen_a = set()
    dedup_a = []
    for l in alb_links:
        key = (l["album_id"], l["genre_id"])
        if key in seen_a:
            continue
        seen_a.add(key)
        dedup_a.append(l)
    seen_r = set()
    dedup_r = []
    for l in art_links:
        key = (l["artist_id"], l["genre_id"])
        if key in seen_r:
            continue
        seen_r.add(key)
        dedup_r.append(l)
    return genre_rows, dedup_a, dedup_r


def make_album_comments(album_id: str, ratings: List[dict]) -> List[dict]:
    """Synthesize one album_comments row per rated album using its album comments."""
    comments_blob = []
    for r in ratings:
        for c in r.get("albumComments") or []:
            if c and c not in comments_blob:
                comments_blob.append(c)
    if not comments_blob:
        return []
    # average star across track ratings
    stars = [r["rating"] for r in ratings if r.get("rating")]
    avg = int(round(sum(stars) / len(stars))) if stars else 3
    text = " / ".join(comments_blob)[:255]
    return [{
        "album_id": album_id,
        "comment": text,
        "user_id": DEMO_USER_ID,
        "star": max(1, min(5, avg)),
        "num_like": 0,
    }]


def make_song_comments(ratings: List[dict]) -> List[dict]:
    """One song_comments row per rated track that matched a songId."""
    rows = []
    for r in ratings:
        sl = r.get("songLookup") or {}
        matched = sl.get("matchedSong")
        if not matched:
            continue
        sid = matched.get("songId") or matched.get("song_id")
        if not sid:
            continue
        star = r.get("rating") or 3
        comment = (r.get("trackComment") or "").strip()
        if not comment:
            comment = f"Rated {star}/5 on track {r.get('track')}"
        rows.append({
            "song_id": str(sid),
            "comment": comment[:255],
            "user_id": DEMO_USER_ID,
            "star": max(1, min(5, int(star))),
            "num_like": 0,
        })
    return rows


def serialize_taste_profile(tp: models.TasteProfile) -> dict:
    return {
        "id": tp.id,
        "user_id": tp.user_id,
        "profile_text": tp.profile_text,  # to be sanitized by hand in step D
        "inputs_hash": tp.inputs_hash,
        "cache_key": tp.cache_key,
        "model": tp.model,
        "prompt_version": tp.prompt_version,
        "input_tokens": tp.input_tokens,
        "output_tokens": tp.output_tokens,
    }


def serialize_recommendation(rec: models.Recommendation) -> dict:
    return {
        "id": rec.id,
        "user_id": rec.user_id,
        "taste_profile_id": rec.taste_profile_id,
        "generation_method": rec.generation_method,
        "embedding_model": rec.embedding_model,
        "judge_model": rec.judge_model,
        "top_n": N_RECS,  # demo only ships 3
        "notes": "Demo subset of original 50-item Day 6 run",
    }


def serialize_rec_item(item: models.RecommendationItem, rank: int, catalog_entry: dict) -> dict:
    """Round-trip a recommendation_items row with engagement denormalized from catalog."""
    return {
        "id": item.id,
        "recommendation_id": item.recommendation_id,
        "album_id": item.album_id,
        "artist_name": item.artist_name,
        "album_name": item.album_name,
        "rank": rank,
        "similarity_score": item.similarity_score,
        "fit_score": item.fit_score,
        "reason": item.reason,  # to be sanitized in step D
        "risk": item.risk,
        "nearest_neighbors_json": item.nearest_neighbors_json,
        "styles_json": item.styles_json,
        "judge_cache_key": item.judge_cache_key,
        "play_count": catalog_entry.get("playCount") if catalog_entry else None,
        "collects": catalog_entry.get("collects") if catalog_entry else None,
        "recommends": catalog_entry.get("recommends") if catalog_entry else None,
    }


def serialize_demo_user() -> dict:
    return {
        "id": DEMO_USER_ID,
        "user_name": "demo",
        "password": "demo",
        "location": "local",
        "age": 0,
        "gender": "unspecified",
        "constellation": "unspecified",
        "play_count": 0,
        "join_time": "2026-05-26",
    }


def main() -> int:
    print(f"reading sources from {PRIVATE}")
    catalog = load_json(CATALOG_PATH)
    songs_idx = load_json(SONGS_BY_ALBUM_TRACK_PATH)
    ratings = load_json(RATINGS_PATH)
    # Load the richer album list and key it by albumId for fast lookup
    print(f"reading formatted albums from {FORMATTED_ALBUMS_PATH}")
    formatted_albums = load_json(FORMATTED_ALBUMS_PATH)
    formatted_by_id = {str(a.get("albumId")): a for a in formatted_albums}

    db = SessionLocal()

    rec_items = pick_recommendation_items(db)
    rec_album_ids = {it.album_id for it in rec_items}
    print(f"picked {len(rec_items)} recs: {[(it.rank, it.artist_name, it.album_name) for it in rec_items]}")

    grouped_ratings = group_rated_albums(ratings)
    rated_picks = pick_rated_albums(grouped_ratings, excluded=rec_album_ids)
    rated_album_ids = {aid for aid, _ in rated_picks}
    print(f"picked {len(rated_picks)} rated albums")

    excluded = rec_album_ids | rated_album_ids
    filler_ids = pick_fillers(catalog, excluded=excluded)
    print(f"picked {len(filler_ids)} fillers")

    all_album_ids = sorted({*rec_album_ids, *rated_album_ids, *filler_ids})
    catalog_entries = []
    for aid in all_album_ids:
        ce = catalog.get(aid)
        if ce is None:
            print(f"  WARNING: catalog has no entry for album_id={aid}; skipping")
            continue
        catalog_entries.append(ce)

    # Build sections
    albums = []
    album_metas = []
    for ce in catalog_entries:
        aid = str(ce["albumId"])
        fe = formatted_by_id.get(aid)
        albums.append(make_album_row(ce, fe))
        meta = make_album_meta_row(aid, fe)
        if meta:
            album_metas.append(meta)
    artists_by_id: Dict[str, dict] = {}
    for ce in catalog_entries:
        art = make_artist_row(ce)
        if art:
            artists_by_id[art["artist_id"]] = art

    songs: List[dict] = []
    for ce in catalog_entries:
        for s in collect_songs_for_album(songs_idx, str(ce["albumId"]), SONGS_PER_ALBUM):
            songs.append(make_song_row(s))

    genres, alb_links, art_links = make_genre_rows(catalog_entries)

    # Only keep song_comments whose song_id is in the songs list we're seeding;
    # otherwise the FK on song_comments.song_id breaks at insert time.
    kept_song_ids = {s["song_id"] for s in songs}
    album_comments: List[dict] = []
    song_comments: List[dict] = []
    for aid, rs in rated_picks:
        album_comments.extend(make_album_comments(aid, rs))
        for sc in make_song_comments(rs):
            if sc["song_id"] in kept_song_ids:
                song_comments.append(sc)

    # taste profile + recommendation
    tp = db.query(models.TasteProfile).first()
    rec = db.query(models.Recommendation).first()
    taste_profile = serialize_taste_profile(tp) if tp else None
    recommendation = serialize_recommendation(rec) if rec else None
    rec_items_out = []
    for idx, it in enumerate(rec_items, start=1):
        ce = catalog.get(it.album_id)
        rec_items_out.append(serialize_rec_item(it, rank=idx, catalog_entry=ce))

    payload = {
        "users": [serialize_demo_user()],
        "artists": list(artists_by_id.values()),
        "albums": albums,
        "album_meta": album_metas,
        "songs": songs,
        "genre_categories": [
            {
                "id": 0,
                "name": "Demo Styles",
                "info": "",
                "info_zh": None,
                "info_en": "Public-safe demo category for sampled styles.",
            }
        ],
        "genres": genres,
        "album_genre_link": alb_links,
        "artist_genre_link": art_links,
        "album_comments": album_comments,
        "song_comments": song_comments,
        "taste_profile": taste_profile,
        "recommendation": recommendation,
        "recommendation_items": rec_items_out,
    }

    SAMPLE_OUT.parent.mkdir(parents=True, exist_ok=True)
    with SAMPLE_OUT.open("w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
    print(f"\nwrote {SAMPLE_OUT}")
    print(f"  artists: {len(payload['artists'])}")
    print(f"  albums: {len(payload['albums'])}")
    print(f"  songs: {len(payload['songs'])}")
    print(f"  genres: {len(payload['genres'])}")
    print(f"  album_comments: {len(payload['album_comments'])}")
    print(f"  song_comments: {len(payload['song_comments'])}")
    print(f"  recommendation_items: {len(payload['recommendation_items'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
