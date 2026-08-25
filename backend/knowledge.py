"""
Organizational memory layer for Auskulta.

This is what turns a raw anomaly score into a diagnosis that's grounded in
real (or, for now, synthetic-but-realistic) maintenance history instead of
an LLM guessing freely. It loads a small knowledge base of past maintenance
records and retrieves the most similar past incidents for a given query
using TF-IDF + cosine similarity — no external embedding API required, so
it works fully offline and starts instantly.

Upgrade path: swap `_vectorizer`/`_matrix` for a real embedding model
(e.g. sentence-transformers) if the knowledge base grows large enough that
TF-IDF's keyword-overlap limitation starts to matter.
"""

import json
from dataclasses import dataclass
from pathlib import Path
from typing import List

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

KNOWLEDGE_BASE_PATH = Path(__file__).resolve().parent.parent / "data" / "knowledge_base.json"


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


class KnowledgeBase:
    def __init__(self, path: Path = KNOWLEDGE_BASE_PATH):
        with open(path, "r", encoding="utf-8") as f:
            self.records = json.load(f)

        corpus = [f"{r['machine']} {r['symptom']} {r['root_cause']}" for r in self.records]
        self._vectorizer = TfidfVectorizer()
        self._matrix = self._vectorizer.fit_transform(corpus)

    def retrieve(self, query: str, top_k: int = 3) -> List[EvidenceRecord]:
        query_vec = self._vectorizer.transform([query])
        scores = cosine_similarity(query_vec, self._matrix).flatten()
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
                )
            )
        return results


_kb = KnowledgeBase()


def retrieve_evidence(query: str, top_k: int = 3) -> List[EvidenceRecord]:
    return _kb.retrieve(query, top_k=top_k)
