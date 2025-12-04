from __future__ import annotations

from statistics import mean
from typing import Dict, List, Optional

from backend.domain.models import AnalysisResult, Clause, ClauseRisk


class RiskPolicy:
    """Strategy interface for contract-type-specific risk scoring."""

    def score(
        self,
        clause: Clause,
        hint: str,
        llm_score: Optional[int] = None,
        llm_level: Optional[str] = None,
    ) -> ClauseRisk:
        raise NotImplementedError


class BaseRiskPolicy(RiskPolicy):
    """Default policy using hint/LLM score with minimal heuristics."""

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

    def score(
        self,
        clause: Clause,
        hint: str,
        llm_score: Optional[int] = None,
        llm_level: Optional[str] = None,
    ) -> ClauseRisk:
        score = llm_score if llm_score is not None else self._score_from_hint(hint)
        level = self._level_from_score(score)
        if llm_score is None and llm_level:
            level = llm_level
        return ClauseRisk(score=score, level=level, explanation=hint)


class EmploymentRiskPolicy(BaseRiskPolicy):
    """Weights termination/probation/penalty clauses higher for employment contracts."""

    def score(
        self,
        clause: Clause,
        hint: str,
        llm_score: Optional[int] = None,
        llm_level: Optional[str] = None,
    ) -> ClauseRisk:
        base = super().score(clause, hint, llm_score, llm_level)
        text = (clause.raw_text or "").lower()
        category = (clause.category or "").lower()
        risky_keywords = ["해지", "수습", "penalty", "손해배상", "위약금", "책임"]
        if category in {"termination", "penalty", "responsibility"} or any(k in text for k in risky_keywords):
            base.score = min(100, base.score + 10)
        if "근로시간" in clause.raw_text or "overtime" in text:
            base.score = min(100, base.score + 5)
        base.level = self._level_from_score(base.score)
        return base


class LeaseRiskPolicy(BaseRiskPolicy):
    """Weights deposit/maintenance/penalty clauses higher for lease contracts."""

    def score(
        self,
        clause: Clause,
        hint: str,
        llm_score: Optional[int] = None,
        llm_level: Optional[str] = None,
    ) -> ClauseRisk:
        base = super().score(clause, hint, llm_score, llm_level)
        text = (clause.raw_text or "").lower()
        category = (clause.category or "").lower()
        deposit_hits = ["보증금", "deposit", "담보"]
        maintenance_hits = ["수리", "보수", "원상복구", "maintenance", "repair"]
        if category in {"payment", "penalty"} or any(k in text for k in deposit_hits):
            base.score = min(100, base.score + 10)
        if any(k in text for k in maintenance_hits):
            base.score = min(100, base.score + 8)
        base.level = self._level_from_score(base.score)
        return base


class RiskAnalyzer:
    """Assign numeric risk scores using contract-type-specific policy."""

    def __init__(self, policies: Optional[Dict[str, RiskPolicy]] = None) -> None:
        default_policies: Dict[str, RiskPolicy] = {
            "general": BaseRiskPolicy(),
            "employment": EmploymentRiskPolicy(),
            "lease": LeaseRiskPolicy(),
        }
        self.policies = {**default_policies, **(policies or {})}

    def choose_policy(self, contract_type: str) -> RiskPolicy:
        key = (contract_type or "general").lower()
        return self.policies.get(key, self.policies["general"])

    def analyze(
        self,
        document_id: str,
        clauses: List[Clause],
        risk_data: List[Dict[str, Optional[str | int]]],
        contract_type: str = "general",
    ) -> AnalysisResult:
        policy = self.choose_policy(contract_type)
        for clause, rd in zip(clauses, risk_data):
            hint = str(rd.get("risk_reason") or rd.get("hint") or "")
            llm_score = rd.get("risk_score")
            llm_level = rd.get("risk_level")
            clause.risk = policy.score(clause, hint, llm_score=llm_score, llm_level=llm_level)

        overall = mean([clause.risk.score for clause in clauses]) if clauses else 0.0
        return AnalysisResult(
            document_id=document_id,
            clauses=clauses,
            overall_risk_score=overall,
            contract_type=contract_type or "general",
        )
