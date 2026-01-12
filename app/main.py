"""
FastAPI application for AI RAG Agent.
"""

import logging
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.api.routes import router
from app.rag.retriever import document_retriever
from app.agent.memory import session_memory

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for FastAPI app startup and shutdown.
    """
    # Startup
    logger.info("Starting AI RAG Agent...")
    
    # Initialize vector store with documents
    documents_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "documents")
    try:
        document_retriever.initialize_vector_store(documents_dir)
        logger.info("✓ Vector store initialized successfully")
    except Exception as e:
        logger.error(f"✗ Failed to initialize vector store: {e}")
    
    logger.info(f"✓ API running in {settings.environment} mode")
    logger.info(f"✓ Using {'Azure OpenAI' if settings.is_azure_openai else 'OpenAI'}")
    
    yield
    
    # Shutdown
    logger.info("Shutting down AI RAG Agent...")
    session_memory.cleanup_expired_sessions()
    logger.info("✓ Cleanup complete")


# Create FastAPI app
app = FastAPI(
    title="AI RAG Agent API",
    description="AI-powered question-answering system with RAG capabilities",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routes
app.include_router(router, prefix="/api")

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "name": "AI RAG Agent API",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.environment == "development"
    )
