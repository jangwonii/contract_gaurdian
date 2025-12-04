from __future__ import annotations

import uuid
from pathlib import Path
from typing import Optional

from fastapi import HTTPException, UploadFile

from backend.application.clause_extractor import ClauseExtractor
from backend.application.llm_agent import LLMAgent
from backend.application.ocr_service import OCRService
from backend.application.risk_analyzer import RiskAnalyzer
from backend.domain.models import AnalysisResult, Document, DocumentStatus
from backend.infrastructure.storage.repository import InMemoryRepository


class AnalysisFacade:
    """Single entry point for the end-to-end analysis pipeline."""

    def __init__(
        self,
        repository: InMemoryRepository,
        ocr_service: OCRService,
        clause_extractor: ClauseExtractor,
        llm_agent: LLMAgent,
        risk_analyzer: RiskAnalyzer,
    ) -> None:
        self.repository = repository
        self.ocr_service = ocr_service
        self.clause_extractor = clause_extractor
        self.llm_agent = llm_agent
        self.risk_analyzer = risk_analyzer

    async def register_document(self, upload_file: UploadFile) -> Document:
        document_id = str(uuid.uuid4())
        document = await self.repository.store_upload(document_id, upload_file)
        return document

    async def analyze(self, document_id: str, contract_type: str = "general") -> AnalysisResult:
        document = self.repository.get_document(document_id)
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")
        if not document.stored_path:
            raise HTTPException(status_code=400, detail="Document file missing on disk")

        self.repository.save_status(DocumentStatus(document_id=document_id, stage="extract", progress=10, message="문서 텍스트 추출 중"))
        text = await self.ocr_service.extract_text(Path(document.stored_path), document.content_type)
        self.repository.save_document_text(document.id, text)

        self.repository.save_status(DocumentStatus(document_id=document_id, stage="split", progress=30, message="조항 구조 파악 중"))
        clauses = self.clause_extractor.build_clauses(text)
        self.repository.save_status(DocumentStatus(document_id=document_id, stage="llm", progress=55, message="위험 패턴 스캔 중"))
        clauses, risk_data = await self.llm_agent.annotate(clauses)

        # Self-query for contract type if not provided
        auto_type = await self.llm_agent.infer_contract_type(clauses) or contract_type
        chosen_type = contract_type if contract_type != "general" else (auto_type or "general")

        self.repository.save_status(DocumentStatus(document_id=document_id, stage="risk", progress=75, message="법적 관점에서 문제 조항 평가 중"))
        result = self.risk_analyzer.analyze(document.id, clauses, risk_data, contract_type=chosen_type)
        result.auto_contract_type = auto_type

        self.repository.save_analysis_result(result)
        self.repository.save_status(DocumentStatus(document_id=document_id, stage="done", progress=100, message="분석 완료"))
        return result

    async def get_result(self, document_id: str) -> Optional[AnalysisResult]:
        return self.repository.get_analysis_result(document_id)
