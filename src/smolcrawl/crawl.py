from typing import List, Optional
from loguru import logger
from crawlee.crawlers import BeautifulSoupCrawler, BeautifulSoupCrawlingContext
import readabilipy.simple_json
import markdownify

from crawlee.http_clients import HttpResponse

from .utils import get_cache
from .db import Page


def replace_domained(url: str, domain_override: Optional[str]) -> str:
    if domain_override:
        from urllib.parse import urlparse

        parsed_url = urlparse(url)
        new_netloc = urlparse(domain_override).netloc

        # Reconstruct the URL with the new netloc
        new_url = parsed_url._replace(netloc=new_netloc).geturl()
        return new_url
    return url


def extract_content_from_html(html: str) -> str:
    """Extract and convert HTML content to Markdown format.

    Args:
        html: Raw HTML content to process

    Returns:
        Simplified markdown version of the content
    """
    ret = readabilipy.simple_json.simple_json_from_html_string(
        html, use_readability=True
    )
    if not ret["content"]:
        return "<error>Page failed to be simplified from HTML</error>"
    content = markdownify.markdownify(
        ret["content"],
        heading_style=markdownify.ATX,
    )
    return content


def extract_from_response(url: str, response: HttpResponse) -> Page | None:
    try:
        raw_bytes = response.read()
        raw_html = raw_bytes.decode("utf-8")
        if "<title>" in raw_html:
            title = raw_html.split("<title>")[1].split("</title>")[0]
        else:
            title = ""
        content = extract_content_from_html(raw_html)
        return Page(url=url, title=title, content=content, raw_html=raw_html)
    except Exception as e:
        logger.error(f"Error extracting from response: {e}")
        return None


async def crawl_target(target_url: str) -> List[Page]:
    # BeautifulSoupCrawler crawls the web using HTTP requests
    # and parses HTML using the BeautifulSoup library.
    crawler = BeautifulSoupCrawler()
    cache = get_cache("crawl")

    pages = cache.get(target_url)
    if pages:
        return [Page(**page) for page in pages]

    pages: List[Page] = []

    # Define a request handler to process each crawled page
    # and attach it to the crawler using a decorator.
    @crawler.router.default_handler
    async def request_handler(context: BeautifulSoupCrawlingContext) -> None:
        page = extract_from_response(context.request.url, context.http_response)
        if page:
            pages.append(page)
        # Extract links from the current page and add them to the crawling queue.
        await context.enqueue_links()

    # Add first URL to the queue and start the crawl.
    await crawler.run([target_url])

    pages_as_dicts = [page.model_dump() for page in pages]
    cache.set(target_url, pages_as_dicts, expire=72.0 * 3600)
    return pages
