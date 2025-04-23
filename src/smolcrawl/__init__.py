from .db import Indexer, Page, Section
from .crawl import crawl_target
import typer
import asyncio
from typing import List
from loguru import logger
from .utils import get_storage_path
import os

app = typer.Typer()


@app.command()
def crawl(target_url: str) -> List[Page]:
    logger.info(f"Crawling {target_url}")
    results = asyncio.run(crawl_target(target_url))
    logger.success(f"Crawled {len(results)} pages from {target_url}")
    return results


@app.command()
def index(target_url: str, name: str) -> List[Page]:
    logger.info(f"Indexing {target_url} into {name}")
    crawl_results = crawl(target_url)
    indexer = Indexer(name)
    logger.info(f"Adding {len(crawl_results)} pages to {name}")
    indexer.add_pages(crawl_results)
    logger.success(f"Indexed {len(crawl_results)} pages into {name}")
    return crawl_results


@app.command()
def list_indices() -> None:
    for f in os.listdir(os.path.join(get_storage_path(), "db")):
        print(f)


@app.command()
def delete_index(name: str) -> None:
    import os

    os.remove(os.path.join(get_storage_path(), "db", name))
    logger.success(f"Deleted index {name}")


@app.command()
def query(
    index_name: str, query: str, limit: int = 10, score_threshold: float = 0.5
) -> None:
    indexer = Indexer(index_name)

    res = list(indexer.query(query, limit=limit, score_threshold=score_threshold))
    logger.success(f"Found {len(res)} results")
    for r in res:
        logger.info(f" - {r.title} / {r.url}")


if __name__ == "__main__":
    app()
