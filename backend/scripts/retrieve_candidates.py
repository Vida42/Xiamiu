#!/usr/bin/env python3
"""Retrieve top candidate albums by cosine similarity to taste centroid.

Inputs:
- private_data/20_embeddings/album_embeddings/catalog_album_vectors.npz
- private_data/20_embeddings/album_embeddings/rated_album_vectors.npz
- private_data/20_embeddings/album_embeddings/taste_centroid.npz
- private_data/10_intermediate/catalog_indexes/album_by_id.json
- private_data/10_intermediate/structured_ratings/all_ratings_scan.json

Output:
- private_data/30_recommendations/ai_outputs/embedding_candidates_day5.json

Filters (per Day 5 plan — no positive scoring rules):
- Exclude already-rated albums (any match, not just confident)
- Exclude known false-positive matches (album_name_fallback IDs)
- Per-artist cap in top-K (max 2 per artist among top 50)

For each candidate, attach the top-3 nearest *rated* neighbors as evidence
for Day 6's LLM judge.
"""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from datetime import date
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CATALOG_VEC_PATH = REPO_ROOT / "private_data" / "20_embeddings" / "album_embeddings" / "catalog_album_vectors.npz"
DEFAULT_RATED_VEC_PATH = REPO_ROOT / "private_data" / "20_embeddings" / "album_embeddings" / "rated_album_vectors.npz"
DEFAULT_CENTROID_PATH = REPO_ROOT / "private_data" / "20_embeddings" / "album_embeddings" / "taste_centroid.npz"
DEFAULT_CATALOG_INDEX_PATH = REPO_ROOT / "private_data" / "10_intermediate" / "catalog_indexes" / "album_by_id.json"
DEFAULT_RATINGS_PATH = REPO_ROOT / "private_data" / "10_intermediate" / "structured_ratings" / "all_ratings_scan.json"
DEFAULT_OUTPUT_PATH = REPO_ROOT / "private_data" / "30_recommendations" / "ai_outputs" / "embedding_candidates_day5.json"

DEFAULT_TOP_K = 300
DEFAULT_TOP_DISPLAY = 50
ARTIST_CAP_IN_TOP_DISPLAY = 2


def collect_exclusion_ids(rows: list[dict[str, Any]]) -> tuple[set[int], set[int]]:
    """Return (excluded_album_ids, false_positive_album_ids).

    Anything with status=matched is excluded so we don't recommend back what
    the user has already rated. Fallback matches are recorded separately so
    the limitation is reported on the output.
    """
    excluded: set[int] = set()
    false_positives: set[int] = set()
    for row in rows:
        ma = row["albumLookup"].get("matchedAlbum") or {}
        album_id = ma.get("albumId")
        if album_id is None:
            continue
        if row["albumLookup"]["status"] != "matched":
            continue
        if row["albumLookup"]["strategy"] == "album_name_fallback":
            false_positives.add(album_id)
            excluded.add(album_id)
        else:
            excluded.add(album_id)
    return excluded, false_positives


def lookup_rated_album_index(rated_ids: Any) -> dict[int, int]:
    return {int(album_id): idx for idx, album_id in enumerate(rated_ids.tolist())}


def find_nearest_rated_neighbors(
    candidate_vector: Any,
    rated_ids: Any,
    rated_vectors: Any,
    rated_album_meta: dict[int, dict[str, Any]],
    top_n: int = 3,
) -> list[dict[str, Any]]:
    import numpy as np
    sims = rated_vectors @ candidate_vector
    order = np.argsort(-sims)[:top_n]
    neighbors = []
    for idx in order.tolist():
        album_id = int(rated_ids[idx])
        meta = rated_album_meta.get(album_id, {})
        neighbors.append({
            "albumId": album_id,
            "artistName": meta.get("artistName"),
            "albumName": meta.get("albumName"),
            "similarity": round(float(sims[idx]), 4),
            "ratingHistogram": meta.get("ratingHistogram", {}),
        })
    return neighbors


def build_rated_album_meta(rows: list[dict[str, Any]]) -> dict[int, dict[str, Any]]:
    meta: dict[int, dict[str, Any]] = {}
    for row in rows:
        if row["albumLookup"]["status"] != "matched":
            continue
        if row["albumLookup"]["strategy"] == "album_name_fallback":
            continue
        ma = row["albumLookup"]["matchedAlbum"] or {}
        album_id = ma.get("albumId")
        if album_id is None:
            continue
        entry = meta.setdefault(album_id, {
            "artistName": ma.get("artistName"),
            "albumName": ma.get("albumName"),
            "ratingHistogram": defaultdict(int),
        })
        entry["ratingHistogram"][str(row.get("rating"))] += 1

    for v in meta.values():
        v["ratingHistogram"] = dict(v["ratingHistogram"])
    return meta


def retrieve(args: argparse.Namespace) -> None:
    import numpy as np

    with args.catalog_index_path.open("r", encoding="utf-8") as f:
        catalog_index = json.load(f)
    with args.ratings_path.open("r", encoding="utf-8") as f:
        ratings = json.load(f)

    catalog_data = np.load(args.catalog_vec_path)
    catalog_ids = catalog_data["album_ids"]
    catalog_vectors = catalog_data["vectors"]

    rated_data = np.load(args.rated_vec_path)
    rated_ids = rated_data["album_ids"]
    rated_vectors = rated_data["vectors"]

    centroid = np.load(args.centroid_path)["centroid"].astype(catalog_vectors.dtype)

    excluded, false_positives = collect_exclusion_ids(ratings)
    rated_album_meta = build_rated_album_meta(ratings)

    sims = catalog_vectors @ centroid

    order = np.argsort(-sims)

    candidates: list[dict[str, Any]] = []
    seen_artists: dict[str, int] = defaultdict(int)
    capped_skips = 0

    for idx in order.tolist():
        album_id = int(catalog_ids[idx])
        if album_id in excluded:
            continue
        catalog_entry = catalog_index.get(str(album_id))
        if catalog_entry is None:
            continue
        artist_name = catalog_entry.get("artistName") or "<unknown>"

        in_display_zone = len(candidates) < args.top_display
        if in_display_zone and seen_artists[artist_name] >= ARTIST_CAP_IN_TOP_DISPLAY:
            capped_skips += 1
            continue

        neighbors = find_nearest_rated_neighbors(
            catalog_vectors[idx], rated_ids, rated_vectors, rated_album_meta
        )

        candidate = {
            "candidateId": f"album:{album_id}",
            "candidateType": "album",
            "albumId": album_id,
            "artistName": artist_name,
            "albumName": catalog_entry.get("albumName"),
            "styles": [s.get("styleName") for s in (catalog_entry.get("styles") or []) if s.get("styleName")],
            "playCount": catalog_entry.get("playCount"),
            "collects": catalog_entry.get("collects"),
            "recommends": catalog_entry.get("recommends"),
            "similarityScore": round(float(sims[idx]), 4),
            "nearestRatedNeighbors": neighbors,
            "filtersApplied": [],
            "limitations": [],
        }
        if album_id in false_positives:
            candidate["filtersApplied"].append("known_false_positive_blocked_separately")
        seen_artists[artist_name] += 1
        candidates.append(candidate)

        if len(candidates) >= args.top_k:
            break

    limitations = []
    if false_positives:
        limitations.append(
            f"{len(false_positives)} known album_name_fallback false-positive ids excluded from recommendation pool"
        )
    if capped_skips:
        limitations.append(
            f"{capped_skips} same-artist duplicates skipped under artist cap ({ARTIST_CAP_IN_TOP_DISPLAY} per artist in top {args.top_display})"
        )

    output = {
        "generatedAt": date.today().isoformat(),
        "topK": args.top_k,
        "topDisplay": args.top_display,
        "artistCapInTopDisplay": ARTIST_CAP_IN_TOP_DISPLAY,
        "centroidL2Norm": round(float(np.linalg.norm(centroid)), 6),
        "candidateCount": len(candidates),
        "limitations": limitations,
        "candidates": candidates,
    }

    args.output_path.parent.mkdir(parents=True, exist_ok=True)
    with args.output_path.open("w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
        f.write("\n")

    print("Embedding candidates retrieved.")
    print(f"  candidates returned: {len(candidates)}")
    print(f"  top score: {candidates[0]['similarityScore'] if candidates else 'n/a'}")
    print(f"  output: {args.output_path}")

    if candidates:
        print("\nTop 10 preview:")
        for i, c in enumerate(candidates[:10], 1):
            styles = ", ".join(c["styles"][:3])
            print(f"  {i:2d}. [{c['similarityScore']:.4f}] {c['artistName']} / {c['albumName']}"
                  + (f"  ({styles})" if styles else ""))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--catalog-vec-path", type=Path, default=DEFAULT_CATALOG_VEC_PATH)
    parser.add_argument("--rated-vec-path", type=Path, default=DEFAULT_RATED_VEC_PATH)
    parser.add_argument("--centroid-path", type=Path, default=DEFAULT_CENTROID_PATH)
    parser.add_argument("--catalog-index-path", type=Path, default=DEFAULT_CATALOG_INDEX_PATH)
    parser.add_argument("--ratings-path", type=Path, default=DEFAULT_RATINGS_PATH)
    parser.add_argument("--output-path", type=Path, default=DEFAULT_OUTPUT_PATH)
    parser.add_argument("--top-k", type=int, default=DEFAULT_TOP_K)
    parser.add_argument("--top-display", type=int, default=DEFAULT_TOP_DISPLAY)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    retrieve(args)


if __name__ == "__main__":
    main()
