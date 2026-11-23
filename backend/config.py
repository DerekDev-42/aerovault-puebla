from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    APP_NAME: str = "AeroVault Puebla API"
    APP_VERSION: str = "1.0.0"
    DATABASE_URL: str = "sqlite:///./aerovault_puebla.db"
    AWS_ACCESS_KEY_ID: str = ""
    AWS_SECRET_ACCESS_KEY: str = ""
    AWS_REGION: str = "us-east-1"
    S3_BUCKET_NAME: str = "dw-aerovault-puebla-utbis"
    LLM_API_KEY: str = ""

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()