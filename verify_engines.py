#!/usr/bin/env python3
"""Quick script to verify engine configuration."""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.config import settings
from google.cloud import discoveryengine_v1 as discoveryengine
from google.api_core.client_options import ClientOptions

print("Configuration Check:")
print(f"Project: {settings.gcp_project_id}")
print(f"Location: {settings.gcp_location}")
print(f"\nDatastores:")
print(f"  Nursing: {settings.nursing_datastore_id}")
print(f"  Pharmacy: {settings.pharmacy_datastore_id}")
print(f"  PO: {settings.po_datastore_id}")
print(f"\nExpected Engines:")
print(f"  Nursing: {settings.nursing_datastore_id}-app")
print(f"  Pharmacy: {settings.pharmacy_datastore_id}-app")
print(f"  PO: {settings.po_datastore_id}-app")

# Try to list engines
print(f"\n{'='*60}")
print("Checking if engines exist...")
print(f"{'='*60}\n")

try:
    client_options = ClientOptions(
        api_endpoint=f"{settings.gcp_location}-discoveryengine.googleapis.com"
    )
    client = discoveryengine.EngineServiceClient(client_options=client_options)
    parent = f"projects/{settings.gcp_project_id}/locations/{settings.gcp_location}/collections/default_collection"
    
    engines = list(client.list_engines(parent=parent))
    
    if engines:
        print(f"✅ Found {len(engines)} engine(s):")
        for engine in engines:
            engine_id = engine.name.split("/")[-1]
            print(f"  - {engine.display_name} (ID: {engine_id})")
            print(f"    State: {engine.create_time}")
    else:
        print("❌ No engines found")
        
except Exception as e:
    print(f"❌ Error listing engines: {e}")
