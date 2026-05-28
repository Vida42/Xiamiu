# Recommendations API + DB Spec (Day 7)

This document is the authoritative spec for the recommendation feature's
backend API and database schema. Use it to build the frontend in parallel.

## TL;DR

- 3 GET endpoints (read-only for v1)
- No auth for v1 (uses hardcoded demo `user_id=1`)
- 3 new DB tables (already migrated; see `backend/alembic/versions/005_add_recommendation_tables.py`)
- Base URL during development: `http://localhost:8000`

## File pointers for the frontend AI

| What | Where |
| --- | --- |
| SQLAlchemy models (new) | `backend/app/models.py` — classes `TasteProfile`, `Recommendation`, `RecommendationItem` (at end of file) |
| Alembic migration | `backend/alembic/versions/005_add_recommendation_tables.py` |
| Existing API style to follow | `backend/app/main.py`, `backend/app/schemas.py`, `backend/app/crud.py` |
| Existing UI components to reuse | `frontend/components/Cards/`, `frontend/components/PlaylistSection.js`, `frontend/components/Layout/` |
| Existing axios pattern | grep `frontend/` for `import axios` to see how existing pages call backend |
| **Sample recommendation data** (mock against this shape) | `private_data/30_recommendations/ai_outputs/llm_ranked_recommendations_day6.json` |
| Sample taste profile structure | `private_data/40_model_cache/taste_profile.json` |
| Sample LLM judgment file | `private_data/40_model_cache/llm_candidate_judgments/*.json` (50 files) |
| Day 5 pipeline report | `local_reports/ai_recommendation_demo/taste_embedding_day5.md` |
| Day 6 LLM judge report | `local_reports/ai_recommendation_demo/llm_judge_day6.md` |

---

## API: 3 GET Endpoints

### 1. `GET /recommendations/daily`

**Purpose**: Get the latest (most recently generated) recommendation set for the
current user. This is the **main endpoint** the Daily Recommendations page
consumes.

**Auth**: None (v1). Returns latest for hardcoded `user_id=1`.

**Path params**: none.
**Query params**: none.

**Success response (200)**:

```json
{
  "id": 1,
  "user_id": 1,
  "generated_at": "2026-05-26T20:00:00Z",
  "generation_method": "embedding_centroid+llm_judge_v1",
  "embedding_model": "BAAI/bge-m3",
  "judge_model": "claude-haiku-4-5-20251001",
  "top_n": 20,
  "taste_profile_id": 1,
  "taste_profile_text": "This listener gravitates toward Mandarin pop and Chinese singer-songwriter work...",
  "items": [
    {
      "id": 1,
      "rank": 1,
      "album_id": "2102746427",
      "artist_name": "陈奕迅",
      "album_name": "反正是我",
      "styles": [
        "国语流行 Mandarin Pop",
        "华语唱作人 Chinese Singer-Songwriter"
      ],
      "similarity_score": 0.837,
      "fit_score": 7.2,
      "reason": "陈奕迅's 反正是我 aligns with the listener's core Mandarin pop and Chinese singer-songwriter foundation...",
      "risk": null,
      "nearest_neighbors": [
        {
          "album_id": "32627",
          "artist_name": "周杰伦",
          "album_name": "我很忙",
          "similarity": 0.9021,
          "rating_histogram": {"5": 4, "4": 4, "3": 2}
        },
        {
          "album_id": "...",
          "artist_name": "...",
          "album_name": "...",
          "similarity": 0.89,
          "rating_histogram": {"5": 3, "4": 6, "3": 5, "2": 3, "1": 1}
        }
      ],
      "play_count": 9591413,
      "collects": 4606,
      "recommends": 559
    }
    // ... 19 more items, total 20
  ]
}
```

**Notes about the response**:
- `items` array contains exactly **20 items** (LLM-ranked top 20), ordered by `rank` ASC (rank 1 = best fit).
- DB actually stores 50 items per set; API only returns the LLM-curated top 20. Don't add a "show more" feature in v1.
- `nearest_neighbors` is **already deserialized** to a list of objects (the DB stores JSON text; API does the parse). Frontend should NOT call `JSON.parse` on this field.
- `styles` is similarly deserialized.
- `risk` is `null` for some items when the LLM judged no significant risk. UI should handle `null` gracefully (e.g., hide the risk row).
- `play_count` / `collects` / `recommends` come from a join with the catalog (not stored on the recommendation_items table itself).
- `taste_profile_text` is the long-form English profile (~200 words). The frontend can show it collapsed by default.

**Error response (404)**:

```json
{ "detail": "No recommendations generated yet for this user." }
```

Frontend should show an empty state ("Rate some songs to get your first recommendations").

---

### 2. `GET /recommendations`

**Purpose**: List all recommendation sets the user has ever received, newest
first. **Metadata only** — no items embedded. Used for a "recommendation
history" view if you build one.

**Auth**: None (v1).
**Path params**: none.
**Query params**: none.

**Success response (200)**:

```json
{
  "count": 3,
  "items": [
    {
      "id": 3,
      "generated_at": "2026-05-28T20:00:00Z",
      "top_n": 20,
      "generation_method": "embedding_centroid+llm_judge_v1",
      "embedding_model": "BAAI/bge-m3",
      "judge_model": "claude-haiku-4-5-20251001",
      "notes": null
    },
    {
      "id": 2,
      "generated_at": "2026-05-27T20:00:00Z",
      "top_n": 20,
      "generation_method": "embedding_centroid+llm_judge_v1",
      "embedding_model": "BAAI/bge-m3",
      "judge_model": "claude-haiku-4-5-20251001",
      "notes": "regenerated after user feedback"
    },
    {
      "id": 1,
      "generated_at": "2026-05-26T20:00:00Z",
      "top_n": 20,
      "generation_method": "embedding_centroid+llm_judge_v1",
      "embedding_model": "BAAI/bge-m3",
      "judge_model": "claude-haiku-4-5-20251001",
      "notes": null
    }
  ]
}
```

**Note**: For v1 (only one pipeline run), this returns a single-element list.
The endpoint exists to be future-ready; it becomes useful once feedback
triggers reruns.

---

### 3. `GET /recommendations/{rec_id}`

**Purpose**: Get a specific historical recommendation set by its id. Same
response shape as `/recommendations/daily`, just for an older set instead of
the latest one.

**Auth**: None (v1).
**Path params**: `rec_id` (integer)
**Query params**: none.

**Success response (200)**: Identical structure to `/recommendations/daily`.

**Error response (404)**: When `rec_id` doesn't exist:

```json
{ "detail": "Recommendation set not found." }
```

---

## CORS

Frontend (`http://localhost:3000`) needs to call backend (`http://localhost:8000`).
Backend must add `CORSMiddleware`:

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

Without this, browser blocks the request before it reaches the backend.

---

## DB Schema (3 new tables)

Already defined in `backend/app/models.py` and migrated in
`backend/alembic/versions/005_add_recommendation_tables.py`. Summary here:

### `taste_profiles`

LLM-written English taste profile. Append-only audit log — regenerating creates a new row.

| Column | Type | Notes |
| --- | --- | --- |
| `id` | int PK | |
| `user_id` | int FK → users.id, indexed | |
| `profile_text` | text | ~200-word English prose |
| `inputs_hash` | varchar(32), indexed | sha256 prefix of input ratings + document |
| `cache_key` | varchar(32), indexed | matches the on-disk cache file |
| `model` | varchar(64) | e.g. `claude-haiku-4-5-20251001` |
| `prompt_version` | varchar(16) | e.g. `v1` |
| `input_tokens` | int | for cost tracking |
| `output_tokens` | int | for cost tracking |
| `created`, `modified` | datetime | from BaseModel mixin |

### `recommendations`

One row per pipeline run. Many-to-one with users; many-to-one with taste_profiles; one-to-many with recommendation_items.

| Column | Type | Notes |
| --- | --- | --- |
| `id` | int PK | |
| `user_id` | int FK → users.id, indexed | |
| `taste_profile_id` | int FK → taste_profiles.id, indexed | |
| `generation_method` | varchar(32) | e.g. `embedding_centroid+llm_judge_v1` |
| `embedding_model` | varchar(64) | e.g. `BAAI/bge-m3` |
| `judge_model` | varchar(64) | e.g. `claude-haiku-4-5-20251001` |
| `top_n` | int | default display count (20) |
| `notes` | text, nullable | freeform note about this run |
| `created`, `modified` | datetime | |

### `recommendation_items`

Individual recommended albums with LLM judgment. 50 rows per `recommendations` set (only top 20 served via API).

| Column | Type | Notes |
| --- | --- | --- |
| `id` | int PK | |
| `recommendation_id` | int FK → recommendations.id, indexed | |
| `album_id` | varchar(20), indexed | Xiami albumId; **NOT** a FK (catalog not fully ingested) |
| `artist_name` | varchar(255) | denormalized for fast display |
| `album_name` | varchar(255) | denormalized |
| `rank` | int | 1-50, where 1 = highest LLM fit_score |
| `similarity_score` | float | cosine sim to taste centroid (Day 5) |
| `fit_score` | float, nullable | LLM-assigned 0-10 (Day 6) |
| `reason` | text, nullable | LLM one-sentence reason |
| `risk` | text, nullable | LLM one-sentence risk (can be null when no risk) |
| `nearest_neighbors_json` | text, nullable | JSON-encoded list of 3 nearest rated neighbors |
| `styles_json` | text, nullable | JSON-encoded list of style names |
| `judge_cache_key` | varchar(32), nullable, indexed | audit pointer to on-disk LLM cache |
| `created`, `modified` | datetime | |

---

## Frontend Implementation Notes

### Recommended page layout

```
┌─────────────────────────────────────────────────────────┐
│  Daily AI Recommendations                                │
│  Generated 2026-05-26 · curated by Claude Haiku 4.5      │
├─────────────────────────────────────────────────────────┤
│  [▼ Why these? Click to see your taste profile]          │
├─────────────────────────────────────────────────────────┤
│  #1  陈奕迅 — 反正是我                       fit 7.2 ★   │
│      Mandarin Pop · Chinese Singer-Songwriter            │
│      "陈奕迅's 反正是我 aligns with the listener's..."   │
│      Risk: (none noted)                                  │
│      [▼ Similar to your: 我很忙 (周杰伦)]                │
├─────────────────────────────────────────────────────────┤
│  #2  薛之谦 — 绅士                           fit 7.2 ★   │
│      ...                                                 │
└─────────────────────────────────────────────────────────┘
```

### State handling

- **Loading**: spinner while fetching `/recommendations/daily`
- **404 (no recs yet)**: empty state with friendly message
- **Network error**: retry button
- **Each item**: show reason inline; risk only if non-null; nearest_neighbors as a collapsible "evidence" panel

### Sanitization for demo

Some `reason` / `risk` / `nearest_neighbors.rating_histogram` contain Chinese
prose comments from private ratings (e.g., `"难听且长..."`, `"口水"`). For a
public demo recording, either:
- Translate to English in the LLM prompt before generation
- Or visually hide nearest_neighbors prose if it contains private comments

This is a v1 sanitization concern — not blocking for backend, but worth flagging when wiring up display.

---

## What's NOT in this spec (deferred)

- POST endpoints for feedback (Day 9)
- Taste profile detail endpoint (`GET /taste-profiles/*` — won't be built)
- Auth (Day 11+ if at all)
- Pagination (not needed — 20 items max per response)

---

## Quick verification once backend is ready

```bash
# from project root
curl http://localhost:8000/recommendations/daily | jq

# should return JSON matching the shape above
```

If frontend gets a 200 with the right shape from this curl, frontend can start
mocking against it immediately, even before the DB is populated (use a static
JSON file at `frontend/public/sample_recommendation.json` for development).
