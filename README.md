# KindleMD

Convert Kindle "My Clippings.txt" to structured Markdown/JSON.

## Features
- Multi-language support (English, Chinese, Japanese).
- Deduplication via SQLite.
- Markdown/JSON export.

## Installation
```bash
pip install click
```

## Usage
```bash
python3 kindlemd.py init-db
python3 kindlemd.py import-clippings "My Clippings.txt" --output-dir ./notes
```

## Example Output
```markdown
# The Pragmatic Programmer

**Author:** Andrew Hunt, David Thomas

**Location:** 123-124

**Timestamp:** Tuesday, May 26, 2026 10:00:00 AM

> The most damaging phrase in the language is "We've always done it this way!"
```

## License
MIT