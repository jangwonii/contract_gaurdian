from __future__ import annotations

from abc import ABC, abstractmethod


class LLMProvider(ABC):
    """Interface for LLM providers."""

    async def analyze_clause(self, clause_text: str) -> dict:
        """Optional: return structured analysis with summary/category/risk."""
        raise NotImplementedError

    @abstractmethod
    async def summarize_clause(self, clause_text: str) -> str:
        raise NotImplementedError

    @abstractmethod
    async def classify_clause(self, clause_text: str) -> str:
        raise NotImplementedError

    @abstractmethod
    async def analyze_risk(self, clause_text: str) -> str:
        raise NotImplementedError

    async def infer_contract_type(self, clauses) -> str | None:
        """Optional: infer contract type from clauses."""
        raise NotImplementedError

    async def suggest_improvement(self, clause_text: str) -> dict:
        """Optional: suggest improved clause text."""
        raise NotImplementedError
