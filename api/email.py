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

@router.post("/send-welcome")
async def send_welcome(email: EmailStr, username: str, background_tasks: BackgroundTasks):
    html = await MailService.welcome(email, username)
    background_tasks.add_task(mailer.send_email, to=email, subject="Welcome to our service!", html=html)
    return {"message": "Welcome email has been sent", "email": email}


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

@router.post("/send-delete")
async def send_delete_notification(email: EmailStr, background_tasks: BackgroundTasks):
    html = await MailService.account_deleted(email)
    background_tasks.add_task(mailer.send_email, to=email, subject="Your OTP Code", html=html)
    return {"message": "OTP email has been sent", "email": email}


@router.post("/send-payment")
async def send_payment_notification(email: EmailStr, amount: str, currency: str, transaction_id: str, description: str, background_tasks: BackgroundTasks):
    html = await MailService.payment_successful(email, amount, currency, transaction_id, description)
    background_tasks.add_task(mailer.send_email, to=email, subject=f"Payment receipt – {amount} {currency}", html=html)
    return {"message": "Payment email has been sent", "email": email}

@router.post("/send-subscription-upgrade")
async def send_subscription_notification(email: EmailStr, plan_name: str, next_billing_date: str, background_tasks: BackgroundTasks):
    html = await MailService.subscription_upgraded(email, "Basic Plan", plan_name, next_billing_date)
    background_tasks.add_task(mailer.send_email, to=email, subject=f"Upgraded to {plan_name}", html=html)
    return {"message": "Subscription email has been sent", "email": email}

@router.post("/send-payment-failed")
async def send_payment_failed_notification(email: EmailStr, amount: str, currency: str, transaction_id: str, description: str, background_tasks: BackgroundTasks):
    html = await MailService.payment_failed(email, amount, currency, transaction_id, description)
    background_tasks.add_task(mailer.send_email, to=email, subject=f"Payment failed – {amount} {currency}", html=html)
    return {"message": "Payment failure email has been sent", "email": email}

@router.post("/send-subscription-upgrade")
async def send_subscription_upgrade_notification(email: EmailStr, old_plan: str, new_plan: str, background_tasks: BackgroundTasks):
        html = await MailService.subscription_upgraded(email, old_plan, new_plan)
        background_tasks.add_task(mailer.send_email, to=email, subject="Your subscription has been upgraded", html=html)
        return {"message": "Subscription upgrade email has been sent", "email": email}

@router.post("/send-subscription-cancel")
async def send_subscription_cancellation_notification(email: EmailStr, plan_name: str, background_tasks: BackgroundTasks):
        html = await MailService.subscription_cancelled(email, plan_name)
        background_tasks.add_task(mailer.send_email, to=email, subject="Your subscription has been cancelled", html=html)
        return {"message": "Subscription cancellation email has been sent", "email": email}

@router.post("/send-login-alert")
async def send_login_alert(email: EmailStr, ip_address: str, device: str, location: str, background_tasks: BackgroundTasks):
    html = await MailService.new_login_alert(email, ip_address, device, location)
    background_tasks.add_task(mailer.send_email, to=email, subject="New Login Detected", html=html)
    return {"message": "Login alert email has been sent", "email": email}

@router.post("/send-congratulations")
async def send_congratulations(email: EmailStr, achievement: str, background_tasks: BackgroundTasks):
    html = await MailService.congratulations(email, achievement)
    background_tasks.add_task(mailer.send_email, to=email, subject=f"You unlocked: {achievement}", html=html)
    return {"message": "Congratulations email has been sent", "email": email}   

@router.post("/send-report")
async def send_report(email: EmailStr, report_data: dict, background_tasks: BackgroundTasks):
    html = await MailService.report_received(email, report_data)
    background_tasks.add_task(mailer.send_email, to=email, subject="Your requested report", html=html)
    return {"message": "Report email has been sent", "email": email}

@router.post("/send-account-banned")
async def send_account_banned_notification(email: EmailStr, reason: str, background_tasks: BackgroundTasks):
    html = await MailService.account_banned(email, reason)
    background_tasks.add_task(mailer.send_email, to=email, subject="Your account has been banned", html=html)
    return {"message": "Account ban email has been sent", "email": email}