from __future__ import annotations

import logging
from typing import List, Tuple, Optional

from backend.domain.models import Clause
from backend.infrastructure.llm.base import LLMProvider


class LLMAgent:
    """Orchestrates LLM calls for clause-level analysis."""

    def __init__(self, provider: LLMProvider) -> None:
        self.provider = provider
        self.logger = logging.getLogger(__name__)

    async def annotate(self, clauses: List[Clause]) -> Tuple[List[Clause], List[dict]]:
        risk_data: List[dict] = []
        for clause in clauses:
            try:
                if hasattr(self.provider, "analyze_clause"):
                    result = await self.provider.analyze_clause(clause.raw_text)
                    clause.summary = result.get("summary") or clause.summary
                    clause.category = result.get("category") or clause.category
                    clause.reasoning = result.get("reasoning") or clause.reasoning
                    risk_data.append(
                        {
                            "risk_reason": result.get("risk_reason") or "",
                            "risk_score": result.get("risk_score"),
                            "risk_level": result.get("risk_level"),
                        }
                    )
                    continue
                clause.summary = await self.provider.summarize_clause(clause.raw_text)
                clause.category = await self.provider.classify_clause(clause.raw_text)
                hint = await self.provider.analyze_risk(clause.raw_text)
            except Exception as exc:  # noqa: BLE001
                # Fail soft: keep pipeline running with graceful defaults
                self.logger.warning("LLM provider failed, using fallback summary: %s", exc)
                clause.summary = clause.summary or "[LLM error] 요약 불가"
                clause.category = clause.category or "general"
                clause.reasoning = clause.reasoning or "LLM unavailable"
                hint = f"LLM unavailable: {exc}"
            risk_data.append({"risk_reason": hint, "risk_score": None, "risk_level": None})
        return clauses, risk_data

    async def infer_contract_type(self, clauses: List[Clause]) -> Optional[str]:
        try:
            if hasattr(self.provider, "infer_contract_type"):
                return await self.provider.infer_contract_type(clauses)
        except Exception as exc:  # noqa: BLE001
            self.logger.warning("LLM contract type inference failed: %s", exc)
        # Heuristic fallback
        categories = [c.category or "" for c in clauses]
        text = " ".join([c.raw_text for c in clauses])
        if any(cat in {"employment", "responsibility", "termination"} for cat in categories) or "급여" in text:
            return "employment"
        if any(cat in {"lease"} for cat in categories) or "보증금" in text:
            return "lease"
        return None
