#!/usr/bin/env python3
"""Build taste profile from matched ratings.

Reads structured rating output from parse_rating_markdown.py and produces:
- private_data/10_intermediate/taste_profile/taste_document.md  (prose, human-readable)
- private_data/10_intermediate/taste_profile/taste_profile.json (structured signals)

Confident matches only: status == 'matched' AND strategy != 'album_name_fallback'.
Lower-confidence rows (fallback matches, ambiguous, unmatched) still contribute
to unmatchedTextSignals for prose taste preservation.
"""

from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_RATINGS_PATH = REPO_ROOT / "private_data" / "10_intermediate" / "structured_ratings" / "all_ratings_scan.json"
DEFAULT_DOC_PATH = REPO_ROOT / "private_data" / "10_intermediate" / "taste_profile" / "taste_document.md"
DEFAULT_PROFILE_PATH = REPO_ROOT / "private_data" / "10_intermediate" / "taste_profile" / "taste_profile.json"

POSITIVE_WEIGHTS = {5: 1.0, 4: 0.5, 3: 0.0}
NEGATIVE_WEIGHTS = {2: -0.7, 1: -0.7}


@dataclass
class AlbumBucket:
    artistName: str
    albumName: str
    sourceFile: str
    startLine: int
    releaseText: str | None = None
    listenDateText: str | None = None
    albumComments: list[str] = field(default_factory=list)
    tracksByRating: dict[int, list[dict[str, Any]]] = field(default_factory=lambda: defaultdict(list))
    inferredTracks: list[dict[str, Any]] = field(default_factory=list)
    matchedAlbum: dict[str, Any] | None = None
    matchStrategy: str | None = None
    matchStatus: str = "unknown"
    confident: bool = False


def is_confident_match(row: dict[str, Any]) -> bool:
    return (
        row["albumLookup"]["status"] == "matched"
        and row["albumLookup"]["strategy"] != "album_name_fallback"
    )


def bucket_by_album(rows: list[dict[str, Any]]) -> dict[tuple[str, str], AlbumBucket]:
    buckets: dict[tuple[str, str], AlbumBucket] = {}

    for row in rows:
        key = (row["artistName"], row["albumName"])
        bucket = buckets.get(key)
        if bucket is None:
            bucket = AlbumBucket(
                artistName=row["artistName"],
                albumName=row["albumName"],
                sourceFile=row["sourceFile"],
                startLine=row["startLine"],
                releaseText=row.get("releaseText"),
                listenDateText=row.get("listenDateText"),
                albumComments=list(row.get("albumComments") or []),
                matchedAlbum=row["albumLookup"].get("matchedAlbum"),
                matchStrategy=row["albumLookup"].get("strategy"),
                matchStatus=row["albumLookup"].get("status", "unknown"),
                confident=is_confident_match(row),
            )
            buckets[key] = bucket

        track_entry = {
            "track": row["track"],
            "rating": row["rating"],
            "trackComment": row.get("trackComment"),
            "inferred": row.get("inferred", False),
            "songId": (row["songLookup"].get("matchedSong") or {}).get("songId"),
            "songName": (row["songLookup"].get("matchedSong") or {}).get("songName"),
            "songMatched": row["songLookup"].get("status") == "matched",
        }
        if track_entry["inferred"]:
            bucket.inferredTracks.append(track_entry)
        else:
            bucket.tracksByRating[row["rating"]].append(track_entry)

    return buckets


def style_pair(style: dict[str, Any]) -> tuple[str, str]:
    name = style.get("styleName") or ""
    if " " in name:
        parts = name.split(" ", 1)
        return parts[0].strip(), parts[1].strip()
    return name.strip(), ""


def format_styles(matched_album: dict[str, Any] | None) -> str:
    if not matched_album:
        return ""
    styles = matched_album.get("styles") or []
    if not styles:
        return ""
    return ", ".join(s.get("styleName", "") for s in styles if s.get("styleName"))


def aggregate_style_signals(
    confident_buckets: list[AlbumBucket],
) -> tuple[Counter[str], Counter[str]]:
    positive = Counter()
    negative = Counter()

    for bucket in confident_buckets:
        if not bucket.matchedAlbum:
            continue
        styles = bucket.matchedAlbum.get("styles") or []
        if not styles:
            continue

        for rating, tracks in bucket.tracksByRating.items():
            weight = POSITIVE_WEIGHTS.get(rating, 0.0)
            if rating in NEGATIVE_WEIGHTS:
                weight = NEGATIVE_WEIGHTS[rating]
            if weight == 0.0:
                continue
            for style in styles:
                name = style.get("styleName")
                if not name:
                    continue
                if weight > 0:
                    positive[name] += weight * len(tracks)
                else:
                    negative[name] += abs(weight) * len(tracks)

    return positive, negative


def aggregate_artist_signals(
    confident_buckets: list[AlbumBucket],
) -> tuple[Counter[str], Counter[str]]:
    positive = Counter()
    negative = Counter()

    for bucket in confident_buckets:
        for rating, tracks in bucket.tracksByRating.items():
            weight = POSITIVE_WEIGHTS.get(rating, 0.0)
            if rating in NEGATIVE_WEIGHTS:
                weight = NEGATIVE_WEIGHTS[rating]
            if weight == 0.0:
                continue
            if weight > 0:
                positive[bucket.artistName] += weight * len(tracks)
            else:
                negative[bucket.artistName] += abs(weight) * len(tracks)

    return positive, negative


def build_high_low_examples(
    confident_buckets: list[AlbumBucket],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    high: list[dict[str, Any]] = []
    low: list[dict[str, Any]] = []

    for bucket in confident_buckets:
        album_meta = bucket.matchedAlbum or {}
        styles = format_styles(album_meta)
        base = {
            "artistName": bucket.artistName,
            "albumName": bucket.albumName,
            "albumId": album_meta.get("albumId"),
            "releaseText": bucket.releaseText,
            "styles": styles,
        }

        for rating in (5, 4):
            for track in bucket.tracksByRating.get(rating, []):
                high.append({
                    **base,
                    "track": track["track"],
                    "rating": rating,
                    "songId": track["songId"],
                    "songName": track["songName"],
                    "trackComment": track["trackComment"],
                    "songMatched": track["songMatched"],
                })

        for rating in (2, 1):
            for track in bucket.tracksByRating.get(rating, []):
                low.append({
                    **base,
                    "track": track["track"],
                    "rating": rating,
                    "songId": track["songId"],
                    "songName": track["songName"],
                    "trackComment": track["trackComment"],
                    "songMatched": track["songMatched"],
                })

    return high, low


def build_album_patterns(confident_buckets: list[AlbumBucket]) -> list[dict[str, Any]]:
    patterns: list[dict[str, Any]] = []
    for bucket in confident_buckets:
        if not bucket.albumComments:
            continue
        album_meta = bucket.matchedAlbum or {}
        rating_distribution = {
            str(rating): len(tracks) for rating, tracks in sorted(bucket.tracksByRating.items())
        }
        patterns.append({
            "artistName": bucket.artistName,
            "albumName": bucket.albumName,
            "albumId": album_meta.get("albumId"),
            "albumComments": bucket.albumComments,
            "ratingDistribution": rating_distribution,
            "inferredTrackCount": len(bucket.inferredTracks),
            "styles": format_styles(album_meta),
        })
    return patterns


def build_unmatched_text_signals(buckets: list[AlbumBucket]) -> list[dict[str, Any]]:
    signals: list[dict[str, Any]] = []
    for bucket in buckets:
        track_comments = []
        for rating_tracks in bucket.tracksByRating.values():
            for track in rating_tracks:
                if track["trackComment"]:
                    track_comments.append({
                        "track": track["track"],
                        "rating": track["rating"],
                        "trackComment": track["trackComment"],
                    })
        if not bucket.albumComments and not track_comments:
            continue
        signals.append({
            "artistName": bucket.artistName,
            "albumName": bucket.albumName,
            "matchStatus": bucket.matchStatus,
            "matchStrategy": bucket.matchStrategy,
            "albumComments": bucket.albumComments,
            "trackComments": track_comments,
            "ratingDistribution": {
                str(rating): len(tracks)
                for rating, tracks in sorted(bucket.tracksByRating.items())
            },
        })
    return signals


def build_known_limitations(
    confident_buckets: list[AlbumBucket],
    non_confident_buckets: list[AlbumBucket],
) -> list[str]:
    limitations: list[str] = []

    fallback_albums = [
        f"{b.artistName} / {b.albumName}"
        for b in non_confident_buckets
        if b.matchStatus == "matched" and b.matchStrategy == "album_name_fallback"
    ]
    if fallback_albums:
        limitations.append(
            "album_name_fallback matches excluded (high false-positive risk): "
            + "; ".join(fallback_albums)
        )

    unmatched_count = sum(1 for b in non_confident_buckets if b.matchStatus == "unmatched")
    if unmatched_count:
        limitations.append(
            f"{unmatched_count} rated albums unmatched in catalog; prose preserved in unmatchedTextSignals."
        )

    inferred_count = sum(len(b.inferredTracks) for b in confident_buckets)
    if inferred_count:
        limitations.append(
            f"{inferred_count} track ratings are inferred (e.g. natural-language rule), marked separately."
        )

    return limitations


def build_taste_profile(rows: list[dict[str, Any]]) -> dict[str, Any]:
    buckets = bucket_by_album(rows)
    confident = [b for b in buckets.values() if b.confident]
    non_confident = [b for b in buckets.values() if not b.confident]

    pos_styles, neg_styles = aggregate_style_signals(confident)
    pos_artists, neg_artists = aggregate_artist_signals(confident)
    high_examples, low_examples = build_high_low_examples(confident)
    album_patterns = build_album_patterns(confident)
    unmatched_signals = build_unmatched_text_signals(non_confident)
    limitations = build_known_limitations(confident, non_confident)

    profile = {
        "generatedAt": date.today().isoformat(),
        "summary": {
            "confidentAlbumCount": len(confident),
            "nonConfidentAlbumCount": len(non_confident),
            "highRatedExampleCount": len(high_examples),
            "lowRatedExampleCount": len(low_examples),
            "unmatchedTextSignalCount": len(unmatched_signals),
        },
        "positiveSignals": {
            "styles": [{"name": k, "weight": round(v, 2)} for k, v in pos_styles.most_common()],
            "artists": [{"name": k, "weight": round(v, 2)} for k, v in pos_artists.most_common()],
        },
        "negativeSignals": {
            "styles": [{"name": k, "weight": round(v, 2)} for k, v in neg_styles.most_common()],
            "artists": [{"name": k, "weight": round(v, 2)} for k, v in neg_artists.most_common()],
        },
        "highRatedExamples": high_examples,
        "lowRatedExamples": low_examples,
        "albumLevelPatterns": album_patterns,
        "styleSignals": {
            "positiveTop": [{"name": k, "weight": round(v, 2)} for k, v in pos_styles.most_common(20)],
            "negativeTop": [{"name": k, "weight": round(v, 2)} for k, v in neg_styles.most_common(20)],
        },
        "unmatchedTextSignals": unmatched_signals,
        "knownLimitations": limitations,
    }
    return profile


def render_album_block(bucket: AlbumBucket) -> list[str]:
    lines: list[str] = []
    album_meta = bucket.matchedAlbum or {}
    styles = format_styles(album_meta)
    header = f"### {bucket.artistName} — {bucket.albumName}"
    lines.append(header)
    meta_bits = []
    if bucket.releaseText:
        meta_bits.append(f"release: {bucket.releaseText}")
    if bucket.listenDateText:
        meta_bits.append(f"listened: {bucket.listenDateText}")
    if styles:
        meta_bits.append(f"styles: {styles}")
    if album_meta.get("albumId"):
        meta_bits.append(f"albumId: {album_meta.get('albumId')}")
    if meta_bits:
        lines.append("_" + " · ".join(meta_bits) + "_")
    lines.append("")

    if bucket.albumComments:
        lines.append("**Album notes:**")
        for comment in bucket.albumComments:
            lines.append(f"> {comment}")
        lines.append("")

    for rating in (5, 4, 3, 2, 1):
        tracks = bucket.tracksByRating.get(rating, [])
        if not tracks:
            continue
        star_label = "★" * rating
        lines.append(f"**{star_label} ({rating}-star)**")
        for track in sorted(tracks, key=lambda t: t["track"]):
            piece = f"- track {track['track']}"
            if track["songName"]:
                piece += f" — {track['songName']}"
            if track["trackComment"]:
                piece += f"  _({track['trackComment']})_"
            lines.append(piece)
        lines.append("")

    if bucket.inferredTracks:
        lines.append("**Inferred ratings** (from natural-language album comments):")
        for track in sorted(bucket.inferredTracks, key=lambda t: t["track"]):
            piece = f"- track {track['track']} → {track['rating']}★"
            if track["songName"]:
                piece += f" ({track['songName']})"
            lines.append(piece)
        lines.append("")

    return lines


def render_taste_document(rows: list[dict[str, Any]], profile: dict[str, Any]) -> str:
    buckets = bucket_by_album(rows)
    confident = [b for b in buckets.values() if b.confident]
    non_confident = [b for b in buckets.values() if not b.confident]

    confident.sort(key=lambda b: (b.artistName, b.albumName))
    non_confident.sort(key=lambda b: (b.artistName, b.albumName))

    lines: list[str] = [
        "# Taste Document",
        "",
        f"Generated: {profile['generatedAt']}",
        "",
        "This document preserves the user's rating prose verbatim. It is the human-readable",
        "source of truth for the taste vector built in `taste_profile.json`.",
        "",
        "## Summary",
        "",
        f"- Confident matched albums: {profile['summary']['confidentAlbumCount']}",
        f"- Non-confident albums (unmatched / fallback / ambiguous): {profile['summary']['nonConfidentAlbumCount']}",
        f"- 4-5 star track examples: {profile['summary']['highRatedExampleCount']}",
        f"- 1-2 star track examples: {profile['summary']['lowRatedExampleCount']}",
        f"- Unmatched-but-useful prose entries: {profile['summary']['unmatchedTextSignalCount']}",
        "",
        "## Aggregate Style Signals (confident matches only)",
        "",
    ]

    pos_top = profile["styleSignals"]["positiveTop"]
    neg_top = profile["styleSignals"]["negativeTop"]

    if pos_top:
        lines.append("**Positive style weight (4-5★):**")
        for entry in pos_top:
            lines.append(f"- {entry['name']} — weight {entry['weight']}")
        lines.append("")
    else:
        lines.append("_No positive style signals from confident matches._")
        lines.append("")

    if neg_top:
        lines.append("**Negative style weight (1-2★):**")
        for entry in neg_top:
            lines.append(f"- {entry['name']} — weight {entry['weight']}")
        lines.append("")
    else:
        lines.append("_No negative style signals from confident matches._")
        lines.append("")

    lines.extend([
        "## Confident Matched Albums",
        "",
        "Per-album rating prose. Use these for taste-vector training.",
        "",
    ])

    if not confident:
        lines.append("_No confident matched albums in the input._")
        lines.append("")
    for bucket in confident:
        lines.extend(render_album_block(bucket))

    lines.extend([
        "## Unmatched / Non-Confident Prose Signals",
        "",
        "These albums did not yield a confident catalog match (unmatched, ambiguous, or",
        "`album_name_fallback`). Their prose is preserved as taste signal but cannot be",
        "tied to a catalog albumId. Use for LLM context, not embedding training.",
        "",
    ])
    if not non_confident:
        lines.append("_No unmatched prose signals._")
        lines.append("")
    for bucket in non_confident:
        lines.extend(render_album_block(bucket))

    lines.extend([
        "## Known Limitations",
        "",
    ])
    for limitation in profile["knownLimitations"]:
        lines.append(f"- {limitation}")
    if not profile["knownLimitations"]:
        lines.append("- None recorded.")
    lines.append("")

    return "\n".join(lines)


def write_outputs(profile: dict[str, Any], doc_text: str, profile_path: Path, doc_path: Path) -> None:
    profile_path.parent.mkdir(parents=True, exist_ok=True)
    with profile_path.open("w", encoding="utf-8") as f:
        json.dump(profile, f, ensure_ascii=False, indent=2)
        f.write("\n")
    doc_path.parent.mkdir(parents=True, exist_ok=True)
    doc_path.write_text(doc_text, encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ratings-path", type=Path, default=DEFAULT_RATINGS_PATH)
    parser.add_argument("--doc-path", type=Path, default=DEFAULT_DOC_PATH)
    parser.add_argument("--profile-path", type=Path, default=DEFAULT_PROFILE_PATH)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    with args.ratings_path.open("r", encoding="utf-8") as f:
        rows = json.load(f)

    profile = build_taste_profile(rows)
    doc_text = render_taste_document(rows, profile)
    write_outputs(profile, doc_text, args.profile_path, args.doc_path)

    print("Taste profile built.")
    print(f"  confident albums: {profile['summary']['confidentAlbumCount']}")
    print(f"  high (4-5★) examples: {profile['summary']['highRatedExampleCount']}")
    print(f"  low (1-2★) examples: {profile['summary']['lowRatedExampleCount']}")
    print(f"  unmatched prose entries: {profile['summary']['unmatchedTextSignalCount']}")
    print(f"  doc: {args.doc_path}")
    print(f"  profile: {args.profile_path}")


if __name__ == "__main__":
    main()
