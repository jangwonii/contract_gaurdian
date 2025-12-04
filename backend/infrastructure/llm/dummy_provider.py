from __future__ import annotations

from backend.infrastructure.llm.base import LLMProvider


class DummyLLMProvider(LLMProvider):
    """Development-friendly provider that returns deterministic mock data."""

    def __init__(self) -> None:
        self.keyword_categories = {
            "해지": "termination",
            "penalty": "penalty",
            "손해배상": "penalty",
            "지급": "payment",
            "급여": "payment",
            "책임": "responsibility",
            "의무": "responsibility",
        }

    async def summarize_clause(self, clause_text: str) -> str:
        head = clause_text.strip().split("\n")[0][:160]
        return f"요약: {head}" if head else "요약: 내용 확인 필요"

    async def classify_clause(self, clause_text: str) -> str:
        for keyword, category in self.keyword_categories.items():
            if keyword in clause_text:
                return category
        if "payment" in clause_text.lower():
            return "payment"
        if "termination" in clause_text.lower():
            return "termination"
        return "general"

    async def analyze_risk(self, clause_text: str) -> str:
        text = clause_text.lower()
        reasons = []
        label = "Low risk"
        score = 25

        penalty_hits = ["손해배상", "위약금", "penalty", "배상"]
        termination_hits = ["해지", "termination", "해약", "수습", "연장"]
        obligation_hits = ["의무", "책임", "must", "shall", "obligation", "responsibility"]
        payment_hits = ["지급", "급여", "payment", "보수", "대가"]

        if any(k in clause_text for k in penalty_hits):
            label = "High risk"
            score = 90
            reasons.append("벌칙/배상 조건이 포함되어 있습니다.")
        if any(k in clause_text for k in termination_hits):
            label = "Medium risk" if label == "Low risk" else label
            score = max(score, 70)
            reasons.append("해지/수습/연장 조건이 있으니 세부 조항을 검토하세요.")
        if any(k in clause_text for k in obligation_hits):
            label = "Medium risk" if label == "Low risk" else label
            score = max(score, 60)
            reasons.append("의무/책임 범위가 명시되어 있습니다.")
        if any(k in clause_text for k in payment_hits):
            reasons.append("보수/지급 관련 조항입니다.")

        if not reasons:
            reasons.append("정보성 조항으로 보입니다.")

        return f"{label}: " + " ".join(reasons)

    async def analyze_clause(self, clause_text: str) -> dict:
        summary = await self.summarize_clause(clause_text)
        category = await self.classify_clause(clause_text)
        risk_text = await self.analyze_risk(clause_text)
        # Derive score from label prefix
        score = 25
        if risk_text.lower().startswith("high"):
            score = 90
        elif risk_text.lower().startswith("medium"):
            score = 65
        return {
            "summary": summary,
            "category": category,
            "risk_score": score,
            "risk_level": "high" if score >= 75 else "medium" if score >= 50 else "low",
            "risk_reason": risk_text,
        }
