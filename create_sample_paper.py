"""Generate a sample research paper PDF for testing the Multi-Agent System."""
from fpdf import FPDF

pdf = FPDF()
pdf.set_auto_page_break(auto=True, margin=15)

# Page 1 - Title & Abstract
pdf.add_page()
pdf.set_font("Helvetica", "B", 22)
pdf.cell(0, 15, "Multi-Agent AI Systems:", ln=True, align="C")
pdf.cell(0, 12, "Architecture, Patterns & Applications", ln=True, align="C")
pdf.ln(10)
pdf.set_font("Helvetica", "I", 11)
pdf.cell(0, 8, "A Research Paper on Agentic AI Design Patterns", ln=True, align="C")
pdf.cell(0, 8, "Authors: Research Team, 2026", ln=True, align="C")
pdf.ln(15)

pdf.set_font("Helvetica", "B", 14)
pdf.cell(0, 10, "Abstract", ln=True)
pdf.set_font("Helvetica", "", 11)
abstract = (
    "This paper explores the design patterns and architectural choices for building "
    "multi-agent AI systems. We examine how specialized agents can collaborate to solve "
    "complex research tasks through a pipeline approach. The three-agent model (Librarian, "
    "Researcher, Analyst) demonstrates how decomposing tasks into autonomous units improves "
    "accuracy, maintainability, and scalability. We evaluate Retrieval-Augmented Generation (RAG) "
    "patterns, vector database optimizations, and LLM integration strategies for production systems."
)
pdf.multi_cell(0, 7, abstract)

# Page 1 continued - Introduction
pdf.ln(10)
pdf.set_font("Helvetica", "B", 14)
pdf.cell(0, 10, "1. Introduction", ln=True)
pdf.set_font("Helvetica", "", 11)
intro = (
    "The rise of Large Language Models (LLMs) has created new paradigms for building intelligent "
    "systems. However, a single monolithic LLM call is often insufficient for complex workflows. "
    "Multi-agent systems address this by decomposing tasks into specialized units, each with a "
    "focused responsibility.\n\n"
    "Key challenges in modern AI systems include:\n"
    "- One-to-one accuracy in information retrieval\n"
    "- Handling large document corpuses efficiently\n"
    "- Generating structured, actionable insights\n"
    "- Maintaining context across multi-step pipelines\n\n"
    "Our approach uses three specialized agents:\n"
    "1. The Librarian: Handles document ingestion, text extraction, and metadata indexing\n"
    "2. The Researcher: Manages vector embeddings and semantic search for precise retrieval\n"
    "3. The Analyst: Uses LLMs to generate analysis, summaries, comparisons, and development plans"
)
pdf.multi_cell(0, 7, intro)

# Page 2 - Architecture
pdf.add_page()
pdf.set_font("Helvetica", "B", 14)
pdf.cell(0, 10, "2. System Architecture", ln=True)
pdf.set_font("Helvetica", "", 11)
arch = (
    "The system follows a pipeline architecture where data flows sequentially through agents:\n\n"
    "PDF Documents -> Librarian Agent -> Researcher Agent -> Analyst Agent -> Final Insights\n\n"
    "2.1 The Librarian Agent\n"
    "The Librarian uses PyMuPDF for PDF text extraction, achieving near-perfect accuracy on "
    "standard PDF formats. Text is split into overlapping chunks (500 characters, 50 overlap) "
    "to preserve context boundaries. Metadata including keywords, page counts, and timestamps "
    "are stored in SQLite via SQLAlchemy ORM.\n\n"
    "2.2 The Researcher Agent\n"
    "The Researcher employs Sentence Transformers (all-MiniLM-L6-v2) for generating 384-dimensional "
    "dense embeddings. FAISS IndexFlatL2 provides exact nearest-neighbor search with L2 distance. "
    "The one-to-one accuracy principle ensures that retrieved chunks exactly match the query context "
    "without hallucination.\n\n"
    "2.3 The Analyst Agent\n"
    "The Analyst supports multiple LLM providers through a unified interface:\n"
    "- OpenRouter: Access to 100+ models including Gemini, Claude, GPT-4, Llama\n"
    "- Google Gemini: Free tier with strong performance\n"
    "- OpenAI: Premium GPT-4 capabilities\n"
    "- Ollama: Fully local inference for privacy-sensitive applications\n\n"
    "Four analysis modes are supported:\n"
    "- Analyze: Deep analysis with findings, patterns, and recommendations\n"
    "- Summarize: Concise key-point extraction\n"
    "- Compare: Side-by-side evaluation with feasibility metrics\n"
    "- Develop: Structured implementation plans"
)
pdf.multi_cell(0, 7, arch)

# Page 3 - RAG Patterns
pdf.add_page()
pdf.set_font("Helvetica", "B", 14)
pdf.cell(0, 10, "3. RAG Design Patterns", ln=True)
pdf.set_font("Helvetica", "", 11)
rag = (
    "Retrieval-Augmented Generation (RAG) is the core pattern our system uses. Unlike fine-tuning, "
    "RAG allows the system to work with any document set without retraining.\n\n"
    "3.1 Chunking Strategies\n"
    "We evaluated three chunking approaches:\n"
    "- Fixed window: Simple but may cut mid-sentence\n"
    "- Sentence-based: Preserves boundaries but variable size\n"
    "- Overlapping window: Best balance of context preservation and consistency\n\n"
    "Our implementation uses overlapping windows (500 chars, 50 overlap) as the default, "
    "providing a good balance between retrieval precision and computational cost.\n\n"
    "3.2 Embedding Models\n"
    "Sentence Transformers provide state-of-the-art embeddings for semantic search. "
    "The all-MiniLM-L6-v2 model offers an excellent speed-quality tradeoff:\n"
    "- 384 dimensions (compact, fast)\n"
    "- 22M parameters (lightweight)\n"
    "- Top-tier performance on semantic textual similarity benchmarks\n\n"
    "3.3 Vector Database Selection\n"
    "FAISS (Facebook AI Similarity Search) was chosen for:\n"
    "- In-memory speed for small-to-medium datasets\n"
    "- IndexFlatL2 for exact search (no approximation errors)\n"
    "- Easy serialization for persistent storage\n"
    "- GPU acceleration potential for scaling\n\n"
    "3.4 Context Window Management\n"
    "Retrieved chunks are ranked by L2 distance and presented to the LLM with source attribution. "
    "The system uses top-k (default: 3) retrieval to balance context richness with token limits."
)
pdf.multi_cell(0, 7, rag)

# Page 4 - Evaluation & Results
pdf.add_page()
pdf.set_font("Helvetica", "B", 14)
pdf.cell(0, 10, "4. Evaluation & Results", ln=True)
pdf.set_font("Helvetica", "", 11)
results = (
    "4.1 Retrieval Accuracy\n"
    "The one-to-one accuracy approach achieved 94.2% precision on our test set of 50 queries "
    "across 10 research papers, significantly outperforming keyword-based search (67.8%).\n\n"
    "4.2 Analysis Quality\n"
    "Using Gemini 2.0 Flash via OpenRouter, the Analyst agent produced structured outputs "
    "that were rated 4.3/5.0 by domain experts for:\n"
    "- Relevance to the query context\n"
    "- Accuracy of extracted information\n"
    "- Usefulness of recommendations\n"
    "- Structure and readability of output\n\n"
    "4.3 Processing Performance\n"
    "Benchmark results on a standard machine (8GB RAM, no GPU):\n"
    "- PDF extraction: ~2 seconds per 10-page document\n"
    "- Embedding generation: ~1.5 seconds for 100 chunks\n"
    "- FAISS search: <100ms for top-3 retrieval\n"
    "- LLM analysis: 2-5 seconds depending on model and prompt\n\n"
    "4.4 Scalability\n"
    "The system handles up to 1000 documents efficiently with the current architecture. "
    "For larger datasets, we recommend:\n"
    "- FAISS IVF index for approximate search\n"
    "- Batch processing for embedding generation\n"
    "- Redis queue for decoupled agent communication"
)
pdf.multi_cell(0, 7, results)

# Page 5 - Conclusion
pdf.add_page()
pdf.set_font("Helvetica", "B", 14)
pdf.cell(0, 10, "5. Future Directions", ln=True)
pdf.set_font("Helvetica", "", 11)
future = (
    "Several areas present opportunities for enhancement:\n\n"
    "5.1 Multi-Format Support\n"
    "Extending beyond PDF to support Word documents, Excel spreadsheets, Markdown files, "
    "and code repositories would significantly expand the system's utility.\n\n"
    "5.2 Agent Memory\n"
    "Implementing persistent conversation history and agent memory would allow the system "
    "to build on previous analyses and track evolving research themes.\n\n"
    "5.3 Distributed Architecture\n"
    "Using Redis as a command bus would enable distributed agent execution, allowing "
    "horizontal scaling and real-time collaboration between agent instances.\n\n"
    "5.4 Web Dashboard\n"
    "A React-based web interface would make the system accessible to non-technical users, "
    "providing visual upload, query, and result exploration capabilities.\n\n"
    "5.5 Advanced RAG Techniques\n"
    "- Hybrid search (combining dense and sparse retrieval)\n"
    "- Re-ranking with cross-encoders\n"
    "- Query expansion and decomposition\n"
    "- Multi-hop reasoning across chunks"
)
pdf.multi_cell(0, 7, future)

pdf.ln(10)
pdf.set_font("Helvetica", "B", 14)
pdf.cell(0, 10, "6. Conclusion", ln=True)
pdf.set_font("Helvetica", "", 11)
conclusion = (
    "Multi-agent systems represent a powerful paradigm for building intelligent research tools. "
    "By decomposing complex tasks into specialized agents (Librarian, Researcher, Analyst), "
    "we achieve better accuracy, maintainability, and flexibility compared to monolithic approaches. "
    "The combination of RAG patterns with structured agent pipelines creates a system that is "
    "both powerful and extensible, suitable for academic research, enterprise knowledge management, "
    "and personal learning applications."
)
pdf.multi_cell(0, 7, conclusion)

# Save
pdf.output("my_papers/sample_research_paper.pdf")
print("PDF created: my_papers/sample_research_paper.pdf")
