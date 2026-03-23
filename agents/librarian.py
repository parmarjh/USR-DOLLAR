"""
📚 THE LIBRARIAN AGENT
=======================
Role: Data Manager — Scans PDFs, extracts text, indexes metadata into database.

Capabilities:
  • PDF text extraction using PyMuPDF
  • Automatic keyword extraction
  • Metadata indexing via SQLAlchemy
  • Document chunking for vector storage
"""

import os
from typing import List, Dict, Optional
from .base_agent import BaseAgent

try:
    import fitz  # PyMuPDF
except ImportError:
    fitz = None

from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime

Base = declarative_base()


# ==========================================
# Database Model for Document Metadata
# ==========================================
class DocumentRecord(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, autoincrement=True)
    filename = Column(String(255), nullable=False)
    filepath = Column(String(500), nullable=False)
    page_count = Column(Integer)
    keywords = Column(Text)
    chunk_count = Column(Integer, default=0)
    indexed_at = Column(DateTime, default=datetime.now)
    status = Column(String(50), default="indexed")


# ==========================================
# THE LIBRARIAN AGENT
# ==========================================
class LibrarianAgent(BaseAgent):
    """
    📚 The Librarian Agent
    ----------------------
    Scans PDF files, extracts text, splits into chunks,
    and indexes metadata into an SQLite database.
    """

    def __init__(self, db_url: str = "sqlite:///research_metadata.db",
                 chunk_size: int = 500, chunk_overlap: int = 50):
        super().__init__(name="The Librarian", role="librarian")
        self.db_url = db_url
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

        # Setup database
        self.engine = create_engine(db_url, echo=False)
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)

        self.log("Initialized with database ready", "success")

    def execute(self, folder_path: str) -> Dict:
        """
        Main execution: Process all PDFs in a folder.
        Returns dict with all extracted text chunks and metadata.
        """
        self.log(f"Scanning folder: {folder_path}")
        results = {
            "total_files": 0,
            "total_pages": 0,
            "total_chunks": 0,
            "documents": [],
            "all_chunks": [],
        }

        if not os.path.exists(folder_path):
            self.log(f"Folder not found: {folder_path}", "error")
            return results

        pdf_files = [f for f in os.listdir(folder_path) if f.lower().endswith(".pdf")]
        results["total_files"] = len(pdf_files)
        self.log(f"Found {len(pdf_files)} PDF file(s)")

        for pdf_file in pdf_files:
            filepath = os.path.join(folder_path, pdf_file)
            doc_data = self.process_pdf(filepath)
            if doc_data:
                results["documents"].append(doc_data)
                results["total_pages"] += doc_data["page_count"]
                results["total_chunks"] += len(doc_data["chunks"])
                results["all_chunks"].extend(doc_data["chunks"])

        self.log(
            f"[OK] Processed {results['total_files']} files, "
            f"{results['total_pages']} pages, "
            f"{results['total_chunks']} chunks",
            "success"
        )
        return results

    def process_pdf(self, filepath: str) -> Optional[Dict]:
        """Process a single PDF file."""
        if fitz is None:
            self.log("PyMuPDF not installed. Install with: pip install PyMuPDF", "error")
            return None

        filename = os.path.basename(filepath)
        self.log(f"📄 Reading: {filename}")

        try:
            doc = fitz.open(filepath)
            full_text = ""
            for page in doc:
                full_text += page.get_text()

            page_count = len(doc)
            doc.close()

            # Extract keywords
            keywords = self._extract_keywords(full_text)

            # Chunk the text
            chunks = self._chunk_text(full_text)

            # Save metadata to database
            self._save_to_db(filename, filepath, page_count, keywords, len(chunks))

            self.log(f"  → {page_count} pages, {len(chunks)} chunks, keywords: {keywords[:5]}", "info")

            return {
                "filename": filename,
                "filepath": filepath,
                "page_count": page_count,
                "full_text": full_text,
                "chunks": chunks,
                "keywords": keywords,
            }
        except Exception as e:
            self.log(f"Error processing {filename}: {str(e)}", "error")
            return None

    def _extract_keywords(self, text: str, top_n: int = 10) -> List[str]:
        """Extract keywords using simple frequency analysis."""
        import re
        from collections import Counter

        # Simple keyword extraction (no external dependency needed)
        words = re.findall(r'\b[a-zA-Z]{4,}\b', text.lower())
        stopwords = {
            "this", "that", "with", "from", "have", "been", "were", "will",
            "what", "when", "where", "which", "their", "there", "these",
            "those", "about", "would", "could", "should", "other", "than",
            "each", "into", "more", "some", "such", "only", "also", "very",
            "just", "over", "after", "before", "between", "through", "during",
        }
        filtered = [w for w in words if w not in stopwords]
        common = Counter(filtered).most_common(top_n)
        return [word for word, count in common]

    def _chunk_text(self, text: str) -> List[str]:
        """Split text into overlapping chunks."""
        chunks = []
        start = 0
        while start < len(text):
            end = start + self.chunk_size
            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)
            start += self.chunk_size - self.chunk_overlap
        return chunks

    def _save_to_db(self, filename: str, filepath: str,
                    page_count: int, keywords: List[str], chunk_count: int):
        """Save document metadata to the database."""
        session = self.Session()
        try:
            record = DocumentRecord(
                filename=filename,
                filepath=filepath,
                page_count=page_count,
                keywords=",".join(keywords),
                chunk_count=chunk_count,
            )
            session.add(record)
            session.commit()
        except Exception as e:
            session.rollback()
            self.log(f"DB Error: {str(e)}", "error")
        finally:
            session.close()

    def get_all_records(self) -> List[Dict]:
        """Retrieve all document records from the database."""
        session = self.Session()
        try:
            records = session.query(DocumentRecord).all()
            return [
                {
                    "id": r.id,
                    "filename": r.filename,
                    "page_count": r.page_count,
                    "keywords": r.keywords,
                    "chunk_count": r.chunk_count,
                    "indexed_at": str(r.indexed_at),
                }
                for r in records
            ]
        finally:
            session.close()
