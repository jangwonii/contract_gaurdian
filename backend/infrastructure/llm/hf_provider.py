from __future__ import annotations

import asyncio
import json
from typing import Optional

from backend.infrastructure.llm.base import LLMProvider

try:
    from huggingface_hub import InferenceClient
except ImportError as exc:  # pragma: no cover - optional dependency
    raise ImportError("Install huggingface_hub to use HuggingFaceLLMProvider.") from exc


class HuggingFaceLLMProvider(LLMProvider):
    """LLM provider using Hugging Face Inference API or custom inference endpoint."""

    def __init__(self, model: str, token: Optional[str] = None, api_url: Optional[str] = None) -> None:
        # Only set base_url when provided to avoid "model + base_url" conflict
        if api_url:
            self.client = InferenceClient(model=api_url, token=token, base_url=None)
        else:
            self.client = InferenceClient(model=model, token=token)
        self.model = model

    async def _chat_call(self, system_prompt: str, user_prompt: str, max_new_tokens: int = 128) -> str:
        def _run_chat() -> str:
            response = self.client.chat_completion(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                max_tokens=max_new_tokens,
                temperature=0.1,
            )
            # chat_completion returns dict-like with content
            return response.choices[0].message["content"]

        return await asyncio.to_thread(_run_chat)

    async def _invoke(self, system_prompt: str, user_prompt: str, max_new_tokens: int = 128) -> str:
        return await self._chat_call(system_prompt, user_prompt, max_new_tokens=max_new_tokens)

    async def summarize_clause(self, clause_text: str) -> str:
        user_prompt = (
            "한글 계약 조항을 한 문장으로 요약하세요. 법률 자문 표현은 피하고 핵심만 적어주세요.\n\n"
            f"조항:\n{clause_text}\n\n요약:"
        )
        system = "You summarize Korean contract clauses concisely."
        return await self._invoke(system, user_prompt, max_new_tokens=96)

    async def classify_clause(self, clause_text: str) -> str:
        user_prompt = (
            "계약 조항을 카테고리 하나로 반환하세요. "
            "가능한 라벨: payment, termination, responsibility, penalty, confidentiality, general.\n\n"
            f"조항:\n{clause_text}\n\n라벨:"
        )
        system = "You classify contract clauses into one label."
        return await self._invoke(system, user_prompt, max_new_tokens=8)

    async def analyze_risk(self, clause_text: str) -> str:
        user_prompt = (
            "계약 조항의 잠재적 위험을 간단히 설명하세요. "
            "법률 자문이 아님을 전제로, 한국어로 짧게 위험 신호만 적어주세요.\n\n"
            f"조항:\n{clause_text}\n\n위험 설명:"
        )
        system = "You point out potential risks in contract clauses in Korean, concisely."
        return await self._invoke(system, user_prompt, max_new_tokens=128)

    async def analyze_clause(self, clause_text: str) -> dict:
        system = (
            "You are a Korean contract analysis agent. Use only the given clause text; do NOT invent amounts, dates, or names. "
            "If a field is missing, set it to null. Return JSON with fields: "
            "summary, category(one of payment, termination, responsibility, penalty, confidentiality, general), "
            "risk_score(0-100 integer), risk_level(low|medium|high), risk_reason(short Korean explanation), reasoning(short bullet style). "
            "Output JSON only."
        )
        raw = await self._invoke(system, clause_text, max_new_tokens=196)
        try:
            data = json.loads(raw)
            return {
                "summary": data.get("summary") or raw,
                "category": data.get("category") or "general",
                "risk_score": int(data.get("risk_score", 0)),
                "risk_level": data.get("risk_level") or "low",
                "risk_reason": data.get("risk_reason") or "",
                "reasoning": data.get("reasoning") or "",
            }
        except Exception:
            return {
                "summary": raw[:200],
                "category": "general",
                "risk_score": 40,
                "risk_level": "medium",
                "risk_reason": raw,
                "reasoning": "",
            }

    async def infer_contract_type(self, clauses) -> str | None:
        prompt = (
            "다음 계약 조항이 어떤 계약 유형에 속하는지 하나로 분류하세요. employment(근로/용역), lease(임대차), general 중 하나. "
            "JSON {\"type\": \"...\", \"reason\": \"...\"} 만 반환."
        )
        joined = "\n\n".join([getattr(c, "raw_text", "") for c in clauses])
        try:
            raw = await self._invoke(prompt, joined, max_new_tokens=64)
            data = json.loads(raw)
            return data.get("type")
        except Exception:
            return None

    async def suggest_improvement(self, clause_text: str) -> dict:
        prompt = (
            "다음 계약 조항을 더 공정하고 균형 있게 수정한 제안을 JSON으로 반환하세요. "
            "필드: suggestion(수정안), rationale(이유), risk_delta(정수, 위험 감소는 음수). "
        )
        try:
            raw = await self._invoke(prompt, clause_text, max_new_tokens=196)
            data = json.loads(raw)
            return {
                "suggestion": data.get("suggestion") or clause_text,
                "rationale": data.get("rationale") or "",
                "risk_delta": int(data.get("risk_delta", 0)),
            }
        except Exception:
            return {"suggestion": clause_text, "rationale": "", "risk_delta": 0}
