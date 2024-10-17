import logging

from fastapi_mail import FastMail, MessageSchema, MessageType


from app.config import email_config

logger = logging.getLogger("uvicorn")


async def send_registration_notification(recipient_email: str):
    try:
        message = MessageSchema(
            subject="Thank you for registration in Sentilens!",
            recipients=[recipient_email],
            subtype=MessageType.html
        )
        fm = FastMail(email_config)
        await fm.send_message(
            message,
            template_name="registration_notification.html"
        )
    except Exception as e:
        logger.error("Something went wrong in registration email notification")
        logger.error(str(e))


async def send_password_reset_notification(
    recipient_email: str,
    reset_code: str
) -> None:
    templare_body = {
        "reset_code": reset_code
    }
    try:
        message = MessageSchema(
            subject="Password reset",
            recipients=[recipient_email],
            template_body=templare_body,
            subtype=MessageType.html
        )
        fm = FastMail(email_config)
        await fm.send_message(
            message,
            template_name="password_reset_notification.html"
        )
    except Exception as e:
        logger.error(
            "Something went wrong in password reset email notification"
        )
        logger.error(str(e))
