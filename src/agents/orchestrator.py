"""
Orchestrator agent for routing queries and aggregating results.
"""
import logging
from typing import List, Dict, Any, Optional
from src.agents.domain_agents import AgentRegistry, DomainAgent

logger = logging.getLogger(__name__)


class QueryRouter:
    """Router for determining which domains to query."""
    
    def __init__(self, agent_registry: AgentRegistry):
        self.agent_registry = agent_registry
    
    def route_query(self, query: str, routing_strategy: str = "keyword") -> List[str]:
        """
        Route query to appropriate domains.
        
        Args:
            query: User query
            routing_strategy: "keyword", "all", or "llm"
        
        Returns:
            List of domain names to query
        """
        if routing_strategy == "all":
            return list(self.agent_registry.get_all_agents().keys())
        
        elif routing_strategy == "keyword":
            # Use keyword-based routing
            relevant_agents = self.agent_registry.get_relevant_agents(query)
            return [agent.domain for agent in relevant_agents]
        
        elif routing_strategy == "llm":
            # TODO: Implement LLM-based routing for complex queries
            # For now, fall back to keyword routing
            logger.info("LLM routing not yet implemented, using keyword routing")
            relevant_agents = self.agent_registry.get_relevant_agents(query)
            return [agent.domain for agent in relevant_agents]
        
        else:
            # Default to querying all domains
            return list(self.agent_registry.get_all_agents().keys())


class ResultAggregator:
    """Aggregator for combining results from multiple domains."""
    
    @staticmethod
    def aggregate_results(domain_results: Dict[str, List[Dict[str, Any]]], 
                         max_results: int = 10) -> List[Dict[str, Any]]:
        """
        Aggregate results from multiple domains.
        
        Args:
            domain_results: Dictionary mapping domain names to their search results
            max_results: Maximum number of results to return
        
        Returns:
            Aggregated and sorted list of results
        """
        all_results = []
        
        for domain, results in domain_results.items():
            for result in results:
                result["domain"] = domain
                all_results.append(result)
        
        # Sort by relevance score if available
        all_results.sort(key=lambda x: x.get("score", 0.0), reverse=True)
        
        return all_results[:max_results]
    
    @staticmethod
    def format_aggregated_results(results: List[Dict[str, Any]]) -> str:
        """Format aggregated results for display."""
        if not results:
            return "No results found across any domain."
        
        formatted = ["\n=== Search Results Across All Domains ===\n"]
        
        current_domain = None
        for idx, result in enumerate(results, 1):
            domain = result.get("domain", "Unknown")
            
            # Add domain header if switching domains
            if domain != current_domain:
                formatted.append(f"\n--- {domain.upper()} Domain ---\n")
                current_domain = domain
            
            formatted.append(f"Result {idx}:")
            formatted.append(f"Content: {result.get('content', 'N/A')[:300]}...")
            
            metadata = result.get('metadata', {})
            if metadata:
                formatted.append(f"Source: {metadata.get('filename', 'Unknown')}")
                formatted.append(f"File Type: {metadata.get('file_type', 'Unknown')}")
            
            formatted.append("")
        
        return "\n".join(formatted)


class OrchestratorAgent:
    """Main orchestrator for managing multi-domain queries."""
    
    def __init__(self, agent_registry: AgentRegistry, default_strategy: str = "keyword"):
        self.agent_registry = agent_registry
        self.router = QueryRouter(agent_registry)
        self.aggregator = ResultAggregator()
        self.default_strategy = default_strategy
        
        # Conversation history
        self.conversations: Dict[str, List[Dict[str, Any]]] = {}
    
    def process_query(self, 
                     query: str, 
                     conversation_id: Optional[str] = None,
                     routing_strategy: Optional[str] = None,
                     top_k: int = 5) -> Dict[str, Any]:
        """
        Process a query across relevant domains.
        
        Args:
            query: User query
            conversation_id: Optional conversation ID for multi-turn
            routing_strategy: Optional routing strategy override
            top_k: Number of results per domain
        
        Returns:
            Dictionary containing results and metadata
        """
        strategy = routing_strategy or self.default_strategy
        
        # Add to conversation history
        if conversation_id:
            if conversation_id not in self.conversations:
                self.conversations[conversation_id] = []
            self.conversations[conversation_id].append({
                "role": "user",
                "content": query
            })
        
        # Route query to domains
        domains = self.router.route_query(query, strategy)
        logger.info(f"Routing query to domains: {domains}")
        
        # Query each domain
        domain_results = {}
        for domain_name in domains:
            agent = self.agent_registry.get_agent(domain_name)
            if agent:
                try:
                    results = agent.search(query, top_k=top_k)
                    domain_results[domain_name] = results
                    logger.info(f"Found {len(results)} results in {domain_name}")
                except Exception as e:
                    logger.error(f"Error querying {domain_name}: {e}")
                    domain_results[domain_name] = []
        
        # Aggregate results
        aggregated_results = self.aggregator.aggregate_results(domain_results, max_results=10)
        
        response = {
            "query": query,
            "domains_queried": domains,
            "results": aggregated_results,
            "total_results": len(aggregated_results),
            "domain_breakdown": {
                domain: len(results) for domain, results in domain_results.items()
            }
        }
        
        # Add to conversation history
        if conversation_id:
            self.conversations[conversation_id].append({
                "role": "assistant",
                "content": f"Found {len(aggregated_results)} results across {len(domains)} domains",
                "metadata": response
            })
        
        return response
    
    def get_conversation_history(self, conversation_id: str) -> List[Dict[str, Any]]:
        """Get conversation history for a specific conversation."""
        return self.conversations.get(conversation_id, [])
    
    def clear_conversation(self, conversation_id: str):
        """Clear conversation history."""
        if conversation_id in self.conversations:
            del self.conversations[conversation_id]
