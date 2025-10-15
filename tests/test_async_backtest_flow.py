"""Tests for async backtest flow in interactive webapp."""
import unittest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from webapp_v2.interactive_app import run_backtest_async, log_backtest_performance


class TestAsyncBacktestFlow(unittest.TestCase):
    """Test suite for async backtest execution flow."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.symbol = "BTC/USDT"
        self.strategy = "baseline"
        self.start_date = "2024-01-01"
        self.end_date = "2024-12-31"
        self.timestamp = str(datetime.now().timestamp())
    
    @patch('webapp_v2.interactive_app.get_engine_from_pool')
    @patch('webapp_v2.interactive_app.log_backtest_performance')
    @patch('webapp_v2.interactive_app.invalidate_cache')
    def test_successful_backtest_with_valid_metrics(self, mock_invalidate, mock_log_perf, mock_get_engine):
        """Test successful backtest execution with valid metrics."""
        mock_metrics = Mock()
        mock_metrics.total_trades = 10
        mock_metrics.total_return = 1500.0
        mock_metrics.win_rate = 60.0
        mock_metrics.profit_factor = 1.5
        mock_metrics.final_equity = 11500.0
        mock_metrics.total_return_pct = 15.0
        mock_engine = Mock()
        mock_engine.run_backtest.return_value = {"symbol": self.symbol, "trades": [], "metrics": mock_metrics, "equity_curve": Mock(), "start_date": self.start_date, "end_date": self.end_date, "elapsed_time": 5.5}
        mock_get_engine.return_value = mock_engine
        result = run_backtest_async(self.symbol, self.strategy, self.start_date, self.end_date, self.timestamp)
        self.assertTrue(result["success"])
        self.assertEqual(result["results"]["symbol"], self.symbol)
        self.assertEqual(result["results"]["metrics"].total_trades, 10)
        mock_log_perf.assert_called_once()
        call_args = mock_log_perf.call_args[0]
        self.assertEqual(call_args[0], self.symbol)
        self.assertEqual(call_args[1], self.strategy)
        self.assertEqual(call_args[4], 5.5)
        self.assertEqual(call_args[5], 10)
        self.assertTrue(call_args[6])
        mock_invalidate.assert_called_once()
    
    @patch('webapp_v2.interactive_app.get_engine_from_pool')
    @patch('webapp_v2.interactive_app.log_backtest_performance')
    def test_backtest_with_no_data_error(self, mock_log_perf, mock_get_engine):
        """Test backtest handling when no data is available."""
        mock_engine = Mock()
        mock_engine.run_backtest.return_value = {"error": "No data available for BTC/USDT 15m in range 2024-01-01 to 2024-12-31", "error_code": "NO_DATA", "symbol": self.symbol, "start_date": self.start_date, "end_date": self.end_date, "elapsed_time": 0.5}
        mock_get_engine.return_value = mock_engine
        result = run_backtest_async(self.symbol, self.strategy, self.start_date, self.end_date, self.timestamp)
        self.assertFalse(result["success"])
        self.assertEqual(result["error_code"], "NO_DATA")
        self.assertEqual(result["error_title"], "Datos insuficientes")
        self.assertIn("No data available", result["error"])
        mock_log_perf.assert_called_once()
        call_args = mock_log_perf.call_args[0]
        self.assertFalse(call_args[6])
        self.assertIn("No data available", call_args[7])
    
    @patch('webapp_v2.interactive_app.get_engine_from_pool')
    @patch('webapp_v2.interactive_app.log_backtest_performance')
    def test_backtest_with_metrics_none_error(self, mock_log_perf, mock_get_engine):
        """Test backtest handling when metrics calculation returns None."""
        mock_engine = Mock()
        mock_engine.run_backtest.return_value = {"error": "Metrics calculation returned None", "error_code": "METRICS_NONE", "symbol": self.symbol, "start_date": self.start_date, "end_date": self.end_date, "elapsed_time": 3.0}
        mock_get_engine.return_value = mock_engine
        result = run_backtest_async(self.symbol, self.strategy, self.start_date, self.end_date, self.timestamp)
        self.assertFalse(result["success"])
        self.assertEqual(result["error_code"], "METRICS_NONE")
        self.assertEqual(result["error_title"], "Error al calcular métricas")
        mock_log_perf.assert_called_once()
    
    @patch('webapp_v2.interactive_app.get_engine_from_pool')
    @patch('webapp_v2.interactive_app.log_backtest_performance')
    def test_backtest_with_exception(self, mock_log_perf, mock_get_engine):
        """Test backtest handling when engine raises an exception."""
        mock_engine = Mock()
        mock_engine.run_backtest.side_effect = ValueError("Invalid configuration")
        mock_get_engine.return_value = mock_engine
        result = run_backtest_async(self.symbol, self.strategy, self.start_date, self.end_date, self.timestamp)
        self.assertFalse(result["success"])
        self.assertEqual(result["error_code"], "ASYNC_EXCEPTION")
        self.assertIn("Invalid configuration", result["error"])
        mock_log_perf.assert_called_once()
        call_args = mock_log_perf.call_args[0]
        self.assertFalse(call_args[6])
    
    @patch('webapp_v2.interactive_app.get_engine_from_pool')
    @patch('webapp_v2.interactive_app.log_backtest_performance')
    def test_backtest_with_invalid_metrics_error(self, mock_log_perf, mock_get_engine):
        """Test backtest handling when metrics object is invalid."""
        mock_engine = Mock()
        mock_engine.run_backtest.return_value = {"error": "Metrics object missing total_trades attribute", "error_code": "INVALID_METRICS", "symbol": self.symbol, "start_date": self.start_date, "end_date": self.end_date, "elapsed_time": 2.5}
        mock_get_engine.return_value = mock_engine
        result = run_backtest_async(self.symbol, self.strategy, self.start_date, self.end_date, self.timestamp)
        self.assertFalse(result["success"])
        self.assertEqual(result["error_code"], "INVALID_METRICS")
        self.assertEqual(result["error_title"], "Métricas inválidas")
        mock_log_perf.assert_called_once()
    
    @patch('webapp_v2.interactive_app.get_engine_from_pool')
    @patch('webapp_v2.interactive_app.log_backtest_performance')
    def test_backtest_with_exception_error_code(self, mock_log_perf, mock_get_engine):
        """Test backtest handling when engine returns EXCEPTION error code."""
        mock_engine = Mock()
        mock_engine.run_backtest.return_value = {"error": "Backtest failed: KeyError: 'close'", "error_code": "EXCEPTION", "symbol": self.symbol, "start_date": self.start_date, "end_date": self.end_date, "elapsed_time": 1.0}
        mock_get_engine.return_value = mock_engine
        result = run_backtest_async(self.symbol, self.strategy, self.start_date, self.end_date, self.timestamp)
        self.assertFalse(result["success"])
        self.assertEqual(result["error_code"], "EXCEPTION")
        self.assertEqual(result["error_title"], "Error crítico")
        self.assertIn("KeyError", result["error"])
        mock_log_perf.assert_called_once()


class TestPerformanceLogging(unittest.TestCase):
    """Test suite for performance logging functionality."""
    
    @patch('webapp_v2.interactive_app.pd.DataFrame.to_csv')
    @patch('webapp_v2.interactive_app.Path.exists')
    def test_log_backtest_performance_success(self, mock_exists, mock_to_csv):
        """Test performance logging for successful backtest."""
        mock_exists.return_value = True
        log_backtest_performance("BTC/USDT", "baseline", "2024-01-01", "2024-12-31", 10.5, 15, True)
        mock_to_csv.assert_called_once()
        call_kwargs = mock_to_csv.call_args[1]
        self.assertEqual(call_kwargs['mode'], 'a')
        self.assertFalse(call_kwargs['header'])
    
    @patch('webapp_v2.interactive_app.pd.DataFrame.to_csv')
    @patch('webapp_v2.interactive_app.Path.exists')
    def test_log_backtest_performance_failure(self, mock_exists, mock_to_csv):
        """Test performance logging for failed backtest."""
        mock_exists.return_value = False
        log_backtest_performance("BTC/USDT", "baseline", "2024-01-01", "2024-12-31", 0, 0, False, "No data available")
        mock_to_csv.assert_called_once()
        call_kwargs = mock_to_csv.call_args[1]
        self.assertEqual(call_kwargs['mode'], 'w')
        self.assertTrue(call_kwargs['header'])


if __name__ == "__main__":
    unittest.main()







