from langchain_core.messages import AIMessage, HumanMessage, SystemMessage, get_buffer_string
from langgraph.graph import END
from langgraph.types import Send
import json
import re

from config.settings import llm
from src.state import (
    Analyst, Perspectives, GenerateAnalystsState,
    InterviewState, ResearchGraphState, SearchQuery
)
from src.prompts import (
    analyst_instructions, question_instructions, search_instructions,
    answer_instructions, section_writer_instructions, format_persona,
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

    system_message = question_instructions.format(persona=format_persona(analyst))
    question = llm.invoke([SystemMessage(content=system_message)] + messages)

    return {"messages": [question]}


def _extract_search_query(state: InterviewState) -> str:
    """Try to extract a structured search query, fallback to raw message text.

    The analyst's persona is injected into the search prompt so that the
    generated query reflects the analyst's specific perspective (Fix 5:
    improve search query diversity per analyst).
    """
    analyst = state.get("analyst")
    persona_str = format_persona(analyst) if analyst else "General analyst"
    query = None
    try:
        structured_llm = llm.with_structured_output(SearchQuery)
        search_prompt = search_instructions.content.format(persona=persona_str)
        search_query = structured_llm.invoke(
            [SystemMessage(content=search_prompt)] + state['messages']
        )
        if search_query and search_query.search_query:
            query = search_query.search_query
    except (json.JSONDecodeError, Exception):
        pass

    if query is None:
        # Fallback: use last message content
        last_msg = state['messages'][-1].content if state['messages'] else ""
        query = last_msg[:200] if last_msg else "trending topics in AI"

    # Log the query for observability / verification that different
    # analysts produce different searches
    if analyst:
        print(f"  [SEARCH] Analyst '{analyst.name}' query: '{query}'")
    else:
        print(f"  [SEARCH] Query: '{query}'")

    return query


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
            f'<Document href="{doc.get("url", "")}" title="{doc.get("title", "")}"/>\n{doc.get("content", "")}\n</Document>'
            for doc in search_docs
            if isinstance(doc, dict) and doc.get("url")  # filter invalid entries
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
            f'<Document href="{doc.metadata["source"]}" title="{doc.metadata.get("title", doc.metadata.get("page", ""))}"/>\n{doc.page_content}\n</Document>'
            for doc in search_docs
            if hasattr(doc, "metadata") and doc.metadata.get("source")
        ]
    )

    return {"context": [formatted_search_docs]}


def generate_answer(state: InterviewState):
    analyst = state["analyst"]
    messages = state["messages"]
    context = state["context"]

    system_message = answer_instructions.format(
        persona=format_persona(analyst), context=context
    )
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


# ============================================================
# Shared Helper Functions
# ============================================================

def normalize_headings(text: str) -> str:
    """Ensure all markdown headings have a blank line before and a newline after.

    Handles cases where the model runs headings directly into preceding/following text
    without proper line breaks. Preserves content inside code blocks.
    """
    if not text:
        return text

    # Split by code blocks (keeping the fences as separate parts)
    parts = re.split(r'(```)', text)

    result_parts = []
    in_code_block = False

    for part in parts:
        if part == '```':
            result_parts.append(part)
            in_code_block = not in_code_block
        else:
            if in_code_block:
                result_parts.append(part)
            else:
                # Step 1: Fix headings that run directly into preceding text
                part = re.sub(r'([^\n#\s])\s*(#{1,6}\s)', r'\1\n\n\2', part)
                # Step 2: Insert blank line before any heading preceded by a single newline
                part = re.sub(r'([^\n])\n(#{1,6}\s)', r'\1\n\n\2', part)
                # Step 3: Clean up excessive newlines
                part = re.sub(r'\n{3,}', '\n\n', part)
                result_parts.append(part)

    return ''.join(result_parts)


def extract_clean_sources(text: str) -> str:
    """Extract clean URL/title references from <Document> tags in source sections."""
    doc_pattern = re.compile(
        r'<Document\s[^>]*?href="([^"]*)"(?:[^>]*?title="([^"]*)")?[^>]*/>',
        re.DOTALL
    )
    doc_source_pattern = re.compile(
        r'<Document\s[^>]*?source="([^"]*)"[^>]*/>',
        re.DOTALL
    )

    def replace_doc(match):
        url = match.group(1)
        title = match.group(2) if match.group(2) else ""
        if title:
            return f'{url}, {title}'
        return url

    text = doc_pattern.sub(replace_doc, text)
    text = doc_source_pattern.sub(lambda m: m.group(1), text)
    # Remove any remaining raw JSON/object dumps
    text = re.sub(r'\{[^{}]*?\}', '', text)
    text = re.sub(r'<[^/>]+/>', '', text)

    return text


def write_section(state: InterviewState):
    interview = state["interview"]
    context = state["context"]
    analyst = state["analyst"]

    system_message = section_writer_instructions.format(
        persona=format_persona(analyst)
    )
    section = llm.invoke(
        [SystemMessage(content=system_message)] +
        [HumanMessage(content=f"Use this source to write your section: {context}\n\nInterview transcript:\n{interview}")]
    )

    # Clean up the section content: normalize headings and extract clean sources
    section_content = normalize_headings(section.content)
    section_content = extract_clean_sources(section_content)

    return {"sections": [section_content]}


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
        content = content[len("## Insights"):].lstrip()

    # Apply heading normalization to the body content
    content = normalize_headings(content)

    # Extract source entries ONLY from "## Sources" or "### Sources" sections
    source_section_pattern = re.compile(
        r'###?\s+Sources\s*\n(.*?)(?=\n## |\n\n## |\Z)', re.DOTALL
    )
    source_sections = source_section_pattern.findall(content)

    placeholder_phrases = [
        "source not provided", "source not found",
        "not provided in the given", "not found in", "no source",
        "document not explicitly cited", "source #", "<document",
        "document source", "not relevant",
    ]

    # Parse source entries from source sections only
    # A valid source entry looks like: [N] <url> or [N] Author, Title, etc.
    unique_sources = []
    seen_texts = set()

    source_entry_pattern = re.compile(r'\[(\d+)\]\s+(.+)')

    for sec in source_sections:
        # Clean up any raw <Document> tags or JSON dumps in the source section
        sec = extract_clean_sources(sec)
        
        for match in source_entry_pattern.findall(sec):
            text = match.strip()
            text_lower = text.lower()
            is_placeholder = any(p in text_lower for p in placeholder_phrases)
            # Skip entries that look like fragments (too short or end with ) or ,)
            if not text or is_placeholder:
                continue
            if text_lower in seen_texts:
                continue
            # Skip very short entries that are likely citation artifacts
            if len(text) < 10:
                continue
            # Skip entries that are just closing punctuation
            if re.match(r'^[\),\]\s]+', text):
                continue
            # Skip entries that are still raw JSON dumps or object reprs
            if text.startswith('{') or text.startswith('<'):
                continue
            seen_texts.add(text_lower)
            unique_sources.append(text)

    # Strip ALL source sections from the body content (both ## and ###)
    body_content = re.sub(
        r'###?\s+Sources\s*\n.*?(?=\n## |\n\n## |\Z)', '', content, flags=re.DOTALL
    )

    # Remove all inline citation markers [n] from the body text
    body_content = re.sub(r'\[\d+\]', '', body_content)
    # Handle citations in parentheses like ([1])
    body_content = re.sub(r'\s*\(\s*\)', '', body_content)
    body_content = re.sub(r'\s*\[\s*\]', '', body_content)
    body_content = re.sub(r'\s+,', ',', body_content)
    body_content = re.sub(r'\s{3,}', '  ', body_content)

    # Fix common capitalization artifacts
    for _typo in ["AGentic", "AGetic", "AGenti"]:
        body_content = re.sub(_typo, "Agentic", body_content)
    body_content = re.sub(r'agnetic-ai', 'agentic-ai', body_content)

    # Process introduction
    introduction = state["introduction"]
    introduction = re.sub(r"^(#+)\s*(#+\s*)?", "# ", introduction, count=1) if introduction.startswith("#") else introduction
    introduction = normalize_headings(introduction)
    for _typo in ["AGentic", "AGetic", "AGenti"]:
        introduction = re.sub(_typo, "Agentic", introduction)
        introduction = re.sub(r'agnetic-ai', 'agentic-ai', introduction)

    # Process conclusion with heading normalization
    conclusion = state["conclusion"]
    conclusion = normalize_headings(conclusion)
    for _typo in ["AGentic", "AGetic", "AGenti"]:
        conclusion = re.sub(_typo, "Agentic", conclusion)
        conclusion = re.sub(r'agnetic-ai', 'agentic-ai', conclusion)

    # Process individual sections - normalize headings and clean sources
    sections = state.get("sections", [])
    cleaned_sections = []
    for sec in sections:
        sec = normalize_headings(sec)
        # Clean any raw <Document> tags from source sections within individual sections
        # Extract the ### Sources section and clean it
        sec_source_pattern = re.compile(r'###\s+Sources\s*\n(.*?)(?=\n###|\n##|\Z)', re.DOTALL)
        sec_source_sections = sec_source_pattern.findall(sec)
        if sec_source_sections:
            # Clean each source section
            for sec_src in sec_source_sections:
                cleaned_src = extract_clean_sources(sec_src)
                sec = sec.replace(sec_src, cleaned_src)
        cleaned_sections.append(sec)

    # ---------------------------------------------------------------
    # Deterministic backstop BEFORE assembly: strip stray "Conclusion"
    # headings from the body content. If the model ignored the "###
    # Conclusion -> ### Takeaways" rename in section_writer_instructions,
    # it may emit "### Conclusion" (or any-level) inside an analyst section
    # that ends up in the body. We remove those stray heading lines
    # (preserving the text content) so only the intended "## Conclusion"
    # from the conclusion section remains in the final report.
    # ---------------------------------------------------------------
    body_content = re.sub(
        r'^[ \t]*#{1,6}\s+Conclusion[ \t]*\n',
        '',
        body_content,
        flags=re.IGNORECASE | re.MULTILINE
    )
    body_content = re.sub(r'\n{3,}', '\n\n', body_content)

    # Build the final report
    formatted_sources = "\n".join(
        f"[{i+1}] {src}" for i, src in enumerate(unique_sources)
    )

    final_report = (
        introduction + "\n\n---\n\n" +
        body_content + "\n\n---\n\n" +
        conclusion
    )
    final_report += "\n\n## Sources\n" + formatted_sources

    # Final sanity check: after assembly, ensure there is exactly one
    # "## Conclusion" heading. If the model also added stray Conclusion
    # headings in the body (which we stripped above), or if the conclusion
    # section itself got a duplicate, keep only the last occurrence.
    conclusion_matches = list(re.finditer(
        r'^##\s+Conclusion\s*$', final_report,
        re.IGNORECASE | re.MULTILINE
    ))
    if len(conclusion_matches) > 1:
        # Remove all but the last
        for match in reversed(conclusion_matches[:-1]):
            final_report = final_report[:match.start()] + final_report[match.end():]
        final_report = re.sub(r'\n{3,}', '\n\n', final_report).strip()

    return {"final_report": final_report, "sections": cleaned_sections}