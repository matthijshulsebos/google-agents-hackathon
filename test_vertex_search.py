#!/usr/bin/env python3
"""
Test script to verify ADK can access documents via Vertex AI Search.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.config import settings
from src.ingestion.vertex_search import VertexSearchRetriever

print("="*70)
print("TESTING VERTEX AI SEARCH ACCESS")
print("="*70)
print(f"\nProject: {settings.gcp_project_id}")
print(f"Location: {settings.gcp_location}")
print()

# Test each domain
domains = [
    ("Nursing", settings.nursing_datastore_id),
    ("Pharmacy", settings.pharmacy_datastore_id),
    ("HR/PO", settings.po_datastore_id)
]

for domain_name, datastore_id in domains:
    print(f"\n{'='*70}")
    print(f"Testing {domain_name} Domain")
    print(f"{'='*70}")
    print(f"Datastore ID: {datastore_id}")
    print(f"Expected Engine ID: {datastore_id}-app")
    
    if not datastore_id:
        print(f"❌ {domain_name} datastore ID not configured")
        continue
    
    try:
        # Initialize retriever
        retriever = VertexSearchRetriever(
            project_id=settings.gcp_project_id,
            location=settings.gcp_location,
            datastore_id=datastore_id
        )
        
        # Try a simple search
        test_query = "information"  # Generic query that should match something
        print(f"\nSearching for: '{test_query}'")
        
        results = retriever.search(test_query, top_k=3)
        
        if results:
            print(f"✅ SUCCESS! Found {len(results)} results")
            print(f"\nSample results:")
            for i, result in enumerate(results[:2], 1):
                content = result.get('content', 'No content')[:150]
                metadata = result.get('metadata', {})
                filename = metadata.get('filename', 'Unknown')
                print(f"\n  Result {i}:")
                print(f"    Source: {filename}")
                print(f"    Content preview: {content}...")
        else:
            print(f"⚠️  No results found")
            print(f"    This could mean:")
            print(f"    1. The datastore is empty (run ingestion)")
            print(f"    2. The search engine isn't ready yet (wait 5 min)")
            print(f"    3. The query didn't match any documents")
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
        error_str = str(e)
        if "404" in error_str:
            print(f"\n   Likely causes:")
            print(f"   • Search engine doesn't exist or isn't ready")
            print(f"   • Engine ID mismatch: expected '{datastore_id}-app'")
            print(f"   • Wait 5-10 minutes after creating search apps")
        elif "403" in error_str:
            print(f"\n   Permission issue - check IAM roles")
        elif "400" in error_str:
            print(f"\n   Bad request - check datastore configuration")

print(f"\n{'='*70}")
print("TEST COMPLETE")
print(f"{'='*70}\n")
