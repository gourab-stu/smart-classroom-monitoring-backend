import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


def send_email(receiver_email: str, subject: str, body: str) -> bool:
    try:
        sender_email = os.getenv("SENDER_EMAIL")
        sender_password = os.getenv("APP_PASSWORD")

        message = MIMEMultipart()
        message['Subject'] = subject
        message['From'] = sender_email
        message['To'] = receiver_email
        message.attach(MIMEText(body))

        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.send_message(message)
            print("✅ Email sent successfully.")
            return True
    except Exception:
        print(Exception)
        return False
