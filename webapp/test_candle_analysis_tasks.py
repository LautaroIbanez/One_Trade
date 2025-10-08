"""Test suite for annual candle analysis enhancements. This module tests the date-range helper and candle analysis tasks builder to ensure minimum 365-day coverage and proper task generation across modes and inversion states."""
import pytest
from datetime import datetime, timedelta, timezone
from webapp.app import determine_price_date_range, build_candle_analysis_tasks


class TestDeterminePriceDateRange:
    """Test cases for determine_price_date_range helper function."""
    
    def test_no_since_date_returns_365_days(self):
        """Test that when no since_date is provided, returns exactly 365 days of coverage."""
        symbol = "BTC/USDT:USDT"
        start_date, end_date = determine_price_date_range(symbol, since_date=None, lookback_days=365)
        days_diff = (end_date.date() - start_date.date()).days
        assert days_diff == 365, f"Expected 365 days, got {days_diff}"
        assert start_date.tzinfo == timezone.utc, "Start date should be UTC aware"
        assert end_date.tzinfo == timezone.utc, "End date should be UTC aware"
    
    def test_short_since_date_expanded_to_365_days(self):
        """Test that a since_date less than 365 days ago is expanded to 365 days."""
        symbol = "BTC/USDT:USDT"
        recent_date = (datetime.now(timezone.utc) - timedelta(days=100)).date().isoformat()
        start_date, end_date = determine_price_date_range(symbol, since_date=recent_date, lookback_days=365)
        days_diff = (end_date.date() - start_date.date()).days
        assert days_diff >= 365, f"Expected at least 365 days, got {days_diff}"
        assert start_date.tzinfo == timezone.utc, "Start date should be UTC aware"
        assert end_date.tzinfo == timezone.utc, "End date should be UTC aware"
    
    def test_valid_since_date_preserved(self):
        """Test that a since_date more than 365 days ago is preserved."""
        symbol = "BTC/USDT:USDT"
        old_date = (datetime.now(timezone.utc) - timedelta(days=500)).date().isoformat()
        start_date, end_date = determine_price_date_range(symbol, since_date=old_date, lookback_days=365)
        days_diff = (end_date.date() - start_date.date()).days
        assert days_diff >= 365, f"Expected at least 365 days, got {days_diff}"
        assert start_date.date().isoformat() == old_date, f"Expected start_date to match {old_date}"
        assert start_date.tzinfo == timezone.utc, "Start date should be UTC aware"
        assert end_date.tzinfo == timezone.utc, "End date should be UTC aware"
    
    def test_invalid_since_date_falls_back_to_lookback(self):
        """Test that an invalid since_date falls back to lookback_days."""
        symbol = "BTC/USDT:USDT"
        invalid_date = "not-a-date"
        start_date, end_date = determine_price_date_range(symbol, since_date=invalid_date, lookback_days=365)
        days_diff = (end_date.date() - start_date.date()).days
        assert days_diff == 365, f"Expected 365 days fallback, got {days_diff}"
    
    def test_custom_lookback_days(self):
        """Test that custom lookback_days parameter works correctly."""
        symbol = "BTC/USDT:USDT"
        start_date, end_date = determine_price_date_range(symbol, since_date=None, lookback_days=730)
        days_diff = (end_date.date() - start_date.date()).days
        assert days_diff == 730, f"Expected 730 days, got {days_diff}"
    
    def test_timezone_awareness(self):
        """Test that returned datetimes are timezone-aware (UTC)."""
        symbol = "BTC/USDT:USDT"
        start_date, end_date = determine_price_date_range(symbol, since_date=None, lookback_days=365)
        assert start_date.tzinfo is not None, "Start date must be timezone-aware"
        assert end_date.tzinfo is not None, "End date must be timezone-aware"
        assert start_date.tzinfo == timezone.utc, "Start date must be UTC"
        assert end_date.tzinfo == timezone.utc, "End date must be UTC"


class TestBuildCandleAnalysisTasks:
    """Test cases for build_candle_analysis_tasks helper function."""
    
    @pytest.mark.parametrize("mode", ["conservative", "moderate", "aggressive"])
    def test_all_modes_return_tasks(self, mode):
        """Test that all modes return a non-empty list of tasks."""
        tasks = build_candle_analysis_tasks(mode, inverted=False)
        assert isinstance(tasks, list), "Should return a list"
        assert len(tasks) > 0, f"Mode {mode} should return tasks"
    
    @pytest.mark.parametrize("mode", ["conservative", "moderate", "aggressive"])
    def test_task_structure(self, mode):
        """Test that each task has required fields: title, description, priority."""
        tasks = build_candle_analysis_tasks(mode, inverted=False)
        for task in tasks:
            assert "title" in task, "Task must have 'title' field"
            assert "description" in task, "Task must have 'description' field"
            assert "priority" in task, "Task must have 'priority' field"
            assert isinstance(task["title"], str), "Title must be a string"
            assert isinstance(task["description"], str), "Description must be a string"
            assert isinstance(task["priority"], int), "Priority must be an integer"
    
    @pytest.mark.parametrize("mode", ["conservative", "moderate", "aggressive"])
    def test_priority_scale(self, mode):
        """Test that priorities stay within agreed scale (1-3)."""
        tasks = build_candle_analysis_tasks(mode, inverted=False)
        for task in tasks:
            assert 1 <= task["priority"] <= 3, f"Priority {task['priority']} out of range (1-3)"
    
    def test_inverted_flag_changes_descriptions(self):
        """Test that inverted=True adds inversion notes to descriptions."""
        mode = "moderate"
        tasks_normal = build_candle_analysis_tasks(mode, inverted=False)
        tasks_inverted = build_candle_analysis_tasks(mode, inverted=True)
        assert len(tasks_normal) == len(tasks_inverted), "Same number of tasks in both modes"
        for normal, inverted in zip(tasks_normal, tasks_inverted):
            assert normal["title"] == inverted["title"], "Titles should match"
            if "invertida" in inverted["description"]:
                assert "invertida" not in normal["description"], "Normal mode should not mention inversion"
    
    @pytest.mark.parametrize("mode", ["conservative", "moderate", "aggressive"])
    def test_base_tasks_present(self, mode):
        """Test that base tasks (validation, patterns) are present in all modes."""
        tasks = build_candle_analysis_tasks(mode, inverted=False)
        titles = [task["title"] for task in tasks]
        assert any("Validar cobertura" in title for title in titles), "Should have data coverage validation task"
        assert any("patrones de largo plazo" in title for title in titles), "Should have long-term patterns task"
    
    def test_conservative_mode_specific_tasks(self):
        """Test that conservative mode includes mean reversion specific tasks."""
        tasks = build_candle_analysis_tasks("conservative", inverted=False)
        descriptions = [task["description"] for task in tasks]
        assert any("Bollinger" in desc or "RSI" in desc for desc in descriptions), "Conservative should mention Bollinger/RSI"
        assert any("reversión" in desc for desc in descriptions), "Conservative should mention mean reversion"
    
    def test_moderate_mode_specific_tasks(self):
        """Test that moderate mode includes trend following specific tasks."""
        tasks = build_candle_analysis_tasks("moderate", inverted=False)
        descriptions = [task["description"] for task in tasks]
        assert any("EMA" in desc or "ADX" in desc or "Heikin Ashi" in desc for desc in descriptions), "Moderate should mention EMA/ADX/Heikin Ashi"
        assert any("tendencia" in desc for desc in descriptions), "Moderate should mention trend"
    
    def test_aggressive_mode_specific_tasks(self):
        """Test that aggressive mode includes breakout fade specific tasks."""
        tasks = build_candle_analysis_tasks("aggressive", inverted=False)
        descriptions = [task["description"] for task in tasks]
        assert any("breakout" in desc or "fakeout" in desc for desc in descriptions), "Aggressive should mention breakouts/fakeouts"
        assert any("volatilidad" in desc or "RSI extremo" in desc for desc in descriptions), "Aggressive should mention volatility/extreme RSI"
    
    def test_unknown_mode_defaults_to_moderate(self):
        """Test that an unknown mode defaults to moderate tasks."""
        tasks_unknown = build_candle_analysis_tasks("unknown_mode", inverted=False)
        tasks_moderate = build_candle_analysis_tasks("moderate", inverted=False)
        assert len(tasks_unknown) == len(tasks_moderate), "Unknown mode should default to moderate"
    
    def test_case_insensitivity(self):
        """Test that mode parameter is case-insensitive."""
        tasks_lower = build_candle_analysis_tasks("conservative", inverted=False)
        tasks_upper = build_candle_analysis_tasks("CONSERVATIVE", inverted=False)
        tasks_mixed = build_candle_analysis_tasks("Conservative", inverted=False)
        assert len(tasks_lower) == len(tasks_upper) == len(tasks_mixed), "Mode should be case-insensitive"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

