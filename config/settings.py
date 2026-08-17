import os
import subprocess
from pathlib import Path
from dotenv import load_dotenv
from langchain_ollama import ChatOllama
from langchain_groq import ChatGroq
from langchain_google_genai import ChatGoogleGenerativeAI

dotenv_path = Path(__file__).resolve().parent.parent / '.env'
load_dotenv(dotenv_path)

# ============================================================
# Ollama Configuration
# ============================================================
# Named constants for easy tuning after test runs
OLLAMA_MODEL = "qwen2.5:3b"
TEMPERATURE = 0.3
REPEAT_PENALTY = 1.2
REPEAT_LAST_N = 128

def _check_ollama_model(model_name: str) -> None:
    """Fail-fast check: raise a clear error if the given Ollama model is not
    present locally.  We do NOT auto-pull (2 GB+ download mid-run is bad
    behaviour) and do NOT silently fall back (defeats the purpose)."""
    try:
        result = subprocess.run(
            ["ollama", "list"], capture_output=True, text=True, timeout=15
        )
        if model_name not in result.stdout:
            raise ValueError(
                f"Ollama model '{model_name}' is not installed locally.\n"
                f"Please run:  ollama pull {model_name}\n"
                f"Then retry."
            )
    except FileNotFoundError:
        raise ValueError(
            "Ollama executable not found.\n"
            "Please install Ollama (https://ollama.ai) and ensure it is running."
        )


# LLM Provider configuration
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "ollama").lower()  # Options: ollama, groq, gemini

if LLM_PROVIDER == "groq":
    groq_api_key = os.getenv("GROQ_API_KEY")
    if not groq_api_key:
        raise ValueError("GROQ_API_KEY is required for Groq provider")
    llm = ChatGroq(
        model=os.getenv("GROQ_MODEL", "llama-3.1-8b-instant"),
        temperature=0,
        max_tokens=4096,
        api_key=groq_api_key
    )
elif LLM_PROVIDER == "gemini":
    gemini_api_key = os.getenv("GEMINI_API_KEY")
    if not gemini_api_key:
        raise ValueError("GEMINI_API_KEY is required for Gemini provider")
    llm = ChatGoogleGenerativeAI(
        model="gemini-1.5-pro",
        temperature=0,
        max_tokens=4096,
        api_key=gemini_api_key
    )
else:  # Default to Ollama
    _check_ollama_model(OLLAMA_MODEL)
    llm = ChatOllama(
        model=OLLAMA_MODEL,
        temperature=TEMPERATURE,
        num_predict=4096,
        repeat_penalty=REPEAT_PENALTY,
        repeat_last_n=REPEAT_LAST_N
    )
