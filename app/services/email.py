from aiosmtplib import SMTP
from email.message import EmailMessage

from app.core.config import settings


async def send_email(to_email: str, subject: str, content: str):
    # print("sending email")
    message = EmailMessage()
    message["From"] = settings.SMTP_USERNAME
    message["To"] = to_email
    message["Subject"] = subject
    message.set_content(content)

    async with SMTP(hostname=settings.SMTP_HOST, port=int(settings.SMTP_PORT), start_tls=True) as smtp:
        await smtp.login(settings.SMTP_USERNAME, settings.SMTP_PASSWORD)
        await smtp.send_message(message)
        smtp.close()
