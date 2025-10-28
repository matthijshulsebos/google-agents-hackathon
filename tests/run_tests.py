#!/usr/bin/env python3
"""
Test runner for Hospital AI Assistant
Run with: python tests/run_tests.py
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_search():
    """Test basic search functionality"""
    print("\n" + "="*70)
    print("TEST 1: Search Functionality")
    print("="*70)
    
    from src.ingestion.vertex_search import VertexSearchRetriever
    from src.config import settings
    
    try:
        retriever = VertexSearchRetriever(
            settings.gcp_project_id,
            settings.gcp_location,
            settings.nursing_datastore_id
        )
        results = retriever.search('blood glucose monitoring', top_k=1)
        
        if results and len(results) > 0:
            print("✅ PASS: Search returned results")
            print(f"   Found: {len(results)} result(s)")
            print(f"   Content length: {len(results[0].get('content', ''))} chars")
            return True
        else:
            print("❌ FAIL: No results returned")
            return False
    except Exception as e:
        print(f"❌ FAIL: {e}")
        return False

def test_adk_agent():
    """Test ADK agent with a simple query"""
    print("\n" + "="*70)
    print("TEST 2: ADK Agent Integration")
    print("="*70)
    
    from src.adk_agent.hospital_agent_vertex import chat_with_agent
    
    try:
        query = "Tell me about blood glucose monitoring"
        print(f"Query: {query}")
        result = chat_with_agent(query)
        
        if result and result.get('answer'):
            print("✅ PASS: Agent returned answer")
            print(f"   Answer length: {len(result['answer'])} chars")
            print(f"   Sources: {len(result.get('sources', []))} document(s)")
            return True
        else:
            print("❌ FAIL: No answer returned")
            return False
    except Exception as e:
        print(f"❌ FAIL: {e}")
        return False

def main():
    print("="*70)
    print("🧪 Hospital AI Assistant - Test Suite")
    print("="*70)
    
    results = []
    
    # Run tests
    results.append(("Search Functionality", test_search()))
    
    print("\n⏳ Waiting 5 seconds before next test...")
    import time
    time.sleep(5)
    
    results.append(("ADK Agent Integration", test_adk_agent()))
    
    # Summary
    print("\n" + "="*70)
    print("📊 Test Summary")
    print("="*70)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {test_name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed!")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())
