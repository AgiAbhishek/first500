"""
Embeddings generation using OpenAI API or local sentence-transformers.
Supports both standard OpenAI, Azure OpenAI, and local models.
"""

import logging
from typing import List
from openai import OpenAI, AzureOpenAI
from app.config import settings

logger = logging.getLogger(__name__)


class EmbeddingsGenerator:
    """Generate embeddings using OpenAI's embedding models or local models."""
    
    def __init__(self):
        """Initialize embeddings client based on configuration."""
        self.use_local = settings.use_local_embeddings
        
        if self.use_local:
            # Use local sentence-transformers model
            try:
                from sentence_transformers import SentenceTransformer
                self.model = SentenceTransformer(settings.local_embedding_model)
                self.dimension = self.model.get_sentence_embedding_dimension()
                logger.info(f"Initialized local embeddings with model: {settings.local_embedding_model} (dimension: {self.dimension})")
            except Exception as e:
                logger.error(f"Failed to load local embedding model: {e}")
                raise
        else:
            # Use OpenAI or Azure OpenAI
            if settings.is_azure_openai:
                self.client = AzureOpenAI(
                    api_key=settings.azure_openai_api_key,
                    api_version="2024-02-01",
                    azure_endpoint=settings.azure_openai_endpoint
                )
                self.model = settings.azure_openai_embeddings_deployment or "text-embedding-3-small"
            else:
                self.client = OpenAI(api_key=settings.openai_api_key)
                self.model = settings.openai_embedding_model
            
            self.dimension = 1536  # Default for OpenAI models
            logger.info(f"Initialized cloud embeddings with model: {self.model}")
    
    def generate_embedding(self, text: str) -> List[float]:
        """
        Generate embedding for a single text.
        
        Args:
            text: Text to generate embedding for
            
        Returns:
            List of floats representing the embedding
        """
        if self.use_local:
            try:
                # Use local model
                embedding = self.model.encode(text, convert_to_numpy=True)
                return embedding.tolist()
            except Exception as e:
                logger.error(f"Error generating local embedding: {e}")
                raise
        else:
            try:
                # Use OpenAI API
                response = self.client.embeddings.create(
                    model=self.model,
                    input=text
                )
                return response.data[0].embedding
            except Exception as e:
                logger.error(f"Error generating cloud embedding: {e}")
                raise
    
    def generate_embeddings_batch(self, texts: List[str], batch_size: int = 100) -> List[List[float]]:
        """
        Generate embeddings for multiple texts in batches.
        
        Args:
            texts: List of texts to generate embeddings for
            batch_size: Number of texts to process in each batch
            
        Returns:
            List of embeddings
        """
        if self.use_local:
            # Local model can handle batches efficiently
            try:
                embeddings = self.model.encode(texts, convert_to_numpy=True, show_progress_bar=True)
                logger.info(f"Generated {len(embeddings)} local embeddings")
                return embeddings.tolist()
            except Exception as e:
                logger.error(f"Error generating local embeddings batch: {e}")
                raise
        else:
            # Use OpenAI API with batching
            embeddings = []
            
            for i in range(0, len(texts), batch_size):
                batch = texts[i:i + batch_size]
                try:
                    response = self.client.embeddings.create(
                        model=self.model,
                        input=batch
                    )
                    batch_embeddings = [item.embedding for item in response.data]
                    embeddings.extend(batch_embeddings)
                    logger.info(f"Generated embeddings for batch {i//batch_size + 1}/{(len(texts)-1)//batch_size + 1}")
                except Exception as e:
                    logger.error(f"Error generating embeddings for batch: {e}")
                    raise
            
            return embeddings


# Global instance
embeddings_generator = EmbeddingsGenerator()
