# Hospital Multi-Agent Information Retrieval System

## Project Overview
Build a multi-agent hospital information retrieval system using Google ADK (Application Development Kit) with Vertex AI Search. The system serves three user types: Nurses, Employees (HR), and Pharmacists, with multilingual support (English, Dutch, Spanish, French, German).

## Architecture
- **Layer 1**: Orchestrator Agent - Routes queries to specialized agents
- **Layer 2**: Three Specialized Agents - Nursing, HR, Pharmacy
- **Layer 3**: Vertex AI Search - Three separate datastores for document retrieval
- **Layer 4**: Documents - PDF/Markdown files (3-5 per domain, 2 languages each)

## Technology Stack
- Google ADK (Gemini 2.0 Flash)
- Vertex AI Search
- Python 3.10+
- Google Cloud Platform

---

## Coding Agents & Role Prompts

### Agent 1: Project Setup & Configuration Specialist

**Role**: You are a Google Cloud and Python project setup expert. Your responsibility is to create the foundational project structure, configuration files, and ensure all dependencies are properly managed.

**Responsibilities**:
1. Create project directory structure
2. Set up configuration management (config.py)
3. Create requirements.txt with all necessary dependencies
4. Set up environment variable templates (.env.example)
5. Create README.md with setup instructions
6. Initialize git repository with proper .gitignore

**Key Files to Create**:
- `config.py` - GCP project settings, datastore IDs, model configurations
- `requirements.txt` - All Python dependencies
- `.env.example` - Template for environment variables
- `README.md` - Setup and usage instructions
- `.gitignore` - Python and GCP-specific ignores
- Project folder structure

**Technical Requirements**:
- Use environment variables for sensitive data
- Support for multiple GCP projects (dev/prod)
- Validation of required environment variables
- Clear error messages for missing configurations

---

### Agent 2: Vertex AI Search Integration Specialist

**Role**: You are a Vertex AI Search expert specializing in document retrieval and grounding. Your responsibility is to create the document management system and Vertex AI Search integration utilities.

**Responsibilities**:
1. Create utilities for Vertex AI Search datastore interaction
2. Implement document upload/management scripts
3. Build search query optimization logic
4. Handle grounding metadata extraction
5. Create test scripts for Vertex AI Search functionality

**Key Files to Create**:
- `utils/vertex_search.py` - Vertex AI Search wrapper class
- `utils/document_manager.py` - Document upload and management
- `scripts/setup_datastores.py` - Automated datastore creation
- `scripts/upload_documents.py` - Batch document upload
- `tests/test_vertex_search.py` - Unit tests for search functionality

**Technical Requirements**:
- Implement retry logic for API calls
- Handle rate limiting gracefully
- Support batch operations for efficiency
- Extract and format grounding metadata properly
- Support multiple document formats (PDF, Markdown)

**Google ADK Integration**:
```python
from google import genai
from google.genai import types

# Use GoogleSearch tool with dynamic retrieval
google_search_tool = types.Tool(
    google_search=types.GoogleSearch(
        dynamic_retrieval_config=types.DynamicRetrievalConfig(
            mode=types.DynamicRetrievalConfigMode.MODE_DYNAMIC,
            dynamic_threshold=0.3
        )
    )
)
```

---

### Agent 3: Nursing Agent Developer

**Role**: You are a healthcare IT specialist building AI agents for medical environments. Your responsibility is to create the Nursing Agent that helps nurses find information about medical procedures and protocols.

**Responsibilities**:
1. Build NursingAgent class with Vertex AI Search integration
2. Implement medical procedure query handling
3. Add step-by-step guidance formatting
4. Support multilingual queries (English, Spanish)
5. Implement proper medical terminology handling
6. Create unit tests specific to nursing scenarios

**Key Files to Create**:
- `agents/nursing_agent.py` - Main NursingAgent class
- `agents/prompts/nursing_prompts.py` - System instructions and prompts
- `tests/test_nursing_agent.py` - Unit tests with sample queries
- `docs/nursing/` - Sample nursing protocol documents (EN, ES)

**System Instruction Template**:
```
You are a professional nursing assistant AI that helps nurses find information 
about medical procedures, protocols, and patient care guidelines.

Key Requirements:
1. Provide clear, step-by-step guidance for medical procedures
2. Always cite document sources with specific references
3. Use professional medical terminology appropriately
4. Respond in the same language as the query (English or Spanish)
5. If information is not found in protocols, clearly state this
6. Prioritize patient safety in all responses
7. Format procedural steps as numbered lists when applicable

When answering:
- Be precise and concise
- Include safety warnings when relevant
- Reference specific protocol sections
- Maintain professional medical tone
```

**Sample Test Queries**:
- English: "How do I insert an IV line?", "What is the protocol for wound dressing?", "Steps for administering medication"
- Spanish: "¿Cómo inserto una vía intravenosa?", "¿Cuál es el protocolo para curar heridas?"

---

### Agent 4: HR Agent Developer

**Role**: You are an HR technology specialist building AI solutions for employee support. Your responsibility is to create the HR Agent that helps employees with policies, benefits, and workplace questions.

**Responsibilities**:
1. Build HRAgent class with Vertex AI Search integration
2. Implement policy and benefits query handling
3. Add calculation capabilities (vacation days, etc.)
4. Support multilingual queries (English, French)
5. Handle general vs. specific HR queries
6. Create unit tests for HR scenarios

**Key Files to Create**:
- `agents/hr_agent.py` - Main HRAgent class
- `agents/prompts/hr_prompts.py` - System instructions and prompts
- `tests/test_hr_agent.py` - Unit tests with sample queries
- `docs/hr/` - Sample HR policy documents (EN, FR)

**System Instruction Template**:
```
You are a helpful HR assistant AI that supports employees with workplace 
policies, benefits, procedures, and general HR questions.

Key Requirements:
1. Provide clear answers about company policies and benefits
2. Always cite the specific policy documents and sections
3. Respond in the same language as the query (English or French)
4. If a question requires personal data (specific to an employee), 
   explain what general policy applies
5. For calculations (vacation days, etc.), show the logic clearly
6. Maintain a friendly but professional tone
7. If information is not in policies, clearly state this

When answering:
- Be helpful and empathetic
- Explain policies in plain language
- Provide examples when helpful
- Include relevant dates and deadlines
- Direct to appropriate resources when needed
```

**Sample Test Queries**:
- English: "How many vacation days do I have?", "What are the public holidays?", "When can I take sick leave?"
- French: "Combien de jours de vacances ai-je?", "Quels sont les jours fériés?", "Comment demander un congé?"

---

### Agent 5: Pharmacy Agent Developer

**Role**: You are a pharmacy systems specialist building AI solutions for medication management. Your responsibility is to create the Pharmacy Agent that helps pharmacists with inventory and drug information.

**Responsibilities**:
1. Build PharmacyAgent class with Vertex AI Search integration
2. Implement drug inventory query handling
3. Add medication information retrieval
4. Support multilingual queries (English, German)
5. Handle stock availability checks
6. Create unit tests for pharmacy scenarios

**Key Files to Create**:
- `agents/pharmacy_agent.py` - Main PharmacyAgent class
- `agents/prompts/pharmacy_prompts.py` - System instructions and prompts
- `tests/test_pharmacy_agent.py` - Unit tests with sample queries
- `docs/pharmacy/` - Sample pharmacy inventory documents (EN, DE)

**System Instruction Template**:
```
You are a pharmacy assistant AI that helps pharmacists check medication 
inventory, drug information, and pharmaceutical guidelines.

Key Requirements:
1. Provide accurate information about medication availability
2. Always cite the inventory documents and drug information sources
3. Respond in the same language as the query (English or German)
4. Include drug names (generic and brand) when relevant
5. If inventory information is not current, state the document date
6. Use pharmaceutical terminology appropriately
7. Prioritize accuracy for medication-related information

When answering:
- Be precise with dosages and quantities
- Include relevant warnings or contraindications if in documents
- Format drug information clearly
- State confidence level if inventory data is unclear
- Reference document timestamps for inventory questions
```

**Sample Test Queries**:
- English: "Is ibuprofen 400mg in stock?", "Do we have acetaminophen?", "What's the inventory level for insulin?"
- German: "Ist Ibuprofen 400mg auf Lager?", "Haben wir Paracetamol?", "Welche Antibiotika sind verfügbar?"

---

### Agent 6: Orchestrator Developer

**Role**: You are a senior software architect specializing in multi-agent systems. Your responsibility is to create the Orchestrator Agent that intelligently routes queries to specialized agents.

**Responsibilities**:
1. Build HospitalOrchestrator class
2. Implement query classification logic using Gemini
3. Create routing mechanism to specialized agents
4. Add multi-agent consultation capability (optional)
5. Implement response merging logic
6. Create comprehensive integration tests

**Key Files to Create**:
- `orchestrator.py` - Main HospitalOrchestrator class
- `utils/query_classifier.py` - Query classification utilities
- `utils/response_merger.py` - Multi-agent response merging
- `tests/test_orchestrator.py` - Integration tests
- `tests/test_routing.py` - Routing logic tests

**Query Classification Logic**:
```python
# Classification prompt for Gemini
CLASSIFICATION_PROMPT = """
Analyze the following query and classify it into ONE category:

Categories:
- nursing: Medical procedures, nursing protocols, patient care, clinical procedures
- hr: Holidays, vacation, benefits, HR policies, employment questions, workplace policies
- pharmacy: Medications, drug inventory, prescriptions, pharmaceutical information

Examples:
- "How do I insert an IV?" → nursing
- "How many vacation days do I have?" → hr
- "Is ibuprofen available?" → pharmacy
- "¿Cuántos días festivos tenemos?" → hr
- "Protocole pour administration médicament?" → nursing

Query: {query}

Respond with ONLY the category name: nursing, hr, or pharmacy
"""
```

**Routing Strategy**:
1. **Explicit routing**: If user role is provided, route directly
2. **Intelligent routing**: Use Gemini to classify query intent
3. **Fallback routing**: Default to most likely agent if classification is ambiguous
4. **Multi-agent**: Optional feature to query multiple agents and merge results

**Technical Requirements**:
- Implement timeout handling for agent calls
- Log all routing decisions for debugging
- Support async agent calls for performance
- Handle agent failures gracefully
- Provide clear error messages to users

---

### Agent 7: Document Generator & Content Specialist

**Role**: You are a technical writer and content specialist. Your responsibility is to create realistic sample documents for all three domains in multiple languages.

**Responsibilities**:
1. Create 3-5 nursing protocol documents (English, Spanish)
2. Create 3-5 HR policy documents (English, French)
3. Create 3-5 pharmacy inventory documents (English, German)
4. Ensure documents are realistic and comprehensive
5. Add metadata and proper formatting
6. Create document upload scripts

**Key Files to Create**:
- `docs/nursing/*.md` - Nursing protocols in EN and ES
- `docs/hr/*.md` - HR policies in EN and FR
- `docs/pharmacy/*.md` - Pharmacy inventory in EN and DE
- `scripts/generate_documents.py` - Document generation utilities
- `docs/README.md` - Document overview and structure

**Document Requirements**:

**Nursing Documents (English + Spanish)**:
1. IV Insertion Protocol
2. Wound Care Procedures
3. Medication Administration Guidelines
4. Vital Signs Monitoring
5. Patient Safety Checklist

**HR Documents (English + French)**:
1. Annual Leave Policy
2. Employee Benefits Guide
3. Public Holidays Calendar
4. Sick Leave Procedures
5. Workplace Policies

**Pharmacy Documents (English + German)**:
1. Medication Inventory List
2. Drug Storage Guidelines
3. Prescription Handling Procedures
4. Controlled Substances Protocol
5. Medication Safety Information

**Document Format**:
- Use Markdown for easy parsing
- Include clear sections and headers
- Add metadata (date, version, department)
- Use professional medical/HR/pharmaceutical terminology
- Ensure translations are accurate and natural

---

### Agent 8: Testing & Quality Assurance Specialist

**Role**: You are a QA engineer specializing in AI systems testing. Your responsibility is to create comprehensive tests for all components and ensure system reliability.

**Responsibilities**:
1. Create unit tests for all agent classes
2. Build integration tests for orchestrator
3. Create end-to-end test scenarios
4. Implement multilingual test coverage
5. Add performance benchmarks
6. Create test documentation

**Key Files to Create**:
- `tests/test_nursing_agent.py` - Nursing agent unit tests
- `tests/test_hr_agent.py` - HR agent unit tests
- `tests/test_pharmacy_agent.py` - Pharmacy agent unit tests
- `tests/test_orchestrator.py` - Orchestrator integration tests
- `tests/test_e2e.py` - End-to-end test scenarios
- `tests/test_multilingual.py` - Language-specific tests
- `tests/conftest.py` - Pytest configuration and fixtures

**Test Coverage Requirements**:
- Minimum 80% code coverage
- Test all error handling paths
- Test multilingual support for each agent
- Test routing accuracy (>90%)
- Test response time (<5 seconds per query)
- Test grounding/citation accuracy

**Sample Test Structure**:
```python
import pytest
from agents.nursing_agent import NursingAgent

class TestNursingAgent:
    @pytest.fixture
    def nursing_agent(self):
        return NursingAgent(
            project_id="test-project",
            datastore_id="test-datastore"
        )
    
    def test_english_query(self, nursing_agent):
        result = nursing_agent.search_protocols("How to insert IV?")
        assert result["agent"] == "nursing"
        assert "answer" in result
        assert len(result["answer"]) > 0
    
    def test_spanish_query(self, nursing_agent):
        result = nursing_agent.search_protocols("¿Cómo insertar IV?")
        assert result["language"] == "es"
        # Spanish response expected
    
    def test_grounding_metadata(self, nursing_agent):
        result = nursing_agent.search_protocols("IV insertion steps")
        assert "grounding_metadata" in result
        # Verify citations are present
```

---

### Agent 9: Demo & Presentation Developer

**Role**: You are a developer advocate creating compelling demos and presentations. Your responsibility is to create demo scripts, UI components, and presentation materials.

**Responsibilities**:
1. Create interactive demo script (demo.py)
2. Build simple Streamlit UI (optional)
3. Create presentation-ready test scenarios
4. Generate demo output files (JSON, logs)
5. Create video/presentation script
6. Build hackathon presentation deck

**Key Files to Create**:
- `demo.py` - Main demo script with test scenarios
- `demo_ui.py` - Optional Streamlit UI (if time permits)
- `scripts/run_demo.sh` - Automated demo runner
- `outputs/demo_results.json` - Sample demo outputs
- `presentation/HACKATHON_DEMO.md` - Demo script for presentation

**Demo Script Requirements**:
```python
# demo.py structure
def run_demo():
    """
    Run comprehensive demo showcasing:
    1. Multilingual capabilities (4 languages)
    2. Intelligent routing across 3 agents
    3. Document grounding and citations
    4. Real-time query processing
    """
    
    demo_scenarios = [
        # Nursing scenarios
        ("en", "nurse", "How do I insert an IV line?"),
        ("es", "nurse", "¿Cuál es el protocolo de curación?"),
        
        # HR scenarios
        ("en", "employee", "How many vacation days do I get?"),
        ("fr", "employee", "Quels sont les jours fériés?"),
        
        # Pharmacy scenarios
        ("en", "pharmacist", "Is ibuprofen 400mg in stock?"),
        ("de", "pharmacist", "Ist Paracetamol verfügbar?"),
        
        # Multi-agent scenario
        ("en", None, "What's the protocol for medication administration?"),
    ]
    
    # Run each scenario and collect results
    # Display in presentation-ready format
    # Save to JSON for analysis
```

**Demo Flow**:
1. Introduction (30 seconds)
2. Architecture overview (1 minute)
3. Live demo - 6-8 queries across languages (3 minutes)
4. Highlight key features (1 minute)
5. Q&A preparation

---

### Agent 10: Documentation & Integration Specialist

**Role**: You are a technical documentation expert. Your responsibility is to create comprehensive documentation and ensure seamless integration of all components.

**Responsibilities**:
1. Create comprehensive README.md
2. Write API documentation
3. Create setup and deployment guides
4. Document troubleshooting procedures
5. Create architecture documentation
6. Ensure all components integrate properly

**Key Files to Create**:
- `README.md` - Main project documentation
- `docs/API.md` - API reference for all agents
- `docs/SETUP.md` - Step-by-step setup guide
- `docs/ARCHITECTURE.md` - System architecture details
- `docs/TROUBLESHOOTING.md` - Common issues and solutions
- `docs/DEPLOYMENT.md` - GCP deployment instructions

**README Structure**:
```markdown
# Hospital Multi-Agent Information Retrieval System

## Overview
Brief description of the system and its purpose.

## Features
- ✨ Multi-agent orchestration
- 🌐 Multilingual support (EN, ES, FR, DE)
- 🔍 Vertex AI Search integration
- 📚 Document grounding and citations
- 🏥 Healthcare-specific agents

## Prerequisites
- Google Cloud Project with billing enabled
- Vertex AI API enabled
- Python 3.10+
- Service account with appropriate permissions

## Quick Start
Step-by-step instructions to get the system running.

## Usage Examples
Code snippets showing how to use each component.

## Architecture
Link to detailed architecture documentation.

## Testing
How to run tests and verify functionality.

## Contributing
Guidelines for hackathon team collaboration.

## License
MIT License
```

---

## Development Workflow

### Phase 1: Foundation (Hour 0-1)
**Agents involved**: Project Setup Specialist, Document Generator
1. Set up project structure
2. Create configuration files
3. Generate sample documents
4. Set up version control

### Phase 2: Core Components (Hour 1-3)
**Agents involved**: Vertex AI Specialist, All Agent Developers (3-5)
1. Implement Vertex AI Search utilities
2. Build three specialized agents in parallel
3. Create agent-specific tests
4. Upload documents to datastores

### Phase 3: Integration (Hour 3-4)
**Agents involved**: Orchestrator Developer, Testing Specialist
1. Build orchestrator with routing logic
2. Integrate all three agents
3. Run integration tests
4. Fix integration issues

### Phase 4: Testing & Polish (Hour 4-5)
**Agents involved**: Testing Specialist, Demo Developer
1. Run comprehensive test suite
2. Create demo scenarios
3. Test multilingual support
4. Performance optimization

### Phase 5: Demo Preparation (Hour 5-6)
**Agents involved**: Demo Developer, Documentation Specialist
1. Prepare demo script
2. Create presentation materials
3. Final testing and rehearsal
4. Document known issues

---

## Project Structure

```
hospital-multiagent-system/
├── README.md
├── requirements.txt
├── config.py
├── .env.example
├── .gitignore
│
├── agents/
│   ├── __init__.py
│   ├── nursing_agent.py
│   ├── hr_agent.py
│   ├── pharmacy_agent.py
│   └── prompts/
│       ├── nursing_prompts.py
│       ├── hr_prompts.py
│       └── pharmacy_prompts.py
│
├── orchestrator.py
│
├── utils/
│   ├── __init__.py
│   ├── vertex_search.py
│   ├── document_manager.py
│   ├── query_classifier.py
│   └── response_merger.py
│
├── docs/
│   ├── README.md
│   ├── API.md
│   ├── SETUP.md
│   ├── ARCHITECTURE.md
│   ├── nursing/
│   │   ├── iv_insertion_protocol_en.md
│   │   ├── iv_insertion_protocol_es.md
│   │   └── ...
│   ├── hr/
│   │   ├── leave_policy_en.md
│   │   ├── leave_policy_fr.md
│   │   └── ...
│   └── pharmacy/
│       ├── medication_inventory_en.md
│       ├── medication_inventory_de.md
│       └── ...
│
├── scripts/
│   ├── setup_datastores.py
│   ├── upload_documents.py
│   ├── generate_documents.py
│   └── run_demo.sh
│
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   ├── test_nursing_agent.py
│   ├── test_hr_agent.py
│   ├── test_pharmacy_agent.py
│   ├── test_orchestrator.py
│   ├── test_e2e.py
│   └── test_multilingual.py
│
├── demo.py
├── demo_ui.py (optional)
│
└── outputs/
    └── demo_results.json
```

---

## Key Technical Requirements

### Google ADK Integration
```python
from google import genai
from google.genai import types

# Initialize client
client = genai.Client(
    vertexai=True,
    project=PROJECT_ID,
    location="us-central1"
)

# Use Vertex AI Search tool
google_search_tool = types.Tool(
    google_search=types.GoogleSearch(
        dynamic_retrieval_config=types.DynamicRetrievalConfig(
            mode=types.DynamicRetrievalConfigMode.MODE_DYNAMIC,
            dynamic_threshold=0.3
        )
    )
)

# Generate with search
response = client.models.generate_content(
    model="gemini-2.0-flash-exp",
    contents=query,
    config=types.GenerateContentConfig(
        system_instruction=system_instruction,
        tools=[google_search_tool],
        temperature=0.2,
    )
)
```

### Error Handling Pattern
```python
import logging
from typing import Dict, Any

def safe_agent_call(func):
    """Decorator for safe agent calls with error handling"""
    def wrapper(*args, **kwargs) -> Dict[str, Any]:
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logging.error(f"Agent call failed: {str(e)}")
            return {
                "error": True,
                "message": str(e),
                "agent": func.__self__.__class__.__name__
            }
    return wrapper
```

### Multilingual Support
```python
def detect_language(text: str) -> str:
    """Detect query language"""
    # Simple keyword-based detection
    if any(word in text.lower() for word in ['¿', '¡', 'días', 'cómo']):
        return "es"
    elif any(word in text.lower() for word in ['combien', 'quels', 'jours']):
        return "fr"
    elif any(word in text.lower() for word in ['ist', 'haben', 'wie']):
        return "de"
    return "en"
```

---

## Success Metrics

### Technical Metrics
- [ ] All 3 agents successfully integrated
- [ ] Routing accuracy >90%
- [ ] Response time <5 seconds
- [ ] Test coverage >80%
- [ ] Support for 4 languages

### Demo Metrics
- [ ] 8+ successful demo queries
- [ ] Multilingual examples working
- [ ] Citations properly displayed
- [ ] No crashes during demo
- [ ] Clear presentation of features

### Hackathon Metrics
- [ ] Project completed in 5-6 hours
- [ ] All team members contributed
- [ ] Architecture clearly explained
- [ ] Impressive "wow" factor
- [ ] Code ready to share

---

## Important Notes for Claude Code

1. **Start with Agent 1** (Project Setup) to establish foundation
2. **Parallelize Agents 3-5** (domain agents) for efficiency
3. **Test incrementally** - don't wait until the end
4. **Keep code simple** - hackathon code doesn't need to be perfect
5. **Focus on demo impact** - make sure demo queries work flawlessly
6. **Document as you go** - helps with presentation
7. **Use provided templates** - they're tested and proven
8. **Ask for help** - experts are available during hackathon

## Emergency Fallback Plans

If running short on time:
- **Priority 1**: Get 1 agent working end-to-end (choose Nursing)
- **Priority 2**: Add orchestrator with basic routing
- **Priority 3**: Add remaining agents
- **Priority 4**: Multilingual support
- **Priority 5**: Advanced features (multi-agent consultation)

---

## Contact & Support

For hackathon support:
- Google ADK documentation: https://ai.google.dev/
- Vertex AI Search: https://cloud.google.com/generative-ai-app-builder/docs
- Team lead: [Add contact info]
- Slack channel: [Add channel]
