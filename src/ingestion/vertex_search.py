"""
Vertex AI Search integration for document indexing and retrieval.
"""
import logging
from typing import List, Dict, Any, Optional
from google.cloud import discoveryengine_v1 as discoveryengine
from google.api_core.client_options import ClientOptions

logger = logging.getLogger(__name__)


class VertexSearchIndexer:
    """Index documents into Vertex AI Search."""
    
    def __init__(self, project_id: str, location: str, datastore_id: str):
        self.project_id = project_id
        self.location = location
        self.datastore_id = datastore_id
        
        # Initialize client
        client_options = ClientOptions(
            api_endpoint=f"{location}-discoveryengine.googleapis.com"
        )
        self.client = discoveryengine.DocumentServiceClient(
            client_options=client_options
        )
        
        self.parent = self.client.branch_path(
            project=project_id,
            location=location,
            data_store=datastore_id,
            branch="default_branch"
        )
    
    def index_documents(self, documents: List[Dict[str, Any]]) -> bool:
        """Index a batch of documents."""
        try:
            for idx, doc in enumerate(documents):
                # Create document object
                document = discoveryengine.Document(
                    id=f"{doc['metadata']['filename']}_chunk_{doc['metadata']['chunk_id']}",
                    content=discoveryengine.Document.Content(
                        mime_type="text/plain",
                        raw_bytes=doc["content"].encode("utf-8")
                    ),
                    struct_data=doc["metadata"]
                )
                
                # Create document
                request = discoveryengine.CreateDocumentRequest(
                    parent=self.parent,
                    document=document,
                    document_id=document.id
                )
                
                try:
                    self.client.create_document(request=request)
                    if (idx + 1) % 10 == 0:
                        logger.info(f"Indexed {idx + 1}/{len(documents)} documents")
                except Exception as e:
                    logger.warning(f"Error indexing document {document.id}: {e}")
            
            logger.info(f"Successfully indexed {len(documents)} documents to {self.datastore_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error in batch indexing: {e}")
            return False


class VertexSearchRetriever:
    """Retrieve documents from Vertex AI Search."""
    
    def __init__(self, project_id: str, location: str, datastore_id: str):
        self.project_id = project_id
        self.location = location
        self.datastore_id = datastore_id
        
        # Initialize client
        client_options = ClientOptions(
            api_endpoint=f"{location}-discoveryengine.googleapis.com"
        )
        self.client = discoveryengine.SearchServiceClient(
            client_options=client_options
        )
        
        self.serving_config = self.client.serving_config_path(
            project=project_id,
            location=location,
            data_store=datastore_id,
            serving_config="default_config"
        )
    
    def search(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """Search for documents matching the query."""
        try:
            request = discoveryengine.SearchRequest(
                serving_config=self.serving_config,
                query=query,
                page_size=top_k,
                content_search_spec=discoveryengine.SearchRequest.ContentSearchSpec(
                    snippet_spec=discoveryengine.SearchRequest.ContentSearchSpec.SnippetSpec(
                        return_snippet=True
                    ),
                    summary_spec=discoveryengine.SearchRequest.ContentSearchSpec.SummarySpec(
                        summary_result_count=top_k
                    )
                )
            )
            
            response = self.client.search(request)
            
            results = []
            for result in response.results:
                doc_data = {
                    "id": result.id,
                    "content": "",
                    "metadata": {},
                    "score": 0.0
                }
                
                # Extract content
                if hasattr(result.document, 'derived_struct_data'):
                    derived_data = dict(result.document.derived_struct_data)
                    if 'snippets' in derived_data:
                        snippets = derived_data['snippets']
                        if snippets:
                            doc_data["content"] = snippets[0].get('snippet', '')
                
                # Extract metadata
                if hasattr(result.document, 'struct_data'):
                    doc_data["metadata"] = dict(result.document.struct_data)
                
                results.append(doc_data)
            
            logger.info(f"Found {len(results)} results for query: {query[:50]}...")
            return results
            
        except Exception as e:
            logger.error(f"Error searching: {e}")
            return []
