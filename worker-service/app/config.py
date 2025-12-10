"""
Worker Service configuration using Pydantic Settings.
"""
from pydantic_settings import BaseSettings
from functools import lru_cache
from pydantic import field_validator

class Settings(BaseSettings):
    """Worker service settings loaded from environment variables."""
    
    # Application
    APP_NAME: str = "Voice Reminder Worker Service"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # Database - use postgresql+psycopg for psycopg3
    # Credentials must be provided in .env file
    DATABASE_URL: str
    
    # Infobip API - SMS/Voice Provider
    INFOBIP_API_KEY: str = ""
    INFOBIP_BASE_URL: str = "https://jr5ryn.api.infobip.com"
    INFOBIP_FROM_NUMBER: str = ""  # Your Infobip sender ID (e.g., "YourApp" or phone number)
    
    # Mock Mode Settings
    MOCK_MODE: bool = True  # Set to True to simulate calls without real API calls
    MOCK_CALL_SUCCESS_RATE: float = 0.9  # 90% success rate for mock calls
    
    # Scheduler
    SCHEDULER_INTERVAL_SECONDS: int = 30
    
    # Webhook
    WEBHOOK_SECRET: str = ""
    WEBHOOK_URL: str = ""  # Public URL for receiving webhooks
    
    # CORS
    CORS_ORIGINS: list[str] | str = ["http://localhost:3000", "http://localhost:5173"]

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def parse_cors_origins(cls, v):
        if isinstance(v, str) and not v.startswith("["):
            return [origin.strip() for origin in v.split(",")]
        return v
    
    # Logging
    LOG_LEVEL: str = "INFO"
    
    class Config:
        env_file = "../.env"
        env_file_encoding = "utf-8"
        extra = "ignore"


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


settings = get_settings()
