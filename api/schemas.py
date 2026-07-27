from pydantic import BaseModel, Field
from typing import Optional, List
from src.state import Analyst


class ResearchInitRequest(BaseModel):
    topic: str = Field(
        ...,
        description="The research topic or inquiry to explore.",
        min_length=1,
        max_length=500,
    )
    max_analysts: int = Field(
        default=3,
        description="Number of analyst personas to generate.",
        ge=1,
        le=10,
    )
    max_turns: int = Field(
        default=2,
        description="Number of interview turns per analyst.",
        ge=1,
        le=5,
    )


class FeedbackRequest(BaseModel):
    thread_id: str
    feedback: Optional[str] = Field(
        default=None,
        description="Optional guidance to refine the analyst panel.",
    )


class ApproveRequest(BaseModel):
    thread_id: str


class ResearchStatusResponse(BaseModel):
    thread_id: str
    status: str  # "analysts_pending", "interviewing", "complete", "error"
    analysts: Optional[List[Analyst]] = None
    progress: Optional[dict] = None