"""Worker configuration"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Worker settings"""

    # Redis
    REDIS_URL: str
    CELERY_BROKER_URL: str

    # Supabase
    SUPABASE_URL: str
    SUPABASE_KEY: str

    # Docker
    DOCKER_HOST: str = "unix:///var/run/docker.sock"

    # Sentry
    SENTRY_DSN: str | None = None

    # Environment
    ENVIRONMENT: str = "development"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
    )


settings = Settings()

