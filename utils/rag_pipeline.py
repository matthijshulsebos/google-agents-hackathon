"""
RAG (Retrieval Augmented Generation) Pipeline
Combines Vertex AI Search with Gemini for grounded responses
"""

import logging
from typing import Dict, Any, List, Optional
from google import genai
from google.genai import types
from utils.vertex_search_adapter import VertexSearchAdapter

logger = logging.getLogger(__name__)


class RAGPipeline:
    """
    Retrieval Augmented Generation pipeline
    Uses Vertex AI Search for retrieval and Gemini for generation
    """

    def __init__(
        self,
        project_id: str,
        search_engine_id: str,
        location: str = "us-central1",
        search_location: str = "global",
        model_name: str = "gemini-2.5-flash"
    ):
        """
        Initialize RAG pipeline

        Args:
            project_id: GCP project ID
            search_engine_id: Vertex AI Search engine ID
            location: Location for Gemini (e.g., us-central1)
            search_location: Location for Vertex Search (usually global)
            model_name: Gemini model to use
        """
        self.project_id = project_id
        self.search_engine_id = search_engine_id
        self.location = location
        self.model_name = model_name

        # Initialize Vertex Search adapter
        self.search_adapter = VertexSearchAdapter(
            project_id=project_id,
            location=search_location,
            search_engine_id=search_engine_id
        )

        # Initialize Gemini client
        self.gemini_client = genai.Client(
            vertexai=True,
            project=project_id,
            location=location
        )

        logger.info(f"RAG Pipeline initialized with search engine: {search_engine_id}")

    def generate_response(
        self,
        query: str,
        system_instruction: str,
        temperature: float = 0.2,
        max_search_results: int = 5,
        conversation_history: Optional[List[Dict[str, str]]] = None
    ) -> Dict[str, Any]:
        """
        Generate response using RAG approach

        Args:
            query: User query
            system_instruction: System instruction for Gemini
            temperature: Model temperature
            max_search_results: Maximum number of search results to use as context
            conversation_history: Optional list of previous conversation turns
                Format: [{"role": "user", "content": "..."}, {"role": "assistant", "content": "..."}]

        Returns:
            Dictionary with answer and metadata
        """
        try:
            # Step 1: Retrieve relevant documents from Vertex AI Search
            logger.info(f"Searching for: {query[:50]}...")
            search_results = self.search_adapter.search(
                query=query,
                page_size=max_search_results,
                query_expansion=False,  # Disable for multi-datastore
                spell_correction=False
            )

            if search_results.get('error'):
                logger.error(f"Search error: {search_results['error']}")
                return {
                    "error": True,
                    "message": f"Search failed: {search_results['error']}",
                    "answer": None
                }

            # Step 2: Format search results as context
            context = self._format_search_context(search_results)

            # Step 3: Generate response with Gemini using retrieved context
            logger.info(f"Generating response with {len(search_results.get('results', []))} search results...")
            answer = self._generate_with_gemini(
                query=query,
                context=context,
                system_instruction=system_instruction,
                temperature=temperature,
                conversation_history=conversation_history
            )

            # Step 4: Return response with metadata
            return {
                "answer": answer,
                "search_results": search_results.get('results', []),
                "total_results": search_results.get('total_size', 0),
                "query": query,
                "error": False
            }

        except Exception as e:
            logger.error(f"RAG pipeline error: {str(e)}")
            return {
                "error": True,
                "message": str(e),
                "answer": None
            }

    def _format_conversation_history(self, conversation_history: List[Dict[str, str]]) -> str:
        """
        Format conversation history for inclusion in system instruction

        Args:
            conversation_history: List of conversation turns

        Returns:
            Formatted conversation history string
        """
        if not conversation_history:
            return ""

        history_parts = ["Previous Conversation:\n"]

        for turn in conversation_history:
            role = turn.get("role", "")
            content = turn.get("content", "")

            if role == "user":
                history_parts.append(f"User: {content}")
            elif role == "assistant":
                history_parts.append(f"Assistant: {content}")

        history_parts.append("\nCurrent Question:\n")

        return "\n".join(history_parts)

    def _format_search_context(self, search_results: Dict[str, Any]) -> str:
        """
        Format search results into context for Gemini

        Args:
            search_results: Results from Vertex AI Search

        Returns:
            Formatted context string
        """
        results = search_results.get('results', [])

        if not results:
            return "No relevant documents found in the knowledge base."

        context_parts = ["Retrieved Information from Knowledge Base:\n"]

        for i, result in enumerate(results, 1):
            doc_data = result.get('document', {}).get('data', {})
            if doc_data:
                context_parts.append(f"\n[Document {i}]")
                # Format each field from the document
                for key, value in doc_data.items():
                    # Convert value to string and limit length
                    value_str = str(value)
                    if len(value_str) > 1000:
                        value_str = value_str[:1000] + "..."
                    context_parts.append(f"{key}: {value_str}")

        return "\n".join(context_parts)

    def _generate_with_gemini(
        self,
        query: str,
        context: str,
        system_instruction: str,
        temperature: float,
        conversation_history: Optional[List[Dict[str, str]]] = None
    ) -> str:
        """
        Generate response using Gemini with retrieved context

        Args:
            query: User query
            context: Retrieved context from search
            system_instruction: System instruction
            temperature: Model temperature
            conversation_history: Optional conversation history

        Returns:
            Generated answer
        """
        # Format conversation history if provided
        conversation_context = self._format_conversation_history(conversation_history) if conversation_history else ""

        # Combine system instruction with conversation history and retrieved context
        enhanced_instruction = f"""{system_instruction}

{conversation_context}

Use the following retrieved information to answer the user's question. If the information is not in the retrieved documents, clearly state that.

{context}
"""

        # Generate response
        response = self.gemini_client.models.generate_content(
            model=self.model_name,
            contents=query,
            config=types.GenerateContentConfig(
                system_instruction=enhanced_instruction,
                temperature=temperature
            )
        )

        return response.text if hasattr(response, 'text') else str(response)
