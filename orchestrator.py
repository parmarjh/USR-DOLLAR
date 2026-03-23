"""
🚀 Agent Orchestrator
=====================
Coordinates the three agents in a pipeline:
  Librarian → Researcher → Analyst

This is the brain that manages the flow between agents.
"""

from typing import List, Dict, Optional
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

from setup_table import AgentSetupTable, AgentStatus
from agents import LibrarianAgent, ResearcherAgent, AnalystAgent

console = Console()


class AgentOrchestrator:
    """
    Orchestrates the three agents in a pipeline.
    
    Usage:
        orchestrator = AgentOrchestrator()
        orchestrator.display_agents()
        orchestrator.ingest_documents("./my_papers")
        result = orchestrator.query("What is the core architecture?")
    """

    def __init__(self, config: Dict = None):
        config = config or {}

        # Initialize Setup Table
        self.setup_table = AgentSetupTable()

        # Create the three agents
        self.librarian = LibrarianAgent(
            db_url=config.get("db_url", "sqlite:///research_metadata.db"),
            chunk_size=config.get("chunk_size", 500),
            chunk_overlap=config.get("chunk_overlap", 50),
        )

        self.researcher = ResearcherAgent(
            model_name=config.get("embedding_model", "all-MiniLM-L6-v2"),
            vector_db_path=config.get("vector_db_path", "./faiss_research_db"),
            top_k=config.get("top_k", 3),
        )

        self.analyst = AnalystAgent(
            llm_provider=config.get("llm_provider", "openrouter"),
            api_key=config.get("api_key"),
            temperature=config.get("temperature", 0.2),
            model_name=config.get("model_name"),
        )

        self._print_banner()

    def _print_banner(self):
        """Display startup banner."""
        banner = Panel(
            Text.from_markup(
                "[bold cyan]Multi-Agent Research System[/bold cyan]\n"
                "[dim]Three specialized agents working together[/dim]\n\n"
                "[magenta][LIBRARIAN][/magenta] -> [magenta][RESEARCHER][/magenta] -> [magenta][ANALYST][/magenta]"
            ),
            border_style="bright_blue",
            padding=(1, 4),
        )
        console.print(banner)

    # ------------------------------------------
    # Pipeline Operations
    # ------------------------------------------
    def ingest_documents(self, folder_path: str) -> Dict:
        """
        Step 1 & 2: Librarian reads PDFs, Researcher indexes them.
        """
        console.print("\n[bold cyan]=== STEP 1: LIBRARIAN PROCESSING ===[/bold cyan]")
        self.setup_table.update_status("librarian", AgentStatus.WORKING, "Processing PDFs")
        
        # Librarian extracts text
        doc_results = self.librarian.execute(folder_path)
        chunks = doc_results.get("all_chunks", [])
        
        self.setup_table.update_status("librarian", AgentStatus.DONE, 
                                        f"Processed {doc_results['total_files']} files")
        self.setup_table.increment_processed("librarian", doc_results["total_files"])

        if chunks:
            console.print("\n[bold cyan]=== STEP 2: RESEARCHER INDEXING ===[/bold cyan]")
            self.setup_table.update_status("researcher", AgentStatus.WORKING, "Embedding chunks")
            
            # Build metadata for each chunk
            metadata = []
            for doc in doc_results.get("documents", []):
                for _ in doc.get("chunks", []):
                    metadata.append({"source": doc["filename"]})

            # Researcher stores in vector DB
            self.researcher.execute(chunks, metadata)
            self.researcher.save_index()
            
            self.setup_table.update_status("researcher", AgentStatus.DONE,
                                            f"Indexed {len(chunks)} chunks")
            self.setup_table.increment_processed("researcher", len(chunks))

        return doc_results

    def query(self, question: str, mode: str = "analyze", top_k: int = None) -> str:
        """
        Step 3: Researcher retrieves context, Analyst generates insights.
        
        Args:
            question: The query to answer
            mode: "analyze", "summarize", "compare", or "develop"
            top_k: Number of context chunks to retrieve
        """
        console.print(f"\n[bold cyan]=== QUERYING: {mode.upper()} ===[/bold cyan]")
        console.print(f"[dim]Question: {question}[/dim]\n")

        # Researcher retrieves relevant context
        self.setup_table.update_status("researcher", AgentStatus.WORKING, "Retrieving context")
        results = self.researcher.retrieve(question, top_k)
        context_chunks = [r["text"] for r in results]
        
        self.setup_table.update_status("researcher", AgentStatus.DONE, 
                                        f"Retrieved {len(context_chunks)} chunks")

        if not context_chunks:
            return "[FAILED] No relevant context found. Please ingest documents first."

        # Display retrieved sources
        console.print("[dim]Retrieved sources:[/dim]")
        for r in results:
            score = f"{r['score']:.3f}"
            console.print(f"  [green]#{r['rank']}[/green] (score: {score}) {r['text'][:80]}...")

        # Analyst generates insights
        console.print()
        self.setup_table.update_status("analyst", AgentStatus.WORKING, f"{mode} mode")
        insight = self.analyst.execute(question, context_chunks, mode=mode)
        
        self.setup_table.update_status("analyst", AgentStatus.DONE, f"Generated {mode}")
        self.setup_table.increment_processed("analyst", 1)

        return insight

    def analyze(self, question: str, top_k: int = None) -> str:
        """Shortcut for analysis query."""
        return self.query(question, mode="analyze", top_k=top_k)

    def summarize(self, question: str, top_k: int = None) -> str:
        """Shortcut for summary query."""
        return self.query(question, mode="summarize", top_k=top_k)

    def compare(self, topic: str, top_k: int = 6) -> str:
        """Shortcut for comparison query."""
        return self.query(topic, mode="compare", top_k=top_k)

    def develop(self, idea: str, top_k: int = None) -> str:
        """Shortcut for idea development."""
        return self.query(idea, mode="develop", top_k=top_k)

    # ------------------------------------------
    # Display & Utility
    # ------------------------------------------
    def display_agents(self):
        """Show the agent setup table."""
        self.setup_table.display_setup_table()

    def display_config(self):
        """Show agent configurations."""
        self.setup_table.display_config_table()

    def display_pipeline(self):
        """Show the pipeline flow."""
        self.setup_table.display_pipeline_flow()

    def display_stats(self):
        """Display current system statistics."""
        researcher_stats = self.researcher.get_stats()
        db_records = self.librarian.get_all_records()

        console.print("\n[bold yellow]📊 System Statistics[/bold yellow]")
        console.print(f"  📄 Documents indexed: {len(db_records)}")
        console.print(f"  🔢 Total vectors: {researcher_stats['total_vectors']}")
        console.print(f"  📏 Vector dimension: {researcher_stats['vector_dimension']}")
        console.print(f"  🤖 Embedding model: {researcher_stats['model']}")
        console.print()

    def load_existing_index(self, path: str = None):
        """Load a previously saved vector index."""
        self.researcher.load_index(path)
