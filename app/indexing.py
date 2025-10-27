from typing import List, Dict

from google.cloud import discoveryengine_v1 as de

from .resources import ensure_resources_for_domains
from .config import DOMAINS, DEFAULT_PROJECT
from .auth import setup_adc_from_env


def upload_chunks_to_data_store(data_store: str, records: List[Dict], location: str = "global") -> int:
    """
    Upload chunk records into a Discovery Engine (Vertex AI Search) data store as documents.
    Each record is a dict with keys: doc_id, content, metadata.
    Returns number of documents uploaded.
    """
    client = de.DocumentServiceClient()
    parent = data_store  # Expected full resource name

    docs = []
    for r in records:
        doc = de.Document(
            id=str(r.get("doc_id")),
            struct_data={
                "content": r.get("content", ""),
                **(r.get("metadata", {}) or {}),
            },
        )
        docs.append(doc)

    inline_source = de.ImportDocumentsRequest.InlineSource(documents=docs)
    request = de.ImportDocumentsRequest(
        parent=parent,
        inline_source=inline_source,
        reconciliation_mode=de.ImportDocumentsRequest.ReconciliationMode.INCREMENTAL,
    )
    operation = client.import_documents(request=request)
    result = operation.result()
    # result has metadata and errors; for simplicity, return count attempted
    return len(docs)


if __name__ == "__main__":
    import argparse
    from .ingestion import ingest_bucket

    parser = argparse.ArgumentParser(description="Ingest GCS bucket and upload to Vertex AI Search data store")
    parser.add_argument("domain", choices=list(DOMAINS.keys()))
    parser.add_argument("--prefix", default="", help="Optional prefix filter in bucket")
    parser.add_argument("--limit", type=int, default=None)
    args = parser.parse_args()

    # Ensure ADC from env (path, JSON, or base64) before calling any GCP APIs
    try:
        setup_adc_from_env()
    except Exception as e:
        print(f"[WARN] Failed to set up ADC from env: {e}")

    # Ensure resources exist and get full resource names
    ensured = ensure_resources_for_domains(DEFAULT_PROJECT, DOMAINS)
    cfg = ensured[args.domain]
    recs = ingest_bucket(cfg["bucket"], args.prefix, args.limit)
    print(f"Prepared {len(recs)} chunk records for domain {args.domain}")
    if not cfg.get("data_store"):
        raise SystemExit("Discovery Engine data store not available; ensure credentials and permissions are configured.")
    n = upload_chunks_to_data_store(cfg["data_store"], recs)
    print(f"Uploaded {n} documents to data store {cfg['data_store']}")
