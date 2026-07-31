"""
Debug script to test research graph with stream_mode='values' (like the API)
"""

import asyncio
from langchain_core.messages import HumanMessage
from src.graph import build_research_graph, build_interview_graph
from src.state import Analyst

async def test_research_graph_values():
    print("Testing research graph with stream_mode='values'...")
    
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
    
    thread = {"configurable": {"thread_id": "debug_research_002"}}
    
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
        # Use stream with values mode (like the API)
        print("\n--- Streaming with stream_mode='values' ---")
        event_count = 0
        for event in research_graph.stream(initial_state, thread, stream_mode="values"):
            event_count += 1
            print(f"  [{event_count}] Event keys: {list(event.keys())}")
            
            if "sections" in event and event["sections"]:
                print(f"     Sections: {len(event['sections'])}")
                for i, section in enumerate(event['sections']):
                    print(f"       Section {i+1}: {section[:100]}...")
            
            if "final_report" in event and event["final_report"]:
                print(f"     Final report: {len(event['final_report'])} chars")
        
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
            
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_research_graph_values())