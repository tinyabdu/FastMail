import asyncio
from fastapi_mail import FastMail, MessageType, MessageSchema, ConnectionConfig
from pydantic import SecretStr, EmailStr
from utils.rate_limiter import rate_limit
from core.settings import settings

_config = ConnectionConfig(
    MAIL_USERNAME=settings.MAIL_USERNAME,
    MAIL_FROM=str(settings.MAIL_FROM),
    MAIL_PASSWORD=SecretStr(settings.MAIL_PASSWORD),
    MAIL_PORT=settings.MAIL_PORT,
    MAIL_SERVER=settings.MAIL_SERVER,
    MAIL_SSL_TLS=False,
    MAIL_STARTTLS=True,
)


# Shared helpers

def _base_template(title: str, accent: str, body_html: str) -> str:
    """Wrap any body block in a consistent branded shell."""
    return f"""
    <html>
    <body style="font-family:Arial,sans-serif;background:#f4f4f4;padding:30px 0;">
      <div style="max-width:600px;margin:auto;background:#fff;border-radius:10px;
                  box-shadow:0 2px 12px rgba(0,0,0,.1);overflow:hidden;">
        <div style="background:{accent};padding:20px 30px;">
          <h2 style="color:#fff;margin:0;font-size:22px;">{title}</h2>
        </div>
        <div style="padding:30px;">
          {body_html}
        </div>
        <div style="background:#f9f9f9;padding:15px 30px;border-top:1px solid #eee;">
          <p style="font-size:12px;color:#aaa;margin:0;text-align:center;">
            &copy; 2026 Tsira &mdash; All rights reserved.<br>
            If you did not request this email, please ignore it or contact support.
          </p>
        </div>
      </div>
    </body>
    </html>
    """


async def _send(email_to: EmailStr, subject: str, html: str, ip: str = "global") -> None:
    if not rate_limit(ip):
        raise Exception("Too many email requests")

    message = MessageSchema(
        subject=subject,
        recipients=[email_to],
        subtype=MessageType.html,
        body=html,
    )

    try:
        await asyncio.wait_for(
            FastMail(_config).send_message(message),
            timeout=10
        )
    except Exception as e:
        print("[EMAIL ERROR]:", str(e))


# Convenience functions (exported via __init__)

async def send_email(email_to: str, subject: str, body: str, ip: str = "global") -> None:
    """Send a plain HTML email."""
    await _send(email_to, subject, body, ip)


async def send_otp(email_to: str, otp_code: str, ip: str = "global") -> None:
    """Send an OTP verification code."""
    await MailService.verify_account(email_to, otp_code)


async def send_bulk_email(recipients: list[str], subject: str, body: str) -> None:
    """Send the same email to multiple recipients (sequentially)."""
    for recipient in recipients:
        await _send(recipient, subject, body)


async def send_template_email(
    email_to: str, template_name: str, context: dict, subject: str
) -> None:
    """Render a template and send it."""
    from services.templates import render_template
    html = render_template(template_name, **context)
    await _send(email_to, subject, html)


async def send_scheduled_email(
    email_to: str, subject: str, body: str, delay_seconds: float = 0
) -> None:
    """Send an email after an optional delay."""
    if delay_seconds > 0:
        await asyncio.sleep(delay_seconds)
    await _send(email_to, subject, body)


# Mail Service

class MailService:

    @staticmethod
    async def verify_account(email_to: EmailStr, otp_code: str) -> None:
        body = f"""
        <p style="font-size:16px;color:#333;">Hi there,</p>
        <p style="font-size:16px;color:#333;">
          Thanks for joining <strong>Tsira</strong>! Use the code below to verify your account.
          It expires in <strong>10 minutes</strong>.
        </p>
        <div style="text-align:center;margin:30px 0;">
          <span style="font-size:36px;font-weight:bold;letter-spacing:8px;
                       border:2px dashed #4CAF50;padding:12px 24px;
                       border-radius:8px;color:#222;">{otp_code}</span>
        </div>
        """
        html = _base_template("Verify Your Account", "#4CAF50", body)
        # await _send(email_to, "Your Tsira verification code", html)
        return html

    @staticmethod
    async def otp_login(email_to: EmailStr, otp_code: str) -> None:
        body = f"""
        <p style="font-size:16px;color:#333;">Hi,</p>
        <p style="font-size:16px;color:#333;">
          Here is your one-time login code for <strong>Tsira</strong>.
          It expires in <strong>10 minutes</strong>.
        </p>
        <div style="text-align:center;margin:30px 0;">
          <span style="font-size:36px;font-weight:bold;letter-spacing:8px;
                       border:2px dashed #2196F3;padding:12px 24px;
                       border-radius:8px;color:#222;">{otp_code}</span>
        </div>
        <p style="font-size:14px;color:#888;">
          If you did not try to log in, please change your password immediately.
        </p>
        """
        html = _base_template("One-Time Login Code", "#2196F3", body)
        # await _send(email_to, "Your Tsira login code", html)
        return html

    @staticmethod
    async def reset_password(email_to: EmailStr, reset_link: str) -> None:
        body = f"""
        <p style="font-size:16px;color:#333;">Hello,</p>
        <p style="font-size:16px;color:#333;">
          We received a request to reset your password. Click the button below —
          the link expires in <strong>30 minutes</strong>.
        </p>
        <div style="text-align:center;margin:30px 0;">
          <a href="{reset_link}"
             style="background:#FF5733;color:#fff;padding:14px 28px;
                    text-decoration:none;border-radius:6px;font-size:16px;
                    font-weight:bold;">Reset My Password</a>
        </div>
        """
        html = _base_template("Password Reset Request", "#FF5733", body)
        await _send(email_to, "Reset your Tsira password", html)

    @staticmethod
    async def password_changed(email_to: EmailStr) -> None:
        body = """
        <p style="font-size:16px;color:#333;">Hi,</p>
        <p style="font-size:16px;color:#333;">
          Your <strong>Tsira</strong> password was just changed successfully.
        </p>
        <p style="font-size:14px;color:#e53935;font-weight:bold;">
          &#9888; If you did NOT make this change, please reset your password immediately
          or contact our support team.
        </p>
        """
        html = _base_template("Password Changed", "#607D8B", body)
        await _send(email_to, "Your password has been changed", html)

    @staticmethod
    async def welcome(email_to: EmailStr, username: str) -> None:
        body = f"""
        <p style="font-size:18px;color:#333;">Welcome, <strong>{username}</strong>! 🎉</p>
        <p style="font-size:16px;color:#333;">
          Your account is now fully verified. Start exploring everything
          <strong>Tsira</strong> has to offer.
        </p>
        <div style="text-align:center;margin:30px 0;">
          <a href="https://yourapp.com/dashboard"
             style="background:#4CAF50;color:#fff;padding:14px 28px;
                    text-decoration:none;border-radius:6px;font-size:16px;">
            Go to Dashboard
          </a>
        </div>
        """
        html = _base_template("Welcome to Tsira!", "#4CAF50", body)
        # await _send(email_to, "Welcome to Tsira 🎉", html)
        return html

    @staticmethod
    async def account_banned(email_to: EmailStr, reason: str | None = None) -> None:
        reason_block = (
            f'<p style="font-size:14px;color:#555;"><strong>Reason:</strong> {reason}</p>'
            if reason else ""
        )
        body = f"""
        <p style="font-size:16px;color:#333;">Hello,</p>
        <p style="font-size:16px;color:#333;">
          Your <strong>Tsira</strong> account has been <strong style="color:#e53935;">suspended</strong>
          due to a violation of our Terms of Service.
        </p>
        {reason_block}
        <p style="font-size:14px;color:#555;">
          If you believe this is a mistake, please contact
          <a href="mailto:support@yourapp.com">support@yourapp.com</a>.
        </p>
        """
        html = _base_template("Account Suspended", "#e53935", body)
        # await _send(email_to, "Your Tsira account has been suspended", html)
        return html

    @staticmethod
    async def account_reactivated(email_to: EmailStr) -> None:
        body = """
        <p style="font-size:16px;color:#333;">Good news!</p>
        <p style="font-size:16px;color:#333;">
          Your <strong>Tsira</strong> account has been <strong style="color:#4CAF50;">reactivated</strong>.
          You can now log in and resume using all features.
        </p>
        <div style="text-align:center;margin:30px 0;">
          <a href="https://yourapp.com/login"
             style="background:#4CAF50;color:#fff;padding:14px 28px;
                    text-decoration:none;border-radius:6px;font-size:16px;">
            Log In Now
          </a>
        </div>
        """
        html = _base_template("Account Reactivated", "#4CAF50", body)
        await _send(email_to, "Your Tsira account has been reactivated", html)

    @staticmethod
    async def account_deleted(email_to: EmailStr) -> None:
        body = """
        <p style="font-size:16px;color:#333;">Hello,</p>
        <p style="font-size:16px;color:#333;">
          Your <strong>Tsira</strong> account has been permanently deleted
          as requested. All your data has been removed from our systems.
        </p>
        <p style="font-size:14px;color:#888;">
          We're sorry to see you go. If you change your mind,
          you can always create a new account.
        </p>
        """
        html = _base_template("Account Deleted", "#9E9E9E", body)
        # await _send(email_to, "Your Tsira account has been deleted", html)
        return html

    @staticmethod
    async def payment_successful(
        email_to: EmailStr,
        amount: str,
        currency: str,
        transaction_id: str,
        description: str,
    ) -> None:
        body = f"""
        <p style="font-size:16px;color:#333;">Hi,</p>
        <p style="font-size:16px;color:#333;">
          Your payment was processed successfully. Here is your receipt:
        </p>
        <table style="width:100%;border-collapse:collapse;margin:20px 0;">
          <tr style="background:#f5f5f5;">
            <td style="padding:10px;border:1px solid #ddd;font-weight:bold;">Description</td>
            <td style="padding:10px;border:1px solid #ddd;">{description}</td>
          </tr>
          <tr>
            <td style="padding:10px;border:1px solid #ddd;font-weight:bold;">Amount</td>
            <td style="padding:10px;border:1px solid #ddd;">{amount} {currency}</td>
          </tr>
          <tr style="background:#f5f5f5;">
            <td style="padding:10px;border:1px solid #ddd;font-weight:bold;">Transaction ID</td>
            <td style="padding:10px;border:1px solid #ddd;">{transaction_id}</td>
          </tr>
        </table>
        <p style="font-size:14px;color:#888;">
          Keep this email as your payment receipt.
          Questions? Contact <a href="mailto:support@yourapp.com">support@yourapp.com</a>.
        </p>
        """
        html = _base_template("Payment Successful", "#4CAF50", body)
        # await _send(email_to, f"Payment receipt – {amount} {currency}", html)
        return html

    @staticmethod
    async def payment_failed(
        email_to: EmailStr,
        amount: str,
        currency: str,
        reason: str | None = None,
    ) -> None:
        reason_block = (
            f'<p style="font-size:14px;color:#e53935;"><strong>Reason:</strong> {reason}</p>'
            if reason else ""
        )
        body = f"""
        <p style="font-size:16px;color:#333;">Hi,</p>
        <p style="font-size:16px;color:#333;">
          Unfortunately, your payment of <strong>{amount} {currency}</strong> could not be processed.
        </p>
        {reason_block}
        <p style="font-size:14px;color:#555;">
          Please update your payment details and try again, or contact
          <a href="mailto:support@yourapp.com">support@yourapp.com</a> for help.
        </p>
        """
        html = _base_template("Payment Failed", "#e53935", body)
        # await _send(email_to, f"Payment failed – {amount} {currency}", html)
        return html

    @staticmethod
    async def subscription_upgraded(
        email_to: EmailStr, plan_name: str, next_billing_date: str
    ) -> None:
        body = f"""
        <p style="font-size:16px;color:#333;">Hi,</p>
        <p style="font-size:16px;color:#333;">
          Your subscription has been upgraded to the
          <strong style="color:#9C27B0;">{plan_name}</strong> plan. 🎉
        </p>
        <p style="font-size:14px;color:#555;">
          Your next billing date is <strong>{next_billing_date}</strong>.
          Enjoy your new features!
        </p>
        """
        html = _base_template(f"Upgraded to {plan_name}", "#9C27B0", body)
        # await _send(email_to, f"You're now on the {plan_name} plan!", html)
        return html

    @staticmethod
    async def subscription_cancelled(email_to: EmailStr, end_date: str) -> None:
        body = f"""
        <p style="font-size:16px;color:#333;">Hi,</p>
        <p style="font-size:16px;color:#333;">
          Your subscription has been cancelled. You will continue to have access
          to premium features until <strong>{end_date}</strong>.
        </p>
        <p style="font-size:14px;color:#888;">
          We'd love to have you back. You can re-subscribe any time from your dashboard.
        </p>
        """
        html = _base_template("Subscription Cancelled", "#FF9800", body)
        await _send(email_to, "Your subscription has been cancelled", html)

    @staticmethod
    async def report_received(email_to: EmailStr, report_type: str) -> None:
        body = f"""
        <p style="font-size:16px;color:#333;">Hello,</p>
        <p style="font-size:16px;color:#333;">
          We have received your report regarding <strong>{report_type}</strong>.
          Our moderation team will review it within <strong>24–48 hours</strong>.
        </p>
        <p style="font-size:14px;color:#888;">
          Thank you for helping keep Tsira safe for everyone.
        </p>
        """
        html = _base_template("Report Received", "#607D8B", body)
        # await _send(email_to, "We received your report", html)
        return html

    @staticmethod
    async def new_login_alert(
        email_to: EmailStr, ip_address: str, device: str, location: str
    ) -> None:
        body = f"""
        <p style="font-size:16px;color:#333;">Hi,</p>
        <p style="font-size:16px;color:#333;">
          We detected a new login to your Tsira account:
        </p>
        <table style="width:100%;border-collapse:collapse;margin:20px 0;">
          <tr style="background:#f5f5f5;">
            <td style="padding:10px;border:1px solid #ddd;font-weight:bold;">IP Address</td>
            <td style="padding:10px;border:1px solid #ddd;">{ip_address}</td>
          </tr>
          <tr>
            <td style="padding:10px;border:1px solid #ddd;font-weight:bold;">Device</td>
            <td style="padding:10px;border:1px solid #ddd;">{device}</td>
          </tr>
          <tr style="background:#f5f5f5;">
            <td style="padding:10px;border:1px solid #ddd;font-weight:bold;">Location</td>
            <td style="padding:10px;border:1px solid #ddd;">{location}</td>
          </tr>
        </table>
        <p style="font-size:14px;color:#e53935;font-weight:bold;">
          If this was not you, please reset your password immediately.
        </p>
        """
        html = _base_template("New Login Detected", "#FF5733", body)
        # await _send(email_to, "New login to your Tsira account", html)
        return html

    @staticmethod
    async def congratulations(email_to: EmailStr, achievement: str) -> None:
        body = f"""
        <p style="font-size:18px;color:#333;">Congratulations!</p>
        <p style="font-size:16px;color:#333;">
          You just unlocked: <strong style="color:#FF9800;">{achievement}</strong>
        </p>
        <p style="font-size:14px;color:#888;">
          Keep it up &mdash; there are more milestones waiting for you on Tsira.
        </p>
        """
        html = _base_template("Achievement Unlocked", "#FF9800", body)
        # await _send(email_to, f"You unlocked: {achievement}", html)
        return html
