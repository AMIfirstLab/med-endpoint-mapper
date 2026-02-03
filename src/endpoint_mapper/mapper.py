from __future__ import annotations

import difflib
import json
import re
import unicodedata
from dataclasses import asdict, dataclass
from pathlib import Path


def normalize(text: str) -> str:
    text = unicodedata.normalize("NFKC", text).lower().strip()
    text = re.sub(r"[%_/()\-]+", " ", text)
    return re.sub(r"\s+", " ", text).strip()


@dataclass(frozen=True)
class MappingResult:
    source: str
    endpoint_id: str | None
    canonical_name: str | None
    label_ko: str | None
    canonical_unit: str | None
    domain: str | None
    match_method: str
    confidence: float
    matched_term: str | None
    needs_review: bool

    def to_dict(self) -> dict:
        return asdict(self)


class EndpointMapper:
    def __init__(self, concepts: list[dict], fuzzy_threshold: float = 0.72):
        self.concepts = concepts
        self.threshold = fuzzy_threshold
        self.index: dict[str, tuple[dict, str]] = {}
        for concept in concepts:
            terms = [concept["canonical_name"], *concept.get("aliases", [])]
            for term in terms:
                self.index[normalize(term)] = (concept, term)

    @classmethod
    def from_json(cls, path: str | Path, fuzzy_threshold: float = 0.72) -> "EndpointMapper":
        with Path(path).open(encoding="utf-8") as f:
            return cls(json.load(f), fuzzy_threshold=fuzzy_threshold)

    def map(self, source: str, domain: str | None = None) -> MappingResult:
        query = normalize(source)
        if query in self.index:
            concept, term = self.index[query]
            if not domain or concept["domain"] == domain:
                method = "canonical" if normalize(term) == normalize(concept["canonical_name"]) else "alias"
                return self._result(source, concept, method, 1.0 if method == "canonical" else 0.98, term)

        candidates: list[tuple[float, dict, str]] = []
        for normalized_term, (concept, original_term) in self.index.items():
            if domain and concept["domain"] != domain:
                continue
            score = difflib.SequenceMatcher(None, query, normalized_term).ratio()
            query_tokens, candidate_tokens = set(query.split()), set(normalized_term.split())
            if query_tokens and candidate_tokens:
                overlap = len(query_tokens & candidate_tokens) / len(query_tokens | candidate_tokens)
                score = 0.78 * score + 0.22 * overlap
            candidates.append((score, concept, original_term))

        if candidates:
            score, concept, term = max(candidates, key=lambda item: item[0])
            if score >= self.threshold:
                return self._result(source, concept, "fuzzy", round(score, 4), term)
        return MappingResult(source, None, None, None, None, domain, "unmapped", 0.0, None, True)

    @staticmethod
    def _result(source: str, concept: dict, method: str, confidence: float, term: str) -> MappingResult:
        return MappingResult(
            source=source,
            endpoint_id=concept["id"],
            canonical_name=concept["canonical_name"],
            label_ko=concept["label_ko"],
            canonical_unit=concept["unit"],
            domain=concept["domain"],
            match_method=method,
            confidence=confidence,
            matched_term=term,
            needs_review=method == "fuzzy" or confidence < 0.95,
        )
