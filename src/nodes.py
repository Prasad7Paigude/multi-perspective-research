from langchain_core.messages import AIMessage, HumanMessage, SystemMessage, get_buffer_string
from langgraph.graph import END
from langgraph.types import Send
import json

from config.settings import llm
from src.state import (
    Analyst, Perspectives, GenerateAnalystsState,
    InterviewState, ResearchGraphState, SearchQuery
)
from src.prompts import (
    analyst_instructions, question_instructions, search_instructions,
    answer_instructions, section_writer_instructions,
    report_writer_instructions, intro_conclusion_instructions
)
from utils.tools import tavily_search, WikipediaLoader


# ============================================================
# Analyst Nodes
# ============================================================

def create_analysts(state: GenerateAnalystsState):
    """Generate AI analyst personas for the given topic."""
    topic = state['topic']
    max_analysts = state['max_analysts']
    human_analyst_feedback = state.get('human_analyst_feedback', '')
    existing_analysts = state.get('analysts', [])

    # If analysts already exist and no new feedback, skip LLM call
    if existing_analysts and not human_analyst_feedback:
        # Ensure we return exactly max_analysts
        sliced_analysts = existing_analysts[:max_analysts]
        # If we have fewer than requested, create placeholder analysts
        while len(sliced_analysts) < max_analysts:
            sliced_analysts.append(Analyst(
                affiliation=f"Research Institute {len(sliced_analysts) + 1}",
                name=f"Dr. Analyst {len(sliced_analysts) + 1}",
                role="Research Analyst",
                description=f"Expert analyst focusing on {topic}"
            ))
        return {"analysts": sliced_analysts[:max_analysts]}

    structured_llm = llm.with_structured_output(Perspectives)
    system_message = analyst_instructions.format(
        topic=topic,
        human_analyst_feedback=human_analyst_feedback,
        max_analysts=max_analysts
    )
    try:
        analysts = structured_llm.invoke(
            [SystemMessage(content=system_message)] +
            [HumanMessage(content="Generate the set of analysts.")]
        )
        # Ensure we return exactly max_analysts analysts
        generated_analysts = analysts.analysts[:max_analysts]
        # If LLM generated fewer than requested, create placeholder analysts
        while len(generated_analysts) < max_analysts:
            generated_analysts.append(Analyst(
                affiliation=f"Research Institute {len(generated_analysts) + 1}",
                name=f"Dr. Analyst {len(generated_analysts) + 1}",
                role="Research Analyst",
                description=f"Expert analyst focusing on {topic}"
            ))
        return {"analysts": generated_analysts[:max_analysts]}
    except json.JSONDecodeError:
        # Local model failed to produce valid JSON — return empty list
        # Create placeholder analysts as fallback
        fallback_analysts = []
        for i in range(max_analysts):
            fallback_analysts.append(Analyst(
                affiliation=f"Research Institute {i + 1}",
                name=f"Dr. Analyst {i + 1}",
                role="Research Analyst",
                description=f"Expert analyst focusing on {topic}"
            ))
        return {"analysts": fallback_analysts}


def human_feedback(state: GenerateAnalystsState):
    pass


def should_continue(state: GenerateAnalystsState):
    human_analyst_feedback = state.get('human_analyst_feedback', None)
    if human_analyst_feedback:
        return "create_analysts"
    return END


# ============================================================
# Interview Nodes
# ============================================================

def generate_question(state: InterviewState):
    analyst = state["analyst"]
    messages = state["messages"]

    system_message = question_instructions.format(goals=analyst.persona)
    question = llm.invoke([SystemMessage(content=system_message)] + messages)

    return {"messages": [question]}


def _extract_search_query(state: InterviewState) -> str:
    """Try to extract a structured search query, fallback to raw message text."""
    try:
        structured_llm = llm.with_structured_output(SearchQuery)
        search_query = structured_llm.invoke([search_instructions] + state['messages'])
        if search_query and search_query.search_query:
            return search_query.search_query
    except (json.JSONDecodeError, Exception):
        pass
    
    # Fallback: use last message content
    last_msg = state['messages'][-1].content if state['messages'] else ""
    return last_msg[:200] if last_msg else "trending topics in AI"


def search_web(state: InterviewState):
    query = _extract_search_query(state)

    try:
        data = tavily_search.invoke({"query": query})
        if isinstance(data, dict):
            search_docs = data.get("results", [])
        elif isinstance(data, list):
            search_docs = data
        else:
            search_docs = []
    except Exception:
        search_docs = []

    formatted_search_docs = "\n\n---\n\n".join(
        [
            f'<Document href="{doc.get("url", "")}"/>\n{doc.get("content", str(doc))}\n</Document>'
            for doc in search_docs
        ]
    )

    return {"context": [formatted_search_docs]}


def search_wikipedia(state: InterviewState):
    query = _extract_search_query(state)

    try:
        search_docs = WikipediaLoader(
            query=query,
            load_max_docs=2
        ).load()
    except Exception:
        search_docs = []

    formatted_search_docs = "\n\n---\n\n".join(
        [
            f'<Document source="{doc.metadata["source"]}" page="{doc.metadata.get("page", "")}"/>\n{doc.page_content}\n</Document>'
            for doc in search_docs
        ]
    )

    return {"context": [formatted_search_docs]}


def generate_answer(state: InterviewState):
    analyst = state["analyst"]
    messages = state["messages"]
    context = state["context"]

    system_message = answer_instructions.format(goals=analyst.persona, context=context)
    answer = llm.invoke([SystemMessage(content=system_message)] + messages)

    answer.name = "expert"

    return {"messages": [answer]}


def save_interview(state: InterviewState):
    messages = state["messages"]
    interview = get_buffer_string(messages)
    return {"interview": interview}


def route_messages(state: InterviewState, name: str = "expert"):
    messages = state["messages"]
    max_num_turns = state.get('max_num_turns', 2)

    # Need at least 2 messages to check the last question
    if len(messages) < 2:
        return 'save_interview'

    num_responses = len(
        [m for m in messages if isinstance(m, AIMessage) and m.name == name]
    )

    if num_responses >= max_num_turns:
        return 'save_interview'

    last_question = messages[-2]

    if "Thank you so much for your help" in last_question.content:
        return 'save_interview'
    return "ask_question"


def write_section(state: InterviewState):
    interview = state["interview"]
    context = state["context"]
    analyst = state["analyst"]

    system_message = section_writer_instructions.format(focus=analyst.description)
    section = llm.invoke(
        [SystemMessage(content=system_message)] +
        [HumanMessage(content=f"Use this source to write your section: {context}")]
    )

    return {"sections": [section.content]}


# ============================================================
# Research Graph Nodes
# ============================================================

def initiate_all_interviews(state: ResearchGraphState):
    # Always proceed to conduct interviews with the approved analysts
    # The analysts are already in the state from the initial_state
    topic = state["topic"]
    max_num_turns = state.get("max_num_turns", 2)
    return [Send("conduct_interview", {
        "analyst": analyst,
        "max_num_turns": max_num_turns,
        "messages": [HumanMessage(
            content=f"So you said you were writing an article on {topic}?"
        )],
        "context": [],
        "interview": "",
        "sections": [],
    }) for analyst in state["analysts"]]


def write_report(state: ResearchGraphState):
    sections = state["sections"]
    topic = state["topic"]

    formatted_str_sections = "\n\n".join([f"{section}" for section in sections])

    system_message = report_writer_instructions.format(
        topic=topic, context=formatted_str_sections
    )
    report = llm.invoke(
        [SystemMessage(content=system_message)] +
        [HumanMessage(content=f"Write a report based upon these memos.")]
    )
    return {"content": report.content}


def write_introduction(state: ResearchGraphState):
    sections = state["sections"]
    topic = state["topic"]

    formatted_str_sections = "\n\n".join([f"{section}" for section in sections])

    instructions = intro_conclusion_instructions.format(
        topic=topic, formatted_str_sections=formatted_str_sections
    )
    intro = llm.invoke(
        [instructions] + [HumanMessage(content=f"Write the report introduction")]
    )
    return {"introduction": intro.content}


def write_conclusion(state: ResearchGraphState):
    sections = state["sections"]
    topic = state["topic"]

    formatted_str_sections = "\n\n".join([f"{section}" for section in sections])

    instructions = intro_conclusion_instructions.format(
        topic=topic, formatted_str_sections=formatted_str_sections
    )
    conclusion = llm.invoke(
        [instructions] + [HumanMessage(content=f"Write the report conclusion")]
    )
    return {"conclusion": conclusion.content}


def finalize_report(state: ResearchGraphState):
    content = state["content"]
    if content.startswith("## Insights"):
        content = content.strip("## Insights")
    if "## Sources" in content:
        try:
            content, sources = content.split("\n## Sources\n")
        except:
            sources = None
    else:
        sources = None

    final_report = (
        state["introduction"] + "\n\n---\n\n" +
        content + "\n\n---\n\n" +
        state["conclusion"]
    )
    if sources is not None:
        final_report += "\n\n## Sources\n" + sources
    return {"final_report": final_report}