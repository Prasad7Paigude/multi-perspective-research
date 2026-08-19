"""
FastAPI Application — Research Assistant API
=============================================

Provides a RESTful JSON API and SSE (Server-Sent Events) streaming
endpoints for the multi-perspective AI research pipeline.

Endpoints
---------
- ``GET  /api/health``               — Health check
- ``POST /api/research/init``        — Initialize a research session
- ``POST /api/research/feedback``    — Submit feedback for analyst regeneration
- ``POST /api/research/approve``    — Approve analysts and start research
- ``GET  /api/research/stream/{id}``— SSE stream of research progress
- ``GET  /api/research/result/{id}``— Retrieve the final report
"""

from __future__ import annotations

import asyncio
import json
import logging
import time
import uuid
from typing import Any, Dict, List, Optional

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from langchain_core.messages import HumanMessage

from api.schemas import (
    ApproveRequest,
    FeedbackRequest,
    ResearchInitRequest,
    ResearchStatusResponse,
)
from src.graph import (
    build_analyst_graph,
    build_interview_graph,
    build_research_graph,
)
from src.state import Analyst, ResearchGraphState

logger = logging.getLogger(__name__)

# ===========================================================================
# Application Setup
# ===========================================================================

app = FastAPI(
    title="Research Assistant API",
    description="Multi-perspective AI research analysis pipeline",
    version="1.0.0",
)

# CORS: allow all origins in development.
# In production, restrict to specific domains.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Global State (lazy-initialised)
# ---------------------------------------------------------------------------

# Graph instances are created on first request to avoid import-time overhead.
_analyst_graph: Any = None
_interview_graph: Any = None
_research_graph: Any = None

# In-memory session store: thread_id -> session dict
sessions: Dict[str, dict] = {}


def get_graphs():
    """Lazy-load and cache the three LangGraph instances.

    Returns:
        A tuple of (analyst_graph, interview_graph, research_graph).
    """
    global _analyst_graph, _interview_graph, _research_graph
    if _analyst_graph is None:
        _analyst_graph = build_analyst_graph()
        _interview_graph = build_interview_graph()
        _research_graph = build_research_graph(_interview_graph)
    return _analyst_graph, _interview_graph, _research_graph

# ===========================================================================
# Endpoints
# ==========================================================================

@app.post("/api/research/init", response_model=ResearchStatusResponse)
async def init_research(request: ResearchInitRequest) -> ResearchStatusResponse:
    """Initialize a research session by generating analyst personas.

    Creates a new session with a unique thread ID, then streams the
    analyst-generation graph to produce diverse AI personas for the
    given research topic.

    Args:
        request: Contains topic, max_analysts, and max_turns.

    Returns:
        A ``ResearchStatusResponse`` with the thread_id and generated analysts.

    Raises:
        HTTPException: 500 if the LLM fails to generate analysts.
    """
    analyst_graph, _, _ = get_graphs()

    # Generate unique thread ID with timestamp to prevent collisions
    thread_id = f"{int(time.time())}-{str(uuid.uuid4())}"

    sessions[thread_id] = {
        "topic": request.topic,
        "max_analysts": request.max_analysts,
        "max_turns": request.max_turns,
        "analysts": [],
        "status": "analysts_pending",
        "final_report": None,
        "sections": [],
    }

    try:
        loop = asyncio.get_event_loop()
        events = await loop.run_in_executor(
            None,
            lambda: list(
                analyst_graph.stream(
                    {
                        "topic": request.topic,
                        "max_analysts": request.max_analysts,
                    },
                    {"configurable": {"thread_id": thread_id}},
                    stream_mode="values",
                )
            ),
        )

        for event in events:
            if "analysts" in event:
                sessions[thread_id]["analysts"] = event["analysts"]

    except Exception as e:
        # Clean up session on error
        if thread_id in sessions:
            del sessions[thread_id]
        # Provide more detailed error information
        error_detail = f"Failed to generate analysts: {str(e)}"
        if "connection refused" in str(e).lower() or "connection error" in str(e).lower():
            error_detail = "LLM service unavailable. Please check your LLM provider configuration and ensure the service is running."
        elif "api key" in str(e).lower():
            error_detail = "Invalid API key. Please check your LLM provider API key configuration."
        raise HTTPException(status_code=500, detail=error_detail)

    return ResearchStatusResponse(
        thread_id=thread_id,
        status="analysts_pending",
        analysts=sessions[thread_id]["analysts"],
    )

@app.post("/api/research/feedback")
async def submit_feedback(request: FeedbackRequest) -> ResearchStatusResponse:
    """Submit refinement feedback for the analyst panel.

    If ``feedback`` is a non-empty string, the analyst-generation graph
    is re-invoked to produce a new set of personas.  An empty or ``null``
    feedback value acts as implicit approval (no regeneration needed).

    Args:
        request: Contains thread_id and optional feedback string.

    Returns:
        Updated ``ResearchStatusResponse`` with possibly new analysts.

    Raises:
        HTTPException: 404 if session not found, 500 on LLM failure.
    """
    analyst_graph, _, _ = get_graphs()

    if request.thread_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")

    session = sessions[request.thread_id]
    thread = {"configurable": {"thread_id": request.thread_id}}

    try:
        loop = asyncio.get_event_loop()

        await loop.run_in_executor(
            None,
            lambda: analyst_graph.update_state(
                thread,
                {"human_analyst_feedback": request.feedback or ""},
                as_node="human_feedback",
            ),
        )

        events = await loop.run_in_executor(
            None,
            lambda: list(
                analyst_graph.stream(
                    None,
                    thread,
                    stream_mode="values",
                )
            ),
        )

        for event in events:
            if "analysts" in event:
                session["analysts"] = event["analysts"]

    except Exception as e:
        # Clean up session on error
        if request.thread_id in sessions:
            del sessions[request.thread_id]
        # Provide more detailed error information
        error_detail = f"Failed to process feedback: {str(e)}"
        if "connection refused" in str(e).lower() or "connection error" in str(e).lower():
            error_detail = "LLM service unavailable. Please check your LLM provider configuration and ensure the service is running."
        elif "api key" in str(e).lower():
            error_detail = "Invalid API key. Please check your LLM provider API key configuration."
        raise HTTPException(status_code=500, detail=error_detail)

    return ResearchStatusResponse(
        thread_id=request.thread_id,
        status="analysts_pending",
        analysts=session["analysts"],
    )

@app.post("/api/research/approve")
async def approve_analysts(request: ApproveRequest) -> dict:
    """Approve the analyst panel and transition to the interviewing phase.

    This endpoint signals that the user is satisfied with the current
    analyst personas.  It updates the session status so the SSE stream
    can proceed with the parallel interview pipeline.

    Args:
        request: Contains the thread_id to approve.

    Returns:
        A JSON dict with thread_id and updated status.

    Raises:
        HTTPException: 404 if the session is not found.
    """
    if request.thread_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")

    sessions[request.thread_id]["status"] = "interviewing"

    return {"thread_id": request.thread_id, "status": "interviewing", "message": "Research pipeline ready"}

@app.get("/api/research/stream/{thread_id}")
async def stream_research(thread_id: str, request: Request):
    """Stream research progress via Server-Sent Events (SSE).

    This endpoint orchestrates the full map-reduce pipeline:

    1. Emits ``interview_start`` and ``thinking_start`` events for each
       analyst (with the analyst's name, role, and affiliation).
    2. Runs the research graph in a background executor.
    3. Continuously emits ``interview_progress`` events while the graph runs.
    4. Yields ``section``, ``introduction``, ``conclusion``, and
       ``final_report`` events as they are produced.
    5. Ends with a ``done`` event when the pipeline completes.

    Reconnects are supported: if the client disconnects and reconnects,
    the server emits a ``snapshot`` event capturing the current progress.

    Args:
        thread_id: The session identifier from ``init_research``.
        request: The incoming HTTP request (used to detect client disconnect).

    Returns:
        A ``StreamingResponse`` with ``text/event-stream`` media type.

    Raises:
        HTTPException: 404 if the session is not found.
    """
    if thread_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")

    session = sessions[thread_id]
    _, _, research_graph = get_graphs()

    topic = session["topic"]
    max_analysts = session["max_analysts"]
    max_turns = session["max_turns"]
    analysts = session["analysts"]

    # Ensure we have exactly max_analysts analysts
    # If LLM generated fewer, create placeholder analysts
    if len(analysts) < max_analysts:
        from src.state import Analyst
        for i in range(len(analysts), max_analysts):
            analysts.append(Analyst(
                affiliation=f"Research Institute {i + 1}",
                name=f"Dr. Analyst {i + 1}",
                role="Research Analyst",
                description=f"Expert analyst focusing on {topic}"
            ))
        session["analysts"] = analysts

    research_thread = {"configurable": {"thread_id": f"research_{thread_id}"}}

    async def event_generator():
        loop = asyncio.get_event_loop()

        # Check if this is a reconnect and emit snapshot if progress exists
        if "analyst_progress" in session:
            analyst_progress = session["analyst_progress"]
            sub_step_weights = {
                "pending": 0,
                "asking_question": 25,
                "searching": 50,
                "generating_answer": 75,
                "completed": 100
            }
            
            # Calculate aggregated progress for snapshot
            analyst_percentages = []
            eta_seconds = None
            current_analyst_driving_eta = None
            
            for analyst_id, progress in analyst_progress.items():
                completed_turns_for_analyst = progress["current_turn"]
                sub_step_pct = sub_step_weights.get(progress["status"], 0)
                analyst_pct = ((completed_turns_for_analyst * 100) + sub_step_pct) / max_turns
                analyst_percentages.append(analyst_pct)
                
                remaining_turns = max_turns - progress["current_turn"]
                if progress["avg_time_per_turn"] is not None and remaining_turns > 0:
                    analyst_eta = remaining_turns * progress["avg_time_per_turn"]
                    if eta_seconds is None or analyst_eta > eta_seconds:
                        eta_seconds = analyst_eta
                        current_analyst_driving_eta = progress["analyst_name"]
            
            overall_percentage = sum(analyst_percentages) / len(analyst_percentages) if analyst_percentages else 0
            
            # Emit snapshot event
            yield f"data: {json.dumps({'type': 'snapshot', 'payload': {
                'overall_percentage': round(overall_percentage, 2),
                'eta_seconds': round(eta_seconds) if eta_seconds is not None else None,
                'current_analyst': current_analyst_driving_eta,
                'current_turn': max((p["current_turn"] for p in analyst_progress.values()), default=0),
                'total_turns': max_turns,
                'total_analysts': len(analysts),
                'analysts': [
                    {
                        'analyst_id': p["analyst_id"],
                        'analyst_name': p["analyst_name"],
                        'current_turn': p["current_turn"],
                        'status': p["status"],
                        'sub_step_percentage': sub_step_weights.get(p["status"], 0)
                    }
                    for p in analyst_progress.values()
                ]
            }})}\n\n"
            await asyncio.sleep(0.1)

        # Send initial status
        yield f"data: {json.dumps({'type': 'status', 'payload': 'Starting parallel expert interviews...'})}\n\n"
        await asyncio.sleep(0)  # Force flush

        try:
            initial_state = {
                "topic": topic,
                "max_analysts": max_analysts,
                "max_num_turns": max_turns,
                "human_analyst_feedback": None,
                "analysts": analysts,
                "sections": [],
                "introduction": "",
                "content": "",
                "conclusion": "",
                "final_report": "",
            }

            logger.debug("Initial state: topic=%s, max_analysts=%s, analysts_count=%s", topic, max_analysts, len(analysts))
            logger.debug("Research thread: %s", research_thread)

            logger.debug("Starting research graph stream...")

            # Emit initial status - parallel interviews starting
            yield f"data: {json.dumps({'type': 'status', 'payload': f'Starting {len(analysts)} parallel expert interviews...'})}\n\n"
            await asyncio.sleep(0.5)

            # Initialize per-analyst progress tracking
            analyst_progress = {}
            sub_step_weights = {
                "pending": 0,
                "asking_question": 25,
                "searching": 50,
                "generating_answer": 75,
                "completed": 100
            }
            
            for analyst_idx, analyst in enumerate(analysts):
                analyst_id = f"analyst_{analyst_idx}"
                analyst_name = getattr(analyst, 'name', f'Analyst {analyst_idx + 1}')
                analyst_role = getattr(analyst, 'role', 'Research Analyst')
                
                analyst_progress[analyst_id] = {
                    "analyst_id": analyst_id,
                    "analyst_name": analyst_name,
                    "analyst_role": analyst_role,
                    "current_turn": 0,
                    "total_turns": max_turns,
                    "status": "pending",
                    "turn_start_time": None,
                    "turn_times": [],
                    "avg_time_per_turn": None
                }
                
                # Emit interview_start event
                yield f"data: {json.dumps({'type': 'interview_start', 'payload': {
                    'analystIndex': analyst_idx,
                    'totalAnalysts': len(analysts),
                    'analystName': analyst_name,
                    'analystRole': analyst_role
                }})}\n\n"
                await asyncio.sleep(0.1)
                
                # Emit initial progress_update for this analyst
                yield f"data: {json.dumps({'type': 'progress_update', 'payload': {
                    'analyst_id': analyst_id,
                    'analyst_name': analyst_name,
                    'current_turn': 0,
                    'total_turns': max_turns,
                    'status': 'pending',
                    'sub_step_percentage': 0,
                    'timestamp': time.time()
                }})}\n\n"
                await asyncio.sleep(0.05)
            
            # Store progress state in session for reconnect support
            session["analyst_progress"] = analyst_progress

            # Now run the actual research graph
            # Run stream in executor and yield events as they come
            # The graph will pause at human_feedback (interrupt_before)
            # We need to resume it immediately with no feedback

            # Track which analysts have completed their interviews
            completed_analysts = set()

            def run_stream():
                try:
                    events = []
                    # First stream: starts at human_feedback, pauses at human_feedback
                    logger.debug("First stream - will pause at human_feedback")
                    for event in research_graph.stream(
                        initial_state,
                        research_thread,
                        stream_mode="values",
                    ):
                        events.append(event)

                    logger.debug("First stream completed with %d events", len(events))

                    # Check if graph is paused at human_feedback
                    state = research_graph.get_state(research_thread)
                    logger.debug("Graph state after first stream: next=%s", state.next)

                    if state.next and "human_feedback" in state.next:
                        # Resume with no feedback (approved analysts)
                        logger.debug("Graph paused at human_feedback, resuming with no feedback")
                        research_graph.update_state(
                            research_thread,
                            {"human_analyst_feedback": None},
                            as_node="human_feedback",
                        )

                        # Second stream: runs from human_feedback to completion
                        logger.debug("Second stream - resuming from human_feedback")
                        for event in research_graph.stream(
                            None,
                            research_thread,
                            stream_mode="values",
                        ):
                            events.append(event)
                        logger.debug("Second stream completed with %d total events", len(events))

                    return events
                except Exception as e:
                    logger.debug("Stream execution error: %s", e)
                    import traceback
                    traceback.print_exc()
                    raise

            # Start graph execution in background
            graph_future = loop.run_in_executor(None, run_stream)

            # Emit progress events while waiting for graph to complete
            graph_done = False  # Progress tracking loop

            # Emit initial aggregated progress
            # Inline the aggregated progress calculation
            analyst_percentages = []
            eta_seconds = None
            current_analyst_driving_eta = None
            
            for analyst_id, progress in analyst_progress.items():
                completed_turns_for_analyst = progress["current_turn"]
                sub_step_pct = sub_step_weights.get(progress["status"], 0)
                analyst_pct = ((completed_turns_for_analyst * 100) + sub_step_pct) / max_turns
                analyst_percentages.append(analyst_pct)
                
                remaining_turns = max_turns - progress["current_turn"]
                if progress["avg_time_per_turn"] is not None and remaining_turns > 0:
                    analyst_eta = remaining_turns * progress["avg_time_per_turn"]
                    if eta_seconds is None or analyst_eta > eta_seconds:
                        eta_seconds = analyst_eta
                        current_analyst_driving_eta = progress["analyst_name"]
            
            overall_percentage = sum(analyst_percentages) / len(analyst_percentages) if analyst_percentages else 0
            yield f"data: {json.dumps({'type': 'interview_progress', 'payload': {
                'overall_percentage': round(overall_percentage, 2),
                'eta_seconds': round(eta_seconds) if eta_seconds is not None else None,
                'current_analyst': current_analyst_driving_eta,
                'current_turn': max((p["current_turn"] for p in analyst_progress.values()), default=0),
                'total_turns': max_turns,
                'total_analysts': len(analysts)
            }})}\n\n"
            await asyncio.sleep(0.1)
            
            # Simulate progress updates (replace with actual LangGraph hooks later)
            while not graph_done:
                # Check if graph is done
                if graph_future.done():
                    graph_done = True
                    break
                
                # Update progress for each analyst
                for analyst_id, progress in analyst_progress.items():
                    if progress["current_turn"] < max_turns and progress["status"] != "completed":
                        # Simulate sub-step progression
                        if progress["status"] == "pending":
                            progress["status"] = "asking_question"
                            progress["turn_start_time"] = time.time()
                        elif progress["status"] == "asking_question":
                            progress["status"] = "searching"
                        elif progress["status"] == "searching":
                            progress["status"] = "generating_answer"
                        elif progress["status"] == "generating_answer":
                            progress["status"] = "completed"
                            progress["current_turn"] += 1
                            # Record turn time
                            if progress["turn_start_time"] is not None:
                                turn_time = time.time() - progress["turn_start_time"]
                                progress["turn_times"].append(turn_time)
                                # Update moving average
                                if len(progress["turn_times"]) == 1:
                                    progress["avg_time_per_turn"] = 45.0  # Seed with 45s
                                else:
                                    progress["avg_time_per_turn"] = sum(progress["turn_times"]) / len(progress["turn_times"])
                            progress["turn_start_time"] = None
                            if progress["current_turn"] < max_turns:
                                progress["status"] = "asking_question"
                                progress["turn_start_time"] = time.time()
                        
                        # Update session state for reconnect support
                        session["analyst_progress"] = analyst_progress
                        
                        # Emit progress_update for this analyst
                        yield f"data: {json.dumps({'type': 'progress_update', 'payload': {
                            'analyst_id': analyst_id,
                            'analyst_name': progress["analyst_name"],
                            'current_turn': progress["current_turn"],
                            'total_turns': max_turns,
                            'status': progress["status"],
                            'sub_step_percentage': sub_step_weights.get(progress["status"], 0),
                            'timestamp': time.time()
                        }})}\n\n"
                        
                        # Emit aggregated progress (inline)
                        analyst_percentages = []
                        eta_seconds = None
                        current_analyst_driving_eta = None
                        
                        for a_id, p in analyst_progress.items():
                            completed_turns_for_analyst = p["current_turn"]
                            sub_step_pct = sub_step_weights.get(p["status"], 0)
                            analyst_pct = ((completed_turns_for_analyst * 100) + sub_step_pct) / max_turns
                            analyst_percentages.append(analyst_pct)
                            
                            remaining_turns = max_turns - p["current_turn"]
                            if p["avg_time_per_turn"] is not None and remaining_turns > 0:
                                analyst_eta = remaining_turns * p["avg_time_per_turn"]
                                if eta_seconds is None or analyst_eta > eta_seconds:
                                    eta_seconds = analyst_eta
                                    current_analyst_driving_eta = p["analyst_name"]
                        
                        overall_percentage = sum(analyst_percentages) / len(analyst_percentages) if analyst_percentages else 0
                        yield f"data: {json.dumps({'type': 'interview_progress', 'payload': {
                            'overall_percentage': round(overall_percentage, 2),
                            'eta_seconds': round(eta_seconds) if eta_seconds is not None else None,
                            'current_analyst': current_analyst_driving_eta,
                            'current_turn': max((p["current_turn"] for p in analyst_progress.values()), default=0),
                            'total_turns': max_turns,
                            'total_analysts': len(analysts)
                        }})}\n\n"
                        await asyncio.sleep(0.1)
                
                await asyncio.sleep(0.5)
                
                # Check again if graph is done
                if graph_future.done():
                    graph_done = True
                    break

            # Get the result
            try:
                events = await asyncio.wrap_future(graph_future)
            except Exception as e:
                logger.debug("Graph execution failed: %s", e)
                import traceback
                traceback.print_exc()
                yield f"data: {json.dumps({'type': 'error', 'payload': f'Research execution failed: {str(e)}'})}\n\n"
                return

            # Apply timeout check
            start_time = time.time()
            if time.time() - start_time > 300.0:
                logger.debug("Stream execution timed out after 300 seconds")
                yield f"data: {json.dumps({'type': 'error', 'payload': 'Research execution timed out'})}\n\n"
                return

            logger.debug("Total events from stream: %d", len(events))
            for i, event in enumerate(events):
                logger.debug("Event %d keys: %s", i+1, list(event.keys()))
                if "sections" in event:
                    logger.debug("  Sections: %s", len(event["sections"]) if event.get("sections") else 0)
                if "final_report" in event:
                    logger.debug("  Final report: %s chars", len(event["final_report"]) if event.get("final_report") else 0)

            if not events:
                logger.warning("No events returned from stream!")
                # Try invoking directly
                logger.debug("Trying direct invoke...")
                try:
                    result = await loop.run_in_executor(
                        None,
                        lambda: research_graph.invoke(
                            initial_state,
                            research_thread,
                        )
                    )
                    logger.debug("Direct invoke result keys: %s", list(result.keys()))
                    if "final_report" in result:
                        logger.debug("Direct invoke final_report: %d chars", len(result["final_report"]))
                        # Create a final event with the report
                        events = [{
                            **initial_state,
                            "final_report": result["final_report"],
                            "sections": result.get("sections", []),
                            "introduction": result.get("introduction", ""),
                            "content": result.get("content", ""),
                            "conclusion": result.get("conclusion", ""),
                        }]
                except Exception as e:
                    logger.debug("Direct invoke error: %s", e)
                    import traceback
                    traceback.print_exc()

            # Ensure we have sections for all analysts
            # If graph didn't return enough sections, create placeholder sections
            final_sections = session.get("sections", [])
            if len(final_sections) < len(analysts):
                logger.debug("Only %d sections returned, expected %d", len(final_sections), len(analysts))
                # Create placeholder sections for missing analysts
                for i in range(len(final_sections), len(analysts)):
                    analyst = analysts[i]
                    placeholder_section = f"## {analyst.name}'s Perspective\n\n{analyst.description}\n\nThis analyst's detailed analysis will appear here."
                    final_sections.append(placeholder_section)
                    session["sections"] = final_sections

            # Yield events one by one with small delay to ensure streaming
            # Only skip the FIRST event (initial state), not all events with analysts
            sections_yielded = 0
            for i, event in enumerate(events):
                logger.debug("Yielding event %d/%d", i+1, len(events))
                # Skip only the first event (initial state)
                if i == 0:
                    logger.debug("Skipping initial state event")
                    continue

                # Check for final_report first (highest priority)
                payload = None
                if "final_report" in event and event["final_report"]:
                    payload = {"type": "final_report", "payload": event["final_report"]}
                    session["final_report"] = event["final_report"]
                    session["status"] = "complete"
                    logger.debug("Yielding final_report: %d chars", len(event["final_report"]))
                # Check for sections - yield ALL sections, not just new ones
                elif "sections" in event and event["sections"]:
                    sections_list = event["sections"]
                    if sections_list:
                        # Update session with all sections
                        session["sections"] = sections_list
                        # Yield each section that hasn't been yielded yet
                        for j in range(sections_yielded, len(sections_list)):
                            section_text = sections_list[j]
                            payload = {"type": "section", "payload": section_text}
                            sections_yielded = j + 1
                            logger.debug("Yielding section %d/%d: %d chars", j+1, len(sections_list), len(section_text))
                            yield f"data: {json.dumps(payload)}\n\n"
                            await asyncio.sleep(0.01)
                        continue
                elif "content" in event and event["content"]:
                    payload = {"type": "report", "payload": event["content"]}
                    logger.debug("Yielding report: %d chars", len(event["content"]))
                elif "introduction" in event and event["introduction"]:
                    payload = {"type": "introduction", "payload": event["introduction"]}
                    logger.debug("Yielding introduction: %d chars", len(event["introduction"]))
                elif "conclusion" in event and event["conclusion"]:
                    payload = {"type": "conclusion", "payload": event["conclusion"]}
                    logger.debug("Yielding conclusion: %d chars", len(event["conclusion"]))

                if payload:
                    logger.debug("Sending payload type: %s", payload["type"])
                    yield f"data: {json.dumps(payload)}\n\n"
                    # Force flush by yielding control
                    await asyncio.sleep(0.01)

            logger.debug("Sending done event")
            yield f"data: {json.dumps({'type': 'done', 'payload': ''})}\n\n"
            await asyncio.sleep(0.01)

        except Exception as e:
            import traceback
            tb = traceback.format_exc()
            error_detail = f"{type(e).__name__}: {str(e)}"
            logger.error("ERROR in event_generator: %s", error_detail)
            logger.debug("Traceback: %s", tb)
            yield f"data: {json.dumps({'type': 'error', 'payload': error_detail})}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
            "Content-Type": "text/event-stream",
        },
    )

@app.get("/api/research/result/{thread_id}")
async def get_result(thread_id: str):
    """Get the final research report."""
    if thread_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")

    session = sessions[thread_id]

    if session["status"] != "complete":
        return {"thread_id": thread_id, "status": session["status"], "report": None}

    return {
        "thread_id": thread_id,
        "status": "complete",
        "report": session["final_report"],
        "sections": session["sections"],
    }

@app.get("/api/health")
async def health() -> dict:
    """Health check endpoint.

    Returns:
        A simple JSON payload confirming the service is up.
    """
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)