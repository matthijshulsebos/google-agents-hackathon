"""
Help/Onboarding Agent - Guides users on how to use the system
This agent does NOT answer domain questions, only provides guidance
"""
from typing import Dict, Any, Optional
import logging
from google import genai
from google.genai import types
from config import config
from agents.prompts.help_prompts import (
    HELP_SYSTEM_INSTRUCTION,
    format_help_response,
    get_help_examples_by_role
)

logger = logging.getLogger(__name__)


class HelpAgent:
    """
    Agent specialized in helping users understand how to use the system
    Does NOT answer domain questions - only provides guidance and examples
    Handles queries in English, Spanish, French, and German
    """

    def __init__(
        self,
        project_id: str,
        location: str = "us-central1"
    ):
        """
        Initialize Help Agent

        Args:
            project_id: Google Cloud Project ID
            location: GCP location
        """
        self.project_id = project_id
        self.location = location
        self.agent_type = "help"

        # Initialize Gemini client
        try:
            self.client = genai.Client(
                vertexai=True,
                project=self.project_id,
                location=self.location
            )
            logger.info("Help Agent initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Help Agent: {str(e)}")
            raise

    def detect_language(self, text: str) -> str:
        """
        Detect query language

        Args:
            text: Query text

        Returns:
            Language code (en, es, fr, de)
        """
        text_lower = text.lower()

        # Spanish
        if any(word in text_lower for word in ['¿', '¡', 'cómo', 'cuál', 'puedo', 'usar', 'sistema']):
            return "es"
        # French
        elif any(word in text_lower for word in ['comment', 'puis-je', 'utiliser', 'système', 'combien']):
            return "fr"
        # German
        elif any(word in text_lower for word in ['wie', 'kann', 'ich', 'system', 'benutzen']):
            return "de"

        return "en"

    def detect_user_role(self, query: str) -> Optional[str]:
        """
        Try to detect user role from query

        Args:
            query: User query

        Returns:
            Role string (nurse, employee, pharmacist) or None
        """
        query_lower = query.lower()

        # Nurse indicators
        if any(word in query_lower for word in [
            'nurse', 'nursing', 'enfermera', 'enfermería', 'infirmier', 'infirmière',
            'krankenschwester', 'pflege', 'medical', 'patient', 'clinical'
        ]):
            return "nurse"

        # Pharmacist indicators
        if any(word in query_lower for word in [
            'pharmacist', 'pharmacy', 'farmacia', 'pharmacie', 'apotheke',
            'apotheker', 'medication', 'drug', 'inventory', 'stock'
        ]):
            return "pharmacist"

        # HR/Employee indicators
        if any(word in query_lower for word in [
            'employee', 'hr', 'vacation', 'holiday', 'leave', 'benefits',
            'empleado', 'vacaciones', 'congé', 'urlaub', 'mitarbeiter'
        ]):
            return "employee"

        return None

    def provide_guidance(
        self,
        query: str,
        temperature: float = 0.3
    ) -> Dict[str, Any]:
        """
        Provide guidance on how to use the system

        Args:
            query: User's help/onboarding question
            temperature: Model temperature

        Returns:
            Dict with guidance response and metadata
        """
        try:
            # Detect language and role
            language = self.detect_language(query)
            user_role = self.detect_user_role(query)

            logger.info(f"Help query - Language: {language}, Role: {user_role}")

            # Check if this is a simple "how to use" question
            # If so, return templated response (faster)
            if self._is_simple_help_query(query):
                answer = format_help_response(role=user_role, language=language)

                return {
                    "answer": answer,
                    "agent": "help",
                    "agent_type": "help",
                    "language": language,
                    "user_role": user_role,
                    "method": "template",
                    "grounding_metadata": []
                }

            # For more complex questions, use Gemini
            # Build context-aware system instruction
            system_instruction = HELP_SYSTEM_INSTRUCTION

            if user_role:
                system_instruction += f"\n\nThe user appears to be a {user_role}. Tailor your guidance accordingly."

            system_instruction += f"\n\nRespond in {self._get_language_name(language)}."

            # Add examples for context
            examples_data = get_help_examples_by_role(user_role, language)
            system_instruction += f"\n\nHere are some example questions for this role:\n"
            for example in examples_data['examples']:
                system_instruction += f"- {example}\n"

            # Generate response using Gemini
            response = self.client.models.generate_content(
                model=config.MODEL_NAME,
                contents=query,
                config=types.GenerateContentConfig(
                    system_instruction=system_instruction,
                    temperature=temperature,
                )
            )

            answer = response.text

            return {
                "answer": answer,
                "agent": "help",
                "agent_type": "help",
                "language": language,
                "user_role": user_role,
                "method": "gemini",
                "grounding_metadata": []
            }

        except Exception as e:
            logger.error(f"Error in help agent: {str(e)}")
            return {
                "error": True,
                "message": f"Help agent error: {str(e)}",
                "agent": "help",
                "agent_type": "help"
            }

    def _is_simple_help_query(self, query: str) -> bool:
        """
        Check if query is a simple help question that can use template

        Args:
            query: User query

        Returns:
            True if simple help query
        """
        query_lower = query.lower()

        simple_patterns = [
            'how to use',
            'how do i use',
            'can i use',
            'what can i ask',
            'help',
            'guide',
            'cómo usar',
            'puedo usar',
            'qué preguntas',
            'comment utiliser',
            'puis-je utiliser',
            'wie benutze',
            'kann ich'
        ]

        return any(pattern in query_lower for pattern in simple_patterns)

    def _get_language_name(self, code: str) -> str:
        """Get full language name from code"""
        names = {
            "en": "English",
            "es": "Spanish",
            "fr": "French",
            "de": "German"
        }
        return names.get(code, "English")

    @staticmethod
    def is_help_query(query: str) -> bool:
        """
        Static method to detect if a query is asking for help/guidance
        This is used by the orchestrator for Priority 1 routing

        Args:
            query: User query

        Returns:
            True if query is asking for help about using the system
        """
        query_lower = query.lower()

        # Help/guidance indicators
        help_patterns = [
            # English
            'how to use', 'how do i use', 'how can i use',
            'what can i ask', 'what questions can i ask',
            'can i check', 'can i find', 'can i get',
            'how does this work', 'how does this tool work',
            'what is this', 'what does this do',
            'help me', 'guide me', 'show me how',

            # Spanish
            'cómo usar', 'cómo puedo usar', 'cómo utilizar',
            'qué preguntas puedo', 'qué puedo preguntar',
            'puedo consultar', 'puedo verificar',
            'cómo funciona', 'ayúdame', 'guíame',

            # French
            'comment utiliser', 'comment puis-je utiliser',
            'quelles questions puis-je', 'que puis-je demander',
            'puis-je vérifier', 'puis-je consulter',
            'comment ça marche', 'aidez-moi', 'guidez-moi',

            # German
            'wie benutze', 'wie kann ich', 'wie verwende',
            'welche fragen kann ich', 'was kann ich fragen',
            'kann ich prüfen', 'kann ich überprüfen',
            'wie funktioniert', 'hilf mir', 'zeig mir'
        ]

        # System reference words (indicates asking about the system itself)
        system_refs = [
            'system', 'tool', 'chat', 'chatbot', 'assistant',
            'sistema', 'herramienta', 'asistente',
            'système', 'outil',
            'werkzeug'
        ]

        # Check for help patterns
        has_help_pattern = any(pattern in query_lower for pattern in help_patterns)

        # Check for system reference (asking about the tool itself)
        has_system_ref = any(ref in query_lower for ref in system_refs)

        # Consider it a help query if:
        # 1. Has explicit help pattern, OR
        # 2. Has both question word + system reference
        if has_help_pattern:
            return True

        # Check for question word + system reference pattern
        question_words = ['how', 'what', 'can', 'cómo', 'qué', 'puedo', 'comment', 'que', 'puis-je', 'wie', 'was', 'kann']
        has_question = any(word in query_lower.split() for word in question_words)

        if has_question and has_system_ref:
            return True

        return False
