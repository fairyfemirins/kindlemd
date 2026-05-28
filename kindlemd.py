#!/usr/bin/env python3
"""
KindleMD: Convert Kindle Highlights to Markdown

Usage:
    python3 kindlemd.py import-clippings /path/to/My\\ Clippings.txt --output-dir ./notes
"""

import re
import json
import sqlite3
import click
import os
from dataclasses import dataclass
from typing import List, Optional
from pathlib import Path


@dataclass
class Highlight:
    book_title: str
    author: str
    location: str
    date: str
    text: str
    tags: Optional[List[str]] = None
    
    def __post_init__(self):
        if self.tags is None:
            self.tags = []


def parse_clippings(file_path: str) -> List[Highlight]:
    """Parse My Clippings.txt and return a list of Highlight objects."""
    with open(file_path, 'r', encoding='utf-8-sig') as file:
        content = file.read()
    
    entries = content.split('==========')
    highlights = []
    
    for entry in entries:
        entry = entry.strip()
        if not entry:
            continue
        
        lines = entry.split('\n')
        if len(lines) < 3:
            continue
        
        title_author_match = re.match(r'^(.+) \((.+)\)$', lines[0].strip())
        if not title_author_match:
            title_author_match = re.match(r'^(.+)$', lines[0].strip())
            if not title_author_match:
                continue
            book_title = title_author_match.group(1)
            author = "Unknown Author"
        else:
            book_title, author = title_author_match.groups()
        
        meta_match = re.match(r'^- Your (?:Highlight|Note|Bookmark) on (?:Location|位置|Page) (.+?)(?: \| Added on )?(.*)$', lines[1].strip())
        if not meta_match:
            meta_match = re.match(r'^- Your (?:Highlight|Note|Bookmark) on (.+)$', lines[1].strip())
            if not meta_match:
                continue
            location = meta_match.group(1)
            date = "Unknown Date"
        else:
            location, date = meta_match.groups()
        
        text = '\n'.join(lines[2:]).strip()
        
        highlights.append(Highlight(
            book_title=book_title,
            author=author,
            location=location,
            date=date,
            text=text,
            tags=[]
        ))
    
    return highlights


def init_db(db_path: str) -> None:
    """Initialize the SQLite database."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS highlights (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            book_title TEXT NOT NULL,
            author TEXT NOT NULL,
            location TEXT NOT NULL,
            date TEXT NOT NULL,
            text TEXT NOT NULL
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tags (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            highlight_id INTEGER NOT NULL,
            tag TEXT NOT NULL,
            FOREIGN KEY (highlight_id) REFERENCES highlights (id)
        )
    """)
    conn.commit()
    conn.close()


def insert_highlight(db_path: str, highlight: Highlight) -> None:
    """Insert a highlight into the database."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO highlights (book_title, author, location, date, text)
        VALUES (?, ?, ?, ?, ?)
    """, (highlight.book_title, highlight.author, highlight.location, highlight.date, highlight.text))
    highlight_id = cursor.lastrowid
    
    for tag in highlight.tags or []:
        cursor.execute("""
            INSERT INTO tags (highlight_id, tag)
            VALUES (?, ?)
        """, (highlight_id, tag))
    
    conn.commit()
    conn.close()


def export_to_markdown(highlights: List[Highlight], output_dir: str) -> None:
    """Export highlights to markdown files (one per book)."""
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    books = {}
    for highlight in highlights:
        if highlight.book_title not in books:
            books[highlight.book_title] = []
        books[highlight.book_title].append(highlight)
    
    for book_title, book_highlights in books.items():
        safe_title = "".join(c for c in book_title if c.isalnum() or c in (' ', '_')).rstrip()
        file_path = os.path.join(output_dir, f"{safe_title}.md")
        
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(f"# {book_title}\n\n")
            file.write(f"**Author**: {book_highlights[0].author}\n\n")
            
            for highlight in book_highlights:
                file.write(f"## Location {highlight.location} | {highlight.date}\n")
                if highlight.tags:
                    file.write(f"**Tags**: {', '.join(highlight.tags)}\n")
                file.write(f"\n{highlight.text}\n\n---\n\n")


@click.group()
@click.option('--debug/--no-debug', default=False, help='Enable debug mode.')
def cli(debug: bool) -> None:
    """Convert Kindle highlights to markdown, JSON, or a searchable database."""
    if debug:
        click.echo("Debug mode is on.")


@cli.command()
@click.argument('clippings_file', type=click.Path(exists=True))
@click.option('--db', default='highlights.db', help='SQLite database path.')
@click.option('--output-dir', default='output', help='Output directory for markdown files.')
def import_clippings(clippings_file: str, db: str, output_dir: str) -> None:
    """Import Kindle clippings into the database and export to markdown."""
    init_db(db)
    highlights = parse_clippings(clippings_file)
    
    for highlight in highlights:
        insert_highlight(db, highlight)
    
    export_to_markdown(highlights, output_dir)
    
    click.echo(f"Imported {len(highlights)} highlights to {db} and exported to {output_dir}.")


if __name__ == '__main__':
    cli()