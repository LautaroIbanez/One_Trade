"""
Application configuration using Pydantic Settings.
"""

from typing import List, Optional, Union
from pydantic import AnyHttpUrl, field_validator, Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings with environment variable support."""
    
    # Project
    PROJECT_NAME: str = "One Trade Decision App"
    VERSION: str = "1.0.0"
    DESCRIPTION: str = "Sistema inteligente de recomendaciones de trading"
    ENVIRONMENT: str = "development"
    
    # API
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 days
    
    # Database
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_USER: str = "onetrade"
    POSTGRES_PASSWORD: str = "onetrade_dev"
    POSTGRES_DB: str = "onetrade"
    POSTGRES_PORT: int = 5432
    USE_SQLITE: bool = True  # Use SQLite for development when Docker is not available
    DATABASE_URL: Optional[str] = None
    
    @field_validator("DATABASE_URL", mode="before")
    @classmethod
    def assemble_db_connection(cls, v: Optional[str], info) -> str:
        if isinstance(v, str):
            return v
        
        # Get values from info.data
        values = info.data if hasattr(info, 'data') else {}
        
        # Use SQLite for development if USE_SQLITE is True
        if values.get('USE_SQLITE', False):
            return "sqlite:///./onetrade.db"
        
        return (
            f"postgresql://{values.get('POSTGRES_USER')}:"
            f"{values.get('POSTGRES_PASSWORD')}@"
            f"{values.get('POSTGRES_SERVER')}:"
            f"{values.get('POSTGRES_PORT')}/"
            f"{values.get('POSTGRES_DB')}"
        )
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379"
    REDIS_PASSWORD: Optional[str] = None
    
    # RabbitMQ
    RABBITMQ_URL: str = "amqp://onetrade:onetrade_dev@localhost:5672"
    
    # CORS
    BACKEND_CORS_ORIGINS: str = Field(
        default="http://localhost:3000,http://localhost:5173"
    )

    @property
    def CORS_ORIGINS_LIST(self) -> List[str]:
        """Parse CORS origins into list."""
        return [origin.strip() for origin in self.BACKEND_CORS_ORIGINS.split(",")]
    
    # Security
    ALLOWED_HOSTS: str = Field(default="localhost,127.0.0.1")
    
    # External APIs
    BINANCE_API_URL: str = "https://api.binance.com"
    BINANCE_WS_URL: str = "wss://stream.binance.com:9443/ws"
    # Optional credentials for Binance (read from environment if provided)
    BINANCE_API_KEY: Optional[str] = None
    BINANCE_API_SECRET: Optional[str] = None
    
    # Trading
    DEFAULT_SYMBOLS: str = Field(default="BTCUSDT,ETHUSDT,ADAUSDT")
    DEFAULT_TIMEFRAMES: str = Field(default="1h,4h,1d")
    
    # Recommendation Engine
    RECOMMENDATION_CACHE_TTL: int = 3600  # 1 hour
    MAX_RECOMMENDATIONS_PER_SYMBOL: int = 3
    
    # Monitoring
    SENTRY_DSN: Optional[str] = None
    LOG_LEVEL: str = "INFO"
    
    class Config:
        case_sensitive = True
        env_file = ".env"


# Global settings instance
settings = Settings()

