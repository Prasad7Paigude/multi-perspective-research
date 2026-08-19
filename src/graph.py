"""
Graph Definitions
==================

LangGraph state machines that orchestrate the research pipeline.

Three graphs are defined:

1. **Analyst Generation Graph** – creates diverse AI analyst personas with
   human-in-the-loop feedback for refinement.

2. **Interview Sub-Graph** – conducts a multi-turn interview between an
   analyst and an expert AI, gathering source documents and writing a
   report section.

3. **Research Graph** – the top-level map-reduce pipeline that runs
   interviews for every analyst in parallel, then synthesises the
   results into a final report.
"""

from __future__ import annotations

from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph

from src.nodes import (
    create_analysts,
    human_feedback,
    should_continue,
    generate_question,
    search_web,
    search_wikipedia,
    generate_answer,
    save_interview,
    write_section,
    route_messages,
    initiate_all_interviews,
    write_report,
    write_introduction,
    write_conclusion,
    finalize_report,
)
from src.state import (
    GenerateAnalystsState,
    InterviewState,
    ResearchGraphState,
)


# ===========================================================================
# Analyst Generation Graph
# ===========================================================================

def build_analyst_graph() -> "CompiledStateGraph[GenerateAnalystsState]":
    """Build and compile the analyst-generation sub-graph.

    The graph performs two steps:

    1. ``create_analysts`` – invokes the LLM to generate analyst personas.
    2. ``human_feedback`` – a *human-in-the-loop* checkpoint that pauses
       execution so the user can review and refine the analyst panel
       before the research proceeds.

    Returns:
        A compiled LangGraph with ``interrupt_before=['human_feedback']``
        so the pipeline pauses after analyst generation.
    """
    builder = StateGraph(GenerateAnalystsState)

    builder.add_node("create_analysts", create_analysts)
    builder.add_node("human_feedback", human_feedback)

    builder.add_edge(START, "create_analysts")
    builder.add_edge("create_analysts", "human_feedback")

    builder.add_conditional_edges(
        "human_feedback",
        should_continue,
        ["create_analysts", END],
    )

    memory = MemorySaver()
    graph = builder.compile(
        interrupt_before=["human_feedback"],
        checkpointer=memory,
    )
    return graph


# ===========================================================================
# Interview Sub-Graph
# ===========================================================================

def build_interview_graph() -> "CompiledStateGraph[InterviewState]":
    """Build and compile the interview sub-graph.

    The interview proceeds in a loop:

    1. ``ask_question`` – the analyst formulates a question.
    2. ``search_web`` and ``search_wikipedia`` – parallel retrieval of
       relevant documents.
    3. ``answer_question`` – an expert AI answers using the retrieved context.
    4. ``route_messages`` – decides whether to continue the interview or
       save the transcript.
    5. ``save_interview`` – stores the conversation transcript.
    6. ``write_section`` – the expert technical writer produces a report
       section from the interview transcript.

    Returns:
        A compiled, stateless LangGraph (the sub-graph is invoked via
        ``Send`` for parallel execution, so no checkpointer is needed).
    """
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
        "answer_question",
        route_messages,
        ["ask_question", "save_interview"],
    )
    interview_builder.add_edge("save_interview", "write_section")
    interview_builder.add_edge("write_section", END)

    # No checkpointer needed for sub-graph — Send() API handles parallelism
    interview_graph = interview_builder.compile().with_config(
        run_name="Conduct Interviews",
    )
    return interview_graph


# ===========================================================================
# Full Research Graph (Map-Reduce)
# ===========================================================================

def build_research_graph(
    interview_graph: "CompiledStateGraph[InterviewState]",
) -> "CompiledStateGraph[ResearchGraphState]":
    """Build and compile the full research pipeline graph.

    Uses a map-reduce pattern:

    1. ``human_feedback`` – user reviews/refines analysts (interrupt point).
    2. ``conduct_interview`` – parallel map: each analyst interviews an expert.
    3. ``write_report`` – consolidate interview memos into body content.
    4. ``write_introduction`` – generate the introduction.
    5. ``write_conclusion`` – generate the conclusion.
    6. ``finalize_report`` – assemble everything into the final report.

    Args:
        interview_graph: The compiled interview sub-graph (from
            ``build_interview_graph``).

    Returns:
        A compiled LangGraph with ``interrupt_before=['human_feedback']``
        for the human-in-the-loop checkpoint.
    """
    builder = StateGraph(ResearchGraphState)

    builder.add_node("human_feedback", human_feedback)
    builder.add_node("conduct_interview", interview_graph)
    builder.add_node("write_report", write_report)
    builder.add_node("write_introduction", write_introduction)
    builder.add_node("write_conclusion", write_conclusion)
    builder.add_node("finalize_report", finalize_report)

    builder.add_edge(START, "human_feedback")
    builder.add_conditional_edges(
        "human_feedback",
        initiate_all_interviews,
        ["conduct_interview"],
    )
    builder.add_edge("conduct_interview", "write_report")
    builder.add_edge("conduct_interview", "write_introduction")
    builder.add_edge("conduct_interview", "write_conclusion")
    builder.add_edge(
        ["write_conclusion", "write_report", "write_introduction"],
        "finalize_report",
    )
    builder.add_edge("finalize_report", END)

    memory = MemorySaver()
    graph = builder.compile(
        checkpointer=memory,
        interrupt_before=["human_feedback"],
    )
    return graph
