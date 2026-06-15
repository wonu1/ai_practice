from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str
    jwt_secret_key: str
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60
    openai_api_key: str | None = None
    ai_provider: str = "openai"
    ai_chat_model: str = "gpt-5.4-mini"
    ai_embedding_model: str = "text-embedding-3-small"
    ai_embedding_dimension: int = 1536
    langsmith_tracing: bool = False
    langsmith_api_key: str | None = None
    langsmith_project: str = "ai-board-local"
    mcp_server_command: str | None = None
    mcp_server_cwd: str = "mcp-server"

    model_config = SettingsConfigDict(
        env_file="backend/.env",
        env_file_encoding="utf-8",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
