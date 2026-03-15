from pydantic_settings import BaseSettings
from dotenv import load_dotenv
import os

load_dotenv()
from typing import Set


class Settings(BaseSettings):
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Zoom API"
    VERSION: str = "1.1"
    DOCS_URL: str = "/docs"
    SERVER_HOST: str = "127.0.0.1"
    SERVER_PORT: int = 8181
    ENVIRONMET: str = "dev"
    ZOOM_ACCOUNT_ID: str
    ZOOM_CLIENT_ID: str
    ZOOM_CLIENT_SECRET: str
    ZOOM_BASE_URL: str 
    ZOOM_SECRET_TOKEN: str




    class Config:
        env_file = ".env"

    @property
    def fastapi_kwargs(self):
        return {
            "docs_url": self.DOCS_URL,
            "title": self.PROJECT_NAME,
            "version": self.VERSION,
        }


settings = Settings()
