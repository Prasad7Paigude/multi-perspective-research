# 🔬 Research Assistant: AI-Powered Multi-Agent Research Infrastructure

[![Python 3.12+](https://img.shields.io/badge/Python-3.12+-3670A0?style=flat&logo=python&logoColor=ffdd54)](https://www.python.org/downloads/)
[![LangGraph 1.2.9](https://img.shields.io/badge/LangGraph-1.2.9-000000?style=flat)](https://langchain-ai.github.io/langgraph/)
[![LangChain 1.3.11](https://img.shields.io/badge/LangChain-1.3.11-1C3C3C?style=flat&logo=langchain&logoColor=fff)](https://github.com/langchain-ai/langchain)
[![FastAPI 0.140.1](https://img.shields.io/badge/FastAPI-0.140.1-009688?style=flat&logo=fastapi&logoColor=fff)](https://fastapi.tiangolo.com/)
[![Uvicorn 0.50.2](https://img.shields.io/badge/Uvicorn-0.50.2-4990E2?style=flat)](https://www.uvicorn.org/)

> **Status:** Practice project to showcase **LangGraph and its concepts** (nodes, graphs, reducers, map-reduce, memory, multi-agent systems). **Not intended for production use**.

## 🎯 Core Mission

### The Problem
In the AI landscape, there is a growing need to understand how **multi-agent systems** can be orchestrated to perform **complex workflows**. This project was created to explore and demonstrate the capabilities of **LangGraph** in building such systems.

### The Solution
**Research Assistant** is a **practice project** built on **LangGraph** and **LangChain** to demonstrate:

- ✅ **Multi-agent collaboration** with **LangGraph state machines**.
- ✅ **Graph-based workflows** (nodes, edges, reducers, map-reduce).
- ✅ **Human-in-the-loop feedback** for analyst refinement.
- ✅ **Parallel interviews** with **Tavily + Wikipedia RAG**.
- ✅ **Real-time streaming** via **FastAPI SSE**.
### Purpose
**Key Takeaways**:
- Demonstrates **LangGraph** for **multi-agent orchestration**.
- Implements **map-reduce patterns** for report synthesis.
- Uses **RAG (Tavily + Wikipedia)** for contextual answers.
- Showcases **human-in-the-loop feedback** and **real-time streaming**.

### Graph-Based Architecture
This project implements **three LangGraph state machines** that work together to orchestrate the research pipeline:

#### 1. Analyst Generation Graph
![Analyst Generation Graph](media/analyst%20generation%20graph.png)

- **Purpose**: Creates **diverse AI analyst personas** for a given research topic.
- **Nodes**:
  - `create_analysts`: Generates analyst personas using **LLM structured output**.
  - `human_feedback`: **Human-in-the-loop checkpoint** for reviewing and refining analysts.
- **Flow**:
  `START → create_analysts → human_feedback → (loop or END)`
  - If feedback is provided, the graph **regenerates analysts** with the new input.

---

#### 2. Interview Sub-Graph
![Interviews Sub-Graph](media/interviews%20sub-graph.png)

- **Purpose**: Conducts **multi-turn interviews** between an analyst and an expert AI.
- **Nodes**:
  - `generate_question`: Analyst formulates a question.
  - `search_web` (Tavily): Retrieves **real-time web results**.
  - `search_wikipedia`: Retrieves **Wikipedia articles**.
  - `generate_answer`: Expert AI answers using retrieved context.
  - `route_messages`: Decides whether to **continue the interview** or **save the transcript**.
  - `save_interview`: Stores the conversation transcript.
  - `write_section`: Generates a **report section** from the interview.
- **Flow**:
  `START → generate_question → [search_web + search_wikipedia] → generate_answer → route_messages → (loop or save_interview) → write_section → END`
  - **Parallel execution**: `search_web` and `search_wikipedia` run **concurrently** for efficiency.

---

#### 3. Full Research Graph (Map-Reduce)
![Full Research Graph](media/Full%20Research%20Graph.png)

- **Purpose**: **Orchestrates the entire research pipeline** using a **map-reduce pattern**.
- **Nodes**:
  - `human_feedback`: User reviews/refines analysts (interrupt point).
  - `conduct_interview`: **Parallel map phase** – each analyst interviews an expert.
  - `write_report`: **Reduce phase** – consolidates interview memos into body content.
  - `write_introduction`: Generates the **report introduction**.
  - `write_conclusion`: Generates the **report conclusion**.
  - `finalize_report`: Assembles everything into the **final report**.
- **Flow**:
  `START → human_feedback → conduct_interview → [write_report + write_introduction + write_conclusion] → finalize_report → END`
  - **Map-Reduce**: Interviews run in **parallel**, and results are **reduced** into a single report.

---

### Module Topology
```
Research Assistant/
├── api/
│   ├── __init__.py
│   ├── schemas.py           # Pydantic request/response models
│   └── server.py            # FastAPI backend with SSE streaming
│
├── config/
│   ├── __init__.py
│   └── settings.py          # LLM configuration (Ollama / Groq / Gemini)
│
├── src/
│   ├── __init__.py
│   ├── graph.py             # LangGraph definitions (analyst, interview, research)
│   ├── nodes.py             # Node functions (analyst generation, interviews, report writing)
│   ├── prompts.py           # LLM prompt templates for all agents
│   └── state.py             # TypedDict / Pydantic state models
│
├── utils/
│   ├── __init__.py
│   └── tools.py             # TavilySearch and WikipediaLoader wrappers
│
├── frontend/                # React + TypeScript + Vite frontend
│   ├── public/
│   ├── src/
│   │   ├── assets/
│   │   ├── components/
│   │   ├── hooks/
│   │   ├── types/
│   │   ├── App.tsx
│   │   ├── main.tsx
│   │   ├── index.css
│   │   └── markdown.css
│   ├── index.html
│   ├── package.json
│   └── vite.config.ts
│
├── notebooks/
│   └── research-assistant.ipynb
│
├── media/                   # Graph diagrams
│   ├── analyst generation graph.png
│   ├── interviews sub-graph.png
│   └── Full Research Graph.png
│
├── .env.example             # Environment variable template
├── requirements.txt         # Python dependencies
├── start_api.sh             # API server startup script
└── README.md
```

## 🚀 Engineering Triumphs

### 1. Multi-Agent Collaboration with LangGraph
- **Problem**: Traditional research workflows are **linear and manual**, with no way to **orchestrate multiple agents** efficiently.
- **Solution**:
  - **Three LangGraph state machines** (`Analyst Generation`, `Interview Sub-Graph`, `Full Research Graph`) work together to **automate the entire pipeline**.
  - **Human-in-the-loop feedback**: Users can **review and refine analysts** before proceeding.
  - **Parallel interviews**: Multiple analysts **interview experts concurrently** for efficiency.
- **Result**:
  - **Fully automated research workflow** from analyst generation to report synthesis.
  - **Scalable and modular** – new agents or steps can be added without breaking existing logic.

---

### 2. Map-Reduce Pattern for Report Synthesis
- **Problem**: Consolidating **multiple interview transcripts** into a **single coherent report** is complex and error-prone.
- **Solution**:
  - **Map Phase**: Each analyst conducts an **independent interview** in parallel.
  - **Reduce Phase**: Interview memos are **consolidated** into a **structured report** with:
    - **Introduction** (generated by `write_introduction`).
    - **Body** (synthesized from all sections by `write_report`).
    - **Conclusion** (generated by `write_conclusion`).
- **Result**:
  - **Efficient parallel execution** reduces total research time.
  - **Structured output** ensures **consistency and readability**.

---

### 3. Real-Time Streaming with FastAPI & SSE
- **Problem**: Users want **real-time updates** on research progress, but traditional REST APIs require **polling**.
- **Solution**:
  - **Server-Sent Events (SSE)** stream **interview progress**, **section generation**, and **final report assembly** in real-time.
  - Endpoints:
    - `/api/research/stream/{thread_id}`: Streams **live updates** (analysts, interviews, sections, report).
    - `/api/research/result/{thread_id}`: Retrieves the **final report** after completion.
- **Result**:
  - **Seamless user experience** with **no polling overhead**.
  - **Transparent progress tracking** for long-running research tasks.

---

### 4. Retrieval-Augmented Generation (RAG) for Contextual Answers
- **Problem**: LLMs **hallucinate** or provide **generic answers** without **real-world context**.
- **Solution**:
  - **Tavily Web Search**: Retrieves **up-to-date web results** for expert answers.
  - **Wikipedia Loader**: Fetches **structured knowledge** from Wikipedia.
  - **Parallel Retrieval**: Both sources are queried **simultaneously** for efficiency.
- **Result**:
  - **Accurate, context-rich answers** grounded in **real-world data**.
  - **Reduced hallucinations** by leveraging **retrieval-augmented generation (RAG)**.

---

### 5. Structured Prompts & State Management
- **Problem**: LLMs **ignore instructions** or **lose context** in long conversations.
- **Solution**:
  - **Pydantic Models** (`Analyst`, `Perspectives`, `SearchQuery`) ensure **structured outputs**.
  - **TypedDict States** (`GenerateAnalystsState`, `InterviewState`, `ResearchGraphState`) maintain **context across nodes**.
  - **Custom Reducers** (e.g., `_reduce_max_turns`) handle **state merging** in parallel workflows.
- **Result**:
  - **Consistent, predictable** LLM behavior.
  - **No context loss** between graph nodes.

---

### 6. Multi-Provider LLM Support
- **Problem**: Users want **flexibility** in choosing LLM providers (local vs. cloud).
- **Solution**:
  - **Ollama (Local)**: Default provider for **offline, private** inference (e.g., `qwen2.5:3b`).
  - **Groq (Cloud)**: Fast, low-latency **cloud-based** inference (e.g., `llama-3.1-8b-instant`).
  - **Gemini (Google)**: High-performance **cloud-based** models (e.g., `gemini-1.5-pro`).
  - **Environment-based selection**: Set `LLM_PROVIDER` in `.env` to switch between providers.
- **Result**:
  - **No vendor lock-in** – users can **choose their preferred LLM**.
  - **Seamless switching** between local and cloud models.

---

### 7. Graceful Error Handling & Fallbacks
- **Problem**: LLM failures or API errors can **crash the pipeline**.
- **Solution**:
  - **Fallback Analysts**: If LLM fails to generate analysts, **placeholder analysts** are created.
  - **Structured Error Responses**: API returns **clear error messages** (e.g., `{"type": "error", "payload": "..."}`).
  - **Ollama Model Validation**: Checks if the **Ollama model is installed** before runtime.
- **Result**:
  - **No silent failures** – users get **actionable error messages**.
  - **Resilient pipeline** that **degrades gracefully** under failures.

---

### 8. Human-in-the-Loop Feedback
- **Problem**: AI-generated analysts may **not align** with user expectations.
- **Solution**:
  - **Interrupt Points**: The `Analyst Generation Graph` **pauses** at `human_feedback` for user review.
  - **Regeneration**: Users can **provide feedback** to refine analysts before proceeding.
- **Result**:
  - **User control** over the research process.
  - **Higher-quality outputs** by incorporating **human judgment**.

## 🛠 Quick Start
<details>
<summary><b>View Installation & Execution Commands</b></summary>

### Prerequisites
| Requirement | Version | Purpose |
|-------------|---------|---------|
| **Python** | 3.12+ | Runtime environment |
| **Ollama** (optional) | Latest | Local LLM inference |
| **Node.js** (frontend) | 18+ | Frontend development |
| **Tavily API Key** | - | Web search for RAG |
| **Groq/Gemini API Key** (optional) | - | Cloud LLM inference |

---

### Backend Setup

#### 1. Clone the Repository
```bash
git clone https://github.com/Prasad7Paigude/research-assistant.git
cd research-assistant
```

#### 2. Create a Virtual Environment
```bash
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
.venv\Scripts\activate      # Windows
```

#### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

#### 4. Configure Environment Variables
```bash
cp .env.example .env
```
Edit `.env` with your **API keys** (e.g., `TAVILY_API_KEY`, `GROQ_API_KEY`, `GEMINI_API_KEY`).
Example:
```ini
LLM_PROVIDER=ollama  # or "groq" / "gemini"
TAVILY_API_KEY=your_tavily_api_key_here
GROQ_API_KEY=your_groq_api_key_here  # if using Groq
GEMINI_API_KEY=your_gemini_api_key_here  # if using Gemini
```

#### 5. Start the API Server
```bash
python -m uvicorn api.server:app --host 0.0.0.0 --port 8000 --reload
```
Or use the provided script:
```bash
./start_api.sh
```
**API will be available at:** `http://localhost:8000`

---

### Frontend Setup (Optional)
If you want to use the **React frontend**:
```bash
cd frontend
npm install
npm run dev
```
**Frontend will be available at:** `http://localhost:5173`

---

### API Endpoints
| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/health` | Health check |
| `POST` | `/api/research/init` | Initialize research and generate analysts |
| `POST` | `/api/research/feedback` | Submit feedback for analyst regeneration |
| `POST` | `/api/research/approve` | Approve analysts and start research |
| `GET` | `/api/research/stream/{thread_id}` | Stream real-time research progress (SSE) |
| `GET` | `/api/research/result/{thread_id}` | Retrieve the final report |

---

### Example Workflow

#### 1. Initialize Research
```bash
curl -X POST http://localhost:8000/api/research/init \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "Impact of AI on Healthcare",
    "max_analysts": 3,
    "max_turns": 2
  }'
```
**Response**:
```json
{
  "thread_id": "abc123",
  "status": "analysts_pending",
  "analysts": [
    {
      "name": "Dr. Alice Chen",
      "role": "Medical Ethicist",
      "affiliation": "Harvard Medical School",
      "description": "Focuses on AI ethics in healthcare..."
    },
    {
      "name": "Dr. Bob Smith",
      "role": "AI Researcher",
      "affiliation": "Stanford AI Lab",
      "description": "Specializes in LLMs for medical diagnosis..."
    }
  ]
}
```

#### 2. Approve Analysts & Start Research
```bash
curl -X POST http://localhost:8000/api/research/approve \
  -H "Content-Type: application/json" \
  -d '{"thread_id": "abc123"}'
```
**Response**: Research begins, and **SSE stream** becomes available.

#### 3. Stream Progress (SSE)
```bash
curl http://localhost:8000/api/research/stream/abc123
```
**Stream Output** (example):
```text
data: {"type": "analyst", "payload": "Dr. Alice Chen started interview..."}
data: {"type": "section", "payload": "# Insights on AI Ethics..."}
data: {"type": "report", "payload": "# Final Report: Impact of AI on Healthcare..."}
data: {"type": "done", "payload": ""}
```

#### 4. Retrieve Final Report
```bash
curl http://localhost:8000/api/research/result/abc123
```
**Response**:
```json
{
  "thread_id": "abc123",
  "status": "complete",
  "report": "# Impact of AI on Healthcare\n\n## Introduction\n...\n\n## Insights\n...\n\n## Conclusion\n...\n\n## Sources\n1. [Wikipedia - AI in Healthcare](...)\n2. [Tavily - Latest AI Medical Breakthroughs](...)",
  "sections": ["...", "..."]
}
```

</details>

---

## 🛠 Tech Stack

| Layer | Component | Version | Purpose |
|-------|-----------|---------|---------|
| **Runtime** | Python | 3.12+ | Execution environment |
| **Graph Orchestration** | LangGraph | 1.2.9 | Multi-agent workflow orchestration |
| **Graph Checkpointing** | LangGraph Checkpoint | 4.1.1 | State persistence for LangGraph |
| **LLM Framework** | LangChain | 1.3.11 | LLM integration & agent orchestration |
| **LangChain Core** | LangChain Core | 1.5.1 | Core abstractions for LangChain |
| **LangChain Community** | LangChain Community | 0.4.2 | Community tools (Wikipedia, Tavily) |
| **LLM Providers** | LangChain Ollama | 0.2.2 | Ollama LLM integration |
| **LLM Providers** | LangChain Groq | 0.2.0 | Groq LLM integration |
| **LLM Providers** | LangChain Google GenAI | 4.3.1 | Gemini LLM integration |
| **Web Search** | Tavily Python | 0.7.26 | Real-time web search for RAG |
| **Web Search** | Tavily LangChain | 0.2.18 | Tavily integration with LangChain |
| **Knowledge Base** | Wikipedia | 1.4.0 | Wikipedia article retrieval |
| **API Framework** | FastAPI | 0.140.1 | RESTful API backend |
| **ASGI Server** | Uvicorn | 0.50.2 | FastAPI server |
| **Data Validation** | Pydantic | 2.13.4 | Request/response model validation |
| **Environment Management** | Python Dotenv | 1.2.2 | `.env` file loading |
| **Type Hints** | Typing Extensions | 4.16.0 | Advanced type annotations |
| **HTTP Client** | Requests | 2.32.5+ | HTTP requests for external APIs |

---

## 🔒 Security & Reliability

### Error Handling
- **Structured Errors**: API returns **clear, actionable error messages** (e.g., `{"type": "error", "payload": "..."}`).
- **Fallback Mechanisms**:
  - If LLM fails to generate analysts, **placeholder analysts** are created.
  - If Ollama model is missing, **explicit error** with installation instructions.
- **Graceful Degradation**: Pipeline **continues or fails gracefully** without crashing.

### API Security
- **CORS**: Configured to **allow all origins in development** (restrict in production).
- **Input Validation**: **Pydantic models** ensure **type-safe requests**.
- **Environment Variables**: **No hardcoded secrets** – all keys loaded from `.env`.

### Observability
- **Structured Logging**: All major events are **logged with context** (e.g., `logger.info`, `logger.error`).
- **Health Check**: `/api/health` endpoint confirms **service availability**.

### Performance
- **Parallel Execution**: Interviews run **concurrently** for efficiency.
- **Caching**: **No redundant LLM calls** – state is **reused** where possible.
- **Streaming**: **Real-time updates** via **SSE** for a responsive UI.
