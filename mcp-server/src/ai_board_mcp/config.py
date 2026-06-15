from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    github_token: str | None = None
    github_api_base: str = "https://api.github.com"
    mcp_server_name: str = "ai-board-github"

    model_config = SettingsConfigDict(
        env_file="mcp-server/.env",
        env_file_encoding="utf-8",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
