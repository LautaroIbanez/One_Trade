"""Recursively fix all Unicode emojis in Python files."""
from pathlib import Path

emojis = {'🚀': '[START]', '📊': '[DATA]', '✅': '[OK]', '🔄': '[RUN]', '⚠️': '[WARN]', '❌': '[ERROR]', '📈': '[CHART]', '💰': '[MONEY]', '📉': '[DOWN]', '🎯': '[TARGET]', '🔴': '[FAIL]', '🟢': '[PASS]', '⏸️': '[PAUSE]', '💡': '[INFO]', '📂': '[FOLDER]', '🔐': '[SECURE]', '⚡': '[FAST]', '📝': '[WRITE]', '🔎': '[SEARCH]', '💾': '[SAVE]', '🧪': '[TEST]', '🏁': '[FINISH]', '📋': '[LIST]', '🔍': '[SEARCH2]', '💸': '[PROFIT]', '📉': '[LOSS]', '🎉': '[CELEBRATE]'}

base = Path('.')
py_files = list(base.glob('btc_1tpd_backtester/**/*.py')) + list(base.glob('webapp/**/*.py'))

total_changes = 0
files_changed = 0

for file_path in py_files:
    try:
        content = file_path.read_text(encoding='utf-8')
        file_changes = 0
        for emoji, replacement in emojis.items():
            count = content.count(emoji)
            if count > 0:
                content = content.replace(emoji, replacement)
                file_changes += count
        if file_changes > 0:
            file_path.write_text(content, encoding='utf-8')
            total_changes += file_changes
            files_changed += 1
            print(f"Fixed {file_changes} emojis in {file_path}")
    except Exception as e:
        print(f"Error: {file_path}: {e}")

print(f"\nTotal: Fixed {total_changes} emojis in {files_changed} files ({len(py_files)} scanned)")










