"""
Parse Kindle's "My Clippings.txt" file into structured data.
Format:
	Book Title (Author)
	- Your Highlight on Location 123-456 | Added on Monday, May 20, 2026
	Highlight text here...
	==========
"""

import re
from dataclasses import dataclass
from typing import List, Optional


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
    
    # Split into entries
    entries = content.split('==========')
    highlights = []
    
    for entry in entries:
        entry = entry.strip()
        if not entry:
            continue
        
        lines = entry.split('\n')
        if len(lines) < 3:
            continue
        
        # Parse book title and author (fallback for missing author)
        title_author_match = re.match(r'^(.+) \((.+)\)$', lines[0].strip())
        if not title_author_match:
            title_author_match = re.match(r'^(.+)$', lines[0].strip())
            if not title_author_match:
                continue
            book_title = title_author_match.group(1)
            author = "Unknown Author"
        else:
            book_title, author = title_author_match.groups()
        
        # Parse location and date (fallback for missing location/date, multi-language support)
        meta_match = re.match(r'^- Your (?:Highlight|Note|Bookmark) on (?:Location|位置|Page) (.+?)(?: \| Added on )?(.*)$', lines[1].strip())
        if not meta_match:
            meta_match = re.match(r'^- Your (?:Highlight|Note|Bookmark) on (.+)$', lines[1].strip())
            if not meta_match:
                continue
            location = meta_match.group(1)
            date = "Unknown Date"
        else:
            location, date = meta_match.groups()
        
        # Extract text
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