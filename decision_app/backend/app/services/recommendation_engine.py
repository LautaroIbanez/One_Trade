"""
Enhanced recommendation engine that combines multiple strategies.
"""

from typing import Dict, List, Any, Optional
import pandas as pd
import numpy as np
from datetime import datetime

from app.services.strategy_service import strategy_service
from app.services.signal_consolidator import signal_consolidator, RecommendationType
from app.services.binance_service import BinanceService
from app.core.logging import get_logger

logger = get_logger(__name__)


class RecommendationEngine:
    """Enhanced recommendation engine with multi-strategy support."""
    
    def __init__(self):
        """Initialize the recommendation engine."""
        self.supported_symbols = ["BTCUSDT", "ETHUSDT", "ADAUSDT", "SOLUSDT"]
        self.default_timeframe = "1d"
        self.default_days = 30
    
    async def generate_recommendation(
        self,
        symbol: str = "BTCUSDT",
        timeframe: str = "1d",
        days: int = 30
    ) -> Dict[str, Any]:
        """
        Generate a comprehensive trading recommendation.
        
        Args:
            symbol: Trading symbol
            timeframe: Data timeframe
            days: Number of days of historical data
            
        Returns:
            Complete recommendation with analysis
        """
        try:
            logger.info(f"Generating recommendation for {symbol}")
            
            # Step 1: Get market data
            market_data = await self._get_market_data(symbol, timeframe, days)
            if market_data.empty:
                raise ValueError(f"No market data available for {symbol}")
            
            # Step 2: Get current market info
            current_price = market_data['close'].iloc[-1]
            market_info = await self._get_market_info(symbol)
            
            # Step 3: Analyze with all strategies
            strategy_signals = {}
            for strategy_name in strategy_service._strategies.keys():
                try:
                    signals = strategy_service.analyze_with_strategy(
                        strategy_name, market_data
                    )
                    strategy_signals[strategy_name] = signals
                    logger.info(f"Generated {len(signals)} signals for {strategy_name}")
                except Exception as e:
                    logger.error(f"Error analyzing {strategy_name}: {e}")
                    strategy_signals[strategy_name] = []
            
            # Step 4: Consolidate signals
            consolidated = signal_consolidator.consolidate_signals(
                strategy_signals, current_price, symbol
            )
            
            # Step 5: Add market context
            market_context = self._analyze_market_context(market_data, market_info)
            
            # Step 6: Calculate trading levels (entry, TP, SL)
            trading_levels = self._calculate_trading_levels(
                market_data, current_price, consolidated['recommendation']
            )
            
            # Step 7: Generate final recommendation
            final_recommendation = {
                **consolidated,
                "market_context": market_context,
                "data_summary": {
                    "symbol": symbol,
                    "timeframe": timeframe,
                    "data_points": len(market_data),
                    "price_range": {
                        "min": float(market_data['close'].min()),
                        "max": float(market_data['close'].max()),
                        "current": float(current_price)
                    },
                    "volatility": self._calculate_volatility(market_data)
                },
                "trading_levels": trading_levels,
                "generated_at": datetime.now().isoformat()
            }
            
            logger.info(f"Generated recommendation: {consolidated['recommendation']} "
                       f"with {consolidated['confidence']:.1%} confidence")
            
            return final_recommendation
            
        except Exception as e:
            logger.error(f"Error generating recommendation: {e}")
            raise
    
    async def _get_market_data(
        self, 
        symbol: str, 
        timeframe: str, 
        days: int
    ) -> pd.DataFrame:
        """Get market data from Binance."""
        try:
            async with BinanceService() as binance:
                return await binance.get_market_data(
                    symbol=symbol,
                    interval=timeframe,
                    days=days
                )
        except Exception as e:
            logger.error(f"Error getting market data: {e}")
            raise
    
    async def _get_market_info(self, symbol: str) -> Dict[str, Any]:
        """Get current market information."""
        try:
            async with BinanceService() as binance:
                tickers = await binance.get_24hr_ticker(symbol=symbol)
                if tickers:
                    ticker = tickers[0]
                    return {
                        "last_price": float(ticker['lastPrice']),
                        "price_change_24h": float(ticker['priceChange']),
                        "price_change_percent_24h": float(ticker['priceChangePercent']),
                        "volume_24h": float(ticker['volume']),
                        "high_24h": float(ticker['highPrice']),
                        "low_24h": float(ticker['lowPrice']),
                        "trades_24h": int(ticker['count'])
                    }
                else:
                    return {}
        except Exception as e:
            logger.error(f"Error getting market info: {e}")
            return {}
    
    def _analyze_market_context(
        self, 
        market_data: pd.DataFrame, 
        market_info: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Analyze market context and trends."""
        
        if market_data.empty:
            return {"trend": "UNKNOWN", "volatility": "UNKNOWN"}
        
        # Calculate trend
        price_change = market_data['close'].iloc[-1] - market_data['close'].iloc[0]
        price_change_percent = (price_change / market_data['close'].iloc[0]) * 100
        
        if price_change_percent > 5:
            trend = "STRONG_UPTREND"
        elif price_change_percent > 2:
            trend = "UPTREND"
        elif price_change_percent < -5:
            trend = "STRONG_DOWNTREND"
        elif price_change_percent < -2:
            trend = "DOWNTREND"
        else:
            trend = "SIDEWAYS"
        
        # Calculate volatility
        returns = market_data['close'].pct_change().dropna()
        volatility = returns.std() * 100
        
        if volatility > 5:
            volatility_level = "HIGH"
        elif volatility > 2:
            volatility_level = "MEDIUM"
        else:
            volatility_level = "LOW"
        
        # Recent performance
        recent_performance = {
            "day_1": market_info.get("price_change_percent_24h", 0),
            "day_7": price_change_percent,
            "volatility": volatility
        }
        
        return {
            "trend": trend,
            "volatility": volatility_level,
            "recent_performance": recent_performance,
            "market_activity": {
                "volume_24h": market_info.get("volume_24h", 0),
                "trades_24h": market_info.get("trades_24h", 0)
            }
        }
    
    def _calculate_volatility(self, market_data: pd.DataFrame) -> float:
        """Calculate price volatility."""
        if len(market_data) < 2:
            return 0.0
        
        returns = market_data['close'].pct_change().dropna()
        return float(returns.std() * 100)
    
    def _calculate_atr(self, market_data: pd.DataFrame, period: int = 14) -> float:
        """Calculate Average True Range (ATR)."""
        if len(market_data) < period:
            return 0.0
        
        high = market_data['high']
        low = market_data['low']
        close = market_data['close']
        
        # Calculate True Range
        tr1 = high - low
        tr2 = abs(high - close.shift())
        tr3 = abs(low - close.shift())
        
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        
        # Calculate ATR (simple moving average of TR)
        atr = tr.rolling(window=period).mean().iloc[-1]
        
        return float(atr) if not pd.isna(atr) else 0.0
    
    def _find_support_resistance(
        self, 
        market_data: pd.DataFrame, 
        window: int = 20
    ) -> Dict[str, float]:
        """Find support and resistance levels using recent highs and lows."""
        if len(market_data) < window:
            window = len(market_data)
        
        recent_data = market_data.tail(window)
        
        support = float(recent_data['low'].min())
        resistance = float(recent_data['high'].max())
        
        # Calculate mid-level
        mid_level = (support + resistance) / 2
        
        return {
            "support": support,
            "resistance": resistance,
            "mid_level": mid_level
        }
    
    def _calculate_trading_levels(
        self, 
        market_data: pd.DataFrame, 
        current_price: float,
        recommendation: str
    ) -> Optional[Dict[str, Any]]:
        """Calculate entry ranges, take profit and stop loss levels."""
        try:
            # Calculate ATR for volatility-based levels
            atr = self._calculate_atr(market_data)
            
            if atr == 0:
                logger.warning("ATR is 0, cannot calculate trading levels")
                return None
            
            # Find support and resistance
            levels = self._find_support_resistance(market_data)
            
            # Calculate entry ranges (using ATR and current price)
            # LONG entry: slightly below current price or near support
            entry_long_max = current_price * 0.995  # 0.5% below current
            entry_long_min = max(
                current_price - (atr * 1.5), 
                levels['support'] * 1.01
            )
            
            # SHORT entry: slightly above current price or near resistance
            entry_short_min = current_price * 1.005  # 0.5% above current
            entry_short_max = min(
                current_price + (atr * 1.5),
                levels['resistance'] * 0.99
            )
            
            # Calculate Take Profit levels
            # LONG TP: 2x ATR above entry or near resistance
            take_profit_long = min(
                current_price + (atr * 2.5),
                levels['resistance'] * 0.98
            )
            
            # SHORT TP: 2x ATR below entry or near support
            take_profit_short = max(
                current_price - (atr * 2.5),
                levels['support'] * 1.02
            )
            
            # Calculate Stop Loss levels
            # LONG SL: 1.5x ATR below entry
            stop_loss_long = max(
                current_price - (atr * 1.5),
                levels['support'] * 0.98
            )
            
            # SHORT SL: 1.5x ATR above entry
            stop_loss_short = min(
                current_price + (atr * 1.5),
                levels['resistance'] * 1.02
            )
            
            # Determine confidence based on recommendation strength
            confidence = 0.7
            if recommendation in ["STRONG_BUY", "STRONG_SELL"]:
                confidence = 0.85
            elif recommendation in ["BUY", "SELL"]:
                confidence = 0.75
            
            trading_levels = {
                "entry_long": {
                    "min": round(entry_long_min, 2),
                    "max": round(entry_long_max, 2),
                    "confidence": confidence
                },
                "entry_short": {
                    "min": round(entry_short_min, 2),
                    "max": round(entry_short_max, 2),
                    "confidence": confidence
                },
                "take_profit_long": round(take_profit_long, 2),
                "stop_loss_long": round(stop_loss_long, 2),
                "take_profit_short": round(take_profit_short, 2),
                "stop_loss_short": round(stop_loss_short, 2),
                "atr": round(atr, 2)
            }
            
            logger.info(f"Calculated trading levels with ATR={atr:.2f}")
            return trading_levels
            
        except Exception as e:
            logger.error(f"Error calculating trading levels: {e}")
            return None
    
    def get_supported_symbols(self) -> List[str]:
        """Get list of supported trading symbols."""
        return self.supported_symbols.copy()
    
    def add_supported_symbol(self, symbol: str) -> None:
        """Add a new supported symbol."""
        if symbol not in self.supported_symbols:
            self.supported_symbols.append(symbol)
            logger.info(f"Added supported symbol: {symbol}")
    
    def remove_supported_symbol(self, symbol: str) -> None:
        """Remove a supported symbol."""
        if symbol in self.supported_symbols:
            self.supported_symbols.remove(symbol)
            logger.info(f"Removed supported symbol: {symbol}")


# Global recommendation engine instance
recommendation_engine = RecommendationEngine()
