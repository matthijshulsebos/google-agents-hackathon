import io
import os
from typing import Dict, List, Optional, Iterable, Tuple

import pdfplumber
import docx
import pandas as pd
from bs4 import BeautifulSoup
from google.cloud import storage

from .config import CHUNK_TOKENS, CHUNK_OVERLAP


def read_gcs_file(bucket: str, blob_name: str) -> bytes:
    client = storage.Client()
    bucket_obj = client.bucket(bucket)
    blob = bucket_obj.blob(blob_name)
    return blob.download_as_bytes()


def list_gcs_files(bucket: str, prefix: str = "") -> List[str]:
    client = storage.Client()
    bucket_obj = client.bucket(bucket)
    return [b.name for b in client.list_blobs(bucket_obj, prefix=prefix)]


def detect_type(filename: str) -> str:
    ext = os.path.splitext(filename)[1].lower()
    return {
        ".pdf": "pdf",
        ".docx": "docx",
        ".xlsx": "xlsx",
        ".xls": "xlsx",
        ".csv": "csv",
        ".txt": "txt",
        ".html": "html",
        ".htm": "html",
    }.get(ext, "txt")


def extract_text_from_bytes(data: bytes, file_type: str) -> str:
    if file_type == "pdf":
        with io.BytesIO(data) as f:
            with pdfplumber.open(f) as pdf:
                return "\n".join(page.extract_text() or "" for page in pdf.pages)
    elif file_type == "docx":
        with io.BytesIO(data) as f:
            document = docx.Document(f)
            return "\n".join(p.text for p in document.paragraphs)
    elif file_type == "xlsx":
        with io.BytesIO(data) as f:
            try:
                df = pd.read_excel(f, engine="openpyxl")
            except Exception:
                df = pd.read_excel(f)
            return df.to_csv(index=False)
    elif file_type == "csv":
        with io.BytesIO(data) as f:
            df = pd.read_csv(f)
            return df.to_csv(index=False)
    elif file_type == "html":
        html = data.decode("utf-8", errors="ignore")
        soup = BeautifulSoup(html, "html.parser")
        return soup.get_text(separator="\n")
    else:
        return data.decode("utf-8", errors="ignore")


def simple_token_count(text: str) -> int:
    # Approximate tokenization using whitespace split
    return max(1, len(text.split()))


def chunk_text(text: str, chunk_tokens: int = CHUNK_TOKENS, overlap_tokens: int = CHUNK_OVERLAP) -> List[str]:
    words = text.split()
    chunks: List[str] = []
    if not words:
        return chunks
    step = max(1, chunk_tokens - overlap_tokens)
    for start in range(0, len(words), step):
        piece = words[start:start + chunk_tokens]
        if not piece:
            break
        chunks.append(" ".join(piece))
        if start + chunk_tokens >= len(words):
            break
    return chunks


def build_chunk_records(bucket: str, filename: str, file_type: str, chunks: List[str]) -> List[Dict]:
    records: List[Dict] = []
    for idx, ch in enumerate(chunks):
        records.append({
            "doc_id": f"{filename}#chunk-{idx}",
            "content": ch,
            "metadata": {
                "bucket": bucket,
                "filename": filename,
                "file_type": file_type,
                "chunk_id": idx,
            }
        })
    return records


def ingest_bucket(bucket: str, prefix: str = "", limit: Optional[int] = None) -> List[Dict]:
    files = list_gcs_files(bucket, prefix)
    if limit:
        files = files[:limit]
    all_records: List[Dict] = []
    for name in files:
        ftype = detect_type(name)
        try:
            data = read_gcs_file(bucket, name)
            text = extract_text_from_bytes(data, ftype)
            chunks = chunk_text(text)
            all_records.extend(build_chunk_records(bucket, name, ftype, chunks))
        except Exception as e:
            # Skip problematic files
            print(f"[WARN] Failed to ingest {name}: {e}")
            continue
    return all_records


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Ingest and chunk files from a GCS bucket")
    parser.add_argument("bucket", help="GCS bucket name")
    parser.add_argument("--prefix", default="", help="Optional prefix")
    parser.add_argument("--limit", type=int, default=None)
    args = parser.parse_args()
    recs = ingest_bucket(args.bucket, args.prefix, args.limit)
    print(f"Ingested {len(recs)} chunk records")
