from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class Document(BaseModel):
    id: str
    filename: str
    content_type: Optional[str] = None
    stored_path: Optional[str] = None
    text: Optional[str] = None


class ClauseRisk(BaseModel):
    score: int = Field(0, ge=0, le=100)
    level: str = "low"
    explanation: str = ""


class Clause(BaseModel):
    id: str
    raw_text: str
    summary: Optional[str] = None
    category: Optional[str] = None
    risk: ClauseRisk = Field(default_factory=ClauseRisk)
    reasoning: Optional[str] = None


class DocumentStatus(BaseModel):
    document_id: str
    stage: str = "idle"
    progress: int = 0  # 0-100
    message: str = ""


class AnalysisResult(BaseModel):
    document_id: str
    clauses: List[Clause] = Field(default_factory=list)
    overall_risk_score: float = 0.0
    contract_type: str = "general"
    auto_contract_type: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

    @property
    def overall_risk_level(self) -> str:
        if self.overall_risk_score >= 75:
            return "high"
        if self.overall_risk_score >= 50:
            return "medium"
        return "low"


class User(BaseModel):
    id: str
    display_name: str
    email: Optional[str] = None
