#!/usr/bin/env python3
"""Build embedding text documents for catalog and rated albums.

Produces:
- private_data/20_embeddings/album_embeddings/catalog_album_documents.json
- private_data/20_embeddings/album_embeddings/rated_album_documents.json

Document text format (per the Day 5 plan):
    {artistName} | {albumName} | {styles bilingual} | tags {tag ids}

No numeric magnitudes (playCount, collects, recommends) — those belong in
the rule layer per the embedding signal design report.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CATALOG_PATH = REPO_ROOT / "private_data" / "10_intermediate" / "catalog_indexes" / "album_by_id.json"
DEFAULT_RATINGS_PATH = REPO_ROOT / "private_data" / "10_intermediate" / "structured_ratings" / "all_ratings_scan.json"
DEFAULT_CATALOG_DOC_PATH = REPO_ROOT / "private_data" / "20_embeddings" / "album_embeddings" / "catalog_album_documents.json"
DEFAULT_RATED_DOC_PATH = REPO_ROOT / "private_data" / "20_embeddings" / "album_embeddings" / "rated_album_documents.json"


def format_styles(styles: list[dict[str, Any]] | None) -> str:
    if not styles:
        return ""
    names = []
    for s in styles:
        name = (s.get("styleName") or "").strip()
        if name:
            names.append(name)
    return ", ".join(names)


def format_tags(tags: list[Any] | None) -> str:
    if not tags:
        return ""
    return " ".join(str(t) for t in tags if t is not None and str(t).strip())


def build_document_text(album: dict[str, Any]) -> str:
    artist = (album.get("artistName") or "").strip()
    name = (album.get("albumName") or "").strip()
    styles = format_styles(album.get("styles"))
    tags = format_tags(album.get("tags"))

    parts = [artist, name]
    if styles:
        parts.append(styles)
    if tags:
        parts.append(f"tags {tags}")
    return " | ".join(parts)


def load_catalog(catalog_path: Path) -> dict[str, dict[str, Any]]:
    with catalog_path.open("r", encoding="utf-8") as f:
        return json.load(f)


def build_catalog_documents(catalog: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    docs: list[dict[str, Any]] = []
    for album_id, album in catalog.items():
        text = build_document_text(album)
        docs.append({
            "albumId": int(album_id) if str(album_id).isdigit() else album_id,
            "artistName": album.get("artistName"),
            "albumName": album.get("albumName"),
            "hasStyles": bool(album.get("styles")),
            "text": text,
        })
    docs.sort(key=lambda d: (d["albumId"] if isinstance(d["albumId"], int) else 0))
    return docs


def is_confident_match(row: dict[str, Any]) -> bool:
    return (
        row["albumLookup"]["status"] == "matched"
        and row["albumLookup"]["strategy"] != "album_name_fallback"
    )


def build_rated_documents(
    ratings: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    by_album_id: dict[int, dict[str, Any]] = {}
    for row in ratings:
        if not is_confident_match(row):
            continue
        matched_album = row["albumLookup"]["matchedAlbum"]
        if not matched_album:
            continue
        album_id = matched_album.get("albumId")
        if album_id is None:
            continue

        if album_id not in by_album_id:
            text = build_document_text(matched_album)
            by_album_id[album_id] = {
                "albumId": album_id,
                "artistName": matched_album.get("artistName"),
                "albumName": matched_album.get("albumName"),
                "ratedArtistName": row.get("artistName"),
                "text": text,
                "trackRatings": [],
            }

        by_album_id[album_id]["trackRatings"].append({
            "track": row.get("track"),
            "rating": row.get("rating"),
            "inferred": row.get("inferred", False),
            "trackComment": row.get("trackComment"),
        })

    rated = list(by_album_id.values())
    rated.sort(key=lambda d: d["albumId"])
    return rated


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
        f.write("\n")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--catalog-path", type=Path, default=DEFAULT_CATALOG_PATH)
    parser.add_argument("--ratings-path", type=Path, default=DEFAULT_RATINGS_PATH)
    parser.add_argument("--catalog-doc-path", type=Path, default=DEFAULT_CATALOG_DOC_PATH)
    parser.add_argument("--rated-doc-path", type=Path, default=DEFAULT_RATED_DOC_PATH)
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    catalog = load_catalog(args.catalog_path)
    with args.ratings_path.open("r", encoding="utf-8") as f:
        ratings = json.load(f)

    catalog_docs = build_catalog_documents(catalog)
    rated_docs = build_rated_documents(ratings)

    catalog_payload = {
        "generatedAt": date.today().isoformat(),
        "format": "{artistName} | {albumName} | {styles bilingual} | tags {tag ids}",
        "count": len(catalog_docs),
        "withStylesCount": sum(1 for d in catalog_docs if d["hasStyles"]),
        "documents": catalog_docs,
    }
    rated_payload = {
        "generatedAt": date.today().isoformat(),
        "format": "{artistName} | {albumName} | {styles bilingual} | tags {tag ids}",
        "count": len(rated_docs),
        "documents": rated_docs,
    }

    write_json(args.catalog_doc_path, catalog_payload)
    write_json(args.rated_doc_path, rated_payload)

    print("Album documents built.")
    print(f"  catalog: {len(catalog_docs):,} albums "
          f"({catalog_payload['withStylesCount']:,} with styles)")
    print(f"  rated:   {len(rated_docs):,} confidently matched albums")
    print(f"  output:  {args.catalog_doc_path}")
    print(f"           {args.rated_doc_path}")

    if catalog_docs:
        print("\nSample catalog document:")
        sample = next((d for d in catalog_docs if d["hasStyles"]), catalog_docs[0])
        print(f"  albumId={sample['albumId']}: {sample['text']}")
    if rated_docs:
        print("\nSample rated document:")
        sample = rated_docs[0]
        print(f"  albumId={sample['albumId']}: {sample['text']}")


if __name__ == "__main__":
    main()
