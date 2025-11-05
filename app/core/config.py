from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    APP_PORT: int = 8000
    CORS_ALLOW_ALL: bool = True
    CORS_ORIGINS: list[str] = []

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()
