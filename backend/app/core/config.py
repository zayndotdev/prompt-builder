import os
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List

# Resolve path to backend/.env
BASE_DIR = Path(__file__).resolve().parent.parent.parent
ENV_PATH = BASE_DIR / ".env"

class Settings(BaseSettings):
    # Free-tier LLM API Keys
    GROQ_API_KEY: str = ""
    GEMINI_API_KEY: str = ""
    COHERE_API_KEY: str = ""
    MISTRAL_API_KEY: str = ""

    # Server configuration
    PORT: int = 8000
    HOST: str = "0.0.0.0"
    CORS_ORIGINS: str = "http://localhost:5173,http://localhost:3000,http://127.0.0.1:5173"

    # Default Models (Verified Active)
    GROQ_DEFAULT_MODEL: str = "allam-2-7b"
    GROQ_FAST_MODEL: str = "allam-2-7b"
    GEMINI_DEFAULT_MODEL: str = "gemini-3.6-flash"
    MISTRAL_DEFAULT_MODEL: str = "mistral-small-latest"
    COHERE_DEFAULT_MODEL: str = "command-r-plus-08-2024"

    model_config = SettingsConfigDict(
        env_file=str(ENV_PATH) if ENV_PATH.exists() else None,
        env_file_encoding="utf-8",
        extra="ignore"
    )

    @property
    def cors_origins_list(self) -> List[str]:
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]

settings = Settings()
