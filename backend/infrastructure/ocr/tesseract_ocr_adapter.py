from __future__ import annotations

import asyncio
from pathlib import Path
from typing import Optional

from backend.application.ocr_service import OCRService

try:
    import easyocr  # type: ignore
except ImportError:  # pragma: no cover - optional dependency
    easyocr = None

try:
    import pdfplumber  # type: ignore
except ImportError:  # pragma: no cover - optional dependency
    pdfplumber = None

try:
    import fitz  # PyMuPDF  # type: ignore
except ImportError:  # pragma: no cover - optional dependency
    fitz = None


class TesseractOCRAdapter(OCRService):
    """OCR adapter that wraps EasyOCR; falls back to plain text when missing."""

    def __init__(self, language: str = "kor+eng", use_gpu: bool = False) -> None:
        self.language = language
        langs = [lang.strip() for lang in language.split("+") if lang.strip()]
        self.reader = easyocr.Reader(langs, gpu=use_gpu) if easyocr else None

    async def extract_text(self, file_path: Path, content_type: Optional[str] = None) -> str:
        return await asyncio.to_thread(self._extract_sync, file_path, content_type)

    def _extract_sync(self, file_path: Path, content_type: Optional[str]) -> str:
        # Prefer direct PDF text extraction when possible
        if content_type and "pdf" in content_type.lower():
            text = self._extract_pdf_text(file_path)
            if text:
                return text
        # Use EasyOCR for image-based OCR
        if self.reader is None:
            try:
                return file_path.read_text(encoding="utf-8")
            except Exception:
                return "OCR unavailable: install easyocr, torch, and pillow."

        try:
            lines = self.reader.readtext(str(file_path), detail=0, paragraph=True)
            return "\n".join(lines).strip()
        except Exception:
            # As a last resort, attempt simple file read for text-like inputs
            try:
                return file_path.read_text(encoding="utf-8")
            except Exception:
                return "OCR failed: EasyOCR could not process the file."

    def _extract_pdf_text(self, file_path: Path) -> str:
        # Prefer PyMuPDF for speed and layout-friendly extraction
        if fitz is not None:
            try:
                with fitz.open(str(file_path)) as doc:
                    pages = [page.get_text("text") or "" for page in doc]
                text = "\n\n".join(pages).strip()
                if text:
                    return text
            except Exception:
                pass

        if pdfplumber is not None:
            try:
                with pdfplumber.open(str(file_path)) as pdf:
                    pages = [page.extract_text() or "" for page in pdf.pages]
                return "\n\n".join(pages).strip()
            except Exception:
                pass

        return ""
