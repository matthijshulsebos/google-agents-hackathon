"""
LLM integration for generating grounded responses using Vertex AI.
"""
import logging
from typing import List, Dict, Any, Optional
import vertexai
from vertexai.generative_models import GenerativeModel, Part, Content
from vertexai.preview.generative_models import HarmCategory, HarmBlockThreshold

logger = logging.getLogger(__name__)


class ResponseGenerator:
    """Generate grounded responses using Vertex AI Gemini."""
    
    def __init__(self, project_id: str, location: str, model_name: str = "gemini-1.5-pro"):
        self.project_id = project_id
        self.location = location
        self.model_name = model_name
        
        # Initialize Vertex AI
        vertexai.init(project=project_id, location=location)
        
        # Initialize model
        self.model = GenerativeModel(model_name)
        
        # Safety settings
        self.safety_settings = {
            HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
            HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
            HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
            HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
        }
        
        # Generation config
        self.generation_config = {
            "temperature": 0.2,
            "top_p": 0.95,
            "top_k": 40,
            "max_output_tokens": 2048,
        }
    
    def create_grounded_prompt(self, 
                              query: str, 
                              results: List[Dict[str, Any]], 
                              conversation_history: Optional[List[Dict[str, Any]]] = None) -> str:
        """Create a prompt with grounded context."""
        
        prompt_parts = []
        
        # System instruction
        system_instruction = """You are a helpful AI assistant for hospital staff. Your role is to answer questions 
based ONLY on the provided document excerpts. Follow these guidelines:

1. Only use information from the provided documents
2. Cite the source document for each piece of information
3. If the information is not in the documents, say so clearly
4. Be concise but comprehensive
5. Maintain a professional tone appropriate for healthcare settings
6. For multi-part questions, address each part separately"""
        
        prompt_parts.append(system_instruction)
        prompt_parts.append("\n\n")
        
        # Add conversation history if available
        if conversation_history:
            prompt_parts.append("=== Previous Conversation ===\n")
            for msg in conversation_history[-6:]:  # Last 3 turns
                role = msg.get("role", "user")
                content = msg.get("content", "")
                prompt_parts.append(f"{role.upper()}: {content}\n")
            prompt_parts.append("\n")
        
        # Add retrieved documents
        if results:
            prompt_parts.append("=== Retrieved Documents ===\n\n")
            for idx, result in enumerate(results, 1):
                content = result.get("content", "")
                metadata = result.get("metadata", {})
                domain = result.get("domain", "Unknown")
                filename = metadata.get("filename", "Unknown")
                file_type = metadata.get("file_type", "Unknown")
                
                prompt_parts.append(f"[Document {idx}]\n")
                prompt_parts.append(f"Domain: {domain}\n")
                prompt_parts.append(f"Source: {filename} ({file_type})\n")
                prompt_parts.append(f"Content: {content}\n\n")
        else:
            prompt_parts.append("=== No documents were found matching this query ===\n\n")
        
        # Add current query
        prompt_parts.append("=== Current Question ===\n")
        prompt_parts.append(f"{query}\n\n")
        
        # Add instruction
        prompt_parts.append("=== Instructions ===\n")
        prompt_parts.append("Please answer the question based on the retrieved documents above. ")
        prompt_parts.append("Cite specific document numbers [Document N] when referencing information. ")
        prompt_parts.append("If the information is not available in the documents, clearly state that.\n")
        
        return "".join(prompt_parts)
    
    def generate_response(self, 
                         query: str, 
                         results: List[Dict[str, Any]],
                         conversation_history: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
        """Generate a grounded response based on search results."""
        
        try:
            # Create grounded prompt
            prompt = self.create_grounded_prompt(query, results, conversation_history)
            
            # Generate response
            response = self.model.generate_content(
                prompt,
                generation_config=self.generation_config,
                safety_settings=self.safety_settings
            )
            
            # Extract response text
            response_text = response.text if response.text else "I apologize, but I couldn't generate a response."
            
            # Extract sources from results
            sources = []
            for result in results:
                metadata = result.get("metadata", {})
                source = {
                    "domain": result.get("domain", "Unknown"),
                    "filename": metadata.get("filename", "Unknown"),
                    "file_type": metadata.get("file_type", "Unknown"),
                    "chunk_id": metadata.get("chunk_id", 0)
                }
                if source not in sources:
                    sources.append(source)
            
            return {
                "answer": response_text,
                "sources": sources,
                "has_sources": len(results) > 0,
                "num_sources": len(sources)
            }
            
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            return {
                "answer": f"I apologize, but I encountered an error while generating a response: {str(e)}",
                "sources": [],
                "has_sources": False,
                "num_sources": 0,
                "error": str(e)
            }
    
    def format_response(self, response_data: Dict[str, Any]) -> str:
        """Format the response for display."""
        parts = []
        
        # Add answer
        parts.append("=== Answer ===\n")
        parts.append(response_data["answer"])
        parts.append("\n\n")
        
        # Add sources
        if response_data["has_sources"]:
            parts.append("=== Sources ===\n")
            for idx, source in enumerate(response_data["sources"], 1):
                parts.append(f"{idx}. {source['filename']} ({source['domain']} domain, {source['file_type']})\n")
        else:
            parts.append("=== Sources ===\n")
            parts.append("No sources were found for this query.\n")
        
        return "".join(parts)


class ConversationManager:
    """Manage multi-turn conversations with context."""
    
    def __init__(self, max_history: int = 10):
        self.max_history = max_history
        self.conversations: Dict[str, List[Dict[str, Any]]] = {}
    
    def add_message(self, conversation_id: str, role: str, content: str, metadata: Optional[Dict[str, Any]] = None):
        """Add a message to conversation history."""
        if conversation_id not in self.conversations:
            self.conversations[conversation_id] = []
        
        message = {
            "role": role,
            "content": content
        }
        
        if metadata:
            message["metadata"] = metadata
        
        self.conversations[conversation_id].append(message)
        
        # Trim history if too long
        if len(self.conversations[conversation_id]) > self.max_history:
            self.conversations[conversation_id] = self.conversations[conversation_id][-self.max_history:]
    
    def get_history(self, conversation_id: str) -> List[Dict[str, Any]]:
        """Get conversation history."""
        return self.conversations.get(conversation_id, [])
    
    def clear_conversation(self, conversation_id: str):
        """Clear a specific conversation."""
        if conversation_id in self.conversations:
            del self.conversations[conversation_id]
    
    def get_context_for_query(self, conversation_id: str, max_turns: int = 3) -> List[Dict[str, Any]]:
        """Get recent conversation context for a query."""
        history = self.get_history(conversation_id)
        # Return last N turns (each turn = user + assistant)
        return history[-(max_turns * 2):] if history else []
