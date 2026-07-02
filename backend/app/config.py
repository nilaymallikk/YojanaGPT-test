from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "YojanaGPT"
    database_url: str = "postgresql+psycopg2://yojana:yojana_dev_password@localhost:5432/yojana"
    qdrant_url: str = "http://localhost:6333"
    qdrant_collection: str = "yojana_chunks"
    openrouter_api_key: str = ""
    openrouter_model: str = "Qwen/Qwen3-Next-80B-A3B-Instruct"
    embedding_model: str = "BAAI/bge-small-en-v1.5"
    reranker_model: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"
    allowed_origins: str = Field(default="http://localhost:3000")
    llm_cache_ttl_seconds: int = 60 * 60 * 24

    @property
    def origins(self) -> list[str]:
        return [origin.strip() for origin in self.allowed_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
