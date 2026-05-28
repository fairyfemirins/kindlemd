"""
SQLite database for Kindle highlights.
"""

import sqlite3
from typing import List, Optional
from .parser import Highlight


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


def search_highlights(db_path: str, query: Optional[str] = None, tag: Optional[str] = None) -> List[Highlight]:
    """Search highlights by keyword or tag."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    sql = """
        SELECT h.book_title, h.author, h.location, h.date, h.text
        FROM highlights h
        LEFT JOIN tags t ON h.id = t.highlight_id
    """
    conditions = []
    params = []
    
    if query:
        conditions.append("(h.book_title LIKE ? OR h.text LIKE ?)")
        params.extend([f"%{query}%", f"%{query}%"])
    
    if tag:
        conditions.append("t.tag = ?")
        params.append(tag)
    
    if conditions:
        sql += " WHERE " + " AND ".join(conditions)
    
    cursor.execute(sql, params)
    rows = cursor.fetchall()
    conn.close()
    
    highlights = []
    for row in rows:
        highlights.append(Highlight(
            book_title=row[0],
            author=row[1],
            location=row[2],
            date=row[3],
            text=row[4],
            tags=[]
        ))
    
    return highlights