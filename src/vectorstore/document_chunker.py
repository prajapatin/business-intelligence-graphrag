import os
from typing import Any, Dict, List

from loguru import logger


class DocumentChunker:
    """Reads report text files and splits them into overlapping chunks for embedding."""

    def __init__(self, chunk_size: int = 500, chunk_overlap: int = 100):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def chunk_directory(self, directory: str) -> List[Dict[str, Any]]:
        """Read all .txt files in a directory and return chunked documents with metadata.

        Returns:
            List of dicts: {"text": str, "metadata": {"source": filename, "doc_type": str, "chunk_index": int}}
        """
        all_chunks = []

        if not os.path.isdir(directory):
            logger.warning(f"Report directory not found: {directory}")
            return all_chunks

        for filename in sorted(os.listdir(directory)):
            if not filename.endswith(".txt"):
                continue

            filepath = os.path.join(directory, filename)
            with open(filepath, "r") as f:
                text = f.read()

            doc_type = self._infer_doc_type(filename)
            chunks = self._split_text(text)

            for i, chunk in enumerate(chunks):
                all_chunks.append({
                    "text": chunk,
                    "metadata": {
                        "source": filename,
                        "doc_type": doc_type,
                        "chunk_index": i,
                    },
                })

        logger.info(f"Chunked {len(all_chunks)} text segments from {directory}")
        return all_chunks

    def _split_text(self, text: str) -> List[str]:
        """Split text into overlapping chunks, respecting paragraph boundaries."""
        # Split by double newline (paragraphs) first
        paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]

        chunks = []
        current_chunk = ""

        for para in paragraphs:
            # If adding this paragraph exceeds chunk size, save current and start new
            if len(current_chunk) + len(para) + 2 > self.chunk_size and current_chunk:
                chunks.append(current_chunk.strip())
                # Overlap: keep the tail of the current chunk
                overlap_text = current_chunk[-self.chunk_overlap:] if len(current_chunk) > self.chunk_overlap else current_chunk
                current_chunk = overlap_text + "\n\n" + para
            else:
                current_chunk = current_chunk + "\n\n" + para if current_chunk else para

        if current_chunk.strip():
            chunks.append(current_chunk.strip())

        # If no chunks were created (very short text), return the full text
        if not chunks and text.strip():
            chunks = [text.strip()]

        return chunks

    @staticmethod
    def _infer_doc_type(filename: str) -> str:
        """Infer document type from filename."""
        if filename.startswith("quarterly_report"):
            return "quarterly_report"
        elif filename.startswith("dept_memo"):
            return "department_memo"
        elif filename.startswith("product_brief"):
            return "product_brief"
        elif filename.startswith("regional_summary"):
            return "regional_summary"
        elif filename.startswith("case_study"):
            return "customer_case_study"
        elif filename.startswith("annual_review"):
            return "annual_review"
        return "unknown"
