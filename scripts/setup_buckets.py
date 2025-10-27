#!/usr/bin/env python3
"""
Script to create GCS buckets for each domain.
"""
import argparse
import logging
from google.cloud import storage
from src.config import settings, config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_bucket(bucket_name: str, project_id: str, location: str = "US"):
    """Create a GCS bucket."""
    try:
        storage_client = storage.Client(project=project_id)
        
        # Check if bucket already exists
        try:
            bucket = storage_client.get_bucket(bucket_name)
            logger.info(f"Bucket {bucket_name} already exists")
            return bucket
        except Exception:
            pass
        
        # Create bucket
        bucket = storage_client.bucket(bucket_name)
        bucket.storage_class = "STANDARD"
        bucket = storage_client.create_bucket(bucket, location=location)
        
        logger.info(f"Bucket {bucket_name} created successfully in {location}")
        return bucket
        
    except Exception as e:
        logger.error(f"Error creating bucket {bucket_name}: {e}")
        return None


def setup_all_buckets():
    """Set up all buckets for the system."""
    project_id = settings.gcp_project_id or config.get("gcp", {}).get("project_id", "")
    location = settings.gcp_location
    
    if not project_id:
        logger.error("GCP_PROJECT_ID not set!")
        return
    
    buckets = [
        settings.finance_bucket,
        settings.legal_bucket,
        settings.healthcare_bucket
    ]
    
    for bucket_name in buckets:
        if bucket_name:
            logger.info(f"Creating bucket {bucket_name}...")
            create_bucket(bucket_name, project_id, location)
    
    logger.info("All buckets setup complete!")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Create GCS buckets for document storage")
    parser.add_argument("--all", action="store_true", help="Create all buckets")
    parser.add_argument("--bucket-name", type=str, help="Specific bucket name to create")
    
    args = parser.parse_args()
    
    if args.all:
        setup_all_buckets()
    elif args.bucket_name:
        project_id = settings.gcp_project_id
        location = settings.gcp_location
        create_bucket(args.bucket_name, project_id, location)
    else:
        parser.print_help()
