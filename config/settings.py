import os
from pathlib import Path
from dotenv import load_dotenv
from langchain_ollama import ChatOllama

dotenv_path = Path(__file__).resolve().parent.parent / '.env'
load_dotenv(dotenv_path)


llm = ChatOllama(
    model="llama3.2:3b",
    temperature=0,
    num_predict=4096
)