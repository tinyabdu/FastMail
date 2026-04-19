from fastapi_mail import FastMail, MessageSchema, MessageType, ConnectionConfig
from pydantic import EmailStr, SecretStr
from core.settings import settings

_config = ConnectionConfig(
    MAIL_USERNAME=settings.MAIL_USERNAME,
    MAIL_FROM=str(settings.MAIL_FROM),
    MAIL_PASSWORD=SecretStr(settings.MAIL_PASSWORD),
    MAIL_PORT=settings.MAIL_PORT,
    MAIL_SERVER=settings.MAIL_SERVER,
    MAIL_SSL_TLS=True,
    MAIL_STARTTLS=False
)


class Mailer:
    """Simple wrapper around FastMail for use in background tasks."""

    async def send_email(self, to: str, subject: str, html: str) -> None:
        message = MessageSchema(
            subject=subject,
            recipients=[to],
            subtype=MessageType.html,
            body=html,
        )
        try:
            await FastMail(_config).send_message(message)
        except Exception as e:
            print(f"[MAILER ERROR]: {e}")
