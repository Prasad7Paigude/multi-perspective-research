from typing import List, Annotated
from typing_extensions import TypedDict
from pydantic import BaseModel, Field
import operator
from langgraph.graph import MessagesState


class Analyst(BaseModel):
    affiliation: str = Field(
        description="Primary affiliation of the analyst.",
    )
    name: str = Field(
        description="Name of the analyst."
    )
    role: str = Field(
        description="Role of the analyst in the context of the topic.",
    )
    description: str = Field(
        description="Description of the analyst focus, concerns, and motives.",
    )

    @property
    def persona(self) -> str:
        return f"Name: {self.name}\nRole: {self.role}\nAffiliation: {self.affiliation}\nDescription: {self.description}\n"


class Perspectives(BaseModel):
    analysts: List[Analyst] = Field(
        description="Comprehensive list of analysts with their roles and affiliations.",
    )


class GenerateAnalystsState(TypedDict):
    topic: str
    max_analysts: int
    human_analyst_feedback: str
    analysts: List[Analyst]


class SearchQuery(BaseModel):
    search_query: str = Field(description="Search query for retrieval.")


class InterviewState(MessagesState):
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


def _reduce_max_turns(current: int, new: int) -> int:
    """Reducer for max_num_turns: accept any value (all parallel interviews use the same)."""
    return new


class ResearchGraphState(TypedDict):
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
