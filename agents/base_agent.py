"""
🔧 Base Agent
=============
Abstract base class for all agents in the system.
Provides common interface and logging.
"""

from abc import ABC, abstractmethod
from datetime import datetime
from rich.console import Console

console = Console()


class BaseAgent(ABC):
    """Base class that all agents inherit from."""

    def __init__(self, name: str, role: str):
        self.name = name
        self.role = role
        self.created_at = datetime.now()
        self._log_history = []

    def log(self, message: str, level: str = "info"):
        """Log an action with timestamp."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        entry = f"[{timestamp}] [{self.name}] {message}"
        self._log_history.append(entry)

        style_map = {
            "info": "cyan",
            "success": "green",
            "warning": "yellow",
            "error": "red",
        }
        style = style_map.get(level, "white")
        console.print(f"  [{style}]{entry}[/{style}]")

    @abstractmethod
    def execute(self, *args, **kwargs):
        """Execute the agent's primary task."""
        pass

    def get_history(self):
        """Return the agent's action history."""
        return self._log_history

    def __repr__(self):
        return f"<{self.__class__.__name__}(name='{self.name}', role='{self.role}')>"
