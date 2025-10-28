#!/usr/bin/env python3
"""
Script to delete Vertex AI Search datastores.
"""
import argparse
import logging
from google.cloud import discoveryengine_v1 as discoveryengine
from google.api_core.client_options import ClientOptions
from src.config import settings, config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def delete_datastore(project_id: str, location: str, datastore_id: str):
    """Delete a Vertex AI Search datastore."""
    try:
        client_options = ClientOptions(
            api_endpoint=f"{location}-discoveryengine.googleapis.com"
        )
        client = discoveryengine.DataStoreServiceClient(client_options=client_options)
        
        name = f"projects/{project_id}/locations/{location}/collections/default_collection/dataStores/{datastore_id}"
        
        logger.info(f"Deleting datastore {datastore_id}...")
        operation = client.delete_data_store(name=name)
        logger.info(f"Datastore {datastore_id} deletion initiated (this may take a few minutes)...")
        return True
        
    except Exception as e:
        logger.error(f"Error deleting datastore {datastore_id}: {e}")
        return False


def delete_all_datastores():
    """Delete all datastores for the system."""
    project_id = settings.gcp_project_id or config.get("gcp", {}).get("project_id", "")
    location = settings.gcp_location
    
    if not project_id:
        logger.error("GCP_PROJECT_ID not set!")
        return
    
    # Nursing datastore
    nursing_datastore_id = settings.nursing_datastore_id or config.get("vertex_search", {}).get("nursing", {}).get("datastore_id")
    if nursing_datastore_id:
        delete_datastore(project_id, location, nursing_datastore_id)
    
    # Pharmacy datastore
    pharmacy_datastore_id = settings.pharmacy_datastore_id or config.get("vertex_search", {}).get("pharmacy", {}).get("datastore_id")
    if pharmacy_datastore_id:
        delete_datastore(project_id, location, pharmacy_datastore_id)
    
    # HR datastore
    po_datastore_id = settings.po_datastore_id or config.get("vertex_search", {}).get("po", {}).get("datastore_id")
    if po_datastore_id:
        delete_datastore(project_id, location, po_datastore_id)
    
    logger.info("All datastores deletion complete!")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Delete Vertex AI Search datastores")
    parser.add_argument("--all", action="store_true", help="Delete all datastores")
    parser.add_argument("--datastore-id", type=str, help="Specific datastore ID to delete")
    
    args = parser.parse_args()
    
    if args.all:
        delete_all_datastores()
    elif args.datastore_id:
        project_id = settings.gcp_project_id
        location = settings.gcp_location
        delete_datastore(project_id, location, args.datastore_id)
    else:
        parser.print_help()
