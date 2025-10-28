#!/usr/bin/env python3
"""
Script to set up Vertex AI Search Apps (Engines) for each datastore.
A Search App is required to actually query the datastores.
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
from google.api_core.exceptions import NotFound, AlreadyExists
from src.config import settings, config

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logging.getLogger('google').setLevel(logging.WARNING)
logger = logging.getLogger(__name__)


def create_search_app(project_id: str, location: str, datastore_id: str, engine_id: str, display_name: str):
    """Create a Vertex AI Search App (Engine) for a datastore."""
    try:
        client_options = ClientOptions(
            api_endpoint=f"{location}-discoveryengine.googleapis.com"
        )
        client = discoveryengine.EngineServiceClient(client_options=client_options)
        
        parent = f"projects/{project_id}/locations/{location}/collections/default_collection"
        datastore_path = f"{parent}/dataStores/{datastore_id}"
        
        # Check if engine already exists
        try:
            engine_name = f"{parent}/engines/{engine_id}"
            get_request = discoveryengine.GetEngineRequest(name=engine_name)
            existing_engine = client.get_engine(request=get_request)
            logger.info(f"✅ Search App '{engine_id}' already exists. Skipping creation.")
            return existing_engine
        except NotFound:
            pass  # Engine doesn't exist, proceed with creation
        
        # Create the engine
        engine = discoveryengine.Engine(
            display_name=display_name,
            solution_type=discoveryengine.SolutionType.SOLUTION_TYPE_SEARCH,
            industry_vertical=discoveryengine.IndustryVertical.GENERIC,
            data_store_ids=[datastore_id],
            search_engine_config=discoveryengine.Engine.SearchEngineConfig(
                search_tier=discoveryengine.SearchTier.SEARCH_TIER_STANDARD,
                search_add_ons=[discoveryengine.SearchAddOn.SEARCH_ADD_ON_LLM]
            )
        )
        
        request = discoveryengine.CreateEngineRequest(
            parent=parent,
            engine=engine,
            engine_id=engine_id
        )
        
        logger.info(f"Creating Search App '{engine_id}' for datastore '{datastore_id}'...")
        operation = client.create_engine(request=request)
        
        # Wait for operation to complete (can take a few minutes)
        logger.info(f"Waiting for Search App '{engine_id}' creation to complete...")
        response = operation.result(timeout=600)  # 10 minute timeout
        
        logger.info(f"✅ Search App '{engine_id}' created successfully!")
        return response
        
    except AlreadyExists:
        logger.info(f"✅ Search App '{engine_id}' already exists (race condition). Skipping.")
        return None
    except Exception as e:
        logger.error(f"❌ Error creating Search App '{engine_id}': {e}")
        return None


def setup_all_search_apps():
    """Set up Search Apps for all configured datastores."""
    project_id = settings.gcp_project_id or config.get("gcp", {}).get("project_id", "")
    location = settings.gcp_location
    
    if not project_id:
        logger.error("❌ GCP_PROJECT_ID not set!")
        return
    
    logger.info(f"Setting up Search Apps for project '{project_id}' in location '{location}'...")
    
    # Define the search apps to create
    search_apps = [
        {
            "datastore_id": settings.nursing_datastore_id,
            "engine_id": f"{settings.nursing_datastore_id}-app",
            "display_name": "Nursing Search App"
        },
        {
            "datastore_id": settings.pharmacy_datastore_id,
            "engine_id": f"{settings.pharmacy_datastore_id}-app",
            "display_name": "Pharmacy Search App"
        },
        {
            "datastore_id": settings.po_datastore_id,
            "engine_id": f"{settings.po_datastore_id}-app",
            "display_name": "HR Search App"
        }
    ]
    
    success_count = 0
    for app_config in search_apps:
        datastore_id = app_config["datastore_id"]
        engine_id = app_config["engine_id"]
        display_name = app_config["display_name"]
        
        if not datastore_id:
            logger.warning(f"⚠️  Datastore ID not configured for '{display_name}'. Skipping.")
            continue
        
        result = create_search_app(project_id, location, datastore_id, engine_id, display_name)
        if result is not None:
            success_count += 1
        
        # Small delay between creations
        time.sleep(2)
    
    logger.info(f"\n{'='*60}")
    logger.info(f"Search App setup complete! {success_count}/{len([a for a in search_apps if a['datastore_id']])} apps created/verified.")
    logger.info(f"{'='*60}\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Set up Vertex AI Search Apps (Engines)")
    parser.add_argument("--all", action="store_true", help="Set up all search apps")
    parser.add_argument("--datastore-id", type=str, help="Specific datastore ID")
    parser.add_argument("--engine-id", type=str, help="Engine ID for the search app")
    parser.add_argument("--display-name", type=str, help="Display name for the search app")
    
    args = parser.parse_args()
    
    if args.all:
        setup_all_search_apps()
    elif args.datastore_id and args.engine_id and args.display_name:
        project_id = settings.gcp_project_id
        location = settings.gcp_location
        create_search_app(project_id, location, args.datastore_id, args.engine_id, args.display_name)
    else:
        parser.print_help()
