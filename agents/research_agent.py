"""
Research Agent - Agentic loop with tool-based reasoning
Uses Gemini function calling for multi-step research and reasoning
"""
from typing import Dict, Any, List, Optional
import logging
from datetime import datetime, timedelta
from google import genai
from google.genai import types

logger = logging.getLogger(__name__)


class ResearchAgent:
    """
    Research agent that uses ReAct-style agentic loop with tool calling
    Capable of multi-step reasoning across multiple data sources
    """

    def __init__(
        self,
        project_id: str,
        nursing_agent=None,
        pharmacy_agent=None,
        location: str = "us-central1",
        model_name: str = "gemini-2.5-flash",
        max_iterations: int = 10
    ):
        """
        Initialize Research Agent

        Args:
            project_id: Google Cloud Project ID
            nursing_agent: NursingAgent instance (optional, will create if not provided)
            pharmacy_agent: PharmacyAgent instance (optional, will create if not provided)
            location: GCP location
            model_name: Gemini model to use
            max_iterations: Maximum number of tool-calling iterations
        """
        self.project_id = project_id
        self.location = location
        self.model_name = model_name
        self.max_iterations = max_iterations
        self.agent_type = "research"

        # Initialize Gemini client
        self.gemini_client = genai.Client(
            vertexai=True,
            project=project_id,
            location=location
        )

        # Initialize specialized agents if not provided
        if nursing_agent is None:
            from agents.nursing_agent import NursingAgent
            self.nursing_agent = NursingAgent(project_id=project_id, location=location)
        else:
            self.nursing_agent = nursing_agent

        if pharmacy_agent is None:
            from agents.pharmacy_agent import PharmacyAgent
            self.pharmacy_agent = PharmacyAgent(project_id=project_id, location=location)
        else:
            self.pharmacy_agent = pharmacy_agent

        # Define tools for function calling
        self.tools = self._build_tools()

        logger.info(f"Research Agent initialized with {len(self.tools.function_declarations)} tools")

    def _build_tools(self) -> types.Tool:
        """
        Build function declarations for Gemini function calling

        Returns:
            Tool object with all function declarations
        """
        # Tool 1: Get patient details
        get_patient_details = types.FunctionDeclaration(
            name="get_patient_details",
            description="Get detailed patient information including age, scheduled medications, medical history, and current treatment plan. Use this when you need to know specific information about a patient.",
            parameters={
                "type": "OBJECT",
                "properties": {
                    "patient_name": {
                        "type": "STRING",
                        "description": "Full name of the patient (e.g., 'Juan de Marco', 'Maria Silva')"
                    }
                },
                "required": ["patient_name"]
            }
        )

        # Tool 2: Search nursing procedures
        search_nursing_procedures = types.FunctionDeclaration(
            name="search_nursing_procedures",
            description="Search nursing protocols, procedures, and clinical guidelines. Use this to find information about medical procedures, medication administration protocols, patient care protocols, safety requirements, and clinical guidelines. Returns detailed protocol information with step-by-step instructions.",
            parameters={
                "type": "OBJECT",
                "properties": {
                    "query": {
                        "type": "STRING",
                        "description": "Natural language search query for nursing procedures. Formulate specific queries based on context from previous tool calls (e.g., if patient is 65 years old and scheduled for oxycodone, query 'oxycodone administration for 65 year old patient' or 'controlled medication protocol geriatric patient over 60'). Include specific patient details like age, medication names, or conditions when available."
                    }
                },
                "required": ["query"]
            }
        )

        # Tool 3: Search pharmacy information
        search_pharmacy_info = types.FunctionDeclaration(
            name="search_pharmacy_info",
            description="Search pharmacy inventory, medication availability, drug information, audit dates, and pharmaceutical guidelines. Use this to check medication stock levels, audit compliance, drug interactions, and medication-specific requirements. Returns inventory data and medication details.",
            parameters={
                "type": "OBJECT",
                "properties": {
                    "query": {
                        "type": "STRING",
                        "description": "Natural language search query for pharmacy information. Formulate specific queries based on medication names and requirements discovered from previous tools (e.g., if patient needs oxycodone, query 'oxycodone 5mg inventory and audit status' or 'oxycodone availability and audit date for geriatric patients'). Include specific medication details when available."
                    }
                },
                "required": ["query"]
            }
        )

        # Combine all tools
        return types.Tool(
            function_declarations=[
                get_patient_details,
                search_nursing_procedures,
                search_pharmacy_info
            ]
        )

    def _execute_tool(self, function_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a tool function

        Args:
            function_name: Name of the function to execute
            arguments: Function arguments

        Returns:
            Tool execution result
        """
        try:
            logger.info(f"Executing tool: {function_name} with args: {arguments}")

            if function_name == "get_patient_details":
                return self._get_patient_details(arguments.get("patient_name", ""))

            elif function_name == "search_nursing_procedures":
                return self._search_nursing_procedures(arguments.get("query", ""))

            elif function_name == "search_pharmacy_info":
                return self._search_pharmacy_info(arguments.get("query", ""))

            else:
                return {
                    "error": True,
                    "message": f"Unknown function: {function_name}"
                }

        except Exception as e:
            logger.error(f"Error executing tool {function_name}: {str(e)}")
            return {
                "error": True,
                "message": f"Tool execution error: {str(e)}"
            }

    def _get_patient_details(self, patient_name: str) -> Dict[str, Any]:
        """
        Get patient details (hardcoded for demo)

        Args:
            patient_name: Patient name

        Returns:
            Patient information
        """
        # Hardcoded patient database for demo
        patients = {
            "juan de marco": {
                "name": "Juan de Marco",
                "age": 65,
                "date_of_birth": "1960-03-15",
                "medical_record_number": "MRN-789456",
                "scheduled_medications_today": [
                    {
                        "medication": "Oxycodone",
                        "strength": "5mg",
                        "scheduled_time": "09:00 AM",
                        "route": "Oral",
                        "reason": "Post-surgical pain management"
                    },
                    {
                        "medication": "Metformin",
                        "strength": "500mg",
                        "scheduled_time": "08:00 AM, 08:00 PM",
                        "route": "Oral",
                        "reason": "Type 2 Diabetes"
                    },
                    {
                        "medication": "Lisinopril",
                        "strength": "10mg",
                        "scheduled_time": "08:00 AM",
                        "route": "Oral",
                        "reason": "Hypertension"
                    }
                ],
                "medical_history": [
                    "Type 2 Diabetes (diagnosed 2015)",
                    "Hypertension (diagnosed 2018)",
                    "Total knee replacement surgery (January 20, 2025)"
                ],
                "allergies": ["Penicillin (rash)"],
                "current_location": "Room 302, Orthopedic Ward",
                "attending_physician": "Dr. Sarah Thompson"
            },
            "maria silva": {
                "name": "Maria Silva",
                "age": 45,
                "date_of_birth": "1980-07-22",
                "medical_record_number": "MRN-456123",
                "scheduled_medications_today": [
                    {
                        "medication": "Ibuprofen",
                        "strength": "400mg",
                        "scheduled_time": "10:00 AM, 06:00 PM",
                        "route": "Oral",
                        "reason": "Chronic back pain"
                    },
                    {
                        "medication": "Omeprazole",
                        "strength": "20mg",
                        "scheduled_time": "08:00 AM",
                        "route": "Oral",
                        "reason": "GERD"
                    }
                ],
                "medical_history": [
                    "Chronic lower back pain (diagnosed 2019)",
                    "GERD (diagnosed 2020)"
                ],
                "allergies": ["None"],
                "current_location": "Room 215, General Medicine",
                "attending_physician": "Dr. Michael Chen"
            },
            "robert johnson": {
                "name": "Robert Johnson",
                "age": 72,
                "date_of_birth": "1953-11-08",
                "medical_record_number": "MRN-321654",
                "scheduled_medications_today": [
                    {
                        "medication": "Morphine Sulfate",
                        "strength": "10mg",
                        "scheduled_time": "08:00 AM, 02:00 PM, 08:00 PM",
                        "route": "Injectable",
                        "reason": "Cancer pain management"
                    },
                    {
                        "medication": "Warfarin",
                        "strength": "5mg",
                        "scheduled_time": "06:00 PM",
                        "route": "Oral",
                        "reason": "Atrial fibrillation"
                    }
                ],
                "medical_history": [
                    "Stage IV lung cancer (diagnosed 2024)",
                    "Atrial fibrillation (diagnosed 2021)",
                    "History of deep vein thrombosis"
                ],
                "allergies": ["Sulfa drugs (severe reaction)"],
                "current_location": "Room 410, Oncology",
                "attending_physician": "Dr. Jennifer Lee"
            }
        }

        # Normalize patient name for lookup
        normalized_name = patient_name.lower().strip()

        if normalized_name in patients:
            patient_data = patients[normalized_name]
            logger.info(f"Found patient: {patient_data['name']}, age {patient_data['age']}")
            return patient_data
        else:
            return {
                "error": True,
                "message": f"Patient '{patient_name}' not found in system. Available patients: {', '.join([p['name'] for p in patients.values()])}"
            }

    def _search_nursing_procedures(self, query: str) -> Dict[str, Any]:
        """
        Search nursing procedures using NursingAgent

        Args:
            query: Search query

        Returns:
            Search results from nursing procedures
        """
        logger.info(f"Searching nursing procedures for: {query}")

        try:
            result = self.nursing_agent.search_protocols(query, temperature=0.1)

            if result.get('error'):
                return {
                    "error": True,
                    "message": f"Nursing search failed: {result.get('message', 'Unknown error')}"
                }

            # Return formatted result optimized for tool response
            return {
                "answer": result.get("answer", ""),
                "total_results": result.get("total_results", 0),
                "sources": [
                    {
                        "title": source.get("title", ""),
                        "snippet": source.get("snippet", "")[:300]  # Limit snippet length
                    }
                    for source in result.get("grounding_metadata", [])[:3]  # Limit to top 3 sources
                ],
                "query": query
            }

        except Exception as e:
            logger.error(f"Error in nursing procedure search: {str(e)}")
            return {
                "error": True,
                "message": f"Search error: {str(e)}"
            }

    def _search_pharmacy_info(self, query: str) -> Dict[str, Any]:
        """
        Search pharmacy information using PharmacyAgent

        Args:
            query: Search query

        Returns:
            Search results from pharmacy inventory
        """
        logger.info(f"Searching pharmacy info for: {query}")

        try:
            result = self.pharmacy_agent.search_inventory(query, temperature=0.1)

            if result.get('error'):
                return {
                    "error": True,
                    "message": f"Pharmacy search failed: {result.get('message', 'Unknown error')}"
                }

            # Return formatted result optimized for tool response
            return {
                "answer": result.get("answer", ""),
                "total_results": result.get("total_results", 0),
                "sources": [
                    {
                        "title": source.get("title", ""),
                        "snippet": source.get("snippet", "")[:300]  # Limit snippet length
                    }
                    for source in result.get("grounding_metadata", [])[:3]  # Limit to top 3 sources
                ],
                "query": query
            }

        except Exception as e:
            logger.error(f"Error in pharmacy info search: {str(e)}")
            return {
                "error": True,
                "message": f"Search error: {str(e)}"
            }

    def research(
        self,
        query: str,
        temperature: float = 0.1
    ) -> Dict[str, Any]:
        """
        Perform research using agentic loop with tool calling

        Args:
            query: User's research query
            temperature: Model temperature (lower = more focused)

        Returns:
            Dict with answer, reasoning trace, and metadata
        """
        try:
            logger.info(f"Starting research for query: {query[:50]}...")

            # System instruction for research agent
            system_instruction = """You are a hospital research assistant AI that helps healthcare workers gather and analyze information across multiple hospital systems.

Your capabilities:
1. Access patient records to understand patient details, age, scheduled medications, and medical history
2. Search nursing protocols and procedures for clinical guidelines and requirements
3. Search pharmacy inventory for medication availability, audit dates, and drug information

Your approach:
- Think step-by-step and reason through what information you need
- Use tools iteratively to gather relevant information
- Cross-reference information from different sources (patient data, nursing protocols, pharmacy info)
- Pay special attention to age-specific requirements and safety protocols
- Identify any compliance issues or missing information
- Provide a clear, actionable answer based on all gathered information

When handling questions about patient care:
1. First, get patient details to understand their age, medications, and context
2. Then, search relevant protocols or procedures
3. Then, check pharmacy information if medication-related
4. Finally, synthesize all information to provide a complete answer

CRITICAL - When formulating search queries for tools:
- DO NOT use generic queries - always include specific context from previous tool results
- After getting patient details, incorporate patient age, medication names, and specific conditions into your search queries
- Good query example: If patient is 65 years old and scheduled for oxycodone → "oxycodone administration protocol for 65 year old patient" or "controlled medication audit requirements patient over 60 years"
- Bad query example: "oxycodone protocol for elderly patients" (too generic, lacks specific patient context)
- Good query example: If you need pharmacy info about oxycodone → "oxycodone 5mg inventory status and audit date" or "oxycodone geriatric audit compliance"
- Bad query example: "oxycodone availability" (lacks specificity about what information you need)

Important guidelines:
- Always cite which tools you used to gather information
- Highlight any safety concerns, compliance issues, or required actions
- If audit dates are mentioned, calculate if they are overdue (>6 months is typically overdue)
- Be specific about what needs to be done and why
- Format your final answer clearly with key points highlighted
- Make each tool query specific and contextual based on what you've already learned

Current date: """ + datetime.now().strftime("%B %d, %Y")

            # Initialize conversation with user query
            contents = [query]

            # Track tool calls and iterations
            tool_call_history = []
            iteration = 0

            # ReAct loop
            while iteration < self.max_iterations:
                iteration += 1
                logger.info(f"Research iteration {iteration}/{self.max_iterations}")

                # Generate response from Gemini with tool support
                response = self.gemini_client.models.generate_content(
                    model=self.model_name,
                    contents=contents,
                    config=types.GenerateContentConfig(
                        system_instruction=system_instruction,
                        tools=[self.tools],
                        temperature=temperature
                    )
                )

                # Check if model wants to call a function
                if response.candidates[0].content.parts:
                    first_part = response.candidates[0].content.parts[0]

                    # If function call, execute it
                    if hasattr(first_part, 'function_call') and first_part.function_call:
                        function_call = first_part.function_call
                        function_name = function_call.name
                        function_args = dict(function_call.args)

                        logger.info(f"Model called function: {function_name}")

                        # Execute the function
                        tool_result = self._execute_tool(function_name, function_args)

                        # Record tool call
                        tool_call_history.append({
                            "iteration": iteration,
                            "function": function_name,
                            "arguments": function_args,
                            "result_summary": str(tool_result)[:200] + "..." if len(str(tool_result)) > 200 else str(tool_result)
                        })

                        # Add function call and response to conversation
                        contents.append(response.candidates[0].content)
                        contents.append(
                            types.Content(
                                role="user",
                                parts=[
                                    types.Part.from_function_response(
                                        name=function_name,
                                        response=tool_result
                                    )
                                ]
                            )
                        )

                        # Continue loop to let model process the result
                        continue

                    # If text response (no more function calls), we have final answer
                    elif hasattr(first_part, 'text') and first_part.text:
                        final_answer = first_part.text
                        logger.info(f"Research completed after {iteration} iterations")

                        return {
                            "answer": final_answer,
                            "agent": "research",
                            "iterations": iteration,
                            "tool_calls": len(tool_call_history),
                            "tool_call_history": tool_call_history,
                            "query": query,
                            "error": False
                        }

                else:
                    # No parts in response, something went wrong
                    logger.warning("Empty response from model")
                    break

            # If we reached max iterations without final answer
            logger.warning(f"Reached max iterations ({self.max_iterations}) without final answer")
            return {
                "answer": "Research incomplete: Reached maximum number of iterations without finding a complete answer. Please try a more specific query.",
                "agent": "research",
                "iterations": iteration,
                "tool_calls": len(tool_call_history),
                "tool_call_history": tool_call_history,
                "query": query,
                "error": False,
                "warning": "max_iterations_reached"
            }

        except Exception as e:
            logger.error(f"Research error: {str(e)}")
            return {
                "error": True,
                "message": str(e),
                "agent": "research",
                "query": query
            }
