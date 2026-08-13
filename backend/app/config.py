import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "SentinelRisk"
    API_PREFIX: str = "/api/v1"
    VERSION: str = "1.0.0"
    
    # Environment
    ENV: str = os.getenv("ENV", "development")
    SECRET_KEY: str = os.getenv("SECRET_KEY", "sentinelrisk-secret-key-super-secure-change-in-production-2026")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 # 24 hours
    
    # Database (PostgreSQL default with SQLite fallback for lightweight local dev)
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL", 
        "sqlite:///./sentinelrisk.db"
    )
    
    # Dataset & Storage
    DATA_PATH: str = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "data", "creditcard.csv")
    MODEL_DIR: str = os.path.join(os.path.dirname(os.path.abspath(__file__)), "saved_models")
    
    # Default Risk Thresholds (0 - 100)
    THRESHOLD_ALLOW: float = 20.0     # 0-20 LOW -> ALLOW
    THRESHOLD_CHALLENGE: float = 50.0 # 21-50 MEDIUM -> CHALLENGE
    THRESHOLD_REVIEW: float = 75.0    # 51-75 HIGH -> REVIEW
    # > 75 CRITICAL -> BLOCK
    
    # Default Business Cost Matrix ($)
    COST_FALSE_POSITIVE: float = 50.0  # Customer friction & lost lifetime value
    COST_MISSED_FRAUD_BASE: float = 100.0 # Chargeback fee + operational cost on top of transaction amount
    COST_MANUAL_REVIEW: float = 15.0   # Analyst review hourly cost per ticket
    
    class Config:
        case_sensitive = True

settings = Settings()
