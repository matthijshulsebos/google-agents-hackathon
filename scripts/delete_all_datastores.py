#!/usr/bin/env python3
"""
Deletes all versions of the hospital datastores (v2, v3, etc.)
to ensure a completely clean slate before recreating them.
"""
from google.cloud import discoveryengine_v1
from google.api_core import exceptions
import time

PROJECT_ID = "qwiklabs-gcp-04-488d2ba9611d"
LOCATION = "eu"

# List all datastore prefixes to be deleted
datastore_prefixes = [
    "nursing-datastore",
    "pharmacy-datastore",
    "po-datastore"
]

client = discoveryengine_v1.DataStoreServiceClient(
    client_options={'api_endpoint': f'{LOCATION}-discoveryengine.googleapis.com'}
)

parent = f"projects/{PROJECT_ID}/locations/{LOCATION}/collections/default_collection"

print("=" * 80)
print("DELETING ALL EXISTING DATASTORES")
print("=" * 80)

try:
    # List all datastores in the project
    all_datastores = client.list_data_stores(parent=parent)
    
    datastores_to_delete = []
    for ds in all_datastores:
        for prefix in datastore_prefixes:
            if ds.display_name.startswith(prefix.replace('-', ' ').title()):
                datastores_to_delete.append(ds)
                break

    if not datastores_to_delete:
        print("✅ No matching datastores found to delete.")
    else:
        for ds in datastores_to_delete:
            print(f"\n🗑️  Deleting datastore: {ds.display_name} ({ds.name.split('/')[-1]})")
            try:
                operation = client.delete_data_store(name=ds.name)
                print("   ⏳ Waiting for deletion to complete...")
                operation.result(timeout=120)
                print(f"   ✅ Deleted successfully.")
            except exceptions.FailedPrecondition as e:
                print(f"   ❌ Error: {e.message}")
                print("      This can happen if there's an ongoing operation. Please wait and try again.")
            except Exception as e:
                print(f"   ❌ An unexpected error occurred: {e}")

except Exception as e:
    print(f"❌ Error listing datastores: {e}")

print("\n" + "=" * 80)
print("✅ Datastore cleanup complete.")
print("=" * 80)
