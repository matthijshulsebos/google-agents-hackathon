"""
Vertex AI Search integration utilities for hospital multi-agent system
"""
from typing import Dict, Any, List, Optional
from google import genai
from google.genai import types
import logging
from config import config

# Set up logging
logging.basicConfig(
    level=getattr(logging, config.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class VertexSearchClient:
    """
    Wrapper class for Vertex AI Search using Google ADK
    Provides document retrieval and grounding capabilities
    """

    def __init__(
        self,
        project_id: str,
        location: str = "us-central1",
        model_name: str = None,
        datastore_id: str = None
    ):
        """
        Initialize Vertex AI Search client

        Args:
            project_id: Google Cloud Project ID
            location: GCP location (default: us-central1)
            model_name: Gemini model to use (default: from config)
            datastore_id: Vertex AI Search datastore ID for grounding
        """
        self.project_id = project_id
        self.location = location
        self.model_name = model_name or config.MODEL_NAME
        self.datastore_id = datastore_id

        # Get project number for Vertex AI Search (it requires number, not ID)
        self.project_number = None
        try:
            import subprocess
            result = subprocess.run(
                ['gcloud', 'projects', 'describe', project_id, '--format=value(projectNumber)'],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0:
                self.project_number = result.stdout.strip()
                logger.info(f"Retrieved project number: {self.project_number}")
        except Exception as e:
            logger.warning(f"Could not get project number: {e}. Will use project ID instead.")

        try:
            # Initialize Google ADK client with Vertex AI
            self.client = genai.Client(
                vertexai=True,
                project=self.project_id,
                location=self.location
            )
            logger.info(f"Initialized Vertex Search client for project: {project_id}")
        except Exception as e:
            logger.error(f"Failed to initialize Vertex Search client: {str(e)}")
            raise

    def create_search_tool(
        self,
        datastore_id: str = None,
        dynamic_threshold: float = None
    ) -> types.Tool:
        """
        Create Vertex AI Search tool with datastore configuration

        Args:
            datastore_id: Vertex AI Search datastore ID (required for proper grounding)
            dynamic_threshold: Threshold for dynamic retrieval (default: from config)

        Returns:
            types.Tool: Configured Vertex AI Search tool
        """
        threshold = dynamic_threshold or config.DYNAMIC_THRESHOLD

        if datastore_id:
            # Format datastore as full resource name
            # Format: projects/PROJECT_NUMBER/locations/LOCATION/collections/COLLECTION/dataStores/DATASTORE_ID
            # Note: Vertex AI Search datastores are typically in 'global' location
            # IMPORTANT: Must use project NUMBER not project ID
            # IMPORTANT: Must use 'dataStores' not 'engines' for the VertexAISearch tool
            if not datastore_id.startswith('projects/'):
                datastore_location = 'global'  # Vertex AI Search uses global location
                project_identifier = self.project_number or self.project_id
                # Use dataStores path as required by VertexAISearch
                datastore_resource = f"projects/{project_identifier}/locations/{datastore_location}/collections/default_collection/dataStores/{datastore_id}"
            else:
                datastore_resource = datastore_id

            # Use Vertex AI Search with specific datastore for grounding
            search_tool = types.Tool(
                retrieval=types.Retrieval(
                    disable_attribution=False,
                    vertex_ai_search=types.VertexAISearch(
                        datastore=datastore_resource
                    )
                )
            )
            logger.info(f"Created Vertex AI Search tool with datastore: {datastore_resource}")
        else:
            # Fallback to Google Search Retrieval with dynamic config
            search_tool = types.Tool(
                google_search_retrieval=types.GoogleSearchRetrieval(
                    dynamic_retrieval_config=types.DynamicRetrievalConfig(
                        mode='MODE_DYNAMIC',
                        dynamicThreshold=threshold
                    )
                )
            )
            logger.debug(f"Created Google Search Retrieval tool")

        return search_tool

    def generate_with_search(
        self,
        query: str,
        system_instruction: str,
        temperature: float = None,
        dynamic_threshold: float = None
    ) -> Dict[str, Any]:
        """
        Generate response using Gemini with Vertex AI Search grounding

        Args:
            query: User query to process
            system_instruction: System instruction for the agent
            temperature: Model temperature (default: from config)
            dynamic_threshold: Search threshold (default: from config)

        Returns:
            Dict containing:
                - answer: Generated text response
                - grounding_metadata: Citation and source information
                - search_queries: Queries used for retrieval
        """
        try:
            # Create search tool with datastore configuration
            search_tool = self.create_search_tool(
                datastore_id=self.datastore_id,
                dynamic_threshold=dynamic_threshold
            )

            # Set temperature
            temp = temperature or config.TEMPERATURE

            # Generate content with search
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=query,
                config=types.GenerateContentConfig(
                    system_instruction=system_instruction,
                    tools=[search_tool],
                    temperature=temp,
                )
            )

            # Extract response text
            answer = response.text if hasattr(response, 'text') else str(response)

            # Extract grounding metadata
            grounding_metadata = self._extract_grounding_metadata(response)

            # Extract search queries if available
            search_queries = self._extract_search_queries(response)

            result = {
                "answer": answer,
                "grounding_metadata": grounding_metadata,
                "search_queries": search_queries,
                "model": self.model_name,
                "temperature": temp
            }

            logger.info(f"Successfully generated response for query: {query[:50]}...")
            return result

        except Exception as e:
            logger.error(f"Error generating response: {str(e)}")
            return {
                "error": True,
                "message": str(e),
                "answer": None,
                "grounding_metadata": None
            }

    def _extract_grounding_metadata(self, response: Any) -> Optional[List[Dict[str, Any]]]:
        """
        Extract grounding metadata (citations) from response

        Args:
            response: Response from generate_content

        Returns:
            List of citation dictionaries or None
        """
        try:
            if not hasattr(response, 'candidates') or not response.candidates:
                return None

            candidate = response.candidates[0]

            if not hasattr(candidate, 'grounding_metadata'):
                return None

            grounding = candidate.grounding_metadata

            citations = []

            # Extract grounding chunks
            if hasattr(grounding, 'grounding_chunks'):
                for chunk in grounding.grounding_chunks:
                    citation = {}

                    if hasattr(chunk, 'web'):
                        citation['source'] = 'web'
                        citation['uri'] = chunk.web.uri if hasattr(chunk.web, 'uri') else None
                        citation['title'] = chunk.web.title if hasattr(chunk.web, 'title') else None

                    if hasattr(chunk, 'retrieved_context'):
                        citation['source'] = 'vertex_search'
                        citation['uri'] = chunk.retrieved_context.uri if hasattr(chunk.retrieved_context, 'uri') else None
                        citation['title'] = chunk.retrieved_context.title if hasattr(chunk.retrieved_context, 'title') else None

                    if citation:
                        citations.append(citation)

            # Extract grounding supports (which parts of answer are grounded)
            if hasattr(grounding, 'grounding_supports'):
                for idx, support in enumerate(grounding.grounding_supports):
                    if idx < len(citations):
                        if hasattr(support, 'segment'):
                            citations[idx]['grounded_text'] = support.segment.text if hasattr(support.segment, 'text') else None
                        if hasattr(support, 'confidence_score'):
                            citations[idx]['confidence'] = support.confidence_score

            return citations if citations else None

        except Exception as e:
            logger.warning(f"Could not extract grounding metadata: {str(e)}")
            return None

    def _extract_search_queries(self, response: Any) -> Optional[List[str]]:
        """
        Extract search queries used for retrieval

        Args:
            response: Response from generate_content

        Returns:
            List of search queries or None
        """
        try:
            if not hasattr(response, 'candidates') or not response.candidates:
                return None

            candidate = response.candidates[0]

            if not hasattr(candidate, 'grounding_metadata'):
                return None

            grounding = candidate.grounding_metadata

            queries = []

            if hasattr(grounding, 'search_entry_point'):
                if hasattr(grounding.search_entry_point, 'rendered_content'):
                    # Extract queries from rendered content if available
                    queries.append(grounding.search_entry_point.rendered_content)

            if hasattr(grounding, 'retrieval_queries'):
                for query in grounding.retrieval_queries:
                    queries.append(str(query))

            return queries if queries else None

        except Exception as e:
            logger.warning(f"Could not extract search queries: {str(e)}")
            return None

    def health_check(self) -> Dict[str, Any]:
        """
        Perform health check on Vertex AI Search connection

        Returns:
            Dict with health status
        """
        try:
            # Simple test query
            test_response = self.client.models.generate_content(
                model=self.model_name,
                contents="Hello",
                config=types.GenerateContentConfig(
                    temperature=0.1,
                )
            )

            return {
                "healthy": True,
                "project_id": self.project_id,
                "location": self.location,
                "model": self.model_name,
                "message": "Connection successful"
            }

        except Exception as e:
            logger.error(f"Health check failed: {str(e)}")
            return {
                "healthy": False,
                "project_id": self.project_id,
                "error": str(e)
            }


class BaseAgent:
    """
    Base class for specialized agents (Nursing, HR, Pharmacy)
    Provides common functionality for all agents
    """

    def __init__(
        self,
        agent_type: str,
        project_id: str,
        datastore_id: str = None,
        location: str = "us-central1"
    ):
        """
        Initialize base agent

        Args:
            agent_type: Type of agent (nursing, hr, pharmacy)
            project_id: Google Cloud Project ID
            datastore_id: Vertex AI Search datastore ID (optional, uses config)
            location: GCP location
        """
        self.agent_type = agent_type.lower()
        self.project_id = project_id
        self.datastore_id = datastore_id or config.get_datastore_id(self.agent_type)
        self.location = location

        # Initialize Vertex Search client with datastore
        self.search_client = VertexSearchClient(
            project_id=self.project_id,
            location=self.location,
            datastore_id=self.datastore_id
        )

        logger.info(f"Initialized {self.agent_type} agent with datastore: {self.datastore_id}")

    def query(
        self,
        user_query: str,
        system_instruction: str,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Process user query and return response

        Args:
            user_query: User's question
            system_instruction: System instruction for the agent
            **kwargs: Additional arguments for generate_with_search

        Returns:
            Dict with response and metadata
        """
        try:
            # Generate response with search
            result = self.search_client.generate_with_search(
                query=user_query,
                system_instruction=system_instruction,
                **kwargs
            )

            # Add agent metadata
            result['agent'] = self.agent_type
            result['query'] = user_query

            return result

        except Exception as e:
            logger.error(f"Error processing query in {self.agent_type} agent: {str(e)}")
            return {
                "error": True,
                "message": str(e),
                "agent": self.agent_type,
                "query": user_query
            }

# Language detection moved to utils/language_detector.py for centralized LLM-based detection
