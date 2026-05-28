#!/usr/bin/env python3
"""Re-rank Day 5 candidates by LLM fit_score and produce the final top-N set.

Inputs:
- private_data/30_recommendations/ai_outputs/embedding_candidates_day5.json
- private_data/40_model_cache/llm_candidate_judgments/*.json
- private_data/40_model_cache/taste_profile.json

Output:
- private_data/30_recommendations/ai_outputs/llm_ranked_recommendations_day6.json
"""

from __future__ import annotations

import argparse
import json
from datetime import date
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CANDIDATES_PATH = REPO_ROOT / "private_data" / "30_recommendations" / "ai_outputs" / "embedding_candidates_day5.json"
DEFAULT_JUDGMENTS_DIR = REPO_ROOT / "private_data" / "40_model_cache" / "llm_candidate_judgments"
DEFAULT_TASTE_CACHE_PATH = REPO_ROOT / "private_data" / "40_model_cache" / "taste_profile.json"
DEFAULT_OUTPUT_PATH = REPO_ROOT / "private_data" / "30_recommendations" / "ai_outputs" / "llm_ranked_recommendations_day6.json"
DEFAULT_TOP_N = 20


def load_judgments(judgments_dir: Path) -> dict[str, dict[str, Any]]:
    """Index judgments by candidate_id for fast lookup."""
    out: dict[str, dict[str, Any]] = {}
    for path in judgments_dir.glob("*.json"):
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            continue
        cid = payload.get("candidate_id")
        if cid:
            out[cid] = payload
    return out


def run(args: argparse.Namespace) -> None:
    candidates_payload = json.loads(args.candidates_path.read_text(encoding="utf-8"))
    candidates = candidates_payload.get("candidates") or []

    judgments = load_judgments(args.judgments_dir)
    taste = json.loads(args.taste_cache_path.read_text(encoding="utf-8"))

    judged: list[dict[str, Any]] = []
    missing = 0
    for c in candidates:
        cid = c["candidateId"]
        j = judgments.get(cid)
        if j is None:
            missing += 1
            continue
        merged = {
            **c,
            "llm": {
                "fit_score": j.get("fit_score"),
                "reason": j.get("reason"),
                "risk": j.get("risk"),
                "model": j.get("model"),
                "prompt_version": j.get("prompt_version"),
                "cache_key": j.get("cache_key"),
            },
        }
        judged.append(merged)

    judged.sort(
        key=lambda c: (
            -(c["llm"]["fit_score"] if isinstance(c["llm"]["fit_score"], (int, float)) else -1),
            -(c["similarityScore"] or 0),
        )
    )

    top = judged[: args.top_n]

    score_buckets: dict[str, int] = {}
    for c in judged:
        s = c["llm"]["fit_score"]
        if not isinstance(s, (int, float)):
            bucket = "?"
        elif s >= 8:
            bucket = "8-10"
        elif s >= 6:
            bucket = "6-8"
        elif s >= 4:
            bucket = "4-6"
        elif s >= 2:
            bucket = "2-4"
        else:
            bucket = "0-2"
        score_buckets[bucket] = score_buckets.get(bucket, 0) + 1

    payload = {
        "generatedAt": date.today().isoformat(),
        "tasteProfileCacheKey": taste.get("cache_key"),
        "judgedCount": len(judged),
        "missingJudgmentCount": missing,
        "scoreBuckets": score_buckets,
        "topN": args.top_n,
        "recommendations": top,
    }

    args.output_path.parent.mkdir(parents=True, exist_ok=True)
    args.output_path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    print("LLM-ranked recommendations written.")
    print(f"  judged candidates:     {len(judged)}")
    print(f"  missing judgments:     {missing}")
    print(f"  score buckets:         {dict(sorted(score_buckets.items()))}")
    print(f"  output:                {args.output_path}")
    print()
    print(f"Top {args.top_n} (after LLM reranking):")
    for i, c in enumerate(top, start=1):
        score = c["llm"]["fit_score"]
        score_str = f"{score:>4.1f}" if isinstance(score, (int, float)) else "??.??"
        sim = c.get("similarityScore", 0.0)
        print(f"  {i:2d}. fit {score_str} (sim {sim:.3f}) | "
              f"{c['artistName']} / {c['albumName']}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--candidates-path", type=Path, default=DEFAULT_CANDIDATES_PATH)
    parser.add_argument("--judgments-dir", type=Path, default=DEFAULT_JUDGMENTS_DIR)
    parser.add_argument("--taste-cache-path", type=Path, default=DEFAULT_TASTE_CACHE_PATH)
    parser.add_argument("--output-path", type=Path, default=DEFAULT_OUTPUT_PATH)
    parser.add_argument("--top-n", type=int, default=DEFAULT_TOP_N)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    run(args)


if __name__ == "__main__":
    main()
