from typing import List, Dict, Any, Optional
import os

from google.cloud import discoveryengine_v1 as de
import google.generativeai as genai
from google.cloud import aiplatform
from vertexai import init as vertexai_init
from vertexai.generative_models import GenerativeModel as VertexGenerativeModel

from .config import MODEL_NAME, TOP_K_PER_DOMAIN, MAX_SOURCES, DEFAULT_PROJECT


_vertexai_initialized = False


def _ensure_vertexai():
    global _vertexai_initialized
    if _vertexai_initialized:
        return True
    try:
        project = DEFAULT_PROJECT or os.getenv("GOOGLE_CLOUD_PROJECT") or os.getenv("PROJECT_ID")
        # Prefer explicit VERTEX_LOCATION; else REGION; avoid "global" for Vertex AI
        location = os.getenv("VERTEX_LOCATION") or os.getenv("REGION") or "us-central1"
        if location.lower() == "global":
            location = "us-central1"
        vertexai_init(project=project, location=location)
        _vertexai_initialized = True
        return True
    except Exception as e:
        print(f"[WARN] Failed to initialize Vertex AI SDK: {e}")
        return False


class VertexSearchAgent:
    def __init__(self, serving_config: str, domain: str):
        self.serving_config = serving_config
        self.domain = domain
        self.client = None  # lazy init to avoid failing app startup without GCP creds
        try:
            # Try create client eagerly; if it fails, keep None so app can still boot
            self.client = de.SearchServiceClient()
        except Exception as e:
            print(f"[WARN] Could not initialize Discovery Engine client for {domain}: {e}")
            self.client = None

    def _ensure_client(self):
        if self.client is None:
            try:
                self.client = de.SearchServiceClient()
            except Exception as e:
                print(f"[WARN] Discovery Engine client unavailable for {self.domain}: {e}")
                self.client = None
        return self.client is not None

    def search(self, query: str, page_size: int = TOP_K_PER_DOMAIN) -> List[Dict[str, Any]]:
        # If no serving config configured, skip search
        if not self.serving_config:
            return []
        if not self._ensure_client():
            return []
        request = de.SearchRequest(
            serving_config=self.serving_config,
            query=query,
            page_size=page_size,
        )
        results: List[Dict[str, Any]] = []
        try:
            response = self.client.search(request=request)
            for r in response:
                # Try to extract content text and metadata
                doc = r.document
                content = ""
                if doc.derived_struct_data and "chunk" in doc.derived_struct_data:
                    content = str(doc.derived_struct_data.get("chunk"))
                elif doc.derived_struct_data and "content" in doc.derived_struct_data:
                    content = str(doc.derived_struct_data.get("content"))
                elif doc.struct_data and "content" in doc.struct_data:
                    content = str(doc.struct_data.get("content"))
                else:
                    # fallback to text snippet
                    content = r.snippet.value if r.snippet and r.snippet.value else ""
                results.append({
                    "domain": self.domain,
                    "doc_id": doc.id,
                    "content": content,
                    "metadata": dict(doc.struct_data) if doc.struct_data else {},
                    "uri": doc.content_uri or "",
                })
        except Exception as e:
            # Return empty on errors; caller can handle
            print(f"[WARN] Discovery Engine search failed for {self.domain}: {e}")
        return results


def configure_genai(api_key: Optional[str] = None):
    if api_key:
        genai.configure(api_key=api_key)
    else:
        # Prefer using Vertex AI on Cloud Run via service account
        _ensure_vertexai()


def _generate_with_vertex_ai(prompt: str, model_name: str) -> Optional[str]:
    if not _ensure_vertexai():
        return None
    try:
        model = VertexGenerativeModel(model_name)
        resp = model.generate_content(prompt)
        return getattr(resp, "text", None) or ""
    except Exception as e:
        print(f"[WARN] Vertex AI generation failed: {e}")
        return None


def _generate_with_genai(prompt: str, model_name: str) -> Optional[str]:
    try:
        model = genai.GenerativeModel(model_name)
        resp = model.generate_content(prompt)
        return resp.text or ""
    except Exception as e:
        print(f"[WARN] Generative AI (API key) generation failed: {e}")
        return None


def generate_grounded_answer(query: str, contexts: List[Dict[str, Any]], history: List[Dict[str, str]],
                              model_name: str = MODEL_NAME) -> Dict[str, Any]:
    # If no contexts, return actionable guidance instead of a generic failure
    if not contexts:
        return {
            "answer": (
                "I couldn't find any indexed sources for your request. "
                "Please index documents for the targeted domain(s) first, then try again. "
                "To index: run python -m app.indexing nursing|pharmacy|po with the appropriate buckets configured."
            ),
            "sources": []
        }

    # Build prompt with sources
    sources_text = "\n\n".join([
        f"[Source {i+1} | {c.get('domain')} | {c.get('doc_id')}]:\n{c.get('content','')[:2000]}"
        for i, c in enumerate(contexts[:MAX_SOURCES])
    ])
    convo_preamble = (
        "You are a hospital assistant. Answer using ONLY the information from the provided sources. "
        "If the answer is not present in the sources, say you cannot find it. "
        "Cite sources as [Source N]. Be concise and precise.\n"
    )
    hist_lines = []
    for turn in history[-6:]:
        role = turn.get("role", "user")
        content = turn.get("content", "")
        hist_lines.append(f"{role.capitalize()}: {content}")
    hist_block = "\n".join(hist_lines)
    prompt = f"{convo_preamble}\n{hist_block}\n\nUser: {query}\n\nSources:\n{sources_text}\n\nAssistant:"

    # Try Vertex AI (service account) first; fall back to API-key library if configured
    text = _generate_with_vertex_ai(prompt, model_name)
    if not text:
        api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GENAI_API_KEY")
        if api_key:
            try:
                genai.configure(api_key=api_key)
            except Exception:
                pass
            text = _generate_with_genai(prompt, model_name)

    if not text:
        text = "I'm unable to generate a response at the moment."

    used_sources = [
        {
            "label": f"Source {i+1}",
            "domain": c.get("domain"),
            "doc_id": c.get("doc_id"),
            "uri": c.get("uri", ""),
            "metadata": c.get("metadata", {}),
        }
        for i, c in enumerate(contexts[:MAX_SOURCES])
    ]
    return {"answer": text, "sources": used_sources}
