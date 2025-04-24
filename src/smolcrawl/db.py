import os
import tantivy
from smolcrawl.utils import get_storage_path
from typing import List, Iterable, Set
from pydantic import BaseModel
from loguru import logger
import xml.etree.ElementTree as ET
from xml.dom import minidom


class Section(BaseModel):
    heading: str
    content: str
    url: str
    title: str


class Page(BaseModel):
    url: str
    title: str
    content: str
    raw_html: str

    def __hash__(self) -> int:
        return hash(self.url)

    def get_sections(self) -> List[Section]:
        sections = []
        parts = self.content.split("## ")
        if len(parts) > 1:
            for part in parts[1:]:
                lines = part.splitlines()
                heading = lines[0]
                content = "\n".join(lines[1:])

                sections.append(
                    Section(
                        heading=heading,
                        content=content,
                        url=self.url,
                        title=self.title,
                    )
                )

        return sections


class TantivyIndexer:
    def __init__(self, index_name: str):
        self.DB_PATH = os.path.join(get_storage_path(), "db", index_name)
        schema_builder = tantivy.SchemaBuilder()
        self.name = index_name
        schema_builder.add_text_field("name", stored=True)
        schema_builder.add_text_field("url", stored=True)
        schema_builder.add_text_field("title", stored=True)
        schema_builder.add_text_field("content", stored=True)
        schema_builder.add_text_field("raw_html", stored=True)
        self.schema = schema_builder.build()

        try:
            self.index = tantivy.Index.open(self.DB_PATH)
        except:
            os.makedirs(self.DB_PATH, exist_ok=True)
            self.index = tantivy.Index(self.schema, path=self.DB_PATH)

    def add_page(self, page: Page):
        writer = self.index.writer()
        new_doc = tantivy.Document()

        new_doc.add_text("url", page.url)
        new_doc.add_text("title", page.title)
        new_doc.add_text("content", page.content)
        new_doc.add_text("raw_html", page.raw_html)
        writer.add_document(new_doc)
        writer.commit()
        writer.wait_merging_threads()
        self.index.reload()

    def add_pages(self, pages: List[Page]):
        logger.info(f"Adding {len(pages)} pages to {self.name}")
        writer = self.index.writer()
        for page in pages:
            new_doc = tantivy.Document()

            new_doc.add_text("url", page.url)
            new_doc.add_text("title", page.title)
            new_doc.add_text("content", page.content)
            new_doc.add_text("raw_html", page.raw_html)
            writer.add_document(new_doc)
        writer.commit()
        writer.wait_merging_threads()
        logger.success(f"Added {len(pages)} pages to {self.name}")
        self.index.reload()

    def query(
        self,
        query_string: str,
        fields: List[str] = ["title", "content"],
        limit: int = 10,
        score_threshold: float = 0.5,
    ) -> Iterable[Page]:
        logger.info(f"Searching for {query_string} in {self.name}")
        searcher = self.index.searcher()
        query = self.index.parse_query(query_string, fields)
        results = searcher.search(query, limit).hits
        output: Set[Page] = set()
        logger.success(f"Found {len(results)} raw results")
        for result in results:
            doc_score = result[0]
            doc_address = result[1]
            doc = searcher.doc(doc_address)
            if doc_score > score_threshold:
                output.add(
                    Page(
                        url=doc.get_first("url"),
                        title=doc.get_first("title"),
                        content=doc.get_first("content"),
                        raw_html=doc.get_first("raw_html"),
                    )
                )

        logger.info(f"Found {len(output)} deduplicated results")
        return output


class MarkdownFileIndexer:
    def __init__(self, index_name: str):
        self.target_dir = os.path.join(get_storage_path(), "markdown_files", index_name)
        self.name = index_name
        os.makedirs(self.target_dir, exist_ok=True)
        logger.info(f"Initialized MarkdownFileIndexer writing to {self.target_dir}")

    def _get_file_path(self, url: str) -> str:
        from urllib.parse import urlparse
        import pathlib

        parsed_url = urlparse(url)
        path_parts = [part for part in parsed_url.path.split("/") if part]

        if not path_parts:
            filename = "index.md"
        else:
            last_part = path_parts[-1]
            if "." in last_part:  # Assumes it's a file if it has an extension
                filename = pathlib.Path(last_part).stem + ".md"
                path_parts = path_parts[:-1]
            else:
                filename = "index.md"

        dir_path = os.path.join(self.target_dir, *path_parts)
        return os.path.join(dir_path, filename)

    def add_page(self, page: Page):
        file_path = self._get_file_path(page.url)
        dir_path = os.path.dirname(file_path)

        try:
            os.makedirs(dir_path, exist_ok=True)
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(f"# {page.title}\n\n")
                f.write(page.content)
            # logger.debug(f"Wrote page {page.url} to {file_path}")
        except OSError as e:
            logger.error(f"Error writing file {file_path} for url {page.url}: {e}")

    def add_pages(self, pages: List[Page]):
        logger.info(
            f"Writing {len(pages)} pages to markdown files in {self.target_dir}"
        )
        count = 0
        for page in pages:
            try:
                self.add_page(page)
                count += 1
            except Exception as e:
                logger.error(f"Failed to add page {page.url}: {e}")
        logger.success(
            f"Successfully wrote {count}/{len(pages)} pages to {self.target_dir}"
        )


class XmlFileIndexer:
    def __init__(self, index_name: str):
        self.target_dir = os.path.join(get_storage_path(), "xml_files")
        self.target_file = os.path.join(self.target_dir, f"{index_name}.xml")
        self.name = index_name
        os.makedirs(self.target_dir, exist_ok=True)
        logger.info(f"Initialized XmlFileIndexer writing to {self.target_file}")

    def _to_pretty_xml(self, elem):
        """Return a pretty-printed XML string for the Element."""
        rough_string = ET.tostring(elem, "utf-8")
        reparsed = minidom.parseString(rough_string)
        return reparsed.toprettyxml(indent="")

    def add_pages(self, pages: List[Page]):
        logger.info(f"Writing {len(pages)} pages to XML file {self.target_file}")
        count = 0

        preamble = """<file_summary>
This file contains crawled pages from websites, indexed by SmolCrawl.
<purpose>
    This file contains a collection of crawled web pages, suitable for creating searchable document collections.
</purpose>
<features>
    - Crawled websites and extracted content
    - Converted HTML content to readable markdown (in the content field)
    - Indexed pages for efficient searching
    - Query indexed content with relevance scoring
</features>
<usage_guidelines>
    - This file is read-only.
    - Use the 'url' attribute to identify the source of the content.
    - The 'content' field contains the extracted and converted markdown.
</usage_guidelines>
</file_summary>
"""

        root = ET.Element("crawled_pages", attrib={"format": "markdown"})

        for page in pages:
            try:
                page_elem = ET.SubElement(
                    root, "page", attrib={"url": page.url, "title": page.title}
                )
                page_elem.text = "\n" + page.content

                count += 1
            except Exception as e:
                logger.error(f"Failed to add page {page.url} to XML: {e}")

        try:
            # Use minidom for pretty printing
            pages_xml = self._to_pretty_xml(root)
            full_xml = preamble + pages_xml + "</crawled_pages>"

            with open(self.target_file, "w", encoding="utf-8") as f:
                f.write(full_xml.replace('<?xml version="1.0" ?>\n', ""))
            logger.success(
                f"Successfully wrote {count}/{len(pages)} pages to {self.target_file}"
            )
        except Exception as e:
            logger.error(f"Error writing XML file {self.target_file}: {e}")
