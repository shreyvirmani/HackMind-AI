from dotenv import load_dotenv
from pydantic_settings import BaseSettings

# Load environment variables from .env
load_dotenv()


class Settings(BaseSettings):

    # ---- Provider API keys (all genuinely free tiers) ----
    # GOOGLE_API_KEY_2 is a SECOND Gemini key from a *different*
    # Google AI Studio project. Gemini's free quota is tracked per
    # project/key, so a second free key effectively doubles the free
    # request budget instead of costing anything.
    # GROQ_API_KEY is Groq's free, no-card-required tier (open-source
    # models only: Llama, GPT-OSS, etc). It's a genuinely different
    # provider/infrastructure, so a Google-side outage doesn't take it
    # down too.
    # OPENAI_API_KEY / ANTHROPIC_API_KEY are OPTIONAL and NOT free --
    # both require a paid balance to use anything beyond a token
    # trial. Leave them blank to stay 100% on free tiers; the chain
    # simply skips any provider whose key isn't set.
    GOOGLE_API_KEY: str
    GOOGLE_API_KEY_2: str = ""
    GROQ_API_KEY: str = ""
    OPENAI_API_KEY: str = ""
    ANTHROPIC_API_KEY: str = ""

    # ---- Fallback chain (in this order) ----
    # Gemini key 1 -> Gemini key 2 -> Groq -> OpenAI -> Claude.
    # Each provider gets its own rate limiter + circuit breaker, so a
    # 429 on one immediately rolls over to the next without wasting
    # requests on the one that's already exhausted.
    PRIMARY_MODEL: str = "gemini-2.5-flash"       # Gemini key 1
    SECONDARY_MODEL: str = "gemini-2.5-flash"     # Gemini key 2
    GROQ_MODEL: str = "openai/gpt-oss-120b"  # llama-3.3-70b-versatile decommissioned Aug 16, 2026
    TERTIARY_MODEL: str = "gpt-4o-mini"           # only used if OPENAI_API_KEY set
    QUATERNARY_MODEL: str = "claude-sonnet-4-6"   # only used if ANTHROPIC_API_KEY set

    MAX_RETRIES: int = 3
    REQUEST_DELAY: int = 2

    CACHE_ENABLED: bool = True

    # ---- Payments (Razorpay) ----
    # Optional: leave blank in dev. Payment routes return a clear
    # error instead of crashing if these aren't configured.
    RAZORPAY_KEY_ID: str = ""
    RAZORPAY_KEY_SECRET: str = ""
    RAZORPAY_WEBHOOK_SECRET: str = ""
    PRO_PLAN_PRICE_INR: int = 99  # rupees; charged as paise (x100) to Razorpay
    MAX_PLAN_PRICE_INR: int = 299  # rupees; charged as paise (x100) to Razorpay

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