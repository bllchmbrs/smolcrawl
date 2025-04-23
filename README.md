# SmolCrawl

A lightweight web crawler and indexer for creating searchable document collections from websites.

## Overview

SmolCrawl is a Python-based tool that helps you:
- Crawl websites and extract content
- Convert HTML content to readable markdown
- Index pages for efficient searching
- Query indexed content with relevance scoring

Perfect for creating local knowledge bases, documentation search, or personal research collections.

## Features

- **Simple Web Crawling**: Easily crawl and extract content from target websites
- **Content Extraction**: Automatically extracts meaningful content from HTML using readability algorithms
- **Markdown Conversion**: Converts HTML content to clean, readable markdown format
- **Fast Indexing**: Uses Tantivy (Rust-based search library) for performant full-text search
- **Caching**: Implements disk-based caching to avoid redundant crawling
- **CLI Interface**: Simple command-line interface for all operations

## Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/smolcrawl.git
cd smolcrawl

# Install the package
pip install -e .
```

## Requirements

- Python 3.11 or higher
- Dependencies are automatically installed with the package

## Usage

### Crawl a Website

```bash
smolcrawl crawl https://example.com
```

### Index a Website

```bash
smolcrawl index https://example.com my_index_name
```

### List Available Indices

```bash
smolcrawl list_indices
```

### Query an Index

```bash
smolcrawl query my_index_name "your search query" --limit 10 --score_threshold 0.5
```

### Delete an Index

```bash
smolcrawl delete_index my_index_name
```

## Configuration

SmolCrawl uses environment variables for configuration:

- `STORAGE_PATH`: Path to store data (default: `./data`)
- `CACHE_PATH`: Path for caching (default: `./data/cache`)

You can set these in a `.env` file in the project root.

## Project Structure

```
smolcrawl/
├── src/smolcrawl/
│   ├── __init__.py    # CLI and entry points
│   ├── crawl.py       # Web crawling functionality
│   ├── db.py          # Indexing and search functionality
│   └── utils.py       # Utility functions
├── data/              # Storage for indices and cache (gitignored)
├── .gitignore
└── pyproject.toml     # Project metadata and dependencies
```

## How It Works

1. **Crawling**: Uses BeautifulSoupCrawler to fetch web pages and extract links
2. **Content Processing**: Extracts meaningful content using ReadabiliPy and converts to markdown
3. **Indexing**: Stores extracted content in a Tantivy index for efficient searching
4. **Searching**: Performs full-text search on indexed content with relevance ranking

## License

[Your License Choice]

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request