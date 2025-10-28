#!/usr/bin/env python3
"""
Script to list existing Vertex AI Search datastores.
"""
import sys
import os

# Add parent directory to path so we can import src modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from google.cloud import discoveryengine_v1 as discoveryengine
from google.api_core.client_options import ClientOptions
from src.config import settings

project_id = settings.gcp_project_id
location = settings.gcp_location

client_options = ClientOptions(api_endpoint=f"{location}-discoveryengine.googleapis.com")
client = discoveryengine.DataStoreServiceClient(client_options=client_options)

parent = f"projects/{project_id}/locations/{location}/collections/default_collection"

print(f"📊 Listing datastores in project: {project_id}")
print(f"📍 Location: {location}")
print(f"🔗 Parent: {parent}")
print()

try:
    datastores = list(client.list_data_stores(parent=parent))
    
    if datastores:
        print(f"✅ Found {len(datastores)} datastore(s):")
        print()
        for ds in datastores:
            datastore_id = ds.name.split("/")[-1]
            print(f"  📁 {ds.display_name}")
            print(f"     ID: {datastore_id}")
            print(f"     Full path: {ds.name}")
            print()
    else:
        print("❌ No datastores found")
        
except Exception as e:
    print(f"❌ Error: {e}")
    print()
    print("Possible reasons:")
    print("  - Discovery Engine API not enabled")
    print("  - Wrong location")
    print("  - Permission issues")
