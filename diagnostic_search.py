#!/usr/bin/env python3
"""
Detailed diagnostic for Vertex AI Search.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.config import settings
from google.cloud import discoveryengine_v1 as discoveryengine
from google.api_core.client_options import ClientOptions

print("="*70)
print("DETAILED VERTEX AI SEARCH DIAGNOSTIC")
print("="*70)
print(f"\nProject: {settings.gcp_project_id}")
print(f"Location: {settings.gcp_location}")

datastore_id = settings.nursing_datastore_id  # Test with nursing
engine_id = f"{datastore_id}-app"

print(f"\nTesting Domain: Nursing")
print(f"Datastore ID: {datastore_id}")
print(f"Engine ID: {engine_id}")

# Initialize client
client_options = ClientOptions(
    api_endpoint=f"{settings.gcp_location}-discoveryengine.googleapis.com"
)
client = discoveryengine.SearchServiceClient(client_options=client_options)

# Construct serving config path
serving_config = f"projects/{settings.gcp_project_id}/locations/{settings.gcp_location}/collections/default_collection/engines/{engine_id}/servingConfigs/default_config"

print(f"\nServing config path:")
print(f"  {serving_config}")

# Try a search with detailed logging
query = "patient"
print(f"\nSearching for: '{query}'")
print("-"*70)

try:
    # Use basic search without Enterprise edition features
    request = discoveryengine.SearchRequest(
        serving_config=serving_config,
        query=query,
        page_size=5
    )
    
    print("Executing search request...")
    response = client.search(request)
    
    result_count = 0
    for result in response.results:
        result_count += 1
        print(f"\n✅ Result {result_count}:")
        print(f"   ID: {result.id}")
        
        # Check document structure
        doc = result.document
        print(f"   Document name: {doc.name}")
        
        # Check struct_data
        if hasattr(doc, 'struct_data') and doc.struct_data:
            struct = dict(doc.struct_data)
            print(f"   Struct data keys: {list(struct.keys())}")
            
            if 'text_content' in struct:
                content = struct['text_content']
                print(f"   Text content length: {len(content)} chars")
                print(f"   Content preview: {content[:200]}...")
            else:
                print(f"   ⚠️  No 'text_content' field in struct_data")
                print(f"   Available fields: {struct.keys()}")
        else:
            print(f"   ⚠️  No struct_data found")
        
        # Check derived_struct_data (snippets)
        if hasattr(doc, 'derived_struct_data') and doc.derived_struct_data:
            derived = dict(doc.derived_struct_data)
            print(f"   Derived data keys: {list(derived.keys())}")
            if 'snippets' in derived:
                print(f"   Has snippets: {len(derived['snippets'])}")
        
        print("-"*70)
    
    if result_count == 0:
        print("\n❌ No results returned")
        print("\nPossible causes:")
        print("  1. Documents are indexed but searchable content is missing")
        print("  2. The 'text_content' field might not be properly searchable")
        print("  3. The datastore content type configuration might be wrong")
        print("\nTo fix:")
        print("  • Check if documents have 'text_content' field in the console")
        print("  • Verify datastore is set to NO_CONTENT with struct_data indexing")
        print("  • May need to re-create datastore with correct schema")
    else:
        print(f"\n✅ Total results: {result_count}")
        
except Exception as e:
    print(f"\n❌ ERROR: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*70)
print("DIAGNOSTIC COMPLETE")
print("="*70)
