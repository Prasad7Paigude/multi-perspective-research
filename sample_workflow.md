# Research Assistant - Sample Project Workflow

**Note:** This sample is extracted directly from code files (`main.py`, `Testing/test_ai_workflow.py`, `Testing/test_run.py`, `report.md`, `src/graph.py`, `src/nodes.py`, `src/state.py`) **without executing any code or running the project**.

## 1. User Inputs
- **Topic**: "Impact of Computer Vision on Automobile Industry in 2026" (or "Trending topics in Artificial Intelligence in 2026" / "Gen AI Native Startup")
- **Max Analysts**: 2 (or 3 in test_run.py)
- **Thread ID**: "test_analyst_001" (or "1")
- **Interview Max Turns**: 2
- **Starter Message**: `HumanMessage(f"So you said you were writing an article on {topic}?")`
- **Human Feedback** (at interruption): "Add an expert from Tesla's Autopilot team" (example from tests) or "Have one persona from Google R&D Team" (from report.md)

## 2. User Interactions / Feedback Loop
The workflow uses **human-in-the-loop** at the `human_feedback` node (interrupted via LangGraph `interrupt_before`).

**Step-by-step interaction:**
1. **Analyst Generation**: 
   - Graph starts at `create_analysts`.
   - Streams generated analysts (e.g., Dr. Rachel Kim, Dr. Liam Chen, Dr. Sofia Patel).
   - Pauses at `human_feedback`.
   - User reviews analysts and provides **feedback string** (e.g., "Add an expert from Tesla's Autopilot team").
   - Graph updates state and resumes regeneration.

2. **Approval**:
   - User presses **Enter without text** (empty feedback).
   - This sets `human_analyst_feedback: None` and continues.

3. **Interview Phase**:
   - For each approved analyst: Sends `HumanMessage` to start interview.
   - Multi-turn: `ask_question` → search_web / search_wikipedia → `generate_answer`.
   - Routes based on "Thank you..." or turn count.
   - Saves interview → writes section.

4. **Full Pipeline**:
   - Parallel `conduct_interview` for all analysts.
   - Consolidates into `write_report` + `write_introduction` + `write_conclusion`.
   - `finalize_report` assembles final Markdown.

**API Interaction Example** (from `api/server.py` + `test_backend_api.py`):
- POST `/api/research/feedback` with JSON: `{"thread_id": "...", "feedback": "Add an expert from Tesla's Autopilot team"}`
- Empty feedback for approval.

**Terminal Interaction** (from `Testing/test_ai_workflow.py`):
- `input("Your feedback (or press Enter to approve): ")`
- Empty string = approve.

## 3. Outputs
**Approved Analysts** (example from report.md + main.py):
```
1. Dr. Rachel Kim | Google R&D Team | AI Researcher | ...
2. Dr. Liam Chen | Microsoft Research Team | AI Engineer | ...
3. Dr. Sofia Patel | IBM Research Team | AI Scientist | ...
```

**Interview Section** (example preview):
```
## The Future of Natural Language Processing (NLP) in 2024
### Expert Insights and Trends
As an expert in Natural Language Processing (NLP), I have analyzed various sources...
```

**Final Report** (consolidated from map-reduce):
```
# Unconventional Intelligence: Exploring Surprising AI Applications

## Introduction
Artificial Intelligence is transforming industries...

## Insights
(Consolidated from analyst memos)

## Conclusion
As we conclude this report...

## Sources
[1] ...
```

**Execution Log** (from `report.md`):
- Graph Initialization: PASS
- Analyst Generation: PASS
- Human Feedback: PASS
- Interview: PASS
- Research Pipeline: PASS

**Key Code Patterns Used**:
- `human_analyst_feedback` in state (TypedDict).
- `update_state(..., as_node="human_feedback")`
- `HumanMessage` for interviews.
- Structured output for analysts (`Perspectives` model).
- Conditional edges for routing.

This matches the full flow in `test_run.py` and `test_ai_workflow.py`.