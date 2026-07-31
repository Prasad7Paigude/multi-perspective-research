"""
Frontend Integration Test Script
=================================
Tests the frontend-backend integration by:
1. Verifying API endpoints are accessible
2. Testing the full flow: init -> feedback -> approve -> stream -> result
3. Validating data structures match frontend expectations
"""

import asyncio
import aiohttp
import json

BASE_URL = "http://localhost:8000"

async def test_basic_connectivity():
    """Test that the API is reachable"""
    print("\n" + "=" * 60)
    print("TEST: Basic API Connectivity")
    print("=" * 60)
    
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{BASE_URL}/api/health") as resp:
            data = await resp.json()
            print(f"Status: {resp.status}")
            print(f"Response: {data}")
            assert resp.status == 200
            assert data["status"] == "ok"
            print("✅ Basic connectivity PASSED")

async def test_frontend_flow():
    """Test the complete frontend flow"""
    print("\n" + "=" * 60)
    print("TEST: Complete Frontend Flow")
    print("=" * 60)
    
    async with aiohttp.ClientSession() as session:
        # Step 1: Initialize research
        print("\n1. POST /api/research/init")
        payload = {
            "topic": "Impact of Computer Vision on Automobile Industry in 2026",
            "max_analysts": 2,
            "max_turns": 2
        }
        async with session.post(f"{BASE_URL}/api/research/init", json=payload) as resp:
            data = await resp.json()
            print(f"   Status: {resp.status}")
            print(f"   Thread ID: {data.get('thread_id')}")
            print(f"   Analysts count: {len(data.get('analysts', []))}")
            assert resp.status == 200
            assert data["status"] == "analysts_pending"
            assert len(data["analysts"]) == 2
            thread_id = data["thread_id"]
            print("   ✅ Init PASSED")
        
        # Step 2: Submit feedback (optional)
        print("\n2. POST /api/research/feedback (with feedback)")
        feedback_payload = {
            "thread_id": thread_id,
            "feedback": "Add an expert from Tesla's Autopilot team"
        }
        async with session.post(f"{BASE_URL}/api/research/feedback", json=feedback_payload) as resp:
            data = await resp.json()
            print(f"   Status: {resp.status}")
            print(f"   Analysts count: {len(data.get('analysts', []))}")
            assert resp.status == 200
            assert data["status"] == "analysts_pending"
            print("   ✅ Feedback with regeneration PASSED")
        
        # Step 3: Approve analysts (empty feedback)
        print("\n3. POST /api/research/feedback (empty - approve)")
        approval_payload = {"thread_id": thread_id, "feedback": ""}
        async with session.post(f"{BASE_URL}/api/research/feedback", json=approval_payload) as resp:
            data = await resp.json()
            print(f"   Status: {resp.status}")
            print(f"   Analysts count: {len(data.get('analysts', []))}")
            assert resp.status == 200
            assert data["status"] == "analysts_pending"
            print("   ✅ Feedback approval PASSED")
        
        # Step 4: Approve analysts
        print("\n4. POST /api/research/approve")
        approve_payload = {"thread_id": thread_id}
        async with session.post(f"{BASE_URL}/api/research/approve", json=approve_payload) as resp:
            data = await resp.json()
            print(f"   Status: {resp.status}")
            print(f"   Status from response: {data.get('status')}")
            assert resp.status == 200
            assert data["status"] == "interviewing"
            print("   ✅ Approve PASSED")
        
        # Step 5: Stream research
        print("\n5. GET /api/research/stream/{thread_id}")
        url = f"{BASE_URL}/api/research/stream/{thread_id}"
        timeout_obj = aiohttp.ClientTimeout(total=180)
        
        async with session.get(url, timeout=timeout_obj) as resp:
            print(f"   Status: {resp.status}")
            assert resp.status == 200
            
            final_report = None
            sections = []
            event_count = 0
            
            try:
                buffer = b""
                async for chunk in resp.content.iter_any():
                    buffer += chunk
                    
                    while b'\n' in buffer:
                        line, buffer = buffer.split(b'\n', 1)
                        line = line.decode('utf-8').strip()
                        
                        if not line:
                            continue
                        
                        if line.startswith("data: "):
                            event_data = line[6:]
                            try:
                                event = json.loads(event_data)
                                event_count += 1
                                event_type = event.get("type")
                                payload = event.get("payload")
                                
                                if event_type == "status":
                                    print(f"   [{event_count}] Status: {payload}")
                                elif event_type == "section":
                                    sections.append(payload)
                                    print(f"   [{event_count}] Section received ({len(payload)} chars)")
                                elif event_type == "final_report":
                                    final_report = payload
                                    print(f"   [{event_count}] Final report received ({len(payload)} chars)")
                                elif event_type == "done":
                                    print(f"   [{event_count}] Stream complete")
                                elif event_type == "error":
                                    print(f"   [{event_count}] ERROR: {payload}")
                                    raise Exception(f"Stream error: {payload}")
                            except json.JSONDecodeError:
                                print(f"   [{event_count}] Failed to parse: {event_data[:100]}")
            
            except asyncio.TimeoutError:
                print("   Request timeout")
                raise
            
            print(f"\n   Total events: {event_count}")
            print(f"   Sections received: {len(sections)}")
            print(f"   Final report: {'YES' if final_report else 'NO'}")
            
            if final_report:
                print(f"   Final report length: {len(final_report)} chars")
                print("   ✅ Stream PASSED")
            else:
                print("   ❌ Stream FAILED - No final report")
                raise AssertionError("No final report received")
        
        # Step 6: Get result
        print("\n6. GET /api/research/result/{thread_id}")
        async with session.get(f"{BASE_URL}/api/research/result/{thread_id}") as resp:
            data = await resp.json()
            print(f"   Status: {resp.status}")
            print(f"   Status from response: {data.get('status')}")
            print(f"   Report length: {len(data.get('report', '')) if data.get('report') else 0}")
            print(f"   Sections count: {len(data.get('sections', []))}")
            assert resp.status == 200
            assert data["status"] == "complete"
            assert data["report"] is not None
            assert len(data["report"]) > 0
            print("   ✅ Result endpoint PASSED")
        
        print("\n" + "=" * 60)
        print("COMPLETE FRONTEND FLOW TEST PASSED! ✅")
        print("=" * 60)

async def test_data_structures():
    """Test that data structures match frontend expectations"""
    print("\n" + "=" * 60)
    print("TEST: Data Structure Validation")
    print("=" * 60)
    
    async with aiohttp.ClientSession() as session:
        # Initialize
        payload = {"topic": "Test Topic", "max_analysts": 1, "max_turns": 1}
        async with session.post(f"{BASE_URL}/api/research/init", json=payload) as resp:
            data = await resp.json()
            
            # Validate Analyst structure
            analyst = data["analysts"][0]
            required_fields = ["name", "affiliation", "role", "description"]
            for field in required_fields:
                assert field in analyst, f"Missing field: {field}"
            print("   ✅ Analyst structure valid")
            
            # Validate ResearchStatusResponse
            assert "thread_id" in data
            assert "status" in data
            assert "analysts" in data
            print("   ✅ ResearchStatusResponse structure valid")
            
            thread_id = data["thread_id"]
            
            # Test feedback flow
            await session.post(f"{BASE_URL}/api/research/feedback", json={
                "thread_id": thread_id, "feedback": "Test feedback"
            })
            await session.post(f"{BASE_URL}/api/research/feedback", json={
                "thread_id": thread_id, "feedback": ""
            })
            await session.post(f"{BASE_URL}/api/research/approve", json={"thread_id": thread_id})
            
            # Test result structure (without waiting for full stream)
            async with session.get(f"{BASE_URL}/api/research/result/{thread_id}") as resp:
                data = await resp.json()
                # When status is not complete, report and sections may be None/empty
                required_fields = ["thread_id", "status"]
                for field in required_fields:
                    assert field in data, f"Missing field: {field}"
                # When complete, should have report and sections
                if data["status"] == "complete":
                    assert "report" in data
                    assert "sections" in data
                print("   ✅ Result structure valid")

async def main():
    print("=" * 60)
    print("FRONTEND INTEGRATION TEST SUITE")
    print("=" * 60)
    
    try:
        await test_basic_connectivity()
        await test_data_structures()
        await test_frontend_flow()
        
        print("\n" + "=" * 60)
        print("ALL FRONTEND INTEGRATION TESTS PASSED! ✅")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    result = asyncio.run(main())
    exit(0 if result else 1)