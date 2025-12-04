from __future__ import annotations

from statistics import mean
from typing import Dict, List, Optional

from backend.domain.models import AnalysisResult, Clause, ClauseRisk


class RiskAnalyzer:
    """Assign numeric risk scores based on LLM hints and simple policy."""

    def _level_from_score(self, score: int) -> str:
        if score >= 75:
            return "high"
        if score >= 50:
            return "medium"
        return "low"

    def _score_from_hint(self, hint: str) -> int:
        lowered = hint.lower()
        if "high" in lowered:
            return 85
        if "medium" in lowered:
            return 60
        if "low" in lowered:
            return 25
        return 40

    def compute_clause_risk(
        self,
        clause: Clause,
        hint: str,
        llm_score: Optional[int] = None,
        llm_level: Optional[str] = None,
    ) -> ClauseRisk:
        score = llm_score if llm_score is not None else self._score_from_hint(hint)
        # Prefer score-derived level to keep badge consistent even if llm_level is off
        level = self._level_from_score(score)
        if llm_score is None and llm_level:
            level = llm_level
        return ClauseRisk(score=score, level=level, explanation=hint)

    def analyze(
        self,
        document_id: str,
        clauses: List[Clause],
        risk_data: List[Dict[str, Optional[str | int]]],
    ) -> AnalysisResult:
        for clause, rd in zip(clauses, risk_data):
            hint = str(rd.get("risk_reason") or rd.get("hint") or "")
            llm_score = rd.get("risk_score")
            llm_level = rd.get("risk_level")
            clause.risk = self.compute_clause_risk(clause, hint, llm_score=llm_score, llm_level=llm_level)

        overall = mean([clause.risk.score for clause in clauses]) if clauses else 0.0
        return AnalysisResult(document_id=document_id, clauses=clauses, overall_risk_score=overall)
