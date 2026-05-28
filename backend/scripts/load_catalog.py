import json
from pathlib import Path
from dotenv import load_dotenv
from sqlalchemy import text
from sqlalchemy.dialects.postgresql import insert

script_path = Path(__file__)
backend_dir = script_path.parent.parent
repo_dir = backend_dir.parent
catalog_dir = repo_dir / "private_data" / "00_source" / "catalog"

load_dotenv(dotenv_path=repo_dir / ".env")
load_dotenv(dotenv_path=backend_dir / ".env")

from ..app.database import SessionLocal
from ..app.models import (
    GenreCategory, Genre, Artist, Album, Song,
    ArtistMeta, AlbumMeta, SongMeta,
    artist_genre_link, album_genre_link, song_artist_link,
)

# (table, json filename, chunk size) in FK-dependency order.
# Chunk sizes balance Postgres' 65535 bind-param limit (chunk x columns)
# against per-statement byte size for wide text rows (meta tables).
LOAD_SPEC = [
    (GenreCategory.__table__, "genre_categories.json", 500),
    (Genre.__table__, "genres.json", 500),
    (Artist.__table__, "artists.json", 5000),
    (Album.__table__, "albums.json", 2000),
    (Song.__table__, "songs.json", 10000),
    (ArtistMeta.__table__, "artist_meta.json", 2000),
    (AlbumMeta.__table__, "album_meta.json", 2000),
    (SongMeta.__table__, "song_meta.json", 5000),
    (artist_genre_link, "artist_genre_link.json", 10000),
    (album_genre_link, "album_genre_link.json", 10000),
    (song_artist_link, "song_artist_link.json", 10000),
]

# Integer-id tables loaded with explicit ids: their sequences must be
# bumped past max(id) so future auto-generated inserts don't collide.
SEQUENCE_TABLES = [
    ("genre_categories", "id"),
    ("genres", "id"),
    ("artist_genre_link", "id"),
    ("album_genre_link", "id"),
    ("song_artist_link", "id"),
]


def load_json(filename):
    with open(catalog_dir / filename, "r", encoding="utf-8") as f:
        return json.load(f)


def strip_nul(rows):
    """Postgres text columns reject NUL (0x00) bytes; scrub them in place."""
    cleaned = 0
    for r in rows:
        for k, v in r.items():
            if isinstance(v, str) and "\x00" in v:
                r[k] = v.replace("\x00", "")
                cleaned += 1
    return cleaned


def load_table(session, table, filename, chunk_size, keep=None):
    rows = load_json(filename)
    if keep is not None:
        kept = [r for r in rows if keep(r)]
        skipped = len(rows) - len(kept)
        rows = kept
    else:
        skipped = 0
    nul = strip_nul(rows)
    for i in range(0, len(rows), chunk_size):
        chunk = rows[i:i + chunk_size]
        session.execute(insert(table).values(chunk).on_conflict_do_nothing())
        session.commit()
    notes = []
    if skipped:
        notes.append(f"{skipped} skipped")
    if nul:
        notes.append(f"{nul} NUL-cleaned")
    note = f"  ({', '.join(notes)})" if notes else ""
    print(f"  {table.name}: {len(rows)} rows{note}")


def reset_sequences(session, only=None):
    for table, col in SEQUENCE_TABLES:
        if only and table not in only:
            continue
        session.execute(text(
            f"SELECT setval(pg_get_serial_sequence('{table}', '{col}'), "
            f"COALESCE((SELECT max({col}) FROM {table}), 1)) "
            f"WHERE pg_get_serial_sequence('{table}', '{col}') IS NOT NULL"
        ))
    session.commit()
    print("  sequences reset")


def load_catalog(only=None):
    spec = LOAD_SPEC
    if only:
        only = set(only)
        known = {e[0].name for e in LOAD_SPEC}
        unknown = only - known
        if unknown:
            raise SystemExit(
                f"Unknown table(s): {', '.join(sorted(unknown))}\n"
                f"Valid: {', '.join(sorted(known))}"
            )
        spec = [e for e in LOAD_SPEC if e[0].name in only]

    song_ids = None

    session = SessionLocal()
    try:
        print("Loading catalog...")
        for table, filename, chunk_size in spec:
            if table is SongMeta.__table__:
                # Drop lyrics whose song is absent from the catalog (orphans).
                if song_ids is None:
                    song_ids = {s["song_id"] for s in load_json("songs.json")}
                load_table(session, table, filename, chunk_size,
                           keep=lambda r: r["song_id"] in song_ids)
            else:
                load_table(session, table, filename, chunk_size)

        print("Resetting sequences...")
        reset_sequences(session, only)
        print("Done.")
    except Exception as e:
        session.rollback()
        print(f"Error: {e}")
        raise
    finally:
        session.close()


if __name__ == "__main__":
    import sys
    load_catalog(sys.argv[1:] or None)
