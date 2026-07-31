"""
Debug script to test research graph execution directly
"""

import asyncio
import sys
import os
from langchain_core.messages import HumanMessage

# Add parent directory to path so we can import from src, config, utils
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.graph import build_research_graph, build_interview_graph
from src.state import Analyst

async def test_research_graph():
    print("Testing research graph directly...")
    
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
    
    topic = "Impact of Computer Vision on Automobile Industry in 2026"
    max_analysts = 2
    max_turns = 2
    
    thread = {"configurable": {"thread_id": "debug_research_001"}}
    
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
    
    print(f"Invoking research graph with {len(analysts)} analysts...")
    print(f"Topic: {topic}")
    print(f"Max turns: {max_turns}")
    
    try:
        # First stream: runs create_analysts, pauses at human_feedback
        print("\n--- First stream (will pause at human_feedback) ---")
        event_count = 0
        for event in research_graph.stream(initial_state, thread, stream_mode="updates"):
            event_count += 1
            node_name = list(event.keys())[0]
            print(f"  [{event_count}] Node: {node_name}")
        
        # Check if graph is paused at human_feedback
        state = research_graph.get_state(thread)
        print(f"\nGraph state after first stream: next={state.next}")
        
        if state.next and "human_feedback" in state.next:
            # Resume with no feedback (approved analysts)
            print("\n--- Graph paused at human_feedback, resuming with no feedback ---")
            research_graph.update_state(
                thread,
                {"human_analyst_feedback": None},
                as_node="human_feedback",
            )
            
            # Second stream: runs from human_feedback to completion
            print("\n--- Second stream (resuming from human_feedback) ---")
            for event in research_graph.stream(None, thread, stream_mode="updates"):
                event_count += 1
                node_name = list(event.keys())[0]
                print(f"  [{event_count}] Node: {node_name}")
                
                if node_name == "conduct_interview":
                    interview_state = event[node_name]
                    if "sections" in interview_state and interview_state["sections"]:
                        print(f"     Section generated: {len(interview_state['sections'])} sections")
                        for i, section in enumerate(interview_state['sections']):
                            print(f"       Section {i+1}: {section[:100]}...")
        
        print(f"\nTotal events: {event_count}")
        
        # Get final state
        final_state = research_graph.get_state(thread)
        print(f"\nFinal state keys: {list(final_state.values.keys())}")
        
        final_report = final_state.values.get('final_report', '')
        if final_report:
            print(f"Final report generated: {len(final_report)} chars")
            print(f"Preview: {final_report[:200]}...")
        else:
            print("No final report generated")
            print(f"Sections: {final_state.values.get('sections', [])}")
            print(f"Introduction: {final_state.values.get('introduction', '')[:100]}...")
            print(f"Content: {final_state.values.get('content', '')[:100]}...")
            print(f"Conclusion: {final_state.values.get('conclusion', '')[:100]}...")
            
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_research_graph())