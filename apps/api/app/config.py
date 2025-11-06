"""Application configuration"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings"""

    # Supabase
    SUPABASE_URL: str
    SUPABASE_KEY: str
    SUPABASE_JWT_SECRET: str

    # OpenAI
    OPENAI_API_KEY: str

    # Redis
    REDIS_URL: str
    CELERY_BROKER_URL: str

    # Sentry
    SENTRY_DSN: str | None = None

    # Environment
    ENVIRONMENT: str = "development"

    # CORS
    CORS_ORIGINS: list[str] = ["*"]

    # Rate limiting
    RATE_LIMIT_PER_MINUTE: int = 100
    RATE_LIMIT_LLM_PER_HOUR: int = 20

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
    )

    @property
    def is_production(self) -> bool:
        """Check if running in production"""
        return self.ENVIRONMENT == "production"


settings = Settings()

