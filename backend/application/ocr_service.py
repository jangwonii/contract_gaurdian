from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional


class OCRService(ABC):
    """Abstract OCR service that extracts text from a file."""

    @abstractmethod
    async def extract_text(self, file_path: Path, content_type: Optional[str] = None) -> str:
        raise NotImplementedError
