#!/usr/bin/env python3
"""Parse private rating markdown and match tracks against catalog indexes.

This script reads local markdown files under private_data/00_source/ratings/ and writes
structured private JSON for a small Day 4 validation batch. It does not write to
the app database.
"""

from __future__ import annotations

import argparse
import json
import re
import unicodedata
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_RATINGS_DIR = REPO_ROOT / "private_data" / "00_source" / "ratings"
DEFAULT_INDEX_DIR = REPO_ROOT / "private_data" / "10_intermediate" / "catalog_indexes"
DEFAULT_OUTPUT_PATH = REPO_ROOT / "private_data" / "10_intermediate" / "structured_ratings" / "sample_ratings.json"
DEFAULT_REPORT_PATH = REPO_ROOT / "local_reports" / "ai_recommendation_demo" / "ratings_match_day4.md"


@dataclass
class TrackRating:
    rating: int
    track: int
    comment: str | None = None
    rawToken: str = ""
    inferred: bool = False
    inferenceRule: str | None = None


@dataclass
class AlbumRating:
    sourceFile: str
    startLine: int
    artistName: str
    albumHeading: str
    albumName: str
    releaseText: str | None = None
    listenDateText: str | None = None
    albumComments: list[str] = field(default_factory=list)
    trackRatings: list[TrackRating] = field(default_factory=list)


def normalize_text(value: Any) -> str:
    if value is None:
        return ""
    text = unicodedata.normalize("NFKC", str(value))
    text = text.casefold()
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def clean_heading(value: str) -> str:
    text = value.strip()
    text = re.sub(r"^#+\s*", "", text)
    return text.strip()


def strip_release_hint(album_heading: str) -> str:
    """Remove common release-year hints from album headings before matching."""
    text = album_heading.strip()
    text = re.sub(r"\s*\((?:19|20)\d{2}\)\s*$", "", text)
    return text.strip()


def album_name_variants(album_name: str) -> list[str]:
    variants = [album_name.strip()]
    without_release_tail = re.sub(
        r"\s+(?:19|20)\d{2}\s+(?:re-?release|remaster(?:ed)?|edition)\s*$",
        "",
        album_name.strip(),
        flags=re.IGNORECASE,
    ).strip()
    variants.append(without_release_tail)

    without_parenthetical_year = strip_release_hint(album_name)
    variants.append(without_parenthetical_year)

    seen: set[str] = set()
    unique: list[str] = []
    for variant in variants:
        key = normalize_text(variant)
        if key and key not in seen:
            seen.add(key)
            unique.append(variant)
    return unique


def parse_release_line(line: str) -> str | None:
    stripped = line.strip()
    match = re.fullmatch(r"\*(.+?)\*", stripped)
    if match:
        return match.group(1).strip()
    return None


def looks_like_listen_date(value: str) -> bool:
    text = value.strip()
    return bool(
        re.fullmatch(r"\d{1,2}/\d{1,2}/\d{2,4}", text)
        or re.fullmatch(r"\d{1,2}/+/\d{2,4}", text)
        or re.fullmatch(r"\d{1,2}/\d{2,4}", text)
        or re.fullmatch(r"(?:19|20)\d{2}(?:[.-]\d{1,2})?(?:[.-]\d{1,2})?", text)
    )


def natural_language_inference_rule(album: AlbumRating) -> str | None:
    text = " ".join(album.albumComments)
    if "第一首" in text and "惊艳" in text and "后面" in text and "普通" in text:
        return "first_track_5_rest_3"
    return None


def parse_track_tokens(content: str, rating: int) -> list[TrackRating]:
    ratings: list[TrackRating] = []
    for match in re.finditer(r"(\d+)\s*(?:[（(]([^）)]*)[）)])?", content):
        raw = match.group(0)
        comment = match.group(2).strip() if match.group(2) else None
        ratings.append(
            TrackRating(
                rating=rating,
                track=int(match.group(1)),
                comment=comment or None,
                rawToken=raw,
            )
        )
    return ratings


def finalize_album(
    albums: list[AlbumRating],
    current_album: AlbumRating | None,
    album_limit: int,
) -> bool:
    if current_album and (
        current_album.trackRatings or natural_language_inference_rule(current_album)
    ):
        albums.append(current_album)
    return len(albums) >= album_limit


def parse_markdown_file(path: Path, album_limit: int) -> list[AlbumRating]:
    albums: list[AlbumRating] = []
    current_artist: str | None = None
    current_album: AlbumRating | None = None
    pending_rating = 5

    lines = path.read_text(encoding="utf-8").splitlines()
    for line_number, line in enumerate(lines, start=1):
        if line.startswith("## ") and not line.startswith("### "):
            if finalize_album(albums, current_album, album_limit):
                return albums
            current_artist = clean_heading(line)
            current_album = None
            pending_rating = 5
            continue

        if line.startswith("### "):
            if finalize_album(albums, current_album, album_limit):
                return albums
            album_heading = clean_heading(line)
            if current_artist:
                current_album = AlbumRating(
                    sourceFile=str(path.relative_to(REPO_ROOT)),
                    startLine=line_number,
                    artistName=current_artist,
                    albumHeading=album_heading,
                    albumName=strip_release_hint(album_heading),
                )
                pending_rating = 5
            continue

        if not current_album:
            continue

        release_text = parse_release_line(line)
        if release_text:
            current_album.releaseText = release_text
            continue

        stripped = line.strip()
        if stripped.startswith(">"):
            comment = stripped.lstrip(">").strip()
            if comment:
                if current_album.listenDateText is None and looks_like_listen_date(comment):
                    current_album.listenDateText = comment
                else:
                    current_album.albumComments.append(comment)
            continue

        bullet_match = re.match(r"^\s*-\s*(.*)$", line)
        if bullet_match and 1 <= pending_rating <= 5:
            content = bullet_match.group(1).strip()
            current_album.trackRatings.extend(parse_track_tokens(content, pending_rating))
            pending_rating -= 1

    finalize_album(albums, current_album, album_limit)
    return albums[:album_limit]


def parse_rating_markdown(ratings_dir: Path, album_limit: int) -> list[AlbumRating]:
    parsed: list[AlbumRating] = []
    for path in sorted(ratings_dir.glob("*.md")):
        if path.name.startswith("."):
            continue
        remaining = album_limit - len(parsed)
        if remaining <= 0:
            break
        parsed.extend(parse_markdown_file(path, remaining))
    return parsed[:album_limit]


def read_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def build_primary_tracks_by_album(
    embedded_songs_by_album_track: dict[str, list[dict[str, Any]]],
) -> dict[str, list[int]]:
    tracks_by_album: dict[str, set[int]] = defaultdict(set)
    for key, candidates in embedded_songs_by_album_track.items():
        album_id, _, track_text = key.partition("::")
        if not album_id or not track_text.isdigit():
            continue
        cd1_candidates = [
            candidate for candidate in candidates if candidate.get("cdSerial") == 1
        ]
        if cd1_candidates or len(candidates) == 1:
            tracks_by_album[album_id].add(int(track_text))
    return {album_id: sorted(tracks) for album_id, tracks in tracks_by_album.items()}


def inferred_track_ratings(
    album: AlbumRating,
    matched_album: dict[str, Any] | None,
    primary_tracks_by_album: dict[str, list[int]],
) -> list[TrackRating]:
    rule = natural_language_inference_rule(album)
    if album.trackRatings or not rule or not matched_album:
        return album.trackRatings

    album_id = str(matched_album.get("albumId"))
    tracks = primary_tracks_by_album.get(album_id, [])
    inferred: list[TrackRating] = []
    for track in tracks:
        inferred.append(
            TrackRating(
                rating=5 if track == 1 else 3,
                track=track,
                rawToken=f"inferred:{track}",
                inferred=True,
                inferenceRule=rule,
            )
        )
    return inferred


def album_lookup_candidates(
    album: AlbumRating,
    albums_by_artist_and_name: dict[str, list[dict[str, Any]]],
    albums_by_name: dict[str, list[dict[str, Any]]],
) -> tuple[str, list[dict[str, Any]], str]:
    artist_key = normalize_text(album.artistName)
    for variant in album_name_variants(album.albumName):
        album_key = normalize_text(variant)
        combined_key = f"{artist_key}::{album_key}"
        candidates = albums_by_artist_and_name.get(combined_key, [])
        if candidates:
            return combined_key, candidates, "artist_album"

    for variant in album_name_variants(album.albumName):
        album_key = normalize_text(variant)
        fallback_candidates = albums_by_name.get(album_key, [])
        if fallback_candidates:
            return album_key, fallback_candidates, "album_name_fallback"

    album_key = normalize_text(album.albumName)
    return album_key, [], "album_name_fallback"


def match_track(
    album_id: Any,
    track: int,
    songs_by_album_track: dict[str, list[dict[str, Any]]],
    embedded_songs_by_album_track: dict[str, list[dict[str, Any]]],
) -> tuple[str, list[dict[str, Any]], str, int]:
    key = f"{album_id}::{track}"
    embedded_candidates = embedded_songs_by_album_track.get(key, [])
    if embedded_candidates:
        cd1_candidates = [
            candidate for candidate in embedded_candidates if candidate.get("cdSerial") == 1
        ]
        if len(embedded_candidates) > 1 and len(cd1_candidates) == 1:
            return (
                key,
                cd1_candidates,
                "embedded_album_songs_cd1_default",
                len(embedded_candidates),
            )
        return key, embedded_candidates, "embedded_album_songs", len(embedded_candidates)

    formatted_candidates = songs_by_album_track.get(key, [])
    return key, formatted_candidates, "formatted_songs", len(formatted_candidates)


def build_structured_ratings(
    album_ratings: list[AlbumRating],
    index_dir: Path,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    albums_by_artist_and_name = read_json(index_dir / "albums_by_artist_and_name.json")
    albums_by_name = read_json(index_dir / "albums_by_normalized_name.json")
    songs_by_album_track = read_json(index_dir / "songs_by_album_track.json")
    embedded_songs_by_album_track = read_json(index_dir / "songs_by_album_track_embedded.json")
    primary_tracks_by_album = build_primary_tracks_by_album(embedded_songs_by_album_track)

    output: list[dict[str, Any]] = []
    album_status_counts: Counter[str] = Counter()
    track_status_counts: Counter[str] = Counter()
    inferred_track_count = 0
    album_examples: dict[str, list[dict[str, Any]]] = defaultdict(list)
    track_examples: dict[str, list[dict[str, Any]]] = defaultdict(list)

    for album in album_ratings:
        lookup_key, album_candidates, lookup_strategy = album_lookup_candidates(
            album, albums_by_artist_and_name, albums_by_name
        )

        if len(album_candidates) == 1:
            album_status = "matched"
            matched_album = album_candidates[0]
        elif len(album_candidates) > 1:
            album_status = "ambiguous"
            matched_album = None
        else:
            album_status = "unmatched"
            matched_album = None
        album_status_counts[album_status] += 1

        if album_status != "matched" and len(album_examples[album_status]) < 8:
            album_examples[album_status].append(
                {
                    "artistName": album.artistName,
                    "albumName": album.albumName,
                    "lookupKey": lookup_key,
                    "candidateCount": len(album_candidates),
                    "lookupStrategy": lookup_strategy,
                    "sourceFile": album.sourceFile,
                    "startLine": album.startLine,
                }
            )

        track_ratings = inferred_track_ratings(album, matched_album, primary_tracks_by_album)
        for track_rating in track_ratings:
            if track_rating.inferred:
                inferred_track_count += 1
            song_key = None
            song_lookup_strategy = None
            original_song_candidate_count = 0
            song_candidates: list[dict[str, Any]] = []
            matched_song: dict[str, Any] | None = None

            if matched_album:
                (
                    song_key,
                    song_candidates,
                    song_lookup_strategy,
                    original_song_candidate_count,
                ) = match_track(
                    matched_album.get("albumId"),
                    track_rating.track,
                    songs_by_album_track,
                    embedded_songs_by_album_track,
                )

            if not matched_album:
                track_status = f"album_{album_status}"
            elif len(song_candidates) == 1:
                track_status = "matched"
                matched_song = song_candidates[0]
            elif len(song_candidates) > 1:
                track_status = "ambiguous_track"
            else:
                track_status = "unmatched_track"

            track_status_counts[track_status] += 1
            if track_status != "matched" and len(track_examples[track_status]) < 8:
                track_examples[track_status].append(
                    {
                        "artistName": album.artistName,
                        "albumName": album.albumName,
                        "rating": track_rating.rating,
                        "track": track_rating.track,
                        "albumStatus": album_status,
                        "songLookupKey": song_key,
                        "songCandidateCount": len(song_candidates),
                        "sourceFile": album.sourceFile,
                        "startLine": album.startLine,
                    }
                )

            output.append(
                {
                    "sourceFile": album.sourceFile,
                    "startLine": album.startLine,
                    "artistName": album.artistName,
                    "albumHeading": album.albumHeading,
                    "albumName": album.albumName,
                    "releaseText": album.releaseText,
                    "listenDateText": album.listenDateText,
                    "albumComments": album.albumComments,
                    "rating": track_rating.rating,
                    "track": track_rating.track,
                    "trackComment": track_rating.comment,
                    "rawTrackToken": track_rating.rawToken,
                    "inferred": track_rating.inferred,
                    "inferenceRule": track_rating.inferenceRule,
                    "albumLookup": {
                        "strategy": lookup_strategy,
                        "key": lookup_key,
                        "status": album_status,
                        "candidateCount": len(album_candidates),
                        "matchedAlbum": matched_album,
                    },
                    "songLookup": {
                        "strategy": song_lookup_strategy,
                        "key": song_key,
                        "status": track_status,
                        "candidateCount": len(song_candidates),
                        "originalCandidateCount": original_song_candidate_count,
                        "matchedSong": matched_song,
                    },
                }
            )

    summary = {
        "generatedAt": date.today().isoformat(),
        "albumBatchSize": len(album_ratings),
        "trackRatingCount": len(output),
        "inferredTrackRatingCount": inferred_track_count,
        "sampleSourceFiles": sorted({album.sourceFile for album in album_ratings}),
        "sampledAlbums": [
            {
                "sourceFile": album.sourceFile,
                "startLine": album.startLine,
                "artistName": album.artistName,
                "albumName": album.albumName,
                "releaseText": album.releaseText,
                "listenDateText": album.listenDateText,
            }
            for album in album_ratings
        ],
        "albumStatusCounts": dict(album_status_counts),
        "trackStatusCounts": dict(track_status_counts),
        "albumExamples": dict(album_examples),
        "trackExamples": dict(track_examples),
    }
    return output, summary


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=2)
        file.write("\n")


def write_report(path: Path, summary: dict[str, Any], output_path: Path) -> None:
    album_counts = Counter(summary["albumStatusCounts"])
    track_counts = Counter(summary["trackStatusCounts"])
    try:
        display_output_path = output_path.relative_to(REPO_ROOT)
    except ValueError:
        display_output_path = output_path

    lines = [
        "# Day 4 Ratings Match Report",
        "",
        f"Date: {summary['generatedAt']}",
        "",
        "## Scope",
        "",
        "Parsed a small private markdown ratings batch and matched it against the Day 3 catalog indexes.",
        "",
        f"Structured output: `{display_output_path}`",
        "",
        "## Counts",
        "",
        "| Metric | Count |",
        "| --- | ---: |",
        f"| Albums parsed in batch | {summary['albumBatchSize']:,} |",
        f"| Track ratings parsed | {summary['trackRatingCount']:,} |",
        f"| Inferred track ratings | {summary.get('inferredTrackRatingCount', 0):,} |",
        f"| Albums matched | {album_counts.get('matched', 0):,} |",
        f"| Albums ambiguous | {album_counts.get('ambiguous', 0):,} |",
        f"| Albums unmatched | {album_counts.get('unmatched', 0):,} |",
        f"| Track ratings matched | {track_counts.get('matched', 0):,} |",
        f"| Track ratings with ambiguous tracks | {track_counts.get('ambiguous_track', 0):,} |",
        f"| Track ratings with unmatched tracks | {track_counts.get('unmatched_track', 0):,} |",
        "",
        "## Sample Source Files",
        "",
    ]

    for source_file in summary.get("sampleSourceFiles", []):
        lines.append(f"- `{source_file}`")

    lines.extend(
        [
            "",
            "## Sampled Albums",
            "",
            "| # | Source | Artist | Album | Release | Listen Date |",
            "| ---: | --- | --- | --- | --- | --- |",
        ]
    )

    for index, album in enumerate(summary.get("sampledAlbums", []), start=1):
        lines.append(
            f"| {index} | `{album['sourceFile']}:{album['startLine']}` | "
            f"{album['artistName']} | {album['albumName']} | "
            f"{album.get('releaseText') or ''} | {album.get('listenDateText') or ''} |"
        )

    lines.extend(
        [
            "",
        "## Album Issues",
        "",
        ]
    )

    album_examples = summary["albumExamples"]
    if not album_examples:
        lines.append("- None in this sample.")
    else:
        for status, examples in album_examples.items():
            lines.append(f"- {status}: {len(examples)} example(s)")
            for example in examples[:5]:
                lines.append(
                    f"  - `{example['artistName']}` / `{example['albumName']}` "
                    f"({example['candidateCount']} candidates, {example['sourceFile']}:{example['startLine']})"
                )

    lines.extend(["", "## Track Issues", ""])
    track_examples = summary["trackExamples"]
    if not track_examples:
        lines.append("- None in this sample.")
    else:
        for status, examples in track_examples.items():
            lines.append(f"- {status}: {len(examples)} example(s)")
            for example in examples[:5]:
                lines.append(
                    f"  - `{example['artistName']}` / `{example['albumName']}` "
                    f"track {example['track']} rating {example['rating']} "
                    f"({example['sourceFile']}:{example['startLine']})"
                )

    lines.extend(
        [
            "",
            "## Day 4 Finding",
            "",
            "The parser can convert the markdown heading, release date, listening date, album comments, and five-bullet rating format into structured track ratings.",
            "",
            "It also supports a narrow natural-language inference rule for comments like `第一首惊艳，后面流于普通`, marking those track ratings as inferred.",
            "",
        ]
    )

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ratings-dir", type=Path, default=DEFAULT_RATINGS_DIR)
    parser.add_argument("--index-dir", type=Path, default=DEFAULT_INDEX_DIR)
    parser.add_argument("--output-path", type=Path, default=DEFAULT_OUTPUT_PATH)
    parser.add_argument("--report-path", type=Path, default=DEFAULT_REPORT_PATH)
    parser.add_argument(
        "--album-limit",
        type=int,
        default=20,
        help="Number of albums with non-empty ratings to parse for the Day 4 sample.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    album_ratings = parse_rating_markdown(args.ratings_dir, args.album_limit)
    structured_ratings, summary = build_structured_ratings(album_ratings, args.index_dir)

    write_json(args.output_path, structured_ratings)
    write_report(args.report_path, summary, args.output_path)

    print("Rating markdown sample parsed and matched.")
    print(f"Albums parsed: {summary['albumBatchSize']:,}")
    print(f"Track ratings parsed: {summary['trackRatingCount']:,}")
    print(f"Album statuses: {summary['albumStatusCounts']}")
    print(f"Track statuses: {summary['trackStatusCounts']}")
    print(f"Output: {args.output_path}")
    print(f"Report: {args.report_path}")


if __name__ == "__main__":
    main()
