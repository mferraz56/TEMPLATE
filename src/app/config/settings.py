try:
    # Prefer the standalone pydantic-settings package (Pydantic v2+)
    from pydantic_settings import BaseSettings as _BaseSettings  # type: ignore
    PYDANTIC_SETTINGS = True
except Exception:
    # Fallback to the legacy location (pydantic.BaseSettings)
    from pydantic import BaseSettings as _BaseSettings  # type: ignore
    PYDANTIC_SETTINGS = False

from pydantic import Field


if PYDANTIC_SETTINGS:
    class Settings(_BaseSettings):
        env: str = Field("development", env="ENV")
        force_https: bool = Field(False, env="FORCE_HTTPS")
        session_cookie_secure: bool = Field(False, env="SESSION_COOKIE_SECURE")
        database_url: str = Field(
            "postgresql+psycopg://postgres:postgres@db:5432/template_db",
            env="DATABASE_URL",
        )
        redis_url: str = Field("redis://redis:6379/0", env="REDIS_URL")
        celery_broker_url: str = Field("redis://redis:6379/1", env="CELERY_BROKER_URL")
        secret_key: str = Field("changeme", env="SECRET_KEY")

        # Pydantic v2 / pydantic-settings configuration
        model_config = {
            "env_file": ".env",
            "env_file_encoding": "utf-8",
            "extra": "ignore",
        }

else:
    class Settings(_BaseSettings):
        env: str = Field("development", env="ENV")
        force_https: bool = Field(False, env="FORCE_HTTPS")
        session_cookie_secure: bool = Field(False, env="SESSION_COOKIE_SECURE")
        database_url: str = Field(
            "postgresql+psycopg://postgres:postgres@db:5432/template_db",
            env="DATABASE_URL",
        )
        redis_url: str = Field("redis://redis:6379/0", env="REDIS_URL")
        celery_broker_url: str = Field("redis://redis:6379/1", env="CELERY_BROKER_URL")
        secret_key: str = Field("changeme", env="SECRET_KEY")

        class Config:  # type: ignore
            env_file = ".env"
            env_file_encoding = "utf-8"
            extra = "ignore"


settings = Settings()
