from __future__ import annotations

from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    storage_path: Path = Path("data/documents")
    ocr_language: str = "kor+eng"
    openai_model: str = "gpt-4o-mini"
    openai_api_key: str | None = None
    llm_provider: str = "dummy"  # options: dummy, openai, hf
    hf_model: str = "meta-llama/Meta-Llama-3-8B-Instruct"
    hf_token: str | None = None
    hf_api_url: str | None = None
    model_config = SettingsConfigDict(env_file=(".env", "config/.env"), extra="ignore")
