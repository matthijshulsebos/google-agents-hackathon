"""
Domain-specific agents that wrap Vertex AI Search.
"""
import logging
from typing import List, Dict, Any, Optional
from src.ingestion.vertex_search import VertexSearchRetriever

logger = logging.getLogger(__name__)


class DomainAgent:
    """Base class for domain-specific search agents."""
    
    def __init__(self, domain: str, project_id: str, location: str, datastore_id: str, top_k: int = 5):
        self.domain = domain
        self.project_id = project_id
        self.location = location
        self.datastore_id = datastore_id
        self.top_k = top_k
        self.retriever = VertexSearchRetriever(
            project_id=project_id,
            location=location,
            datastore_id=datastore_id
        )
    
    def search(self, query: str, top_k: Optional[int] = None) -> List[Dict[str, Any]]:
        """Search for documents in this domain."""
        k = top_k if top_k is not None else self.top_k
        results = self.retriever.search(query, top_k=k)
        
        # Add domain information to results
        for result in results:
            result["domain"] = self.domain
        
        return results
    
    def format_results(self, results: List[Dict[str, Any]]) -> str:
        """Format search results for display."""
        if not results:
            return f"No results found in {self.domain} domain."
        
        formatted = [f"\n=== {self.domain.upper()} Domain Results ===\n"]
        
        for idx, result in enumerate(results, 1):
            formatted.append(f"Result {idx}:")
            formatted.append(f"Content: {result.get('content', 'N/A')[:300]}...")
            
            metadata = result.get('metadata', {})
            if metadata:
                formatted.append(f"Source: {metadata.get('filename', 'Unknown')}")
                formatted.append(f"File Type: {metadata.get('file_type', 'Unknown')}")
            
            formatted.append("")
        
        return "\n".join(formatted)


class NursingAgent(DomainAgent):
    """Agent for nursing domain queries."""
    
    def __init__(self, project_id: str, location: str, datastore_id: str, top_k: int = 5):
        super().__init__("nursing", project_id, location, datastore_id, top_k)
        self.keywords = [
            "nurse", "nursing", "patient care", "vital signs", "medication administration",
            "rounds", "shift", "assessment", "care plan", "bedside", "charting", "intake"
        ]
    
    def is_relevant(self, query: str) -> bool:
        """Check if query is relevant to nursing domain."""
        query_lower = query.lower()
        return any(keyword in query_lower for keyword in self.keywords)


class PharmacyAgent(DomainAgent):
    """Agent for pharmacy domain queries."""
    
    def __init__(self, project_id: str, location: str, datastore_id: str, top_k: int = 5):
        super().__init__("pharmacy", project_id, location, datastore_id, top_k)
        self.keywords = [
            "pharmacy", "medication", "drug", "prescription", "dosage", "pharmaceutical",
            "adverse", "interaction", "formulary", "dispense", "refill", "therapeutic"
        ]
    
    def is_relevant(self, query: str) -> bool:
        """Check if query is relevant to pharmacy domain."""
        query_lower = query.lower()
        return any(keyword in query_lower for keyword in self.keywords)


class HRAgent(DomainAgent):
    """Agent for HR (Human Resources) documents."""
    
    def __init__(self, project_id: str, location: str, datastore_id: str, top_k: int = 5):
        super().__init__("po", project_id, location, datastore_id, top_k)
        # Keywords that indicate HR queries
        self.keywords = [
            "hr", "human resources", "employee", "personnel", "staff",
            "hiring", "recruitment", "onboarding", "benefits", "payroll",
            "vacation", "leave", "training", "performance", "contract",
            "salary", "compensation", "policy", "handbook", "time off"
        ]
    
    def is_relevant(self, query: str) -> bool:
        """Check if query is relevant to HR domain."""
        query_lower = query.lower()
        return any(keyword in query_lower for keyword in self.keywords)


class AgentRegistry:
    """Registry for managing domain agents."""
    
    def __init__(self, project_id: str, location: str, config: Dict[str, Any]):
        self.project_id = project_id
        self.location = location
        self.config = config
        self.agents: Dict[str, DomainAgent] = {}
        self._initialize_agents()
    
    def _initialize_agents(self):
        """Initialize all domain agents."""
        top_k = self.config.get("retrieval", {}).get("top_k", 5)
        
        # Nursing agent
        nursing_config = self.config.get("vertex_search", {}).get("nursing", {})
        if nursing_config.get("datastore_id"):
            self.agents["nursing"] = NursingAgent(
                project_id=self.project_id,
                location=self.location,
                datastore_id=nursing_config["datastore_id"],
                top_k=top_k
            )
            logger.info("Initialized Nursing agent")
        
        # Pharmacy agent
        pharmacy_config = self.config.get("vertex_search", {}).get("pharmacy", {})
        if pharmacy_config.get("datastore_id"):
            self.agents["pharmacy"] = PharmacyAgent(
                project_id=self.project_id,
                location=self.location,
                datastore_id=pharmacy_config["datastore_id"],
                top_k=top_k
            )
            logger.info("Initialized Pharmacy agent")
        
        # HR agent
        po_config = self.config.get("vertex_search", {}).get("po", {})
        if po_config.get("datastore_id"):
            self.agents["po"] = HRAgent(
                project_id=self.project_id,
                location=self.location,
                datastore_id=po_config["datastore_id"],
                top_k=top_k
            )
            logger.info("Initialized HR agent")
    
    def get_agent(self, domain: str) -> Optional[DomainAgent]:
        """Get agent for a specific domain."""
        return self.agents.get(domain)
    
    def get_all_agents(self) -> Dict[str, DomainAgent]:
        """Get all registered agents."""
        return self.agents
    
    def get_relevant_agents(self, query: str) -> List[DomainAgent]:
        """Get agents that are relevant to the query based on keywords."""
        relevant = []
        for agent in self.agents.values():
            if hasattr(agent, 'is_relevant') and agent.is_relevant(query):
                relevant.append(agent)
        return relevant if relevant else list(self.agents.values())
