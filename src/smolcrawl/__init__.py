from .db import TantivyIndexer, MarkdownFileIndexer, Page, Section, XmlFileIndexer
from .crawl import crawl_target
import typer
import asyncio
from typing import List, Literal
from loguru import logger
from .utils import get_storage_path
import os

app = typer.Typer()


@app.command()
def crawl(target_url: str = typer.Argument(..., help="The URL to crawl.")) -> List[Page]:
    """Crawls a target URL and returns the extracted pages."""
    logger.info(f"Crawling {target_url}")
    results = asyncio.run(crawl_target(target_url))
    logger.success(f"Crawled {len(results)} pages from {target_url}")
    return results


@app.command()
def index(
    target_url: str = typer.Argument(..., help="The URL to crawl."),
    name: str = typer.Argument(..., help="The name of the index to create or update."),
    index_type: str = typer.Option(
        "search", help="The type of index to create ('search' for Tantivy, 'markdown' for files, 'xml' for a single XML file)."
    ),
) -> List[Page]:
    """Crawls a target URL and indexes the content into the specified index."""
    logger.info(f"Indexing {target_url} into {name}")
    crawl_results = crawl(target_url)
    if index_type == "search":
        indexer = TantivyIndexer(name)
        logger.info(f"Adding {len(crawl_results)} pages to {name}")
        indexer.add_pages(crawl_results)
        logger.success(f"Indexed {len(crawl_results)} pages into {name}")
    elif index_type == "markdown":
        indexer = MarkdownFileIndexer(name)
        logger.info(f"Writing {len(crawl_results)} pages to markdown files in {name}")
        indexer.add_pages(crawl_results)
        logger.success(f"Wrote {len(crawl_results)} pages to markdown files in {name}")
    elif index_type == "xml":
        indexer = XmlFileIndexer(name)
        logger.info(f"Writing {len(crawl_results)} pages to XML file {indexer.target_file}")
        indexer.add_pages(crawl_results)
        logger.success(f"Wrote {len(crawl_results)} pages to {indexer.target_file}")
    return crawl_results


@app.command()
def list_indices() -> None:
    """Lists the available Tantivy (search) indices."""
    for f in os.listdir(os.path.join(get_storage_path(), "db")):
        print(f)


@app.command()
def delete_index(name: str = typer.Argument(..., help="The name of the Tantivy index to delete.")) -> None:
    """Deletes the specified Tantivy (search) index."""
    import os

    os.remove(os.path.join(get_storage_path(), "db", name))
    logger.success(f"Deleted index {name}")


@app.command()
def query(
    index_name: str = typer.Argument(..., help="The name of the Tantivy (search) index to query."),
    query: str = typer.Argument(..., help="The search query string."),
    limit: int = typer.Option(10, help="The maximum number of results to return."),
    score_threshold: float = typer.Option(
        0.5, help="The minimum score for results to be included."
    ),
) -> None:
    """Queries a Tantivy index and prints the results."""
    indexer = TantivyIndexer(index_name)

    res = list(indexer.query(query, limit=limit, score_threshold=score_threshold))
    logger.success(f"Found {len(res)} results")
    for r in res:
        logger.info(f" - {r.title} / {r.url}")


if __name__ == "__main__":
    app()
