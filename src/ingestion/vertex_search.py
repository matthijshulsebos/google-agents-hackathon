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
                # Create safe document ID (only alphanumeric, hyphen, underscore allowed)
                filename = doc['metadata']['filename']
                safe_filename = filename.replace('.', '_').replace(' ', '_').replace('/', '_')
                doc_id = f"{safe_filename}_chunk_{doc['metadata']['chunk_id']}"
                
                content_text = doc["content"]
                logger.info(f"Indexing doc {doc_id}: content length = {len(content_text)} chars")
                
                # For CONTENT_REQUIRED datastores: use document.content for searchable text
                # and struct_data for metadata only
                document = discoveryengine.Document()
                document.id = doc_id
                document.content = discoveryengine.Document.Content(
                    mime_type="text/plain",
                    raw_bytes=content_text.encode('utf-8')
                )
                # Metadata in struct_data (not searchable, just for filtering/display)
                document.struct_data = doc["metadata"]
                
                logger.info(f"Document metadata keys: {list(doc['metadata'].keys())}")
                
                # Try to create document, if exists (409), update it
                try:
                    request = discoveryengine.CreateDocumentRequest(
                        parent=self.parent,
                        document=document,
                        document_id=document.id
                    )
                    self.client.create_document(request=request)
                    if (idx + 1) % 10 == 0:
                        logger.info(f"Indexed {idx + 1}/{len(documents)} documents")
                        
                except Exception as e:
                    if "409" in str(e) or "already exists" in str(e).lower():
                        # Document exists, update it instead
                        doc_name = f"{self.parent}/documents/{doc_id}"
                        try:
                            document.name = doc_name
                            update_request = discoveryengine.UpdateDocumentRequest(
                                document=document,
                                allow_missing=False
                            )
                            
                            self.client.update_document(request=update_request)
                            logger.info(f"Updated existing document {doc_id}")
                        except Exception as update_error:
                            logger.warning(f"Error updating document {doc_id}: {update_error}")
                    else:
                        logger.warning(f"Error indexing document {document.id}: {e}")
            
            logger.info(f"Successfully indexed {len(documents)} documents to {self.datastore_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error in batch indexing: {e}")
            return False


class VertexSearchRetriever:
    """Retrieve documents from Vertex AI Search."""
    
    def __init__(self, project_id: str, location: str, datastore_id: str, engine_id: Optional[str] = None):
        self.project_id = project_id
        self.location = location
        self.datastore_id = datastore_id
        self.engine_id = engine_id or f"{datastore_id}-app"  # Default engine naming convention
        
        # Initialize clients
        client_options = ClientOptions(
            api_endpoint=f"{location}-discoveryengine.googleapis.com"
        )
        self.client = discoveryengine.SearchServiceClient(
            client_options=client_options
        )
        self.document_client = discoveryengine.DocumentServiceClient(
            client_options=client_options
        )
        
        # Use the engine's serving config (required for Search Apps)
        # Format: projects/{project}/locations/{location}/collections/default_collection/engines/{engine}/servingConfigs/default_config
        self.serving_config = f"projects/{project_id}/locations/{location}/collections/default_collection/engines/{self.engine_id}/servingConfigs/default_config"
        
        logger.info(f"Initialized retriever with engine '{self.engine_id}'")
    
    def search(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """Search for documents matching the query."""
        try:
            # Request document content in search results
            request = discoveryengine.SearchRequest(
                serving_config=self.serving_config,
                query=query,
                page_size=top_k,
                content_search_spec=discoveryengine.SearchRequest.ContentSearchSpec(
                    search_result_mode=discoveryengine.SearchRequest.ContentSearchSpec.SearchResultMode.DOCUMENTS
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
                
                # Fetch full document to get content (raw_bytes not included in search results by default)
                try:
                    full_doc = self.document_client.get_document(name=result.document.name)
                    
                    # Extract content from full document
                    if hasattr(full_doc, 'content') and full_doc.content:
                        if hasattr(full_doc.content, 'raw_bytes') and full_doc.content.raw_bytes:
                            doc_data["content"] = full_doc.content.raw_bytes.decode('utf-8')
                        elif hasattr(full_doc.content, 'uri'):
                            doc_data["content"] = f"[Content at: {full_doc.content.uri}]"
                    
                    # Metadata is in struct_data
                    if hasattr(full_doc, 'struct_data') and full_doc.struct_data:
                        doc_data["metadata"] = dict(full_doc.struct_data)
                        
                except Exception as fetch_error:
                    logger.warning(f"Could not fetch full document {result.document.name}: {fetch_error}")
                    # Fall back to what's available in search result
                    if hasattr(result.document, 'struct_data') and result.document.struct_data:
                        doc_data["metadata"] = dict(result.document.struct_data)
                
                results.append(doc_data)
            
            logger.info(f"Found {len(results)} results for query: {query[:50]}...")
            return results
            
        except Exception as e:
            logger.error(f"Error searching: {e}")
            return []
