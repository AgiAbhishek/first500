"""
Configuration management for the AI RAG Agent.
Uses Pydantic Settings for type-safe environment variable management.
"""

from typing import Literal, Optional
from pydantic import Field, validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # OpenAI Configuration (optional if using Azure OpenAI)
    openai_api_key: Optional[str] = Field(default=None, description="OpenAI API Key")
    openai_model: str = Field(default="gpt-4-turbo-preview", description="OpenAI model name")
    openai_embedding_model: str = Field(default="text-embedding-3-small", description="Embedding model")
    
    # Azure OpenAI Configuration (optional)
    azure_openai_endpoint: Optional[str] = Field(default=None, description="Azure OpenAI endpoint")
    azure_openai_api_key: Optional[str] = Field(default=None, description="Azure OpenAI API key")
    azure_openai_deployment_name: Optional[str] = Field(default=None, description="Azure deployment name")
    azure_openai_embeddings_deployment: Optional[str] = Field(default=None, description="Azure embeddings deployment")
    
    # Local Embeddings Configuration
    use_local_embeddings: bool = Field(default=True, description="Use local embeddings instead of OpenAI/Azure")
    local_embedding_model: str = Field(default="all-MiniLM-L6-v2", description="Local embedding model name")
    
    # Vector Store Configuration
    vector_store_type: Literal["faiss", "azure_search"] = Field(default="faiss", description="Vector store type")
    vector_store_path: str = Field(default="./data/vector_store", description="Path to store FAISS index")
    
    # Azure AI Search (if using azure_search)
    azure_search_endpoint: Optional[str] = Field(default=None, description="Azure Search endpoint")
    azure_search_key: Optional[str] = Field(default=None, description="Azure Search key")
    azure_search_index_name: Optional[str] = Field(default="documents", description="Azure Search index name")
    
    # Application Configuration
    environment: Literal["development", "production"] = Field(default="development", description="Environment")
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = Field(default="INFO", description="Log level")
    session_ttl: int = Field(default=3600, description="Session TTL in seconds")
    max_conversation_history: int = Field(default=10, description="Max messages in conversation history")
    
    # RAG Configuration
    chunk_size: int = Field(default=1000, description="Text chunk size for splitting")
    chunk_overlap: int = Field(default=200, description="Overlap between chunks")
    top_k_results: int = Field(default=3, description="Number of documents to retrieve")
    
    # API Configuration
    cors_origins: str = Field(default="*", description="Comma-separated CORS origins")
    
    @validator("*", pre=True)
    def empty_str_to_none(cls, v):
        """Convert empty strings to None."""
        if v == "":
            return None
        return v
    
    def __init__(self, **kwargs):
        """Custom initialization with validation."""
        super().__init__(**kwargs)
        
        # Validate that we have either OpenAI or Azure OpenAI credentials
        has_openai = bool(self.openai_api_key)
        has_azure = bool(self.azure_openai_endpoint and self.azure_openai_api_key)
        
        if not has_openai and not has_azure:
            raise ValueError("Either openai_api_key or complete Azure OpenAI credentials must be provided")
        
        if self.azure_openai_endpoint and not self.azure_openai_api_key:
            raise ValueError("azure_openai_api_key is required when azure_openai_endpoint is set")
    
    @property
    def is_azure_openai(self) -> bool:
        """Check if using Azure OpenAI."""
        return bool(self.azure_openai_endpoint and self.azure_openai_api_key)
    
    @property
    def cors_origins_list(self) -> list[str]:
        """Get CORS origins as a list."""
        if self.cors_origins == "*":
            return ["*"]
        return [origin.strip() for origin in self.cors_origins.split(",")]
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# Global settings instance
settings = Settings()
