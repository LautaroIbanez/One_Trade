"""Tests for UI banner logic. Parametrises scenarios: no open position (OK), reversal suggestion (warning), aligned positions (OK), invalid signal payload (error)."""
import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from ui import determine_signal_banner


@pytest.mark.parametrize("today_signal,open_position,expected_level,description", [
    (None, None, 'ok', "No signal, no position"),
    (None, 'long', 'ok', "No signal, long position open"),
    ({}, None, 'ok', "Empty signal dict, no position"),
    ({'valid': False, 'reason': 'no_data'}, None, 'ok', "Invalid signal (no_data), no position"),
    ({'valid': False, 'reason': 'no_alignment'}, 'short', 'ok', "Invalid signal (no_alignment), short position"),
    ({'valid': True, 'side': 'long', 'entry_price': 50000, 'sl': 49000, 'tp': 51500}, None, 'ok', "Valid long signal, no position"),
    ({'valid': True, 'side': 'short', 'entry_price': 50000, 'sl': 51000, 'tp': 48500}, 'flat', 'ok', "Valid short signal, flat position"),
    ({'valid': True, 'side': 'long', 'entry_price': 50000, 'sl': 49000, 'tp': 51500}, 'long', 'ok', "Long signal aligns with long position"),
    ({'valid': True, 'side': 'short', 'entry_price': 50000, 'sl': 51000, 'tp': 48500}, 'short', 'ok', "Short signal aligns with short position"),
    ({'valid': True, 'side': 'long', 'entry_price': 50000, 'sl': 49000, 'tp': 51500}, 'short', 'warning', "Long signal reversal (short position open)"),
    ({'valid': True, 'side': 'short', 'entry_price': 50000, 'sl': 51000, 'tp': 48500}, 'long', 'warning', "Short signal reversal (long position open)"),
    ({'valid': True, 'side': 'invalid_side', 'entry_price': 50000, 'sl': 49000, 'tp': 51500}, None, 'error', "Invalid signal side"),
    ({'valid': True, 'side': 'long', 'entry_price': None, 'sl': 49000, 'tp': 51500}, None, 'error', "Missing entry_price"),
    ({'valid': True, 'side': 'long', 'entry_price': 0, 'sl': 49000, 'tp': 51500}, None, 'error', "Zero entry_price"),
    ({'valid': True, 'side': 'long', 'entry_price': -50000, 'sl': 49000, 'tp': 51500}, None, 'error', "Negative entry_price"),
    ({'valid': True, 'side': 'long', 'entry_price': 50000, 'sl': None, 'tp': 51500}, None, 'error', "Missing stop_loss"),
    ({'valid': True, 'side': 'long', 'entry_price': 50000, 'sl': 49000, 'tp': None}, None, 'error', "Missing take_profit"),
    ({'valid': True, 'side': 'long', 'entry_price': 50000, 'sl': 0, 'tp': 51500}, None, 'error', "Zero stop_loss"),
    ({'valid': True, 'side': 'long', 'entry_price': 50000, 'sl': 49000, 'tp': 0}, None, 'error', "Zero take_profit"),
])
def test_signal_banner_scenarios(today_signal, open_position, expected_level, description):
    """Test all banner scenarios with parametrized inputs."""
    result = determine_signal_banner(today_signal, open_position)
    assert isinstance(result, dict), f"{description}: Should return dict"
    assert 'level' in result, f"{description}: Should have 'level' key"
    assert 'message' in result, f"{description}: Should have 'message' key"
    assert result['level'] == expected_level, f"{description}: Expected level '{expected_level}', got '{result['level']}' - {result['message']}"
    print(f"✓ {description}: level={result['level']}, message='{result['message']}'")


def test_banner_message_content():
    """Test that banner messages contain expected information."""
    signal = {'valid': True, 'side': 'long', 'entry_price': 50000, 'sl': 49000, 'tp': 51500}
    result = determine_signal_banner(signal, None)
    assert 'LONG' in result['message'] or 'long' in result['message'], "Message should mention signal side"
    assert '50000' in result['message'], "Message should mention entry price"
    result_reversal = determine_signal_banner(signal, 'short')
    assert 'Reversal' in result_reversal['message'] or 'reversal' in result_reversal['message'], "Reversal message should indicate reversal"
    assert 'warning' in result_reversal['message'].lower() or '⚠' in result_reversal['message'], "Reversal should have warning indicator"
    print(f"✓ Banner messages contain expected content")


def test_banner_handles_case_insensitivity():
    """Test that position side comparison is case-insensitive."""
    signal = {'valid': True, 'side': 'long', 'entry_price': 50000, 'sl': 49000, 'tp': 51500}
    result_lower = determine_signal_banner(signal, 'long')
    result_upper = determine_signal_banner(signal, 'LONG')
    result_mixed = determine_signal_banner(signal, 'Long')
    assert result_lower['level'] == 'ok', "Lowercase position should work"
    assert result_upper['level'] == 'ok', "Uppercase position should work"
    assert result_mixed['level'] == 'ok', "Mixed case position should work"
    print(f"✓ Banner handles case-insensitive position sides")


def test_banner_logs_context():
    """Test that banner function logs appropriate context (manual verification of logs)."""
    signal_ok = {'valid': True, 'side': 'long', 'entry_price': 50000, 'sl': 49000, 'tp': 51500}
    signal_reversal = {'valid': True, 'side': 'short', 'entry_price': 50000, 'sl': 51000, 'tp': 48500}
    signal_invalid = {'valid': True, 'side': 'invalid', 'entry_price': 50000, 'sl': 49000, 'tp': 51500}
    result1 = determine_signal_banner(signal_ok, None)
    assert result1['level'] == 'ok'
    result2 = determine_signal_banner(signal_reversal, 'long')
    assert result2['level'] == 'warning'
    result3 = determine_signal_banner(signal_invalid, None)
    assert result3['level'] == 'error'
    print(f"✓ Banner logs context appropriately (check logs for signal_ok_no_position, signal_reversal, error messages)")


if __name__ == '__main__':
    pytest.main([__file__, '-v', '-s'])

