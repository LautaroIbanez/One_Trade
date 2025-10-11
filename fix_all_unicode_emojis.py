"""Fix all Unicode emoji encoding issues across the backtester codebase."""
import re
from pathlib import Path

emoji_replacements = {'🚀': '[START]', '📊': '[DATA]', '✅': '[OK]', '🔄': '[RUN]', '⚠️': '[WARN]', '❌': '[ERROR]', '📈': '[CHART]', '💰': '[MONEY]', '📉': '[DOWN]', '🎯': '[TARGET]', '🔴': '[FAIL]', '🟢': '[PASS]', '⏸️': '[PAUSE]', '💡': '[INFO]', '📂': '[FOLDER]', '🔐': '[SECURE]', '⚡': '[FAST]', '📝': '[WRITE]', '🔎': '[SEARCH]', '💾': '[SAVE]', '🧪': '[TEST]', '🏁': '[FINISH]', '📋': '[LIST]'}

base_dir = Path(__file__).parent
files_to_fix = [base_dir / "btc_1tpd_backtester" / "btc_1tpd_backtest_final.py", base_dir / "btc_1tpd_backtester" / "strategies" / "mode_strategies.py", base_dir / "webapp" / "app.py", base_dir / "btc_1tpd_backtester" / "utils.py"]

total_changes = 0
for file_path in files_to_fix:
    if not file_path.exists():
        print(f"Skipping {file_path.name} (not found)")
        continue
    print(f"\nProcessing {file_path}...")
    try:
        content = file_path.read_text(encoding='utf-8')
        file_changes = 0
        for emoji, replacement in emoji_replacements.items():
            count = content.count(emoji)
            if count > 0:
                content = content.replace(emoji, replacement)
                file_changes += count
                print(f"  Replaced {count} instances of '{emoji}' with '{replacement}'")
        if file_changes > 0:
            file_path.write_text(content, encoding='utf-8')
            print(f"  ✓ Fixed {file_changes} emoji instances")
            total_changes += file_changes
        else:
            print(f"  No emojis found")
    except Exception as e:
        print(f"  ✗ Error processing {file_path.name}: {e}")

print(f"\n{'='*60}")
print(f"Total: Fixed {total_changes} emoji instances across {len(files_to_fix)} files")
print(f"{'='*60}")




