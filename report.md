# Research Assistant --- Comprehensive Test Report

## Test Information

| Field | Value |
|---|---|
| **Test Date** | 2026-07-28 |
| **Project Root** | D:\\Desktop\\Projects\\Research Assistant |
| **Python Env** | lc-academy-env (3.12.6) |
| **Node.js** | Available |
| **Ollama** | NOT installed / NOT running |
| **LLM Config** | ChatOllama (model: llama3.2:3b) |
| **API Server** | FastAPI |
| **Frontend** | React + TypeScript + Vite + Tailwind v4 |

---

## 1. Architecture Overview

User Browser (React SPA) <-> HTTP/SSE <-> FastAPI Backend (api/server.py) <-> LangGraph Engine (src/graph.py) <-> LLM (Ollama) + Tavily + Wikipedia

Flow: Init Topic -> Generate Analysts -> Human Feedback(optional) -> Approve -> SSE Stream (Interviews -> Report)

---

## 2. Test Results Summary

| Component | Status | Details |
|---|---|---|
| Python module imports | PASS | All modules import cleanly |
| Graph initialization | PASS | All 3 graphs (analyst, interview, research) build OK |
| API server startup | PASS | Uvicorn serves successfully |
| GET /api/health | PASS | Returns ok |
| POST /api/research/init | FAIL | Server crashes --- see Section 3 |
| POST /api/research/feedback | UNTESTABLE | Depends on init working |
| POST /api/research/approve | UNTESTABLE | Depends on init working |
| GET /api/research/stream/{id} | UNTESTABLE | Depends on init working |
| GET /api/research/result/{id} | UNTESTABLE | Depends on init working |
| Frontend npm install | PASS | Dependencies install cleanly |
| Frontend npm run build | FAIL | 4 TypeScript errors |
| Frontend dist/ (pre-built) | EXISTS | Pre-built version available |

---

## 3. Critical Issues Found

### CRITICAL 1: LLM Provider Mismatch (Configuration Broken)

Files: config/settings.py (line 4, 10-13) vs .env (lines 1-3)

settings.py uses ChatOllama (requires langchain-ollama package), but .env contains GROQ_API_KEY (needs langchain-groq).

- langchain-ollama is MISSING from requirements.txt
- .env contains GROQ_API_KEY which is NEVER read by settings.py
- Neither langchain-groq nor langchain-ollama are in requirements.txt
- Ollama is not installed on this system, so all LLM calls fail

Impact: Every LLM-dependent endpoint crashes on first use.

---

### CRITICAL 2: Missing Dependencies in requirements.txt

Missing Package | Needed By | Why
fastapi | api/server.py | API framework
uvicorn | start_api.sh | ASGI server
langchain-ollama | config/settings.py | Current LLM provider
langchain-groq | .env | Alternative LLM provider
requests | test_run.py | HTTP calls

Users cloning and running pip install -r requirements.txt cannot start the API.

---

### CRITICAL 3: API Server Crashes on /api/research/init

File: api/server.py (lines 82-96)

When init is called, analyst_graph.stream() runs inside loop.run_in_executor().
Since Ollama is not running, the httpx connection to localhost:11434 fails with
connection refused, and the server process crashes with no recovery.

Root cause: No fallback or graceful error when the LLM backend is unreachable.

---

### CRITICAL 4: Frontend TypeScript Build Fails

4 TypeScript errors block fresh npm run build:

- AnalystCard.tsx(1,10): User imported but never used
- AnalystReview.tsx(2,55): Sparkles imported but never used
- ResearchSetup.tsx(2,32): ListTree imported but never used
- useResearch.ts(2,15): Analyst type imported but never used

A pre-built dist/ exists but any code change requires a successful build.

---

### HIGH 5: SSE Event Handling Gap (Frontend Ignores Server Events)

Server sends these event types. Frontend ignores report, introduction, conclusion:

- status -> handled (no-op)
- section -> handled (appended)
- report -> IGNORED by frontend
- introduction -> IGNORED by frontend
- conclusion -> IGNORED by frontend
- final_report -> handled (displayed)
- done -> handled (close)
- error -> handled (displayed)

Impact: ResearchProgress never shows introduction/conclusion status updates.

---

### HIGH 6: Research Progress Step Logic Bug

File: frontend/src/components/ResearchProgress.tsx (lines 16-25)

The 3-step indicator (Analysts=0, Interviews=1, Report=2) has incorrect logic:

- When sections arrive (interviews done) -> sets step=1 (should be 2)
- When complete -> sets step=2 (should be 3)
- Initial is 1 which shows interviews active before they start

---

### HIGH 7: Thread ID Collision Risk

File: api/server.py (lines 70, 184)

Session thread IDs are UUIDs (unique). SSE endpoint creates research_{thread_id}.
If a user re-initiates research for the same session, the research_{thread_id}
could potentially collide.

---

### MEDIUM 8: Extra Fields in Send() Payload

File: src/nodes.py (lines 202-211)

initiate_all_interviews passes context, interview, sections fields in the Send()
payload. These are already initialized as empty defaults in InterviewState.
Harmless but unnecessary.

---

### MEDIUM 9: test_run.py Hardcoded Wrong Provider

File: test_run.py (lines 291-292)

Report template hardcodes LLM Provider as Groq with model llama-3.1-8b-instant,
but settings.py uses ChatOllama with llama3.2:3b.

---

### MEDIUM 10: No Per-Interview Progress in SSE

File: api/server.py (lines 206-238)

For N analysts, the SSE sends N section events but the frontend has no way to
track which interview is currently running (e.g., Interview 2 of 4).

---

### LOW 11: Unused CSS in App.css (180 lines)

File: frontend/src/App.css

Contains .counter, .hero, .base, .framework, .vite, .ticks -- none used by any component.

---

### LOW 12: Source index.html Wrong Dev Title

File: frontend/index.html (line 7)

Title is frontend. The built dist/index.html correctly has Research Assistant.

---

## 4. API Endpoint Summary

Method | Endpoint | Expected Behavior | Result
GET | /api/health | Returns ok | PASS
POST | /api/research/init | Generate analysts, return thread + analysts | FAIL (crash)
POST | /api/research/feedback | Refine analysts | UNTESTABLE
POST | /api/research/approve | Mark interviewing | UNTESTABLE
GET | /api/research/stream/{id} | SSE interview progress | UNTESTABLE
GET | /api/research/result/{id} | Get final report | UNTESTABLE

---

## 5. Frontend Execution Flow Trace

User opens http://localhost:5173
  -> App.tsx renders ResearchSetup (status=idle)
  -> User fills topic, clicks Begin Research
  -> useResearch.initResearch()
      -> POST /api/research/init -> status=generating_analysts
      -> On success -> status=analysts_pending, shows AnalystReview
      -> User can provide feedback -> POST /api/research/feedback
      -> User clicks Proceed -> approveAnalysts()
          -> POST /api/research/approve -> status=interviewing
          -> EventSource connects to /api/research/stream/{thread_id}
          -> SSE events: status -> section -> ... -> final_report -> done
          -> status=complete, shows FinalReport

Blocking point: POST /api/research/init fails (LLM crashes server).

---

## 6. Configuration Matrix

Current (settings.py): ChatOllama, needs langchain-ollama, Ollama local, NOT working
Env says (.env): GROQ_API_KEY, needs langchain-groq, NOT configured in code
Previous (Gemini): ChatGoogleGenerativeAI, needs langchain-google-genai, installed

---

## 7. Quick-Fix Priority

P0: Align settings.py LLM provider with .env (5 min) - Unblocks all LLM calls
P0: Add missing deps to requirements.txt (2 min) - Fresh installs work
P0: Remove 4 unused frontend imports (2 min) - Frontend builds
P1: Handle LLM errors gracefully in API server (15 min) - No more crashes
P1: Fix ResearchProgress step indicator logic (5 min) - Correct progress
P1: Update test_run.py to read LLM config dynamically (10 min) - Accurate reports
P2: Handle report/intro/conclusion SSE events in frontend (10 min) - Better UX
P2: Remove unused App.css boilerplate (5 min) - Cleaner code
P3: Fix index.html dev title (1 min) - Polish

---

## 8. Conclusion

The project has a well-structured multi-agent architecture with clean separation
across config/, src/, utils/, api/, and frontend/. The LangGraph pipeline design
(analyst generation -> interviews -> report) is sound.

However, the project is currently non-functional end-to-end due to:

1. LLM provider mismatch between settings.py (ChatOllama) and .env (GROQ_API_KEY)
2. Missing runtime dependencies in requirements.txt
3. API server crashes on any LLM-dependent call
4. Frontend build failure from unused TypeScript imports

The critical path to fix:
1. Pick one LLM provider (Ollama, Groq, or Gemini)
2. Update config/settings.py and .env consistently
3. Add all required packages to requirements.txt
4. Clean up the 4 unused frontend imports

After these fixes, the expected user flow should work end-to-end.

---

*Report generated by comprehensive codebase analysis on 2026-07-26*
