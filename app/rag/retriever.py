"""
Document retriever for RAG system.
Handles document loading, chunking, and retrieval.
"""

import os
import logging
from typing import List, Dict
from app.config import settings
from app.rag.vector_store import Document, vector_store

logger = logging.getLogger(__name__)


class DocumentRetriever:
    """Retrieves relevant documents for queries."""
    
    def __init__(self):
        """Initialize document retriever."""
        self.chunk_size = settings.chunk_size
        self.chunk_overlap = settings.chunk_overlap
        logger.info("Document retriever initialized")
    
    def load_documents_from_directory(self, directory: str) -> List[Document]:
        """
        Load all text documents from a directory.
        
        Args:
            directory: Path to directory containing documents
            
        Returns:
            List of Document objects
        """
        documents = []
        
        if not os.path.exists(directory):
            logger.error(f"Directory not found: {directory}")
            return documents
        
        # Load all .txt files
        for filename in os.listdir(directory):
            if filename.endswith('.txt'):
                filepath = os.path.join(directory, filename)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Split into chunks
                    chunks = self._split_text(content)
                    
                    # Create Document objects for each chunk
                    for i, chunk in enumerate(chunks):
                        doc = Document(
                            content=chunk,
                            metadata={
                                'source': filename,
                                'chunk_id': i,
                                'total_chunks': len(chunks)
                            }
                        )
                        documents.append(doc)
                    
                    logger.info(f"Loaded {filename}: {len(chunks)} chunks")
                except Exception as e:
                    logger.error(f"Error loading {filename}: {e}")
        
        logger.info(f"Total documents loaded: {len(documents)}")
        return documents
    
    def _split_text(self, text: str) -> List[str]:
        """
        Split text into chunks with overlap.
        
        Args:
            text: Text to split
            
        Returns:
            List of text chunks
        """
        chunks = []
        start = 0
        text_length = len(text)
        
        while start < text_length:
            end = start + self.chunk_size
            
            # Find the last newline or space before chunk_size to avoid breaking words
            if end < text_length:
                # Try to break at paragraph
                last_newline = text.rfind('\n\n', start, end)
                if last_newline != -1 and last_newline > start:
                    end = last_newline + 2
                else:
                    # Try to break at sentence
                    last_period = text.rfind('. ', start, end)
                    if last_period != -1 and last_period > start:
                        end = last_period + 2
                    else:
                        # Try to break at word
                        last_space = text.rfind(' ', start, end)
                        if last_space != -1 and last_space > start:
                            end = last_space + 1
            
            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)
            
            # Move start with overlap
            start = end - self.chunk_overlap if end < text_length else text_length
        
        return chunks
    
    def retrieve(self, query: str, k: int = None) -> List[Dict]:
        """
        Retrieve relevant documents for a query.
        
        Args:
            query: Search query
            k: Number of documents to retrieve
            
        Returns:
            List of dictionaries containing document content and metadata
        """
        results = vector_store.search(query, k)
        
        retrieved_docs = []
        for doc, distance in results:
            retrieved_docs.append({
                'content': doc.content,
                'source': doc.metadata.get('source', 'unknown'),
                'chunk_id': doc.metadata.get('chunk_id', 0),
                'distance': distance
            })
        
        return retrieved_docs
    
    def initialize_vector_store(self, documents_dir: str = "./data/documents"):
        """
        Initialize vector store with documents from directory.
        
        Args:
            documents_dir: Directory containing documents to index
        """
        # Try to load existing vector store
        if vector_store.load():
            logger.info("Vector store loaded from disk")
            return
        
        # Load and index documents
        logger.info(f"Loading documents from {documents_dir}")
        documents = self.load_documents_from_directory(documents_dir)
        
        if not documents:
            logger.warning("No documents loaded. Vector store will be empty.")
            return
        
        # Add to vector store
        vector_store.add_documents(documents)
        
        # Save for future use
        vector_store.save()
        logger.info("Vector store initialized and saved")


# Global instance
document_retriever = DocumentRetriever()
