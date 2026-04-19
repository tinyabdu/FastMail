from pydantic import BaseModel, EmailStr, Field
from core.config import get_env


class Settings(BaseModel):

    # APP
    APP_NAME: str = "Secure Email Service"
    DEBUG: bool = get_env("DEBUG", "False") == "True"

    # SMTP CONFIG
    MAIL_SERVER: str = get_env("SMTP_HOST", required=True)
    MAIL_PORT: int = int(get_env("SMTP_PORT", 587))
    MAIL_USERNAME: str = get_env("SMTP_USER", required=True)
    MAIL_PASSWORD: str = get_env("SMTP_PASS", required=True)
    MAIL_FROM: EmailStr = get_env("FROM_EMAIL", required=True)

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

    def verify_api_key(self, key: str) -> bool:
        return key == self.API_SECRET_KEY


# Singleton instance
settings = Settings()
