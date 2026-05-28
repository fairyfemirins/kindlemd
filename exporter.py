"""
Export Kindle highlights to markdown or JSON.
"""

import json
import os
from typing import List
from pathlib import Path
from .parser import Highlight


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


def export_to_json(highlights: List[Highlight], output_path: str) -> None:
    """Export highlights to a JSON file."""
    with open(output_path, 'w', encoding='utf-8') as file:
        json.dump([{
            "book_title": h.book_title,
            "author": h.author,
            "location": h.location,
            "date": h.date,
            "text": h.text,
            "tags": h.tags
        } for h in highlights], file, indent=2, ensure_ascii=False)