"""
CLI interface for Kindle Highlights to Markdown.
"""

import click
import os
import sys

# Add the current directory to Python path for local imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from parser import parse_clippings
from database import init_db, insert_highlight
from exporter import export_to_markdown, export_to_json


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
@click.option('--export-format', type=click.Choice(['markdown', 'json']), default='markdown', help='Export format.')
def import_clippings(clippings_file: str, db: str, output_dir: str, export_format: str) -> None:
    """Import Kindle clippings into the database and export to markdown/JSON."""
    init_db(db)
    highlights = parse_clippings(clippings_file)
    
    for highlight in highlights:
        insert_highlight(db, highlight)
    
    if export_format == 'markdown':
        export_to_markdown(highlights, output_dir)
    elif export_format == 'json':
        export_to_json(highlights, os.path.join(output_dir, 'highlights.json'))
    
    click.echo(f"Imported {len(highlights)} highlights to {db} and exported to {output_dir}.")


@cli.command()
@click.option('--db', default='highlights.db', help='SQLite database path.')
@click.option('--query', help='Search query (keyword).')
@click.option('--tag', help='Filter by tag.')
@click.option('--output-dir', default='search_results', help='Output directory for search results.')
@click.option('--export-format', type=click.Choice(['markdown', 'json']), default='markdown', help='Export format.')
def search(db: str, query: str, tag: str, output_dir: str, export_format: str) -> None:
    """Search highlights by keyword or tag and export results."""
    from database import search_highlights
    highlights = search_highlights(db, query, tag)
    
    if not highlights:
        click.echo("No highlights found.")
        return
    
    if export_format == 'markdown':
        export_to_markdown(highlights, output_dir)
    elif export_format == 'json':
        export_to_json(highlights, os.path.join(output_dir, 'search_results.json'))
    
    click.echo(f"Found {len(highlights)} highlights. Exported to {output_dir}.")


if __name__ == '__main__':
    cli()