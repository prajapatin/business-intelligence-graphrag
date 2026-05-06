import os
import pytest

import chromadb
from chromadb.utils import embedding_functions

from src.vectorstore.base_store import BaseVectorStore
from src.vectorstore.chroma_store import ChromaVectorStore
from src.vectorstore.document_chunker import DocumentChunker


class InMemoryChromaStore(BaseVectorStore):
    """In-memory ChromaDB store for testing (avoids SQLite disk issues)."""

    def __init__(self, collection_name: str = "test"):
        self._client = chromadb.EphemeralClient()
        self._ef = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name="all-MiniLM-L6-v2",
        )
        self._collection = self._client.get_or_create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"},
            embedding_function=self._ef,
        )
        self.collection_name = collection_name

    def add_documents(self, documents, metadatas=None, ids=None):
        if not documents:
            return
        if ids is None:
            ids = [f"doc_{self._collection.count() + i}" for i in range(len(documents))]
        clean_metas = None
        if metadatas:
            clean_metas = [{k: v if isinstance(v, (str, int, float, bool)) else str(v) for k, v in m.items()} for m in metadatas]
        self._collection.add(documents=documents, metadatas=clean_metas, ids=ids)

    def search(self, query, top_k=5):
        if self._collection.count() == 0:
            return []
        results = self._collection.query(query_texts=[query], n_results=min(top_k, self._collection.count()))
        hits = []
        if results and results["documents"]:
            for doc, meta, dist in zip(
                results["documents"][0],
                results["metadatas"][0] if results["metadatas"] else [{}] * len(results["documents"][0]),
                results["distances"][0] if results["distances"] else [0.0] * len(results["documents"][0]),
            ):
                hits.append({"text": doc, "metadata": meta or {}, "score": 1.0 - dist})
        return hits

    def count(self):
        return self._collection.count()

    def clear(self):
        self._client.delete_collection(self.collection_name)
        self._collection = self._client.get_or_create_collection(
            name=self.collection_name, metadata={"hnsw:space": "cosine"}, embedding_function=self._ef,
        )

    def persist(self):
        pass


@pytest.fixture
def vector_store(request):
    return InMemoryChromaStore(collection_name=f"test_{request.node.name}")


def test_add_and_count(vector_store):
    vector_store.add_documents(
        documents=["The Engineering department focuses on SaaS products."],
        metadatas=[{"source": "test.txt", "doc_type": "test"}],
        ids=["doc_0"],
    )
    assert vector_store.count() == 1


def test_search_returns_results(vector_store):
    docs = [
        "CloudSync Pro is a SaaS product with strong Q4 sales.",
        "The Finance department manages the annual budget.",
        "SecureNet Gateway is our flagship hardware product.",
    ]
    metas = [
        {"source": "prod.txt", "doc_type": "product_brief"},
        {"source": "dept.txt", "doc_type": "department_memo"},
        {"source": "prod2.txt", "doc_type": "product_brief"},
    ]
    vector_store.add_documents(docs, metadatas=metas, ids=["d0", "d1", "d2"])

    results = vector_store.search("What SaaS products do we sell?", top_k=2)
    assert len(results) == 2
    assert all("text" in r for r in results)
    assert all("score" in r for r in results)
    # First result should be about SaaS/CloudSync (most relevant)
    assert "SaaS" in results[0]["text"] or "CloudSync" in results[0]["text"]


def test_search_empty_store():
    store = InMemoryChromaStore(collection_name="empty_store_test")
    results = store.search("anything", top_k=5)
    assert results == []


def test_clear(vector_store):
    vector_store.add_documents(["some document"], ids=["d0"])
    assert vector_store.count() == 1
    vector_store.clear()
    assert vector_store.count() == 0


def test_document_chunker_splits_text():
    chunker = DocumentChunker(chunk_size=100, chunk_overlap=20)
    text = "Paragraph one about sales.\n\nParagraph two about engineering.\n\nParagraph three about products."
    chunks = chunker._split_text(text)
    assert len(chunks) >= 1
    # All original content should be covered
    full = " ".join(chunks)
    assert "sales" in full
    assert "engineering" in full
    assert "products" in full


def test_document_chunker_infer_type():
    assert DocumentChunker._infer_doc_type("quarterly_report_q1_2023.txt") == "quarterly_report"
    assert DocumentChunker._infer_doc_type("dept_memo_engineering.txt") == "department_memo"
    assert DocumentChunker._infer_doc_type("product_brief_prod-001.txt") == "product_brief"
    assert DocumentChunker._infer_doc_type("regional_summary_north_america.txt") == "regional_summary"
    assert DocumentChunker._infer_doc_type("case_study_cust-001.txt") == "customer_case_study"
    assert DocumentChunker._infer_doc_type("annual_review_2023.txt") == "annual_review"
    assert DocumentChunker._infer_doc_type("random_file.txt") == "unknown"


def test_document_chunker_directory(tmp_path):
    # Create test report files
    (tmp_path / "quarterly_report_q1.txt").write_text("Q1 revenue was strong.\n\nProducts performed well.")
    (tmp_path / "dept_memo_eng.txt").write_text("Engineering focuses on innovation.")

    chunker = DocumentChunker(chunk_size=500, chunk_overlap=50)
    chunks = chunker.chunk_directory(str(tmp_path))

    assert len(chunks) >= 2
    sources = {c["metadata"]["source"] for c in chunks}
    assert "quarterly_report_q1.txt" in sources or "dept_memo_eng.txt" in sources
