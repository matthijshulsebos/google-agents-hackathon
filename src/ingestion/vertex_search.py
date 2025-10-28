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
                safe_filename = filename.replace('.', '_').replace(' ', '_')
                doc_id = f"{safe_filename}_chunk_{doc['metadata']['chunk_id']}"
                
                                # For NO_CONTENT datastores: use struct_data with text_content field
                content_text = doc["content"]
                logger.info(f"Indexing doc {doc_id}: content length = {len(content_text)} chars")
                
                # Put metadata AND content in struct_data
                doc_data = dict(doc["metadata"])
                doc_data["text_content"] = content_text  # This will be searchable
                
                # Create document
                document = discoveryengine.Document()
                document.id = doc_id
                document.struct_data = doc_data  # Everything in struct_data for NO_CONTENT datastores
                
                logger.info(f"Document struct_data keys: {list(doc_data.keys())}")
                
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
        
        # Initialize client
        client_options = ClientOptions(
            api_endpoint=f"{location}-discoveryengine.googleapis.com"
        )
        self.client = discoveryengine.SearchServiceClient(
            client_options=client_options
        )
        
        # Use the engine's serving config (required for Search Apps)
        # Format: projects/{project}/locations/{location}/collections/default_collection/engines/{engine}/servingConfigs/default_config
        self.serving_config = f"projects/{project_id}/locations/{location}/collections/default_collection/engines/{self.engine_id}/servingConfigs/default_config"
        
        logger.info(f"Initialized retriever with engine '{self.engine_id}'")
    
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
                
                # For NO_CONTENT datastores, content is in struct_data["text_content"]
                if hasattr(result.document, 'struct_data'):
                    struct = dict(result.document.struct_data)
                    # Extract the text content
                    if 'text_content' in struct:
                        doc_data["content"] = struct['text_content']
                    # Store other metadata
                    doc_data["metadata"] = {k: v for k, v in struct.items() if k != 'text_content'}
                
                # Also try snippets if available (more relevant excerpts)
                if not doc_data["content"] and hasattr(result.document, 'derived_struct_data'):
                    derived_data = dict(result.document.derived_struct_data)
                    if 'snippets' in derived_data:
                        snippets = derived_data['snippets']
                        if snippets:
                            doc_data["content"] = snippets[0].get('snippet', '')
                
                results.append(doc_data)
            
            logger.info(f"Found {len(results)} results for query: {query[:50]}...")
            return results
            
        except Exception as e:
            logger.error(f"Error searching: {e}")
            return []
