#!/usr/bin/env python3
"""Judge Day 5 candidates with cached LLM calls.

For each of the top N Day 5 candidates, prompt Claude with:
- cached English taste profile
- candidate metadata (artist, album, styles, engagement)
- nearest rated neighbors (artist, album, similarity, rating histogram)

Expect a JSON response: {fit_score: 0-10, reason: <1 sentence>, risk: <1 sentence>}.

Cache key per candidate:
    sha256(taste_profile_cache_key | candidate_id | model | prompt_version)
Cache hit short-circuits the API call.

Writes:
- private_data/40_model_cache/llm_candidate_judgments/<cache_key>.json (one per candidate)
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from anthropic import Anthropic


REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CANDIDATES_PATH = REPO_ROOT / "private_data" / "30_recommendations" / "ai_outputs" / "embedding_candidates_day5.json"
DEFAULT_TASTE_PROFILE_CACHE_PATH = REPO_ROOT / "private_data" / "40_model_cache" / "taste_profile.json"
DEFAULT_CACHE_DIR = REPO_ROOT / "private_data" / "40_model_cache" / "llm_candidate_judgments"

DEFAULT_MODEL = "claude-haiku-4-5"
PROMPT_VERSION = "v1"
MAX_OUTPUT_TOKENS = 300
DEFAULT_TOP_N = 50
DEFAULT_RPS_DELAY = 0.0


SYSTEM_PROMPT = """\
You are scoring a candidate music album against a listener's known taste
profile. Use the `record_judgment` tool to return your judgment.

Scoring rubric:
- 9-10: strong alignment with multiple positive taste signals; minimal risk.
- 7-8: solid match on at least one core positive; acceptable risk.
- 5-6: tangential — partial overlap or borderline genre fit.
- 3-4: superficial similarity but conflicts with explicit dislikes.
- 0-2: explicitly contradicts the listener's expressed taste.

Be specific. Cite an artist, album, comment, or style when justifying. Avoid
generic filler like "diverse taste" or "appreciates good music".
"""

JUDGMENT_TOOL = {
    "name": "record_judgment",
    "description": "Record the fit judgment for a candidate album against the listener's taste profile.",
    "input_schema": {
        "type": "object",
        "properties": {
            "fit_score": {
                "type": "number",
                "minimum": 0.0,
                "maximum": 10.0,
                "description": "Fit score from 0.0 to 10.0 per the rubric.",
            },
            "reason": {
                "type": "string",
                "description": "One sentence grounded in the taste profile and the candidate's evidence.",
            },
            "risk": {
                "type": "string",
                "description": "One sentence about why this recommendation might fail for this listener.",
            },
        },
        "required": ["fit_score", "reason", "risk"],
    },
}


def hash_cache_key(taste_cache_key: str, candidate_id: str, model: str, prompt_version: str) -> str:
    h = hashlib.sha256()
    h.update(f"{taste_cache_key}|{candidate_id}|{model}|{prompt_version}".encode("utf-8"))
    return h.hexdigest()[:16]


def build_user_prompt(
    taste_profile_text: str,
    candidate: dict[str, Any],
) -> str:
    styles = ", ".join(candidate.get("styles") or []) or "(none recorded)"
    engagement_bits = []
    for field, label in (("playCount", "playCount"), ("collects", "collects"), ("recommends", "recommends")):
        v = candidate.get(field)
        if v is not None:
            engagement_bits.append(f"{label}={v:,}")
    engagement = " · ".join(engagement_bits) if engagement_bits else "(no engagement data)"

    neighbor_lines = []
    for n in candidate.get("nearestRatedNeighbors") or []:
        hist = n.get("ratingHistogram") or {}
        hist_str = " ".join(f"{star}★×{count}" for star, count in sorted(hist.items(), reverse=True))
        neighbor_lines.append(
            f"  - similarity {n['similarity']:.4f}: {n['artistName']} / {n['albumName']}  ({hist_str or 'no ratings'})"
        )
    neighbors = "\n".join(neighbor_lines) if neighbor_lines else "  (none)"

    return f"""\
# Listener Taste Profile
{taste_profile_text}

# Candidate Album
- artist: {candidate.get('artistName')}
- album: {candidate.get('albumName')}
- styles: {styles}
- engagement: {engagement}
- embedding similarity to taste centroid: {candidate.get('similarityScore'):.4f}

# Nearest Rated Neighbors (from the listener's own ratings — main grounding evidence)
{neighbors}

Return JSON only.
"""


def parse_json_response(text: str) -> dict[str, Any]:
    """Extract the first JSON object from the response."""
    # Strip code fences if present
    cleaned = text.strip()
    if cleaned.startswith("```"):
        cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned)
        cleaned = re.sub(r"\s*```\s*$", "", cleaned)
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", cleaned, re.DOTALL)
        if match:
            return json.loads(match.group(0))
        raise


def judge_candidate(
    client: Anthropic,
    model: str,
    taste_profile_text: str,
    candidate: dict[str, Any],
) -> tuple[dict[str, Any], dict[str, int]]:
    user_prompt = build_user_prompt(taste_profile_text, candidate)
    resp = client.messages.create(
        model=model,
        max_tokens=MAX_OUTPUT_TOKENS,
        system=SYSTEM_PROMPT,
        tools=[JUDGMENT_TOOL],
        tool_choice={"type": "tool", "name": "record_judgment"},
        messages=[{"role": "user", "content": user_prompt}],
    )
    parsed = None
    for block in resp.content:
        if getattr(block, "type", None) == "tool_use" and block.name == "record_judgment":
            parsed = dict(block.input)
            break
    if parsed is None:
        raise RuntimeError("No record_judgment tool_use block returned.")
    usage = {
        "input_tokens": resp.usage.input_tokens,
        "output_tokens": resp.usage.output_tokens,
    }
    return parsed, usage


def run(args: argparse.Namespace) -> None:
    load_dotenv(REPO_ROOT / ".env")

    candidates_payload = json.loads(args.candidates_path.read_text(encoding="utf-8"))
    candidates = candidates_payload.get("candidates") or []
    candidates = candidates[: args.top_n]

    taste_payload = json.loads(args.taste_profile_cache_path.read_text(encoding="utf-8"))
    taste_profile_text = taste_payload["profile_text"]
    taste_cache_key = taste_payload["cache_key"]

    args.cache_dir.mkdir(parents=True, exist_ok=True)

    client = Anthropic()

    cache_hits = 0
    api_calls = 0
    parse_failures = 0
    total_in = 0
    total_out = 0

    print(f"Judging {len(candidates)} candidates with model={args.model}")
    print(f"Taste profile cache_key: {taste_cache_key}")
    print()

    for idx, candidate in enumerate(candidates, start=1):
        candidate_id = candidate["candidateId"]
        cache_key = hash_cache_key(taste_cache_key, candidate_id, args.model, PROMPT_VERSION)
        cache_path = args.cache_dir / f"{cache_key}.json"

        prefix = f"[{idx:3d}/{len(candidates)}]"
        label = f"{candidate.get('artistName')} / {candidate.get('albumName')}"

        if cache_path.exists() and not args.force:
            cache_hits += 1
            print(f"{prefix} cache hit  | {label}")
            continue

        try:
            parsed, usage = judge_candidate(client, args.model, taste_profile_text, candidate)
        except Exception as e:
            parse_failures += 1
            print(f"{prefix} ERROR     | {label}: {e}", file=sys.stderr)
            continue

        api_calls += 1
        total_in += usage["input_tokens"]
        total_out += usage["output_tokens"]

        payload = {
            "cache_key": cache_key,
            "taste_profile_cache_key": taste_cache_key,
            "candidate_id": candidate_id,
            "albumId": candidate.get("albumId"),
            "artistName": candidate.get("artistName"),
            "albumName": candidate.get("albumName"),
            "model": args.model,
            "prompt_version": PROMPT_VERSION,
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "fit_score": parsed.get("fit_score"),
            "reason": parsed.get("reason"),
            "risk": parsed.get("risk"),
            "usage": usage,
            "raw_response": parsed,
        }
        cache_path.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        score = parsed.get("fit_score")
        score_str = f"{score:>4.1f}" if isinstance(score, (int, float)) else "??.??"
        print(f"{prefix} score {score_str} | {label}  ({usage['input_tokens']}→{usage['output_tokens']} tok)")

        if args.rps_delay > 0:
            time.sleep(args.rps_delay)

    print()
    print("Summary:")
    print(f"  cache hits:     {cache_hits}")
    print(f"  api calls:      {api_calls}")
    print(f"  parse failures: {parse_failures}")
    print(f"  total tokens:   in={total_in:,}, out={total_out:,}")

    if api_calls and args.model.startswith("claude-haiku"):
        cost = total_in / 1_000_000 * 1.0 + total_out / 1_000_000 * 5.0
        print(f"  est cost:       ${cost:.4f} (Haiku 4.5 pricing: $1/M in + $5/M out)")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--candidates-path", type=Path, default=DEFAULT_CANDIDATES_PATH)
    parser.add_argument("--taste-profile-cache-path", type=Path, default=DEFAULT_TASTE_PROFILE_CACHE_PATH)
    parser.add_argument("--cache-dir", type=Path, default=DEFAULT_CACHE_DIR)
    parser.add_argument("--model", type=str, default=DEFAULT_MODEL)
    parser.add_argument("--top-n", type=int, default=DEFAULT_TOP_N)
    parser.add_argument("--rps-delay", type=float, default=DEFAULT_RPS_DELAY,
                        help="Seconds to sleep between API calls (0 = none).")
    parser.add_argument("--force", action="store_true", help="Bypass cache and re-judge.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    run(args)


if __name__ == "__main__":
    main()
