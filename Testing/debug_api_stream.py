"""
Debug script to test API stream endpoint logic exactly
"""

import asyncio
import json
from src.graph import build_research_graph, build_interview_graph
from src.state import Analyst

async def test_api_stream_logic():
    print("Testing API stream logic exactly...")
    
    # Build graphs
    interview_graph = build_interview_graph()
    research_graph = build_research_graph(interview_graph)
    
    # Create test analysts (similar to what the API would generate)
    analysts = [
        Analyst(
            affiliation="Tesla's Autopilot Team",
            name="Dr. Rachel Kim",
            role="Senior Engineer and AI Researcher",
            description="Expert in computer vision, machine learning, and autonomous driving systems."
        ),
        Analyst(
            affiliation="Research Institute",
            name="Dr. Liam Chen",
            role="Lead Research Scientist",
            description="Renowned expert in computer vision, with a focus on object detection, tracking, and scene understanding."
        )
    ]
    
    session = {
        "topic": "Impact of Computer Vision on Automobile Industry in 2026",
        "max_analysts": 2,
        "max_turns": 2,
        "analysts": analysts,
    }
    
    topic = session["topic"]
    max_analysts = session["max_analysts"]
    analysts = session["analysts"]
    
    # This is exactly what the API does - creates a NEW thread for research
    research_thread = {"configurable": {"thread_id": f"research_test_001"}}
    
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
    
    print(f"Invoking research graph with {len(analysts)} analysts...")
    print(f"Research thread: {research_thread}")
    
    try:
        # This is exactly what the API's event_generator does
        loop = asyncio.get_event_loop()
        
        events = await loop.run_in_executor(
            None,
            lambda: list(
                research_graph.stream(
                    initial_state,
                    research_thread,
                    stream_mode="values",
                )
            ),
        )
        
        print(f"\nTotal events from stream: {len(events)}")
        for i, event in enumerate(events):
            print(f"  [{i+1}] Keys: {list(event.keys())}")
            if "sections" in event and event["sections"]:
                print(f"     Sections: {len(event['sections'])}")
            if "final_report" in event and event["final_report"]:
                print(f"     Final report: {len(event['final_report'])} chars")
        
        # Get final state
        final_state = research_graph.get_state(research_thread)
        print(f"\nFinal state keys: {list(final_state.values.keys())}")
        
        final_report = final_state.values.get('final_report', '')
        if final_report:
            print(f"Final report generated: {len(final_report)} chars")
        else:
            print("No final report generated")
            
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_api_stream_logic())