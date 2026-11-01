"""Dependency-free TF-IDF cosine retrieval over reviewed source text."""

from __future__ import annotations

import math
import re
from collections import Counter


ALIASES = {
    "cars": "vehicle", "car": "vehicle", "vehicles": "vehicle",
    "signals": "signal", "lights": "signal", "light": "signal",
    "blocked": "obstruction", "blocking": "obstruction", "blockage": "obstruction",
    "pothole": "obstruction", "obstacles": "obstruction", "obstacle": "obstruction",
    "parking": "park", "parked": "park", "pedestrians": "pedestrian",
    "trains": "train", "reports": "report", "reported": "report",
}
STOP = set("a an the and or to of is are was were for on in at by with from what should how do does did i we they it its this that there be can have has not yet who which each other as".split())


def terms(text: str) -> list[str]:
    words = [ALIASES.get(w, w) for w in re.findall(r"[a-z]+", text.lower())]
    words = [w for w in words if len(w) > 2 and w not in STOP]
    return words + [f"{a}_{b}" for a, b in zip(words, words[1:])]


def searchable_text(record: dict) -> str:
    return " ".join(str(record.get(key, "")) for key in
                    ("situation", "description", "entities", "communication_type"))


class Retriever:
    def __init__(self, records: list[dict]):
        self.records = records
        counts = [Counter(terms(searchable_text(r))) for r in records]
        n = len(counts)
        document_frequency = Counter(t for c in counts for t in c)
        self.idf = {t: math.log((1 + n) / (1 + df)) + 1 for t, df in document_frequency.items()}
        self.vectors = [self._vector(c) for c in counts]

    def _vector(self, counts: Counter) -> dict[str, float]:
        weighted = {t: (1 + math.log(c)) * self.idf[t] for t, c in counts.items() if t in self.idf}
        norm = math.sqrt(sum(x * x for x in weighted.values())) or 1.0
        return {t: x / norm for t, x in weighted.items()}

    def search(self, query: str, k: int = 3) -> list[tuple[dict, float]]:
        q = self._vector(Counter(terms(query)))
        scores = [(record, sum(weight * vector.get(term, 0) for term, weight in q.items()))
                  for record, vector in zip(self.records, self.vectors)]
        return sorted((item for item in scores if item[1] > 0), key=lambda item: item[1], reverse=True)[:k]
