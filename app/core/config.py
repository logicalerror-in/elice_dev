from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    APP_PORT: int = 8000
    CORS_ALLOW_ALL: bool = True
    CORS_ORIGINS: str = "" 


    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    def cors_origins_list(self) -> list[str]:
        s = (self.CORS_ORIGINS or "").strip()
        if not s:
            return []
        return [x.strip() for x in s.split(",") if x.strip()]

settings = Settings()
