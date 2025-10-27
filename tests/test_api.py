#!/usr/bin/env python3
"""
Test script for the hospital chat system.
"""
import requests
import json
import time
from typing import Dict, Any

# Configuration
BASE_URL = "http://localhost:8080"  # Change to your deployed URL


def test_health_check():
    """Test the health check endpoint."""
    print("\n=== Testing Health Check ===")
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    assert response.status_code == 200
    print("✓ Health check passed")


def test_list_domains():
    """Test listing available domains."""
    print("\n=== Testing Domain Listing ===")
    response = requests.get(f"{BASE_URL}/domains")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    assert response.status_code == 200
    print("✓ Domain listing passed")


def test_single_domain_query():
    """Test a query targeting a single domain."""
    print("\n=== Testing Single Domain Query (Finance) ===")
    
    payload = {
        "query": "What is the hospital budget for medical equipment?",
        "routing_strategy": "keyword",
        "top_k": 5
    }
    
    response = requests.post(f"{BASE_URL}/chat", json=payload)
    print(f"Status: {response.status_code}")
    result = response.json()
    print(f"Query: {result['query']}")
    print(f"Domains Queried: {result['domains_queried']}")
    print(f"Total Results: {result['total_results']}")
    print(f"Answer: {result['answer'][:200]}...")
    print(f"Sources: {len(result['sources'])} documents")
    
    assert response.status_code == 200
    print("✓ Single domain query passed")
    return result['conversation_id']


def test_multi_domain_query():
    """Test a query that spans multiple domains."""
    print("\n=== Testing Multi-Domain Query ===")
    
    payload = {
        "query": "What are the legal compliance requirements and financial costs for patient data storage?",
        "routing_strategy": "keyword",
        "top_k": 3
    }
    
    response = requests.post(f"{BASE_URL}/chat", json=payload)
    print(f"Status: {response.status_code}")
    result = response.json()
    print(f"Query: {result['query']}")
    print(f"Domains Queried: {result['domains_queried']}")
    print(f"Total Results: {result['total_results']}")
    print(f"Answer: {result['answer'][:200]}...")
    print(f"Sources from domains: {set(s['domain'] for s in result['sources'])}")
    
    assert response.status_code == 200
    assert len(result['domains_queried']) >= 2, "Should query multiple domains"
    print("✓ Multi-domain query passed")


def test_multi_turn_conversation():
    """Test multi-turn conversation with context."""
    print("\n=== Testing Multi-Turn Conversation ===")
    
    # First turn
    payload1 = {
        "query": "What are the standard patient intake procedures?",
        "routing_strategy": "keyword",
        "top_k": 3
    }
    
    response1 = requests.post(f"{BASE_URL}/chat", json=payload1)
    result1 = response1.json()
    conversation_id = result1['conversation_id']
    
    print(f"\nTurn 1:")
    print(f"Query: {result1['query']}")
    print(f"Answer: {result1['answer'][:150]}...")
    print(f"Conversation ID: {conversation_id}")
    
    time.sleep(1)
    
    # Second turn (with context)
    payload2 = {
        "query": "What documents are required for that?",
        "conversation_id": conversation_id,
        "routing_strategy": "keyword",
        "top_k": 3
    }
    
    response2 = requests.post(f"{BASE_URL}/chat", json=payload2)
    result2 = response2.json()
    
    print(f"\nTurn 2:")
    print(f"Query: {result2['query']}")
    print(f"Answer: {result2['answer'][:150]}...")
    
    assert response1.status_code == 200
    assert response2.status_code == 200
    assert result2['conversation_id'] == conversation_id
    print("✓ Multi-turn conversation passed")
    
    return conversation_id


def test_all_domains_query():
    """Test querying all domains."""
    print("\n=== Testing All Domains Query ===")
    
    payload = {
        "query": "What policies and procedures should all staff follow?",
        "routing_strategy": "all",
        "top_k": 2
    }
    
    response = requests.post(f"{BASE_URL}/chat", json=payload)
    print(f"Status: {response.status_code}")
    result = response.json()
    print(f"Query: {result['query']}")
    print(f"Domains Queried: {result['domains_queried']}")
    print(f"Total Results: {result['total_results']}")
    print(f"Answer: {result['answer'][:200]}...")
    
    assert response.status_code == 200
    print("✓ All domains query passed")


def test_clear_conversation(conversation_id: str):
    """Test clearing conversation history."""
    print("\n=== Testing Clear Conversation ===")
    
    response = requests.post(f"{BASE_URL}/chat/clear", params={"conversation_id": conversation_id})
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    assert response.status_code == 200
    print("✓ Clear conversation passed")


def test_no_results_query():
    """Test handling of queries with no results."""
    print("\n=== Testing No Results Query ===")
    
    payload = {
        "query": "What is the weather forecast for Mars next week?",
        "routing_strategy": "keyword",
        "top_k": 5
    }
    
    response = requests.post(f"{BASE_URL}/chat", json=payload)
    print(f"Status: {response.status_code}")
    result = response.json()
    print(f"Query: {result['query']}")
    print(f"Total Results: {result['total_results']}")
    print(f"Answer: {result['answer'][:200]}...")
    
    assert response.status_code == 200
    print("✓ No results query passed")


def run_all_tests():
    """Run all tests."""
    print("=" * 60)
    print("Hospital Chat System - Integration Tests")
    print("=" * 60)
    
    try:
        # Basic tests
        test_health_check()
        test_list_domains()
        
        # Query tests
        conv_id = test_single_domain_query()
        test_multi_domain_query()
        conv_id = test_multi_turn_conversation()
        test_all_domains_query()
        test_no_results_query()
        
        # Cleanup
        test_clear_conversation(conv_id)
        
        print("\n" + "=" * 60)
        print("✓ All tests passed!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n✗ Test failed with error: {e}")
        raise


if __name__ == "__main__":
    run_all_tests()
