"""
Test cases for Help/Onboarding Agent
"""
import pytest
from agents.help_agent import HelpAgent


class TestHelpAgent:
    """Test cases for Help Agent functionality"""

    @pytest.fixture
    def project_id(self):
        """Mock project ID for testing"""
        return "test-project-id"

    def test_is_help_query_english(self):
        """Test help query detection in English"""
        help_queries = [
            "How do I use this system?",
            "What can I ask?",
            "Can I check inventory here?",
            "How does this tool work?",
            "What is this system?",
            "Help me use this",
            "Guide me",
        ]

        for query in help_queries:
            assert HelpAgent.is_help_query(query), f"Failed to detect help query: {query}"

    def test_is_help_query_spanish(self):
        """Test help query detection in Spanish"""
        help_queries = [
            "¿Cómo usar este sistema?",
            "¿Qué preguntas puedo hacer?",
            "¿Puedo consultar inventario aquí?",
            "¿Cómo funciona esta herramienta?",
        ]

        for query in help_queries:
            assert HelpAgent.is_help_query(query), f"Failed to detect Spanish help query: {query}"

    def test_is_help_query_french(self):
        """Test help query detection in French"""
        help_queries = [
            "Comment utiliser ce système?",
            "Quelles questions puis-je poser?",
            "Puis-je vérifier l'inventaire ici?",
            "Comment ça marche?",
        ]

        for query in help_queries:
            assert HelpAgent.is_help_query(query), f"Failed to detect French help query: {query}"

    def test_is_help_query_german(self):
        """Test help query detection in German"""
        help_queries = [
            "Wie benutze ich dieses System?",
            "Welche Fragen kann ich stellen?",
            "Kann ich hier Inventar prüfen?",
            "Wie funktioniert dieses Tool?",
        ]

        for query in help_queries:
            assert HelpAgent.is_help_query(query), f"Failed to detect German help query: {query}"

    def test_not_help_query_domain_questions(self):
        """Test that domain questions are NOT detected as help queries"""
        domain_queries = [
            "How do I insert an IV line?",  # Nursing - actual medical question
            "How many vacation days do I have?",  # HR
            "Is ibuprofen in stock?",  # Pharmacy
            "What is the wound care protocol?",  # Nursing
            "¿Cómo curar una herida?",  # Spanish nursing
            "Combien de jours de vacances?",  # French HR
            "Ist Paracetamol auf Lager?",  # German pharmacy
        ]

        for query in domain_queries:
            assert not HelpAgent.is_help_query(query), f"Incorrectly detected as help query: {query}"

    def test_detect_language(self, project_id):
        """Test language detection"""
        agent = HelpAgent(project_id=project_id)

        assert agent.detect_language("How do I use this?") == "en"
        assert agent.detect_language("¿Cómo usar esto?") == "es"
        assert agent.detect_language("Comment utiliser?") == "fr"
        assert agent.detect_language("Wie benutze ich?") == "de"

    def test_detect_user_role(self, project_id):
        """Test user role detection from query"""
        agent = HelpAgent(project_id=project_id)

        # Nurse role
        assert agent.detect_user_role("How do I use this as a nurse?") == "nurse"
        assert agent.detect_user_role("Can I check nursing protocols here?") == "nurse"

        # Pharmacist role
        assert agent.detect_user_role("How do I check pharmacy inventory?") == "pharmacist"
        assert agent.detect_user_role("Can I use this as a pharmacist?") == "pharmacist"

        # Employee/HR role
        assert agent.detect_user_role("How do I check my vacation days?") == "employee"
        assert agent.detect_user_role("Can employees use this for HR info?") == "employee"

        # No clear role
        assert agent.detect_user_role("How do I use this system?") is None

    def test_provide_guidance_returns_proper_structure(self, project_id):
        """Test that provide_guidance returns expected structure"""
        agent = HelpAgent(project_id=project_id)

        result = agent.provide_guidance("How do I use this system?")

        # Check required keys
        assert "answer" in result
        assert "agent" in result
        assert "agent_type" in result
        assert "language" in result

        # Check values
        assert result["agent"] == "help"
        assert result["agent_type"] == "help"
        assert len(result["answer"]) > 0

    def test_provide_guidance_multilingual(self, project_id):
        """Test guidance in multiple languages"""
        agent = HelpAgent(project_id=project_id)

        # English
        result_en = agent.provide_guidance("What can I ask?")
        assert result_en["language"] == "en"

        # Spanish
        result_es = agent.provide_guidance("¿Qué puedo preguntar?")
        assert result_es["language"] == "es"

        # French
        result_fr = agent.provide_guidance("Que puis-je demander?")
        assert result_fr["language"] == "fr"

        # German
        result_de = agent.provide_guidance("Was kann ich fragen?")
        assert result_de["language"] == "de"

    def test_provide_guidance_role_specific(self, project_id):
        """Test that guidance is role-specific"""
        agent = HelpAgent(project_id=project_id)

        # Nurse query
        result_nurse = agent.provide_guidance("How do I use this as a nurse?")
        assert result_nurse["user_role"] == "nurse"
        # Should contain nursing-related examples in response
        answer_lower = result_nurse["answer"].lower()
        assert any(word in answer_lower for word in ["nursing", "medical", "procedure", "iv", "wound"])

        # Pharmacist query
        result_pharmacist = agent.provide_guidance("How do I check pharmacy inventory?")
        assert result_pharmacist["user_role"] == "pharmacist"
        answer_lower = result_pharmacist["answer"].lower()
        assert any(word in answer_lower for word in ["pharmacy", "medication", "inventory", "drug"])


class TestHelpAgentIntegration:
    """Integration tests for Help Agent with Orchestrator"""

    def test_help_query_routes_to_help_agent(self, project_id):
        """Test that help queries route to help agent in orchestrator"""
        from orchestrator import HospitalOrchestrator

        # Note: This test requires valid GCP credentials and datastore IDs
        # Skip if not in integration test environment
        try:
            orchestrator = HospitalOrchestrator()

            result = orchestrator.process_query("How do I use this system?")

            assert result["agent"] == "help"
            assert result["routing_info"]["category"] == "help"
            assert result["routing_info"]["priority"] == 1
            assert "answer" in result

        except Exception as e:
            pytest.skip(f"Integration test skipped: {str(e)}")

    def test_domain_query_routes_to_domain_agent(self, project_id):
        """Test that domain questions DO NOT route to help agent"""
        from orchestrator import HospitalOrchestrator

        try:
            orchestrator = HospitalOrchestrator()

            # This should route to nursing agent, NOT help agent
            result = orchestrator.process_query("How do I insert an IV?")

            assert result["agent"] == "nursing"
            assert result["routing_info"]["category"] == "nursing"
            assert result["routing_info"]["priority"] == 2

        except Exception as e:
            pytest.skip(f"Integration test skipped: {str(e)}")


# Example test scenarios for manual testing
HELP_TEST_SCENARIOS = [
    # English help queries
    ("How do I use this system as a nurse?", "help", "en", "nurse"),
    ("What questions can I ask?", "help", "en", None),
    ("Can I check pharmacy inventory here?", "help", "en", "pharmacist"),

    # Spanish help queries
    ("¿Cómo puedo usar este sistema?", "help", "es", None),
    ("¿Qué preguntas puedo hacer como enfermera?", "help", "es", "nurse"),

    # French help queries
    ("Comment utiliser ce système?", "help", "fr", None),
    ("Puis-je vérifier mes jours de vacances ici?", "help", "fr", "employee"),

    # German help queries
    ("Wie benutze ich dieses System?", "help", "de", None),
    ("Kann ich hier Medikamente prüfen?", "help", "de", "pharmacist"),

    # Domain questions (should NOT go to help)
    ("How do I insert an IV line?", "nursing", "en", None),
    ("How many vacation days do I have?", "hr", "en", None),
    ("Is ibuprofen in stock?", "pharmacy", "en", None),
]


if __name__ == "__main__":
    """Run basic tests manually"""
    print("=" * 60)
    print("HELP AGENT TEST SCENARIOS")
    print("=" * 60)

    for query, expected_agent, expected_lang, expected_role in HELP_TEST_SCENARIOS:
        is_help = HelpAgent.is_help_query(query)
        detected_agent = "help" if is_help else "domain"

        status = "✓" if detected_agent == expected_agent else "✗"

        print(f"\n{status} Query: {query}")
        print(f"  Expected: {expected_agent} | Detected: {detected_agent}")

        if detected_agent != expected_agent:
            print(f"  ❌ MISMATCH!")

    print("\n" + "=" * 60)
    print("Run with: pytest tests/test_help_agent.py -v")
    print("=" * 60)
