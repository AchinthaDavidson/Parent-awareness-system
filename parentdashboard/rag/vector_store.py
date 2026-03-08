"""
Vector store module for RAG pipeline.
Manages Chroma DB for storing and querying embeddings.
"""
import os
from pathlib import Path
from typing import List, Dict, Optional
import chromadb
from chromadb.config import Settings
from parentdashboard.config import CHROMA_DB_DIR, EMBEDDING_MODEL


class VectorStore:
    """Manages Chroma DB vector store for document embeddings."""
    
    def __init__(self, collection_name: str = "parent_dashboard_kb"):
        """
        Initialize Chroma DB client and collection.
        
        Args:
            collection_name: Name of the Chroma collection
        """
        self.collection_name = collection_name
        self.client = chromadb.PersistentClient(
            path=str(CHROMA_DB_DIR),
            settings=Settings(anonymized_telemetry=False)
        )
        
        # Get or create collection
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"}  # Use cosine similarity
        )
    
    def add_documents(
        self,
        texts: List[str],
        embeddings: List[List[float]],
        metadatas: List[Dict],
        start_id: int = 0
    ) -> None:
        """
        Add documents to the vector store.
        
        Args:
            texts: List of text chunks
            embeddings: List of embedding vectors
            metadatas: List of metadata dictionaries for each chunk
            start_id: Starting ID number for generating unique IDs
        """
        if not texts:
            return
        
        # Generate unique IDs for documents
        # Use source from metadata if available, otherwise use sequential IDs
        source = metadatas[0].get('source', 'unknown') if metadatas else 'unknown'
        ids = [f"{source}_chunk_{start_id + i}" for i in range(len(texts))]
        
        # Add to collection
        self.collection.add(
            embeddings=embeddings,
            documents=texts,
            metadatas=metadatas,
            ids=ids
        )
        
        print(f"Added {len(texts)} documents to vector store")
    
    def query(
        self,
        query_embedding: List[float],
        n_results: int = 3
    ) -> Dict:
        """
        Query the vector store for similar documents.
        
        Args:
            query_embedding: Embedding vector of the query
            n_results: Number of results to return
        
        Returns:
            Dictionary with 'documents', 'metadatas', and 'distances'
        """
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results
        )
        
        return results
    
    def delete_all(self) -> None:
        """Delete all documents from the collection."""
        # Get all IDs
        all_ids = self.collection.get()['ids']
        if all_ids:
            self.collection.delete(ids=all_ids)
            print("Deleted all documents from vector store")
    
    def get_count(self) -> int:
        """Get the number of documents in the collection."""
        return self.collection.count()
    
    def delete_by_source(self, source: str) -> None:
        """
        Delete all documents with a specific source filename.
        
        Args:
            source: The source filename to delete
        """
        # Get all documents with this source
        results = self.collection.get(
            where={"source": source}
        )
        
        if results['ids']:
            self.collection.delete(ids=results['ids'])
            print(f"Deleted {len(results['ids'])} documents with source '{source}' from vector store")
        else:
            print(f"No documents found with source '{source}'")

