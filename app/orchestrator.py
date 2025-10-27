from typing import Dict, List, Any, Tuple
import re

from .config import DOMAINS, ROUTING_KEYWORDS, DEFAULT_PROJECT
from .agents import VertexSearchAgent, generate_grounded_answer
from .resources import ensure_resources_for_domains
from .auth import setup_adc_from_env


def rule_based_route(query: str) -> List[str]:
    q = query.lower()
    selected: List[str] = []
    for domain, keywords in ROUTING_KEYWORDS.items():
        for kw in keywords:
            if re.search(r"\b" + re.escape(kw) + r"\b", q):
                selected.append(domain)
                break
    if not selected:
        # default to po (most common) as a simple fallback; real impl would use LLM classification
        selected = ["po"]
    return selected


class Orchestrator:
    def __init__(self):
        # Ensure ADC is set up before any Google clients are created
        try:
            setup_adc_from_env()
        except Exception as e:
            print(f"[WARN] Failed to set up ADC from env: {e}")
        # Ensure Discovery Engine resources exist (data stores + serving configs)
        try:
            self.domain_configs = ensure_resources_for_domains(DEFAULT_PROJECT, DOMAINS)
        except Exception as e:
            print(f"[WARN] Auto-provisioning Discovery Engine resources failed: {e}")
            self.domain_configs = DOMAINS
        self.agents: Dict[str, VertexSearchAgent] = {}
        for domain, cfg in self.domain_configs.items():
            self.agents[domain] = VertexSearchAgent(cfg.get("serving_config", ""), domain)
        # Conversations stored per session id: list of {role, content}
        self.sessions: Dict[str, List[Dict[str, str]]] = {}

    def get_history(self, session_id: str) -> List[Dict[str, str]]:
        return self.sessions.setdefault(session_id, [])

    def add_turn(self, session_id: str, role: str, content: str):
        self.sessions.setdefault(session_id, []).append({"role": role, "content": content})

    def answer(self, session_id: str, query: str, explicit_domains: List[str] = None) -> Dict[str, Any]:
        self.add_turn(session_id, "user", query)
        domains = explicit_domains or rule_based_route(query)
        contexts: List[Dict[str, Any]] = []
        per_domain_results: Dict[str, List[Dict[str, Any]]] = {}
        for d in domains:
            agent = self.agents.get(d)
            if not agent:
                continue
            hits = agent.search(query)
            per_domain_results[d] = hits
            contexts.extend(hits)
        history = self.get_history(session_id)
        result = generate_grounded_answer(query, contexts, history)
        self.add_turn(session_id, "assistant", result.get("answer", ""))
        # Add routing info and raw hits for transparency
        result["domains"] = domains
        result["retrieval"] = {k: len(v) for k, v in per_domain_results.items()}
        return result
