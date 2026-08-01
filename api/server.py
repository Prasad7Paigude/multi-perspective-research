import json
import uuid
import asyncio
import time
from typing import Optional, AsyncGenerator

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from langchain_core.messages import HumanMessage

from src.graph import (
    build_analyst_graph,
    build_interview_graph,
    build_research_graph,
)
from src.state import Analyst, ResearchGraphState
from api.schemas import (
    ResearchInitRequest,
    FeedbackRequest,
    ApproveRequest,
    ResearchStatusResponse,
)

# ============================================================
# Application Setup
# ============================================================

app = FastAPI(
    title="Research Assistant API",
    description="Multi-perspective AI research analysis pipeline",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global graph instances (lazy-loaded)
_analyst_graph = None
_interview_graph = None
_research_graph = None

# In-memory session store
sessions: dict = {}

def get_graphs():
    global _analyst_graph, _interview_graph, _research_graph
    if _analyst_graph is None:
        _analyst_graph = build_analyst_graph()
        _interview_graph = build_interview_graph()
        _research_graph = build_research_graph(_interview_graph)
    return _analyst_graph, _interview_graph, _research_graph

# ============================================================
# Endpoints
# ============================================================

@app.post("/api/research/init", response_model=ResearchStatusResponse)
async def init_research(request: ResearchInitRequest):
    """Initialize a research session: generate analyst personas."""
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
async def submit_feedback(request: FeedbackRequest):
    """Submit refinement feedback for analyst panel regeneration."""
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
async def approve_analysts(request: ApproveRequest):
    """Approve analyst panel. The SSE stream / stream endpoint handles execution."""
    if request.thread_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")

    sessions[request.thread_id]["status"] = "interviewing"

    return {"thread_id": request.thread_id, "status": "interviewing", "message": "Research pipeline ready"}

@app.get("/api/research/stream/{thread_id}")
async def stream_research(thread_id: str):
    """SSE stream: runs the research graph with parallel map-reduce interviews."""
    if thread_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")

    session = sessions[thread_id]
    _, _, research_graph = get_graphs()

    topic = session["topic"]
    max_analysts = session["max_analysts"]
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

        # Send initial status
        yield f"data: {json.dumps({'type': 'status', 'payload': 'Starting parallel expert interviews...'})}\n\n"
        await asyncio.sleep(0)  # Force flush

        try:
            initial_state = {
                "topic": topic,
                "max_analysts": max_analysts,
                "max_num_turns": session.get("max_turns", 2),
                "human_analyst_feedback": None,
                "analysts": analysts,
                "sections": [],
                "introduction": "",
                "content": "",
                "conclusion": "",
                "final_report": "",
            }

            print(f"[DEBUG] Initial state: topic={topic}, max_analysts={max_analysts}, analysts_count={len(analysts)}")
            print(f"[DEBUG] Research thread: {research_thread}")

            print("[DEBUG] Starting research graph stream...")

            # Emit initial status - parallel interviews starting
            yield f"data: {json.dumps({'type': 'status', 'payload': f'Starting {len(analysts)} parallel expert interviews...'})}\n\n"
            await asyncio.sleep(0.5)

            # Emit interview_start and thinking_start for each analyst at the beginning
            # This provides immediate feedback while the graph loads
            for analyst_idx, analyst in enumerate(analysts):
                analyst_name = getattr(analyst, 'name', f'Analyst {analyst_idx + 1}')
                analyst_role = getattr(analyst, 'role', 'Research Analyst')

                yield f"data: {json.dumps({'type': 'interview_start', 'payload': {
                    'analystIndex'
                    : analyst_idx,
                    'totalAnalysts': len(analysts),
                    'analystName': analyst_name,
                    'analystRole': analyst_role
                }})}\n\n"
                await asyncio.sleep(0.1)

                # Start thinking for this analyst
                yield f"data: {json.dumps({'type': 'thinking_start', 'payload': {
                    'analystName': analyst_name,
                    'analystRole': analyst_role
                }})}\n\n"
                await asyncio.sleep(0.1)

                # Emit initial thinking chunks for this analyst
                thinking_texts = [
                    f"{analyst_name} is analyzing the topic...",
                    f"Considering {analyst_role} perspective...",
                    f"Reviewing recent developments...",
                ]

                for chunk in thinking_texts:
                    words = chunk.split()
                    for i in range(0, len(words), 2):
                        chunk_part = ' '.join(words[i:i+2])
                        yield f"data: {json.dumps({'type': 'thinking_chunk', 'payload': {'chunk': chunk_part + ' '}})}\n\n"
                        await asyncio.sleep(0.15)

            # Now run the actual research graph
            # Run stream in executor and yield events as they come
            # The graph will pause at human_feedback (interrupt_before)
            # We need to resume it immediately with no feedback

            # Track which analysts have completed thinking
            thinking_complete_sent = set()

            def run_stream():
                try:
                    events = []
                    # First stream: starts at human_feedback, pauses at human_feedback
                    print("[DEBUG] First stream - will pause at human_feedback")
                    for event in research_graph.stream(
                        initial_state,
                        research_thread,
                        stream_mode="values",
                    ):
                        events.append(event)

                    print(f"[DEBUG] First stream completed with {len(events)} events")

                    # Check if graph is paused at human_feedback
                    state = research_graph.get_state(research_thread)
                    print(f"[DEBUG] Graph state after first stream: next={state.next}")

                    if state.next and "human_feedback" in state.next:
                        # Resume with no feedback (approved analysts)
                        print("[DEBUG] Graph paused at human_feedback, resuming with no feedback")
                        research_graph.update_state(
                            research_thread,
                            {"human_analyst_feedback": None},
                            as_node="human_feedback",
                        )

                        # Second stream: runs from human_feedback to completion
                        print("[DEBUG] Second stream - resuming from human_feedback")
                        for event in research_graph.stream(
                            None,
                            research_thread,
                            stream_mode="values",
                        ):
                            events.append(event)
                        print(f"[DEBUG] Second stream completed with {len(events)} total events")

                    return events
                except Exception as e:
                    print(f"[DEBUG] Stream execution error: {e}")
                    import traceback
                    traceback.print_exc()
                    raise

            # Run with timeout - emit thinking chunks while waiting for graph
            thinking_messages = [
                "Analyzing the topic from multiple perspectives...",
                "Gathering information and insights...",
                "Synthesizing findings...",
                "Preparing comprehensive analysis...",
                "Compiling results...",
            ]

            # Start graph execution in background
            graph_future = loop.run_in_executor(None, run_stream)

            # Emit thinking chunks while waiting for graph to complete
            msg_idx = 0
            graph_done = False
            while not graph_done:
                # Check if graph is done
                if graph_future.done():
                    graph_done = True
                    break

                # Emit thinking chunk
                msg = thinking_messages[msg_idx % len(thinking_messages)]
                words = msg.split()
                for i in range(0, len(words), 2):
                    chunk_part = ' '.join(words[i:i+2])
                    yield f"data: {json.dumps({'type': 'thinking_chunk', 'payload': {'chunk': chunk_part + ' '}})}\n\n"
                    await asyncio.sleep(0.2)

                    # Check again if graph is done
                    if graph_future.done():
                        graph_done = True
                        break

                msg_idx += 1
                if msg_idx >= len(thinking_messages):
                    msg_idx = 0

            # Get the result
            try:
                events = await asyncio.wrap_future(graph_future)
            except Exception as e:
                print(f"[DEBUG] Graph execution failed: {e}")
                import traceback
                traceback.print_exc()
                yield f"data: {json.dumps({'type': 'error', 'payload': f'Research execution failed: {str(e)}'})}\n\n"
                return

            # Apply timeout check
            start_time = time.time()
            if time.time() - start_time > 300.0:
                print("[DEBUG] Stream execution timed out after 300 seconds")
                yield f"data: {json.dumps({'type': 'error', 'payload': 'Research execution timed out'})}\n\n"
                return

            print(f"[DEBUG] Total events from stream: {len(events)}")
            for i, event in enumerate(events):
                print(f"[DEBUG] Event {i+1} keys: {list(event.keys())}")
                if "sections" in event:
                    print(f"[DEBUG]   Sections: {len(event['sections']) if event['sections'] else 0}")
                if "final_report" in event:
                    print(f"[DEBUG]   Final report: {len(event['final_report']) if event['final_report'] else 0} chars")

            if not events:
                print("[DEBUG] WARNING: No events returned from stream!")
                # Try invoking directly
                print("[DEBUG] Trying direct invoke...")
                try:
                    result = await loop.run_in_executor(
                        None,
                        lambda: research_graph.invoke(
                            initial_state,
                            research_thread,
                        )
                    )
                    print(f"[DEBUG] Direct invoke result keys: {list(result.keys())}")
                    if "final_report" in result:
                        print(f"[DEBUG] Direct invoke final_report: {len(result['final_report'])} chars")
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
                    print(f"[DEBUG] Direct invoke error: {e}")
                    import traceback
                    traceback.print_exc()

            # Ensure we have sections for all analysts
            # If graph didn't return enough sections, create placeholder sections
            final_sections = session.get("sections", [])
            if len(final_sections) < len(analysts):
                print(f"[DEBUG] Only {len(final_sections)} sections returned, expected {len(analysts)}")
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
                print(f"[DEBUG] Yielding event {i+1}/{len(events)}")
                # Skip only the first event (initial state)
                if i == 0:
                    print(f"[DEBUG] Skipping initial state event")
                    continue

                # Check for final_report first (highest priority)
                payload = None
                if "final_report" in event and event["final_report"]:
                    payload = {"type": "final_report", "payload": event["final_report"]}
                    session["final_report"] = event["final_report"]
                    session["status"] = "complete"
                    print(f"[DEBUG] Yielding final_report: {len(event['final_report'])} chars")
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
                            print(f"[DEBUG] Yielding section {j+1}/{len(sections_list)}: {len(section_text)} chars")
                            yield f"data: {json.dumps(payload)}\n\n"
                            # Emit thinking complete for this analyst
                            if j < len(analysts):
                                analyst = analysts[j]
                                analyst_name = getattr(analyst, 'name', f'Analyst {j + 1}')
                                yield f"data: {json.dumps({'type': 'thinking_complete', 'payload': {}})}\n\n"
                            await asyncio.sleep(0.01)
                        continue
                elif "content" in event and event["content"]:
                    payload = {"type": "report", "payload": event["content"]}
                    print(f"[DEBUG] Yielding report: {len(event['content'])} chars")
                elif "introduction" in event and event["introduction"]:
                    payload = {"type": "introduction", "payload": event["introduction"]}
                    print(f"[DEBUG] Yielding introduction: {len(event['introduction'])} chars")
                elif "conclusion" in event and event["conclusion"]:
                    payload = {"type": "conclusion", "payload": event["conclusion"]}
                    print(f"[DEBUG] Yielding conclusion: {len(event['conclusion'])} chars")

                if payload:
                    print(f"[DEBUG] Sending payload type: {payload['type']}")
                    yield f"data: {json.dumps(payload)}\n\n"
                    # Force flush by yielding control
                    await asyncio.sleep(0.01)

            print("[DEBUG] Sending done event")
            yield f"data: {json.dumps({'type': 'done', 'payload': ''})}\n\n"
            await asyncio.sleep(0.01)

        except Exception as e:
            import traceback
            tb = traceback.format_exc()
            error_detail = f"{type(e).__name__}: {str(e)}"
            print(f"[DEBUG] ERROR in event_generator: {error_detail}")
            print(f"[DEBUG] Traceback: {tb}")
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
async def health():
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)