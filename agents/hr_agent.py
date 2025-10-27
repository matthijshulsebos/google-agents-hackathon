"""
HR Agent - Specialized agent for HR policies, benefits, and employee questions
"""
from typing import Dict, Any
import logging
from utils.vertex_search import BaseAgent
from agents.prompts.hr_prompts import (
    HR_SYSTEM_INSTRUCTION,
    get_language_specific_instruction,
    format_hr_response_template,
    get_calculation_prompt
)

logger = logging.getLogger(__name__)


class HRAgent(BaseAgent):
    """
    Agent specialized in HR policies, benefits, leave management, and employee support
    Handles queries in English and French
    """

    def __init__(
        self,
        project_id: str,
        datastore_id: str = None,
        location: str = "us-central1"
    ):
        """
        Initialize HR Agent

        Args:
            project_id: Google Cloud Project ID
            datastore_id: Vertex AI Search datastore ID for HR documents
            location: GCP location
        """
        super().__init__(
            agent_type="hr",
            project_id=project_id,
            datastore_id=datastore_id,
            location=location
        )
        logger.info("HR Agent initialized")

    def search_policies(
        self,
        query: str,
        temperature: float = 0.2
    ) -> Dict[str, Any]:
        """
        Search HR policies and procedures

        Args:
            query: User's question about HR policies
            temperature: Model temperature (lower = more focused)

        Returns:
            Dict with answer, citations, and metadata
        """
        try:
            # Detect language
            language = self.detect_language(query)
            logger.info(f"Detected language: {language} for query: {query[:50]}...")

            # Build system instruction with language-specific additions
            system_instruction = HR_SYSTEM_INSTRUCTION
            system_instruction += get_language_specific_instruction(language)
            system_instruction += format_hr_response_template()

            # Query with search
            result = self.query(
                user_query=query,
                system_instruction=system_instruction,
                temperature=temperature
            )

            # Add language metadata
            result['language'] = language
            result['domain'] = 'hr'

            # Format response for better readability
            if not result.get('error'):
                result['formatted_answer'] = self._format_answer(result.get('answer', ''))

            logger.info(f"HR query processed successfully: {query[:50]}...")
            return result

        except Exception as e:
            logger.error(f"Error in HR agent search_policies: {str(e)}")
            return {
                "error": True,
                "message": str(e),
                "agent": "hr",
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
        # Add any specific formatting needed for HR responses
        return answer

    def get_leave_policy(
        self,
        leave_type: str = "annual",
        language: str = "en"
    ) -> Dict[str, Any]:
        """
        Get specific leave policy information

        Args:
            leave_type: Type of leave (annual, sick, parental, etc.)
            language: Language code (en or fr)

        Returns:
            Dict with leave policy details
        """
        # Build query based on language
        if language == "fr":
            queries = {
                "annual": "Quelle est la politique de congés annuels?",
                "sick": "Quelle est la politique de congé maladie?",
                "parental": "Quelle est la politique de congé parental?",
                "bereavement": "Quelle est la politique de congé de deuil?"
            }
        else:
            queries = {
                "annual": "What is the annual leave policy?",
                "sick": "What is the sick leave policy?",
                "parental": "What is the parental leave policy?",
                "bereavement": "What is the bereavement leave policy?"
            }

        query = queries.get(leave_type, queries["annual"])
        return self.search_policies(query)

    def get_public_holidays(
        self,
        year: int = 2025,
        language: str = "en"
    ) -> Dict[str, Any]:
        """
        Get public holidays list

        Args:
            year: Year to query (default: 2025)
            language: Language code (en or fr)

        Returns:
            Dict with holiday information
        """
        # Build query based on language
        if language == "fr":
            query = f"Quels sont les jours fériés pour {year}?"
        else:
            query = f"What are the public holidays for {year}?"

        return self.search_policies(query)

    def calculate_vacation_days(
        self,
        years_of_service: float,
        is_full_time: bool = True,
        fte: float = 1.0,
        language: str = "en"
    ) -> Dict[str, Any]:
        """
        Calculate vacation days based on years of service

        Args:
            years_of_service: Number of years employed
            is_full_time: Whether employee is full-time
            fte: Full-time equivalent (0-1.0)
            language: Language code (en or fr)

        Returns:
            Dict with calculation results
        """
        # Build query with calculation request
        if language == "fr":
            query = f"Combien de jours de vacances pour un employé avec {years_of_service} ans de service"
            if not is_full_time:
                query += f" et {fte} ETP"
            query += "? Montrez le calcul."
        else:
            query = f"How many vacation days for an employee with {years_of_service} years of service"
            if not is_full_time:
                query += f" and {fte} FTE"
            query += "? Show the calculation."

        # Add calculation prompt
        calc_prompt = get_calculation_prompt("vacation", language)

        result = self.search_policies(query)

        # Add calculation metadata
        if not result.get('error'):
            result['calculation'] = {
                'years_of_service': years_of_service,
                'is_full_time': is_full_time,
                'fte': fte
            }

        return result

    def check_carryover_eligibility(
        self,
        unused_days: int,
        language: str = "en"
    ) -> Dict[str, Any]:
        """
        Check carry-over eligibility and limits

        Args:
            unused_days: Number of unused vacation days
            language: Language code (en or fr)

        Returns:
            Dict with carry-over information
        """
        # Build query based on language
        if language == "fr":
            query = f"J'ai {unused_days} jours de vacances non utilisés. Combien puis-je reporter à l'année prochaine?"
        else:
            query = f"I have {unused_days} unused vacation days. How many can I carry over to next year?"

        result = self.search_policies(query)

        # Add carry-over metadata
        if not result.get('error'):
            result['carryover_query'] = {
                'unused_days': unused_days
            }

        return result

    def get_benefits_info(
        self,
        benefit_type: str = "general",
        language: str = "en"
    ) -> Dict[str, Any]:
        """
        Get employee benefits information

        Args:
            benefit_type: Type of benefit (health, retirement, etc.)
            language: Language code (en or fr)

        Returns:
            Dict with benefits information
        """
        # Build query based on language
        if language == "fr":
            queries = {
                "general": "Quels sont les avantages sociaux offerts?",
                "health": "Quels sont les avantages en matière de santé?",
                "retirement": "Quelle est la politique de retraite?",
                "insurance": "Quelle est la couverture d'assurance?"
            }
        else:
            queries = {
                "general": "What employee benefits are offered?",
                "health": "What are the health benefits?",
                "retirement": "What is the retirement policy?",
                "insurance": "What insurance coverage is provided?"
            }

        query = queries.get(benefit_type, queries["general"])
        return self.search_policies(query)

    def get_leave_request_process(
        self,
        leave_type: str = "annual",
        language: str = "en"
    ) -> Dict[str, Any]:
        """
        Get leave request procedure

        Args:
            leave_type: Type of leave
            language: Language code (en or fr)

        Returns:
            Dict with request process information
        """
        # Build query based on language
        if language == "fr":
            query = f"Comment demander un congé {leave_type}? Quel est le processus?"
        else:
            query = f"How do I request {leave_type} leave? What is the process?"

        return self.search_policies(query)


# Convenience function for quick queries
def ask_hr_question(
    question: str,
    project_id: str,
    datastore_id: str = None
) -> str:
    """
    Quick function to ask an HR question

    Args:
        question: The HR question
        project_id: Google Cloud Project ID
        datastore_id: Optional datastore ID

    Returns:
        Answer string
    """
    agent = HRAgent(project_id=project_id, datastore_id=datastore_id)
    result = agent.search_policies(question)

    if result.get('error'):
        return f"Error: {result.get('message', 'Unknown error')}"

    return result.get('answer', 'No answer generated')
