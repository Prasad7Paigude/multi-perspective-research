from langgraph.graph import START, END, StateGraph
from langgraph.checkpoint.memory import MemorySaver

from src.state import (
    GenerateAnalystsState, InterviewState, ResearchGraphState
)
from src.nodes import (
    create_analysts, human_feedback, should_continue,
    generate_question, search_web, search_wikipedia, generate_answer,
    save_interview, write_section, route_messages,
    initiate_all_interviews, write_report, write_introduction,
    write_conclusion, finalize_report
)


# ============================================================
# Analyst Generation Graph
# ============================================================

def build_analyst_graph():
    builder = StateGraph(GenerateAnalystsState)
    builder.add_node("create_analysts", create_analysts)
    builder.add_node("human_feedback", human_feedback)

    builder.add_edge(START, "create_analysts")
    builder.add_edge("create_analysts", "human_feedback")
    builder.add_conditional_edges(
        "human_feedback", should_continue, ["create_analysts", END]
    )

    memory = MemorySaver()
    graph = builder.compile(interrupt_before=['human_feedback'], checkpointer=memory)
    return graph


# ============================================================
# Interview Sub-Graph
# ============================================================

def build_interview_graph():
    interview_builder = StateGraph(InterviewState)
    interview_builder.add_node("ask_question", generate_question)
    interview_builder.add_node("search_web", search_web)
    interview_builder.add_node("search_wikipedia", search_wikipedia)
    interview_builder.add_node("answer_question", generate_answer)
    interview_builder.add_node("save_interview", save_interview)
    interview_builder.add_node("write_section", write_section)

    interview_builder.add_edge(START, "ask_question")
    interview_builder.add_edge("ask_question", "search_web")
    interview_builder.add_edge("ask_question", "search_wikipedia")
    interview_builder.add_edge("search_web", "answer_question")
    interview_builder.add_edge("search_wikipedia", "answer_question")
    interview_builder.add_conditional_edges(
        "answer_question", route_messages,
        ['ask_question', 'save_interview']
    )
    interview_builder.add_edge("save_interview", "write_section")
    interview_builder.add_edge("write_section", END)

    memory = MemorySaver()
    interview_graph = interview_builder.compile(checkpointer=memory).with_config(
        run_name="Conduct Interviews"
    )
    return interview_graph


# ============================================================
# Full Research Graph (Map-Reduce)
# ============================================================

def build_research_graph(interview_graph):
    builder = StateGraph(ResearchGraphState)
    builder.add_node("create_analysts", create_analysts)
    builder.add_node("human_feedback", human_feedback)
    builder.add_node("conduct_interview", interview_graph)
    builder.add_node("write_report", write_report)
    builder.add_node("write_introduction", write_introduction)
    builder.add_node("write_conclusion", write_conclusion)
    builder.add_node("finalize_report", finalize_report)

    builder.add_edge(START, "create_analysts")
    builder.add_edge("create_analysts", "human_feedback")
    builder.add_conditional_edges(
        "human_feedback", initiate_all_interviews,
        ["create_analysts", "conduct_interview"]
    )
    builder.add_edge("conduct_interview", "write_report")
    builder.add_edge("conduct_interview", "write_introduction")
    builder.add_edge("conduct_interview", "write_conclusion")
    builder.add_edge(
        ["write_conclusion", "write_report", "write_introduction"],
        "finalize_report"
    )
    builder.add_edge("finalize_report", END)

    memory = MemorySaver()
    graph = builder.compile(checkpointer=memory)
    return graph
