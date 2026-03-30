from __future__ import annotations

from pathlib import Path
from typing import List, Dict

import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

BACKEND_DIR = Path(__file__).resolve().parents[1]

EMBED_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

AOSA_INDEX_PATH = BACKEND_DIR / "resources" / "aosa_index.faiss"
AOSA_CHUNKS_PATH = BACKEND_DIR / "resources" / "aosa_chunks.txt"

_EMBED_MODEL: SentenceTransformer | None = None

_AOSA_INDEX: faiss.Index | None = None
_AOSA_CHUNKS: List[str] = []

def _get_model() -> SentenceTransformer:
    global _EMBED_MODEL
    if _EMBED_MODEL is None:
        _EMBED_MODEL = SentenceTransformer(EMBED_MODEL_NAME)
    return _EMBED_MODEL


def _load_aosa() -> None:
    global _AOSA_INDEX, _AOSA_CHUNKS

    if _AOSA_INDEX is None:
        if not AOSA_INDEX_PATH.exists():
            raise RuntimeError(
                f"AOSA FAISS-Index nicht gefunden: {AOSA_INDEX_PATH} – "
                "führe zuerst 'python -m backend.ai.build_aosa_index' aus."
            )
        _AOSA_INDEX = faiss.read_index(str(AOSA_INDEX_PATH))

    if not _AOSA_CHUNKS:
        if not AOSA_CHUNKS_PATH.exists():
            raise RuntimeError(
               f"AOSA Chunk-Datei nicht gefunden: {AOSA_CHUNKS_PATH} – "
                "führe zuerst 'python -m backend.ai.build_aosa_index' aus."
            )
        with open(AOSA_CHUNKS_PATH, "r", encoding="utf-8") as f:
            _AOSA_CHUNKS = [b.strip() for b in f.read().split("\n---\n") if b.strip()]


def retrieve_aosa_context(query: str, k: int = 6) -> List[str]:
    model = _get_model()
    _load_aosa()
    assert _AOSA_INDEX is not None

    chunks = _AOSA_CHUNKS

    query_vec = model.encode([query])
    distances, indices = _AOSA_INDEX.search(query_vec, k)

    results: List[str] = []
    for idx in indices[0]:
        if 0 <= idx < len(chunks):
            results.append(chunks[idx])
    return results

def retrieve_dynamic_context(query: str, texts: List[str], k: int = 6) -> List[str]:
    if not texts:
        return []

    model = _get_model()

    doc_embeddings = model.encode(texts)
    query_embedding = model.encode([query])[0]

    doc_norms = np.linalg.norm(doc_embeddings, axis=1) + 1e-8
    query_norm = np.linalg.norm(query_embedding) + 1e-8
    sims = (doc_embeddings @ query_embedding) / (doc_norms * query_norm)

    idx_sorted = np.argsort(-sims)[:k]
    return [texts[i] for i in idx_sorted]
