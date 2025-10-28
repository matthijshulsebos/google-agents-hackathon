#!/usr/bin/env python3
"""
Provisions the Vertex AI Search datastores with the correct configuration
and schema to enable full-text search on structured data.
"""
from google.cloud import discoveryengine_v1
from google.api_core import exceptions
import json

PROJECT_ID = "qwiklabs-gcp-04-488d2ba9611d"
LOCATION = "eu"

# Define the schema to make 'text_content' searchable
# This is the blueprint for our structured data.
SCHEMA = {
    "text_content": {
        "textual": True,
        "retrievable": True,
        "searchable": True,
        "indexable": True,
        "dynamicFacetable": False
    }
}

# Define the datastores to be created
DATASTORES = [
    {
        "id": "hospital-nursing-ds",
        "display_name": "Hospital Nursing Datastore",
    },
    {
        "id": "hospital-pharmacy-ds",
        "display_name": "Hospital Pharmacy Datastore",
    },
    {
        "id": "hospital-hr-ds",
        "display_name": "Hospital HR Datastore",
    }
]

client = discoveryengine_v1.DataStoreServiceClient(
    client_options={'api_endpoint': f'{LOCATION}-discoveryengine.googleapis.com'}
)

parent = f"projects/{PROJECT_ID}/locations/{LOCATION}/collections/default_collection"

print("=" * 80)
print("PROVISIONING VERTEX AI SEARCH DATASTORES")
print("=" * 80)

for config in DATASTORES:
    print(f"\n📦 Creating datastore: {config['display_name']}")
    
    # 1. Create the datastore with NO_CONTENT config
    datastore = discoveryengine_v1.DataStore(
        display_name=config['display_name'],
        industry_vertical=discoveryengine_v1.IndustryVertical.GENERIC,
        solution_types=[discoveryengine_v1.SolutionType.SOLUTION_TYPE_SEARCH],
        content_config=discoveryengine_v1.DataStore.ContentConfig.NO_CONTENT,
    )
    
    try:
        create_ds_request = discoveryengine_v1.CreateDataStoreRequest(
            parent=parent,
            data_store=datastore,
            data_store_id=config['id'],
        )
        
        ds_operation = client.create_data_store(request=create_ds_request)
        print("   - Waiting for datastore creation...")
        created_datastore = ds_operation.result(timeout=300)
        print(f"   - ✅ Datastore created: {created_datastore.name}")

        # 2. Update the schema for the newly created datastore
        schema_client = discoveryengine_v1.SchemaServiceClient(
            client_options={'api_endpoint': f'{LOCATION}-discoveryengine.googleapis.com'}
        )
        schema_name = f"{created_datastore.name}/schemas/default_schema"
        
        struct_schema = {'json_schema': json.dumps(SCHEMA)}
        
        update_schema_request = discoveryengine_v1.UpdateSchemaRequest(
            schema={'name': schema_name, 'struct_schema': struct_schema},
        )
        
        print("   - Updating schema to make 'text_content' searchable...")
        schema_operation = schema_client.update_schema(request=update_schema_request)
        schema_result = schema_operation.result(timeout=180)
        print(f"   - ✅ Schema updated successfully!")

    except exceptions.AlreadyExists:
        print(f"   ⚠️  Datastore '{config['id']}' already exists. Skipping creation.")
    except exceptions.FailedPrecondition as e:
        print(f"   ❌ Error: {e.message}")
        print("      This can happen if there's an ongoing operation. Please wait and try again.")
    except Exception as e:
        print(f"   ❌ An unexpected error occurred: {e}")

print("\n" + "=" * 80)
print("✅ Datastore provisioning complete.")
print("\nNext steps:")
print("1. Update .env file with the new datastore IDs.")
print("2. Run 'python scripts/ingest_documents.py --all' to populate them.")
print("3. Wait 10-15 minutes for indexing.")
print("4. Test with 'python test_search_simple.py'")
print("=" * 80)
