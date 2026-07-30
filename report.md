# Research Assistant - Test Report

## Test Information

| Field | Value |
|-------|-------|
| **Test Date** | 2026-07-29 11:52:18 |
| **Topic** | Trending Topics in AI |
| **Human Feedback** | Have one persona from Google R&D Team |
| **Max Analysts** | 3 |
| **Pipeline Analysts** | 1 |
| **LLM Provider** | Ollama |
| **LLM Model** | llama3.2:3b |
| **Overall Status** | FAILED |

---

## Step-by-Step Execution Log

### Step 1: Graph Initialization

| Field | Detail |
|-------|--------|
| **Status** | ✅ PASS |
| **Time** | 2026-07-29T11:52:10.416994 |
| **Details** | All 3 graphs built successfully |

---
### Step 2: Analyst Generation (Initial)

| Field | Detail |
|-------|--------|
| **Status** | ❌ FAIL |
| **Time** | 2026-07-29T11:52:14.175842 |
| **Details** | Failed during initial analyst generation |

**Error:** ```
[WinError 10061] No connection could be made because the target machine actively refused it
```

---
### Step 3: Human Feedback Input

| Field | Detail |
|-------|--------|
| **Status** | ✅ PASS |
| **Time** | 2026-07-29T11:52:14.178174 |
| **Details** | Feedback provided: 'Have one persona from Google R&D Team' |

---
### Step 4: Analyst Regeneration with Feedback

| Field | Detail |
|-------|--------|
| **Status** | ❌ FAIL |
| **Time** | 2026-07-29T11:52:16.209543 |
| **Details** | Failed during analyst regeneration |

**Error:** ```
[WinError 10061] No connection could be made because the target machine actively refused it
```

---
### Step 5: Single Interview Test

| Field | Detail |
|-------|--------|
| **Status** | ⏭️ SKIPPED |
| **Time** | 2026-07-29T11:52:16.209543 |
| **Details** | No analysts available |

---
### Step 6: Full Research Pipeline

| Field | Detail |
|-------|--------|
| **Status** | ❌ FAIL |
| **Time** | 2026-07-29T11:52:18.258121 |
| **Details** | Failed during full research pipeline |

**Error:** ```
[WinError 10061] No connection could be made because the target machine actively refused it
```

---

## Raw Execution Log (JSON)

```json
[
  {
    "step": "Graph Initialization",
    "status": "PASS",
    "timestamp": "2026-07-29T11:52:10.416994",
    "details": "All 3 graphs built successfully",
    "error": null
  },
  {
    "step": "Analyst Generation (Initial)",
    "status": "FAIL",
    "timestamp": "2026-07-29T11:52:14.175842",
    "details": "Failed during initial analyst generation",
    "error": "[WinError 10061] No connection could be made because the target machine actively refused it"
  },
  {
    "step": "Human Feedback Input",
    "status": "PASS",
    "timestamp": "2026-07-29T11:52:14.178174",
    "details": "Feedback provided: 'Have one persona from Google R&D Team'",
    "error": null
  },
  {
    "step": "Analyst Regeneration with Feedback",
    "status": "FAIL",
    "timestamp": "2026-07-29T11:52:16.209543",
    "details": "Failed during analyst regeneration",
    "error": "[WinError 10061] No connection could be made because the target machine actively refused it"
  },
  {
    "step": "Single Interview Test",
    "status": "SKIPPED",
    "timestamp": "2026-07-29T11:52:16.209543",
    "details": "No analysts available",
    "error": null
  },
  {
    "step": "Full Research Pipeline",
    "status": "FAIL",
    "timestamp": "2026-07-29T11:52:18.258121",
    "details": "Failed during full research pipeline",
    "error": "[WinError 10061] No connection could be made because the target machine actively refused it"
  }
]
```

---

## Input Summary

- **Topic:** `Trending Topics in AI`
- **Human Response at Interruption:** `Have one persona from Google R&D Team`
- **Max Analysts (Initial):** 3
- **Max Analysts (Research Pipeline):** 1
- **Interview Max Turns:** 2
- **LLM Provider:** Ollama
- **LLM Model:** llama3.2:3b
- **Web Search:** Tavily
- **Wikipedia:** Enabled

## Output Summary


**No final report was generated.**


## Key Observations

- **Graph Initialization:** ✅ Passed
- **Analyst Generation:** ❌ Failed
- **Human Feedback Integration:** ✅ Passed
- **Interview Execution:** ❌ Failed/Not Run
- **Research Pipeline:** ❌ Failed/Not Run

## Configuration Details

- **Python Version:** 3.12.6 (tags/v3.12.6:a4a2d2b, Sep  6 2024, 20:11:23) [MSC v.1940 64 bit (AMD64)]
- **LLM Backend:** Ollama (langchain-ollama)
- **Model:** llama3.2:3b
- **Web Search:** Tavily
- **Wikipedia:** Enabled
- **Checkpointer:** MemorySaver (in-memory)

---

*Report generated automatically by test_run.py*
