# ⚖️ NyaySetu AI: Intelligent Legal Infrastructure

![Next.js 16](https://img.shields.io/badge/Next.js-16.0-000?logo=next.js&logoColor=fff)
![Python 3.11+](https://img.shields.io/badge/Python-3.11%2B-3776AB?logo=python&logoColor=fff)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?logo=fastapi&logoColor=fff)
![LangChain](https://img.shields.io/badge/LangChain-0.3-1C3C3C?logo=langchain&logoColor=fff)
![License](https://img.shields.io/badge/License-MIT-yellow)
![ChromaDB](https://img.shields.io/badge/Vector_DB-ChromaDB-6C47FF)

> **Live Production:** [https://nyay-setu-prod.vercel.app](https://nyay-setu-prod.vercel.app)
>
> **Status:** Enterprise LegalTech monorepo. Multi-engine RAG. Cryptographic evidence logging. Automated jurisdiction-aware legal drafting.

---

## Core Mission

**The Problem:** The legal system is opaque, expensive, and slow. Everyday citizens and paralegals face three critical bottlenecks:

- **The Knowledge Barrier:** Navigating the dense Indian Penal Code (IPC) requires expensive legal counsel, leaving many without basic awareness of their rights or applicable laws.
- **Drafting Friction:** Generating jurisdiction-compliant legal documents (RTI applications, affidavits) requires meticulous formatting and state-specific logic, creating massive delays for paralegals.
- **Evidence Vulnerability:** Digital evidence and case records are frequently stored in centralized, mutable databases, making them highly susceptible to tampering and chain-of-custody disputes.

**The Solution:** NyaySetu is an enterprise-grade LegalTech platform engineered to democratize legal access and secure judicial data. It delivers:

- **AI-Powered Legal Triage:** A multi-engine RAG pipeline that predicts applicable IPC sections from natural language case descriptions, guarded by strict anti-hallucination validation.
- **Automated Drafting Engine:** A dynamic PDF generation microservice that applies state-specific RTI fee rules, BPL waivers, stamp duty requirements, and guardian declarations.
- **Cryptographic Audit Trails:** A custom SHA-256 blockchain network built from scratch — complete with PoW consensus and peer-to-peer node sync — ensuring evidence files are immutably logged and mathematically tamper-proof.
- **Intent-Routed Legal Chatbot:** A LangChain-powered conversational agent that classifies user intent (document explanation, procedural, advice-seeking) and retrieves relevant legal context via ChromaDB vector search.

**Impact:** Transforms the paralegal workflow from days to minutes, democratizes foundational legal knowledge for citizens, and introduces zero-trust cryptographic security to legal record-keeping.

## Achievement

- **Top 50 / 650+ Teams — VOIS Tech Innovation Marathon** (National Level Hackathon)

Post-validation, the entire codebase was **production-hardened**: It features a Next.js frontend orchestrating four strictly decoupled Python microservices, strict anti-hallucination LLM guardrails, and a custom cryptographic blockchain for tamper-proof persistence. A validated concept, now an **operationally bulletproof legal infrastructure.**

---

## Architecture & Data Flow

```
┌────────────────────────────────────────────────────────────────────┐
│                        NEXT.JS FRONTEND                            │
│               (Next.js 16 · React 19 · Tailwind v4)                │
│                                                                    │
│  /app/page.tsx ← /app/chatbot ← /app/ipcpredication                │
│                     /app/generatedraft · /app/blockchain           │
└──────────┬───────────────────────┬──────────────────┬──────────────┘
           │ REST API Routes       │ REST API Routes  │ REST API Routes
           ▼                       ▼                  ▼
┌────────────────────┐ ┌────────────────────┐ ┌────────────────────┐
│  /api/chat         │ │  /api/generate-*   │ │  /api/blockchain/* │
│  Proxy → FastAPI   │ │  Proxy → Flask     │ │  Proxy → Flask     │
│  :5000             │ │  :5002             │ │  :9000             │
└────────┬───────────┘ └────────┬───────────┘ └────────┬───────────┘
         │                      │                      │
         ▼                      ▼                      ▼
┌─────────────────┐ ┌─────────────────────┐ ┌─────────────────────┐
│ LEGAL CHATBOT   │ │ DOCUMENT ENGINE     │ │ BLOCKCHAIN NODE     │
│ (FastAPI)       │ │ (Flask · Port 5002) │ │ (Flask · Port 9000) │
│                 │ │                     │ │                     │
│  ┌───────────┐  │ │  ┌───────────────┐  │ │  ┌───────────────┐  │
│  │ LangChain │  │ │  │ Jurisdiction  │  │ │  │ PoW Miner     │  │
│  │ RAG       │  │ │  │ Manager       │  │ │  │ SHA-256       │  │
│  │ Pipeline  │  │ │  │ (state rules) │  │ │  │ Nonce: random │  │
│  └─────┬─────┘  │ │  └───────┬───────┘  │ │  └───────┬───────┘  │
│        │        │ │          │          │ │          │          │
│  ┌─────┴─────┐  │ │  ┌───────┴───────┐  │ │  ┌───────┴───────┐  │
│  │ ChromaDB  │  │ │  │ ReportLab     │  │ │  │ MongoDB       │  │
│  │ Vector DB │  │ │  │ PDF Generator │  │ │  │ Persistence   │  │
│  └───────────┘  │ │  └───────────────┘  │ │  └───────────────┘  │
└─────────────────┘ └─────────────────────┘ └─────────────────────┘

┌────────────────────────────────────────────────────────────────────┐
│                        IPC PREDICTION API                          │
│               (FastAPI · Port 8000)                                │
│                                                                    │
│  User Query → Similarity Gate (ChromaDB) → Gemini LLM              │
│  → Validation Guard → Structured IPC Section Output                │
└────────────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────────────┐
│                         DATA LAYER                                 │
│                                                                    │
│MongoDB ── Users · Sessions · Blockchain Blocks · Files · Lifecycles│
│  ChromaDB ── IPC Section Embeddings (chroma_ipc_v1)                │
│           ── Legal Document Embeddings (chroma_day1)               │
│  JSON Files ── jurisdiction_rules.json · rti_categories.json       │
│               ipc_cleaned_v4.json · normalized_ipc.json            │
└────────────────────────────────────────────────────────────────────┘
```

### Module Topology

```
NyaySetu-Prod/
├── src/                              # Next.js 16 Frontend
│   ├── app/
│   │   ├── api/                      # REST proxy routes to Python backends
│   │   │   ├── auth/                 # Better Auth handler + account deletion
│   │   │   ├── blockchain/           # Proxy: chain, upload, share, download, init-key
│   │   │   ├── chat/                 # Proxy: POST → FastAPI chatbot (:5000)
│   │   │   ├── generate-affidavit/   # Proxy: POST → Flask affidavit engine (:5002)
│   │   │   ├── generate-rti/         # Proxy: POST → Flask RTI engine (:5002)
│   │   │   └── newsletter/           # Subscribe/unsubscribe/status + Resend email
│   │   ├── blockchain/               # Blockchain file management UI
│   │   ├── chatbot/                  # Legal chatbot conversation UI
│   │   ├── generatedraft/            # Document drafting frontend
│   │   └── ipcpredication/           # IPC section prediction UI
│   ├── components/                   # Shared UI: navbar, footer, theme, shadcn/ui
│   └── lib/                          # Auth (BetterAuth), MongoDB client, utilities
├── supplementary-code/               # Python Backend Microservices
│   ├── chatbot/                      # FastAPI chatbot — LangChain RAG over ChromaDB
│   │   ├── main.py                   # FastAPI entry point (:5000)
│   │   └── scripts/                  # RAG pipeline, retriever, intent router, clarifier
│   ├── ipc_prediction/               # FastAPI IPC prediction — similarity gate + Gemini LLM
│   │   ├── api.py                    # FastAPI entry point (:8000)
│   │   ├── ipc_reasoning_engine.py   # ChromaDB retrieval → Gemini → validation guard
│   │   └── llm_validation_guard.py   # JSON schema checker, section whitelist, confidence clamp
│   ├── draft_generation/             # Flask document engine — PDFs with ReportLab
│   │   ├── api.py                    # Flask entry point (:5002)
│   │   ├── document_engine.py        # Jurisdiction-aware RTI + Affidavit PDF generator
│   │   ├── rti_generator.py          # RTI-specific PDF builder
│   │   └── orchestrator.py           # AI requirement analysis + Groq LLM fallback
│   └── blockchain/                   # Flask blockchain node — SHA-256 PoW + peer sync
│       ├── peer.py                   # Standalone mining peer node (:8800)
│       ├── app/                      # Flask app with file upload/share UI (:9000)
│       ├── Blockchain.py             # Chain, PoW (random/incremental), consensus
│       └── Block.py                  # Block struct with SHA-256 hashing
├── config/                           # Shared Python configuration
│   ├── settings.py                   # All API keys, model names, paths
│   └── .env.example                  # Environment variable template
├── data/                             # Legal corpora & jurisdiction rules
│   ├── ipc_cleaned_v4.json           # Cleaned IPC sections with titles
│   ├── jurisdiction_profiles.json    # State-wise RTI/affidavit rules
│   ├── jurisdiction_rules.json       # RTI fee & BPL waiver per state
│   └── rti_categories.json           # RTI category detection keywords
└── utils/                            # Shared Python utilities
    └── logging_setup.py              # Structured logging for all services
```

---

## Engineering Triumphs

### 1. Multi-Engine RAG Pipeline with Anti-Hallucination Guardrails

- **Problem:** LLMs are prone to hallucinating incorrect IPC sections or fabricating legal references, which is unacceptable in a legal advice context.
- **Solution:** A three-stage pipeline: (a) **Semantic Retrieval** via ChromaDB vector search over 500+ IPC sections to produce a tightly bounded candidate set. (b) **Zero-Temperature Gemini LLM** constrained by a strict instruction template that permits only sections from the candidate set and enforces JSON output. (c) **Validation Guard** (`llm_validation_guard.py`) that strips markdown fences, parses JSON, verifies section numbers against a whitelist, clamps confidence to [0, 1], rejects confidences below 0.30, and returns a controlled fallback on any violation.
- **Result:** Zero tolerance for hallucinated sections. Every prediction is verifiably grounded in the IPC corpus. Confidence scores are mathematically bounded and traceable.

### 2. Custom SHA-256 Blockchain with Proof-of-Work Consensus

- **Problem:** Digital legal documents and evidence files are stored in mutable databases, making them vulnerable to tampering and disputes over chain of custody.
- **Solution:** A complete blockchain implementation from scratch (`Block.py`, `Blockchain.py`) featuring: SHA-256 block hashing, configurable difficulty proof-of-work (with both random-nonce and incremental-nonce strategies), longest-chain peer-to-peer consensus via HTTP, block announcement broadcasts, MongoDB persistence for chain durability, and a full REST API for transaction submission, mining, and chain queries.
- **Result:** Files uploaded to the NyaySetu network are immutably timestamped and linked via cryptographic hashes. Any tampering breaks the chain and is immediately detectable. The system supports multi-peer validation out of the box.

### 3. Jurisdiction-Aware Legal Document PDF Engine

- **Problem:** Legal documents like RTI applications and affidavits have strict formatting requirements that vary by Indian state (fee amounts, BPL exemptions, stamp paper values, guardian age limits, notary requirements).
- **Solution:** A ReportLab-based PDF generator (`document_engine.py`) with a `JurisdictionManager` that loads and applies state-specific rules from `jurisdiction_profiles.json`. Features include: automatic RTI fee clause with BPL waiver detection, category-driven additional clauses, smart subject-line generation with multiple variants, minor/guardian detection with state-specific guardian age limits, configurable notary/verification blocks, and a `DocumentLifecycle` tracker for statutory deadlines (30-day RTI response, 30-day first appeal).
- **Result:** Legally compliant PDFs generated in seconds. Zero manual formatting. Statutory deadlines tracked and surfaced automatically. Documents are hash-verifiable from the moment of generation.

---

## Enterprise Quick Start

<details>
<summary><b>View Installation & Execution Commands</b></summary>

### Prerequisites

- Node.js 20+ and npm
- Python 3.11+
- MongoDB instance (local or Atlas)

### 1. Environment Setup

```bash
# Frontend environment
cp .env.example .env.local

# Backend environment
cp config/.env.example config/.env
```

Edit `.env.local` and `config/.env` with your API keys (OpenRouter, Gemini, Groq, MongoDB URI).

### 2. Frontend (Next.js 16)

```bash
# Install dependencies
npm install

# Generate Prisma client
npx prisma generate

# Start dev server (port 3000)
npm run dev
```

### 3. Backend Microservices

```bash
# Create and activate virtual environment
python -m venv .venv
.venv\Scripts\activate    # Windows
source .venv/bin/activate  # macOS/Linux

# Install Python dependencies
pip install -r requirements.txt
pip install -e .          # Install monorepo in development mode

# Start IPC Prediction API (port 8000)
uvicorn ipc_prediction.api:app --host 0.0.0.0 --port 8000 --reload

# Start Chatbot API (port 5000)
uvicorn chatbot.main:app --host 0.0.0.0 --port 5000 --reload

# Start Document Engine (port 5002)
python supplementary-code/draft_generation/api.py

# Start Blockchain File App (port 9000)
python supplementary-code/blockchain/run_app.py

# Start Blockchain Peer Node (port 8800)
python supplementary-code/blockchain/peer.py --port 8800
```

### 4. Populate Vector Databases

```bash
# Build IPC embeddings (ChromaDB)
python supplementary-code/ipc_prediction/generate_and_store_embeddings.py

# Build chatbot legal document vector DB
python supplementary-code/chatbot/scripts/build_vectordb.py
```

### 5. Verify

```bash
# Frontend
curl http://localhost:3000

# IPC Prediction
curl -X POST http://localhost:8000/ipc/predict \
  -H "Content-Type: application/json" \
  -d '{"text": "Someone stole my phone from my bag on the bus"}'

# Chatbot
curl -X POST http://localhost:5000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What is IPC 420?"}'

# Document Engine health
curl http://localhost:5002

# Blockchain chain
curl http://localhost:8800/chain
```

</details>

---

## Tech Stack

### Frontend

| Layer         | Component                              | Version   | Role                                          |
| ------------- | -------------------------------------- | --------- | --------------------------------------------- |
| Framework     | Next.js                                | 16.0.10   | React meta-framework with App Router          |
| UI Library    | React                                  | 19.2.0    | UI runtime                                    |
| Language      | TypeScript                             | ^5.0      | Type-safe development                         |
| Styling       | Tailwind CSS                           | ^4.1.17   | Utility-first CSS with PostCSS                |
| Animation     | Framer Motion                          | ^12.23.24 | Declarative animations                        |
| UI Primitives | Radix UI (Label, NavigationMenu, Slot) | ^2.1.x    | Accessible headless components                |
| Icons         | Lucide React                           | ^0.554.0  | Icon library                                  |
| Icons (alt)   | Tabler Icons React                     | ^3.36.0   | Supplementary icon set                        |
| Auth          | Better Auth                            | ^1.3.34   | Full-stack authentication (email OTP, social) |
| Auth (legacy) | NextAuth.js                            | ^4.24.13  | OAuth provider compatibility                  |
| Database ORM  | Prisma                                 | ^7.0.0    | Type-safe database client (local)             |
| Database      | MongoDB / Mongoose                     | ^8.20.0   | Document storage                              |
| HTTP          | node-fetch                             | ^2.7.0    | Server-side fetch fallback                    |
| Email         | Resend                                 | ^6.5.2    | Transactional email delivery                  |
| Particles     | tsParticles                            | ^3.9.1    | Animated particle backgrounds                 |
| 3D Globe      | Cobe                                   | ^0.6.5    | Real-time WebGL globe                         |
| Component Lib | shadcn/ui (new-york style)             | —         | Radix + Tailwind component system             |
| Theme         | next-themes                            | ^0.4.6    | Dark/light mode switching                     |
| Toast         | Sonner                                 | ^2.0.7    | Toast notifications                           |
| Class Utils   | class-variance-authority               | ^0.7.1    | Component variant management                  |
| Lint          | ESLint                                 | ^9.0      | Code quality                                  |

### Backend

| Layer                    | Component                                     | Version   | Role                               |
| ------------------------ | --------------------------------------------- | --------- | ---------------------------------- |
| Runtime                  | Python                                        | >= 3.11   | All backend microservices          |
| API (Chatbot + IPC)      | FastAPI                                       | 0.115.6   | Async REST API framework           |
| API (Draft + Blockchain) | Flask                                         | 3.1.0     | Synchronous REST API framework     |
| ASGI Server              | Uvicorn                                       | 0.34.0    | ASGI server for FastAPI            |
| WSGI Server              | Gunicorn                                      | >= 21.2.0 | Production WSGI server for Flask   |
| LLM Framework            | LangChain (core)                              | ~0.3.0    | RAG pipeline orchestration         |
| LLM Provider (Chat)      | OpenRouter (meta-llama/Llama-3.1-8B-Instruct) | —         | Chat completion                    |
| LLM Provider (IPC)       | Gemini 2.5 Flash (via REST)                   | —         | IPC reasoning with zero-temp       |
| LLM Provider (fallback)  | Groq (llama-3.3-70b-versatile)                | 0.18.0    | Document orchestration analysis    |
| Embeddings               | OpenAI text-embedding-3-small                 | —         | Vector embeddings                  |
| Vector Database          | ChromaDB                                      | ~0.5.0    | IPC section + legal doc retrieval  |
| PDF Generation           | ReportLab                                     | ~4.3      | Programmatic PDF document creation |
| Document Validation      | pydantic                                      | 2.10.4    | Schema validation for all APIs     |
| HTTP Client              | httpx                                         | 0.28.1    | Async HTTP for LLM calls           |
| Database                 | PyMongo                                       | 4.11      | MongoDB driver                     |
| QR Codes                 | qrcode                                        | >= 7.4.0  | QR generation on documents         |
| Image Processing         | Pillow                                        | >= 10.0.0 | Image support                      |
| Configuration            | pydantic-settings                             | 2.7.1     | Environment-based config           |

---

## Security & Reliability

- **Anti-Hallucination Validation:** The IPC prediction pipeline uses a three-tier guard: vector-similarity gate restricts the LLM's candidate pool, a zero-temperature Gemini call with strict JSON-only prompting eliminates free-form output, and a `validate_llm_response` function rejects any response containing unlisted section numbers, string-typed confidences, or confidence below 0.30.
- **Cryptographic Tamper-Proofing:** All files uploaded to the blockchain are SHA-256 hashed with proof-of-work (configurable difficulty). Each block links to the previous block's hash, creating an immutable chain. The longest-chain consensus mechanism across peer nodes prevents fork-based manipulation.
- **Intent-Based Chatbot Refusal:** The LangChain chatbot uses a classification-first architecture: it identifies `PROCEDURAL` and `ADVICE` intents and explicitly refuses to answer with hardcoded disclaimers, preventing the system from giving unauthorized legal advice or procedural guidance.
- **Microservice Isolation:** Each backend capability (chatbot, IPC prediction, document generation, blockchain node) runs as an independent service with its own API surface, port, and dependencies. Failures in one service do not cascade. The Next.js API routes act as a thin proxy layer, enabling independent scaling and deployment.

---

## License

MIT — see [LICENSE](LICENSE).
