"""Configuration management."""

from pathlib import Path
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings."""

    # AI - LLM 配置（当前使用阿里云百炼）
    llm_api_key: str = ""
    llm_base_url: str = "https://dashscope.aliyuncs.com/compatible-mode/v1"
    chat_model: str = "qwen-plus"
    embedding_model: str = "text-embedding-v3"

    # Server
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    cors_origins: str = "http://localhost:5173,http://localhost:3000"

    # Security
    max_upload_size: int = 50 * 1024 * 1024  # 50MB

    # Analysis
    max_chapter_content_length: int = 15000
    max_interaction_records: int = 30
    analysis_concurrency: int = 5

    # Paths
    data_dir: Path = Path("../../data")

    @property
    def books_dir(self) -> Path:
        return self.data_dir / "books"

    @property
    def analysis_dir(self) -> Path:
        return self.data_dir / "analysis"

    @property
    def vector_store_dir(self) -> Path:
        return self.data_dir / "vector_store"

    @property
    def cors_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",")]

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
