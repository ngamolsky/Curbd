import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Curbd Post Generator"
    # OpenAI settings
    OPENAI_API_KEY: str | None = os.getenv("OPENAI_API_KEY")

    API_KEY: str | None = os.getenv("API_KEY")

    # Temporary file storage
    TEMP_FILE_DIR: str = "/tmp"

    # Add other configuration variables as needed

    class Config:
        env_file = ".env"


settings = Settings()
