from __future__ import annotations

import os
from typing import Optional

from backend.infrastructure.llm.base import LLMProvider

try:
    from openai import AsyncOpenAI
except ImportError:  # pragma: no cover - optional dependency
    AsyncOpenAI = None


class OpenAILLMProvider(LLMProvider):
    """Thin wrapper around OpenAI chat completions."""

    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-4o-mini") -> None:
        if AsyncOpenAI is None:
            raise ImportError("Install openai>=1.0.0 to use OpenAILLMProvider.")
        self.client = AsyncOpenAI(api_key=api_key or os.getenv("OPENAI_API_KEY"))
        self.model = model

    async def _call(self, system_prompt: str, user_prompt: str) -> str:
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.1,
        )
        return response.choices[0].message.content or ""

    async def summarize_clause(self, clause_text: str) -> str:
        system = "You are a contract clause summarizer. Answer in Korean in one sentence."
        return await self._call(system, clause_text)

    async def classify_clause(self, clause_text: str) -> str:
        system = "You are a classifier that returns one label: payment, termination, responsibility, penalty, confidentiality, or general."
        return await self._call(system, clause_text)

    async def analyze_risk(self, clause_text: str) -> str:
        system = (
            "You highlight potential risks in contract clauses. "
            "Provide concise Korean explanation and avoid legal advice language."
        )
        return await self._call(system, clause_text)

    async def analyze_clause(self, clause_text: str) -> dict:
        system = (
            "You are a Korean contract analysis agent. Use only the provided clause text; do NOT invent amounts, dates, or names. "
            "If a field is missing in the clause, set it to null. Return JSON with fields: "
            "summary, category(one of payment, termination, responsibility, penalty, confidentiality, general), "
            "risk_score(0-100 integer), risk_level(low|medium|high), risk_reason(short Korean explanation). "
            "Output JSON only."
        )
        raw = await self._call(system, clause_text)
        try:
            import json

            data = json.loads(raw)
            return {
                "summary": data.get("summary") or raw,
                "category": data.get("category") or "general",
                "risk_score": int(data.get("risk_score", 0)),
                "risk_level": data.get("risk_level") or "low",
                "risk_reason": data.get("risk_reason") or "",
            }
        except Exception:
            # Fallback: keep raw text in reason
            return {
                "summary": raw[:200],
                "category": "general",
                "risk_score": 40,
                "risk_level": "medium",
                "risk_reason": raw,
            }
