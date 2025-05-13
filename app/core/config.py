import os


mongo_uri: str | None = os.getenv(key="MONGODB_URI")
db_name: str | None = os.getenv(key="DATABASE_NAME")
sender_email: str | None = os.getenv(key="SENDER_EMAIL")
password: str | None = os.getenv(key="EMAIL_APP_PASSWORD")
