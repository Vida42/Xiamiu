#!/usr/bin/env python3
"""Embed catalog and rated album documents using BGE-M3 locally.

Inputs:
- private_data/20_embeddings/album_embeddings/catalog_album_documents.json
- private_data/20_embeddings/album_embeddings/rated_album_documents.json

Outputs:
- private_data/20_embeddings/album_embeddings/catalog_album_vectors.npz
- private_data/20_embeddings/album_embeddings/rated_album_vectors.npz
- private_data/20_embeddings/album_embeddings/embedding_run_meta.json

Uses Apple MPS (Metal) acceleration when available, otherwise CPU.
"""

from __future__ import annotations

import argparse
import json
import time
from datetime import date
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CATALOG_DOC_PATH = REPO_ROOT / "private_data" / "20_embeddings" / "album_embeddings" / "catalog_album_documents.json"
DEFAULT_RATED_DOC_PATH = REPO_ROOT / "private_data" / "20_embeddings" / "album_embeddings" / "rated_album_documents.json"
DEFAULT_CATALOG_VEC_PATH = REPO_ROOT / "private_data" / "20_embeddings" / "album_embeddings" / "catalog_album_vectors.npz"
DEFAULT_RATED_VEC_PATH = REPO_ROOT / "private_data" / "20_embeddings" / "album_embeddings" / "rated_album_vectors.npz"
DEFAULT_META_PATH = REPO_ROOT / "private_data" / "20_embeddings" / "album_embeddings" / "embedding_run_meta.json"

DEFAULT_MODEL = "BAAI/bge-m3"
DEFAULT_BATCH = 64


def select_device() -> str:
    import torch
    if torch.backends.mps.is_available():
        return "mps"
    if torch.cuda.is_available():
        return "cuda"
    return "cpu"


def load_documents(path: Path) -> list[dict[str, Any]]:
    with path.open("r", encoding="utf-8") as f:
        payload = json.load(f)
    return payload["documents"]


def embed_documents(
    documents: list[dict[str, Any]],
    model_name: str,
    device: str,
    batch_size: int,
    label: str,
) -> tuple[Any, Any]:
    import numpy as np
    from sentence_transformers import SentenceTransformer

    print(f"[{label}] loading model {model_name} on {device}...")
    t0 = time.time()
    model = SentenceTransformer(model_name, device=device)
    print(f"[{label}] model loaded in {time.time() - t0:.1f}s")

    texts = [d["text"] for d in documents]
    album_ids = np.array(
        [d["albumId"] if isinstance(d["albumId"], int) else -1 for d in documents],
        dtype=np.int64,
    )

    print(f"[{label}] embedding {len(texts):,} documents (batch={batch_size})...")
    t1 = time.time()
    vectors = model.encode(
        texts,
        batch_size=batch_size,
        show_progress_bar=True,
        convert_to_numpy=True,
        normalize_embeddings=True,
    )
    elapsed = time.time() - t1
    print(f"[{label}] embedded {len(texts):,} in {elapsed:.1f}s ({len(texts)/elapsed:.0f}/s)")
    print(f"[{label}] vector shape: {vectors.shape}")

    return album_ids, vectors


def save_vectors(path: Path, album_ids: Any, vectors: Any) -> None:
    import numpy as np
    path.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(path, album_ids=album_ids, vectors=vectors)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--catalog-doc-path", type=Path, default=DEFAULT_CATALOG_DOC_PATH)
    parser.add_argument("--rated-doc-path", type=Path, default=DEFAULT_RATED_DOC_PATH)
    parser.add_argument("--catalog-vec-path", type=Path, default=DEFAULT_CATALOG_VEC_PATH)
    parser.add_argument("--rated-vec-path", type=Path, default=DEFAULT_RATED_VEC_PATH)
    parser.add_argument("--meta-path", type=Path, default=DEFAULT_META_PATH)
    parser.add_argument("--model", type=str, default=DEFAULT_MODEL)
    parser.add_argument("--batch-size", type=int, default=DEFAULT_BATCH)
    parser.add_argument("--device", type=str, default=None,
                        help="Override auto-detected device (mps/cuda/cpu).")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    device = args.device or select_device()
    print(f"Embedding device: {device}")

    catalog_docs = load_documents(args.catalog_doc_path)
    rated_docs = load_documents(args.rated_doc_path)

    started = time.time()

    catalog_ids, catalog_vecs = embed_documents(
        catalog_docs, args.model, device, args.batch_size, "catalog"
    )
    save_vectors(args.catalog_vec_path, catalog_ids, catalog_vecs)

    rated_ids, rated_vecs = embed_documents(
        rated_docs, args.model, device, args.batch_size, "rated"
    )
    save_vectors(args.rated_vec_path, rated_ids, rated_vecs)

    total = time.time() - started

    meta = {
        "generatedAt": date.today().isoformat(),
        "model": args.model,
        "device": device,
        "batchSize": args.batch_size,
        "catalogCount": int(catalog_ids.shape[0]),
        "ratedCount": int(rated_ids.shape[0]),
        "vectorDim": int(catalog_vecs.shape[1]),
        "totalSeconds": round(total, 1),
    }
    args.meta_path.parent.mkdir(parents=True, exist_ok=True)
    with args.meta_path.open("w", encoding="utf-8") as f:
        json.dump(meta, f, indent=2)
        f.write("\n")

    print(f"\nDone in {total:.1f}s.")
    print(f"  catalog vectors: {args.catalog_vec_path}")
    print(f"  rated vectors:   {args.rated_vec_path}")
    print(f"  meta:            {args.meta_path}")


if __name__ == "__main__":
    main()
