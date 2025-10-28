"""
Query classification utilities for routing to specialized agents
"""
from typing import Dict, Any, Optional
from google import genai
from google.genai import types
import logging
from config import config

logger = logging.getLogger(__name__)


CLASSIFICATION_PROMPT = """Analyze the following query and classify it into ONE category:

Categories:
- nursing: Medical procedures, nursing protocols, patient care, clinical procedures, IV insertion, wound care, medication administration, vital signs
- hr: Holidays, vacation, benefits, HR policies, employment questions, workplace policies, leave requests, sick leave, parental leave, time off
- pharmacy: Medications, drug inventory, prescriptions, pharmaceutical information, medication availability, drug storage, controlled substances

Examples:
- "How do I insert an IV?" → nursing
- "How many vacation days do I have?" → hr
- "Is ibuprofen available?" → pharmacy
- "¿Cuántos días festivos tenemos?" → hr
- "Protocole pour administration médicament?" → nursing
- "Ist Paracetamol auf Lager?" → pharmacy
- "¿Cómo curar una herida?" → nursing
- "Combien de jours de congé?" → hr
- "Welche Antibiotika sind verfügbar?" → pharmacy

Query: {query}

Respond with ONLY the category name: nursing, hr, or pharmacy
No explanation, just the category word."""


class QueryClassifier:
    """
    Classifies user queries to route to appropriate specialized agent
    """

    def __init__(
        self,
        project_id: str,
        location: str = "us-central1",
        model_name: str = None
    ):
        """
        Initialize query classifier

        Args:
            project_id: Google Cloud Project ID
            location: GCP location
            model_name: Gemini model to use
        """
        self.project_id = project_id
        self.location = location
        self.model_name = model_name or config.MODEL_NAME

        try:
            self.client = genai.Client(
                vertexai=True,
                project=self.project_id,
                location=self.location
            )
            logger.info("Query classifier initialized")
        except Exception as e:
            logger.error(f"Failed to initialize query classifier: {str(e)}")
            raise

    def classify(
        self,
        query: str,
        use_keywords: bool = True
    ) -> Dict[str, Any]:
        """
        Classify a query into one of the agent categories

        Args:
            query: User query to classify
            use_keywords: Whether to use keyword-based classification first (faster)

        Returns:
            Dict with:
                - category: Agent category (nursing, hr, pharmacy)
                - confidence: Confidence level (high, medium, low)
                - method: Classification method used (keywords, gemini)
        """
        try:
            # Try keyword-based classification first (faster)
            if use_keywords:
                keyword_result = self._classify_by_keywords(query)
                if keyword_result['confidence'] == 'high':
                    logger.info(f"Query classified by keywords: {keyword_result['category']}")
                    return keyword_result

            # Fall back to Gemini-based classification
            gemini_result = self._classify_by_gemini(query)
            logger.info(f"Query classified by Gemini: {gemini_result['category']}")
            return gemini_result

        except Exception as e:
            logger.error(f"Error classifying query: {str(e)}")
            # Return default classification
            return {
                "category": "hr",  # Default to HR as it's most general
                "confidence": "low",
                "method": "fallback",
                "error": str(e)
            }

    def _classify_by_keywords(self, query: str) -> Dict[str, Any]:
        """
        Fast keyword-based classification

        Args:
            query: User query

        Returns:
            Classification result
        """
        query_lower = query.lower()

        # Define keyword sets for each category
        nursing_keywords = [
            'iv', 'intravenous', 'vía', 'wound', 'herida', 'dressing', 'apósito',
            'patient', 'paciente', 'procedure', 'procedimiento', 'protocol', 'protocolo',
            'nursing', 'enfermería', 'vital signs', 'signos vitales', 'medication administration',
            'curar', 'cuidado', 'insertar', 'administrar medicamento'
        ]

        hr_keywords = [
            'vacation', 'holiday', 'leave', 'congé', 'vacances', 'días', 'jours',
            'benefits', 'policy', 'policies', 'hr', 'employee', 'empleado',
            'sick leave', 'parental', 'time off', 'request', 'avantages',
            'urlaub', 'ferien', 'politique', 'beneficios'
        ]

        pharmacy_keywords = [
            'medication', 'drug', 'pharmacy', 'stock', 'inventory', 'available',
            'ibuprofen', 'acetaminophen', 'paracetamol', 'insulin', 'antibiotic',
            'medikament', 'apotheke', 'lager', 'verfügbar', 'auf lager',
            'médicament', 'pharmacie', 'disponible', 'medicamento', 'farmacia'
        ]

        # Count matches
        nursing_score = sum(1 for kw in nursing_keywords if kw in query_lower)
        hr_score = sum(1 for kw in hr_keywords if kw in query_lower)
        pharmacy_score = sum(1 for kw in pharmacy_keywords if kw in query_lower)

        # Determine category based on scores
        max_score = max(nursing_score, hr_score, pharmacy_score)

        if max_score == 0:
            # No keywords matched
            return {
                "category": "hr",  # Default
                "confidence": "low",
                "method": "keywords",
                "scores": {
                    "nursing": nursing_score,
                    "hr": hr_score,
                    "pharmacy": pharmacy_score
                }
            }

        # Determine confidence based on score difference
        scores = [nursing_score, hr_score, pharmacy_score]
        scores.sort(reverse=True)
        score_diff = scores[0] - scores[1]

        confidence = "high" if score_diff >= 2 else "medium" if score_diff >= 1 else "low"

        if max_score == nursing_score:
            category = "nursing"
        elif max_score == hr_score:
            category = "hr"
        else:
            category = "pharmacy"

        return {
            "category": category,
            "confidence": confidence,
            "method": "keywords",
            "scores": {
                "nursing": nursing_score,
                "hr": hr_score,
                "pharmacy": pharmacy_score
            }
        }

    def _classify_by_gemini(self, query: str) -> Dict[str, Any]:
        """
        Use Gemini to classify the query

        Args:
            query: User query

        Returns:
            Classification result
        """
        try:
            # Format classification prompt
            prompt = CLASSIFICATION_PROMPT.format(query=query)

            # Generate classification
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=0.1,  # Low temperature for consistent classification
                )
            )

            # Extract category from response
            category_text = response.text.strip().lower()

            # Validate category
            valid_categories = ["nursing", "hr", "pharmacy"]
            category = None

            for valid_cat in valid_categories:
                if valid_cat in category_text:
                    category = valid_cat
                    break

            if not category:
                # If no valid category found, default to hr
                logger.warning(f"Invalid category from Gemini: {category_text}, defaulting to hr")
                category = "hr"

            return {
                "category": category,
                "confidence": "high",  # Gemini classifications are generally reliable
                "method": "gemini",
                "raw_response": category_text
            }

        except Exception as e:
            logger.error(f"Error in Gemini classification: {str(e)}")
            return {
                "category": "hr",
                "confidence": "low",
                "method": "gemini_error",
                "error": str(e)
            }

    def get_routing_suggestion(
        self,
        query: str,
        user_role: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get routing suggestion with user role consideration

        Args:
            query: User query
            user_role: Optional user role (nurse, employee, pharmacist)

        Returns:
            Routing suggestion with category and confidence
        """
        # If user role is provided, use it for direct routing
        if user_role:
            role_mapping = {
                "nurse": "nursing",
                "employee": "hr",
                "pharmacist": "pharmacy"
            }

            if user_role.lower() in role_mapping:
                return {
                    "category": role_mapping[user_role.lower()],
                    "confidence": "high",
                    "method": "user_role",
                    "user_role": user_role
                }

        # Otherwise, classify the query
        return self.classify(query)
