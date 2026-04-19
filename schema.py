from pydantic import BaseModel, EmailStr
from fastapi_mail import MessageType
from typing import Optional

class CustomMessageSchema(BaseModel):
    recipients: list[EmailStr]
    subject: str
    subtype: MessageType = MessageType.html
    body: str | None = None

class CustomConnectionConfig(BaseModel):
    MAIL_USERNAME: str
    MAIL_FROM: str
    MAIL_PASSWORD: str
    MAIL_PORT: int
    MAIL_SERVER: str
    MAIL_SSL_TLS: bool
    MAIL_STARTTLS: bool

class SendEmailRequest(BaseModel):
    config: CustomConnectionConfig
    message: CustomMessageSchema

