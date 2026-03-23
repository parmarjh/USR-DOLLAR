"""
🔍 THE RESEARCHER AGENT
========================
Role: Extraction Agent — Performs semantic search for one-to-one accurate context retrieval.

Capabilities:
  • Vector embedding using Sentence Transformers
  • Semantic similarity search via FAISS
  • One-to-one accuracy retrieval
  • Top-K document matching
"""

import os
import numpy as np
from typing import List, Dict, Optional, Tuple
from .base_agent import BaseAgent

try:
    from sentence_transformers import SentenceTransformer
except ImportError:
    SentenceTransformer = None

try:
    import faiss
except ImportError:
    faiss = None


# ==========================================
# THE RESEARCHER AGENT
# ==========================================
class ResearcherAgent(BaseAgent):
    """
    🔍 The Researcher Agent
    -----------------------
    Embeds text chunks into vectors, stores them in FAISS,
    and retrieves the most relevant context for a query.
    One-to-One accuracy is the priority.
    """

    def __init__(self, model_name: str = "all-MiniLM-L6-v2",
                 vector_db_path: str = "./faiss_research_db",
                 top_k: int = 3):
        super().__init__(name="The Researcher", role="researcher")
        self.model_name = model_name
        self.vector_db_path = vector_db_path
        self.top_k = top_k

        # Storage
        self.chunks: List[str] = []
        self.chunk_metadata: List[Dict] = []  # source info per chunk
        self.index = None
        self.embedder = None
        self.vector_dim = None

        self._initialize_embedder()

    def _initialize_embedder(self):
        """Initialize the sentence transformer model."""
        if SentenceTransformer is None:
            self.log("sentence-transformers not installed. Install with: pip install sentence-transformers", "error")
            return

        self.log(f"Loading embedding model: {self.model_name}")
        self.embedder = SentenceTransformer(self.model_name)
        self.vector_dim = self.embedder.get_sentence_embedding_dimension()
        self.log(f"[OK] Model loaded (dimension: {self.vector_dim})", "success")

    def execute(self, chunks: List[str], metadata: List[Dict] = None) -> bool:
        """
        Main execution: Store document chunks into the vector database.
        
        Args:
            chunks: List of text chunks to embed and store
            metadata: Optional list of metadata dicts for each chunk
        """
        if not self.embedder:
            self.log("Embedder not initialized!", "error")
            return False

        if not chunks:
            self.log("No chunks provided", "warning")
            return False

        self.log(f"Embedding {len(chunks)} chunks...")
        
        # Generate embeddings
        embeddings = self.embedder.encode(chunks, show_progress_bar=True)
        embeddings = np.array(embeddings).astype('float32')

        # Create or extend FAISS index
        if self.index is None:
            self.index = faiss.IndexFlatL2(self.vector_dim)

        self.index.add(embeddings)
        self.chunks.extend(chunks)

        # Store metadata
        if metadata:
            self.chunk_metadata.extend(metadata)
        else:
            self.chunk_metadata.extend([{"source": "unknown"}] * len(chunks))

        self.log(
            f"Stored {len(chunks)} chunks. Total in index: {self.index.ntotal}",
            "success"
        )
        return True

    def retrieve(self, query: str, top_k: int = None) -> List[Dict]:
        """
        Retrieve the most relevant chunks for a query.
        One-to-One accuracy: returns exact matching paragraphs.
        
        Returns:
            List of dicts with 'text', 'score', 'index', and 'metadata'
        """
        if not self.embedder or self.index is None or self.index.ntotal == 0:
            self.log("No documents in the index. Store documents first!", "warning")
            return []

        k = top_k or self.top_k
        self.log(f"[SEARCH] Searching for: '{query[:60]}...' (top-{k})")

        # Encode query
        query_vector = self.embedder.encode([query]).astype('float32')

        # Search FAISS
        distances, indices = self.index.search(query_vector, k)

        results = []
        for i, (dist, idx) in enumerate(zip(distances[0], indices[0])):
            if idx < len(self.chunks):
                results.append({
                    "rank": i + 1,
                    "text": self.chunks[idx],
                    "score": float(1 / (1 + dist)),  # Convert distance to similarity
                    "distance": float(dist),
                    "chunk_index": int(idx),
                    "metadata": self.chunk_metadata[idx] if idx < len(self.chunk_metadata) else {},
                })

        self.log(f"Found {len(results)} matching chunks", "success")
        return results

    def retrieve_text(self, query: str, top_k: int = None) -> List[str]:
        """Convenience method: retrieve just the text strings."""
        results = self.retrieve(query, top_k)
        return [r["text"] for r in results]

    def save_index(self, path: str = None):
        """Save the FAISS index and chunks to disk."""
        save_path = path or self.vector_db_path
        os.makedirs(save_path, exist_ok=True)

        if self.index and self.index.ntotal > 0:
            faiss.write_index(self.index, os.path.join(save_path, "index.faiss"))

            import json
            with open(os.path.join(save_path, "chunks.json"), "w", encoding="utf-8") as f:
                json.dump({
                    "chunks": self.chunks,
                    "metadata": self.chunk_metadata,
                }, f, ensure_ascii=False, indent=2)

            self.log(f"[SAVE] Index saved to {save_path} ({self.index.ntotal} vectors)", "success")
        else:
            self.log("No index to save", "warning")

    def load_index(self, path: str = None):
        """Load a previously saved FAISS index."""
        load_path = path or self.vector_db_path
        index_file = os.path.join(load_path, "index.faiss")
        chunks_file = os.path.join(load_path, "chunks.json")

        if os.path.exists(index_file) and os.path.exists(chunks_file):
            self.index = faiss.read_index(index_file)

            import json
            with open(chunks_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                self.chunks = data["chunks"]
                self.chunk_metadata = data.get("metadata", [])

            self.log(f"[LOAD] Index loaded from {load_path} ({self.index.ntotal} vectors)", "success")
        else:
            self.log(f"No saved index found at {load_path}", "warning")

    def get_stats(self) -> Dict:
        """Get statistics about the current index."""
        return {
            "total_chunks": len(self.chunks),
            "total_vectors": self.index.ntotal if self.index else 0,
            "vector_dimension": self.vector_dim,
            "model": self.model_name,
        }
