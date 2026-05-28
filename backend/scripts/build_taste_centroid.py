#!/usr/bin/env python3
"""Build a weighted taste centroid from rated album vectors.

Inputs:
- private_data/20_embeddings/album_embeddings/rated_album_vectors.npz
- private_data/10_intermediate/structured_ratings/all_ratings_scan.json

Output:
- private_data/20_embeddings/album_embeddings/taste_centroid.npz
- private_data/20_embeddings/album_embeddings/taste_centroid_meta.json

Weights (per Day 5 plan):
  5-star: +1.0
  4-star: +0.5
  2-star: -0.7
  1-star: -0.7

Per-album signed weight is the sum of per-track weights divided by track count,
so an album with mixed ratings ends up with a softer per-album weight than one
that's uniformly 5★. The centroid is the normalized weighted mean of rated
album vectors.
"""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from datetime import date
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_RATED_VEC_PATH = REPO_ROOT / "private_data" / "20_embeddings" / "album_embeddings" / "rated_album_vectors.npz"
DEFAULT_RATINGS_PATH = REPO_ROOT / "private_data" / "10_intermediate" / "structured_ratings" / "all_ratings_scan.json"
DEFAULT_CENTROID_PATH = REPO_ROOT / "private_data" / "20_embeddings" / "album_embeddings" / "taste_centroid.npz"
DEFAULT_META_PATH = REPO_ROOT / "private_data" / "20_embeddings" / "album_embeddings" / "taste_centroid_meta.json"

RATING_WEIGHTS = {5: 1.0, 4: 0.5, 3: 0.0, 2: -0.7, 1: -0.7}


def is_confident_match(row: dict[str, Any]) -> bool:
    return (
        row["albumLookup"]["status"] == "matched"
        and row["albumLookup"]["strategy"] != "album_name_fallback"
    )


def aggregate_album_weights(rows: list[dict[str, Any]]) -> dict[int, dict[str, Any]]:
    """Returns {albumId: {artistName, albumName, weight, trackCount, ratingHistogram}}."""
    buckets: dict[int, dict[str, Any]] = {}

    for row in rows:
        if not is_confident_match(row):
            continue
        matched_album = row["albumLookup"]["matchedAlbum"]
        if not matched_album:
            continue
        album_id = matched_album.get("albumId")
        if album_id is None:
            continue

        bucket = buckets.get(album_id)
        if bucket is None:
            bucket = {
                "artistName": matched_album.get("artistName"),
                "albumName": matched_album.get("albumName"),
                "trackCount": 0,
                "totalSignedWeight": 0.0,
                "ratingHistogram": defaultdict(int),
                "inferredCount": 0,
            }
            buckets[album_id] = bucket

        rating = row.get("rating")
        weight = RATING_WEIGHTS.get(rating, 0.0)
        bucket["trackCount"] += 1
        bucket["totalSignedWeight"] += weight
        bucket["ratingHistogram"][rating] += 1
        if row.get("inferred"):
            bucket["inferredCount"] += 1

    return buckets


def build_centroid(args: argparse.Namespace) -> None:
    import numpy as np

    with args.ratings_path.open("r", encoding="utf-8") as f:
        ratings = json.load(f)

    album_weights = aggregate_album_weights(ratings)

    data = np.load(args.rated_vec_path)
    album_ids = data["album_ids"]
    vectors = data["vectors"]

    weighted_sum = np.zeros(vectors.shape[1], dtype=np.float64)
    used_albums: list[dict[str, Any]] = []
    total_abs_weight = 0.0

    for idx, album_id in enumerate(album_ids.tolist()):
        bucket = album_weights.get(album_id)
        if bucket is None or bucket["trackCount"] == 0:
            continue
        per_album_weight = bucket["totalSignedWeight"] / bucket["trackCount"]
        if per_album_weight == 0.0:
            used_albums.append({
                "albumId": album_id,
                "artistName": bucket["artistName"],
                "albumName": bucket["albumName"],
                "perAlbumWeight": 0.0,
                "trackCount": bucket["trackCount"],
                "ratingHistogram": {str(k): v for k, v in bucket["ratingHistogram"].items()},
                "inferredCount": bucket["inferredCount"],
                "contributed": False,
            })
            continue

        weighted_sum += per_album_weight * vectors[idx]
        total_abs_weight += abs(per_album_weight)
        used_albums.append({
            "albumId": album_id,
            "artistName": bucket["artistName"],
            "albumName": bucket["albumName"],
            "perAlbumWeight": round(per_album_weight, 4),
            "trackCount": bucket["trackCount"],
            "ratingHistogram": {str(k): v for k, v in bucket["ratingHistogram"].items()},
            "inferredCount": bucket["inferredCount"],
            "contributed": True,
        })

    if total_abs_weight == 0.0:
        raise RuntimeError("No rated albums contributed to the centroid.")

    centroid = weighted_sum / total_abs_weight
    norm = float(np.linalg.norm(centroid))
    if norm > 0:
        centroid = centroid / norm

    args.centroid_path.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(args.centroid_path, centroid=centroid.astype(np.float32))

    contributing = [a for a in used_albums if a["contributed"]]
    meta = {
        "generatedAt": date.today().isoformat(),
        "ratingWeights": {str(k): v for k, v in RATING_WEIGHTS.items()},
        "vectorDim": int(centroid.shape[0]),
        "contributingAlbumCount": len(contributing),
        "neutralAlbumCount": len([a for a in used_albums if not a["contributed"]]),
        "centroidNormBeforeNormalize": round(norm, 6),
        "centroidL2NormAfter": round(float(np.linalg.norm(centroid)), 6),
        "contributingAlbums": contributing,
        "neutralAlbums": [a for a in used_albums if not a["contributed"]],
    }
    args.meta_path.parent.mkdir(parents=True, exist_ok=True)
    with args.meta_path.open("w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)
        f.write("\n")

    print("Taste centroid built.")
    print(f"  contributing rated albums: {len(contributing)}")
    print(f"  neutral (net 0 weight):    {meta['neutralAlbumCount']}")
    print(f"  vector dim:                {centroid.shape[0]}")
    print(f"  centroid: {args.centroid_path}")
    print(f"  meta:     {args.meta_path}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--rated-vec-path", type=Path, default=DEFAULT_RATED_VEC_PATH)
    parser.add_argument("--ratings-path", type=Path, default=DEFAULT_RATINGS_PATH)
    parser.add_argument("--centroid-path", type=Path, default=DEFAULT_CENTROID_PATH)
    parser.add_argument("--meta-path", type=Path, default=DEFAULT_META_PATH)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    build_centroid(args)


if __name__ == "__main__":
    main()
