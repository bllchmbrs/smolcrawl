import os
import tantivy
from smolcrawl.utils import get_storage_path
from typing import List, Iterable, Set
from pydantic import BaseModel
from loguru import logger


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


class Indexer:
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
