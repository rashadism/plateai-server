import os
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    """
    # Database Configuration
    DATABASE_HOST: str = os.getenv("DATABASE_HOST", "")
    DATABASE_PORT: int = int(os.getenv("DATABASE_PORT", 0))
    DATABASE_USER: str = os.getenv("DATABASE_USER", "")
    DATABASE_PASSWORD: str = os.getenv("DATABASE_PASSWORD", "")
    DATABASE_NAME: str = os.getenv("DATABASE_NAME", "")

    @property
    def DATABASE_URL(self) -> str:
        return f"postgresql://{self.DATABASE_USER}:{self.DATABASE_PASSWORD}@{self.DATABASE_HOST}:{self.DATABASE_PORT}/{self.DATABASE_NAME}"

    # JWT Authentication Configuration
    SECRET_KEY: str = os.getenv("SECRET_KEY", "ashdjasdgajshd")
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))

    # Google API Configuration
    GOOGLE_API_KEY: str = os.getenv("GOOGLE_API_KEY", "")

    class Config:
        env_file = ".env"
        env_file_encoding = 'utf-8'

settings = Settings()