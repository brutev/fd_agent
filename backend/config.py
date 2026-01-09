import os
from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import ConfigDict

class Settings(BaseSettings):
    model_config = ConfigDict(env_file=".env")
    
    # Database
    DATABASE_URL: str = "sqlite:///./fd_agent.db"
    
    # JWT
    SECRET_KEY: str = "fd-agent-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # API
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "FD Agent System"
    
    # Chroma Vector DB
    CHROMA_PERSIST_DIRECTORY: str = "./chroma_db"
    EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 60
    
    # OTP Settings
    OTP_EXPIRE_MINUTES: int = 5
    OTP_LENGTH: int = 6
    
    # Transaction Limits
    NEFT_MIN_AMOUNT: float = 1.0
    NEFT_MAX_AMOUNT: float = 1000000.0
    UPI_MAX_AMOUNT: float = 100000.0
    IMPS_MAX_AMOUNT: float = 500000.0
    
    # File Upload
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB
    UPLOAD_DIR: str = "./uploads"
    
    # External APIs (Mock in development)
    UIDAI_API_URL: str = "https://mock-uidai.example.com"
    NPCI_API_URL: str = "https://mock-npci.example.com"

settings = Settings()