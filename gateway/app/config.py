from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    jwt_secret: str = "dev-secret"
    jwt_expire_minutes: int = 120

settings = Settings()
