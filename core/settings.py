from pydantic import BaseModel, EmailStr, Field
from core import get_env


class Settings(BaseModel):

    # APP
    APP_NAME: str = "Secure Email Service"
    DEBUG: bool = get_env("DEBUG", "False") == "True"


    # SMTP CONFIG
    SMTP_HOST: str = get_env("SMTP_HOST", required=True)
    SMTP_PORT: int = int(get_env("SMTP_PORT", 587))
    SMTP_USER: str = get_env("SMTP_USER", required=True)
    SMTP_PASS: str = get_env("SMTP_PASS", required=True)
    FROM_EMAIL: EmailStr = get_env("FROM_EMAIL", required=True)

    # SECURITY
    API_SECRET_KEY: str = get_env("API_SECRET_KEY", required=True)

    # RATE LIMIT
    RATE_LIMIT_MAX: int = int(get_env("RATE_LIMIT_MAX", 5))
    RATE_LIMIT_WINDOW: int = int(get_env("RATE_LIMIT_WINDOW", 60))


    # OPTIONAL (Future Scaling)
    REDIS_URL: str | None = get_env("REDIS_URL", None)


    # DOMAIN PROTECTION
    ALLOWED_DOMAINS: list[str] = Field(
        default_factory=lambda: get_env("ALLOWED_DOMAINS", "").split(",")
        if get_env("ALLOWED_DOMAINS")
        else []
    )


# Singleton instance
settings = Settings()