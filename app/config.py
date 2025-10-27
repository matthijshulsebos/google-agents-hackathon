import os
from typing import Dict, List

# Domains and their mapping to GCS buckets and Discovery Engine (Vertex AI Search) resources
# Adjust these via environment variables in Cloud Run or .env for local

DEFAULT_PROJECT = os.getenv("GOOGLE_CLOUD_PROJECT", os.getenv("PROJECT_ID", "your-project-id"))
DEFAULT_LOCATION = os.getenv("VERTEX_LOCATION", "global")

# Discovery Engine supports data stores and serving configs; provide per-domain identifiers
DomainConfig = Dict[str, str]

def _env(name: str, default: str = "") -> str:
    v = os.getenv(name)
    return v if v is not None and v != "" else default


def _env_any(names: List[str], default: str = "") -> str:
    for n in names:
        v = os.getenv(n)
        if v:
            return v
    return default


# Allow aliases for buckets to match earlier examples (FINANCE/LEGAL/HEALTHCARE)
DOMAINS: Dict[str, DomainConfig] = {
    "nursing": {
        "bucket": _env_any(["NURSING_BUCKET", "FINANCE_BUCKET"], "nursing-bucket"),
        # data_store/serving_config can be left blank; resources module will auto-create
        "data_store": _env("NURSING_DATA_STORE", ""),
        "serving_config": _env("NURSING_SERVING_CONFIG", ""),
    },
    "pharmacy": {
        "bucket": _env_any(["PHARMACY_BUCKET", "LEGAL_BUCKET"], "pharmacy-bucket"),
        "data_store": _env("PHARMACY_DATA_STORE", ""),
        "serving_config": _env("PHARMACY_SERVING_CONFIG", ""),
    },
    "po": {
        "bucket": _env_any(["PO_BUCKET", "HEALTHCARE_BUCKET"], "po-bucket"),
        "data_store": _env("PO_DATA_STORE", ""),
        "serving_config": _env("PO_SERVING_CONFIG", ""),
    },
}

# If a single BUCKET is provided, use it for all domains (hackathon convenience)
COMMON_BUCKET = _env("BUCKET", "")
if COMMON_BUCKET:
    for _d in DOMAINS.values():
        _d["bucket"] = COMMON_BUCKET

# Model configuration
MODEL_NAME = _env("GENAI_MODEL", "gemini-1.5-flash-002")
SA_EMAIL = _env("SERVICE_ACCOUNT_EMAIL", "")

# Chunking configuration
CHUNK_TOKENS = int(_env("CHUNK_TOKENS", "800"))
CHUNK_OVERLAP = int(_env("CHUNK_OVERLAP", "120"))
MAX_SOURCES = int(_env("MAX_SOURCES", "6"))
TOP_K_PER_DOMAIN = int(_env("TOP_K_PER_DOMAIN", "6"))

# Rule-based routing keywords per domain (simple POC; can be extended)
ROUTING_KEYWORDS: Dict[str, List[str]] = {
    "nursing": ["budget", "invoice", "expense", "revenue", "cost", "payroll", "capex", "procurement"],
    "pharmacy": ["contract", "policy", "compliance", "hipaa", "consent", "liability", "nda", "legal"],
    "po": ["protocol", "clinical", "patient", "triage", "treatment", "medication", "procedure", "guideline"],
}

# Cloud Run / API
API_HOST = _env("API_HOST", "0.0.0.0")
API_PORT = int(_env("API_PORT", "8080"))
