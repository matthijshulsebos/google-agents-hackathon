#!/usr/bin/env python3
"""
Forcefully deletes all datastores configured in the environment.
"""
import argparse
import logging
import sys
import os
import time

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from google.cloud import discoveryengine_v1 as discoveryengine
from google.api_core.client_options import ClientOptions
from google.api_core.exceptions import NotFound
from src.config import settings

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def delete_datastore(client: discoveryengine.DataStoreServiceClient, parent: str, datastore_id: str):
    """Deletes a datastore."""
    datastore_name = f"{parent}/dataStores/{datastore_id}"
    try:
        logger.info(f"Attempting to delete datastore: '{datastore_id}'...")
        request = discoveryengine.DeleteDataStoreRequest(name=datastore_name)
        operation = client.delete_data_store(request=request)
        # Wait for the operation to complete
        operation.result(timeout=120)
        logger.info(f"✅ Successfully deleted datastore: '{datastore_id}'.")
        return True
    except NotFound:
        logger.info(f"⏩ Datastore '{datastore_id}' not found. Skipping.")
        return True
    except Exception as e:
        logger.error(f"❌ Failed to delete datastore '{datastore_id}': {e}")
        return False

def cleanup_all_datastores():
    """Deletes all datastores defined in the settings."""
    project_id = settings.gcp_project_id
    location = settings.gcp_location

    if not project_id:
        logger.critical("GCP_PROJECT_ID is not set. Please configure your .env file.")
        return

    logger.info(f"Starting cleanup for project '{project_id}' in location '{location}'...")

    client_options = ClientOptions(api_endpoint=f"{location}-discoveryengine.googleapis.com")
    client = discoveryengine.DataStoreServiceClient(client_options=client_options)
    parent = f"projects/{project_id}/locations/{location}/collections/default_collection"

    # It's a good practice to have a small delay to avoid hitting API rate limits immediately.
    time.sleep(1)

    # List of datastores to delete from your .env file
    datastores_to_delete = [
        settings.nursing_datastore_id,
        settings.pharmacy_datastore_id,
        settings.po_datastore_id,
    ]
    
    # Also add the old v2 datastores to ensure they are cleaned up
    datastores_to_delete.extend([
        'nursing-datastore-v2',
        'pharmacy-datastore-v2',
        'po-datastore-v2'
    ])

    # Filter out empty strings and duplicates
    unique_datastores = sorted(list(set(filter(None, datastores_to_delete))))

    if not unique_datastores:
        logger.warning("No datastore IDs found in your .env file. Nothing to clean up.")
        return

    logger.info(f"Will attempt to delete the following datastores: {unique_datastores}")

    success_count = 0
    for datastore_id in unique_datastores:
        if delete_datastore(client, parent, datastore_id):
            success_count += 1
            # Wait a moment between deletions
            time.sleep(1)

    logger.info(f"Cleanup complete. {success_count}/{len(unique_datastores)} operations were successful (including skips).")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Cleanup script to delete Vertex AI Search datastores.")
    parser.add_argument(
        "--confirm",
        action="store_true",
        help="You must pass this flag to confirm you want to delete the datastores.",
    )
    args = parser.parse_args()

    if not args.confirm:
        logger.error("This is a destructive operation.")
        logger.error("Please review the script and run again with the --confirm flag to proceed.")
        sys.exit(1)
        
    cleanup_all_datastores()
