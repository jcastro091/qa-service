from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Optional
import os

class Settings(BaseSettings):
    MESSAGES_API_URL: str = Field(
        default=os.getenv(
            "MESSAGES_API_URL",
            "https://november7-730026606190.europe-west1.run.app/messages",
        )
    )
    CACHE_TTL_SECONDS: int = Field(default=int(os.getenv("CACHE_TTL_SECONDS", "900")))
    EMBEDDINGS_MODE: str = Field(default=os.getenv("EMBEDDINGS_MODE", "off"))
    OPENAI_API_KEY: Optional[str] = Field(default=os.getenv("OPENAI_API_KEY"))
    PORT: int = Field(default=int(os.getenv("PORT", "8080")))

settings = Settings()
