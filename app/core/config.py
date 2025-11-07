from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    APP_PORT: int = 8000
    CORS_ALLOW_ALL: bool = True
    CORS_ORIGINS: str = ""
    DATABASE_URL: str
    REDIS_URL: str

    JWT_SECRET: str = "change-me"
    JWT_ALG: str = "HS256"
    ACCESS_TTL_MIN: int = 15
    REFRESH_TTL_DAYS: int = 14
    REFRESH_IN_COOKIE: bool = True
    COOKIE_SECURE: bool = False
    COOKIE_DOMAIN: str | None = None



    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    def cors_origins_list(self) -> list[str]:
        s = (self.CORS_ORIGins or "").strip()
        if not s:
            return []
        return [x.strip() for x in s.split(",") if x.strip()]

    def refresh_cookie_kwargs(self) -> dict:
        kwargs = {"httponly": True, "samesite": "lax", "secure": self.COOKIE_SECURE}
        if self.COOKIE_DOMAIN:
            kwargs["domain"] = self.COOKIE_DOMAIN
        return kwargs


settings = Settings()