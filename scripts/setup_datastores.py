#!/usr/bin/env python3
"""
Script to set up Vertex AI Search datastores and indexes.
"""
import argparse
import logging
from google.cloud import discoveryengine_v1 as discoveryengine
from google.api_core.client_options import ClientOptions
from src.config import settings, config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_datastore(project_id: str, location: str, datastore_id: str, display_name: str):
    """Create a Vertex AI Search datastore."""
    try:
        client_options = ClientOptions(
            api_endpoint=f"{location}-discoveryengine.googleapis.com"
        )
        client = discoveryengine.DataStoreServiceClient(client_options=client_options)
        
        parent = f"projects/{project_id}/locations/{location}/collections/default_collection"
        
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
        logger.info(f"Creating datastore {datastore_id}...")
        response = operation.result()
        logger.info(f"Datastore {datastore_id} created successfully!")
        return response
        
    except Exception as e:
        logger.error(f"Error creating datastore {datastore_id}: {e}")
        return None


def setup_all_datastores():
    """Set up all datastores for the system."""
    project_id = settings.gcp_project_id or config.get("gcp", {}).get("project_id", "")
    location = settings.gcp_location
    
    if not project_id:
        logger.error("GCP_PROJECT_ID not set!")
        return
    
    # Finance datastore
    finance_datastore_id = settings.finance_datastore_id or config.get("vertex_search", {}).get("finance", {}).get("datastore_id")
    if finance_datastore_id:
        logger.info("Setting up Finance datastore...")
        create_datastore(project_id, location, finance_datastore_id, "Finance Documents")
    
    # Legal datastore
    legal_datastore_id = settings.legal_datastore_id or config.get("vertex_search", {}).get("legal", {}).get("datastore_id")
    if legal_datastore_id:
        logger.info("Setting up Legal datastore...")
        create_datastore(project_id, location, legal_datastore_id, "Legal Documents")
    
    # Healthcare datastore
    healthcare_datastore_id = settings.healthcare_datastore_id or config.get("vertex_search", {}).get("healthcare", {}).get("datastore_id")
    if healthcare_datastore_id:
        logger.info("Setting up Healthcare datastore...")
        create_datastore(project_id, location, healthcare_datastore_id, "Healthcare Documents")
    
    logger.info("All datastores setup complete!")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Set up Vertex AI Search datastores")
    parser.add_argument("--all", action="store_true", help="Set up all datastores")
    parser.add_argument("--datastore-id", type=str, help="Specific datastore ID to create")
    parser.add_argument("--display-name", type=str, help="Display name for the datastore")
    
    args = parser.parse_args()
    
    if args.all:
        setup_all_datastores()
    elif args.datastore_id and args.display_name:
        project_id = settings.gcp_project_id
        location = settings.gcp_location
        create_datastore(project_id, location, args.datastore_id, args.display_name)
    else:
        parser.print_help()
