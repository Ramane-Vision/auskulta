"""
Organizational memory layer for Auskulta.

This is what turns a raw anomaly score into a diagnosis that's grounded in
real (or, for now, synthetic-but-realistic) maintenance history instead of
an LLM guessing freely.

Retrieval strategy: semantic retrieval via OpenAI embeddings when an API
key is available (catches paraphrases/synonyms that keyword matching
misses), with TF-IDF + cosine similarity as an always-available fallback
that never depends on network/API availability. This mirrors the same
best-effort-with-fallback pattern used for audio and LLM diagnosis
elsewhere in the codebase: the system should degrade, never break.
"""

import json
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

import config

logger = logging.getLogger("auskulta.knowledge")

KNOWLEDGE_BASE_PATH = Path(__file__).resolve().parent.parent / "data" / "knowledge_base.json"

# Confidence thresholds differ per retrieval method because the two
# similarity metrics live on different scales: OpenAI embedding cosine
# similarity for short related texts typically sits much higher (~0.3-0.8)
# than TF-IDF cosine similarity on a small keyword corpus (~0.1-0.4).
TFIDF_STRONG_THRESHOLD = 0.30
TFIDF_WEAK_THRESHOLD = 0.10
EMBEDDING_STRONG_THRESHOLD = 0.55
EMBEDDING_WEAK_THRESHOLD = 0.25


@dataclass
class EvidenceRecord:
    id: str
    machine: str
    symptom: str
    root_cause: str
    action_taken: str
    downtime_hours: float
    date: str
    similarity: float
    method: str = "tfidf"  # "embedding" or "tfidf" — tells diagnosis.py which threshold pair to use


class KnowledgeBase:
    def __init__(self, path: Path = KNOWLEDGE_BASE_PATH):
        with open(path, "r", encoding="utf-8") as f:
            self.records = json.load(f)

        self._corpus = [f"{r['machine']} {r['symptom']} {r['root_cause']}" for r in self.records]

        # TF-IDF: always built, this is the reliable fallback.
        self._vectorizer = TfidfVectorizer()
        self._matrix = self._vectorizer.fit_transform(self._corpus)

        # Embeddings: best-effort enhancement, built once at startup.
        self._embedding_client = None
        self._embeddings: Optional[np.ndarray] = None
        if config.LLM_API_KEY:
            try:
                from openai import OpenAI

                self._embedding_client = OpenAI(api_key=config.LLM_API_KEY, base_url=config.LLM_BASE_URL)
                response = self._embedding_client.embeddings.create(
                    model=config.LLM_EMBEDDING_MODEL, input=self._corpus
                )
                self._embeddings = np.array([d.embedding for d in response.data])
                logger.info("Semantic embedding retrieval aktif (%s).", config.LLM_EMBEDDING_MODEL)
            except Exception as exc:
                logger.warning("Gagal membangun embedding index, fallback ke TF-IDF: %s", exc)
                self._embedding_client = None
                self._embeddings = None

    def _retrieve_embedding(self, query: str, top_k: int) -> Optional[List[EvidenceRecord]]:
        if self._embeddings is None or self._embedding_client is None:
            return None
        try:
            response = self._embedding_client.embeddings.create(
                model=config.LLM_EMBEDDING_MODEL, input=[query]
            )
            query_vec = np.array([response.data[0].embedding])
            scores = cosine_similarity(query_vec, self._embeddings).flatten()
            return self._build_results(scores, top_k, method="embedding")
        except Exception as exc:
            logger.warning("Embedding retrieval gagal saat request, fallback ke TF-IDF: %s", exc)
            return None

    def _retrieve_tfidf(self, query: str, top_k: int) -> List[EvidenceRecord]:
        query_vec = self._vectorizer.transform([query])
        scores = cosine_similarity(query_vec, self._matrix).flatten()
        return self._build_results(scores, top_k, method="tfidf")

    def _build_results(self, scores: np.ndarray, top_k: int, method: str) -> List[EvidenceRecord]:
        ranked_idx = scores.argsort()[::-1][:top_k]
        results = []
        for idx in ranked_idx:
            if scores[idx] <= 0:
                continue
            r = self.records[idx]
            results.append(
                EvidenceRecord(
                    id=r["id"],
                    machine=r["machine"],
                    symptom=r["symptom"],
                    root_cause=r["root_cause"],
                    action_taken=r["action_taken"],
                    downtime_hours=r["downtime_hours"],
                    date=r["date"],
                    similarity=round(float(scores[idx]), 3),
                    method=method,
                )
            )
        return results

    def retrieve(self, query: str, top_k: int = 3) -> List[EvidenceRecord]:
        results = self._retrieve_embedding(query, top_k)
        if results is not None:
            return results
        return self._retrieve_tfidf(query, top_k)


_kb = KnowledgeBase()


def retrieve_evidence(query: str, top_k: int = 3) -> List[EvidenceRecord]:
    return _kb.retrieve(query, top_k=top_k)


def confidence_thresholds(method: str) -> tuple[float, float]:
    """Returns (strong_threshold, weak_threshold) for the given retrieval method."""
    if method == "embedding":
        return EMBEDDING_STRONG_THRESHOLD, EMBEDDING_WEAK_THRESHOLD
    return TFIDF_STRONG_THRESHOLD, TFIDF_WEAK_THRESHOLD
