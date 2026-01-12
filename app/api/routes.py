"""
FastAPI routes for the AI RAG Agent API.
"""

import logging
from fastapi import APIRouter, HTTPException
from app.models import QueryRequest, QueryResponse, HealthResponse
from app.agent.ai_agent import ai_agent
from app.rag.vector_store import vector_store

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/ask", response_model=QueryResponse)
async def ask_question(request: QueryRequest):
    """
    Process a user query and return an AI-generated answer.
    
    Args:
        request: QueryRequest containing query and optional session_id
        
    Returns:
        QueryResponse with answer, sources, and session_id
    """
    try:
        logger.info(f"Received query: {request.query[:100]}...")
        
        # Process query with AI agent
        result = ai_agent.process_query(
            query=request.query,
            session_id=request.session_id
        )
        
        return QueryResponse(**result)
        
    except Exception as e:
        logger.error(f"Error processing query: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred while processing your request: {str(e)}"
        )


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Health check endpoint to verify service status.
    
    Returns:
        HealthResponse with service status
    """
    return HealthResponse(
        status="healthy",
        version="1.0.0",
        vector_store_initialized=vector_store.is_initialized
    )
