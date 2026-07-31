"""
AI Workflow Test Script - Terminal-based testing for Research Assistant
==========================================================================
This script tests the AI workflow step by step with terminal interaction.
User provides: Topic, max_analysts, max_turns, optional feedback
Expected flow:
1. Generate analysts
2. User reviews and provides feedback (optional)
3. Re-generate if feedback provided
4. User approves
5. Conduct interviews in parallel
6. Generate final report
"""

import sys
import os
from datetime import datetime
from langchain_core.messages import HumanMessage

# Add parent directory to path so we can import from src, config, utils
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.graph import (
    build_analyst_graph,
    build_interview_graph,
    build_research_graph
)
from src.state import Analyst

def print_section(title):
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)

def print_analysts(analysts, prefix="Analyst"):
    if not analysts:
        print(f"  No {prefix}s generated")
        return
    for i, analyst in enumerate(analysts):
        print(f"\n  [{i+1}] {analyst.name}")
        print(f"      Affiliation: {analyst.affiliation}")
        print(f"      Role: {analyst.role}")
        print(f"      Description: {analyst.description}")

def get_user_input(prompt, default=None, required=True):
    while True:
        if default:
            user_input = input(f"{prompt} [{default}]: ").strip()
            if not user_input:
                return default
        else:
            user_input = input(f"{prompt}: ").strip()
        
        if user_input or not required:
            return user_input
        print("  This field is required. Please enter a value.")

def get_int_input(prompt, default=None, min_val=1, max_val=10):
    while True:
        user_input = get_user_input(prompt, default=str(default) if default else None, required=True)
        try:
            val = int(user_input)
            if min_val <= val <= max_val:
                return val
            print(f"  Please enter a value between {min_val} and {max_val}")
        except ValueError:
            print("  Please enter a valid integer")

def test_analyst_generation():
    """Test Step 1: Generate Analysts with Human-in-the-Loop"""
    print_section("STEP 1: ANALYST GENERATION (Human-in-the-Loop)")
    
    # Get user inputs
    topic = get_user_input("Enter research topic", "Impact of Computer Vision on Automobile Industry in 2026")
    max_analysts = get_int_input("Number of analysts", default=2, min_val=1, max_val=5)
    thread_id = get_user_input("Thread ID", "test_analyst_001")
    
    print(f"\n  Topic: {topic}")
    print(f"  Max Analysts: {max_analysts}")
    print(f"  Thread ID: {thread_id}")
    print(f"\n  Building analyst graph...")
    
    analyst_graph = build_analyst_graph()
    thread = {"configurable": {"thread_id": thread_id}}
    
    print("  Generating analysts...")
    initial_analysts = []
    try:
        for event in analyst_graph.stream(
            {"topic": topic, "max_analysts": max_analysts},
            thread,
            stream_mode="values"
        ):
            analysts = event.get('analysts', '')
            if analysts:
                initial_analysts = analysts
        
        state = analyst_graph.get_state(thread)
        print(f"\n  Paused at node: {state.next}")
        print_analysts(initial_analysts, "Generated Analyst")
        
    except Exception as e:
        print(f"  ERROR during analyst generation: {e}")
        return None, None, None
    
    # Step 2: Human Feedback Loop
    while True:
        print_section("STEP 2: HUMAN FEEDBACK (Optional)")
        print("  Review the analysts above.")
        print("  Enter feedback to regenerate (e.g., 'Add an expert from Tesla')")
        print("  Press Enter without text to approve and continue")
        
        feedback = input("\n  Your feedback (or press Enter to approve): ").strip()
        
        if not feedback:
            print("  Analysts approved!")
            break
        
        print(f"\n  Applying feedback: '{feedback}'")
        try:
            analyst_graph.update_state(
                thread,
                {"human_analyst_feedback": feedback},
                as_node="human_feedback"
            )
            
            updated_analysts = []
            for event in analyst_graph.stream(None, thread, stream_mode="values"):
                analysts = event.get('analysts', '')
                if analysts:
                    updated_analysts = analysts
            
            print_analysts(updated_analysts, "Regenerated Analyst")
            
        except Exception as e:
            print(f"  ERROR during regeneration: {e}")
    
    # Final approval - set feedback to None to continue
    print("\n  Finalizing analyst panel...")
    try:
        analyst_graph.update_state(
            thread,
            {"human_analyst_feedback": None},
            as_node="human_feedback"
        )
        
        for event in analyst_graph.stream(None, thread, stream_mode="updates"):
            node_name = list(event.keys())[0]
            print(f"  Executed node: {node_name}")
        
        final_state = analyst_graph.get_state(thread)
        approved_analysts = final_state.values.get('analysts', [])
        
    except Exception as e:
        print(f"  ERROR during finalization: {e}")
        approved_analysts = initial_analysts
    
    print_section("APPROVED ANALYSTS")
    print_analysts(approved_analysts, "Approved Analyst")
    
    return approved_analysts, topic, max_analysts

def test_single_interview(approved_analysts, topic, max_turns):
    """Test Step 3: Single Interview"""
    if not approved_analysts:
        print("  No analysts available for interview")
        return None
    
    print_section("STEP 3: SINGLE INTERVIEW TEST")
    
    analyst = approved_analysts[0]
    print(f"  Interviewing: {analyst.name} ({analyst.role})")
    print(f"  Max turns: {max_turns}")
    
    interview_graph = build_interview_graph()
    thread = {"configurable": {"thread_id": "test_interview_001"}}
    
    messages = [HumanMessage(content=f"So you said you were writing an article on {topic}?")]
    
    try:
        result = interview_graph.invoke(
            {"analyst": analyst, "messages": messages, "max_num_turns": max_turns},
            thread
        )
        
        section = result.get('sections', [''])[0]
        print(f"\n  Interview section generated ({len(section)} chars):")
        print("  " + "-" * 50)
        print(f"  {section[:500]}...")
        print("  " + "-" * 50)
        
        return section
    except Exception as e:
        print(f"  ERROR during interview: {e}")
        import traceback
        traceback.print_exc()
        return None

def test_full_research_pipeline(approved_analysts, topic, max_analysts, max_turns):
    """Test Step 4: Full Research Pipeline (Map-Reduce)"""
    print_section("STEP 4: FULL RESEARCH PIPELINE (Map-Reduce)")
    
    if not approved_analysts:
        print("  No approved analysts available")
        return None
    
    print(f"  Topic: {topic}")
    print(f"  Analysts: {len(approved_analysts)}")
    print(f"  Max turns per interview: {max_turns}")
    print(f"  Running parallel interviews...")
    
    research_graph = build_research_graph(build_interview_graph())
    thread = {"configurable": {"thread_id": f"test_research_{datetime.now().strftime('%Y%m%d_%H%M%S')}"}}
    
    initial_state = {
        "topic": topic,
        "max_analysts": max_analysts,
        "max_num_turns": max_turns,
        "human_analyst_feedback": None,
        "analysts": approved_analysts,
        "sections": [],
        "introduction": "",
        "content": "",
        "conclusion": "",
        "final_report": "",
    }
    
    try:
        print("\n  Streaming research pipeline execution...")
        print("  " + "-" * 60)
        
        # First stream: runs create_analysts, pauses at human_feedback
        print("  -> Running create_analysts (will pause at human_feedback)...")
        for event in research_graph.stream(initial_state, thread, stream_mode="updates"):
            node_name = list(event.keys())[0]
            print(f"  -> Node executed: {node_name}")
        
        # Check if graph is paused at human_feedback
        state = research_graph.get_state(thread)
        if state.next and "human_feedback" in state.next:
            print("  -> Graph paused at human_feedback, resuming with no feedback...")
            research_graph.update_state(
                thread,
                {"human_analyst_feedback": None},
                as_node="human_feedback",
            )
            
            # Second stream: runs from human_feedback to completion
            print("  -> Resuming research pipeline (interviews + report)...")
            for event in research_graph.stream(None, thread, stream_mode="updates"):
                node_name = list(event.keys())[0]
                print(f"  -> Node executed: {node_name}")
                
                # Show progress for interview nodes
                if node_name == "conduct_interview":
                    interview_state = event[node_name]
                    if "sections" in interview_state and interview_state["sections"]:
                        section_preview = interview_state["sections"][-1][:100]
                        print(f"     Section generated: {section_preview}...")
        
        print("  " + "-" * 60)
        print("  Pipeline execution complete!")
        
        final_state = research_graph.get_state(thread)
        final_report = final_state.values.get('final_report', '')
        
        if final_report:
            print(f"\n  FINAL REPORT GENERATED ({len(final_report)} chars):")
            print("  " + "=" * 60)
            print(final_report[:2000] + ("..." if len(final_report) > 2000 else ""))
            print("  " + "=" * 60)
        else:
            print("\n  WARNING: No final report generated")
            print(f"  Final state keys: {list(final_state.values.keys())}")
        
        return final_report
        
    except Exception as e:
        print(f"  ERROR during research pipeline: {e}")
        import traceback
        traceback.print_exc()
        return None

def main():
    print("=" * 70)
    print("  RESEARCH ASSISTANT - AI WORKFLOW TEST")
    print("  Terminal-based Interactive Testing")
    print("=" * 70)
    print("\n  This script tests the AI workflow step by step.")
    print("  You will provide inputs at each stage via terminal.")
    
    # Step 1: Generate Analysts with Human Feedback
    approved_analysts, topic, max_analysts = test_analyst_generation()
    
    if not approved_analysts:
        print("\n  No analysts approved. Exiting.")
        return
    
    # Get max_turns for interviews
    max_turns = get_int_input("\n  Number of interview turns per analyst", default=2, min_val=1, max_val=5)
    
    # Step 2: Single Interview Test (optional)
    run_interview = get_user_input("\n  Run single interview test? (y/n)", "y").lower()
    if run_interview == 'y':
        test_single_interview(approved_analysts, topic, max_turns)
    
    # Step 3: Full Research Pipeline
    run_pipeline = get_user_input("\n  Run full research pipeline? (y/n)", "y").lower()
    if run_pipeline == 'y':
        final_report = test_full_research_pipeline(approved_analysts, topic, max_analysts, max_turns)
        
        if final_report:
            print_section("TEST COMPLETE")
            print("  Full research report generated successfully!")
            print(f"  Report length: {len(final_report)} characters")
        else:
            print_section("TEST COMPLETE WITH ISSUES")
            print("  Research pipeline completed but no report was generated.")
    else:
        print_section("TEST COMPLETE")
        print("  Analyst generation and feedback loop tested successfully.")

if __name__ == "__main__":
    main()