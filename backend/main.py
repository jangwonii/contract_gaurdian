from __future__ import annotations

import logging
from pathlib import Path

from fastapi import Body, FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from fastapi.responses import Response, StreamingResponse

from backend.application.analysis_facade import AnalysisFacade
from backend.application.clause_extractor import ClauseExtractor
from backend.application.llm_agent import LLMAgent
from backend.application.risk_analyzer import RiskAnalyzer
from backend.application.report_builder import render_report_html, render_report_md
from backend.config import Settings
from backend.infrastructure.llm.dummy_provider import DummyLLMProvider
from backend.infrastructure.llm.openai_provider import OpenAILLMProvider
from backend.infrastructure.ocr.tesseract_ocr_adapter import TesseractOCRAdapter
from backend.infrastructure.storage.repository import InMemoryRepository

logger = logging.getLogger(__name__)

settings = Settings()
Path(settings.storage_path).mkdir(parents=True, exist_ok=True)

repository = InMemoryRepository(settings.storage_path)
ocr_service = TesseractOCRAdapter(language=settings.ocr_language)
clause_extractor = ClauseExtractor()
provider_choice = settings.llm_provider.lower().strip()
provider: object

if provider_choice == "openai":
    provider = OpenAILLMProvider(api_key=settings.openai_api_key, model=settings.openai_model)
    logger.info("Using OpenAI LLM provider with model %s", settings.openai_model)
elif provider_choice in {"hf", "huggingface"}:
    try:
        from backend.infrastructure.llm.hf_provider import HuggingFaceLLMProvider

        provider = HuggingFaceLLMProvider(
            model=settings.hf_model,
            token=settings.hf_token,
            api_url=settings.hf_api_url,
        )
        logger.info("Using Hugging Face provider with model %s", settings.hf_model)
    except Exception as exc:  # pragma: no cover - fallback path
        logger.warning("Hugging Face provider init failed, falling back to DummyLLMProvider: %s", exc)
        provider = DummyLLMProvider()
else:
    provider = DummyLLMProvider()
    logger.info("Using Dummy LLM provider")

llm_agent = LLMAgent(provider)
risk_analyzer = RiskAnalyzer()

facade = AnalysisFacade(
    repository=repository,
    ocr_service=ocr_service,
    clause_extractor=clause_extractor,
    llm_agent=llm_agent,
    risk_analyzer=risk_analyzer,
)

app = FastAPI(title="Contract Guardian API", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health_check():
    return {"status": "ok"}


@app.post("/api/documents")
async def upload_document(file: UploadFile = File(...)):
    document = await facade.register_document(file)
    return {"documentId": document.id, "filename": document.filename}


class AnalyzePayload(BaseModel):
    contract_type: str = "general"


@app.post("/api/documents/{document_id}/analyze")
async def analyze_document(document_id: str, payload: AnalyzePayload = Body(default=AnalyzePayload())):
    result = await facade.analyze(document_id, contract_type=payload.contract_type)
    return result


@app.get("/api/documents/{document_id}/result")
async def get_result(document_id: str):
    result = await facade.get_result(document_id)
    if not result:
        raise HTTPException(status_code=404, detail="Result not found")
    return result


@app.get("/api/documents/{document_id}/report")
async def get_report(document_id: str, format: str = "pdf"):
    result = await facade.get_result(document_id)
    if not result:
        raise HTTPException(status_code=404, detail="Result not found")

    fmt = format.lower()
    md = render_report_md(result)
    if fmt == "md":
        return Response(content=md, media_type="text/markdown", headers={"Content-Disposition": "attachment; filename=report.md"})

    # Try to render PDF, otherwise fall back to markdown
    try:
        from weasyprint import HTML  # type: ignore

        html = render_report_html(result)
        pdf_bytes = HTML(string=html).write_pdf()
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={"Content-Disposition": "attachment; filename=report.pdf"},
        )
    except Exception:
        return Response(
            content=md,
            media_type="text/markdown",
            headers={"Content-Disposition": "attachment; filename=report.md"},
        )
