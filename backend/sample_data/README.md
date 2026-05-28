# backend/sample_data

Public-safe demo data for Xiamiu. This directory is committed to git and
contains no private listening history or personal Chinese-language comments.

## Contents

| File | What |
| --- | --- |
| `demo_seed.json` | Single bundle of demo data: 1 user, ~9 artists, 15 albums (10 rated + 3 recommended + 2 catalog-only fillers), 30 songs, 1 genre category, 10 genres, ~24 song comments, 2 album comments, 1 taste profile, 1 recommendation set with 3 items. |

## How it was made

Two scripts in `backend/scripts/` produced this file:

1. `extract_demo_data.py` — pulls a deterministic random sample (`seed=42`)
   from `private_data/` sources: the current `recommendation_items` table,
   `private_data/10_intermediate/structured_ratings/all_ratings_scan.json`, and the
   `album_by_id.json` catalog index. Writes the raw extract here.
2. `sanitize_demo_data.py` — applies a hand-authored Chinese→English
   translation table to artist / album / song / genre names, rewrites
   Chinese-language album comments, and substitutes a clean English-only
   taste profile. Idempotent; runs in place.

If you change the sources or want to regenerate the demo:

```bash
.venv/bin/python backend/scripts/extract_demo_data.py
.venv/bin/python backend/scripts/sanitize_demo_data.py
```

Re-running won't pick the same albums if upstream data has shifted —
treat the **committed `demo_seed.json` as authoritative**, not the scripts.

## How it's loaded

```bash
.venv/bin/python backend/scripts/seed_demo.py
```

Reads `demo_seed.json` and inserts rows into Postgres. Skips any row whose
PK already exists, so it's safe to re-run after a partial failure.
The demo user's plaintext seed password is hashed before it is written to
the database. The committed demo credential is `demo` / `demo`; it exists
only for local demo use.

The loader has no `private_data/` dependency. A fresh `git clone` only
needs Postgres + Python deps + alembic migrations + this seed to render
the full app, including the Daily AI Recommendations page.
