from fastapi import APIRouter, BackgroundTasks, Depends, Request, Header, HTTPException
from pydantic import EmailStr
from fastapi.responses import HTMLResponse
from core import settings
from services import Mailer
from workers import MailService
from services import render_template
from schema import SendEmailRequest
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig

router = APIRouter()
mailer = Mailer()


def verify_api_key(x_api_key: str = Header(..., alias="X-API-Key")) -> str:
    if x_api_key != settings.API_SECRET_KEY:
        raise HTTPException(status_code=401, detail="Invalid API key")
    return x_api_key


from fastapi_mail import MessageType

@router.post("/send")
async def send(payload: SendEmailRequest, _: str = Depends(verify_api_key)):
    config = ConnectionConfig(**payload.config.model_dump())
    
    message_data = payload.message.model_dump()
    message_data["subtype"] = MessageType.html if message_data["subtype"] == "html" else MessageType.plain
    
    message = MessageSchema(**message_data)
    fm = FastMail(config)
    await fm.send_message(message)

    return {
        "message": "Email has been sent",
        "recipients": payload.message.recipients
    }

@router.post("/sendg")
async def send(payload: SendEmailRequest):
    return payload




@router.post("/send-otp")
async def send_welcome(email: EmailStr, otp: str, background_tasks: BackgroundTasks):
    html = await MailService.otp_login(email, otp)
    background_tasks.add_task(mailer.send_email, to=email, subject="Your OTP Code", html=html)
    return {"message": "OTP email has been sent", "email": email}

