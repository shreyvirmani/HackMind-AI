
from dotenv import load_dotenv
from pydantic_settings import BaseSettings

# Load environment variables from .env
load_dotenv()


class Settings(BaseSettings):

    GOOGLE_API_KEY: str

    PRIMARY_MODEL: str
    SECONDARY_MODEL: str
    TERTIARY_MODEL: str

    MAX_RETRIES: int = 3
    REQUEST_DELAY: int = 2

    CACHE_ENABLED: bool = True

    LOG_LEVEL: str = "INFO"

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