"""
Nursing Agent - Specialized agent for nursing procedures and protocols
"""
from typing import Dict, Any, List, Optional
import logging
from utils.rag_pipeline import RAGPipeline
from agents.prompts.nursing_prompts import (
    NURSING_SYSTEM_INSTRUCTION,
    get_language_specific_instruction,
    format_nursing_response_template
)

logger = logging.getLogger(__name__)


class NursingAgent:
    """
    Agent specialized in nursing procedures, protocols, and patient care
    Handles queries in English and Spanish
    Uses RAG (Retrieval Augmented Generation) with Vertex AI Search
    """

    def __init__(
        self,
        project_id: str,
        datastore_id: str = None,
        location: str = "us-central1"
    ):
        """
        Initialize Nursing Agent

        Args:
            project_id: Google Cloud Project ID
            datastore_id: Vertex AI Search engine ID for nursing documents
            location: GCP location
        """
        self.project_id = project_id
        self.location = location
        self.agent_type = "nursing"

        # Get datastore ID from config if not provided
        if not datastore_id:
            from config import Config
            self.datastore_id = Config.get_datastore_id("nursing")
        else:
            self.datastore_id = datastore_id

        # Initialize RAG pipeline
        self.rag = RAGPipeline(
            project_id=project_id,
            search_engine_id=self.datastore_id,
            location=location,
            search_location="global"
        )

        logger.info(f"Nursing Agent initialized with RAG pipeline (engine: {self.datastore_id})")

    def detect_language(self, text: str) -> str:
        """Detect query language"""
        if any(word in text.lower() for word in ['¿', '¡', 'días', 'cómo', 'cuál', 'para']):
            return "es"
        return "en"

    def search_protocols(
        self,
        query: str,
        temperature: float = 0.2,
        conversation_history: Optional[List[Dict[str, str]]] = None
    ) -> Dict[str, Any]:
        """
        Search nursing protocols and procedures using RAG

        Args:
            query: User's question about nursing procedures
            temperature: Model temperature (lower = more focused)
            conversation_history: Optional conversation history for context

        Returns:
            Dict with answer, search results, and metadata
        """
        try:
            # Detect language
            language = self.detect_language(query)
            logger.info(f"Detected language: {language} for query: {query[:50]}...")

            # Build system instruction with language-specific additions
            system_instruction = NURSING_SYSTEM_INSTRUCTION
            system_instruction += get_language_specific_instruction(language)
            system_instruction += format_nursing_response_template()

            # Use RAG pipeline to generate response
            result = self.rag.generate_response(
                query=query,
                system_instruction=system_instruction,
                temperature=temperature,
                max_search_results=5,
                conversation_history=conversation_history
            )

            # Add metadata
            result['agent'] = 'nursing'
            result['language'] = language
            result['domain'] = 'nursing'

            # Map search_results to grounding_metadata for compatibility
            if result.get('search_results'):
                result['grounding_metadata'] = result['search_results']

            logger.info(f"Nursing query processed successfully: {query[:50]}...")
            return result

        except Exception as e:
            logger.error(f"Error in nursing agent search_protocols: {str(e)}")
            return {
                "error": True,
                "message": str(e),
                "agent": "nursing",
                "query": query
            }

    def _format_answer(self, answer: str) -> str:
        """
        Format answer for display

        Args:
            answer: Raw answer text

        Returns:
            Formatted answer string
        """
        # Add any specific formatting needed for nursing responses
        # For now, just return the answer as-is
        return answer

    def get_procedure_steps(
        self,
        procedure_name: str,
        language: str = "en"
    ) -> Dict[str, Any]:
        """
        Get specific procedure steps by name

        Args:
            procedure_name: Name of the procedure (e.g., "IV insertion")
            language: Language code (en or es)

        Returns:
            Dict with procedure steps and details
        """
        # Build query based on language
        if language == "es":
            query = f"¿Cuáles son los pasos del procedimiento para {procedure_name}?"
        else:
            query = f"What are the steps for the {procedure_name} procedure?"

        return self.search_protocols(query)

    def check_safety_protocol(
        self,
        topic: str,
        language: str = "en"
    ) -> Dict[str, Any]:
        """
        Check safety protocols for a specific topic

        Args:
            topic: Safety topic to check
            language: Language code (en or es)

        Returns:
            Dict with safety information
        """
        # Build query based on language
        if language == "es":
            query = f"¿Cuáles son las consideraciones de seguridad para {topic}?"
        else:
            query = f"What are the safety considerations for {topic}?"

        return self.search_protocols(query)

    def get_equipment_list(
        self,
        procedure_name: str,
        language: str = "en"
    ) -> Dict[str, Any]:
        """
        Get equipment list for a procedure

        Args:
            procedure_name: Name of the procedure
            language: Language code (en or es)

        Returns:
            Dict with equipment list
        """
        # Build query based on language
        if language == "es":
            query = f"¿Qué equipo se necesita para {procedure_name}?"
        else:
            query = f"What equipment is needed for {procedure_name}?"

        return self.search_protocols(query)

    def handle_emergency_query(
        self,
        emergency_situation: str,
        language: str = "en"
    ) -> Dict[str, Any]:
        """
        Handle emergency-related queries with high priority

        Args:
            emergency_situation: Description of emergency
            language: Language code (en or es)

        Returns:
            Dict with emergency response information
        """
        logger.warning(f"Emergency query received: {emergency_situation}")

        # Use lower temperature for more focused emergency responses
        if language == "es":
            query = f"EMERGENCIA: {emergency_situation} - ¿Qué protocolo debo seguir?"
        else:
            query = f"EMERGENCY: {emergency_situation} - What protocol should I follow?"

        result = self.search_protocols(query, temperature=0.1)
        result['emergency'] = True

        return result


# Convenience function for quick queries
def ask_nursing_question(
    question: str,
    project_id: str,
    datastore_id: str = None
) -> str:
    """
    Quick function to ask a nursing question

    Args:
        question: The nursing question
        project_id: Google Cloud Project ID
        datastore_id: Optional datastore ID

    Returns:
        Answer string
    """
    agent = NursingAgent(project_id=project_id, datastore_id=datastore_id)
    result = agent.search_protocols(question)

    if result.get('error'):
        return f"Error: {result.get('message', 'Unknown error')}"

    return result.get('answer', 'No answer generated')
