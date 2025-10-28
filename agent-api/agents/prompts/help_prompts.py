"""
Help Agent System Instructions and Prompts
"""

HELP_SYSTEM_INSTRUCTION = """You are a helpful onboarding assistant for the Hospital Multi-Agent Information Retrieval System.

Your role is to help users understand how to use this system effectively. You guide nurses, employees, and pharmacists on what questions they can ask and how to get the best results.

KEY PRINCIPLES:
1. Be welcoming and encouraging
2. Provide clear guidance on system capabilities
3. Give 3-5 specific example questions users can ask
4. NEVER answer domain-specific questions directly (medical, HR, pharmacy questions)
5. Instead, show users how to ask those questions themselves
6. Detect user role when possible and provide role-specific guidance
7. Respond in the same language as the user's query

WHAT YOU DO:
- Explain system capabilities and available agents
- Provide example questions for each agent type
- Guide users on how to phrase their questions
- Explain what information is available
- Encourage users to ask their actual question

WHAT YOU DON'T DO:
- Don't answer medical/nursing questions (redirect to nursing agent)
- Don't answer HR/policy questions (redirect to HR agent)
- Don't answer pharmacy/medication questions (redirect to pharmacy agent)
- Don't provide actual domain knowledge, only guidance

AVAILABLE AGENTS:
1. **Nursing Agent** (English/Spanish)
   - Medical procedures and protocols
   - Patient care guidelines
   - Equipment and safety procedures
   - Wound care, IV insertion, vital signs, etc.

2. **HR Agent** (English/French)
   - Leave policies and vacation days
   - Public holidays
   - Employee benefits
   - Workplace policies and procedures

3. **Pharmacy Agent** (English/German)
   - Medication inventory and availability
   - Drug information
   - Storage requirements
   - Controlled substances

RESPONSE FORMAT:
1. Acknowledge the user's question
2. Explain what the system can do (related to their query)
3. Provide 3-5 specific example questions
4. Encourage them to ask their actual question
5. Be warm and supportive

Remember: Your job is to guide, not to answer domain questions directly!"""


def get_help_examples_by_role(role: str = None, language: str = "en") -> dict:
    """
    Get role-specific help examples

    Args:
        role: User role (nurse, employee, pharmacist)
        language: Language code (en, es, fr, de)

    Returns:
        Dict with examples and guidance text
    """
    examples = {
        "en": {
            "nurse": {
                "greeting": "Welcome, Nurse! I'm here to help you use this information system.",
                "capabilities": "The Nursing Agent can help you with medical procedures, protocols, and patient care guidelines.",
                "examples": [
                    "How do I insert an IV line?",
                    "What is the protocol for wound dressing?",
                    "What equipment do I need for wound care?",
                    "What are the steps for administering medication?",
                    "How do I monitor vital signs?"
                ],
                "encouragement": "What medical procedure or protocol would you like to know about?"
            },
            "employee": {
                "greeting": "Welcome! I'm here to help you navigate our HR information system.",
                "capabilities": "The HR Agent can help you with leave policies, benefits, holidays, and workplace procedures.",
                "examples": [
                    "How many vacation days do I have?",
                    "What are the public holidays for 2025?",
                    "How do I request time off?",
                    "What are the sick leave policies?",
                    "What employee benefits are available?"
                ],
                "encouragement": "What HR information would you like to know about?"
            },
            "pharmacist": {
                "greeting": "Welcome, Pharmacist! I'm here to help you use the pharmacy information system.",
                "capabilities": "The Pharmacy Agent can help you check medication inventory, drug information, and storage requirements.",
                "examples": [
                    "Is ibuprofen 400mg in stock?",
                    "Do we have acetaminophen available?",
                    "What antibiotics are in inventory?",
                    "What is the storage requirement for insulin?",
                    "Which controlled substances do we have?"
                ],
                "encouragement": "What medication or inventory information would you like to check?"
            },
            "general": {
                "greeting": "Welcome to the Hospital Multi-Agent Information Retrieval System!",
                "capabilities": "This system has three specialized agents to help you:\n- Nursing Agent (medical procedures)\n- HR Agent (policies and benefits)\n- Pharmacy Agent (medication inventory)",
                "examples": [
                    "Nursing: 'How do I insert an IV line?'",
                    "HR: 'How many vacation days do I have?'",
                    "Pharmacy: 'Is ibuprofen in stock?'"
                ],
                "encouragement": "What would you like to know?"
            }
        },
        "es": {
            "nurse": {
                "greeting": "¡Bienvenida, Enfermera! Estoy aquí para ayudarte a usar este sistema de información.",
                "capabilities": "El Agente de Enfermería puede ayudarte con procedimientos médicos, protocolos y guías de cuidado del paciente.",
                "examples": [
                    "¿Cómo inserto una vía intravenosa?",
                    "¿Cuál es el protocolo para curar heridas?",
                    "¿Qué equipo necesito para el cuidado de heridas?",
                    "¿Cuáles son los pasos para administrar medicamentos?",
                    "¿Cómo monitoreo los signos vitales?"
                ],
                "encouragement": "¿Sobre qué procedimiento médico o protocolo te gustaría saber?"
            },
            "general": {
                "greeting": "¡Bienvenido al Sistema de Recuperación de Información Multi-Agente del Hospital!",
                "capabilities": "Este sistema tiene tres agentes especializados:\n- Agente de Enfermería (procedimientos médicos)\n- Agente de RRHH (políticas y beneficios)\n- Agente de Farmacia (inventario de medicamentos)",
                "examples": [
                    "Enfermería: '¿Cómo inserto una vía IV?'",
                    "RRHH: '¿Cuántos días de vacaciones tengo?'",
                    "Farmacia: '¿Hay ibuprofeno disponible?'"
                ],
                "encouragement": "¿Qué te gustaría saber?"
            }
        },
        "fr": {
            "employee": {
                "greeting": "Bienvenue! Je suis là pour vous aider à naviguer dans notre système d'information RH.",
                "capabilities": "L'Agent RH peut vous aider avec les politiques de congé, les avantages, les jours fériés et les procédures de travail.",
                "examples": [
                    "Combien de jours de vacances ai-je?",
                    "Quels sont les jours fériés pour 2025?",
                    "Comment demander un congé?",
                    "Quelles sont les politiques de congé maladie?",
                    "Quels avantages sociaux sont disponibles?"
                ],
                "encouragement": "Quelle information RH souhaitez-vous connaître?"
            },
            "general": {
                "greeting": "Bienvenue au Système de Récupération d'Information Multi-Agent de l'Hôpital!",
                "capabilities": "Ce système a trois agents spécialisés:\n- Agent Infirmier (procédures médicales)\n- Agent RH (politiques et avantages)\n- Agent Pharmacie (inventaire de médicaments)",
                "examples": [
                    "Infirmier: 'Comment insérer une ligne IV?'",
                    "RH: 'Combien de jours de vacances ai-je?'",
                    "Pharmacie: 'L'ibuprofène est-il disponible?'"
                ],
                "encouragement": "Que souhaitez-vous savoir?"
            }
        },
        "de": {
            "pharmacist": {
                "greeting": "Willkommen, Apotheker! Ich bin hier, um Ihnen bei der Nutzung des Apotheken-Informationssystems zu helfen.",
                "capabilities": "Der Apotheken-Agent kann Ihnen bei Medikamenteninventar, Arzneimittelinformationen und Lageranforderungen helfen.",
                "examples": [
                    "Ist Ibuprofen 400mg auf Lager?",
                    "Haben wir Paracetamol verfügbar?",
                    "Welche Antibiotika sind im Bestand?",
                    "Was sind die Lageranforderungen für Insulin?",
                    "Welche kontrollierten Substanzen haben wir?"
                ],
                "encouragement": "Welche Medikamenten- oder Bestandsinformationen möchten Sie prüfen?"
            },
            "general": {
                "greeting": "Willkommen beim Multi-Agenten-Informationssystem des Krankenhauses!",
                "capabilities": "Dieses System hat drei spezialisierte Agenten:\n- Pflege-Agent (medizinische Verfahren)\n- HR-Agent (Richtlinien und Vorteile)\n- Apotheken-Agent (Medikamentenbestand)",
                "examples": [
                    "Pflege: 'Wie lege ich eine IV-Leitung?'",
                    "HR: 'Wie viele Urlaubstage habe ich?'",
                    "Apotheke: 'Ist Ibuprofen auf Lager?'"
                ],
                "encouragement": "Was möchten Sie wissen?"
            }
        }
    }

    # Get language-specific examples
    lang_examples = examples.get(language, examples["en"])

    # Get role-specific or general examples
    if role and role in lang_examples:
        return lang_examples[role]
    else:
        return lang_examples.get("general", examples["en"]["general"])


def format_help_response(role: str = None, language: str = "en") -> str:
    """
    Format a help response with examples

    Args:
        role: User role
        language: Language code

    Returns:
        Formatted help response string
    """
    examples_data = get_help_examples_by_role(role, language)

    response = f"""{examples_data['greeting']}

{examples_data['capabilities']}

Example questions you can ask:
"""

    for i, example in enumerate(examples_data['examples'], 1):
        response += f"{i}. \"{example}\"\n"

    response += f"\n{examples_data['encouragement']}"

    return response
