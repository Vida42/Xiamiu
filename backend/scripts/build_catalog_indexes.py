#!/usr/bin/env python3
"""Build local catalog lookup indexes for private rating matching.

This script does not write to the app database. It creates private JSON files
under private_data/10_intermediate/catalog_indexes/ so later steps can resolve markdown ratings from:

artist name + album name + track number -> albumId + track -> songId
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import unicodedata
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CATALOG_DIR = Path(
    "/Users/mugen/Project/xiamiu_resources/2025/formatted results"
)
DEFAULT_OUTPUT_DIR = REPO_ROOT / "private_data" / "10_intermediate" / "catalog_indexes"
DEFAULT_REPORT_PATH = REPO_ROOT / "local_reports" / "ai_recommendation_demo" / "catalog_index_day3.md"


def normalize_text(value: Any) -> str:
    """Normalize catalog/rating headings for repeatable exact-key matching."""
    if value is None:
        return ""
    text = unicodedata.normalize("NFKC", str(value))
    text = text.casefold()
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def read_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=2, sort_keys=True)
        file.write("\n")


def slim_style(style: dict[str, Any]) -> dict[str, Any]:
    return {
        "styleId": style.get("styleId"),
        "styleName": style.get("styleName"),
        "styleType": style.get("styleType"),
    }


def slim_album(album: dict[str, Any]) -> dict[str, Any]:
    """Carry every album-level field the downstream DB schema can consume.

    Rule: anything that maps onto an `albums` or `album_meta` column in
    postgres (see `backend/app/models.py` / migration 001) must round-trip
    through this index. Downstream loaders never need to reach back to the
    raw source files.
    """
    album_name = album.get("albumName", "")
    artist_name = album.get("artistName", "")
    return {
        "albumId": album.get("albumId"),
        "albumStringId": album.get("albumStringId"),
        "albumName": album_name,
        "normalizedAlbumName": normalize_text(album_name),
        "artistId": album.get("artistId"),
        "artistStringId": album.get("artistStringId"),
        "artistName": artist_name,
        "normalizedArtistName": normalize_text(artist_name),
        "subName": album.get("subName"),
        "language": album.get("language"),
        "albumCategory": album.get("albumCategory"),
        "songCount": album.get("songCount"),
        "cdCount": album.get("cdCount"),
        "styles": [slim_style(style) for style in album.get("styles", [])],
        "tags": album.get("tags"),
        "playCount": album.get("playCount"),
        "collects": album.get("collects"),
        "recommends": album.get("recommends"),
        "comments": album.get("comments"),
        # AlbumMeta-bound fields
        "albumLogo": album.get("albumLogo"),       # → album_meta.pic_address
        "description": album.get("description"),   # → album_meta.info
        # Albums table extras not previously carried
        "company": album.get("company"),           # → albums.record_label
        "companyId": album.get("companyId"),
        "pinyin": album.get("pinyin"),
        "type": album.get("type"),
        "categoryId": album.get("categoryId"),
    }


def slim_artist(artist: dict[str, Any]) -> dict[str, Any]:
    """Carry every artist-level field the DB schema can consume.

    Maps to `artists` and `artist_meta` tables.
    """
    artist_name = artist.get("artistName", "")
    return {
        "artistId": artist.get("artistId"),
        "artistStringId": artist.get("artistStringId"),
        "artistName": artist_name,
        "normalizedArtistName": normalize_text(artist_name),
        "alias": artist.get("alias"),
        "area": artist.get("area"),                # → artists.region
        "pinyin": artist.get("pinyin"),
        "categoryId": artist.get("categoryId"),
        "roles": artist.get("roles"),
        "styles": [slim_style(style) for style in artist.get("styles", [])],
        "playCount": artist.get("playCount"),
        "recommends": artist.get("recommends"),
        "comments": artist.get("comments"),
        "countLikes": artist.get("countLikes"),
        # ArtistMeta-bound fields
        "artistLogo": artist.get("artistLogo"),    # → artist_meta.pic_address
        "description": artist.get("description"),  # → artist_meta.info
    }


def slim_song(song: dict[str, Any]) -> dict[str, Any]:
    return {
        "songId": song.get("songId"),
        "songStringId": song.get("songStringId"),
        "songName": song.get("songName"),
        "albumId": song.get("albumId"),
        "albumStringId": song.get("albumStringId"),
        "track": song.get("track"),
        "cdSerial": song.get("cdSerial"),
        "artistId": song.get("artistId"),
        "singers": song.get("singers"),
        "length": song.get("length"),
        "playCount": song.get("playCount"),
        "favCount": song.get("favCount"),
    }


def build_artist_indexes(
    artists: list[dict[str, Any]],
) -> dict[str, dict[str, Any]]:
    """Build artist_by_id index. Mirrors album_by_id structure."""
    artist_by_id: dict[str, dict[str, Any]] = {}
    for artist in artists:
        slim = slim_artist(artist)
        artist_id = slim.get("artistId")
        if artist_id is not None:
            artist_by_id[str(artist_id)] = slim
    return artist_by_id


def build_album_indexes(
    albums: list[dict[str, Any]],
) -> tuple[dict[str, list[dict[str, Any]]], dict[str, list[dict[str, Any]]], dict[str, dict[str, Any]]]:
    albums_by_name: dict[str, list[dict[str, Any]]] = defaultdict(list)
    albums_by_artist_and_name: dict[str, list[dict[str, Any]]] = defaultdict(list)
    album_by_id: dict[str, dict[str, Any]] = {}

    for album in albums:
        slim = slim_album(album)
        album_id = slim.get("albumId")
        album_name_key = slim["normalizedAlbumName"]
        artist_name_key = slim["normalizedArtistName"]

        if album_id is not None:
            album_by_id[str(album_id)] = slim
        if album_name_key:
            albums_by_name[album_name_key].append(slim)
        if artist_name_key and album_name_key:
            albums_by_artist_and_name[f"{artist_name_key}::{album_name_key}"].append(slim)

    return dict(albums_by_name), dict(albums_by_artist_and_name), album_by_id


def build_song_indexes(
    songs: list[dict[str, Any]],
) -> tuple[
    dict[str, list[dict[str, Any]]],
    dict[str, list[dict[str, Any]]],
    dict[str, dict[str, Any]],
]:
    songs_by_album_track: dict[str, list[dict[str, Any]]] = defaultdict(list)
    songs_by_album_cd_track: dict[str, list[dict[str, Any]]] = defaultdict(list)
    song_by_id: dict[str, dict[str, Any]] = {}

    for song in songs:
        slim = slim_song(song)
        song_id = slim.get("songId")
        album_id = slim.get("albumId")
        track = slim.get("track")
        cd_serial = slim.get("cdSerial")

        if song_id is not None:
            song_by_id[str(song_id)] = slim
        if album_id is not None and track is not None:
            songs_by_album_track[f"{album_id}::{track}"].append(slim)
        if album_id is not None and cd_serial is not None and track is not None:
            songs_by_album_cd_track[f"{album_id}::{cd_serial}::{track}"].append(slim)

    return dict(songs_by_album_track), dict(songs_by_album_cd_track), song_by_id


def build_embedded_song_indexes(
    albums_with_songs_path: Path,
) -> tuple[dict[str, list[dict[str, Any]]], dict[str, list[dict[str, Any]]], int]:
    """Build richer song lookup indexes from formatted_albums.json.

    The full albums file is close to 1GB, so use jq to stream one album per line
    instead of loading the entire file into Python memory.
    """
    songs_by_album_track: dict[str, list[dict[str, Any]]] = defaultdict(list)
    songs_by_album_cd_track: dict[str, list[dict[str, Any]]] = defaultdict(list)
    embedded_song_count = 0

    jq_filter = ".[] | {albumId, albumName, artistName, songs:(.songs // [])}"
    process = subprocess.Popen(
        ["jq", "-c", jq_filter, str(albums_with_songs_path)],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
    )
    assert process.stdout is not None

    for line in process.stdout:
        if not line.strip():
            continue
        album = json.loads(line)
        parent_album_id = album.get("albumId")
        for song in album.get("songs", []):
            track = song.get("track")
            cd_serial = song.get("cdSerial")
            if parent_album_id is None or track is None:
                continue
            embedded_song_count += 1
            slim = slim_song(song)
            slim["albumId"] = parent_album_id
            slim["catalogSongAlbumId"] = song.get("albumId")
            slim["albumName"] = album.get("albumName")
            slim["artistName"] = album.get("artistName")
            songs_by_album_track[f"{parent_album_id}::{track}"].append(slim)
            if cd_serial is not None:
                songs_by_album_cd_track[f"{parent_album_id}::{cd_serial}::{track}"].append(slim)

    _, stderr = process.communicate()
    if process.returncode != 0:
        raise RuntimeError(f"jq failed while reading embedded album songs: {stderr}")

    return dict(songs_by_album_track), dict(songs_by_album_cd_track), embedded_song_count


def duplicate_count(index: dict[str, list[dict[str, Any]]]) -> int:
    return sum(1 for values in index.values() if len(values) > 1)


def duplicate_record_count(index: dict[str, list[dict[str, Any]]]) -> int:
    return sum(len(values) for values in index.values() if len(values) > 1)


def top_duplicate_examples(
    index: dict[str, list[dict[str, Any]]],
    fields: list[str],
    limit: int = 10,
) -> list[dict[str, Any]]:
    examples: list[dict[str, Any]] = []
    for key, values in index.items():
        if len(values) <= 1:
            continue
        examples.append(
            {
                "key": key,
                "count": len(values),
                "records": [
                    {field: value.get(field) for field in fields}
                    for value in values[:5]
                ],
            }
        )
        if len(examples) >= limit:
            break
    return examples


def style_counts(albums: list[dict[str, Any]]) -> list[dict[str, Any]]:
    counter: Counter[str] = Counter()
    for album in albums:
        for style in album.get("styles", []):
            style_name = style.get("styleName")
            if style_name:
                counter[str(style_name)] += 1
    return [
        {"styleName": style_name, "albumCount": count}
        for style_name, count in counter.most_common(20)
    ]


def build_summary(
    albums: list[dict[str, Any]],
    songs: list[dict[str, Any]],
    albums_by_name: dict[str, list[dict[str, Any]]],
    albums_by_artist_and_name: dict[str, list[dict[str, Any]]],
    album_by_id: dict[str, dict[str, Any]],
    songs_by_album_track: dict[str, list[dict[str, Any]]],
    songs_by_album_cd_track: dict[str, list[dict[str, Any]]],
    embedded_songs_by_album_track: dict[str, list[dict[str, Any]]],
    embedded_songs_by_album_cd_track: dict[str, list[dict[str, Any]]],
    embedded_song_count: int,
) -> dict[str, Any]:
    album_ids = set(album_by_id)
    song_album_ids = {
        str(song.get("albumId"))
        for song in songs
        if song.get("albumId") is not None
    }
    missing_album_ids = sorted(song_album_ids - album_ids)
    songs_missing_album_metadata = [
        slim_song(song)
        for song in songs
        if str(song.get("albumId")) in missing_album_ids
    ]

    return {
        "generatedAt": date.today().isoformat(),
        "sourceFiles": {
            "albums": str(DEFAULT_CATALOG_DIR / "formatted_albums_no_songs.json"),
            "songs": str(DEFAULT_CATALOG_DIR / "formatted_songs.json"),
        },
        "counts": {
            "albums": len(albums),
            "songs": len(songs),
            "albumNameKeys": len(albums_by_name),
            "artistAlbumKeys": len(albums_by_artist_and_name),
            "songAlbumTrackKeys": len(songs_by_album_track),
            "songAlbumCdTrackKeys": len(songs_by_album_cd_track),
            "embeddedSongs": embedded_song_count,
            "embeddedSongAlbumTrackKeys": len(embedded_songs_by_album_track),
            "embeddedSongAlbumCdTrackKeys": len(embedded_songs_by_album_cd_track),
        },
        "ambiguity": {
            "duplicateAlbumNameKeys": duplicate_count(albums_by_name),
            "albumRecordsInDuplicateAlbumNameKeys": duplicate_record_count(albums_by_name),
            "duplicateArtistAlbumKeys": duplicate_count(albums_by_artist_and_name),
            "albumRecordsInDuplicateArtistAlbumKeys": duplicate_record_count(
                albums_by_artist_and_name
            ),
            "ambiguousAlbumTrackKeys": duplicate_count(songs_by_album_track),
            "songRecordsInAmbiguousAlbumTrackKeys": duplicate_record_count(
                songs_by_album_track
            ),
            "ambiguousAlbumCdTrackKeys": duplicate_count(songs_by_album_cd_track),
            "songRecordsInAmbiguousAlbumCdTrackKeys": duplicate_record_count(
                songs_by_album_cd_track
            ),
            "ambiguousEmbeddedAlbumTrackKeys": duplicate_count(embedded_songs_by_album_track),
            "songRecordsInAmbiguousEmbeddedAlbumTrackKeys": duplicate_record_count(
                embedded_songs_by_album_track
            ),
            "ambiguousEmbeddedAlbumCdTrackKeys": duplicate_count(
                embedded_songs_by_album_cd_track
            ),
            "songRecordsInAmbiguousEmbeddedAlbumCdTrackKeys": duplicate_record_count(
                embedded_songs_by_album_cd_track
            ),
        },
        "missingAlbumMetadata": {
            "distinctSongAlbumIdsMissingFromAlbumCatalog": len(missing_album_ids),
            "songsMissingAlbumMetadata": len(songs_missing_album_metadata),
            "examples": songs_missing_album_metadata[:10],
        },
        "examples": {
            "duplicateAlbumNames": top_duplicate_examples(
                albums_by_name,
                ["albumId", "albumName", "artistName", "albumStringId"],
            ),
            "duplicateArtistAlbumKeys": top_duplicate_examples(
                albums_by_artist_and_name,
                ["albumId", "albumName", "artistName", "albumStringId"],
            ),
            "ambiguousAlbumTrackKeys": top_duplicate_examples(
                songs_by_album_track,
                ["songId", "songName", "albumId", "track", "cdSerial", "singers"],
            ),
            "ambiguousAlbumCdTrackKeys": top_duplicate_examples(
                songs_by_album_cd_track,
                ["songId", "songName", "albumId", "track", "cdSerial", "singers"],
            ),
        },
        "topStyles": style_counts(albums),
    }


def write_report(path: Path, summary: dict[str, Any]) -> None:
    counts = summary["counts"]
    ambiguity = summary["ambiguity"]
    missing = summary["missingAlbumMetadata"]
    examples = summary["examples"]

    lines = [
        "# Day 3 Catalog Index Report",
        "",
        f"Date: {summary['generatedAt']}",
        "",
        "## Output",
        "",
        "Generated private catalog indexes under `private_data/10_intermediate/catalog_indexes/`.",
        "",
        "These files are local matching aids. They are not app database tables and should not be committed.",
        "",
        "## Index Files",
        "",
        "- `catalog_index_summary.json`",
        "- `albums_by_artist_and_name.json`",
        "- `albums_by_normalized_name.json`",
        "- `songs_by_album_track.json`",
        "- `songs_by_album_cd_track.json`",
        "- `songs_by_album_track_embedded.json`",
        "- `songs_by_album_cd_track_embedded.json`",
        "",
        "## Counts",
        "",
        "| Metric | Count |",
        "| --- | ---: |",
        f"| Albums loaded | {counts['albums']:,} |",
        f"| Songs loaded | {counts['songs']:,} |",
        f"| Embedded songs loaded from albums | {counts['embeddedSongs']:,} |",
        f"| Album-name lookup keys | {counts['albumNameKeys']:,} |",
        f"| Artist+album lookup keys | {counts['artistAlbumKeys']:,} |",
        f"| Album+track lookup keys | {counts['songAlbumTrackKeys']:,} |",
        f"| Album+CD+track lookup keys | {counts['songAlbumCdTrackKeys']:,} |",
        f"| Embedded album+track lookup keys | {counts['embeddedSongAlbumTrackKeys']:,} |",
        f"| Embedded album+CD+track lookup keys | {counts['embeddedSongAlbumCdTrackKeys']:,} |",
        "",
        "## Ambiguity",
        "",
        "| Metric | Count |",
        "| --- | ---: |",
        f"| Duplicate album-name keys | {ambiguity['duplicateAlbumNameKeys']:,} |",
        f"| Album records in duplicate album-name keys | {ambiguity['albumRecordsInDuplicateAlbumNameKeys']:,} |",
        f"| Duplicate artist+album keys | {ambiguity['duplicateArtistAlbumKeys']:,} |",
        f"| Album records in duplicate artist+album keys | {ambiguity['albumRecordsInDuplicateArtistAlbumKeys']:,} |",
        f"| Ambiguous album+track keys | {ambiguity['ambiguousAlbumTrackKeys']:,} |",
        f"| Song records in ambiguous album+track keys | {ambiguity['songRecordsInAmbiguousAlbumTrackKeys']:,} |",
        f"| Ambiguous album+CD+track keys | {ambiguity['ambiguousAlbumCdTrackKeys']:,} |",
        f"| Song records in ambiguous album+CD+track keys | {ambiguity['songRecordsInAmbiguousAlbumCdTrackKeys']:,} |",
        f"| Ambiguous embedded album+track keys | {ambiguity['ambiguousEmbeddedAlbumTrackKeys']:,} |",
        f"| Song records in ambiguous embedded album+track keys | {ambiguity['songRecordsInAmbiguousEmbeddedAlbumTrackKeys']:,} |",
        f"| Ambiguous embedded album+CD+track keys | {ambiguity['ambiguousEmbeddedAlbumCdTrackKeys']:,} |",
        f"| Song records in ambiguous embedded album+CD+track keys | {ambiguity['songRecordsInAmbiguousEmbeddedAlbumCdTrackKeys']:,} |",
        "",
        "## Missing Album Metadata",
        "",
        "| Metric | Count |",
        "| --- | ---: |",
        f"| Distinct song albumIds missing from album catalog | {missing['distinctSongAlbumIdsMissingFromAlbumCatalog']:,} |",
        f"| Songs missing album metadata | {missing['songsMissingAlbumMetadata']:,} |",
        "",
        "## Example Duplicate Artist+Album Keys",
        "",
    ]

    duplicate_artist_examples = examples["duplicateArtistAlbumKeys"][:5]
    if duplicate_artist_examples:
        for example in duplicate_artist_examples:
            lines.append(f"- `{example['key']}`: {example['count']} records")
    else:
        lines.append("- None found.")

    lines.extend(
        [
            "",
            "## Example Ambiguous Album+Track Keys",
            "",
        ]
    )
    for example in examples["ambiguousAlbumTrackKeys"][:5]:
        records = ", ".join(
            f"{record.get('songId')}:{record.get('songName')} CD{record.get('cdSerial')}"
            for record in example["records"]
        )
        lines.append(f"- `{example['key']}`: {records}")

    lines.extend(
        [
            "",
            "## Day 3 Finding",
            "",
            "The rating matcher should use `artist name + album name` as the primary album lookup, then use embedded album song indexes for `albumId + track` song lookup.",
            "",
            "This is stronger than album-name-only matching, but it still needs ambiguity reporting because duplicate artist+album keys and multi-disc track collisions exist.",
            "",
            "Day 4 can now parse a small batch of markdown ratings and resolve each rating row against these indexes.",
            "",
        ]
    )

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def build_indexes(catalog_dir: Path, output_dir: Path, report_path: Path) -> dict[str, Any]:
    albums_path = catalog_dir / "formatted_albums_no_songs.json"
    songs_path = catalog_dir / "formatted_songs.json"
    artists_path = catalog_dir / "formatted_artists.json"
    albums_with_songs_path = catalog_dir / "formatted_albums.json"

    albums = read_json(albums_path)
    songs = read_json(songs_path)
    artists = read_json(artists_path)

    albums_by_name, albums_by_artist_and_name, album_by_id = build_album_indexes(albums)
    songs_by_album_track, songs_by_album_cd_track, song_by_id = build_song_indexes(songs)
    artist_by_id = build_artist_indexes(artists)
    (
        embedded_songs_by_album_track,
        embedded_songs_by_album_cd_track,
        embedded_song_count,
    ) = build_embedded_song_indexes(albums_with_songs_path)

    summary = build_summary(
        albums,
        songs,
        albums_by_name,
        albums_by_artist_and_name,
        album_by_id,
        songs_by_album_track,
        songs_by_album_cd_track,
        embedded_songs_by_album_track,
        embedded_songs_by_album_cd_track,
        embedded_song_count,
    )

    write_json(output_dir / "albums_by_normalized_name.json", albums_by_name)
    write_json(output_dir / "albums_by_artist_and_name.json", albums_by_artist_and_name)
    write_json(output_dir / "songs_by_album_track.json", songs_by_album_track)
    write_json(output_dir / "songs_by_album_cd_track.json", songs_by_album_cd_track)
    write_json(output_dir / "songs_by_album_track_embedded.json", embedded_songs_by_album_track)
    write_json(
        output_dir / "songs_by_album_cd_track_embedded.json",
        embedded_songs_by_album_cd_track,
    )
    write_json(output_dir / "songs_by_id.json", song_by_id)
    write_json(output_dir / "album_by_id.json", album_by_id)
    write_json(output_dir / "artist_by_id.json", artist_by_id)
    write_json(output_dir / "catalog_index_summary.json", summary)
    write_report(report_path, summary)

    return summary


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--catalog-dir",
        type=Path,
        default=DEFAULT_CATALOG_DIR,
        help="Directory containing formatted_albums_no_songs.json and formatted_songs.json.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
        help="Directory for generated private index JSON files.",
    )
    parser.add_argument(
        "--report-path",
        type=Path,
        default=DEFAULT_REPORT_PATH,
        help="Markdown report path.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    summary = build_indexes(args.catalog_dir, args.output_dir, args.report_path)
    counts = summary["counts"]
    ambiguity = summary["ambiguity"]
    missing = summary["missingAlbumMetadata"]

    print("Catalog indexes generated.")
    print(f"Albums: {counts['albums']:,}")
    print(f"Songs: {counts['songs']:,}")
    print(f"Embedded songs: {counts['embeddedSongs']:,}")
    print(f"Artist+album keys: {counts['artistAlbumKeys']:,}")
    print(f"Duplicate artist+album keys: {ambiguity['duplicateArtistAlbumKeys']:,}")
    print(f"Ambiguous album+track keys: {ambiguity['ambiguousAlbumTrackKeys']:,}")
    print(f"Songs missing album metadata: {missing['songsMissingAlbumMetadata']:,}")
    print(f"Output dir: {args.output_dir}")
    print(f"Report: {args.report_path}")


if __name__ == "__main__":
    main()
