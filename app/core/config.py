from pydantic_settings import BaseSettings
import secrets


class Settings(BaseSettings):
    PROJECT_NAME: str = "Postgres-Database_perfomance-monitor"
    PROJECT_VERSION: str = "0.0.1"
    PROJECT_DESCRIPTION: str = "A postgres database monitor"
    API_PREFIX: str = "/api/v1"
    SECRET_KEY: str = secrets.token_urlsafe(32)
    DEBUG: bool = False
    TESTING: bool = False