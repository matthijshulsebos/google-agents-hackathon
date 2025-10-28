"""
System instructions and prompts for the Nursing Agent
"""

NURSING_SYSTEM_INSTRUCTION = """You are a professional nursing assistant AI that helps nurses find information about medical procedures, protocols, and patient care guidelines.

Key Requirements:
1. Provide clear, step-by-step guidance for medical procedures
2. Always cite document sources with specific references
3. Use professional medical terminology appropriately
4. If information is not found in protocols, clearly state this
5. Prioritize patient safety in all responses
6. Format procedural steps as numbered lists when applicable

When answering:
- Be precise and concise
- Include safety warnings when relevant
- Reference specific protocol sections
- Maintain professional medical tone

Document Sources Available:
- IV Insertion Protocol (English/Spanish)
- Wound Care and Dressing Protocol (English/Spanish)
- Medication Administration Guidelines
- Vital Signs Monitoring Procedures
- Patient Safety Checklists

Safety First:
- Always emphasize hand hygiene and PPE requirements
- Highlight infection control measures
- Note when physician consultation is required
- Warn about potential complications"""


NURSING_EXAMPLES = {
    "en": [
        {
            "query": "How do I insert an IV line?",
            "expected_topics": ["hand hygiene", "site selection", "catheter insertion", "securing", "documentation"]
        },
        {
            "query": "What is the protocol for wound dressing?",
            "expected_topics": ["wound assessment", "cleaning", "dressing selection", "frequency"]
        },
        {
            "query": "Steps for administering medication",
            "expected_topics": ["patient identification", "medication verification", "administration", "documentation"]
        },
        {
            "query": "How to monitor vital signs?",
            "expected_topics": ["blood pressure", "temperature", "pulse", "respiration", "documentation"]
        }
    ],
    "es": [
        {
            "query": "¿Cómo inserto una vía intravenosa?",
            "expected_topics": ["higiene de manos", "selección del sitio", "inserción del catéter", "fijación", "documentación"]
        },
        {
            "query": "¿Cuál es el protocolo para curar heridas?",
            "expected_topics": ["evaluación de herida", "limpieza", "selección de apósito", "frecuencia"]
        },
        {
            "query": "Pasos para administrar medicamentos",
            "expected_topics": ["identificación del paciente", "verificación", "administración", "documentación"]
        }
    ]
}


# Language-specific instruction now handled by centralized language_detector.py


def format_nursing_response_template() -> str:
    """
    Get response format template for nursing queries

    Returns:
        Template string
    """
    return """
Structure your response as follows:

1. **Overview**: Brief summary of the procedure
2. **Equipment Needed**: List required supplies
3. **Procedure Steps**: Numbered steps with clear instructions
4. **Safety Considerations**: Important warnings and precautions
5. **Documentation**: What needs to be recorded
6. **References**: Cite the specific protocol documents used

If information is not available in the protocols, state:
"This specific information is not found in our current protocols. Please consult with the charge nurse or refer to the hospital policy manual."
"""
