# SmolCrawl

A lightweight web crawler and indexer for creating searchable document collections from websites.

## Overview

SmolCrawl is a Python-based tool that makes crawling websites and building searchable knowledge bases remarkably simple. It helps you:
- Crawl websites and extract content using intelligent algorithms
- Convert HTML content to clean, readable markdown
- Index pages into different formats (searchable index, markdown files, XML)
- Query indexed content with relevance scoring

Perfect for creating local knowledge bases, documentation search, personal research collections, website archives, and more.

## Features

- **Simple Web Crawling**: Crawl entire websites with a single command. Handles URL discovery and request management automatically.
- **Intelligent Content Extraction**: Uses readability algorithms (`readabilipy`) to extract meaningful content, filtering out boilerplate like navigation and ads.
- **Clean Markdown Conversion**: Converts extracted HTML into well-structured markdown (`markdownify`), preserving important elements.
- **Fast Search Indexing**: Built on Tantivy, a Rust-based search library similar to Lucene, for blazing-fast full-text search with relevance ranking.
- **Efficient Caching**: Implements disk-based caching to prevent redundant crawling and speed up subsequent runs.
- **Flexible Output Options**: Generate different outputs based on your needs:
    - Search indexes for fast querying (`tantivy`)
    - Collections of markdown files organized by URL structure (`markdown`)
    - Single XML exports for integration with other systems (`xml`)
- **Easy-to-Use CLI**: Simple, intuitive command-line interface built with Typer.

## Installation

SmolCrawl is available on PyPI and can be installed using pip:

```bash
pip install smolcrawl
```

For the latest development version, you can install directly from the repository:

```bash
# Clone the repository
git clone https://github.com/bllchmbrs/smolcrawl.git
cd smolcrawl

# Install the package in editable mode
pip install -e .
```

## Requirements

- Python 3.11 or higher
- Dependencies are automatically installed with the package

## Usage

### Crawl a Website (Display Info Only)

```bash
smolcrawl crawl https://example.com
```
This command crawls the site and shows information about the pages found but doesn't store the content persistently beyond the cache.

### Create a Searchable Index

```bash
smolcrawl index https://example.com my_index_name --index-type tantivy
# or simply (tantivy is the default):
smolcrawl index https://example.com my_index_name
```
This crawls the website and creates a fast, searchable Tantivy index named `my_index_name`.

### Generate Markdown Files

```bash
smolcrawl index https://example.com my_markdown_collection --index-type markdown
```
This crawls the website and saves the cleaned content as markdown files in `./smolcrawl-data/markdown_files/my_markdown_collection` (by default).

### Generate an XML Export

```bash
smolcrawl index https://example.com my_xml_export --index-type xml
```
This crawls the website and creates a single XML file containing the content in `./smolcrawl-data/xml_files/my_xml_export.xml` (by default).

### List Available Indices/Collections

```bash
smolcrawl list_indices
```

### Query a Search Index

```bash
smolcrawl query my_index_name "your search query" --limit 10
# Optionally filter by relevance score:
# smolcrawl query my_index_name "your search query" --limit 10 --score_threshold 0.5
```
Note: Querying only works for indices created with `--index-type tantivy`.

### Delete an Index/Collection

```bash
smolcrawl delete_index my_index_name
```

## Configuration

SmolCrawl uses environment variables for basic configuration. You can set these in a `.env` file in the project root or export them in your shell:

- `STORAGE_PATH`: Path to store index/collection data (default: `./smolcrawl-data`)
- `CACHE_PATH`: Path for caching downloaded/processed pages (default: `./smolcrawl-data/cache`)

## Project Structure

```
smolcrawl/
├── src/smolcrawl/
│   ├── __init__.py         # CLI definitions (Typer app)
│   ├── cli/                # CLI command modules
│   │   ├── common.py       # Shared CLI functions/options
│   │   ├── crawl_cmd.py    # 'crawl' command logic
│   │   ├── index_cmd.py    # 'index' command logic
│   │   ├── query_cmd.py    # 'query' command logic
│   │   └── ...             # Other commands
│   ├── core/               # Core crawling, processing, indexing logic
│   │   ├── config.py       # Configuration handling
│   │   ├── crawler.py      # Web crawling functionality
│   │   ├── processor.py    # Content extraction and markdown conversion
│   │   └── indexer/        # Indexing backends (Tantivy, Markdown, XML)
│   │       ├── base.py
│   │       ├── markdown_file.py
│   │       ├── tantivy_indexer.py
│   │       └── xml_file.py
│   └── utils.py            # Utility functions
├── data/                   # Default storage for indices and cache (gitignored)
├── tests/                  # Unit and integration tests
├── .env.example            # Example environment variables file
├── .gitignore
├── LICENSE                 # Project license file
└── pyproject.toml          # Project metadata and dependencies
```
*(Note: Actual structure may vary slightly)*

## How It Works

1.  **URL Entry**: Process starts with a root URL.
2.  **Discovery & Crawling**: The crawler (`BeautifulSoupCrawler`) visits the URL, extracts content, finds new links within the same domain, and adds them to a queue. Parallel requests may be used.
3.  **Content Extraction**: For each page, `readabilipy` identifies and extracts the main content, filtering out boilerplate.
4.  **Markdown Conversion**: Extracted HTML is converted to clean markdown using `markdownify`.
5.  **Caching**: Processed pages (URL, extracted content) are cached on disk (`CACHE_PATH`) to avoid redundant work on subsequent runs.
6.  **Indexing**: Depending on the chosen `--index-type`, the markdown content is:
    *   Added to a `Tantivy` search index (`TantivyIndexer`).
    *   Written to a `.md` file mirroring the URL structure (`MarkdownFileIndexer`).
    *   Appended to an XML file (`XmlFileIndexer`).
7.  **Searching** (Tantivy only): Queries are processed by the Tantivy index, returning relevant documents ranked by score.

## Responsible Crawling

SmolCrawl is a powerful tool. Please crawl responsibly and ethically.

- **Check `robots.txt`**: Always review a site's `robots.txt` (e.g., `https://example.com/robots.txt`) before crawling. Respect `Disallow` directives and crawl delays. *Note: SmolCrawl does not currently parse `robots.txt` automatically.*
- **Limit Scope**: Crawl only what you need. Avoid unnecessarily crawling entire large websites.
- **Minimize Impact**: Schedule large crawls during off-peak hours. Be mindful of server load.
- **Rate Limiting**: Avoid overwhelming servers. Pay attention to HTTP 429 (Too Many Requests) errors and slow down if necessary. *Note: SmolCrawl does not currently have built-in rate limiting or automatic backoff, but this is planned.*
- **Identify Yourself**: While not yet configurable in SmolCrawl, identifying your crawler via a User-Agent string is good practice.
- **Use Caching**: SmolCrawl's caching helps reduce repeated requests to the same pages.
- **Get Permission**: For large-scale or commercial crawling, consider seeking permission from the site owner.

Misuse can lead to IP blocks and negatively impact website availability. Crawl responsibly.

## License

[Your License Choice]

## Contributing

Contributions are welcome! SmolCrawl is an open-source project hosted on GitHub:

[https://github.com/bllchmbrs/smolcrawl](https://github.com/bllchmbrs/smolcrawl)

Star the repository to show support!

### How to Contribute

1.  **Fork the Repository**: Create your own fork on GitHub.
2.  **Set Up Environment**:
    ```bash
    git clone https://github.com/yourusername/smolcrawl.git
    cd smolcrawl
    # Install in editable mode with development dependencies
    pip install -e ".[dev]"
    ```
3.  **Create Branch**: `git checkout -b feature/your-new-feature`
4.  **Make Changes**: Implement your feature or fix. Add tests.
5.  **Run Tests**: `pytest`
6.  **Submit Pull Request**: Push your branch to your fork and open a PR against the main repository.
7.  **Engage**: Respond to code review feedback.

### Areas for Contribution

- **Documentation**: Improve README, add examples, write tutorials.
- **Testing**: Increase test coverage, add integration tests.
- **Features**: Implement roadmap items (e.g., `robots.txt` support, rate limiting, JS rendering).
- **Bug Fixes**: Address reported issues.
- **Performance**: Optimize crawling and indexing.
- **New Indexers**: Add support for other output formats.

### Community & Support

- **GitHub Issues**: For bug reports, feature requests, questions.
- **GitHub Discussions**: For broader topics and community engagement.
- **Email**: `contact@learnbybuilding.ai` for direct assistance.

