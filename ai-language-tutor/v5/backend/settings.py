import os
from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Optional

class Settings(BaseSettings):
    base_url: str
    api_key: str
    model: str = Field("gemini-2.0-flash")

    supabase_url: str
    supabase_key: str

    secret_key: str = Field("supersecretkey")
    algorithm: str = Field("HS256")
    access_token_expire_minutes: int = Field(30)
    refresh_token_expire_days: int = Field(7)

    google_client_id: Optional[str] = None
    google_client_secret: Optional[str] = None
    google_redirect_uri: Optional[str] = None

    redis_url: str = Field("redis://localhost:6379/0")
    cache_ttl: int = Field(300)

    query_log_flush_interval_days: int = Field(7)

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = 'ignore'

    @property
    def query_log_flush_interval_seconds(self) -> int:
        return self.query_log_flush_interval_days * 86400

settings = Settings()
