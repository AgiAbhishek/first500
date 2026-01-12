"""
Pydantic models for API request/response validation.
"""

from typing import List, Optional
from pydantic import BaseModel, Field


class QueryRequest(BaseModel):
    """Request model for the /ask endpoint."""
    
    query: str = Field(..., min_length=1, max_length=2000, description="User's question")
    session_id: Optional[str] = Field(default=None, description="Optional session ID for conversation continuity")
    
    class Config:
        json_schema_extra = {
            "example": {
                "query": "What is the company's leave policy?",
                "session_id": "abc123"
            }
        }


class QueryResponse(BaseModel):
    """Response model for the /ask endpoint."""
    
    answer: str = Field(..., description="AI-generated answer")
    sources: List[str] = Field(default_factory=list, description="List of source documents used")
    session_id: str = Field(..., description="Session ID for this conversation")
    
    class Config:
        json_schema_extra = {
            "example": {
                "answer": "The company offers 15 days of paid leave per year...",
                "sources": ["company_policies.txt", "hr_handbook.txt"],
                "session_id": "abc123"
            }
        }


class HealthResponse(BaseModel):
    """Response model for health check endpoint."""
    
    status: str = Field(default="healthy", description="Service status")
    version: str = Field(default="1.0.0", description="API version")
    vector_store_initialized: bool = Field(..., description="Whether vector store is ready")


class ErrorResponse(BaseModel):
    """Error response model."""
    
    error: str = Field(..., description="Error message")
    detail: Optional[str] = Field(default=None, description="Additional error details")
