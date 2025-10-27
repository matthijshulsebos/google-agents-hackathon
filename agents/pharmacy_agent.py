"""
Pharmacy Agent - Specialized agent for medication inventory and pharmaceutical information
"""
from typing import Dict, Any, List, Optional
import logging
from utils.rag_pipeline import RAGPipeline
from agents.prompts.pharmacy_prompts import (
    PHARMACY_SYSTEM_INSTRUCTION,
    get_language_specific_instruction,
    format_pharmacy_response_template,
    get_inventory_status_explanation
)

logger = logging.getLogger(__name__)


class PharmacyAgent:
    """
    Agent specialized in medication inventory, drug information, and pharmaceutical guidelines
    Handles queries in English and German
    Uses RAG (Retrieval Augmented Generation) with Vertex AI Search
    """

    def __init__(
        self,
        project_id: str,
        datastore_id: str = None,
        location: str = "us-central1"
    ):
        """
        Initialize Pharmacy Agent

        Args:
            project_id: Google Cloud Project ID
            datastore_id: Vertex AI Search engine ID for pharmacy documents
            location: GCP location
        """
        self.project_id = project_id
        self.location = location
        self.agent_type = "pharmacy"

        # Get datastore ID from config if not provided
        if not datastore_id:
            from config import Config
            self.datastore_id = Config.get_datastore_id("pharmacy")
        else:
            self.datastore_id = datastore_id

        # Initialize RAG pipeline
        self.rag = RAGPipeline(
            project_id=project_id,
            search_engine_id=self.datastore_id,
            location=location,
            search_location="global"
        )

        logger.info(f"Pharmacy Agent initialized with RAG pipeline (engine: {self.datastore_id})")

    def detect_language(self, text: str) -> str:
        """Detect query language (English or German)"""
        if any(word in text.lower() for word in ['ist', 'haben', 'wie', 'welche', 'verfügbar']):
            return "de"
        return "en"

    def search_inventory(
        self,
        query: str,
        temperature: float = 0.2,
        conversation_history: Optional[List[Dict[str, str]]] = None
    ) -> Dict[str, Any]:
        """
        Search medication inventory and pharmaceutical information using RAG

        Args:
            query: User's question about medications or inventory
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
            system_instruction = PHARMACY_SYSTEM_INSTRUCTION
            system_instruction += get_language_specific_instruction(language)
            system_instruction += format_pharmacy_response_template()
            system_instruction += get_inventory_status_explanation(language)

            # Use RAG pipeline to generate response
            result = self.rag.generate_response(
                query=query,
                system_instruction=system_instruction,
                temperature=temperature,
                max_search_results=5,
                conversation_history=conversation_history
            )

            # Add metadata
            result['agent'] = 'pharmacy'
            result['language'] = language
            result['domain'] = 'pharmacy'

            # Map search_results to grounding_metadata for compatibility
            if result.get('search_results'):
                result['grounding_metadata'] = result['search_results']

            # Format response for better readability
            if not result.get('error'):
                result['formatted_answer'] = self._format_answer(result.get('answer', ''))

            logger.info(f"Pharmacy query processed successfully: {query[:50]}...")
            return result

        except Exception as e:
            logger.error(f"Error in pharmacy agent search_inventory: {str(e)}")
            return {
                "error": True,
                "message": str(e),
                "agent": "pharmacy",
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
        # Add any specific formatting needed for pharmacy responses
        return answer

    def check_medication_availability(
        self,
        medication_name: str,
        strength: str = None,
        language: str = "en"
    ) -> Dict[str, Any]:
        """
        Check if specific medication is in stock

        Args:
            medication_name: Name of medication
            strength: Optional strength (e.g., "400mg")
            language: Language code (en or de)

        Returns:
            Dict with availability information
        """
        # Build query based on language
        if language == "de":
            if strength:
                query = f"Ist {medication_name} {strength} auf Lager?"
            else:
                query = f"Ist {medication_name} verfügbar?"
        else:
            if strength:
                query = f"Is {medication_name} {strength} in stock?"
            else:
                query = f"Is {medication_name} available?"

        return self.search_inventory(query)

    def get_medication_info(
        self,
        medication_name: str,
        language: str = "en"
    ) -> Dict[str, Any]:
        """
        Get detailed information about a medication

        Args:
            medication_name: Name of medication
            language: Language code (en or de)

        Returns:
            Dict with medication information
        """
        # Build query based on language
        if language == "de":
            query = f"Welche Informationen haben wir über {medication_name}?"
        else:
            query = f"What information do we have about {medication_name}?"

        return self.search_inventory(query)

    def check_drug_category(
        self,
        category: str,
        language: str = "en"
    ) -> Dict[str, Any]:
        """
        Check availability of medications in a category

        Args:
            category: Drug category (e.g., "antibiotics", "analgesics")
            language: Language code (en or de)

        Returns:
            Dict with category information
        """
        # Build query based on language
        if language == "de":
            queries = {
                "antibiotics": "Welche Antibiotika sind auf Lager?",
                "analgesics": "Welche Schmerzmittel sind verfügbar?",
                "insulin": "Welche Insulinprodukte haben wir?",
                "cardiovascular": "Welche kardiovaskulären Medikamente sind auf Lager?"
            }
        else:
            queries = {
                "antibiotics": "Which antibiotics are in stock?",
                "analgesics": "Which pain medications are available?",
                "insulin": "What insulin products do we have?",
                "cardiovascular": "Which cardiovascular medications are in stock?"
            }

        query = queries.get(category.lower(),
                           f"Which {category} medications are available?" if language == "en"
                           else f"Welche {category} Medikamente sind verfügbar?")

        return self.search_inventory(query)

    def get_storage_requirements(
        self,
        medication_name: str,
        language: str = "en"
    ) -> Dict[str, Any]:
        """
        Get storage requirements for a medication

        Args:
            medication_name: Name of medication
            language: Language code (en or de)

        Returns:
            Dict with storage information
        """
        # Build query based on language
        if language == "de":
            query = f"Wie wird {medication_name} gelagert? Was sind die Lagerungsanforderungen?"
        else:
            query = f"How is {medication_name} stored? What are the storage requirements?"

        return self.search_inventory(query)

    def check_controlled_substances(
        self,
        medication_name: str = None,
        language: str = "en"
    ) -> Dict[str, Any]:
        """
        Check controlled substances information

        Args:
            medication_name: Optional specific medication name
            language: Language code (en or de)

        Returns:
            Dict with controlled substances information
        """
        # Build query based on language
        if language == "de":
            if medication_name:
                query = f"Ist {medication_name} eine kontrollierte Substanz? Was sind die Anforderungen?"
            else:
                query = "Welche kontrollierten Substanzen haben wir auf Lager?"
        else:
            if medication_name:
                query = f"Is {medication_name} a controlled substance? What are the requirements?"
            else:
                query = "What controlled substances do we have in stock?"

        return self.search_inventory(query)

    def check_reorder_status(
        self,
        language: str = "en"
    ) -> Dict[str, Any]:
        """
        Check medications that need reordering

        Args:
            language: Language code (en or de)

        Returns:
            Dict with reorder status information
        """
        # Build query based on language
        if language == "de":
            query = "Welche Medikamente müssen nachbestellt werden? Was ist der aktuelle Nachbestellstatus?"
        else:
            query = "Which medications need to be reordered? What is the current reorder status?"

        return self.search_inventory(query)

    def get_expiring_medications(
        self,
        days: int = 30,
        language: str = "en"
    ) -> Dict[str, Any]:
        """
        Get medications expiring soon

        Args:
            days: Number of days to look ahead (default: 30)
            language: Language code (en or de)

        Returns:
            Dict with expiring medications information
        """
        # Build query based on language
        if language == "de":
            query = f"Welche Medikamente laufen in den nächsten {days} Tagen ab?"
        else:
            query = f"Which medications are expiring in the next {days} days?"

        return self.search_inventory(query)

    def get_alternative_medications(
        self,
        medication_name: str,
        language: str = "en"
    ) -> Dict[str, Any]:
        """
        Find alternative medications

        Args:
            medication_name: Medication to find alternatives for
            language: Language code (en or de)

        Returns:
            Dict with alternative medication information
        """
        # Build query based on language
        if language == "de":
            query = f"Gibt es Alternativen für {medication_name} in unserem Bestand?"
        else:
            query = f"Are there alternatives for {medication_name} in our inventory?"

        return self.search_inventory(query)


# Convenience function for quick queries
def ask_pharmacy_question(
    question: str,
    project_id: str,
    datastore_id: str = None
) -> str:
    """
    Quick function to ask a pharmacy question

    Args:
        question: The pharmacy question
        project_id: Google Cloud Project ID
        datastore_id: Optional datastore ID

    Returns:
        Answer string
    """
    agent = PharmacyAgent(project_id=project_id, datastore_id=datastore_id)
    result = agent.search_inventory(question)

    if result.get('error'):
        return f"Error: {result.get('message', 'Unknown error')}"

    return result.get('answer', 'No answer generated')
