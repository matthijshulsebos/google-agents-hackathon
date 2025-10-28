"""
Hospital Multi-Agent Orchestrator
Routes queries to specialized agents (Nursing, HR, Pharmacy)
"""
from typing import Dict, Any, Optional, List
import logging
from datetime import datetime

from config import config
from utils.query_classifier import QueryClassifier
from agents.nursing_agent import NursingAgent
from agents.hr_agent import HRAgent
from agents.pharmacy_agent import PharmacyAgent
from agents.help_agent import HelpAgent

# Set up logging
logging.basicConfig(
    level=getattr(logging, config.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class HospitalOrchestrator:
    """
    Main orchestrator for hospital multi-agent system
    Intelligently routes queries to specialized agents
    """

    def __init__(
        self,
        project_id: str = None,
        location: str = "us-central1",
        nursing_datastore_id: str = None,
        hr_datastore_id: str = None,
        pharmacy_datastore_id: str = None
    ):
        """
        Initialize Hospital Orchestrator

        Args:
            project_id: Google Cloud Project ID (uses config if not provided)
            location: GCP location
            nursing_datastore_id: Nursing datastore ID (uses config if not provided)
            hr_datastore_id: HR datastore ID (uses config if not provided)
            pharmacy_datastore_id: Pharmacy datastore ID (uses config if not provided)
        """
        self.project_id = project_id or config.PROJECT_ID
        self.location = location

        # Validate configuration
        try:
            config.validate()
        except ValueError as e:
            logger.error(f"Configuration validation failed: {str(e)}")
            raise

        # Initialize query classifier
        self.classifier = QueryClassifier(
            project_id=self.project_id,
            location=self.location
        )

        # Initialize specialized agents
        self.nursing_agent = NursingAgent(
            project_id=self.project_id,
            datastore_id=nursing_datastore_id,
            location=self.location
        )

        self.hr_agent = HRAgent(
            project_id=self.project_id,
            datastore_id=hr_datastore_id,
            location=self.location
        )

        self.pharmacy_agent = PharmacyAgent(
            project_id=self.project_id,
            datastore_id=pharmacy_datastore_id,
            location=self.location
        )

        # Initialize help/onboarding agent (Priority 1 - no datastore needed)
        self.help_agent = HelpAgent(
            project_id=self.project_id,
            location=self.location
        )

        # Agent routing map
        self.agents = {
            "nursing": self.nursing_agent,
            "hr": self.hr_agent,
            "pharmacy": self.pharmacy_agent,
            "help": self.help_agent
        }

        logger.info("Hospital Orchestrator initialized with all agents (including Help Agent)")

    def process_query(
        self,
        query: str,
        user_role: Optional[str] = None,
        agent_override: Optional[str] = None,
        conversation_history: Optional[List[Dict[str, str]]] = None
    ) -> Dict[str, Any]:
        """
        Process a user query and route to appropriate agent

        Args:
            query: User's question
            user_role: Optional user role (nurse, employee, pharmacist)
            agent_override: Optional agent to use directly (nursing, hr, pharmacy)
            conversation_history: Optional conversation history for context
                Format: [{"role": "user", "content": "..."}, {"role": "assistant", "content": "..."}]

        Returns:
            Dict with:
                - answer: Generated response
                - agent: Agent that handled the query
                - routing_info: Information about how query was routed
                - grounding_metadata: Citations and sources
                - query: Original query
                - timestamp: Processing timestamp
        """
        timestamp = datetime.utcnow().isoformat()

        try:
            logger.info(f"Processing query: {query[:50]}...")

            # PRIORITY 1: Check if this is a help/onboarding query
            # Help queries are checked FIRST before any domain routing
            if not agent_override and HelpAgent.is_help_query(query):
                logger.info("Detected help/onboarding query - routing to Help Agent (Priority 1)")
                agent_category = "help"
                routing_info = {
                    "method": "help_detection",
                    "category": "help",
                    "confidence": "high",
                    "priority": 1
                }
            # PRIORITY 2: Domain routing (nursing, hr, pharmacy)
            elif agent_override:
                # Direct routing via override
                agent_category = agent_override.lower()
                routing_info = {
                    "method": "override",
                    "category": agent_category,
                    "confidence": "explicit",
                    "priority": 2
                }
                logger.info(f"Using agent override: {agent_category}")

            else:
                # Classify query to determine routing
                routing_info = self.classifier.get_routing_suggestion(
                    query=query,
                    user_role=user_role
                )
                routing_info["priority"] = 2
                agent_category = routing_info['category']
                logger.info(f"Routing to {agent_category} (method: {routing_info['method']}, "
                           f"confidence: {routing_info['confidence']})")

            # Get the appropriate agent
            agent = self.agents.get(agent_category)

            if not agent:
                logger.error(f"Invalid agent category: {agent_category}")
                return {
                    "error": True,
                    "message": f"Invalid agent category: {agent_category}",
                    "query": query,
                    "timestamp": timestamp
                }

            # Route to agent based on category
            if agent_category == "help":
                result = agent.provide_guidance(query)
            elif agent_category == "nursing":
                result = agent.search_protocols(query, conversation_history=conversation_history)
            elif agent_category == "hr":
                result = agent.search_policies(query, conversation_history=conversation_history)
            elif agent_category == "pharmacy":
                result = agent.search_inventory(query, conversation_history=conversation_history)
            else:
                result = {
                    "error": True,
                    "message": f"Unknown agent category: {agent_category}"
                }

            # Add orchestrator metadata
            result['routing_info'] = routing_info
            result['timestamp'] = timestamp

            # Log successful processing
            logger.info(f"Query processed successfully by {agent_category} agent")

            return result

        except Exception as e:
            logger.error(f"Error processing query: {str(e)}")
            return {
                "error": True,
                "message": str(e),
                "query": query,
                "timestamp": timestamp
            }

    def multi_agent_query(
        self,
        query: str,
        agents: List[str] = None
    ) -> Dict[str, Any]:
        """
        Query multiple agents and combine results (advanced feature)

        Args:
            query: User's question
            agents: List of agent names to query (default: all agents)

        Returns:
            Dict with results from multiple agents
        """
        timestamp = datetime.utcnow().isoformat()

        if agents is None:
            agents = ["nursing", "hr", "pharmacy"]

        results = {}

        for agent_name in agents:
            logger.info(f"Querying {agent_name} agent...")

            try:
                result = self.process_query(
                    query=query,
                    agent_override=agent_name
                )
                results[agent_name] = result

            except Exception as e:
                logger.error(f"Error querying {agent_name}: {str(e)}")
                results[agent_name] = {
                    "error": True,
                    "message": str(e)
                }

        return {
            "query": query,
            "multi_agent_results": results,
            "timestamp": timestamp
        }

    def health_check(self) -> Dict[str, Any]:
        """
        Perform health check on all components

        Returns:
            Dict with health status of all agents
        """
        health_status = {
            "orchestrator": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "agents": {}
        }

        # Check each agent
        for agent_name, agent in self.agents.items():
            try:
                # Help agent doesn't use RAG pipeline (no document search)
                if agent_name == "help":
                    health_status["agents"][agent_name] = {
                        "healthy": True,
                        "agent_type": agent.agent_type,
                        "implementation": "Gemini Direct (no RAG)",
                        "note": "Help agent provides guidance, not document search"
                    }
                # Check if agent has RAG pipeline initialized
                elif hasattr(agent, 'rag') and agent.rag:
                    health_status["agents"][agent_name] = {
                        "healthy": True,
                        "agent_type": agent.agent_type,
                        "search_engine": agent.datastore_id,
                        "implementation": "RAG Pipeline"
                    }
                else:
                    # Legacy agents or not properly initialized
                    health_status["agents"][agent_name] = {
                        "healthy": False,
                        "error": "Agent not properly initialized (missing RAG pipeline)"
                    }
            except Exception as e:
                logger.error(f"Health check failed for {agent_name}: {str(e)}")
                health_status["agents"][agent_name] = {
                    "healthy": False,
                    "error": str(e)
                }

        # Overall health
        all_healthy = all(
            agent_status.get("healthy", False)
            for agent_status in health_status["agents"].values()
        )

        health_status["orchestrator"] = "healthy" if all_healthy else "degraded"

        return health_status

    def get_agent_info(self) -> Dict[str, Any]:
        """
        Get information about available agents

        Returns:
            Dict with agent information
        """
        return {
            "available_agents": list(self.agents.keys()),
            "project_id": self.project_id,
            "location": self.location,
            "agents": {
                "help": {
                    "name": "Help/Onboarding Agent",
                    "languages": ["English", "Spanish", "French", "German"],
                    "specialization": "System guidance, onboarding, example questions",
                    "priority": 1,
                    "note": "Handles 'how to use' queries BEFORE domain routing"
                },
                "nursing": {
                    "name": "Nursing Agent",
                    "languages": ["English", "Spanish"],
                    "specialization": "Medical procedures, protocols, patient care",
                    "priority": 2
                },
                "hr": {
                    "name": "HR Agent",
                    "languages": ["English", "French"],
                    "specialization": "Policies, benefits, leave management",
                    "priority": 2
                },
                "pharmacy": {
                    "name": "Pharmacy Agent",
                    "languages": ["English", "German"],
                    "specialization": "Medication inventory, drug information",
                    "priority": 2
                }
            }
        }

    def format_response(
        self,
        result: Dict[str, Any],
        include_metadata: bool = True
    ) -> str:
        """
        Format orchestrator response for display

        Args:
            result: Result dict from process_query
            include_metadata: Whether to include metadata in output

        Returns:
            Formatted string response
        """
        if result.get('error'):
            return f"Error: {result.get('message', 'Unknown error occurred')}"

        output = []

        # Main answer
        output.append("=" * 60)
        output.append(result.get('answer', 'No answer generated'))
        output.append("=" * 60)

        if include_metadata:
            # Agent info
            agent = result.get('agent', 'unknown')
            language = result.get('language', 'unknown')
            output.append(f"\nAgent: {agent.title()}")
            output.append(f"Language: {language.upper()}")

            # Routing info
            routing = result.get('routing_info', {})
            if routing:
                output.append(f"Routing: {routing.get('method', 'unknown')} "
                            f"(confidence: {routing.get('confidence', 'unknown')})")

            # Citations
            grounding = result.get('grounding_metadata')
            if grounding and len(grounding) > 0:
                output.append(f"\nSources: {len(grounding)} documents cited")

        return "\n".join(output)


# Convenience function for quick queries
def ask_hospital_question(
    question: str,
    user_role: Optional[str] = None
) -> str:
    """
    Quick function to ask a hospital question

    Args:
        question: The question to ask
        user_role: Optional user role

    Returns:
        Answer string
    """
    try:
        orchestrator = HospitalOrchestrator()
        result = orchestrator.process_query(question, user_role=user_role)
        return orchestrator.format_response(result)
    except Exception as e:
        return f"Error: {str(e)}"
