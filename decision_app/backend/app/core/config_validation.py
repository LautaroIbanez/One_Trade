"""Configuration validation module."""
from pydantic import Field, ValidationError, field_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings with validation."""

    # Project
    PROJECT_NAME: str = Field(default="One Trade Decision App")
    VERSION: str = Field(default="1.0.0")
    ENVIRONMENT: str = Field(default="development")

    # API
    API_V1_STR: str = Field(default="/api/v1")
    SECRET_KEY: str = Field(min_length=32)
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=10080, gt=0)
    API_HOST: str = Field(default="0.0.0.0")
    API_PORT: int = Field(default=8000, gt=0, lt=65536)

    # Database
    POSTGRES_SERVER: str = Field(default="localhost")
    POSTGRES_USER: str = Field(default="onetrade")
    POSTGRES_PASSWORD: str = Field(min_length=1)
    POSTGRES_DB: str = Field(default="onetrade")
    POSTGRES_PORT: int = Field(default=5432, gt=0, lt=65536)

    @property
    def DATABASE_URL(self) -> str:
        """Construct database URL."""
        return f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

    @property
    def DATABASE_URL_SYNC(self) -> str:
        """Construct sync database URL for Alembic."""
        return f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

    # Redis
    REDIS_URL: str = Field(default="redis://localhost:6379/0")
    REDIS_PASSWORD: str = Field(default="")

    # RabbitMQ
    RABBITMQ_URL: str = Field(default="amqp://onetrade:onetrade_dev@localhost:5672/")
    CELERY_BROKER_URL: str = Field(default="redis://localhost:6379/1")
    CELERY_RESULT_BACKEND: str = Field(default="redis://localhost:6379/1")

    # CORS
    BACKEND_CORS_ORIGINS: str = Field(
        default="http://localhost:3000,http://localhost:5173"
    )

    @property
    def CORS_ORIGINS_LIST(self) -> list[str]:
        """Parse CORS origins into list."""
        return [origin.strip() for origin in self.BACKEND_CORS_ORIGINS.split(",")]

    # Security
    ALLOWED_HOSTS: str = Field(default="localhost,127.0.0.1")

    # External APIs
    BINANCE_API_URL: str = Field(default="https://api.binance.com")
    BINANCE_WS_URL: str = Field(default="wss://stream.binance.com:9443/ws")

    # Trading
    DEFAULT_SYMBOLS: str = Field(default="BTCUSDT,ETHUSDT,ADAUSDT")
    DEFAULT_TIMEFRAMES: str = Field(default="1h,4h,1d")

    # Recommendation Engine
    RECOMMENDATION_CACHE_TTL: int = Field(default=3600, gt=0)
    MAX_RECOMMENDATIONS_PER_SYMBOL: int = Field(default=3, gt=0)

    # Monitoring
    SENTRY_DSN: str = Field(default="")
    LOG_LEVEL: str = Field(default="INFO")

    @field_validator("ENVIRONMENT")
    @classmethod
    def validate_environment(cls, v: str) -> str:
        """Validate environment value."""
        allowed = ["development", "staging", "production"]
        if v not in allowed:
            raise ValueError(f"ENVIRONMENT must be one of {allowed}")
        return v

    @field_validator("LOG_LEVEL")
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        """Validate log level."""
        allowed = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if v.upper() not in allowed:
            raise ValueError(f"LOG_LEVEL must be one of {allowed}")
        return v.upper()

    class Config:
        """Pydantic config."""

        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


def validate_settings() -> Settings:
    """Validate and return settings."""
    try:
        settings = Settings()
        return settings
    except ValidationError as e:
        print("❌ Configuration validation failed:")
        print(e)
        raise


# Global settings instance
settings = validate_settings()

