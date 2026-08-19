# 🩺 MediCare AI: Rural Healthcare Infrastructure

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-3670a0?style=flat&logo=python&logoColor=ffdd54)](https://www.python.org/downloads/)
[![Flask 2.3.3](https://img.shields.io/badge/Flask-2.3.3-000000?style=flat&logo=flask&logoColor=white)](https://flask.palletsprojects.com/)
[![MongoDB Atlas](https://img.shields.io/badge/MongoDB-Atlas-13aa52?style=flat&logo=mongodb&logoColor=white)](https://www.mongodb.com/cloud/atlas)
[![aiXplain Llama 3.3](https://img.shields.io/badge/aiXplain-Llama_3.3-FF6B6B?style=flat)](https://aixplain.com/)
[![PyMongo 4.6.1](https://img.shields.io/badge/PyMongo-4.6.1-336B3D?style=flat)](https://pymongo.readthedocs.io/)
[![MIT License](https://img.shields.io/badge/License-MIT-green.svg?style=flat)](LICENSE)

> **Live Production:** [https://aixplain-medicare.vercel.app/](https://aixplain-medicare.vercel.app/)
>
> **Status:** Production-ready. Zero-trust security. AI-powered diagnostic triage + automated hospital logistics for rural healthcare at scale.

---

## Core Mission

**The Problem:** Rural India faces a 1:10,000 doctor-to-patient ratio, fragmented hospital logistics (48-72h booking latencies), and brittle monolithic backends that collapse under single-point-of-failure.

**The Solution:** A zero-trust, modular platform delivering:

- **AI diagnostic triage** — aiXplain Llama 3.3 70B with stateful sessions per user, enabling expert-level symptom evaluation without a human doctor in the loop
- **Unified hospital logistics** — Centralized Flask blueprints for booking appointments, reserving beds, and ordering medicines against MongoDB Atlas with sub-second latency
- **Enterprise resilience** — Transactional email with automatic SMTP fallback, MongoDB connection validation with 503 degradation, and pre-flight config validation ensuring zero-crash startup
- **Zero-trust security** — All secrets via environment variable injection (MongoDB URIs, aiXplain keys, SMTP creds). Bcrypt password hashing. Compliant with twelve-factor app principles

**Impact:** Sub-minute AI consultations for underserved patients. Real-time inventory visibility across districts for hospital administrators. **Bridges a 60-year healthcare infrastructure gap through precision engineering.**

---

## Achievements

- **5th Rank — IEMhacks 3.0** (National Level Hackathon)
- **3rd Rank — Pariyojana Pratiyogita**

Post-validation, the entire codebase was **production-hardened**: the monolithic prototype was decomposed into an 8-module, zero-trust architecture with strict separation of concerns, comprehensive error handling, and resilient fallback matrices. A validated concept, now an **operationally bulletproof platform.**

---

## Architecture & Data Flow

```
┌─────────────────────────────────────────────────────────┐
│             MediCare Frontend (React/Vue)               │
└──────────────────────────┬──────────────────────────────┘
                           │ HTTPS/REST
           ┌───────────────▼───────────────┐
           │    Flask Factory Application  │
           │                               │
           │  ┌─────────────────────────┐  │
           │  │ Authentication Layer    │  │
           │  └────────────┬────────────┘  │
           │               │               │
           │  ┌────────────▼────────────┐  │
           │  │ AI Doctor Endpoint      │  │
           │  └────────────┬────────────┘  │
           │               │               │
           │  ┌────────────▼────────────┐  │
           │  │ Hospital Bookings       │  │
           │  └────────────┬────────────┘  │
           │               │               │
           │  ┌────────────▼────────────┐  │
           │  │ Route Handlers          │  │
           │  └────────────┬────────────┘  │
           └───────────────┬───────────────┘
                           │
       ┌───────────────────┼───────────────────┐
       │                   │                   │
┌──────▼──────┐     ┌──────▼──────┐     ┌──────▼──────┐
│   MongoDB   │     │  aiXplain   │     │ SMTP Email  │
│ (Atlas DB)  │     │ (Llama 70B) │     │  Service    │
│ Persistence │     │ Diagnostics │     │ Degradation │
└─────────────┘     └─────────────┘     └─────────────┘
```

### Module Topology

```
medicare-ai/
├── config/                          # Configuration & Environment Layer
│   ├── __init__.py
│   └── settings.py                  # Twelve-factor config: os.getenv() fallback matrix
│                                     # (MongoDB, aiXplain keys, SMTP credentials, Flask params)
│
├── src/                             # Core Business Logic & ML Integration
│   ├── __init__.py
│   ├── app.py                       # Flask Application Factory
│   │                                 # (create_app(), blueprint registration, service init)
│   ├── ai_doctor.py                 # aiXplain Agent Wrapper
│   │                                 # (session management, message dispatch, fallback matrix)
│   ├── auth.py                      # Authentication Blueprint
│   │                                 # (signup, login, bcrypt hashing, email integration)
│   ├── bookings.py                  # Hospital Logistics Blueprint
│   │                                 # (appointments, bed reservations, medicine orders)
│   ├── database.py                  # MongoDB Connection Manager
│   │                                 # (singleton pattern, connection validation, ping checks)
│   ├── email_service.py             # Transactional Email Pipeline
│   │                                 # (Flask-Mail wrapper, SMTP pre-flight verification,
│   │                                 #  graceful degradation on connection failure)
│   └── routes.py                    # Primary API Route Handlers
│                                     # (AI Doctor dispatch, health checks, utility endpoints)
│
├── utils/                           # Cross-cutting Utilities
│   ├── __init__.py
│   └── logging_setup.py             # Structured logging configuration
│                                     # (ISO 8601 timestamps, contextual field extraction)
│
├── frontend/                        # React/Vue Frontend Application
│   │                                 # (Patient portal, doctor dashboard, appointment UI)
│
├── tests/                           # Test Suite
│   │                                 # (Integration tests, unit tests, fixtures)
│
├── pyproject.toml                   # PEP 517 build metadata, setuptools config
├── requirements.txt                 # Pinned dependency versions (reproducible installs)
├── .env.example                     # Environment template (documentation)
├── server.py                        # Entry point (backward-compatible wrapper)
├── LICENSE                          # MIT
└── README.md                        # This document
```

---

## Engineering Triumphs

### 1. Stateful Session Management for aiXplain AI Doctor

- **Problem:** The raw aiXplain agent API resets conversational context on every call. Multi-turn symptom history is lost, forcing patients to re-explain their condition.
- **Solution:** A stateful wrapper (`AIDoctorAgent`) that maps user IDs to active aiXplain session IDs (O(1) lookup), automatically creating new sessions on first contact and resuming existing ones on follow-ups. Response extraction uses a structured fallback chain; if the agent is unavailable, a polished error message replaces the stack trace.
- **Integrated ModelTools:** Google TTS for speech-based consultation (low-literacy populations) + Microsoft NER for medical entity extraction.
- **Result:** Multi-turn continuity, sub-second session restoration, and accessible voice output — all without human intervention.

### 2. Graceful Degradation & Micro-Backend Resilience

- **Problem:** Monolithic coupling means an SMTP crash takes down the entire platform. A lost MongoDB connection throws unhandled exceptions.
- **Solution:** Strictly decoupled Flask factory with independent fallback per service:
- `connect_to_mongodb()` returns `None` on failure → routes issue 503 instead of crashing
- `init_mail()` with pre-flight SMTP verification → logs a warning on failure, application continues
- `AIDoctorAgent()` returns `None` if aiXplain keys are missing → routes handle `None` gracefully
All initialization failures are logged with full context. No cascading failures. No silent crashes.
- **Result:** Zero cascading failures. Transparent degradation via 503 responses. Full observability at startup.

### 3. Zero-Trust Security & Twelve-Factor Configuration

- **Problem:** Original hackathon code had MongoDB URIs, Gmail passwords, and aiXplain keys hardcoded. Credentials leaked into version control.
- **Solution:** A comprehensive security refactor moved all secrets to `config/settings.py` with strict `os.getenv()` injection. Every parameter has a documented fallback (empty string for required, sensible default for optional). Passwords are bcrypt-hashed with a 12-round work factor. The `.env` file is gitignored; only `.env.example` (with zero secrets) is tracked.
- **Result:** Zero hardcoded credentials. Same binary deploys to dev/staging/production with different env vars. HIPAA/GDPR-ready without architectural changes.

---

## Enterprise Quick Start

<details>
<summary><b>View Installation & Execution Commands</b></summary>

### Prerequisites
- **Python 3.10+** (tested on 3.10, 3.11)
- **MongoDB Atlas account** (free tier available)
- **aiXplain API credentials**
- **~300 MB disk space**

### Installation & First Run
```bash
git clone https://github.com/Prasad7Paigude/medicare-ai.git
cd medicare-ai
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # edit with your credentials
python server.py
```

**On first execution:**
- Config validation
- MongoDB ping
- SMTP pre-flight
- aiXplain agent init
- Flask starts on `localhost:5000`

### Example API Endpoints

<details>
<summary><code>POST /signup</code> — Register a patient account</summary>

```bash
curl -X POST http://localhost:5000/signup \
  -H "Content-Type: application/json" \
  -d '{
    "fullName": "Rajesh Kumar",
    "email": "rajesh@example.com",
    "phone": "9876543210",
    "password": "SecurePassword123!"
  }'
```

```json
{
  "success": true,
  "message": "Account created successfully!",
  "user": { "id": "507f1f77bcf86cd799439011", "fullName": "Rajesh Kumar", "email": "rajesh@example.com" }
}
```
</details>

<details>
<summary><code>POST /ai-doctor</code> — AI diagnostic consultation</summary>

```bash
curl -X POST http://localhost:5000/ai-doctor \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "507f1f77bcf86cd799439011",
    "message": "I have a high fever and severe cough for 3 days"
  }'
```

```json
{
  "success": true,
  "message": "Based on your symptoms (high fever and severe cough for 3 days), this suggests either viral respiratory infection or early pneumonia. I recommend immediate consultation with a pulmonologist or general physician."
}
```
</details>

<details>
<summary><code>POST /book-bed</code> — Hospital bed reservation</summary>

```bash
curl -X POST http://localhost:5000/book-bed \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "507f1f77bcf86cd799439011",
    "hospital": "Aravind Eye Hospital",
    "admission_date": "2026-06-25",
    "ward_type": "General Ward"
  }'
```

```json
{
  "success": true,
  "message": "Bed booked successfully!",
  "booking_id": "bk_60a7e8c3d1f2a9b4c5d6e7f8"
}
```
</details>

<details>
<summary><code>POST /order-medicines</code> — Pharmacy order</summary>

```bash
curl -X POST http://localhost:5000/order-medicines \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "507f1f77bcf86cd799439011",
    "medicines": [
      {"name": "Paracetamol 500mg", "quantity": 20},
      {"name": "Amoxicillin 250mg", "quantity": 10}
    ]
  }'
```

```json
{
  "success": true,
  "message": "Order placed successfully!",
  "order_id": "od_70b8f9d4e2g3b0c5d6e7f8g9"
}
```
</details>

</details>

---

## Tech Stack

| Layer | Component | Version | Role |
|-------|-----------|---------|------|
| **Runtime** | Python | 3.10+ | Execution environment |
| **Framework** | Flask | 2.3.3 | REST API, application factory, blueprint orchestration |
| **Database** | MongoDB Atlas | Latest | Cloud-native NoSQL for users, bookings, inventory |
| **Driver** | PyMongo | 4.6.1 | Connection pooling, CRUD operations |
| **AI/LLM** | aiXplain SDK | 0.2.27 | Agent factory, ModelTool pipeline orchestration |
| **LLM** | Llama 3.3 | 70B | Medical diagnostic inference |
| **TTS** | Google TTS | ModelTool | Voice synthesis for accessibility |
| **NER** | Microsoft NER | ModelTool | Medical entity extraction |
| **Auth** | bcrypt | 4.0.1 | Salted password hashing (12-round work factor) |
| **Email** | Flask-Mail | 0.9.1 | SMTP transactional notifications |
| **Config** | python-dotenv | 1.0.0 | Env file loading (dev only) |
| **Build** | setuptools | ≥68.0 | Packaging, module discovery |

---

## Security & Reliability

- **Bcrypt hashing** — Salted, 12-round work factor; rainbow-table resistant
- **Env-only secrets** — Zero hardcoded credentials; all values injected at runtime
- **Graceful degradation** — Email/DB failures never crash the server; 503 signals client retry
- **Health checks** — Real-time service status at `/health`
- **Structured logging** — All events with ISO 8601 timestamps, severity, and context
- **HTTPS + TLS** — Encrypted in transit; MongoDB Atlas cert pinning

---

## License

MIT — see [LICENSE](LICENSE).
