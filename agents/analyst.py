"""
🧠 THE ANALYST AGENT
=====================
Role: Insight Agent — Analyzes retrieved context, generates summaries,
comparisons, and structured research reports.

Capabilities:
  • LLM-powered analysis (OpenRouter / Google Gemini / OpenAI / Ollama)
  • OpenRouter support — access 100+ models via one API key
  • Structured summary generation
  • Comparison reports with markdown tables
  • Idea development plans
"""

import os
from typing import List, Dict, Optional
from .base_agent import BaseAgent


# ==========================================
# THE ANALYST AGENT
# ==========================================
class AnalystAgent(BaseAgent):
    """
    🧠 The Analyst Agent
    --------------------
    Takes context chunks from the Researcher and generates
    structured insights using an LLM.
    """

    def __init__(self, llm_provider: str = "gemini",
                 api_key: str = None,
                 temperature: float = 0.2,
                 model_name: str = None):
        super().__init__(name="The Analyst", role="analyst")
        self.llm_provider = llm_provider.lower()
        self.api_key = api_key
        self.temperature = temperature
        self.model_name = model_name
        self.llm = None

        self._initialize_llm()

    def _initialize_llm(self):
        """Initialize the LLM based on provider."""
        try:
            if self.llm_provider == "openrouter":
                self._init_openrouter()
            elif self.llm_provider == "gemini":
                self._init_gemini()
            elif self.llm_provider == "openai":
                self._init_openai()
            elif self.llm_provider == "ollama":
                self._init_ollama()
            else:
                self.log(f"Unknown provider: {self.llm_provider}. Using mock mode.", "warning")
        except Exception as e:
            self.log(f"LLM init failed: {e}. Running in mock mode.", "warning")

    def _init_openrouter(self):
        """Initialize OpenRouter (access 100+ models via one API)."""
        try:
            from langchain_openai import ChatOpenAI
            key = self.api_key or os.getenv("OPENROUTER_API_KEY")
            if not key:
                self.log("No OPENROUTER_API_KEY found. Set it in .env or pass api_key", "warning")
                self.log("Get your key at: https://openrouter.ai/keys", "info")
                return
            model = self.model_name or os.getenv("OPENROUTER_MODEL", "google/gemini-2.0-flash-001")
            self.llm = ChatOpenAI(
                model=model,
                openai_api_key=key,
                openai_api_base="https://openrouter.ai/api/v1",
                temperature=self.temperature,
                default_headers={
                    "HTTP-Referer": "https://github.com/multi-agent-research-system",
                    "X-Title": "Multi-Agent Research System",
                },
            )
            self.log(f"OpenRouter initialized (model: {model})", "success")
        except ImportError:
            self.log("Install: pip install langchain-openai", "error")

    def _init_gemini(self):
        """Initialize Google Gemini."""
        try:
            from langchain_google_genai import ChatGoogleGenerativeAI
            key = self.api_key or os.getenv("GEMINI_API_KEY")
            if not key:
                self.log("No GEMINI_API_KEY found. Set it in .env or pass api_key", "warning")
                return
            self.llm = ChatGoogleGenerativeAI(
                model=self.model_name or "gemini-2.0-flash",
                google_api_key=key,
                temperature=self.temperature,
            )
            self.log("Google Gemini initialized", "success")
        except ImportError:
            self.log("Install: pip install langchain-google-genai", "error")

    def _init_openai(self):
        """Initialize OpenAI."""
        try:
            from langchain_openai import ChatOpenAI
            key = self.api_key or os.getenv("OPENAI_API_KEY")
            if not key:
                self.log("No OPENAI_API_KEY found", "warning")
                return
            self.llm = ChatOpenAI(
                model=self.model_name or "gpt-4",
                openai_api_key=key,
                temperature=self.temperature,
            )
            self.log("OpenAI initialized", "success")
        except ImportError:
            self.log("Install: pip install langchain-openai", "error")

    def _init_ollama(self):
        """Initialize Ollama (local LLM)."""
        try:
            from langchain_ollama import ChatOllama
            self.llm = ChatOllama(
                model=self.model_name or "llama3",
                temperature=self.temperature,
            )
            self.log("Ollama initialized", "success")
        except ImportError:
            self.log("Install: pip install ollama", "error")

    def execute(self, query: str, context_chunks: List[str],
                mode: str = "analyze") -> str:
        """
        Main execution: Generate insights from context.
        
        Args:
            query: The user's question or topic
            context_chunks: Retrieved text chunks from the Researcher
            mode: "analyze", "summarize", "compare", or "develop"
        """
        self.log(f"Mode: {mode} | Query: '{query[:50]}...'")

        context = "\n\n".join([
            f"[Source {i+1}]:\n{chunk}" for i, chunk in enumerate(context_chunks)
        ])

        # Select prompt based on mode
        prompt = self._build_prompt(query, context, mode)

        # Call LLM or return mock
        if self.llm:
            try:
                response = self.llm.invoke(prompt)
                result = response.content if hasattr(response, 'content') else str(response)
                self.log(f"✅ Analysis complete ({len(result)} chars)", "success")
                return result
            except Exception as e:
                self.log(f"LLM error: {e}", "error")
                return f"[Error: {e}]"
        else:
            self.log("Running in MOCK mode (no LLM configured)", "warning")
            return self._mock_response(query, context_chunks, mode)

    def _build_prompt(self, query: str, context: str, mode: str) -> str:
        """Build the appropriate prompt based on analysis mode."""
        prompts = {
            "analyze": f"""You are a Research Analyst. Analyze the following context and provide detailed insights.

CONTEXT:
{context}

QUERY: {query}

Provide a thorough analysis with:
1. Key Findings
2. Important Patterns
3. Conclusions
4. Recommendations""",

            "summarize": f"""You are a Research Summarizer. Create a concise, structured summary.

CONTEXT:
{context}

QUERY: {query}

Provide a summary with:
- Executive Summary (2-3 sentences)
- Key Points (bullet list)
- Notable Details""",

            "compare": f"""You are a Technical Evaluator. Compare the different approaches/ideas found in the context.

CONTEXT:
{context}

TOPIC: {query}

Provide a comparison with:
1. List the distinct approaches found
2. Compare them based on: Feasibility, Scalability, and Complexity
3. Decision: Which approach is better for a startup/MVP?
4. Format as a clean Markdown table where possible""",

            "develop": f"""You are a Research Expert and Idea Developer. Develop a structured plan from the research.

CONTEXT:
{context}

USER REQUEST: {query}

Provide a structured development plan with:
1. Core Idea
2. Key Components
3. Implementation Steps
4. Potential Challenges
5. Next Actions""",
        }

        return prompts.get(mode, prompts["analyze"])

    def _mock_response(self, query: str, chunks: List[str], mode: str) -> str:
        """Generate a mock response when no LLM is configured."""
        return (
            f"📋 MOCK {mode.upper()} REPORT\n"
            f"{'=' * 40}\n\n"
            f"Query: {query}\n"
            f"Sources analyzed: {len(chunks)} chunks\n\n"
            f"⚠️  This is a mock response. Configure an LLM provider:\n"
            f"  • Set OPENROUTER_API_KEY in .env (recommended — 100+ models)\n"
            f"  • Or set GEMINI_API_KEY (free tier available)\n"
            f"  • Or set OPENAI_API_KEY\n"
            f"  • Or install Ollama for local inference\n"
        )

    def analyze(self, query: str, chunks: List[str]) -> str:
        """Shortcut: Run analysis mode."""
        return self.execute(query, chunks, mode="analyze")

    def summarize(self, query: str, chunks: List[str]) -> str:
        """Shortcut: Run summarize mode."""
        return self.execute(query, chunks, mode="summarize")

    def compare(self, topic: str, chunks: List[str]) -> str:
        """Shortcut: Run comparison mode."""
        return self.execute(topic, chunks, mode="compare")

    def develop_idea(self, question: str, chunks: List[str]) -> str:
        """Shortcut: Run idea development mode."""
        return self.execute(question, chunks, mode="develop")
