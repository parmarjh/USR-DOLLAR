"""
🚀 Multi-Agent Research System — FastAPI Backend
==================================================
Exposes the 3-agent system as REST API endpoints for the React frontend.
"""

import os
import sys
import json
from typing import Optional
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
import shutil

# Add parent to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

load_dotenv()

from agents.librarian import LibrarianAgent
from agents.researcher import ResearcherAgent
from agents.analyst import AnalystAgent

# ==========================================
# FastAPI App
# ==========================================
app = FastAPI(
    title="Multi-Agent Research System",
    description="3-Agent AI Pipeline: Librarian → Researcher → Analyst",
    version="1.0.0",
)

# CORS for React dev server
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==========================================
# Global Agent Instances
# ==========================================
PDF_FOLDER = os.getenv("PDF_FOLDER", "./my_papers")
os.makedirs(PDF_FOLDER, exist_ok=True)

provider = os.getenv("LLM_PROVIDER", "openrouter")
model_map = {
    "openrouter": os.getenv("OPENROUTER_MODEL", "google/gemini-2.0-flash-001"),
    "gemini": os.getenv("GEMINI_MODEL", "gemini-2.0-flash"),
    "openai": os.getenv("OPENAI_MODEL", "gpt-4"),
    "ollama": os.getenv("OLLAMA_MODEL", "llama3"),
}

librarian = LibrarianAgent(
    db_url=os.getenv("DATABASE_URL", "sqlite:///research_metadata.db"),
)
researcher = ResearcherAgent(
    model_name=os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2"),
    vector_db_path=os.getenv("VECTOR_DB_PATH", "./faiss_research_db"),
)
analyst = AnalystAgent(
    llm_provider=provider,
    api_key=(os.getenv("OPENROUTER_API_KEY") or os.getenv("GEMINI_API_KEY") or os.getenv("OPENAI_API_KEY")),
    model_name=model_map.get(provider),
)

# Try loading existing index
try:
    researcher.load_index()
except Exception:
    pass


# ==========================================
# Request/Response Models
# ==========================================
class QueryRequest(BaseModel):
    question: str
    mode: str = "analyze"  # analyze, summarize, compare, develop
    top_k: int = 3


class IngestResponse(BaseModel):
    total_files: int
    total_pages: int
    total_chunks: int
    filenames: list


class QueryResponse(BaseModel):
    answer: str
    sources: list
    mode: str
    question: str


# ==========================================
# API Endpoints
# ==========================================

@app.get("/")
def root():
    return {"message": "Multi-Agent Research System API", "status": "running"}


@app.get("/api/agents")
def get_agents():
    """Get the status of all 3 agents."""
    return {
        "agents": [
            {
                "id": 1,
                "name": "The Librarian",
                "role": "librarian",
                "emoji": "📚",
                "description": "Scans PDFs, extracts text, indexes metadata into database",
                "capabilities": [
                    "PDF text extraction (PyMuPDF)",
                    "Keyword extraction",
                    "Metadata indexing (SQLAlchemy)",
                    "Document chunking",
                ],
                "status": "ready",
                "tech": ["PyMuPDF", "SQLAlchemy", "SQLite"],
            },
            {
                "id": 2,
                "name": "The Researcher",
                "role": "researcher",
                "emoji": "🔍",
                "description": "Performs semantic search for one-to-one accurate context retrieval",
                "capabilities": [
                    "Vector embedding (Sentence Transformers)",
                    "Semantic similarity search (FAISS)",
                    "One-to-one accuracy retrieval",
                    "Top-K document matching",
                ],
                "status": "ready",
                "tech": ["Sentence Transformers", "FAISS", "NumPy"],
                "stats": researcher.get_stats(),
            },
            {
                "id": 3,
                "name": "The Analyst",
                "role": "analyst",
                "emoji": "🧠",
                "description": "Analyzes retrieved context and generates structured insights",
                "capabilities": [
                    f"LLM analysis ({provider})",
                    f"Model: {model_map.get(provider, 'unknown')}",
                    "4 analysis modes",
                    "Structured reports",
                ],
                "status": "ready" if analyst.llm else "no_llm",
                "tech": [provider.title(), "LangChain"],
            },
        ]
    }


@app.get("/api/documents")
def get_documents():
    """Get all indexed documents."""
    records = librarian.get_all_records()
    return {"documents": records, "total": len(records)}


@app.post("/api/upload")
async def upload_pdf(file: UploadFile = File(...)):
    """Upload a PDF file for processing."""
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are accepted")

    filepath = os.path.join(PDF_FOLDER, file.filename)
    with open(filepath, "wb") as f:
        shutil.copyfileobj(file.file, f)

    return {"message": f"Uploaded {file.filename}", "filename": file.filename}


@app.post("/api/ingest")
def ingest_documents():
    """Run the Librarian to process all PDFs, then Researcher to index them."""
    # Step 1: Librarian processes PDFs
    results = librarian.execute(PDF_FOLDER)
    chunks = results.get("all_chunks", [])
    filenames = [d["filename"] for d in results.get("documents", [])]

    # Step 2: Researcher indexes chunks
    if chunks:
        metadata = []
        for doc in results.get("documents", []):
            for _ in doc.get("chunks", []):
                metadata.append({"source": doc["filename"]})
        researcher.execute(chunks, metadata)
        researcher.save_index()

    return IngestResponse(
        total_files=results["total_files"],
        total_pages=results["total_pages"],
        total_chunks=results["total_chunks"],
        filenames=filenames,
    )


@app.post("/api/query")
def query_system(req: QueryRequest):
    """Query the system: Researcher retrieves context, Analyst generates insights."""
    # Researcher retrieves
    results = researcher.retrieve(req.question, req.top_k)
    context_chunks = [r["text"] for r in results]

    if not context_chunks:
        raise HTTPException(status_code=404, detail="No relevant context found. Ingest documents first.")

    sources = [
        {"rank": r["rank"], "score": round(r["score"], 4), "text": r["text"][:200], "metadata": r.get("metadata", {})}
        for r in results
    ]

    # Analyst generates answer
    answer = analyst.execute(req.question, context_chunks, mode=req.mode)

    return QueryResponse(
        answer=answer,
        sources=sources,
        mode=req.mode,
        question=req.question,
    )


@app.get("/api/stats")
def get_stats():
    """Get system statistics."""
    r_stats = researcher.get_stats()
    docs = librarian.get_all_records()
    return {
        "total_documents": len(docs),
        "total_vectors": r_stats["total_vectors"],
        "vector_dimension": r_stats["vector_dimension"],
        "embedding_model": r_stats["model"],
        "llm_provider": provider,
        "llm_model": model_map.get(provider, "unknown"),
        "pdf_folder": PDF_FOLDER,
    }


@app.get("/api/god-mode-report")
def get_god_mode_report():
    """Get the God Mode master report if it exists."""
    report_path = os.path.join(os.path.dirname(__file__), "GOD_MODE_MASTER_REPORT.md")
    if os.path.exists(report_path):
        with open(report_path, "r", encoding="utf-8") as f:
            return {"exists": True, "content": f.read()}
    return {"exists": False, "content": ""}


@app.get("/api/config")
def get_config():
    """Get current system configuration."""
    return {
        "llm_provider": provider,
        "llm_model": model_map.get(provider, "unknown"),
        "embedding_model": os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2"),
        "database": os.getenv("DATABASE_URL", "sqlite:///research_metadata.db"),
        "vector_db": os.getenv("VECTOR_DB_PATH", "./faiss_research_db"),
        "pdf_folder": PDF_FOLDER,
        "modes": ["analyze", "summarize", "compare", "develop"],
    }
