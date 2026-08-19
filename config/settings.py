"""
LLM Provider Configuration
==========================

Centralised configuration for the Language Model (LLM) backend used
throughout the Research Assistant application.

Supported providers:
    - **Ollama**  (local, default)
    - **Groq**    (cloud, fast)
    - **Gemini**  (Google Generative AI)

The active provider is controlled by the ``LLM_PROVIDER`` environment
variable (defaults to ``"ollama"``).  Only the matching client is instantiated.
"""

from __future__ import annotations

import logging
import os
import subprocess
from pathlib import Path

from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_groq import ChatGroq
from langchain_ollama import ChatOllama

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Environment
# ---------------------------------------------------------------------------

# Load variables from the project root .env file
_ENV_PATH: Path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(_ENV_PATH)

# Handle LangSmith configuration gracefully
LANGSMITH_API_KEY = os.getenv("LANGSMITH_API_KEY", "")
if not LANGSMITH_API_KEY:
    # Disable LangSmith tracing if no API key is provided to prevent 403 errors
    os.environ["LANGSMITH_TRACING_V2"] = "false"
    os.environ["LANGCHAIN_TRACING_V2"] = "false"

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

# Default model name used when the Ollama provider is active.
OLLAMA_MODEL: str = "qwen2.5:3b"

# Sampling temperature for Ollama (higher = more creative, lower = more focused).
TEMPERATURE: float = 0.3

# Penalty for repeated tokens in Ollama (helps reduce repetition).
REPEAT_PENALTY: float = 1.2

# Context window (in tokens) after which repetition is penalised.
REPEAT_LAST_N: int = 128

# Default model name for Groq.
GROQ_DEFAULT_MODEL: str = "llama-3.1-8b-instant"

# Default model name for Gemini.
GEMINI_DEFAULT_MODEL: str = "gemini-1.5-pro"

# Maximum output tokens for all cloud providers and Ollama.
MAX_TOKENS: int = 4_096


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _check_ollama_model(model_name: str) -> None:
    """Verify that the requested Ollama model is installed locally.

    This is a fail-fast guard: we do **not** auto-pull (a 2 GB+ download
    mid-run is poor behaviour) and do **not** silently fall back (it would
    defeat the purpose of explicit model selection).

    Args:
        model_name: The Ollama model identifier to check (e.g. ``"qwen2.5:3b"``).

    Raises:
        FileNotFoundError: If the ``ollama`` executable is not on the PATH.
        ValueError: If the model is not found in ``ollama list`` output.
    """
    try:
        result = subprocess.run(
            ["ollama", "list"],
            capture_output=True,
            text=True,
            timeout=15,
        )
    except FileNotFoundError:
        raise FileNotFoundError(
            "Ollama executable not found. "
            "Please install Ollama (https://ollama.ai) and ensure it is running."
        )

    if model_name not in result.stdout:
        raise ValueError(
            "Ollama model '{}' is not installed locally.\n"
            "Please run:  ollama pull {}\n"
            "Then retry.".format(model_name, model_name)
        )


# ---------------------------------------------------------------------------
# Provider Selection
# ---------------------------------------------------------------------------

# Active LLM provider -- read from environment.
# Options: "ollama" (default), "groq", "gemini"
LLM_PROVIDER: str = os.getenv("LLM_PROVIDER", "ollama").lower()

# Log provider selection if logging is configured
logger.info("LLM provider selected: %s", LLM_PROVIDER)

if LLM_PROVIDER == "groq":
    _groq_api_key = os.getenv("GROQ_API_KEY")
    if not _groq_api_key:
        raise ValueError(
            "GROQ_API_KEY is required when LLM_PROVIDER is set to 'groq'. "
            "Please set it in your .env file."
        )
    llm = ChatGroq(
        model=os.getenv("GROQ_MODEL", GROQ_DEFAULT_MODEL),
        temperature=0,
        max_tokens=MAX_TOKENS,
        api_key=_groq_api_key,
    )

elif LLM_PROVIDER == "gemini":
    _gemini_api_key = os.getenv("GEMINI_API_KEY")
    if not _gemini_api_key:
        raise ValueError(
            "GEMINI_API_KEY is required when LLM_PROVIDER is set to 'gemini'. "
            "Please set it in your .env file."
        )
    llm = ChatGoogleGenerativeAI(
        model=GEMINI_DEFAULT_MODEL,
        temperature=0,
        max_tokens=MAX_TOKENS,
        api_key=_gemini_api_key,
    )

else:
    # Default: Ollama (local)
    _check_ollama_model(OLLAMA_MODEL)
    llm = ChatOllama(
        model=OLLAMA_MODEL,
        temperature=TEMPERATURE,
        num_predict=MAX_TOKENS,
        repeat_penalty=REPEAT_PENALTY,
        repeat_last_n=REPEAT_LAST_N,
    )

# Log successful initialization if logging is configured
logger.info("LLM initialised successfully.")
