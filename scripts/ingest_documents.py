#!/usr/bin/env python3
"""
Script to ingest documents from GCS buckets into Vertex AI Search.
"""
import argparse
import logging
from src.config import settings, config
from src.ingestion.document_processor import DocumentProcessor
from src.ingestion.vertex_search import VertexSearchIndexer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def ingest_bucket(domain: str, bucket_name: str, datastore_id: str):
    """Ingest documents from a bucket into Vertex AI Search."""
    project_id = settings.gcp_project_id or config.get("gcp", {}).get("project_id", "")
    location = settings.gcp_location
    
    if not project_id:
        logger.error("GCP_PROJECT_ID not set!")
        return
    
    logger.info(f"Starting ingestion for {domain} domain from bucket {bucket_name}")
    
    # Initialize processor
    chunk_config = config.get("chunking", {})
    processor = DocumentProcessor(
        project_id=project_id,
        chunk_size=chunk_config.get("chunk_size", 800),
        chunk_overlap=chunk_config.get("chunk_overlap", 200)
    )
    
    # Process bucket
    logger.info(f"Processing documents from bucket {bucket_name}...")
    documents = processor.process_bucket(bucket_name, domain)
    logger.info(f"Processed {len(documents)} document chunks")
    
    if not documents:
        logger.warning("No documents to index!")
        return
    
    # Initialize indexer
    indexer = VertexSearchIndexer(
        project_id=project_id,
        location=location,
        datastore_id=datastore_id
    )
    
    # Index documents
    logger.info(f"Indexing {len(documents)} chunks into datastore {datastore_id}...")
    success = indexer.index_documents(documents)
    
    if success:
        logger.info(f"Successfully ingested {domain} domain documents!")
    else:
        logger.error(f"Failed to ingest {domain} domain documents")


def ingest_all_domains():
    """Ingest documents from all domains."""
    domains = [
        ("finance", settings.finance_bucket, settings.finance_datastore_id),
        ("legal", settings.legal_bucket, settings.legal_datastore_id),
        ("healthcare", settings.healthcare_bucket, settings.healthcare_datastore_id)
    ]
    
    for domain, bucket, datastore_id in domains:
        if bucket and datastore_id:
            try:
                ingest_bucket(domain, bucket, datastore_id)
            except Exception as e:
                logger.error(f"Error ingesting {domain} domain: {e}")
        else:
            logger.warning(f"Skipping {domain} domain - bucket or datastore_id not configured")
    
    logger.info("All domains ingestion complete!")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Ingest documents from GCS to Vertex AI Search")
    parser.add_argument("--all", action="store_true", help="Ingest all domains")
    parser.add_argument("--domain", type=str, help="Domain name (finance, legal, healthcare)")
    parser.add_argument("--bucket", type=str, help="GCS bucket name")
    parser.add_argument("--datastore-id", type=str, help="Vertex AI Search datastore ID")
    
    args = parser.parse_args()
    
    if args.all:
        ingest_all_domains()
    elif args.domain and args.bucket and args.datastore_id:
        ingest_bucket(args.domain, args.bucket, args.datastore_id)
    else:
        parser.print_help()
