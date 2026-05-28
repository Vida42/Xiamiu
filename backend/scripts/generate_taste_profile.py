#!/usr/bin/env python3
"""Generate a cached English taste profile via Claude.

Reads:
- private_data/10_intermediate/taste_profile/taste_profile.json (structured)
- private_data/10_intermediate/taste_profile/taste_document.md (prose)

Writes:
- private_data/40_model_cache/taste_profile.json with:
    profile_text, generated_at, model, prompt_version,
    inputs_hash, cache_key, usage

Cache hit short-circuits the LLM call. Cache key composition:
    sha256(inputs_hash + model + prompt_version)
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from anthropic import Anthropic


REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_PROFILE_PATH = REPO_ROOT / "private_data" / "10_intermediate" / "taste_profile" / "taste_profile.json"
DEFAULT_DOC_PATH = REPO_ROOT / "private_data" / "10_intermediate" / "taste_profile" / "taste_document.md"
DEFAULT_CACHE_PATH = REPO_ROOT / "private_data" / "40_model_cache" / "taste_profile.json"

DEFAULT_MODEL = "claude-haiku-4-5"
PROMPT_VERSION = "v1"
MAX_OUTPUT_TOKENS = 600

SYSTEM_PROMPT = """\
You are a music taste analyst. You read a listener's structured rating data
and prose comments (in mixed Chinese and English) and write a concise English
taste profile that will be used to judge candidate recommendations.

Your profile must:
- Be ~150-200 words, single paragraph.
- Ground every claim in the evidence (artists, albums, styles, prose comments).
- Capture taste boundaries: what the listener likes AND what they explicitly dislike.
- Note any internal contradictions (same artist with both 5-star and 1-star tracks).
- Preserve nuance from prose comments rather than reducing to genre labels.
- Avoid generic phrases like "diverse taste" or "appreciates good music".
- Output prose only. No headers, no lists, no JSON.
"""


def hash_inputs(profile_text: str, document_text: str) -> str:
    h = hashlib.sha256()
    h.update(profile_text.encode("utf-8"))
    h.update(b"\x00")
    h.update(document_text.encode("utf-8"))
    return h.hexdigest()[:16]


def build_cache_key(inputs_hash: str, model: str, prompt_version: str) -> str:
    h = hashlib.sha256()
    h.update(f"{inputs_hash}|{model}|{prompt_version}".encode("utf-8"))
    return h.hexdigest()[:16]


def build_user_prompt(profile_json_text: str, document_text: str) -> str:
    return f"""\
Below is a listener's taste data. Write the taste profile per the system instructions.

# Structured taste signals (JSON)
{profile_json_text}

# Full taste document (prose, listening notes)
{document_text}
"""


def run(args: argparse.Namespace) -> None:
    load_dotenv(Path(args.env_path).resolve() if args.env_path else REPO_ROOT / ".env")

    profile_text = args.profile_path.read_text(encoding="utf-8")
    document_text = args.doc_path.read_text(encoding="utf-8")
    inputs_hash = hash_inputs(profile_text, document_text)
    cache_key = build_cache_key(inputs_hash, args.model, PROMPT_VERSION)

    if args.cache_path.exists():
        cached = json.loads(args.cache_path.read_text(encoding="utf-8"))
        if cached.get("cache_key") == cache_key and not args.force:
            print("Cache hit — no API call made.")
            print(f"  cache_key: {cache_key}")
            print(f"  model:     {cached.get('model')}")
            print(f"  generated: {cached.get('generated_at')}")
            print(f"  profile preview: {cached.get('profile_text', '')[:160]}...")
            return

    print(f"Cache miss (or --force). Calling {args.model}...")
    client = Anthropic()
    user_prompt = build_user_prompt(profile_text, document_text)

    resp = client.messages.create(
        model=args.model,
        max_tokens=MAX_OUTPUT_TOKENS,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_prompt}],
    )

    profile_text_out = "".join(
        block.text for block in resp.content if getattr(block, "type", None) == "text"
    ).strip()

    payload = {
        "cache_key": cache_key,
        "inputs_hash": inputs_hash,
        "model": resp.model,
        "prompt_version": PROMPT_VERSION,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "profile_text": profile_text_out,
        "usage": {
            "input_tokens": resp.usage.input_tokens,
            "output_tokens": resp.usage.output_tokens,
        },
        "stop_reason": resp.stop_reason,
    }

    args.cache_path.parent.mkdir(parents=True, exist_ok=True)
    args.cache_path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    print("Taste profile generated and cached.")
    print(f"  cache_key: {cache_key}")
    print(f"  model:     {resp.model}")
    print(f"  tokens:    in={resp.usage.input_tokens}, out={resp.usage.output_tokens}")
    print(f"  cache:     {args.cache_path}")
    print()
    print("Profile preview (first 240 chars):")
    print(f"  {profile_text_out[:240]}...")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--profile-path", type=Path, default=DEFAULT_PROFILE_PATH)
    parser.add_argument("--doc-path", type=Path, default=DEFAULT_DOC_PATH)
    parser.add_argument("--cache-path", type=Path, default=DEFAULT_CACHE_PATH)
    parser.add_argument("--model", type=str, default=DEFAULT_MODEL)
    parser.add_argument("--env-path", type=str, default=None)
    parser.add_argument("--force", action="store_true", help="Bypass cache and regenerate.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    run(args)


if __name__ == "__main__":
    main()
