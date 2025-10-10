"""Pydantic models for configuration validation."""
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import List, Literal, Optional

import yaml
from pydantic import BaseModel, Field, field_validator


class ExchangeName(str, Enum):
    """Supported exchanges."""
    BINANCE = "binance"
    BYBIT = "bybit"


class StrategyType(str, Enum):
    """Strategy types."""
    CURRENT = "current"
    BASELINE = "baseline"
    CUSTOM = "custom"


class StopLossType(str, Enum):
    """Stop loss types."""
    ATR = "atr"
    PERCENTAGE = "percentage"
    FIXED = "fixed"


class TakeProfitType(str, Enum):
    """Take profit types."""
    ATR = "atr"
    PERCENTAGE = "percentage"
    FIXED = "fixed"
    NONE = "none"


class PositionSizingMethod(str, Enum):
    """Position sizing methods."""
    FIXED_RISK = "fixed_risk"
    FIXED_AMOUNT = "fixed_amount"
    KELLY = "kelly"


class RateLimitConfig(BaseModel):
    """Rate limit configuration."""
    max_requests_per_minute: int = 1200
    retry_attempts: int = 5
    backoff_base: float = 2.0
    backoff_max: float = 60.0


class ExchangeConfig(BaseModel):
    """Exchange configuration."""
    name: ExchangeName
    api_key: str = ""
    api_secret: str = ""
    testnet: bool = False
    rate_limit: RateLimitConfig


class ReconciliationConfig(BaseModel):
    """Data reconciliation configuration."""
    check_gaps: bool = True
    max_gap_minutes: int = 30
    allow_corrections: bool = True


class DataConfig(BaseModel):
    """Data configuration."""
    symbols: List[str]
    timeframes: List[str]
    storage_path: str = "data_incremental"
    format: Literal["csv", "parquet"] = "csv"
    incremental_update: bool = True
    reconciliation: ReconciliationConfig

    @field_validator("timeframes")
    @classmethod
    def validate_timeframes(cls, v: List[str]) -> List[str]:
        """Validate timeframe formats."""
        valid_timeframes = ["1m", "5m", "15m", "30m", "1h", "4h", "1d", "1w"]
        for tf in v:
            if tf not in valid_timeframes:
                raise ValueError(f"Invalid timeframe: {tf}. Must be one of {valid_timeframes}")
        return v


class TimezoneConfig(BaseModel):
    """Timezone configuration."""
    local: str = "America/Argentina/Buenos_Aires"
    exchange: str = "UTC"


class CurrentStrategyIndicators(BaseModel):
    """Current strategy indicator parameters."""
    ema_fast: int = 12
    ema_slow: int = 26
    rsi_period: int = 14
    rsi_oversold: float = 30
    rsi_overbought: float = 70
    macd_fast: int = 12
    macd_slow: int = 26
    macd_signal: int = 9


class CurrentStrategyEntry(BaseModel):
    """Current strategy entry conditions."""
    require_ema_cross: bool = True
    require_rsi_confirmation: bool = True
    require_macd_confirmation: bool = True


class CurrentStrategyConfig(BaseModel):
    """Current strategy configuration."""
    indicators: CurrentStrategyIndicators
    entry_conditions: CurrentStrategyEntry


class BaselineStrategyIndicators(BaseModel):
    """Baseline strategy indicator parameters."""
    ema_period: int = 50
    rsi_period: int = 14
    rsi_oversold: float = 35
    rsi_overbought: float = 65


class BaselineStrategyEntry(BaseModel):
    """Baseline strategy entry conditions."""
    price_above_ema: bool = True
    rsi_range: bool = True


class BaselineStrategyConfig(BaseModel):
    """Baseline strategy configuration."""
    indicators: BaselineStrategyIndicators
    entry_conditions: BaselineStrategyEntry


class StrategyConfig(BaseModel):
    """Strategy configuration."""
    type: StrategyType
    current: CurrentStrategyConfig
    baseline: BaselineStrategyConfig


class SchedulingConfig(BaseModel):
    """Scheduling configuration."""
    entry_window: dict = Field(default={"start": "06:00", "end": "12:00"})
    forced_close_window: dict = Field(default={"start": "19:00", "end": "20:00"})
    max_trades_per_day: int = 1
    enforce_daily_limit: bool = True


class StopLossConfig(BaseModel):
    """Stop loss configuration."""
    type: StopLossType
    atr_multiplier: float = 2.0
    percentage: float = 2.0
    fixed_points: float = 100


class TakeProfitConfig(BaseModel):
    """Take profit configuration."""
    type: TakeProfitType
    atr_multiplier: float = 3.0
    percentage: float = 4.0
    fixed_points: float = 200


class PositionSizingConfig(BaseModel):
    """Position sizing configuration."""
    method: PositionSizingMethod
    risk_per_trade_pct: float = 1.0
    max_position_pct: float = 10.0


class ATRConfig(BaseModel):
    """ATR configuration."""
    period: int = 14
    timeframe: str = "1d"


class RiskConfig(BaseModel):
    """Risk management configuration."""
    stop_loss: StopLossConfig
    take_profit: TakeProfitConfig
    position_sizing: PositionSizingConfig
    atr: ATRConfig


class FeesConfig(BaseModel):
    """Trading fees configuration."""
    maker: float = 0.001
    taker: float = 0.001


class SlippageConfig(BaseModel):
    """Slippage configuration."""
    enabled: bool = True
    percentage: float = 0.05


class BrokerConfig(BaseModel):
    """Broker simulation configuration."""
    initial_capital: float = 10000.0
    quote_currency: str = "USDT"
    fees: FeesConfig
    slippage: SlippageConfig


class TradesOutputConfig(BaseModel):
    """Trades output configuration."""
    path: str = "data_incremental/backtest_results"
    format: Literal["csv", "parquet", "both"] = "csv"


class BacktestConfig(BaseModel):
    """Backtest configuration."""
    start_date: str = "2023-01-01"
    end_date: Optional[str] = None
    warmup_periods: int = 50
    save_trades: bool = True
    trades_output: TradesOutputConfig
    save_equity_curve: bool = True

    @field_validator("start_date")
    @classmethod
    def validate_start_date(cls, v: str) -> str:
        """Validate start date format."""
        try:
            datetime.strptime(v, "%Y-%m-%d")
        except ValueError:
            raise ValueError("start_date must be in YYYY-MM-DD format")
        return v

    @field_validator("end_date")
    @classmethod
    def validate_end_date(cls, v: Optional[str]) -> Optional[str]:
        """Validate end date format."""
        if v is not None:
            try:
                datetime.strptime(v, "%Y-%m-%d")
            except ValueError:
                raise ValueError("end_date must be in YYYY-MM-DD format")
        return v


class MetricsConfig(BaseModel):
    """Metrics configuration."""
    risk_free_rate: float = 0.02
    benchmark_symbol: str = "BTC/USDT"
    calculate: List[str]


class LoggingOutputConfig(BaseModel):
    """Logging output configuration."""
    console: bool = True
    file: bool = True
    file_path: str = "logs/one_trade.log"


class LoggingConfig(BaseModel):
    """Logging configuration."""
    level: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = "INFO"
    format: Literal["structured", "simple"] = "structured"
    output: LoggingOutputConfig
    log_trades: bool = True
    log_signals: bool = True
    log_scheduler_events: bool = True


class ReproducibilityConfig(BaseModel):
    """Reproducibility configuration."""
    seed: int = 42
    deterministic: bool = True


class ValidationConfig(BaseModel):
    """Validation configuration."""
    strict_mode: bool = True
    check_trade_limit_daily: bool = True
    check_entry_windows: bool = True
    check_forced_close: bool = True


class Config(BaseModel):
    """Main configuration model."""
    exchange: ExchangeConfig
    data: DataConfig
    timezone: TimezoneConfig
    strategy: StrategyConfig
    scheduling: SchedulingConfig
    risk: RiskConfig
    broker: BrokerConfig
    backtest: BacktestConfig
    metrics: MetricsConfig
    logging: LoggingConfig
    reproducibility: ReproducibilityConfig
    validation: ValidationConfig


def load_config(config_path: str = "config/config.yaml") -> Config:
    """Load and validate configuration from YAML file. Args: config_path: Path to config file. Returns: Validated Config object. Raises: FileNotFoundError: If config file doesn't exist. ValueError: If config is invalid."""
    config_file = Path(config_path)
    if not config_file.exists():
        raise FileNotFoundError(f"Configuration file not found: {config_path}")
    with open(config_file, "r", encoding="utf-8") as f:
        config_dict = yaml.safe_load(f)
    return Config(**config_dict)

