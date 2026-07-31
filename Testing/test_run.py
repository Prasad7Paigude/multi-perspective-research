"""
Research Assistant - Test Script
==================================
Test with:
  Topic: "Trending Topics in AI"
  Human response at interruption: "Have one persona from Google R&D Team"

This script does NOT modify any existing code files. It reuses the
existing graph, nodes, and state from the project.
"""

import sys
import json
import os
from datetime import datetime
from langchain_core.messages import HumanMessage

# Add parent directory to path so we can import from src, config, utils
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.graph import (
    build_analyst_graph,
    build_interview_graph,
    build_research_graph
)
from config.settings import LLM_PROVIDER

# ============================================================
# Test Configuration
# ============================================================
TOPIC = "Trending Topics in AI"
HUMAN_FEEDBACK = "Have one persona from Google R&D Team"
MAX_ANALYSTS = 3
PIPELINE_ANALYSTS = 1
INTERVIEW_TURNS = 2

# ============================================================
# Test Execution
# ============================================================
log = []
test_passed = True

def log_step(step_name, status, details, error=None):
    log.append({
        "step": step_name,
        "status": status,
        "timestamp": datetime.now().isoformat(),
        "details": details,
        "error": error
    })

approved_analysts = None
interview_section = None
final_report = None

print("=" * 70)
print("RESEARCH ASSISTANT TEST EXECUTION")
print(f"Topic: {TOPIC}")
print(f"Human Feedback: {HUMAN_FEEDBACK}")
print("=" * 70)

# ----------------------------------------------------------
# Initialize Graphs
# ----------------------------------------------------------
print("\n[SETUP] Building graphs...")
try:
    analyst_graph = build_analyst_graph()
    interview_graph = build_interview_graph()
    research_graph = build_research_graph(interview_graph)
    log_step("Graph Initialization", "PASS", "All 3 graphs built successfully")
    print("[SETUP] Graphs built successfully.")
except Exception as e:
    log_step("Graph Initialization", "FAIL", "Failed to build graphs", str(e))
    test_passed = False
    print(f"[SETUP] FAILED: {e}")

if test_passed:
    # ----------------------------------------------------------
    # STEP 1: Generate Analysts (Human-in-the-Loop)
    # ----------------------------------------------------------
    print("\n" + "=" * 70)
    print("STEP 1: Generating Analysts (Human-in-the-Loop)")
    print("=" * 70)

    thread = {"configurable": {"thread_id": "test_001"}}
    initial_analysts = []

    try:
        for event in analyst_graph.stream(
            {"topic": TOPIC, "max_analysts": MAX_ANALYSTS},
            thread,
            stream_mode="values"
        ):
            analysts = event.get('analysts', '')
            if analysts:
                initial_analysts = analysts
                print(f"\nGenerated {len(analysts)} analysts:")
                for i, analyst in enumerate(analysts):
                    print(f"  [{i+1}] {analyst.name} ({analyst.affiliation}) - {analyst.role}")
                    print(f"       {analyst.description}")

        state = analyst_graph.get_state(thread)
        print(f"\nPaused at node: {state.next}")

        log_step("Analyst Generation (Initial)", "PASS",
                 f"Generated {len(initial_analysts)} analysts. Paused at: {state.next}")
    except Exception as e:
        log_step("Analyst Generation (Initial)", "FAIL",
                 "Failed during initial analyst generation", str(e))
        test_passed = False
        print(f"[ERROR] {e}")

    # ----------------------------------------------------------
    # STEP 2: Provide Human Feedback and Regenerate
    # ----------------------------------------------------------
    print("\n" + "=" * 70)
    print(f"STEP 2: Providing Human Feedback -> \"{HUMAN_FEEDBACK}\"")
    print("=" * 70)

    try:
        analyst_graph.update_state(
            thread,
            {"human_analyst_feedback": HUMAN_FEEDBACK},
            as_node="human_feedback"
        )
        log_step("Human Feedback Input", "PASS",
                 f"Feedback provided: '{HUMAN_FEEDBACK}'")
        print(f"[OK] Feedback applied.")

        for event in analyst_graph.stream(None, thread, stream_mode="values"):
            analysts = event.get('analysts', '')
            if analysts:
                print(f"\nRegenerated {len(analysts)} analysts with feedback:")
                for i, analyst in enumerate(analysts):
                    print(f"  [{i+1}] {analyst.name} ({analyst.affiliation}) - {analyst.role}")
                    print(f"       {analyst.description}")

        analyst_graph.update_state(
            thread,
            {"human_analyst_feedback": None},
            as_node="human_feedback"
        )

        for event in analyst_graph.stream(None, thread, stream_mode="updates"):
            node_name = list(event.keys())[0]
            print(f"  -> Node executed: {node_name}")

        final_state = analyst_graph.get_state(thread)
        approved_analysts = final_state.values.get('analysts')

        print(f"\nFINAL APPROVED ANALYSTS ({len(approved_analysts)}):")
        analyst_details = []
        for i, analyst in enumerate(approved_analysts):
            analyst_details.append({
                "name": analyst.name,
                "affiliation": analyst.affiliation,
                "role": analyst.role,
                "description": analyst.description
            })
            print(f"  [{i+1}] {analyst.name} ({analyst.affiliation}) - {analyst.role}")

        log_step("Analyst Regeneration with Feedback", "PASS",
                 f"Regenerated {len(approved_analysts)} analysts after feedback",
                 {"approved_analysts": analyst_details})

    except Exception as e:
        log_step("Analyst Regeneration with Feedback", "FAIL",
                 "Failed during analyst regeneration", str(e))
        test_passed = False
        print(f"[ERROR] {e}")

    if not approved_analysts and initial_analysts:
        approved_analysts = initial_analysts
        print("\n[WARN] Using initial analysts")

    # ----------------------------------------------------------
    # STEP 3: Single Interview Test
    # ----------------------------------------------------------
    print("\n" + "=" * 70)
    print("STEP 3: Running Single Interview Test")
    print("=" * 70)

    if approved_analysts:
        try:
            messages = [HumanMessage(f"So you said you were writing an article on {TOPIC}?")]
            interview_thread = {"configurable": {"thread_id": "test_interview_001"}}
            interview = interview_graph.invoke(
                {"analyst": approved_analysts[0], "messages": messages, "max_num_turns": INTERVIEW_TURNS},
                interview_thread
            )

            interview_section = interview['sections'][0]
            print(f"\nInterview section generated (length: {len(interview_section)} chars):")
            print("-" * 50)
            print(interview_section[:500] + ("..." if len(interview_section) > 500 else ""))
            print("-" * 50)

            log_step("Single Interview Test", "PASS",
                     f"Interview section generated ({len(interview_section)} chars)",
                     {"section_preview": interview_section[:300]})
        except Exception as e:
            log_step("Single Interview Test", "FAIL",
                     "Failed during single interview", str(e))
            test_passed = False
            print(f"[ERROR] {e}")
    else:
        log_step("Single Interview Test", "SKIPPED", "No analysts available")
        print("[SKIP] No analysts available.")

    # ----------------------------------------------------------
    # STEP 4: Full Research Pipeline (Map-Reduce)
    # ----------------------------------------------------------
    print("\n" + "=" * 70)
    print("STEP 4: Running Full Research Pipeline (Map-Reduce)")
    print("=" * 70)

    try:
        research_thread = {"configurable": {"thread_id": "test_research_001"}}

        for event in research_graph.stream(
            {"topic": TOPIC, "max_analysts": PIPELINE_ANALYSTS},
            research_thread,
            stream_mode="values"
        ):
            analysts = event.get('analysts', '')
            if analysts:
                print(f"\nResearch pipeline generated {len(analysts)} analysts:")
                for i, analyst in enumerate(analysts):
                    print(f"  [{i+1}] {analyst.name} ({analyst.affiliation}) - {analyst.role}")

        research_graph.update_state(
            research_thread,
            {"human_analyst_feedback": HUMAN_FEEDBACK},
            as_node="human_feedback"
        )
        print(f"\n[OK] Feedback applied to research pipeline.")

        for event in research_graph.stream(None, research_thread, stream_mode="values"):
            analysts = event.get('analysts', '')
            if analysts:
                print(f"\nRegenerated {len(analysts)} analysts:")
                for i, analyst in enumerate(analysts):
                    print(f"  [{i+1}] {analyst.name} ({analyst.affiliation}) - {analyst.role}")

        research_graph.update_state(
            research_thread,
            {"human_analyst_feedback": None},
            as_node="human_feedback"
        )

        print("\n[RUNNING] Conducting interviews and generating report...")
        for event in research_graph.stream(None, research_thread, stream_mode="updates"):
            node_name = list(event.keys())[0]
            print(f"  -> Node executed: {node_name}")

        final_state = research_graph.get_state(research_thread)
        final_report = final_state.values.get('final_report')

        if final_report:
            print(f"\nFINAL REPORT GENERATED (length: {len(final_report)} chars):")
            print("=" * 70)
            print(final_report[:1000] + ("..." if len(final_report) > 1000 else ""))
            print("=" * 70)
            log_step("Full Research Pipeline", "PASS",
                     f"Final report generated ({len(final_report)} chars)",
                     {"report_preview": final_report[:500]})
        else:
            log_step("Full Research Pipeline", "WARNING",
                     "Pipeline completed but no final report was generated")
            print("\n[WARN] No final report generated.")

    except Exception as e:
        log_step("Full Research Pipeline", "FAIL",
                 "Failed during full research pipeline", str(e))
        test_passed = False
        print(f"[ERROR] {e}")

# ============================================================
# Generate Report
# ============================================================
print("\n" + "=" * 70)
print("TEST EXECUTION COMPLETE")
print("=" * 70)

# Get LLM provider and model information
llm_provider = "Unknown"
llm_model = "Unknown"

if LLM_PROVIDER == "groq":
    llm_provider = "Groq"
    llm_model = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")
elif LLM_PROVIDER == "ollama":
    llm_provider = "Ollama"
    llm_model = "llama3.2:3b"
elif LLM_PROVIDER == "gemini":
    llm_provider = "Gemini"
    llm_model = "gemini-1.5-pro"
else:
    llm_provider = LLM_PROVIDER

report_content = f"""# Research Assistant - Test Report

## Test Information

| Field | Value |
|-------|-------|
| **Test Date** | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} |
| **Topic** | {TOPIC} |
| **Human Feedback** | {HUMAN_FEEDBACK} |
| **Max Analysts** | {MAX_ANALYSTS} |
| **Pipeline Analysts** | {PIPELINE_ANALYSTS} |
| **LLM Provider** | {llm_provider} |
| **LLM Model** | {llm_model} |
| **Overall Status** | {"PASSED" if test_passed else "FAILED"} |

---

## Step-by-Step Execution Log

"""

for i, entry in enumerate(log):
    status_icon = "✅" if entry["status"] == "PASS" else ("⚠️" if entry["status"] == "WARNING" else ("⏭️" if entry["status"] == "SKIPPED" else "❌"))
    report_content += f"""### Step {i+1}: {entry['step']}

| Field | Detail |
|-------|--------|
| **Status** | {status_icon} {entry['status']} |
| **Time** | {entry['timestamp']} |
| **Details** | {entry['details']} |
"""

    if entry.get("error"):
        error_str = str(entry["error"])
        if isinstance(entry["error"], dict):
            for key, val in entry["error"].items():
                if isinstance(val, list):
                    for item in val:
                        if isinstance(item, dict):
                            report_content += f"\n- **{item.get('name', 'N/A')}** | {item.get('affiliation', 'N/A')} | {item.get('role', 'N/A')}"
        else:
            report_content += f"\n**Error:** ```\n{error_str}\n```\n"

    report_content += "\n---\n"

report_content += f"""
## Raw Execution Log (JSON)

```json
{json.dumps(log, indent=2, default=str)}
```

---

## Input Summary

- **Topic:** `{TOPIC}`
- **Human Response at Interruption:** `{HUMAN_FEEDBACK}`
- **Max Analysts (Initial):** {MAX_ANALYSTS}
- **Max Analysts (Research Pipeline):** {PIPELINE_ANALYSTS}
- **Interview Max Turns:** {INTERVIEW_TURNS}
- **LLM Provider:** {llm_provider}
- **LLM Model:** {llm_model}
- **Web Search:** Tavily
- **Wikipedia:** Enabled

## Output Summary

"""

if approved_analysts:
    report_content += "\n### Approved Analysts\n\n"
    report_content += "| # | Name | Affiliation | Role | Description |\n"
    report_content += "|---|------|-------------|------|-------------|\n"
    for i, a in enumerate(approved_analysts):
        report_content += f"| {i+1} | {a.name} | {a.affiliation} | {a.role} | {a.description} |\n"

if interview_section:
    report_content += f"""
### Interview Section (Preview)

Character count: {len(interview_section)}

```markdown
{interview_section[:800]}...
```
"""

if final_report:
    report_content += f"""
### Final Report

Character count: {len(final_report)}

```markdown
{final_report}
```
"""
else:
    report_content += "\n**No final report was generated.**\n"

report_content += f"""

## Key Observations

- **Graph Initialization:** {"✅ Passed" if any(e["step"] == "Graph Initialization" and e["status"] == "PASS" for e in log) else "❌ Failed"}
- **Analyst Generation:** {"✅ Passed" if any("Analyst" in e["step"] and e["status"] == "PASS" for e in log) else "❌ Failed"}
- **Human Feedback Integration:** {"✅ Passed" if any("Feedback" in e["step"] and e["status"] == "PASS" for e in log) else "❌ Failed"}
- **Interview Execution:** {"✅ Passed" if any("Interview" in e["step"] and e["status"] == "PASS" for e in log) else "❌ Failed/Not Run"}
- **Research Pipeline:** {"✅ Passed" if any("Research Pipeline" in e["step"] and e["status"] == "PASS" for e in log) else "❌ Failed/Not Run"}

## Configuration Details

- **Python Version:** {sys.version}
- **LLM Backend:** {llm_provider} ({f"langchain-{LLM_PROVIDER}" if LLM_PROVIDER != "gemini" else "langchain-google-genai"})
- **Model:** {llm_model}
- **Web Search:** Tavily
- **Wikipedia:** Enabled
- **Checkpointer:** MemorySaver (in-memory)

---

*Report generated automatically by test_run.py*
"""

with open("report.md", "w", encoding="utf-8") as f:
    f.write(report_content)

print("\n✅ report.md has been generated.")
print(f"   Overall test status: {'PASSED' if test_passed else 'FAILED'}")