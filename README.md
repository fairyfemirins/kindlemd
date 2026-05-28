# KindleMD: Convert Kindle Highlights to Markdown

**KindleMD** is a CLI tool to convert Kindle's `My Clippings.txt` into a searchable Markdown notebook. Organize your highlights by book, location, and date, and export them for use in Obsidian, Logseq, or Notion.

## Features
- ✅ **Parse `My Clippings.txt`** into structured data.
- ✅ **Export to Markdown** (one file per book).
- ✅ **Export to JSON** for API use.
- ✅ **Search highlights** by keyword or tag.
- ✅ **Multi-language support** (English, Chinese, Japanese).
- ✅ **Deduplication** (SQLite backend).

## Installation
```bash
pip install --user kindlemd
```

## Usage
### Import Highlights
```bash
kindlemd import-clippings /path/to/My\ Clippings.txt --output-dir ./notes
```

### Search Highlights
```bash
kindlemd search --query "systems" --output-dir ./search_results
```

## Example Output
```markdown
# The Pragmatic Programmer

**Author**: Andrew Hunt, David Thomas

## Location 123-124 | Monday, May 20, 2026

The most damaging phrase in the language is “We’ve always done it this way!”

---
```

## License
MIT