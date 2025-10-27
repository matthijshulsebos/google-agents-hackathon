#!/usr/bin/env python3
import os
import subprocess
from pathlib import Path


def _strip_quotes(val: str) -> str:
    if not val:
        return val
    if (val.startswith("'") and val.endswith("'")) or (val.startswith('"') and val.endswith('"')):
        return val[1:-1]
    return val


def load_env_file(path: str) -> None:
    """
    Minimal .env loader so deploy.py can consume variables without extra deps.
    - Supports KEY=VALUE lines.
    - Ignores comments and blank lines.
    - Does not override variables already present in the environment.
    - Trims surrounding single or double quotes from values.
    """
    p = Path(path)
    if not p.exists():
        return
    try:
        for line in p.read_text().splitlines():
            s = line.strip()
            if not s or s.startswith("#"):
                continue
            if "=" not in s:
                continue
            key, value = s.split("=", 1)
            key = key.strip()
            value = _strip_quotes(value.strip())
            if key and key not in os.environ:
                os.environ[key] = value
    except Exception as e:
        print(f"[WARN] Failed to read env file '{path}': {e}")


# Load .env before reading any variables. Allow override via ENV_FILE
ENV_FILE = os.getenv("ENV_FILE", ".env")
load_env_file(ENV_FILE)

SERVICE_NAME = os.getenv("SERVICE_NAME", "hospital-chat")
PROJECT = os.getenv("GOOGLE_CLOUD_PROJECT") or os.getenv("PROJECT_ID")

def _normalize_region(r: str) -> str:
    if not r:
        return r
    r = r.strip()
    alias = {
        "eu-west": "europe-west1",
        "europe-west": "europe-west1",
        "us-central": "us-central1",
        "us-east": "us-east1",
        "us-west": "us-west1",
        "asia-southeast": "asia-southeast1",
        "asia-east": "asia-east1",
        "europe-north": "europe-north1",
        "europe-central": "europe-central2",
    }
    if r in alias:
        fixed = alias[r]
        print(f"[INFO] REGION '{r}' corrected to '{fixed}'.")
        return fixed
    import re
    if not re.match(r"^[a-z]+-[a-z]+[0-9]$", r):
        raise SystemExit(
            f"Invalid REGION '{r}'. Use a value like us-central1, us-east1, europe-west1, asia-southeast1. "
            f"See: gcloud run regions list"
        )
    return r

REGION = _normalize_region(os.getenv("REGION", "us-central1"))
IMAGE = os.getenv("IMAGE", f"gcr.io/{PROJECT}/{SERVICE_NAME}")

if not PROJECT:
    raise SystemExit("Set GOOGLE_CLOUD_PROJECT or PROJECT_ID env var (can be placed in .env)")

# Build & Push
subprocess.check_call(["gcloud", "builds", "submit", "--tag", IMAGE])

# Deploy to Cloud Run
envs = [
    # Primary per-domain buckets
    "NURSING_BUCKET", "PHARMACY_BUCKET", "PO_BUCKET",
    # Backward-compatible aliases (if user still sets old names)
    "FINANCE_BUCKET", "LEGAL_BUCKET", "HEALTHCARE_BUCKET",
    # Data stores and serving configs are auto-provisioned; env overrides are no longer required
    "GENAI_MODEL", "TOP_K_PER_DOMAIN", "MAX_SOURCES", "CHUNK_TOKENS", "CHUNK_OVERLAP",
]

env_flags = []
for e in envs:
    v = os.getenv(e)
    if v is not None and v != "":
        env_flags += ["--set-env-vars", f"{e}={v}"]

subprocess.check_call([
    "gcloud", "run", "deploy", SERVICE_NAME,
    "--image", IMAGE,
    "--region", REGION,
    "--project", PROJECT,
    "--allow-unauthenticated",
    "--platform", "managed",
    "--port", "8080",
] + env_flags)
