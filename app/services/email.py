# import os
# import smtplib
# from email.mime.multipart import MIMEMultipart
# from email.mime.text import MIMEText


# def send_email(receiver_email: str, subject: str, body: str) -> bool:
#     try:
#         sender_email = os.getenv("SENDER_EMAIL")
#         sender_password = os.getenv("APP_PASSWORD")

#         message = MIMEMultipart()
#         message['Subject'] = subject
#         message['From'] = sender_email
#         message['To'] = receiver_email
#         message.attach(MIMEText(body))

#         with smtplib.SMTP("smtp.gmail.com", 587) as server:
#             server.starttls()
#             server.login(sender_email, sender_password)
#             server.send_message(message)
#             print("✅ Email sent successfully.")
#             return True
#     except Exception:
#         print(Exception)
#         return False


# app/services/email_sender.py

from aiosmtplib import SMTP
from email.message import EmailMessage

from app.core import SMTP_PASSWORD, SMTP_PORT, SMTP_USERNAME


async def send_email(to_email: str, subject: str, content: str):
    message = EmailMessage()
    message["From"] = SMTP_USERNAME
    message["To"] = to_email
    message["Subject"] = subject
    message.set_content(content)

    async with SMTP(hostname=SMTP_USERNAME, port=int(SMTP_PORT), start_tls=True) as smtp:
        await smtp.login(SMTP_USERNAME, SMTP_PASSWORD)
        await smtp.send_message(message)
