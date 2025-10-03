"""
Backtester Module
Handles the simulation of trades and calculation of performance metrics.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timezone, timedelta
from indicators import calculate_r_multiple
from typing import Dict, List, Optional, Tuple


class BacktestResults:
    """Container for backtest results with validation."""
    
    def __init__(self, trades_df: pd.DataFrame, config: Dict):
        """Initialize results with trades and configuration."""
        self.trades_df = trades_df
        self.config = config
        
        # Validation thresholds
        self.min_win_rate = config.get('min_win_rate', 80.0)  # 80% default
        self.min_pnl = config.get('min_pnl', 0.0)  # >0 default
        self.min_avg_r = config.get('min_avg_r', 1.0)  # 1R default
        
        # Calculate metrics
        self.metrics = self._calculate_metrics()
        self.validation_results = self._validate_results()
    
    def _calculate_metrics(self) -> Dict:
        """Calculate performance metrics."""
        if self.trades_df.empty:
            return {
                'total_trades': 0,
                'win_rate': 0.0,
                'total_pnl': 0.0,
                'avg_r_multiple': 0.0,
                'profit_factor': 0.0,
                'expectancy': 0.0,
                'max_consecutive_losses': 0,
                'green_days_pct': 0.0
            }
        
        # Basic statistics
        total_trades = len(self.trades_df)
        winning_trades = len(self.trades_df[self.trades_df['pnl_usdt'] > 0])
        losing_trades = len(self.trades_df[self.trades_df['pnl_usdt'] < 0])
        
        win_rate = (winning_trades / total_trades) * 100 if total_trades > 0 else 0
        
        # PnL statistics
        total_pnl = self.trades_df['pnl_usdt'].sum()
        avg_win = self.trades_df[self.trades_df['pnl_usdt'] > 0]['pnl_usdt'].mean() if winning_trades > 0 else 0
        avg_loss = self.trades_df[self.trades_df['pnl_usdt'] < 0]['pnl_usdt'].mean() if losing_trades > 0 else 0
        
        # Profit Factor
        gross_profit = self.trades_df[self.trades_df['pnl_usdt'] > 0]['pnl_usdt'].sum()
        gross_loss = abs(self.trades_df[self.trades_df['pnl_usdt'] < 0]['pnl_usdt'].sum())
        profit_factor = gross_profit / gross_loss if gross_loss > 0 else float('inf')
        
        # Expectancy
        expectancy = (winning_trades * avg_win + losing_trades * avg_loss) / total_trades if total_trades > 0 else 0
        
        # R-multiple statistics
        avg_r_multiple = 0.0
        if 'r_multiple' in self.trades_df.columns:
            avg_r_multiple = self.trades_df['r_multiple'].mean()
        
        # Consecutive losses
        max_consecutive_losses = self._calculate_max_consecutive_losses()
        
        # Green days percentage
        daily_pnl = self.trades_df.groupby('day_key')['pnl_usdt'].sum()
        green_days = len(daily_pnl[daily_pnl > 0])
        total_days = len(daily_pnl)
        green_days_pct = (green_days / total_days) * 100 if total_days > 0 else 0
        
        return {
            'total_trades': total_trades,
            'win_rate': win_rate,
            'total_pnl': total_pnl,
            'avg_r_multiple': avg_r_multiple,
            'profit_factor': profit_factor,
            'expectancy': expectancy,
            'max_consecutive_losses': max_consecutive_losses,
            'green_days_pct': green_days_pct,
            'winning_trades': winning_trades,
            'losing_trades': losing_trades,
            'avg_win': avg_win,
            'avg_loss': avg_loss,
            'gross_profit': gross_profit,
            'gross_loss': gross_loss
        }
    
    def _calculate_max_consecutive_losses(self) -> int:
        """Calculate maximum consecutive losing trades."""
        if self.trades_df.empty:
            return 0
        
        consecutive_losses = 0
        max_consecutive = 0
        
        for pnl in self.trades_df['pnl_usdt']:
            if pnl < 0:
                consecutive_losses += 1
                max_consecutive = max(max_consecutive, consecutive_losses)
            else:
                consecutive_losses = 0
        
        return max_consecutive
    
    def _validate_results(self) -> Dict:
        """Validate results against thresholds."""
        validation_results = {
            'is_valid': True,
            'failed_validations': [],
            'warnings': []
        }
        
        # Check win rate
        if self.metrics['win_rate'] < self.min_win_rate:
            validation_results['is_valid'] = False
            validation_results['failed_validations'].append(
                f"Win rate {self.metrics['win_rate']:.1f}% below minimum {self.min_win_rate}%"
            )
        
        # Check PnL
        if self.metrics['total_pnl'] <= self.min_pnl:
            validation_results['is_valid'] = False
            validation_results['failed_validations'].append(
                f"Total PnL {self.metrics['total_pnl']:.2f} USDT below minimum {self.min_pnl} USDT"
            )
        
        # Check average R-multiple
        if self.metrics['avg_r_multiple'] < self.min_avg_r:
            validation_results['is_valid'] = False
            validation_results['failed_validations'].append(
                f"Average R-multiple {self.metrics['avg_r_multiple']:.2f} below minimum {self.min_avg_r}"
            )
        
        # Check minimum trades
        min_trades = self.config.get('min_trades', 10)
        if self.metrics['total_trades'] < min_trades:
            validation_results['warnings'].append(
                f"Only {self.metrics['total_trades']} trades generated (minimum recommended: {min_trades})"
            )
        
        # Check profit factor
        min_profit_factor = self.config.get('min_profit_factor', 1.2)
        if self.metrics['profit_factor'] < min_profit_factor:
            validation_results['warnings'].append(
                f"Profit factor {self.metrics['profit_factor']:.2f} below recommended {min_profit_factor}"
            )
        
        return validation_results
    
    def is_strategy_suitable(self) -> bool:
        """Check if strategy meets all validation criteria."""
        return self.validation_results['is_valid']
    
    def get_validation_summary(self) -> str:
        """Get human-readable validation summary."""
        if self.validation_results['is_valid']:
            summary = "✅ Strategy PASSED validation"
        else:
            summary = "❌ Strategy FAILED validation"
        
        if self.validation_results['failed_validations']:
            summary += "\nFailed validations:"
            for failure in self.validation_results['failed_validations']:
                summary += f"\n  - {failure}"
        
        if self.validation_results['warnings']:
            summary += "\nWarnings:"
            for warning in self.validation_results['warnings']:
                summary += f"\n  - {warning}"
        
        return summary
    
    def display_summary(self):
        """Display comprehensive backtest summary."""
        print("\n" + "=" * 60)
        print("📊 BACKTEST RESULTS SUMMARY")
        print("=" * 60)
        
        # Basic metrics
        print(f"Total Trades: {self.metrics['total_trades']}")
        if self.metrics['total_trades'] > 0:
            print(f"Win Rate: {self.metrics['win_rate']:.1f}% ({self.metrics['winning_trades']}/{self.metrics['total_trades']})")
        else:
            print(f"Win Rate: {self.metrics['win_rate']:.1f}% (0/0)")
        print(f"Total PnL: {self.metrics['total_pnl']:+.2f} USDT")
        print(f"Average R-Multiple: {self.metrics['avg_r_multiple']:.2f}")
        print(f"Profit Factor: {self.metrics['profit_factor']:.2f}")
        print(f"Expectancy: {self.metrics['expectancy']:+.2f} USDT")
        print(f"Max Consecutive Losses: {self.metrics['max_consecutive_losses']}")
        print(f"Green Days: {self.metrics['green_days_pct']:.0f}%")
        
        # Validation results
        print("\n" + "=" * 60)
        print("🔍 VALIDATION RESULTS")
        print("=" * 60)
        print(self.get_validation_summary())
        
        # Strategy breakdown
        if not self.trades_df.empty:
            print("\n" + "=" * 60)
            print("📈 STRATEGY BREAKDOWN")
            print("=" * 60)
            
            if 'strategy_used' in self.trades_df.columns:
                strategy_counts = self.trades_df['strategy_used'].value_counts()
                for strategy, count in strategy_counts.items():
                    print(f"{strategy.upper()}: {count} trades")
            
            if 'used_fallback' in self.trades_df.columns:
                fallback_trades = len(self.trades_df[self.trades_df['used_fallback'] == True])
                print(f"Fallback Trades: {fallback_trades}")
            
            # Exit reasons breakdown
            if 'exit_reason' in self.trades_df.columns:
                print("\nExit Reasons:")
                exit_reasons = self.trades_df['exit_reason'].value_counts()
                for reason, count in exit_reasons.items():
                    print(f"  {reason}: {count}")
        
        print("=" * 60)


class Backtester:
    """Main backtesting engine for the 1 trade per day strategy."""
    
    def __init__(self, strategy, htf_data, ltf_data, config: Optional[Dict] = None):
        """Initialize backtester with strategy and data."""
        self.strategy = strategy
        self.htf_data = htf_data
        self.ltf_data = ltf_data
        self.config = config or {}
        
        # Results storage
        self.trades = []
        self.daily_stats = {}
        
    def run_backtest(self) -> BacktestResults:
        """Run the complete backtest simulation and return results with validation."""
        print("Starting backtest simulation...")
        
        # Group data by day
        ltf_data_daily = self.ltf_data.groupby(self.ltf_data.index.date)
        
        for date, day_data in ltf_data_daily:
            self.simulate_day(date, day_data)
        
        # Convert trades to DataFrame
        trades_df = pd.DataFrame(self.trades)
        
        if not trades_df.empty:
            # Add additional metrics
            trades_df = self.calculate_additional_metrics(trades_df)
        
        # Create and return BacktestResults object
        return BacktestResults(trades_df, self.config)
    
    def simulate_day(self, date, day_data):
        """Simulate trading for a single day."""
        try:
            # Reset daily state
            self.strategy.reset_daily_state()
            
            # Sort data by time
            day_data = day_data.sort_index()
            
            current_trade = None
            break_even_moved = False
            
            for timestamp, candle in day_data.iterrows():
                current_time = timestamp.to_pydatetime()
                
                # Get corresponding HTF data for macro bias
                htf_slice = self.htf_data[self.htf_data.index <= timestamp]
                if htf_slice.empty:
                    continue
                
                # If we have an open trade, check exit conditions
                if current_trade is not None:
                    should_exit, exit_reason, exit_price = self.strategy.should_exit_trade(
                        current_trade, candle['close'], current_time, break_even_moved
                    )
                    
                    if should_exit:
                        # Close trade
                        pnl = self.strategy.calculate_trade_pnl(current_trade, exit_price, exit_reason)
                        
                        # Create trade record
                        trade_record = {
                            'day_key': date.strftime('%Y-%m-%d'),
                            'entry_time': current_trade['entry_time'],
                            'side': current_trade['side'],
                            'entry_price': current_trade['entry_price'],
                            'sl': current_trade['stop_loss'],
                            'tp': current_trade['take_profit'],
                            'exit_time': timestamp,
                            'exit_price': exit_price,
                            'exit_reason': exit_reason,
                            'pnl_usdt': pnl,
                            'position_size': current_trade['position_size'],
                            'strategy_used': current_trade['strategy'],
                            'used_fallback': current_trade['strategy'] != 'orb'
                        }
                        
                        self.trades.append(trade_record)
                        self.strategy.daily_pnl += pnl
                        self.strategy.daily_trades += 1
                        
                        current_trade = None
                        break_even_moved = False
                        
                        # If we've reached daily limits, stop trading for the day
                        if not self.strategy.can_trade_today():
                            break
                
                # If no open trade, look for entry signals
                if current_trade is None and self.strategy.can_trade_today():
                    # Prepare data slice for strategy
                    ltf_slice = self.ltf_data[self.ltf_data.index <= timestamp]
                    if len(ltf_slice) < 50:  # Need enough data for indicators
                        continue
                    
                    signal = self.strategy.get_trade_signal(ltf_slice, htf_slice, current_time)
                    
                    if signal:
                        # Calculate position size
                        position_size = self.strategy.calculate_position_size(
                            signal['entry_price'], signal['stop_loss']
                        )
                        
                        if position_size > 0:
                            # Create trade
                            current_trade = {
                                'entry_time': timestamp,
                                'side': signal['side'],
                                'entry_price': signal['entry_price'],
                                'stop_loss': signal['stop_loss'],
                                'take_profit': signal['take_profit'],
                                'position_size': position_size,
                                'strategy': signal['strategy'],
                                'break_even_price': signal['entry_price']  # Will be updated when moved
                            }
                
                # Check for break-even move (after +1R)
                if current_trade is not None and not break_even_moved:
                    if current_trade['side'] == 'long':
                        r_distance = current_trade['entry_price'] - current_trade['stop_loss']
                        break_even_target = current_trade['entry_price'] + r_distance
                        if candle['close'] >= break_even_target:
                            current_trade['stop_loss'] = current_trade['entry_price']
                            break_even_moved = True
                    else:  # short
                        r_distance = current_trade['stop_loss'] - current_trade['entry_price']
                        break_even_target = current_trade['entry_price'] - r_distance
                        if candle['close'] <= break_even_target:
                            current_trade['stop_loss'] = current_trade['entry_price']
                            break_even_moved = True
            
            # Close any remaining trade at end of day
            if current_trade is not None:
                last_candle = day_data.iloc[-1]
                last_timestamp = day_data.index[-1]
                
                pnl = self.strategy.calculate_trade_pnl(current_trade, last_candle['close'], 'session_end')
                
                trade_record = {
                    'day_key': date.strftime('%Y-%m-%d'),
                    'entry_time': current_trade['entry_time'],
                    'side': current_trade['side'],
                    'entry_price': current_trade['entry_price'],
                    'sl': current_trade['stop_loss'],
                    'tp': current_trade['take_profit'],
                    'exit_time': last_timestamp,
                    'exit_price': last_candle['close'],
                    'exit_reason': 'session_end',
                    'pnl_usdt': pnl,
                    'position_size': current_trade['position_size'],
                    'strategy_used': current_trade['strategy'],
                    'used_fallback': current_trade['strategy'] != 'orb'
                }
                
                self.trades.append(trade_record)
                self.strategy.daily_pnl += pnl
                self.strategy.daily_trades += 1
        
        except Exception as e:
            print(f"Error simulating day {date}: {e}")
    
    def calculate_additional_metrics(self, trades_df):
        """Calculate additional metrics for trades."""
        if trades_df.empty:
            return trades_df
        
        # Calculate R-multiple for each trade
        r_multiples = []
        for _, trade in trades_df.iterrows():
            r_mult = calculate_r_multiple(
                trade['entry_price'], 
                trade['exit_price'], 
                trade['sl'], 
                trade['side']
            )
            r_multiples.append(r_mult)
        
        trades_df['r_multiple'] = r_multiples
        
        return trades_df
    
    def display_summary(self):
        """Display backtest summary statistics (legacy method)."""
        if not self.trades:
            print("\n❌ No trades generated during backtest period.")
            return
        
        trades_df = pd.DataFrame(self.trades)
        
        # Basic statistics
        total_trades = len(trades_df)
        winning_trades = len(trades_df[trades_df['pnl_usdt'] > 0])
        losing_trades = len(trades_df[trades_df['pnl_usdt'] < 0])
        
        win_rate = (winning_trades / total_trades) * 100 if total_trades > 0 else 0
        
        # PnL statistics
        total_pnl = trades_df['pnl_usdt'].sum()
        avg_win = trades_df[trades_df['pnl_usdt'] > 0]['pnl_usdt'].mean() if winning_trades > 0 else 0
        avg_loss = trades_df[trades_df['pnl_usdt'] < 0]['pnl_usdt'].mean() if losing_trades > 0 else 0
        
        # Profit Factor
        gross_profit = trades_df[trades_df['pnl_usdt'] > 0]['pnl_usdt'].sum()
        gross_loss = abs(trades_df[trades_df['pnl_usdt'] < 0]['pnl_usdt'].sum())
        profit_factor = gross_profit / gross_loss if gross_loss > 0 else float('inf')
        
        # Expectancy
        expectancy = (winning_trades * avg_win + losing_trades * avg_loss) / total_trades if total_trades > 0 else 0
        
        # Consecutive losses
        max_consecutive_losses = self.calculate_max_consecutive_losses(trades_df)
        
        # Green days percentage
        daily_pnl = trades_df.groupby('day_key')['pnl_usdt'].sum()
        green_days = len(daily_pnl[daily_pnl > 0])
        total_days = len(daily_pnl)
        green_days_pct = (green_days / total_days) * 100 if total_days > 0 else 0
        
        # Strategy breakdown
        orb_trades = len(trades_df[trades_df['strategy_used'] == 'orb'])
        fallback_trades = len(trades_df[trades_df['used_fallback'] == True])
        
        # Display summary
        print("\n" + "=" * 50)
        print("📊 BACKTEST SUMMARY")
        print("=" * 50)
        print(f"Total Trades: {total_trades}")
        print(f"Win Rate: {win_rate:.1f}% ({winning_trades}/{total_trades})")
        print(f"Profit Factor: {profit_factor:.2f}")
        print(f"Expectancy: {expectancy:+.2f} USDT")
        print(f"Avg Win: {avg_win:+.2f} USDT")
        print(f"Avg Loss: {avg_loss:+.2f} USDT")
        print(f"Max Consecutive Losses: {max_consecutive_losses}")
        print(f"Green Days: {green_days_pct:.0f}% ({green_days}/{total_days})")
        print(f"Total PnL: {total_pnl:+.2f} USDT")
        print("")
        print("Strategy Breakdown:")
        print(f"  ORB Trades: {orb_trades}")
        print(f"  Fallback Trades: {fallback_trades}")
        print("=" * 50)
        
        # Additional metrics
        if 'r_multiple' in trades_df.columns:
            avg_r_multiple = trades_df['r_multiple'].mean()
            print(f"Average R-Multiple: {avg_r_multiple:.2f}")
        
        # Exit reasons breakdown
        exit_reasons = trades_df['exit_reason'].value_counts()
        print("\nExit Reasons:")
        for reason, count in exit_reasons.items():
            print(f"  {reason}: {count}")
    
    def calculate_max_consecutive_losses(self, trades_df):
        """Calculate maximum consecutive losing trades."""
        if trades_df.empty:
            return 0
        
        consecutive_losses = 0
        max_consecutive = 0
        
        for pnl in trades_df['pnl_usdt']:
            if pnl < 0:
                consecutive_losses += 1
                max_consecutive = max(max_consecutive, consecutive_losses)
            else:
                consecutive_losses = 0
        
        return max_consecutive
    
    def get_daily_stats(self):
        """Get daily performance statistics."""
        if not self.trades:
            return pd.DataFrame()
        
        trades_df = pd.DataFrame(self.trades)
        daily_stats = trades_df.groupby('day_key').agg({
            'pnl_usdt': ['sum', 'count'],
            'side': 'first'
        }).round(2)
        
        daily_stats.columns = ['daily_pnl', 'trades_count', 'side']
        daily_stats['is_green'] = daily_stats['daily_pnl'] > 0
        
        return daily_stats

