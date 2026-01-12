"""
Vector store implementation using FAISS for document storage and retrieval.
"""

import os
import pickle
import logging
from typing import List, Dict, Tuple
import faiss
import numpy as np
from app.config import settings
from app.rag.embeddings import embeddings_generator

logger = logging.getLogger(__name__)


class Document:
    """Represents a document chunk with metadata."""
    
    def __init__(self, content: str, metadata: Dict[str, str]):
        self.content = content
        self.metadata = metadata
    
    def __repr__(self):
        return f"Document(source={self.metadata.get('source')}, chunk={self.metadata.get('chunk_id')})"


class VectorStore:
    """FAISS-based vector store for document embeddings."""
    
    def __init__(self):
        """Initialize vector store."""
        self.index = None
        self.documents: List[Document] = []
        self.dimension = None  # Will be set dynamically from embeddings
        self.is_initialized = False
        
        # Create storage directory if it doesn't exist
        os.makedirs(settings.vector_store_path, exist_ok=True)
        
        logger.info("Vector store initialized")
    
    def add_documents(self, documents: List[Document]):
        """
        Add documents to the vector store.
        
        Args:
            documents: List of Document objects to add
        """
        if not documents:
            logger.warning("No documents to add")
            return
        
        # Extract text content
        texts = [doc.content for doc in documents]
        
        # Generate embeddings
        logger.info(f"Generating embeddings for {len(texts)} documents...")
        embeddings = embeddings_generator.generate_embeddings_batch(texts)
        embeddings_array = np.array(embeddings, dtype=np.float32)
        
        # Initialize or update FAISS index
        if self.index is None:
            self.dimension = embeddings_array.shape[1]
            self.index = faiss.IndexFlatL2(self.dimension)
            logger.info(f"Created new FAISS index with dimension {self.dimension}")
        
        # Add embeddings to index
        self.index.add(embeddings_array)
        
        # Store documents
        self.documents.extend(documents)
        
        self.is_initialized = True
        logger.info(f"Added {len(documents)} documents to vector store. Total: {len(self.documents)}")
    
    def search(self, query: str, k: int = None) -> List[Tuple[Document, float]]:
        """
        Search for similar documents.
        
        Args:
            query: Query text
            k: Number of results to return (defaults to settings.top_k_results)
            
        Returns:
            List of (Document, distance) tuples
        """
        if not self.is_initialized or self.index is None:
            logger.warning("Vector store not initialized or empty")
            return []
        
        k = k or settings.top_k_results
        k = min(k, len(self.documents))  # Can't return more than we have
        
        # Generate query embedding
        query_embedding = embeddings_generator.generate_embedding(query)
        query_vector = np.array([query_embedding], dtype=np.float32)
        
        # Search in FAISS index
        distances, indices = self.index.search(query_vector, k)
        
        # Retrieve documents
        results = []
        for idx, distance in zip(indices[0], distances[0]):
            if idx < len(self.documents):
                results.append((self.documents[idx], float(distance)))
        
        logger.info(f"Found {len(results)} relevant documents for query")
        return results
    
    def save(self, path: str = None):
        """
        Save vector store to disk.
        
        Args:
            path: Path to save the vector store (uses settings.vector_store_path if not provided)
        """
        if not self.is_initialized:
            logger.warning("Cannot save uninitialized vector store")
            return
        
        path = path or settings.vector_store_path
        
        # Save FAISS index
        index_path = os.path.join(path, "faiss.index")
        faiss.write_index(self.index, index_path)
        
        # Save documents metadata
        docs_path = os.path.join(path, "documents.pkl")
        with open(docs_path, "wb") as f:
            pickle.dump(self.documents, f)
        
        logger.info(f"Vector store saved to {path}")
    
    def load(self, path: str = None) -> bool:
        """
        Load vector store from disk.
        
        Args:
            path: Path to load the vector store from
            
        Returns:
            True if loaded successfully, False otherwise
        """
        path = path or settings.vector_store_path
        index_path = os.path.join(path, "faiss.index")
        docs_path = os.path.join(path, "documents.pkl")
        
        if not os.path.exists(index_path) or not os.path.exists(docs_path):
            logger.info("Vector store files not found")
            return False
        
        try:
            # Load FAISS index
            self.index = faiss.read_index(index_path)
            
            # Load documents
            with open(docs_path, "rb") as f:
                self.documents = pickle.load(f)
            
            self.is_initialized = True
            logger.info(f"Vector store loaded from {path}. {len(self.documents)} documents available.")
            return True
        except Exception as e:
            logger.error(f"Error loading vector store: {e}")
            return False
    
    def clear(self):
        """Clear all documents and index."""
        self.index = None
        self.documents = []
        self.is_initialized = False
        logger.info("Vector store cleared")


# Global instance
vector_store = VectorStore()
