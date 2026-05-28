"""
KindleMD - Convert Kindle 'My Clippings.txt' to Markdown/JSON.

Usage:
  python3 kindlemd.py import-clippings <file> --output-dir <dir> [--format markdown|json]

Features:
  - Multi-language support (English, Chinese, Japanese).
  - Deduplication via SQLite.
  - Markdown/JSON export.
"""

import re
import sqlite3
import click
from pathlib import Path
from datetime import datetime

# Regex for parsing Kindle clippings (multi-language)
CLIPPING_REGEX = re.compile(
    r'^(.+?) \((.+?)\)\n'  # Title (Author)
    r'^- Your (?:Highlight|Note|Bookmark) on (?:Location|位置|Page) (.+?)(?: \| Added on )?(.*)$\n'  # Metadata
    r'\n'  # Empty line
    r'(.+?)\n'  # Content
    r'==========$',  # Separator
    re.MULTILINE
)

@click.group()
def cli():
    """KindleMD CLI"""
    pass

@cli.command()
def init_db():
    """Initialize SQLite database for deduplication."""
    conn = sqlite3.connect('kindlemd.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS clippings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            author TEXT NOT NULL,
            location TEXT NOT NULL,
            timestamp TEXT NOT NULL,
            content TEXT NOT NULL,
            UNIQUE(title, author, location, content)
        )
    ''')
    conn.commit()
    conn.close()
    click.echo("Database initialized.")

@cli.command()
@click.argument('file', type=click.Path(exists=True))
@click.option('--output-dir', type=click.Path(), default='./output', help='Output directory')
@click.option('--format', type=click.Choice(['markdown', 'json']), default='markdown', help='Output format')
def import_clippings(file, output_dir, format):
    """Import Kindle clippings from file."""
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect('kindlemd.db')
    cursor = conn.cursor()

    with open(file, 'r', encoding='utf-8-sig') as f:
        content = f.read()
    clippings = CLIPPING_REGEX.findall(content)

    for clipping in clippings:
        title, author, location, timestamp, content = clipping
        try:
            cursor.execute('''
                INSERT INTO clippings (title, author, location, timestamp, content)
                VALUES (?, ?, ?, ?, ?)
            ''', (title, author, location, timestamp, content))
            conn.commit()
        except sqlite3.IntegrityError:
            continue  # Skip duplicates

        # Export to Markdown/JSON
        if format == 'markdown':
            output_file = Path(output_dir) / f"{slugify(title)}.md"
            with open(output_file, 'a', encoding='utf-8') as f:
                f.write(f"# {title}\n\n**Author:** {author}\n\n**Location:** {location}\n\n**Timestamp:** {timestamp}\n\n> {content}\n\n---\n")
        elif format == 'json':
            output_file = Path(output_dir) / f"{slugify(title)}.json"
            with open(output_file, 'a', encoding='utf-8') as f:
                import json
                json.dump({
                    "title": title,
                    "author": author,
                    "location": location,
                    "timestamp": timestamp,
                    "content": content
                }, f, ensure_ascii=False, indent=2)

    conn.close()
    click.echo(f"Processed {len(clippings)} clippings. Output: {output_dir}")

def slugify(text):
    """Convert text to a safe filename."""
    return re.sub(r'[^a-zA-Z0-9]+', '_', text).strip('_')

if __name__ == '__main__':
    cli()