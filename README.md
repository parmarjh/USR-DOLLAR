<p align="center">
  <img src="https://img.icons8.com/fluency/96/bot.png" alt="Multi-Agent Logo" width="96"/>
</p>

<h1 align="center">🤖 Multi-Agent Research System</h1>

<p align="center">
  <strong>A 3-agent AI pipeline that reads your PDFs, retrieves precise context, and generates structured research insights — all locally.</strong>
</p>

<p align="center">
  <a href="#-quick-start"><img src="https://img.shields.io/badge/python-3.10%2B-blue?style=for-the-badge&logo=python&logoColor=white" alt="Python 3.10+"></a>
  <a href="#-license"><img src="https://img.shields.io/badge/license-MIT-green?style=for-the-badge" alt="License: MIT"></a>
  <a href="#-tech-stack"><img src="https://img.shields.io/badge/LLM-OpenRouter%20%7C%20Gemini%20%7C%20OpenAI%20%7C%20Ollama-orange?style=for-the-badge" alt="LLM Support"></a>
  <a href="#-key-features"><img src="https://img.shields.io/badge/agents-3-purple?style=for-the-badge" alt="3 Agents"></a>
  <img src="https://img.shields.io/badge/status-active-success?style=for-the-badge" alt="Status: Active">
</p>

<p align="center">
  <a href="#-quick-start">Quick Start</a> •
  <a href="#-architecture">Architecture</a> •
  <a href="#-agents">Agents</a> •
  <a href="#-usage">Usage</a> •
  <a href="#-contributing">Contributing</a>
</p>

---

## 📖 Table of Contents

- [🧠 Motivation](#-motivation)
- [✨ Key Features](#-key-features)
- [🏗️ Architecture](#️-architecture)
- [🤖 Agents](#-agents)
- [🛠️ Tech Stack](#️-tech-stack)
- [🚀 Quick Start](#-quick-start)
- [💻 Usage](#-usage)
- [🖥️ React Web Dashboard](#️-react-web-dashboard)
- [🔥 God Mode — How to Run Agent Pipeline](#-god-mode--how-to-run-agent-pipeline)
- [❓ Important Research Questions](#-important-research-questions)
- [🧪 Running Tests](#-running-tests)
- [📸 Screenshots](#-screenshots)
- [🤝 Contributing](#-contributing)
- [📄 License](#-license)
- [📬 Contact](#-contact)

---

## 🧠 Motivation

Researchers and developers often deal with **dozens of PDF papers, reports, and documents**. Extracting actionable insights from these is tedious and error-prone.

This project solves that by creating a **team of 3 specialized AI agents** that work together in a pipeline:

1. **Scan & Index** — Automatically process all your PDFs  
2. **Search & Retrieve** — Find the most relevant paragraphs with semantic search  
3. **Analyze & Report** — Generate structured insights, comparisons, and summaries  

> **No cloud dependency required.** The system works with [OpenRouter](https://openrouter.ai) (100+ models, one API key), free-tier Gemini, or fully local models (Ollama).

---

## ✨ Key Features

| Feature | Description |
|---------|-------------|
| 🤖 **3 Specialized Agents** | Librarian, Researcher, Analyst — each with a distinct role |
| 📚 **PDF Processing** | Automatic text extraction, keyword analysis, and chunking |
| 🔍 **Semantic Search** | FAISS-powered vector search with one-to-one accuracy |
| 🧠 **Multi-LLM Support** | OpenRouter (100+ models), Gemini (free), OpenAI, Ollama (local) |
| 📊 **4 Analysis Modes** | Analyze, Summarize, Compare, and Develop |
| 🗄️ **Metadata Database** | SQLite-backed document indexing via SQLAlchemy |
| 📐 **Vector Storage** | Persistent FAISS index with save/load capability |
| 🎨 **Rich Terminal UI** | Beautiful setup tables, pipeline flow, and status tracking |
| ⚡ **Agent Setup Table** | Central registry with CRUD operations for agent management |
| 🔌 **Interactive REPL** | Type queries directly in interactive mode |
| 📦 **Zero Cloud Lock-in** | Works fully offline with Ollama, or with free-tier Gemini |

---

## 🏗️ Architecture

```
📄 PDF Documents
       │
       ▼
┌──────────────────┐
│  📚 THE LIBRARIAN │  ← Scan → Extract → Index → Chunk
│  (Data Manager)   │  ← SQLAlchemy → SQLite DB
└────────┬─────────┘
         │  text chunks + metadata
         ▼
┌──────────────────┐
│  🔍 THE RESEARCHER│  ← Embed → Store → Search → Retrieve
│  (Extraction Agent)│  ← Sentence Transformers → FAISS
└────────┬─────────┘
         │  relevant context
         ▼
┌──────────────────┐
│  🧠 THE ANALYST   │  ← Analyze → Summarize → Compare → Report
│  (Insight Agent)  │  ← OpenRouter / Gemini / OpenAI / Ollama
└────────┬─────────┘
         │
         ▼
   📊 Final Insights & Reports
```

### Data Flow

```
User PDFs ──► Librarian.execute(folder)
                  │
                  ├──► Extract text (PyMuPDF)
                  ├──► Extract keywords (frequency analysis)
                  ├──► Chunk text (overlapping windows)
                  └──► Save metadata (SQLAlchemy → SQLite)
                          │
                          ▼
              Researcher.execute(chunks)
                  │
                  ├──► Generate embeddings (Sentence Transformers)
                  ├──► Store in FAISS index
                  └──► Save index to disk
                          │
                          ▼
              Researcher.retrieve(query)
                  │
                  └──► Semantic similarity search
                          │
                          ▼
              Analyst.execute(query, context, mode)
                  │
                  ├──► Build mode-specific prompt
                  ├──► Call LLM (OpenRouter/Gemini/OpenAI/Ollama)
                  └──► Return structured insights
```

---

## 🤖 Agents

### 📚 Agent 1: The Librarian

> **Role:** Data Manager — Scans PDFs, extracts text, indexes metadata into database.

| Capability | Technology |
|-----------|-----------|
| PDF text extraction | PyMuPDF (`fitz`) |
| Keyword extraction | Frequency-based analysis |
| Document chunking | Overlapping sliding window |
| Metadata indexing | SQLAlchemy → SQLite |

```python
from agents import LibrarianAgent

librarian = LibrarianAgent(db_url="sqlite:///research.db", chunk_size=500)
results = librarian.execute("./my_papers")
# → Processes all PDFs, returns chunks + metadata
```

### 🔍 Agent 2: The Researcher

> **Role:** Extraction Agent — Embeds text into vectors, performs semantic search for one-to-one accurate context retrieval.

| Capability | Technology |
|-----------|-----------|
| Text embedding | Sentence Transformers (`all-MiniLM-L6-v2`) |
| Vector storage | FAISS (`IndexFlatL2`) |
| Similarity search | L2 distance → similarity score |
| Index persistence | Save/load to disk |

```python
from agents import ResearcherAgent

researcher = ResearcherAgent(model_name="all-MiniLM-L6-v2")
researcher.execute(chunks)                          # Store chunks
results = researcher.retrieve("core architecture")  # Search
# → Returns ranked results with scores
```

### 🧠 Agent 3: The Analyst

> **Role:** Insight Agent — Analyzes retrieved context and generates structured insights using LLMs.

| Mode | Purpose | Output |
|------|---------|--------|
| `analyze` | Deep analysis | Key findings, patterns, conclusions, recommendations |
| `summarize` | Concise summary | Executive summary, key points, notable details |
| `compare` | Compare approaches | Markdown table with feasibility, scalability, complexity |
| `develop` | Idea development | Core idea, components, implementation steps, challenges |

```python
from agents import AnalystAgent

# Using OpenRouter (recommended — access 100+ models)
analyst = AnalystAgent(llm_provider="openrouter")  # reads OPENROUTER_API_KEY from .env
report = analyst.analyze("Explain the architecture", context_chunks)
comparison = analyst.compare("RAG vs Fine-tuning", context_chunks)

# Or specify a different model
analyst = AnalystAgent(llm_provider="openrouter", model_name="anthropic/claude-3.5-sonnet")
```

---

## 🛠️ Tech Stack

| Category | Technology | Purpose |
|----------|-----------|--------|
| **Language** | Python 3.10+ | Core runtime |
| **PDF Processing** | PyMuPDF (`fitz`) | Text extraction from PDFs |
| **Embeddings** | Sentence Transformers | Text → vector embeddings |
| **Vector DB** | FAISS | Semantic similarity search |
| **Database** | SQLAlchemy + SQLite | Document metadata storage |
| **LLM Framework** | LangChain | LLM provider abstraction |
| **LLM (Recommended)** | [OpenRouter](https://openrouter.ai) | 100+ models via one API key |
| **LLM (Free)** | Google Gemini | Cloud-based analysis |
| **LLM (Local)** | Ollama | Privacy-first local inference |
| **LLM (Premium)** | OpenAI GPT-4 | High-quality analysis |
| **Terminal UI** | Rich | Beautiful tables and formatting |
| **Config** | python-dotenv | Environment variable management |

---

## 🚀 Quick Start

### Prerequisites

- **Python 3.10+** installed
- **pip** package manager
- (Recommended) An [OpenRouter API Key](https://openrouter.ai/keys) — access 100+ models
- (Alternative) A free [Gemini API Key](https://aistudio.google.com/apikey)

### 1. Clone the Repository

```bash
git clone https://github.com/parmarjh/multi-agent-research-system.git
cd multi-agent-research-system
```

### 2. Create Virtual Environment (Recommended)

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment

```bash
# Copy the example config
copy .env.example .env     # Windows
# cp .env.example .env     # macOS/Linux

# Edit .env and add your API key
# OPENROUTER_API_KEY=your-key-here
```

> 💡 **No API key?** The system works in mock mode and still processes/retrieves documents. Only the Analyst's LLM responses require an API key.

#### Supported LLM Providers

| Provider | Env Variable | Get Key | Notes |
|----------|-------------|---------|-------|
| **OpenRouter** ⭐ | `OPENROUTER_API_KEY` | [openrouter.ai/keys](https://openrouter.ai/keys) | 100+ models, one key |
| **Google Gemini** | `GEMINI_API_KEY` | [aistudio.google.com](https://aistudio.google.com/apikey) | Free tier available |
| **OpenAI** | `OPENAI_API_KEY` | [platform.openai.com](https://platform.openai.com/api-keys) | Paid |
| **Ollama** | — | [ollama.com](https://ollama.com) | Free, runs locally |

#### OpenRouter Model Selection

Set `OPENROUTER_MODEL` in your `.env` to use any model:

```bash
# Fast & free
OPENROUTER_MODEL=google/gemini-2.0-flash-001

# Premium options
OPENROUTER_MODEL=anthropic/claude-3.5-sonnet
OPENROUTER_MODEL=openai/gpt-4o
OPENROUTER_MODEL=meta-llama/llama-3-70b-instruct
OPENROUTER_MODEL=mistralai/mistral-large
```

### 5. Add Your PDFs

```bash
# Place your PDF files in the my_papers folder
copy your_paper.pdf ./my_papers/
```

### 6. Run

```bash
# View the Agent Setup Table
python main.py --setup

# Ingest your PDFs
python main.py --ingest ./my_papers

# Query the system
python main.py --query "What are the main findings?" --mode analyze

# Or use Interactive Mode
python main.py
```

---

## 💻 Usage

### Command Line Interface

```bash
# Show the agent setup table with configuration
python main.py --setup

# Ingest PDFs from a specific folder
python main.py --ingest ./my_papers

# Query with different analysis modes
python main.py --query "Summarize the key points" --mode summarize
python main.py --query "Compare RAG vs Fine-tuning" --mode compare
python main.py --query "Develop a plan for implementation" --mode develop
```

### Interactive REPL Mode

```bash
$ python main.py

🤖 Agent System> help

Available Commands:
  agents        — Show agent setup table
  config        — Show agent configurations
  pipeline      — Show pipeline flow diagram
  stats         — Show system statistics
  ingest <path> — Ingest PDFs from a folder
  load          — Load existing vector index
  analyze <q>   — Analyze a topic
  summarize <q> — Summarize a topic
  compare <q>   — Compare approaches on a topic
  develop <q>   — Develop ideas on a topic
  quit          — Exit

🤖 Agent System> ingest ./my_papers
📄 Reading: paper_1.pdf
  → 12 pages, 48 chunks, keywords: [architecture, system, ...]
✅ Processed 3 files, 34 pages, 156 chunks

🤖 Agent System> analyze What is the core architecture?
🔎 Searching... Found 3 matching chunks
📊 Analysis Result:
  [Structured analysis from LLM...]
```

### Programmatic Usage

```python
from orchestrator import AgentOrchestrator

# Initialize with OpenRouter (recommended)
orchestrator = AgentOrchestrator({
    "llm_provider": "openrouter",
    "api_key": "your-openrouter-api-key",
})

# Display agent information
orchestrator.display_agents()      # Setup table
orchestrator.display_pipeline()    # Flow diagram

# Ingest documents
orchestrator.ingest_documents("./my_papers")

# Query with different modes
analysis  = orchestrator.analyze("What is the core architecture?")
summary   = orchestrator.summarize("Key findings from the papers")
compare   = orchestrator.compare("Approach A vs Approach B")
plan      = orchestrator.develop("Build a recommendation system")

print(analysis)
```

### Agent Setup Table (Programmatic)

```python
from setup_table import AgentSetupTable, AgentRole, AgentStatus

setup = AgentSetupTable()

# Display all registered agents
setup.display_setup_table()

# Create a custom agent
setup.create_agent(
    name="The Validator",
    role=AgentRole.ANALYST,
    description="Cross-validates findings across sources",
    capabilities=["Fact checking", "Source verification", "Bias detection"],
    config={"llm_provider": "openrouter", "temperature": 0.0}
)

# Track agent status
setup.update_status("librarian", AgentStatus.WORKING, "Processing batch...")
setup.update_status("librarian", AgentStatus.DONE, "Processed 50 files")

# Export configuration
setup.export_to_json("agent_setup.json")
```

---

## 📁 Project Structure

```
multi_agent_system/
│
├── 📄 README.md              ← You are here
├── 📄 main.py                ← CLI entry point + Interactive REPL
├── 📄 orchestrator.py        ← Pipeline coordinator (Librarian → Researcher → Analyst)
├── 📄 setup_table.py         ← Agent Setup Table registry with Rich display
├── 📄 requirements.txt       ← Python dependencies
├── 📄 .env.example           ← Environment config template
├── 📄 __init__.py            ← Package init
│
├── 📁 agents/                ← Agent modules
│   ├── 📄 __init__.py        ← Package exports
│   ├── 📄 base_agent.py      ← Abstract base class with logging
│   ├── 📄 librarian.py       ← 📚 The Librarian (PDF → Chunks → DB)
│   ├── 📄 researcher.py      ← 🔍 The Researcher (Embed → FAISS → Search)
│   └── 📄 analyst.py         ← 🧠 The Analyst (Context → LLM → Insights)
│
├── 📁 my_papers/             ← Place your PDF files here
│
├── 📁 faiss_research_db/     ← [Auto-generated] FAISS vector index
│   ├── index.faiss
│   └── chunks.json
│
└── 📄 research_metadata.db   ← [Auto-generated] SQLite metadata database
```

---

## 🧪 Running Tests

```bash
# Run the setup table display test
python setup_table.py

# Test individual agents
python -c "from agents import LibrarianAgent; print(LibrarianAgent())"
python -c "from agents import ResearcherAgent; print(ResearcherAgent())"
python -c "from agents import AnalystAgent; print(AnalystAgent())"

# Full pipeline test (requires PDFs in ./my_papers)
python main.py --ingest ./my_papers
python main.py --query "test query" --mode summarize
```

> 📌 **Note:** Automated unit tests with `pytest` can be added. Contributions welcome!

---

## 🖥️ React Web Dashboard

The system includes a **beautiful React dashboard** powered by Vite:

### Start the Dashboard

```bash
# Terminal 1: Start the FastAPI backend
python -m uvicorn api:app --reload --port 8000

# Terminal 2: Start the React frontend
cd frontend
npm run dev

# Open http://localhost:5173 in your browser
```

### Dashboard Features

| Feature | Description |
|---------|-------------|
| 🤖 Agent Cards | Real-time status for all 3 agents |
| 📤 Drag & Drop Upload | Drop PDFs directly into the browser |
| 🚀 One-Click Ingest | Process all uploaded PDFs instantly |
| 🔍 4 Query Modes | Analyze, Summarize, Compare, Develop |
| 📊 Live Stats | Document count, vector count, model info |
| 📎 Source Citations | See exactly which chunks were used |
| 📚 Document Table | View all indexed documents |
| 🌙 Dark Glassmorphism | Premium dark theme with animations |

---

## 🔥 God Mode — How to Run Agent Pipeline

> **Step-by-step guide to get from zero to AI-powered research insights.**

### Step 1: Install Everything

```bash
# Clone the repository
git clone https://github.com/parmarjh/USR-DOLLAR.git
cd USR-DOLLAR/code/multi_agent_system

# Create virtual environment
python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate     # macOS/Linux

# Install Python dependencies
pip install -r requirements.txt

# Install React frontend
cd frontend
npm install
cd ..
```

### Step 2: Configure Your API Key

```bash
# Copy the example config
copy .env.example .env

# Edit .env → set your OpenRouter API key
# Get free key at: https://openrouter.ai/keys
```

### Step 3: Add Your PDFs

```bash
# Place your research papers in the my_papers/ folder
copy your_paper.pdf my_papers/

# Or generate a sample paper for testing:
python create_sample_paper.py
```

### Step 4: Start the Servers

```bash
# Terminal 1 — Backend (FastAPI)
python -m uvicorn api:app --reload --port 8000

# Terminal 2 — Frontend (React)
cd frontend
npm run dev
```

### Step 5: Run the Agent Pipeline

1. **Open** `http://localhost:5173` in your browser
2. **Upload** a PDF using the drag-and-drop area (or files are already in `my_papers/`)
3. **Click** `🚀 Ingest All PDFs` — this triggers:
   - 📚 **Librarian**: Reads PDF → extracts text → chunks → indexes to SQLite
   - 🔍 **Researcher**: Embeds chunks → stores in FAISS vector database
4. **Type a question** in the query box, e.g.:
   > "What is the core architecture of the multi-agent system?"
5. **Select a mode**: Analyze / Summarize / Compare / Develop
6. **Click** `🧠 Run Agent Pipeline` — this triggers:
   - 🔍 **Researcher**: Semantic search → finds top-3 matching chunks
   - 🧠 **Analyst**: Sends context + query to LLM → generates structured report
7. **View results** in the right panel with source citations

### Alternative: CLI Mode

```bash
# Ingest PDFs
python main.py --ingest ./my_papers

# Query
python main.py --query "What is the core architecture?" --mode analyze
python main.py --query "Compare RAG vs Fine-tuning" --mode compare
python main.py --query "Summarize the key findings" --mode summarize

# Interactive REPL
python main.py
```

---

## ❓ Important Research Questions

Ready-to-use questions for the sample paper (see `IMPORTANT_QUESTIONS.md` for full list):

### 📊 Analyze Mode
| # | Question |
|---|----------|
| 1 | What is the core architecture of the multi-agent system and how do the three agents collaborate? |
| 2 | How does the RAG pattern work in this system? |
| 3 | What are the key design decisions for vector database and embedding model selection? |
| 4 | How does the system achieve one-to-one accuracy in retrieval? |
| 5 | What are the performance benchmarks? |

### 📝 Summarize Mode
| # | Question |
|---|----------|
| 6 | Summarize the main findings and results of the paper |
| 7 | What are the key capabilities of each agent? |
| 8 | Summarize the chunking strategies evaluated |

### ⚖️ Compare Mode
| # | Question |
|---|----------|
| 9 | Compare RAG vs Fine-tuning approaches |
| 10 | Compare the three chunking strategies |
| 11 | Compare OpenRouter vs Gemini vs Ollama |

### 💡 Develop Mode
| # | Question |
|---|----------|
| 12 | Develop a plan for scaling to 10,000+ documents |
| 13 | Develop a roadmap for multi-format support |
| 14 | Develop a strategy for agent memory |

---

## 📸 Screenshots

### React Dashboard
![Multi-Agent Dashboard](https://raw.githubusercontent.com/parmarjh/USR-DOLLAR/main/code/multi_agent_system/screenshots/dashboard.png)

### Agent Setup Table (Terminal)
```
┏━━━┳━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━┓
┃ # ┃ Agent Name      ┃ Role       ┃ Description                  ┃ Status     ┃
┡━━━╇━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━┩
│ 1 │ The Librarian   │ LIBRARIAN  │ Scans PDFs, extracts text... │ 🟢 Idle    │
│ 2 │ The Researcher  │ RESEARCHER │ Performs semantic search...   │ 🟢 Idle    │
│ 3 │ The Analyst     │ ANALYST    │ Analyzes retrieved context... │ 🟢 Idle    │
└───┴─────────────────┴────────────┴──────────────────────────────┴────────────┘
```

### Pipeline Flow
```
📄 PDF Files → 📚 Librarian → 🔍 Researcher → 🧠 Analyst → 📊 Insights
```

---

## 🗺️ Roadmap

- [x] Core 3-agent pipeline (Librarian → Researcher → Analyst)
- [x] FAISS vector database with persistence
- [x] SQLite metadata indexing
- [x] Multi-LLM support (OpenRouter, Gemini, OpenAI, Ollama)
- [x] OpenRouter integration — access 100+ models via one API key
- [x] 4 analysis modes (analyze, summarize, compare, develop)
- [x] Rich terminal UI with setup tables
- [x] Interactive REPL mode
- [x] React web dashboard with FastAPI backend
- [x] Sample research paper & important questions
- [ ] Multi-format support (Word, Excel, Markdown)
- [ ] Redis Command Bus for distributed agents
- [ ] Agent memory & conversation history
- [ ] Automated test suite with pytest
- [ ] Docker containerization

---

## 🤝 Contributing

Contributions are welcome and appreciated! Here's how you can help:

1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/amazing-feature`)
3. **Commit** your changes (`git commit -m 'Add amazing feature'`)
4. **Push** to the branch (`git push origin feature/amazing-feature`)
5. **Open** a Pull Request

### Contribution Ideas

- 🧪 Add unit tests with `pytest`
- 📄 Support more file formats (DOCX, XLSX, MD)
- 🖥️ Build a Streamlit or Gradio web UI
- 🔄 Add agent-to-agent communication via Redis
- 📊 Add visualization (charts, graphs) to reports
- 🌐 Add multilingual support

Please read [CONTRIBUTING.md](CONTRIBUTING.md) for detailed guidelines.

---

## 📄 License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.

```
MIT License

Copyright (c) 2026 [YOUR NAME]

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.
```

---

## 📬 Contact

- **GitHub:** [@parmarjh](https://github.com/parmarjh)
- **Repository:** [USR-DOLLAR](https://github.com/parmarjh/USR-DOLLAR)

---

<p align="center">
  <strong>⭐ If you found this useful, give it a star!</strong>
</p>

<p align="center">
  Built with ❤️ using Python, FAISS, LangChain, OpenRouter, React, and Vite
</p>
