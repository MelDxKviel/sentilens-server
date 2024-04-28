from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic_core import MultiHostUrl
from pydantic import PostgresDsn, computed_field


class Settings(BaseSettings):
    auth_key: str
    pg_host: str
    pg_user: str
    pg_password: str
    host: str = "localhost"
    port: int = 8000

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
