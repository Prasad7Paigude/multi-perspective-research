"""
State Models
=============

TypedDict and Pydantic model definitions that represent the state of the
multi-agent research graph at various stages of execution.

Three state types are defined:

1. ``Analyst`` / ``Perspectives``      -- Pydantic models for analyst personas.
2. ``GenerateAnalystsState``           -- State for the analyst-generation graph.
3. ``InterviewState``                  -- MessagesState for the interview sub-graph.
4. ``ResearchGraphState``              -- Top-level state for the full map-reduce pipeline.
"""

from __future__ import annotations

import operator
from typing import Annotated, List

from langgraph.graph import MessagesState
from pydantic import BaseModel, Field
from typing_extensions import TypedDict


# ===========================================================================
# Pydantic Models
# ===========================================================================

class Analyst(BaseModel):
    """A single AI analyst persona.

    Each analyst represents a distinct stakeholder perspective on the
    research topic -- e.g. an ethicist, an engineer, a policy-maker.

    Attributes:
        affiliation: The organisation or institution the analyst belongs to.
        name: Full name of the analyst persona.
        role: Professional title or role within their domain.
        description: Focus areas, concerns, and motivations.
    """

    affiliation: str = Field(description="Primary affiliation of the analyst.")
    name: str = Field(description="Name of the analyst.")
    role: str = Field(description="Role of the analyst in the context of the topic.")
    description: str = Field(
        description="Description of the analyst focus, concerns, and motives."
    )

    @property
    def persona(self) -> str:
        """Return a formatted string representation of the analyst persona.

        This is injected into LLM prompts so the model can consistently
        reference the analyst's identity and focus areas.
        """
        return (
            f"Name: {self.name}\n"
            f"Role: {self.role}\n"
            f"Affiliation: {self.affiliation}\n"
            f"Description: {self.description}\n"
        )


class Perspectives(BaseModel):
    """A collection of analyst personas returned by the LLM.

    The structured output schema used when invoking the LLM with
    ``llm.with_structured_output(Perspectives)``.

    Attributes:
        analysts: List of Analyst objects representing different perspectives.
    """

    analysts: List[Analyst] = Field(
        description="Comprehensive list of analysts with their roles and affiliations."
    )


class SearchQuery(BaseModel):
    """Structured output model for generating search queries from conversation.

    The LLM is instructed to produce a single, well-structured search query
    that reflects the analyst's persona and the conversation context.

    Attributes:
        search_query: The web search query string for retrieval.
    """

    search_query: str = Field(description="Search query for retrieval.")


# ===========================================================================
# Interview Sub-Graph State
# ===========================================================================

class InterviewState(MessagesState):
    """State for the interview sub-graph.

    Extends ``MessagesState`` (which provides a ``messages`` list for
    conversation history) with interview-specific fields.

    The ``Annotated`` types with reducer functions control how state
    values are merged when multiple parallel interview runs return.

    Attributes:
        max_num_turns: Maximum Q&A rounds in the interview.
        context: Source documents gathered (accumulated via ``operator.add``).
        analyst: The Analyst persona conducting the interview.
        interview: Full interview transcript as a string.
        sections: Final written sections (used by the Send() API).
        current_turn: Current turn number in the interview.
        total_turns: Total turns completed.
        status: Current status of the interview.
        analyst_id: Unique identifier for the analyst.
        analyst_name: Human-readable name of the analyst.
    """

    max_num_turns: Annotated[int, lambda x, y: y]  # use latest value
    context: Annotated[list, operator.add]
    analyst: Annotated[Analyst, lambda c, n: n or c]  # keep existing or use new
    interview: Annotated[str, lambda c, n: n or c]
    sections: Annotated[list, operator.add]
    current_turn: Annotated[int, lambda c, n: n or c]
    total_turns: Annotated[int, lambda c, n: n or c]
    status: Annotated[str, lambda c, n: n or c]
    analyst_id: Annotated[str, lambda c, n: n or c]
    analyst_name: Annotated[str, lambda c, n: n or c]


# ===========================================================================
# Top-Level Graph State
# ===========================================================================

def _reduce_max_turns(current: int, new: int) -> int:
    """Reducer for ``max_num_turns``: accept any value (all parallel interviews use the same).

    Args:
        current: The current max_num_turns value.
        new: The new max_num_turns value (if provided).

    Returns:
        The latest value.
    """
    return new


class ResearchGraphState(TypedDict):
    """Top-level state for the full research graph.

    This state flows through the entire map-reduce pipeline: analyst
    generation --> human feedback --> parallel interviews --> report writing
    --> finalization.

    Attributes:
        topic: The research topic or question.
        max_analysts: Number of analyst personas to generate.
        max_num_turns: Maximum interview turns per analyst.
        human_analyst_feedback: Optional feedback for regenerating analysts.
        analysts: List of approved Analyst personas.
        sections: Accumulated interview sections (via ``operator.add``).
        introduction: Generated introduction text.
        content: Consolidated body content from all sections.
        conclusion: Generated conclusion text.
        final_report: The complete assembled report.
    """

    topic: str
    max_analysts: int
    max_num_turns: Annotated[int, _reduce_max_turns]
    human_analyst_feedback: str
    analysts: List[Analyst]
    sections: Annotated[list, operator.add]
    introduction: str
    content: str
    conclusion: str
    final_report: str


# ===========================================================================
# Analyst Generation Graph State
# ===========================================================================

class GenerateAnalystsState(TypedDict):
    """State for the analyst-generation sub-graph.

    Attributes:
        topic: The research topic.
        max_analysts: Number of analysts to generate.
        human_analyst_feedback: Optional feedback string for regeneration.
        analysts: The generated list of Analyst personas.
    """

    topic: str
    max_analysts: int
    human_analyst_feedback: str
    analysts: List[Analyst]
