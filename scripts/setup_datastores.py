#!/usr/bin/env python3
"""
Script to set up Vertex AI Search datastores and indexes.
"""
import argparse
import logging
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from google.cloud import discoveryengine_v1 as discoveryengine
from google.api_core.client_options import ClientOptions
from google.api_core.exceptions import AlreadyExists, NotFound
from src.config import settings, config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_datastore(project_id: str, location: str, datastore_id: str, display_name: str, force_delete: bool = False):
    """Create a Vertex AI Search datastore, checking if it exists first."""
    client_options = ClientOptions(
        api_endpoint=f"{location}-discoveryengine.googleapis.com"
    )
    client = discoveryengine.DataStoreServiceClient(client_options=client_options)
    
    parent = f"projects/{project_id}/locations/{location}/collections/default_collection"

    if force_delete:
        delete_datastore(client, parent, datastore_id)

    # Check if datastore already exists
    existing_datastore = get_datastore(client, parent, datastore_id)
    if existing_datastore:
        logger.warning(f"Datastore '{datastore_id}' already exists. Skipping creation.")
        # Optional: Check if config matches
        if existing_datastore.content_config != discoveryengine.DataStore.ContentConfig.NO_CONTENT:
            logger.error(f"Datastore '{datastore_id}' has wrong config. It should be NO_CONTENT.")
            logger.error("Please delete it manually or use the --force-delete flag.")
        return existing_datastore

    try:
        datastore = discoveryengine.DataStore(
            display_name=display_name,
            industry_vertical=discoveryengine.IndustryVertical.GENERIC,
            solution_types=[discoveryengine.SolutionType.SOLUTION_TYPE_SEARCH],
            content_config=discoveryengine.DataStore.ContentConfig.CONTENT_REQUIRED
        )
        
        request = discoveryengine.CreateDataStoreRequest(
            parent=parent,
            data_store=datastore,
            data_store_id=datastore_id
        )
        
        operation = client.create_data_store(request=request)
        logger.info(f"Creating datastore '{datastore_id}'...")
        response = operation.result()
        logger.info(f"Datastore '{datastore_id}' created successfully!")
        return response
        
    except AlreadyExists:
        logger.warning(f"Datastore '{datastore_id}' was created by a parallel process. Skipping.")
        return get_datastore(client, parent, datastore_id)
    except Exception as e:
        logger.error(f"Error creating datastore {datastore_id}: {e}")
        return None


def setup_all_datastores(force_delete: bool = False):
    """Set up all datastores for the system."""
    project_id = settings.gcp_project_id or config.get("gcp", {}).get("project_id", "")
    location = settings.gcp_location
    
    if not project_id:
        logger.error("GCP_PROJECT_ID not set!")
        return
    
    datastores_to_create = [
        (settings.nursing_datastore_id, "Nursing Documents v3"),
        (settings.pharmacy_datastore_id, "Pharmacy Documents v3"),
        (settings.po_datastore_id, "HR Documents v3")
    ]

    for datastore_id, display_name in datastores_to_create:
        if datastore_id:
            logger.info(f"Setting up datastore: {datastore_id}")
            create_datastore(project_id, location, datastore_id, display_name, force_delete)
        else:
            logger.warning("A datastore ID is not configured. Skipping.")
    
    logger.info("All datastores setup process complete!")


def get_datastore(client: discoveryengine.DataStoreServiceClient, parent: str, datastore_id: str):
    """Check if a datastore exists."""
    try:
        request = discoveryengine.GetDataStoreRequest(
            name=f"{parent}/dataStores/{datastore_id}"
        )
        return client.get_data_store(request=request)
    except NotFound:
        return None


def delete_datastore(client: discoveryengine.DataStoreServiceClient, parent: str, datastore_id: str):
    """Delete a datastore."""
    try:
        request = discoveryengine.DeleteDataStoreRequest(
            name=f"{parent}/dataStores/{datastore_id}"
        )
        operation = client.delete_data_store(request=request)
        logger.info(f"Deleting datastore {datastore_id}...")
        operation.result()
        logger.info(f"Datastore {datastore_id} deleted successfully!")
        return True
    except NotFound:
        logger.info(f"Datastore {datastore_id} not found, skipping deletion.")
        return True
    except Exception as e:
        logger.error(f"Error deleting datastore {datastore_id}: {e}")
        return False


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Set up Vertex AI Search datastores")
    parser.add_argument("--all", action="store_true", help="Set up all datastores")
    parser.add_argument("--datastore-id", type=str, help="Specific datastore ID to create")
    parser.add_argument("--display-name", type=str, help="Display name for the datastore")
    
    parser.add_argument("--force-delete", action="store_true", help="Force delete existing datastores before creation")
    
    args = parser.parse_args()
    
    if args.all:
        setup_all_datastores(force_delete=args.force_delete)
    elif args.datastore_id and args.display_name:
        project_id = settings.gcp_project_id
        location = settings.gcp_location
        create_datastore(project_id, location, args.datastore_id, args.display_name, force_delete=args.force_delete)
    else:
        parser.print_help()
