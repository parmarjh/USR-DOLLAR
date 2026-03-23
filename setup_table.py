"""
Multi-Agent Research System - Configuration & Setup Tables
==========================================================
Defines the Agent Setup Table and system configuration.
Each agent is registered with its role, capabilities, and status.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, Dict, List, Any
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
import json
import os


# ==========================================
# Agent Status Enum (ASCII SAFE)
# ==========================================
class AgentStatus(Enum):
    IDLE = "[IDLE]"
    WORKING = "[WORKING]"
    DONE = "[DONE]"
    ERROR = "[ERROR]"
    DISABLED = "[DISABLED]"


# ==========================================
# Agent Role Enum
# ==========================================
class AgentRole(Enum):
    LIBRARIAN = "librarian"
    RESEARCHER = "researcher"
    ANALYST = "analyst"


# ==========================================
# Agent Definition (Setup Table Row)
# ==========================================
@dataclass
class AgentDefinition:
    """Represents a single agent in the Setup Table."""
    name: str
    role: AgentRole
    description: str
    capabilities: List[str]
    status: AgentStatus = AgentStatus.IDLE
    config: Dict[str, Any] = field(default_factory=dict)
    last_action: str = "-"
    processed_count: int = 0

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "role": self.role.value,
            "description": self.description,
            "capabilities": self.capabilities,
            "status": self.status.value,
            "config": self.config,
            "last_action": self.last_action,
            "processed_count": self.processed_count,
        }


# ==========================================
# Agent Setup Table (Registry)
# ==========================================
class AgentSetupTable:
    """
    Central registry for all agents.
    Manages agent lifecycle: create, configure, enable/disable, monitor.
    """

    # Default agent blueprints
    DEFAULT_AGENTS = [
        AgentDefinition(
            name="The Librarian",
            role=AgentRole.LIBRARIAN,
            description="Scans PDFs, extracts text, indexes metadata into database",
            capabilities=[
                "PDF text extraction (PyMuPDF)",
                "Keyword extraction",
                "Metadata indexing (SQLAlchemy)",
                "Document chunking",
                "File type detection",
            ],
            config={
                "db_url": "sqlite:///research_metadata.db",
                "supported_formats": [".pdf"],
                "chunk_size": 500,
                "chunk_overlap": 50,
            },
        ),
        AgentDefinition(
            name="The Researcher",
            role=AgentRole.RESEARCHER,
            description="Performs semantic search for one-to-one accurate context retrieval",
            capabilities=[
                "Vector embedding (Sentence Transformers)",
                "Semantic similarity search (FAISS)",
                "One-to-one accuracy retrieval",
                "Top-K document matching",
                "Context window management",
            ],
            config={
                "embedding_model": "all-MiniLM-L6-v2",
                "vector_dim": 384,
                "top_k": 3,
                "vector_db_path": "./faiss_research_db",
            },
        ),
        AgentDefinition(
            name="The Analyst",
            role=AgentRole.ANALYST,
            description="Analyzes retrieved context and generates structured insights",
            capabilities=[
                "LLM-powered analysis (OpenRouter / Gemini / OpenAI / Ollama)",
                "OpenRouter access",
                "Structured summary generation",
                "Comparison reports",
                "Idea development",
            ],
            config={
                "llm_provider": "openrouter",
                "model": "google/gemini-2.0-flash-001",
                "temperature": 0.2,
                "max_tokens": 2048,
            },
        ),
    ]

    def __init__(self):
        self.agents: Dict[str, AgentDefinition] = {}
        self.console = Console(force_terminal=False)
        self._register_defaults()

    def _register_defaults(self):
        """Register the 3 default agents."""
        for agent_def in self.DEFAULT_AGENTS:
            self.agents[agent_def.role.value] = agent_def

    # ------------------------------------------
    # CRUD Operations
    # ------------------------------------------
    def create_agent(self, name: str, role: AgentRole, description: str,
                     capabilities: List[str], config: Dict = None) -> AgentDefinition:
        """Create and register a new agent."""
        agent = AgentDefinition(
            name=name,
            role=role,
            description=description,
            capabilities=capabilities,
            config=config or {},
        )
        self.agents[role.value] = agent
        self.console.print(f"[green][OK] Agent '{name}' created with role '{role.value}'[/green]")
        return agent

    def get_agent(self, role: str) -> Optional[AgentDefinition]:
        """Get agent by role."""
        return self.agents.get(role)

    def update_status(self, role: str, status: AgentStatus, action: str = None):
        """Update agent status and optionally last action."""
        if role in self.agents:
            self.agents[role].status = status
            if action:
                self.agents[role].last_action = action

    def increment_processed(self, role: str, count: int = 1):
        """Increment the processed count for an agent."""
        if role in self.agents:
            self.agents[role].processed_count += count

    def disable_agent(self, role: str):
        """Disable an agent."""
        if role in self.agents:
            self.agents[role].status = AgentStatus.DISABLED

    def enable_agent(self, role: str):
        """Re-enable an agent."""
        if role in self.agents:
            self.agents[role].status = AgentStatus.IDLE

    # ------------------------------------------
    # Display Methods
    # ------------------------------------------
    def display_setup_table(self):
        """Display the Agent Setup Table with Rich formatting."""
        table = Table(
            title="Multi-Agent Setup Table",
            title_style="bold cyan",
            border_style="bright_blue",
            show_lines=True,
            padding=(0, 1),
        )

        table.add_column("#", style="dim", width=3, justify="center")
        table.add_column("Agent Name", style="bold magenta", min_width=15)
        table.add_column("Role", style="cyan", min_width=12)
        table.add_column("Description", style="white", min_width=30)
        table.add_column("Status", justify="center", min_width=12)
        table.add_column("Capabilities", style="green", min_width=30)
        table.add_column("Processed", justify="center", style="yellow", min_width=10)
        table.add_column("Last Action", style="dim", min_width=15)

        for idx, (role, agent) in enumerate(self.agents.items(), 1):
            caps = "\n".join([f"- {c}" for c in agent.capabilities[:3]])
            if len(agent.capabilities) > 3:
                caps += f"\n  (+{len(agent.capabilities) - 3} more)"

            table.add_row(
                str(idx),
                agent.name,
                agent.role.value.upper(),
                agent.description,
                agent.status.value,
                caps,
                str(agent.processed_count),
                agent.last_action,
            )

        self.console.print()
        self.console.print(table)
        self.console.print()

    def display_config_table(self):
        """Display the configuration for each agent."""
        table = Table(
            title="Agent Configuration",
            title_style="bold yellow",
            border_style="yellow",
            show_lines=True,
        )

        table.add_column("Agent", style="bold magenta", min_width=15)
        table.add_column("Config Key", style="cyan", min_width=20)
        table.add_column("Value", style="white", min_width=30)

        for role, agent in self.agents.items():
            for key, value in agent.config.items():
                table.add_row(agent.name, key, str(value))
            table.add_row("", "", "")  # Separator

        self.console.print()
        self.console.print(table)
        self.console.print()

    def display_pipeline_flow(self):
        """Display the agent pipeline flow visually."""
        flow = Panel(
            Text.from_markup(
                "[bold cyan]DOCS: PDF Files[/bold cyan]\n"
                "     |\n"
                "     V\n"
                "[bold magenta]LIBRARIAN[/bold magenta]\n"
                "  [dim]Scan -> Extract -> Index -> Chunk[/dim]\n"
                "     |\n"
                "     V\n"
                "[bold magenta]RESEARCHER[/bold magenta]\n"
                "  [dim]Embed -> Store -> Search -> Retrieve[/dim]\n"
                "     |\n"
                "     V\n"
                "[bold magenta]ANALYST[/bold magenta]\n"
                "  [dim]Analyze -> Summarize -> Compare -> Report[/dim]\n"
                "     |\n"
                "     V\n"
                "[bold green]STATS: Final Insights[/bold green]"
            ),
            title="Agent Pipeline Flow",
            title_align="center",
            border_style="bright_blue",
            padding=(1, 4),
        )
        self.console.print()
        self.console.print(flow)
        self.console.print()

    def export_to_json(self, filepath: str = "agent_setup.json"):
        """Export the setup table to JSON."""
        data = {role: agent.to_dict() for role, agent in self.agents.items()}
        with open(filepath, "w") as f:
            json.dump(data, f, indent=2)
        self.console.print(f"[green][FILE] Setup table exported to {filepath}[/green]")


# ==========================================
# Quick Test
# ==========================================
if __name__ == "__main__":
    setup = AgentSetupTable()
    setup.display_setup_table()
    setup.display_config_table()
    setup.display_pipeline_flow()
