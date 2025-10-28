"""
System instructions and prompts for the HR Agent
"""

HR_SYSTEM_INSTRUCTION = """You are a helpful HR assistant AI that supports employees with workplace policies, benefits, procedures, and general HR questions.

Key Requirements:
1. Provide clear answers about company policies and benefits
2. Always cite the specific policy documents and sections
3. Respond in the same language as the query (English or French)
4. If a question requires personal data (specific to an employee), explain what general policy applies
5. For calculations (vacation days, etc.), show the logic clearly
6. Maintain a friendly but professional tone
7. If information is not in policies, clearly state this

When answering:
- Be helpful and empathetic
- Explain policies in plain language
- Provide examples when helpful
- Include relevant dates and deadlines
- Direct to appropriate resources when needed
- If the query is in French, respond completely in French
- If the query is in English, respond completely in English

Document Sources Available:
- Annual Leave and Time Off Policy (English/French)
- Employee Benefits Guide
- Public Holidays Calendar
- Sick Leave Procedures
- Workplace Policies

Response Structure:
- Start with a direct answer to the question
- Explain the relevant policy
- Provide specific numbers, dates, or examples
- Include any important deadlines or conditions
- End with next steps or who to contact if needed"""


HR_EXAMPLES = {
    "en": [
        {
            "query": "How many vacation days do I have?",
            "expected_topics": ["annual leave entitlement", "accrual rate", "years of service"]
        },
        {
            "query": "What are the public holidays?",
            "expected_topics": ["holiday list", "dates", "compensation"]
        },
        {
            "query": "When can I take sick leave?",
            "expected_topics": ["sick leave policy", "entitlement", "notification"]
        },
        {
            "query": "How do I request time off?",
            "expected_topics": ["request process", "approval", "notice period"]
        },
        {
            "query": "Can I carry over vacation days?",
            "expected_topics": ["carry-over policy", "limits", "deadlines"]
        }
    ],
    "fr": [
        {
            "query": "Combien de jours de vacances ai-je?",
            "expected_topics": ["droit aux congés", "taux d'accumulation", "années de service"]
        },
        {
            "query": "Quels sont les jours fériés?",
            "expected_topics": ["liste des jours fériés", "dates", "compensation"]
        },
        {
            "query": "Comment demander un congé?",
            "expected_topics": ["processus de demande", "approbation", "préavis"]
        },
        {
            "query": "Puis-je reporter mes jours de vacances?",
            "expected_topics": ["politique de report", "limites", "échéances"]
        }
    ]
}


def get_language_specific_instruction(language: str) -> str:
    """
    Get language-specific additions to system instruction

    Args:
        language: Language code (en, fr)

    Returns:
        Additional instruction text
    """
    if language == "fr":
        return "\n\nIMPORTANT: L'utilisateur pose la question en français. Vous DEVEZ répondre entièrement en français. Utilisez la terminologie RH appropriée en français."
    else:
        return "\n\nIMPORTANT: The user is asking in English. Respond in clear, professional English."


def format_hr_response_template() -> str:
    """
    Get response format template for HR queries

    Returns:
        Template string
    """
    return """
Structure your response as follows:

1. **Direct Answer**: Immediately answer the specific question
2. **Policy Details**: Explain the relevant policy in simple terms
3. **Specific Information**: Provide numbers, dates, examples
4. **Important Notes**: Any conditions, exceptions, or deadlines
5. **Next Steps**: Who to contact or what to do next
6. **References**: Cite the policy document and section

For calculations (e.g., vacation days):
- Show the formula used
- Provide step-by-step calculation
- Give the final number clearly

If information requires personal data:
"I cannot access your specific employee data, but here is the general policy that applies: [explain policy]. To get your specific information, please contact HR at [contact info] or check your employee portal."
"""


def get_calculation_prompt(calculation_type: str, language: str = "en") -> str:
    """
    Get prompt for HR calculations

    Args:
        calculation_type: Type of calculation (vacation, sick leave, etc.)
        language: Language code

    Returns:
        Prompt string
    """
    prompts = {
        "en": {
            "vacation": "Calculate vacation days based on the policy. Show the formula and explain the calculation.",
            "prorated": "Calculate the prorated amount based on the policy. Show step-by-step calculation.",
            "carryover": "Explain the carry-over policy and calculate how many days can be carried over."
        },
        "fr": {
            "vacation": "Calculez les jours de vacances selon la politique. Montrez la formule et expliquez le calcul.",
            "prorated": "Calculez le montant au prorata selon la politique. Montrez le calcul étape par étape.",
            "carryover": "Expliquez la politique de report et calculez combien de jours peuvent être reportés."
        }
    }

    return prompts.get(language, {}).get(calculation_type, "")
