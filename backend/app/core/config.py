from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_env: str = Field(default="dev", validation_alias="APP_ENV")
    project_name: str = Field(default="KPI-SOC", validation_alias="PROJECT_NAME")
    version: str = "0.1.0"
    api_v1_prefix: str = "/api/v1"
    database_url: str = Field(
        default="postgresql+psycopg://kpisoc:kpisoc@localhost:5432/kpisoc",
        validation_alias="DATABASE_URL",
    )
    backend_cors_origins_raw: str = Field(
        default="http://localhost:5173,http://127.0.0.1:5173",
        validation_alias="BACKEND_CORS_ORIGINS",
    )

    @property
    def backend_cors_origins(self) -> list[str]:
        return [origin.strip() for origin in self.backend_cors_origins_raw.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
