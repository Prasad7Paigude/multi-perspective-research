# Research Assistant

An AI-powered research assistant that generates analyst personas, conducts expert interviews, and produces comprehensive research reports using LangGraph and LangChain.

## Overview

The Research Assistant automates the research workflow through a multi-agent graph architecture:

1. **Analyst Generation** – Creates diverse AI analyst personas with different roles, affiliations, and areas of expertise, with human-in-the-loop feedback.
2. **Expert Interview** – Each analyst conducts an interview with an expert, using web search (Tavily) and Wikipedia as knowledge sources.
3. **Report Generation** – Individual interview memos are consolidated into a structured final report with introduction, insights, and conclusion.

## Architecture

```
Research Assistant
├── config/
│   └── settings.py          # LLM configuration (Ollama / Groq)
├── src/
│   ├── graph.py             # LangGraph definitions (analyst, interview, research)
│   ├── nodes.py             # Graph node functions
│   ├── prompts.py           # LLM prompt templates
│   └── state.py             # TypedDict / Pydantic state models
├── utils/
│   └── tools.py             # TavilySearch and WikipediaLoader wrappers
├── notebooks/               # Jupyter notebooks
├── main.py                  # Main entry point
├── test_run.py              # Test script with report generation
├── requirements.txt         # Python dependencies
└── .env                     # Environment variables (API keys)
```

## Requirements

- Python 3.12+
- Ollama (local) or Groq API key
- Tavily API key
- Wikipedia API access

## Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/Prasad7Paigude/research-assistant.git
   cd research-assistant
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Configure environment variables in `.env`:
   ```env
   GROQ_API_KEY=your_groq_api_key
   TAVILY_API_KEY=your_tavily_api_key
   ```

4. Run the main pipeline:
   ```bash
   python main.py
   ```

5. Run the test suite:
   ```bash
   python test_run.py
   ```

## Usage

### Main Pipeline

`main.py` runs the full research pipeline end-to-end:
- Generates analysts with human feedback
- Conducts a single interview test
- Runs the complete map-reduce research pipeline
- Outputs the final report

### Test Script

`test_run.py` executes the pipeline with predefined test parameters and generates a detailed `report.md` with execution logs, analyst details, and output summaries.

## License

MIT License
