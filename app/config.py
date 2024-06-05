import os

import redis
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic_core import MultiHostUrl
from pydantic import PostgresDsn, computed_field
from fastapi_mail import ConnectionConfig


dirname = os.path.dirname(__file__)
templates_folder = os.path.join(dirname, 'templates')

class Settings(BaseSettings):
    auth_key: str
    
    pg_host: str
    pg_user: str
    pg_password: str
    
    host: str = "localhost"
    port: int = 8000
    
    sender_gmail: str
    sender_gmail_password: str
    
    yagpt_folder: str
    yagpt_key: str

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @computed_field
    @property
    def psycopg_url(self) -> PostgresDsn:
        return MultiHostUrl.build(
            scheme="postgresql",
            username=self.pg_user,
            password=self.pg_password,
            host=self.pg_host,
            path="postgres"
        )


global_settings = Settings()

email_config = ConnectionConfig(
    MAIL_USERNAME = global_settings.sender_gmail,
    MAIL_PASSWORD = global_settings.sender_gmail_password,
    MAIL_FROM = global_settings.sender_gmail,
    MAIL_PORT = 587,
    MAIL_SERVER = "smtp.gmail.com",
    MAIL_FROM_NAME = "Sentilens",
    MAIL_STARTTLS = True,
    MAIL_SSL_TLS = False,
    USE_CREDENTIALS = True,
    VALIDATE_CERTS = False,
    TEMPLATE_FOLDER = templates_folder,
)

redis_client = redis.Redis("redis", port=6379)
