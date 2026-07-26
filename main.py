from IPython.display import Image, display, Markdown
from langchain_core.messages import HumanMessage

from src.graph import (
    build_analyst_graph,
    build_interview_graph,
    build_research_graph
)


# ============================================================
# Analysts Generation (Human-in-the-Loop)
# ============================================================

analyst_graph = build_analyst_graph()
interview_graph = build_interview_graph()
research_graph = build_research_graph(interview_graph)

max_analysts = 3
topic = "Trending topics in Artificial Intelligence in 2026"
thread = {"configurable": {"thread_id": "1"}}

print("=" * 60)
print("STEP 1: Generating Analysts")
print("=" * 60)

for event in analyst_graph.stream(
    {"topic": topic, "max_analysts": max_analysts},
    thread,
    stream_mode="values"
):
    analysts = event.get('analysts', '')
    if analysts:
        for analyst in analysts:
            print(f"Name: {analyst.name}")
            print(f"Affiliation: {analyst.affiliation}")
            print(f"Role: {analyst.role}")
            print(f"Description: {analyst.description}")
            print("-" * 50)

state = analyst_graph.get_state(thread)
print(f"\nPaused at: {state.next}")

analyst_graph.update_state(
    thread,
    {
        "human_analyst_feedback":
            "Add in someone from a startup to add an entrepreneur perspective"
    },
    as_node="human_feedback"
)

print("\n" + "=" * 60)
print("STEP 2: Regenerating with Feedback")
print("=" * 60)

for event in analyst_graph.stream(None, thread, stream_mode="values"):
    analysts = event.get('analysts', '')
    if analysts:
        for analyst in analysts:
            print(f"Name: {analyst.name}")
            print(f"Affiliation: {analyst.affiliation}")
            print(f"Role: {analyst.role}")
            print(f"Description: {analyst.description}")
            print("-" * 50)

analyst_graph.update_state(
    thread,
    {"human_analyst_feedback": None},
    as_node="human_feedback"
)

for event in analyst_graph.stream(None, thread, stream_mode="updates"):
    print("--Node--")
    node_name = next(iter(event.keys()))
    print(node_name)

final_state = analyst_graph.get_state(thread)
analysts = final_state.values.get('analysts')

print("\n" + "=" * 60)
print("FINAL APPROVED ANALYSTS")
print("=" * 60)
for analyst in analysts:
    print(f"Name: {analyst.name}")
    print(f"Affiliation: {analyst.affiliation}")
    print(f"Role: {analyst.role}")
    print(f"Description: {analyst.description}")
    print("-" * 50)


# ============================================================
# Single Interview Test
# ============================================================

print("\n" + "=" * 60)
print("STEP 3: Running Single Interview Test")
print("=" * 60)

messages = [HumanMessage(f"So you said you were writing an article on {topic}?")]
interview_thread = {"configurable": {"thread_id": "1"}}
interview = interview_graph.invoke(
    {"analyst": analysts[0], "messages": messages, "max_num_turns": 2},
    interview_thread
)

print("\nInterview section generated:")
print(interview['sections'][0])


# ============================================================
# Full Research Pipeline (Map-Reduce)
# ============================================================

print("\n" + "=" * 60)
print("STEP 4: Running Full Research Pipeline")
print("=" * 60)

max_analysts = 2
topic = "Gen AI Native Startup"
research_thread = {"configurable": {"thread_id": "1"}}

for event in research_graph.stream(
    {"topic": topic, "max_analysts": max_analysts},
    research_thread,
    stream_mode="values"
):
    analysts = event.get('analysts', '')
    if analysts:
        for analyst in analysts:
            print(f"Name: {analyst.name}")
            print(f"Affiliation: {analyst.affiliation}")
            print(f"Role: {analyst.role}")
            print(f"Description: {analyst.description}")
            print("-" * 50)

research_graph.update_state(
    research_thread,
    {
        "human_analyst_feedback":
            "Add in the CEO of gen ai native startup"
    },
    as_node="human_feedback"
)

for event in research_graph.stream(None, research_thread, stream_mode="values"):
    analysts = event.get('analysts', '')
    if analysts:
        for analyst in analysts:
            print(f"Name: {analyst.name}")
            print(f"Affiliation: {analyst.affiliation}")
            print(f"Role: {analyst.role}")
            print(f"Description: {analyst.description}")
            print("-" * 50)

research_graph.update_state(
    research_thread,
    {"human_analyst_feedback": None},
    as_node="human_feedback"
)

for event in research_graph.stream(None, research_thread, stream_mode="updates"):
    print("--Node--")
    node_name = next(iter(event.keys()))
    print(node_name)

final_state = research_graph.get_state(research_thread)
report = final_state.values.get('final_report')

print("\n" + "=" * 60)
print("FINAL REPORT")
print("=" * 60)
print(report)
