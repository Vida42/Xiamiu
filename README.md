# Xiamiu

A local AI music recommendation application. Builds a personal taste profile
from a user's private ratings and prose comments, retrieves candidates by
embedding similarity, has an LLM rerank and explain them, and serves the
final recommendations through a FastAPI + Next.js stack.

The recommender is grounded in *the user's own ratings and written comments*,
not crowd behavior. The LLM does real work in the pipeline (it judges and
explains candidates), not just prose generation at the end.

## Stack

| Layer | Tech |
| --- | --- |
| Frontend | Next.js 14, React 18, Chakra UI |
| Backend | FastAPI, SQLAlchemy 2.0, Alembic, Pydantic v2 |
| Database | PostgreSQL 16 |
| Embeddings | BGE-M3 (local, via sentence-transformers, Apple MPS accelerated) |
| LLM Judge | Anthropic Claude Haiku 4.5 (cached) |

## Project layout

```
Xiamiu/
├── backend/              # FastAPI app + alembic migrations + pipeline scripts
│   ├── app/              # main.py, models.py, schemas.py, crud.py, database.py
│   ├── alembic/          # migrations 001–009
│   ├── scripts/          # build_*, embed_*, ingest_*, generate_*, judge_*, rank_*, seed_demo
│   ├── sample_data/      # public-safe demo_seed.json (committed)
│   └── requirements*.txt # python deps (split: web vs ml)
├── frontend/             # Next.js app
│   ├── pages/            # incl. pages/recommendations/daily.js (Day 8)
│   ├── components/       # cards, layout, rating widgets, etc.
│   └── utils/api.js      # axios wrappers
├── private_data/         # GITIGNORED — local catalog, ratings, embeddings, cache
└── docs/                 # specs (some gitignored, see .gitignore)
```

## One-time setup

### 1. PostgreSQL

```bash
brew install postgresql@16
brew services start postgresql@16
createdb xiamiu
```

Default Homebrew install uses your macOS user as a Postgres superuser with no
password (trust auth on local socket).

```bash
whoami                  # show your macOS user name
psql xiamiu             # should open db without asking for a password
\l                      # list all db
\q                      # exit
```

If the above works, your setup works.

### 2. Environment variables

Create `.env` at project root:

```
# Database
DB_USER=          # your macOS username
DB_PASSWORD=      # blank for default local trust auth
DB_HOST=localhost
DB_PORT=
DB_NAME=xiamiu

# Optional. Used by backend/scripts/load_data.py when importing local seed
# users that intentionally omit password. Never commit real passwords.
XIAMIU_DEFAULT_USER_PASSWORD=

# Anthropic API — NOT needed for the demo path. Only required if you re-run
# the offline judge / taste-profile generators (backend/scripts/judge_*,
# generate_taste_profile).
ANTHROPIC_API_KEY=...
```

`.env` is gitignored.

### 3. Python environment

```bash
python3 -m venv .venv
.venv/bin/pip install -r backend/requirements.txt
.venv/bin/pip install -r backend/requirements-ml.txt
```

The ML deps (`sentence-transformers`, `torch`, `anthropic`) are split out
because they're large (~660MB) and only needed when re-running the
recommendation pipeline. If you only want to demo the cached recommendations
through the UI, just the web deps are enough.

### 4. Run database migrations

```bash
cd backend && ../.venv/bin/alembic upgrade head
```

Creates the full schema (artists, albums, songs, users, recommendation
tables, and the Day 9 feedback tables).

### 5. Populate the demo data

Pick **one** of the two paths.

#### 5a. Demo path (no private data, no API key) — **recommended for first run**

```bash
.venv/bin/python backend/scripts/seed_demo.py
```

Loads `backend/sample_data/demo_seed.json` into Postgres: 1 demo user, ~9
artists, 15 albums (10 rated + 3 recommended + 2 catalog-only), 30 songs,
1 genre category, 10 genres, ratings, 1 taste profile, and 3 recommendation
items with their LLM reasoning. All text is English-only, all proper nouns
transliterated, no `private_data/` reads. Idempotent (safe to re-run). The
demo user's seed password is hashed before it is stored.

#### 5b. Full pipeline path (requires `private_data/` + Anthropic key)

```bash
.venv/bin/python backend/scripts/ingest_recommendations.py
```

Reads the Day 5/6 pipeline output from `private_data/` and writes 1 taste
profile + 1 recommendation + 50 items. Use this only if you have your own
pipeline run available.

Either path creates the demo user (`user_id=1`, username `demo`). The
recommendation endpoints use this hardcoded demo user in v1; the legacy login
flow still exists for music/comment pages.

## Run the app

Two terminals:

### Backend

```bash
cd backend && ../.venv/bin/uvicorn app.main:app --reload
# serves on http://127.0.0.1:8000
```

### Frontend

```bash
cd frontend && npm run dev
# serves on http://localhost:3000
```

Then visit:
- `http://localhost:3000` — main app
- `http://localhost:3000/recommendations/daily` — the Daily AI Recommendations page
- `http://127.0.0.1:8000/docs` — auto-generated FastAPI Swagger UI

### Smoke test

```bash
curl -sS http://127.0.0.1:8000/recommendations/daily | jq '{id, top_n, items: (.items | length), first: .items[0].artist_name}'
```

With the demo seed (path 5a), should print:

```json
{
  "id": 1,
  "top_n": 3,
  "items": 3,
  "first": "Eason Chan"
}
```

## Notable runtime characteristics

- **Page load is $0** — all LLM and embedding work was paid once during the
  pipeline. The frontend only reads cached results.
- **Recommendation demo user is hardcoded** (`user_id=1`) in
  `backend/app/main.py`. The top bar defaults to this Demo User when no one
  is logged in; the legacy login flow still exists but is not the main demo
  entry point.
- **PostgreSQL is required at runtime** — the backend will not start without
  a reachable `xiamiu` database. This is the trade-off for using a real
  schema instead of file-only JSON.
- **No live AI calls in the public demo path** — by design. Recommendation
  regeneration is a separate offline pipeline (`backend/scripts/build_*` +
  `embed_*` + `generate_*` + `judge_*` + `rank_*` + `ingest_*`).

## Re-running the recommendation pipeline

Only needed if you change ratings or want to regenerate:

```bash
# 1. parse new markdown ratings (if you've edited private_data/00_source/ratings/)
.venv/bin/python backend/scripts/parse_rating_markdown.py --album-limit 500 \
  --output-path private_data/10_intermediate/structured_ratings/all_ratings_scan.json \
  --report-path local_reports/ai_recommendation_demo/ratings_match_full_scan.md

# 2. taste profile (deterministic)
.venv/bin/python backend/scripts/build_taste_profile.py

# 3. album documents
.venv/bin/python backend/scripts/build_album_documents.py

# 4. BGE-M3 embeddings (one-time per catalog change; ~10 min on Apple MPS)
.venv/bin/python backend/scripts/embed_documents.py

# 5. taste centroid
.venv/bin/python backend/scripts/build_taste_centroid.py

# 6. retrieve top 300 candidates
.venv/bin/python backend/scripts/retrieve_candidates.py

# 7. LLM-generated English taste profile (~$0.07 with Haiku 4.5)
.venv/bin/python backend/scripts/generate_taste_profile.py

# 8. LLM judge top 50 candidates (~$0.12 with Haiku 4.5)
.venv/bin/python backend/scripts/judge_candidates.py

# 9. rank top 20 by LLM fit_score
.venv/bin/python backend/scripts/rank_recommendations.py

# 10. push into Postgres for the API to serve
.venv/bin/python backend/scripts/ingest_recommendations.py
```

Caches dedupe automatically — re-running with no input change costs nothing.

## Architecture (high level)

```
private markdown ratings (private_data/00_source/ratings/)
    │
    │  parse_rating_markdown.py
    ▼
structured_ratings/all_ratings_scan.json
    │
    │  build_taste_profile.py (deterministic aggregation)
    ▼
taste_profile/taste_document.md + taste_profile.json
    │
    │  build_album_documents.py + embed_documents.py (BGE-M3)
    ▼
embeddings/catalog_album_vectors.npz  (53k × 1024-dim)
embeddings/rated_album_vectors.npz   (25 × 1024-dim)
    │
    │  build_taste_centroid.py (weighted mean)
    ▼
embeddings/taste_centroid.npz
    │
    │  retrieve_candidates.py (cosine sim + artist cap + filters)
    ▼
recommendations/embedding_candidates_day5.json (top 300)
    │
    │  generate_taste_profile.py (LLM, Claude Haiku 4.5)
    │  judge_candidates.py (LLM tool-use for top 50)
    │  rank_recommendations.py (sort by fit_score)
    ▼
cache/taste_profile.json + cache/llm_candidate_judgments/*.json
recommendations/llm_ranked_recommendations_day6.json (top 20)
    │
    │  ingest_recommendations.py
    ▼
PostgreSQL: taste_profiles + recommendations + recommendation_items
    │
    │  GET /recommendations/daily
    ▼
Next.js frontend: /recommendations/daily page
```

## Limitations (v1)

- **Catalog coverage**: built on the Xiami catalog (53k albums, frozen 2022),
  which has weak coverage of Western indie/alt-rock. ~35% match rate against
  the user's rating data. v1.1 plan is to swap to MusicBrainz.
- **Single-user recommendation demo**: recommendation endpoints use hardcoded
  `user_id=1`. The legacy auth flow still exists for music/comment pages.
- **Recommendations skew Mandarin Pop** as a structural consequence of (a)
  the user's confidently-matched ratings being Jay Chou-heavy and (b) the
  catalog itself being Chinese-skewed.
- **Album-level recommendations only** in v1 (the original plan mentioned
  songs). Easy to add a song-expansion step on top of the current album
  rankings if needed.
- **Feedback is capture-only**: quick reactions (interested / skip / save) and
  deep feedback (1–5 stars + song impression + recommendation advice) persist
  to Postgres, but the rerun pipeline that would re-judge candidates based on
  those rows is v1.2–v1.5 work and not wired up yet.

## See also

- `docs/RECOMMENDATIONS_API_AND_DB_SPEC.md` — full API + DB schema reference
- `local_reports/ai_recommendation_demo/` (gitignored) — per-day implementation reports with
  cost numbers, observations, and next-step plans
