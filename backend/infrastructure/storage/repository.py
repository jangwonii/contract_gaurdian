from __future__ import annotations

from pathlib import Path
from typing import Dict, Optional

from fastapi import UploadFile

from backend.domain.models import AnalysisResult, Document


class InMemoryRepository:
    """Simple repository that stores metadata in memory and files on disk."""

    def __init__(self, storage_dir: Path) -> None:
        self.storage_dir = storage_dir
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self.documents: Dict[str, Document] = {}
        self.results: Dict[str, AnalysisResult] = {}

    async def store_upload(self, document_id: str, upload_file: UploadFile) -> Document:
        target_path = self.storage_dir / f"{document_id}_{upload_file.filename}"
        target_path.write_bytes(await upload_file.read())
        document = Document(
            id=document_id,
            filename=upload_file.filename,
            content_type=upload_file.content_type,
            stored_path=str(target_path),
        )
        self.documents[document_id] = document
        return document

    def save_document_text(self, document_id: str, text: str) -> None:
        document = self.documents.get(document_id)
        if document:
            document.text = text
            self.documents[document_id] = document

    def get_document(self, document_id: str) -> Optional[Document]:
        return self.documents.get(document_id)

    def save_analysis_result(self, result: AnalysisResult) -> None:
        self.results[result.document_id] = result

    def get_analysis_result(self, document_id: str) -> Optional[AnalysisResult]:
        return self.results.get(document_id)
