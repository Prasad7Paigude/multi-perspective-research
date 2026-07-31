"""
Backend API Test Script - Tests all FastAPI endpoints
======================================================
Tests:
1. /api/health - Health check
2. /api/research/init - Initialize research (generate analysts)
3. /api/research/feedback - Submit feedback for analyst regeneration
4. /api/research/approve - Approve analysts
5. /api/research/stream/{thread_id} - SSE stream for research execution
6. /api/research/result/{thread_id} - Get final report
"""

import asyncio
import aiohttp
import json
import time

BASE_URL = "http://localhost:8000"

async def test_health():
    """Test /api/health endpoint"""
    print("\n" + "=" * 60)
    print("TEST 1: /api/health")
    print("=" * 60)
    
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{BASE_URL}/api/health") as resp:
            data = await resp.json()
            print(f"Status: {resp.status}")
            print(f"Response: {json.dumps(data, indent=2)}")
            assert resp.status == 200
            assert data["status"] == "ok"
            print("✅ Health check PASSED")
            return True

async def test_init_research():
    """Test /api/research/init endpoint"""
    print("\n" + "=" * 60)
    print("TEST 2: /api/research/init")
    print("=" * 60)
    
    payload = {
        "topic": "Impact of Computer Vision on Automobile Industry in 2026",
        "max_analysts": 2,
        "max_turns": 2
    }
    
    async with aiohttp.ClientSession() as session:
        async with session.post(f"{BASE_URL}/api/research/init", json=payload) as resp:
            data = await resp.json()
            print(f"Status: {resp.status}")
            print(f"Response: {json.dumps(data, indent=2)}")
            assert resp.status == 200
            assert data["status"] == "analysts_pending"
            assert len(data["analysts"]) == 2
            print("✅ Research init PASSED")
            return data["thread_id"], data["analysts"]

async def test_feedback(thread_id, analysts):
    """Test /api/research/feedback endpoint"""
    print("\n" + "=" * 60)
    print("TEST 3: /api/research/feedback")
    print("=" * 60)
    
    # First, test with feedback to regenerate
    feedback_payload = {
        "thread_id": thread_id,
        "feedback": "Add an expert from Tesla's Autopilot team"
    }
    
    async with aiohttp.ClientSession() as session:
        async with session.post(f"{BASE_URL}/api/research/feedback", json=feedback_payload) as resp:
            data = await resp.json()
            print(f"Status: {resp.status}")
            print(f"Response: {json.dumps(data, indent=2)}")
            assert resp.status == 200
            assert data["status"] == "analysts_pending"
            assert len(data["analysts"]) == 2
            print("✅ Feedback with regeneration PASSED")
            regenerated_analysts = data["analysts"]
    
    # Now test with empty feedback (approval)
    approval_payload = {
        "thread_id": thread_id,
        "feedback": ""
    }
    
    async with aiohttp.ClientSession() as session:
        async with session.post(f"{BASE_URL}/api/research/feedback", json=approval_payload) as resp:
            data = await resp.json()
            print(f"Status: {resp.status}")
            print(f"Response: {json.dumps(data, indent=2)}")
            assert resp.status == 200
            assert data["status"] == "analysts_pending"
            print("✅ Feedback with approval PASSED")
            return regenerated_analysts

async def test_approve(thread_id):
    """Test /api/research/approve endpoint"""
    print("\n" + "=" * 60)
    print("TEST 4: /api/research/approve")
    print("=" * 60)
    
    payload = {"thread_id": thread_id}
    
    async with aiohttp.ClientSession() as session:
        async with session.post(f"{BASE_URL}/api/research/approve", json=payload) as resp:
            data = await resp.json()
            print(f"Status: {resp.status}")
            print(f"Response: {json.dumps(data, indent=2)}")
            assert resp.status == 200
            assert data["status"] == "interviewing"
            print("✅ Approve PASSED")
            return True

async def test_stream(thread_id, timeout=300):
    """Test /api/research/stream/{thread_id} endpoint"""
    print("\n" + "=" * 60)
    print("TEST 5: /api/research/stream/{thread_id}")
    print("=" * 60)
    
    url = f"{BASE_URL}/api/research/stream/{thread_id}"
    
    # Increase timeout for the whole request
    timeout_obj = aiohttp.ClientTimeout(total=timeout)
    
    async with aiohttp.ClientSession(timeout=timeout_obj) as session:
        async with session.get(url) as resp:
            print(f"Status: {resp.status}")
            assert resp.status == 200
            
            final_report = None
            sections = []
            event_count = 0
            start_time = time.time()
            
            print("  Reading SSE stream...")
            try:
                # Read raw bytes and parse SSE format properly
                buffer = b""
                async for chunk in resp.content.iter_any():
                    buffer += chunk
                    
                    # Process complete lines
                    while b'\n' in buffer:
                        line, buffer = buffer.split(b'\n', 1)
                        line = line.decode('utf-8').strip()
                        
                        if not line:
                            continue
                        
                        if line.startswith("data: "):
                            event_data = line[6:]  # Remove "data: " prefix
                            try:
                                event = json.loads(event_data)
                                event_count += 1
                                event_type = event.get("type")
                                payload = event.get("payload")
                                
                                if event_type == "status":
                                    print(f"  [{event_count}] Status: {payload}")
                                elif event_type == "section":
                                    sections.append(payload)
                                    print(f"  [{event_count}] Section received ({len(payload)} chars)")
                                elif event_type == "introduction":
                                    print(f"  [{event_count}] Introduction received ({len(payload)} chars)")
                                elif event_type == "report":
                                    print(f"  [{event_count}] Report content received ({len(payload)} chars)")
                                elif event_type == "conclusion":
                                    print(f"  [{event_count}] Conclusion received ({len(payload)} chars)")
                                elif event_type == "final_report":
                                    final_report = payload
                                    print(f"  [{event_count}] Final report received ({len(payload)} chars)")
                                elif event_type == "done":
                                    print(f"  [{event_count}] Stream complete")
                                    # Don't break - let the stream finish naturally
                                elif event_type == "error":
                                    print(f"  [{event_count}] ERROR: {payload}")
                                    return False, None
                                
                            except json.JSONDecodeError:
                                print(f"  [{event_count}] Failed to parse: {event_data[:100]}")
                    
                    # Timeout check
                    if time.time() - start_time > timeout:
                        print(f"  TIMEOUT after {timeout} seconds")
                        break
            
            except asyncio.TimeoutError:
                print(f"  Request timeout after {timeout} seconds")
            except Exception as e:
                print(f"  Stream reading error: {e}")
                import traceback
                traceback.print_exc()
            
            print(f"\n  Total events: {event_count}")
            print(f"  Sections received: {len(sections)}")
            print(f"  Final report: {'YES' if final_report else 'NO'}")
            
            if final_report:
                print(f"  Final report length: {len(final_report)} chars")
                print("✅ Stream PASSED")
                return True, final_report
            else:
                print("⚠️  Stream completed but no final report")
                return True, None

async def test_result(thread_id):
    """Test /api/research/result/{thread_id} endpoint"""
    print("\n" + "=" * 60)
    print("TEST 6: /api/research/result/{thread_id}")
    print("=" * 60)
    
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{BASE_URL}/api/research/result/{thread_id}") as resp:
            data = await resp.json()
            print(f"Status: {resp.status}")
            print(f"Status from response: {data.get('status')}")
            print(f"Report length: {len(data.get('report', '')) if data.get('report') else 0}")
            print(f"Sections count: {len(data.get('sections', []))}")
            assert resp.status == 200
            assert data["status"] == "complete"
            assert data["report"] is not None
            print("✅ Result endpoint PASSED")
            return data["report"]

async def main():
    print("=" * 60)
    print("BACKEND API TEST SUITE")
    print("=" * 60)
    
    try:
        # Test 1: Health check
        await test_health()
        
        # Test 2: Initialize research
        thread_id, analysts = await test_init_research()
        
        # Test 3: Submit feedback
        await test_feedback(thread_id, analysts)
        
        # Test 4: Approve analysts
        await test_approve(thread_id)
        
        # Test 5: Stream research execution
        success, final_report = await test_stream(thread_id, timeout=300)
        
        if not success:
            print("\n❌ Stream test failed")
            return
        
        # Test 6: Get final result
        await test_result(thread_id)
        
        print("\n" + "=" * 60)
        print("ALL BACKEND API TESTS PASSED! ✅")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())