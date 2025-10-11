"""Fix Unicode emoji encoding issues in print statements by replacing emojis with ASCII equivalents."""
import re
from pathlib import Path

file_to_fix = Path(__file__).parent / "btc_1tpd_backtester" / "btc_1tpd_backtest_final.py"

emoji_replacements = {
    '🚀': '[START]',
    '📊': '[DATA]',
    '✅': '[OK]',
    '🔄': '[RUN]',
    '⚠️': '[WARN]',
    '❌': '[ERROR]',
    '📈': '[CHART]',
    '💰': '[MONEY]',
    '📉': '[DOWN]',
    '🎯': '[TARGET]',
    '🔴': '[FAIL]',
    '🟢': '[PASS]',
    '⏸️': '[PAUSE]',
    '🔄': '[REFRESH]',
    '💡': '[INFO]',
    '📂': '[FOLDER]',
    '🔐': '[SECURE]',
    '⚡': '[FAST]',
}

print(f"Reading {file_to_fix}...")
content = file_to_fix.read_text(encoding='utf-8')

changes_made = 0
for emoji, replacement in emoji_replacements.items():
    count = content.count(emoji)
    if count > 0:
        content = content.replace(emoji, replacement)
        changes_made += count
        print(f"  Replaced {count} instances of '{emoji}' with '{replacement}'")

if changes_made > 0:
    file_to_fix.write_text(content, encoding='utf-8')
    print(f"\n✓ Fixed {changes_made} emoji instances in {file_to_fix.name}")
else:
    print(f"\nNo emojis found in {file_to_fix.name}")

print("\nDone!")




