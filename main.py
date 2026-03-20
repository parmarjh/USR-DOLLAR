"""
🚀 Multi-Agent Research System — Main Entry Point
===================================================

Usage:
    python main.py                      # Interactive mode
    python main.py --setup              # Show agent setup table
    python main.py --ingest ./papers    # Ingest PDFs from folder
    python main.py --query "question"   # Query the system
"""

import argparse
import os
import sys
from dotenv import load_dotenv
from rich.console import Console
from rich.prompt import Prompt, Confirm

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from setup_table import AgentSetupTable
from orchestrator import AgentOrchestrator

console = Console()

# Load environment variables
load_dotenv()


def get_config() -> dict:
    """Build config from environment variables."""
    provider = os.getenv("LLM_PROVIDER", "openrouter")

    # Resolve API key based on provider
    api_key_map = {
        "openrouter": os.getenv("OPENROUTER_API_KEY"),
        "gemini": os.getenv("GEMINI_API_KEY"),
        "openai": os.getenv("OPENAI_API_KEY"),
        "ollama": None,  # Ollama runs locally, no key needed
    }
    api_key = api_key_map.get(provider) or os.getenv("OPENROUTER_API_KEY") or os.getenv("GEMINI_API_KEY") or os.getenv("OPENAI_API_KEY")

    # Resolve model name based on provider
    model_map = {
        "openrouter": os.getenv("OPENROUTER_MODEL", "google/gemini-2.0-flash-001"),
        "gemini": os.getenv("GEMINI_MODEL", "gemini-2.0-flash"),
        "openai": os.getenv("OPENAI_MODEL", "gpt-4"),
        "ollama": os.getenv("OLLAMA_MODEL", "llama3"),
    }
    model_name = model_map.get(provider, "google/gemini-2.0-flash-001")

    return {
        "llm_provider": provider,
        "api_key": api_key,
        "model_name": model_name,
        "db_url": os.getenv("DATABASE_URL", "sqlite:///research_metadata.db"),
        "vector_db_path": os.getenv("VECTOR_DB_PATH", "./faiss_research_db"),
        "embedding_model": os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2"),
        "pdf_folder": os.getenv("PDF_FOLDER", "./my_papers"),
    }


def show_setup_table():
    """Display the Agent Setup Table."""
    setup = AgentSetupTable()
    setup.display_setup_table()
    setup.display_config_table()
    setup.display_pipeline_flow()


def interactive_mode(orchestrator: AgentOrchestrator):
    """Run the system in interactive mode."""
    console.print("[bold green]🎯 Interactive Mode[/bold green]")
    console.print("[dim]Type 'help' for commands, 'quit' to exit[/dim]\n")

    while True:
        try:
            user_input = Prompt.ask("\n[bold cyan]🤖 Agent System[/bold cyan]")
        except (KeyboardInterrupt, EOFError):
            console.print("\n[yellow]Goodbye! 👋[/yellow]")
            break

        if not user_input.strip():
            continue

        cmd = user_input.strip().lower()

        if cmd in ("quit", "exit", "q"):
            console.print("[yellow]Goodbye! 👋[/yellow]")
            break

        elif cmd == "help":
            console.print("""
[bold cyan]Available Commands:[/bold cyan]
  [green]agents[/green]        — Show agent setup table
  [green]config[/green]        — Show agent configurations
  [green]pipeline[/green]      — Show pipeline flow diagram
  [green]stats[/green]         — Show system statistics
  [green]ingest <path>[/green] — Ingest PDFs from a folder
  [green]load[/green]          — Load existing vector index
  [green]analyze <q>[/green]   — Analyze a topic
  [green]summarize <q>[/green] — Summarize a topic
  [green]compare <q>[/green]   — Compare approaches on a topic
  [green]develop <q>[/green]   — Develop ideas on a topic
  [green]help[/green]          — Show this help
  [green]quit[/green]          — Exit
            """)

        elif cmd == "agents":
            orchestrator.display_agents()

        elif cmd == "config":
            orchestrator.display_config()

        elif cmd == "pipeline":
            orchestrator.display_pipeline()

        elif cmd == "stats":
            orchestrator.display_stats()

        elif cmd == "load":
            orchestrator.load_existing_index()

        elif cmd.startswith("ingest"):
            parts = cmd.split(maxsplit=1)
            path = parts[1] if len(parts) > 1 else get_config()["pdf_folder"]
            orchestrator.ingest_documents(path)
            orchestrator.display_agents()

        elif cmd.startswith("analyze "):
            query = user_input[8:].strip()
            result = orchestrator.analyze(query)
            console.print(f"\n[bold green]📊 Analysis Result:[/bold green]\n{result}")

        elif cmd.startswith("summarize "):
            query = user_input[10:].strip()
            result = orchestrator.summarize(query)
            console.print(f"\n[bold green]📝 Summary:[/bold green]\n{result}")

        elif cmd.startswith("compare "):
            topic = user_input[8:].strip()
            result = orchestrator.compare(topic)
            console.print(f"\n[bold green]⚖️  Comparison:[/bold green]\n{result}")

        elif cmd.startswith("develop "):
            idea = user_input[8:].strip()
            result = orchestrator.develop(idea)
            console.print(f"\n[bold green]💡 Development Plan:[/bold green]\n{result}")

        else:
            # Treat as a general analysis query
            result = orchestrator.analyze(user_input)
            console.print(f"\n[bold green]📊 Result:[/bold green]\n{result}")


def main():
    parser = argparse.ArgumentParser(description="Multi-Agent Research System")
    parser.add_argument("--setup", action="store_true", help="Show agent setup table")
    parser.add_argument("--ingest", type=str, help="Ingest PDFs from folder path")
    parser.add_argument("--query", type=str, help="Query the system")
    parser.add_argument("--mode", type=str, default="analyze",
                        choices=["analyze", "summarize", "compare", "develop"],
                        help="Query mode")
    args = parser.parse_args()

    # Show setup table only
    if args.setup:
        show_setup_table()
        return

    # Create orchestrator
    config = get_config()
    orchestrator = AgentOrchestrator(config)

    # Ingest mode
    if args.ingest:
        orchestrator.ingest_documents(args.ingest)
        orchestrator.display_agents()
        return

    # Query mode
    if args.query:
        orchestrator.load_existing_index()
        result = orchestrator.query(args.query, mode=args.mode)
        console.print(f"\n[bold green]📊 Result:[/bold green]\n{result}")
        return

    # Default: Interactive mode
    interactive_mode(orchestrator)


if __name__ == "__main__":
    main()
