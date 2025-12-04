from __future__ import annotations

import re
from typing import List

from backend.domain.models import Clause


class ClauseExtractor:
    """Heuristic clause splitter for Korean contract text."""

    def split_into_clauses(self, text: str) -> List[str]:
        normalized = text.replace("\r\n", "\n").replace("\r", "\n")
        heading_pattern = r"(?=제\s*\d+\s*조)"

        if re.search(heading_pattern, normalized):
            chunks = re.split(heading_pattern, normalized)
            clauses = [f"{match}{body}".strip() for match, body in zip(re.findall(heading_pattern, normalized), chunks[1:])]
        else:
            clauses = [c.strip() for c in re.split(r"\n\s*\n", normalized) if c.strip()]

        merged: List[str] = []
        for clause in clauses:
            cleaned = re.sub(r"\s{2,}", " ", clause)
            cleaned = cleaned.strip()
            if cleaned:
                merged.append(cleaned)
        return merged

    def build_clauses(self, text: str) -> List[Clause]:
        clauses = []
        for idx, raw in enumerate(self.split_into_clauses(text), start=1):
            clause = Clause(id=f"clause-{idx}", raw_text=raw)
            clauses.append(clause)
        return clauses
