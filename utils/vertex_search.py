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
        model_name: str = None
    ):
        """
        Initialize Vertex AI Search client

        Args:
            project_id: Google Cloud Project ID
            location: GCP location (default: us-central1)
            model_name: Gemini model to use (default: from config)
        """
        self.project_id = project_id
        self.location = location
        self.model_name = model_name or config.MODEL_NAME

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
        dynamic_threshold: float = None
    ) -> types.Tool:
        """
        Create Google Search tool with dynamic retrieval configuration

        Args:
            dynamic_threshold: Threshold for dynamic retrieval (default: from config)

        Returns:
            types.Tool: Configured Google Search tool
        """
        threshold = dynamic_threshold or config.DYNAMIC_THRESHOLD

        google_search_tool = types.Tool(
            google_search=types.GoogleSearch(
                dynamic_retrieval_config=types.DynamicRetrievalConfig(
                    mode=types.DynamicRetrievalConfigMode.MODE_DYNAMIC,
                    dynamic_threshold=threshold
                )
            )
        )

        logger.debug(f"Created search tool with threshold: {threshold}")
        return google_search_tool

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
            # Create search tool
            search_tool = self.create_search_tool(dynamic_threshold)

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

        # Initialize Vertex Search client
        self.search_client = VertexSearchClient(
            project_id=self.project_id,
            location=self.location
        )

        logger.info(f"Initialized {self.agent_type} agent")

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

    def detect_language(self, text: str) -> str:
        """
        Simple language detection based on keywords

        Args:
            text: Text to analyze

        Returns:
            Language code (en, es, fr, de)
        """
        text_lower = text.lower()

        # Spanish indicators
        if any(word in text_lower for word in ['¿', '¡', 'días', 'cómo', 'qué', 'cuál', 'protocolo']):
            return "es"

        # French indicators
        if any(word in text_lower for word in ['combien', 'quels', 'jours', 'comment', 'quand', 'congé']):
            return "fr"

        # German indicators
        if any(word in text_lower for word in ['ist', 'haben', 'wie', 'welche', 'verfügbar', 'lager']):
            return "de"

        # Default to English
        return "en"
