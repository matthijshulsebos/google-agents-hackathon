"""
Research Agent - Agentic loop with tool-based reasoning
Uses Gemini function calling for multi-step research and reasoning
"""
from typing import Dict, Any, List, Optional
import logging
from datetime import datetime, timedelta
from google import genai
from google.genai import types
from data.patient_data import get_patient_details

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
        hr_agent=None,
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
            hr_agent: HRAgent instance (optional, will create if not provided)
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

        if hr_agent is None:
            from agents.hr_agent import HRAgent
            self.hr_agent = HRAgent(project_id=project_id, location=location)
        else:
            self.hr_agent = hr_agent

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

        # Tool 4: Search HR policies
        search_hr_policies = types.FunctionDeclaration(
            name="search_hr_policies",
            description="Search HR policies, employee benefits, leave policies, public holidays, workplace procedures, and employment information. Use this to find information about vacation days, sick leave, employee benefits, public holidays, HR procedures, and workplace policies. Returns detailed policy information.",
            parameters={
                "type": "OBJECT",
                "properties": {
                    "query": {
                        "type": "STRING",
                        "description": "Natural language search query for HR policies. Formulate specific queries about employee benefits, leave policies, holidays, or workplace procedures (e.g., 'annual leave policy for nurses', 'public holidays 2025', 'sick leave procedures', 'employee benefits for healthcare workers'). Include specific context when available."
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
                search_pharmacy_info,
                search_hr_policies
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
                return get_patient_details(arguments.get("patient_name", ""))

            elif function_name == "search_nursing_procedures":
                return self._search_nursing_procedures(arguments.get("query", ""))

            elif function_name == "search_pharmacy_info":
                return self._search_pharmacy_info(arguments.get("query", ""))

            elif function_name == "search_hr_policies":
                return self._search_hr_policies(arguments.get("query", ""))

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

    def _search_hr_policies(self, query: str) -> Dict[str, Any]:
        """
        Search HR policies using HRAgent

        Args:
            query: Search query

        Returns:
            Search results from HR policies
        """
        logger.info(f"Searching HR policies for: {query}")

        try:
            result = self.hr_agent.search_policies(query, temperature=0.1)

            if result.get('error'):
                return {
                    "error": True,
                    "message": f"HR search failed: {result.get('message', 'Unknown error')}"
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
            logger.error(f"Error in HR policy search: {str(e)}")
            return {
                "error": True,
                "message": f"Search error: {str(e)}"
            }

    def _generate_summary(
        self,
        detailed_answer: str,
        query: str,
        temperature: float = 0.2
    ) -> str:
        """
        Generate a concise summary of the detailed answer for chatbot use

        Args:
            detailed_answer: Full detailed answer from research
            query: Original user query
            temperature: Model temperature

        Returns:
            Concise 2-3 sentence summary
        """
        try:
            summary_prompt = f"""Given the detailed research answer below, create a concise 2-3 sentence summary suitable for a chatbot conversation.

The summary should:
- Capture the most critical information and actions needed
- Be conversational and easy to understand
- Highlight any urgent safety concerns or compliance issues
- Be suitable for displaying in a chat interface

Original query: {query}

Detailed answer:
{detailed_answer}

Provide ONLY the summary (2-3 sentences), nothing else:"""

            response = self.gemini_client.models.generate_content(
                model=self.model_name,
                contents=summary_prompt,
                config=types.GenerateContentConfig(
                    temperature=temperature
                )
            )

            if response.candidates and len(response.candidates) > 0:
                summary = response.candidates[0].content.parts[0].text.strip()
                logger.info(f"Generated summary: {summary[:100]}...")
                return summary
            else:
                # Fallback: return first 200 chars of detailed answer
                logger.warning("Failed to generate summary, using fallback")
                return detailed_answer[:200] + "..."

        except Exception as e:
            logger.error(f"Error generating summary: {str(e)}")
            # Fallback: return first 200 chars
            return detailed_answer[:200] + "..."

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
4. Search HR policies for employee benefits, leave policies, public holidays, and workplace procedures

CRITICAL RULES:
- You MUST use the available search tools to gather actual information from the hospital systems
- DO NOT make assumptions or generate answers without using search tools
- DO NOT cite specific protocols, procedures, or inventory data unless you've retrieved them using the search tools
- ALWAYS verify information by calling the appropriate search tools
- Use ONLY the tools that are relevant to the specific question being asked

WORKFLOW - Choose the appropriate approach based on the query type:

A) PATIENT-CENTRIC QUERIES (e.g., "What do I need to do today with patient Juan de Marco?"):
   1. FIRST: Call get_patient_details to understand their age, medications, and context
   2. THEN: Call search_nursing_procedures with specific queries about each medication or procedure
   3. THEN: Call search_pharmacy_info to verify medication availability and audit status
   4. IF relevant: Call search_hr_policies for employee/staff information
   5. FINALLY: Synthesize information from ALL relevant sources into a complete answer

B) HR-ONLY QUERIES (e.g., "What are the public holidays in 2025?" or "How many vacation days do I get?"):
   - Call search_hr_policies directly with the question
   - DO NOT call patient, nursing, or pharmacy tools unless the query specifically mentions them

C) NURSING-ONLY QUERIES (e.g., "What is the IV insertion protocol?" or "How do I administer insulin?"):
   - Call search_nursing_procedures directly with the question
   - DO NOT call patient, HR, or pharmacy tools unless the query specifically mentions them

D) PHARMACY-ONLY QUERIES (e.g., "Is ibuprofen in stock?" or "What's the inventory of acetaminophen?"):
   - Call search_pharmacy_info directly with the question
   - DO NOT call patient, nursing, or HR tools unless the query specifically mentions them

E) MIXED QUERIES (e.g., "What's the protocol for oxycodone and is it in stock?"):
   - Use the appropriate combination of tools based on what's being asked
   - Only call the tools that are relevant to answering the specific question

CRITICAL - When formulating search queries for tools:
- DO NOT use generic queries - always include specific context from previous tool results when available
- For patient care queries: After getting patient details, incorporate patient age, medication names, and specific conditions
  - Good: "oxycodone administration protocol for 65 year old patient"
  - Bad: "oxycodone protocol for elderly patients" (too generic)
- For standalone queries: Be specific about what information you need
  - Good: "public holidays 2025"
  - Good: "IV insertion protocol step by step"
  - Good: "ibuprofen 400mg inventory status"

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
                    parts = response.candidates[0].content.parts

                    # Check if ANY part is a function call
                    has_function_calls = any(hasattr(part, 'function_call') and part.function_call for part in parts)

                    if has_function_calls:
                        # Execute ALL function calls in this response
                        function_response_parts = []

                        for part in parts:
                            if hasattr(part, 'function_call') and part.function_call:
                                function_call = part.function_call
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

                                # Add function response part
                                function_response_parts.append(
                                    types.Part.from_function_response(
                                        name=function_name,
                                        response=tool_result
                                    )
                                )

                        # Add function call and ALL responses to conversation
                        contents.append(response.candidates[0].content)
                        contents.append(
                            types.Content(
                                role="user",
                                parts=function_response_parts
                            )
                        )

                        # Continue loop to let model process the results
                        continue

                    # If text response (no more function calls), we have final answer
                    first_part = parts[0]
                    if hasattr(first_part, 'text') and first_part.text:
                        final_answer = first_part.text
                        logger.info(f"Research completed after {iteration} iterations")

                        # Generate summary for chatbot use
                        logger.info("Generating summary version...")
                        summary = self._generate_summary(final_answer, query, temperature)

                        return {
                            "answer": final_answer,  # Full detailed answer
                            "answer_detailed": final_answer,  # Explicit detailed version
                            "answer_summary": summary,  # Concise summary for chatbot
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
