from fastapi import APIRouter, BackgroundTasks, Depends, Request
from fastapi.responses import HTMLResponse
from core import settings
from services.mailer import Mailer
from services.templates import render_template
from schema import SendEmailRequest
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig

router = APIRouter()
mailer = Mailer()


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/send/email")
async def send(payload: SendEmailRequest, dependencies=[Depends(settings.verify_api_key)]):
    config = ConnectionConfig(**payload.config.model_dump())
    message = MessageSchema(**payload.message.model_dump())

    fm = FastMail(config)
    await fm.send_message(message)

    return {
        "message": "Email has been sent",
        "recipients": payload.message.recipients
    }



@router.post("/send-otp")
async def send_otp(email: str, name: str, otp: str, background_tasks: BackgroundTasks):

    html = render_template("otp.html", name=name, otp=otp)

    background_tasks.add_task(
        mailer.send_email,
        email,
        "Your OTP Code",
        html
    )

    return {"message": "OTP sent successfully"}