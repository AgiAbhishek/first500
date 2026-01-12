"""
AI Agent with tool calling for document retrieval.
Uses OpenAI function calling to decide when to search documents.
"""

import json
import logging
from typing import List, Dict, Optional
from openai import OpenAI, AzureOpenAI
from app.config import settings
from app.agent.memory import session_memory
from app.rag.retriever import document_retriever

logger = logging.getLogger(__name__)


class AIAgent:
    """Intelligent agent that decides when to search documents vs answer directly."""
    
    # Define the search tool for function calling
    TOOLS = [
        {
            "type": "function",
            "function": {
                "name": "search_documents",
                "description": "Search the company knowledge base for relevant information. Use this when the question is about company policies, products, procedures, or requires specific factual information from documents.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "The search query to find relevant documents"
                        },
                        "num_results": {
                            "type": "integer",
                            "description": "Number of results to retrieve (default: 3)",
                            "default": 3
                        }
                    },
                    "required": ["query"]
                }
            }
        }
    ]
    
    SYSTEM_PROMPT = """You are a helpful AI assistant with access to company knowledge base. 
    
Your behavior:
- For questions about company policies, products, procedures, or specific factual information, use the search_documents tool to find relevant information before answering.
- For general questions, mathematical calculations, or common knowledge, you can answer directly without searching.
- Always provide clear, concise, and accurate answers.
- If you use information from documents, cite the sources.
- If you cannot find relevant information in the documents, say so clearly.

Remember: Use the search tool when the question requires company-specific information."""
    
    def __init__(self):
        """Initialize the AI agent."""
        if settings.is_azure_openai:
            # Use OpenAI client with Azure v1 endpoint format
            self.client = OpenAI(
                api_key=settings.azure_openai_api_key,
                base_url=f"{settings.azure_openai_endpoint.rstrip('/')}/openai/v1",
                default_headers={"api-key": settings.azure_openai_api_key}
            )
            self.model = settings.azure_openai_deployment_name or "gpt-4"
        else:
            self.client = OpenAI(api_key=settings.openai_api_key)
            self.model = settings.openai_model
        
        logger.info(f"AI Agent initialized with model: {self.model}")
    
    def _search_documents(self, query: str, num_results: int = 3) -> str:
        """
        Search documents and return formatted results.
        
        Args:
            query: Search query
            num_results: Number of results to retrieve
            
        Returns:
            Formatted search results as a string
        """
        logger.info(f"Searching documents for: {query}")
        results = document_retriever.retrieve(query, k=num_results)
        
        if not results:
            return "No relevant documents found."
        
        # Format results
        formatted_results = []
        for i, result in enumerate(results, 1):
            formatted_results.append(
                f"[Document {i} - {result['source']}]\n{result['content']}\n"
            )
        
        return "\n".join(formatted_results)
    
    def process_query(self, query: str, session_id: Optional[str] = None) -> Dict:
        """
        Process a user query with agent decision-making.
        
        Args:
            query: User's question
            session_id: Optional session ID for conversation continuity
            
        Returns:
            Dictionary with answer, sources, and session_id
        """
        # Create or validate session
        if session_id and session_memory.session_exists(session_id):
            logger.info(f"Using existing session: {session_id}")
        else:
            session_id = session_memory.create_session()
            # Add system message for new sessions
            session_memory.add_message(session_id, "system", self.SYSTEM_PROMPT)
        
        # Add user message to history
        session_memory.add_message(session_id, "user", query)
        
        # Get conversation history
        messages = session_memory.get_history(session_id)
        
        # Make initial API call with tools
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                tools=self.TOOLS,
                tool_choice="auto"  # Let the model decide
            )
            
            response_message = response.choices[0].message
            sources = []
            
            # Check if model wants to call a function
            if response_message.tool_calls:
                # Model decided to search documents
                logger.info("Agent decided to search documents")
                
                # Add assistant's tool call to messages
                messages.append(response_message)
                
                # Process each tool call
                for tool_call in response_message.tool_calls:
                    function_name = tool_call.function.name
                    function_args = json.loads(tool_call.function.arguments)
                    
                    if function_name == "search_documents":
                        # Execute search
                        search_results = self._search_documents(
                            query=function_args.get("query", query),
                            num_results=function_args.get("num_results", 3)
                        )
                        
                        # Extract sources
                        retrieved_docs = document_retriever.retrieve(
                            function_args.get("query", query),
                            k=function_args.get("num_results", 3)
                        )
                        sources = list(set([doc['source'] for doc in retrieved_docs]))
                        
                        # Add function response to messages
                        messages.append({
                            "tool_call_id": tool_call.id,
                            "role": "tool",
                            "name": function_name,
                            "content": search_results
                        })
                
                # Make second API call with function results
                second_response = self.client.chat.completions.create(
                    model=self.model,
                    messages=messages
                )
                
                final_answer = second_response.choices[0].message.content
            else:
                # Model answered directly without searching
                logger.info("Agent answered directly without searching")
                final_answer = response_message.content
            
            # Add assistant's response to session memory
            session_memory.add_message(session_id, "assistant", final_answer)
            
            return {
                "answer": final_answer,
                "sources": sources,
                "session_id": session_id
            }
            
        except Exception as e:
            logger.error(f"Error processing query: {e}")
            raise


# Global instance
ai_agent = AIAgent()
