-- One Trade Decision App - Database Initialization Script
-- This script sets up the initial database structure and sample data

-- Create TimescaleDB extension
CREATE EXTENSION IF NOT EXISTS timescaledb;

-- Create initial symbols
INSERT INTO symbols (symbol, base_asset, quote_asset, is_active, min_qty, max_qty, step_size, tick_size) VALUES
('BTCUSDT', 'BTC', 'USDT', true, 0.00001, 9000.00000000, 0.00001, 0.01),
('ETHUSDT', 'ETH', 'USDT', true, 0.00001, 9000.00000000, 0.00001, 0.01),
('ADAUSDT', 'ADA', 'USDT', true, 0.1, 9000000.00000000, 0.1, 0.0001),
('SOLUSDT', 'SOL', 'USDT', true, 0.01, 90000.00000000, 0.01, 0.001),
('DOTUSDT', 'DOT', 'USDT', true, 0.01, 90000.00000000, 0.01, 0.001)
ON CONFLICT (symbol) DO NOTHING;

-- Create initial timeframes
INSERT INTO timeframes (timeframe, description, seconds, is_active) VALUES
('1m', '1 Minute', 60, true),
('5m', '5 Minutes', 300, true),
('15m', '15 Minutes', 900, true),
('30m', '30 Minutes', 1800, true),
('1h', '1 Hour', 3600, true),
('4h', '4 Hours', 14400, true),
('1d', '1 Day', 86400, true),
('1w', '1 Week', 604800, true)
ON CONFLICT (timeframe) DO NOTHING;

-- Create hypertable for market_data (TimescaleDB)
SELECT create_hypertable('market_data', 'timestamp', if_not_exists => TRUE);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_market_data_symbol_timeframe_timestamp 
ON market_data (symbol, timeframe, timestamp DESC);

CREATE INDEX IF NOT EXISTS idx_market_data_timestamp_symbol 
ON market_data (timestamp DESC, symbol);

-- Create sample recommendations
INSERT INTO recommendations (
    symbol, timeframe, action, confidence, price_target, stop_loss, reasoning,
    strategy_weights, market_conditions, is_active
) VALUES
(
    'BTCUSDT', '1h', 'BUY', 0.85, 72000.0, 64500.0,
    'Strong bullish momentum with RSI in favorable zone. Volume increasing and price breaking above key resistance.',
    '{"rsi_strategy": 0.25, "macd_strategy": 0.20, "bollinger_bands": 0.30, "volume_profile": 0.25}',
    '{"trend": "bullish", "volatility": "medium", "volume": "high"}',
    true
),
(
    'ETHUSDT', '4h', 'SELL', 0.72, 3100.0, 3550.0,
    'Bearish divergence detected. MACD showing weakness and price approaching resistance level with decreasing volume.',
    '{"rsi_strategy": 0.30, "macd_strategy": 0.35, "bollinger_bands": 0.20, "volume_profile": 0.15}',
    '{"trend": "bearish", "volatility": "high", "volume": "medium"}',
    true
),
(
    'ADAUSDT', '1d', 'HOLD', 0.60, NULL, NULL,
    'Sideways consolidation pattern. Wait for clear breakout above resistance or breakdown below support before taking action.',
    '{"rsi_strategy": 0.20, "macd_strategy": 0.15, "bollinger_bands": 0.40, "volume_profile": 0.25}',
    '{"trend": "sideways", "volatility": "low", "volume": "low"}',
    true
);

-- Create sample backtest
INSERT INTO backtests (
    name, description, strategy_name, symbol, timeframe, start_date, end_date,
    initial_capital, parameters, status
) VALUES
(
    'Multi-Strategy Portfolio (BTC/USDT)',
    'Comprehensive backtest using multiple trading strategies on BTC/USDT',
    'multi_strategy', 'BTCUSDT', '1h',
    '2024-01-01 00:00:00+00', '2024-10-01 00:00:00+00',
    10000.0,
    '{"risk_level": "moderate", "max_position_size": 0.1, "stop_loss": 0.05, "take_profit": 0.15}',
    'COMPLETED'
);

-- Create sample backtest metrics
INSERT INTO backtest_metrics (backtest_id, metric_name, metric_value, metric_type, description) VALUES
(1, 'total_return', 24.5, 'PERFORMANCE', 'Total return percentage'),
(1, 'sharpe_ratio', 1.85, 'RISK', 'Risk-adjusted return metric'),
(1, 'max_drawdown', -8.2, 'RISK', 'Maximum peak-to-trough decline'),
(1, 'win_rate', 68.0, 'TRADE', 'Percentage of profitable trades'),
(1, 'total_trades', 142, 'TRADE', 'Total number of trades executed'),
(1, 'avg_trade_duration', 2.3, 'TRADE', 'Average trade duration in days');

-- Create sample backtest results
INSERT INTO backtest_results (
    backtest_id, trade_id, action, entry_timestamp, exit_timestamp,
    entry_price, exit_price, quantity, pnl, pnl_percentage, commission, is_profitable
) VALUES
(1, 'trade_001', 'BUY', '2024-01-15 10:00:00+00', '2024-01-17 14:30:00+00',
 42000.0, 43500.0, 0.1, 150.0, 3.57, 2.0, true),
(1, 'trade_002', 'SELL', '2024-01-20 08:00:00+00', '2024-01-22 16:00:00+00',
 44000.0, 42500.0, 0.1, 150.0, 3.41, 2.0, true),
(1, 'trade_003', 'BUY', '2024-02-01 12:00:00+00', '2024-02-03 09:00:00+00',
 41000.0, 40500.0, 0.1, -50.0, -1.22, 2.0, false);

-- Update the backtest completion timestamp
UPDATE backtests SET completed_at = '2024-10-01 12:00:00+00' WHERE id = 1;

