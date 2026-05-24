from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # The format is postgresql+ASYNC_DRIVER://user:password@host/dbname
    DATABASE_URL: str 
    DATABASE_SYNC_URL: str 
    SECRET_KEY: str
    ALGORITHM: str
    CELERY_BROKER_URL: str
    CELERY_RESULT_BACKEND: str
    class Config:
        env_file = ".env"

settings = Settings()
