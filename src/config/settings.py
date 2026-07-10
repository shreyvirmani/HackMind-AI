"""
Application configuration.

Loads all environment variables from the .env file
and exposes them through a single Settings object.
"""

from dotenv import load_dotenv
from pydantic_settings import BaseSettings

# Load environment variables from .env
load_dotenv()


class Settings(BaseSettings):
    """Application settings."""

    GOOGLE_API_KEY: str
    MODEL_NAME: str = "gemini-2.5-flash"

    DATABASE_URL: str

    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379

    AWS_ACCESS_KEY_ID: str = ""
    AWS_SECRET_ACCESS_KEY: str = ""
    AWS_REGION: str = "ap-south-1"
    S3_BUCKET_NAME: str = ""

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()