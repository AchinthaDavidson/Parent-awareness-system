"""
Retriever module for RAG pipeline.
Retrieves relevant chunks based on user queries.
"""
from typing import List, Dict
from rag.embeddings import EmbeddingGenerator
from rag.vector_store import VectorStore
from config import TOP_K_RETRIEVAL


class Retriever:
    """Retrieves relevant document chunks based on query."""
    
    def __init__(self, vector_store: VectorStore, embedding_generator: EmbeddingGenerator):
        """
        Initialize the retriever.
        
        Args:
            vector_store: VectorStore instance
            embedding_generator: EmbeddingGenerator instance
        """
        self.vector_store = vector_store
        self.embedding_generator = embedding_generator
    
    def retrieve(self, query: str, top_k: int = TOP_K_RETRIEVAL) -> List[Dict]:
        """
        Retrieve relevant chunks for a query.
        """
        import time as _t

        # Generate query embedding
        print("    >>> generate_embedding START", flush=True)
        _s = _t.time()
        query_embedding = self.embedding_generator.generate_embedding(query)
        print(f"    <<< generate_embedding DONE: {_t.time()-_s:.2f}s", flush=True)

        # Query vector store
        print("    >>> vector_store.query START", flush=True)
        _s = _t.time()
        results = self.vector_store.query(query_embedding, n_results=top_k)
        print(f"    <<< vector_store.query DONE: {_t.time()-_s:.2f}s", flush=True)
        
        # Format results
        retrieved_chunks = []
        
        if results['documents'] and len(results['documents'][0]) > 0:
            for i in range(len(results['documents'][0])):
                chunk = {
                    'text': results['documents'][0][i],
                    'source': results['metadatas'][0][i].get('source', 'Unknown'),
                    'page': results['metadatas'][0][i].get('page'),
                    'score': 1 - results['distances'][0][i] if results['distances'] else 0.0  # Convert distance to similarity
                }
                retrieved_chunks.append(chunk)
        
        return retrieved_chunks

