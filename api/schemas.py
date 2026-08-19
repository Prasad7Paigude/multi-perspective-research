"""
API Schemas
===========

Pydantic request and response models for the FastAPI application.
"""

from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, Field

from src.state import Analyst


# ===========================================================================
# Request Models
# ===========================================================================

class ResearchInitRequest(BaseModel):
    """Request payload for initialising a research session.

    Attributes:
        topic: The research topic or inquiry to explore (1-500 chars).
        max_analysts: Number of analyst personas to generate (1-10).
        max_turns: Number of interview turns per analyst (1-5).
    """

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
    """Request payload for submitting feedback on the analyst panel.

    Attributes:
        thread_id: The unique session identifier.
        feedback: Optional guidance string for regenerating analysts.
            An empty or null value signals approval.
    """

    thread_id: str
    feedback: Optional[str] = Field(
        default=None,
        description="Optional guidance to refine the analyst panel.",
    )


class ApproveRequest(BaseModel):
    """Request payload for approving analysts and starting research.

    Attributes:
        thread_id: The unique session identifier.
    """

    thread_id: str


# ===========================================================================
# Response Models
# ===========================================================================

class ResearchStatusResponse(BaseModel):
    """Response model for research session status.

    Attributes:
        thread_id: The unique session identifier.
        status: Current session status. One of:
            ``"analysts_pending"``, ``"interviewing"``, ``"complete"``, ``"error"``.
        analysts: The generated analyst personas (present when status
            is ``"analysts_pending"``).
        progress: Optional progress metadata (sections count, etc.).
    """

    thread_id: str
    status: str
    analysts: Optional[List[Analyst]] = None
    progress: Optional[dict] = None
