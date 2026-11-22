import os
from typing import List, Union
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PROJECT_NAME: str = "PreBurn API"
    VERSION: str = "1.0.0"
    DESCRIPTION: str = "A Predictive Early-Warning System for Stubble Burning in North India"
    API_V1_PREFIX: str = "/api/v1"
    ENVIRONMENT: str = "development"

    # Database Configuration (PostgreSQL / SQLite fallback)
    DATABASE_URL: str = "sqlite:///./preburn.db"

    # CORS Configuration
    CORS_ORIGINS: Union[List[str], str] = ["*"]

    # SMS Configuration (Demo mode default; provider configurable)
    SMS_PROVIDER: str = "demo"  # "demo", "twilio", "fast2sms"
    SMS_ENABLED: bool = True
    SMS_DEFAULT_OFFICER_PHONE: str = "+919876543210"
    TWILIO_ACCOUNT_SID: str = ""
    TWILIO_AUTH_TOKEN: str = ""
    TWILIO_FROM_PHONE: str = ""
    FAST2SMS_API_KEY: str = ""

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v):
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, str) and v.startswith("["):
            import json
            try:
                return json.loads(v)
            except Exception:
                return ["*"]
        return v

    model_config = SettingsConfigDict(
        env_file=os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env"),
        env_file_encoding="utf-8",
        extra="ignore"
    )


settings = Settings()
