import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache
from dotenv import load_dotenv

load_dotenv()


class Settings(BaseSettings):
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Curbd Post Generator"
    OPENAI_API_KEY: str | None = os.getenv("OPENAI_API_KEY")
    API_KEY: str | None = os.getenv("API_KEY")
    FRONTEND_URL: str = os.getenv("FRONTEND_URL") or ""

    # Temporary file storage
    TEMP_FILE_DIR: str = "/tmp"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )


@lru_cache()
def get_settings():
    return Settings()
