"""
Text chunking module for RAG pipeline.
Splits text into overlapping chunks for better retrieval.
"""
from typing import List
from parentdashboard.config import CHUNK_SIZE, CHUNK_OVERLAP


def chunk_text(text: str, chunk_size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> List[str]:
    """
    Split text into chunks with overlap.
    
    Args:
        text: The text to chunk
        chunk_size: Maximum size of each chunk (in characters)
        overlap: Number of characters to overlap between chunks
    
    Returns:
        List of text chunks
    """
    if len(text) <= chunk_size:
        return [text]
    
    chunks = []
    start = 0
    
    while start < len(text):
        end = start + chunk_size
        
        # If not the last chunk, try to break at a sentence boundary
        if end < len(text):
            # Look for sentence endings within the last 100 characters
            search_start = max(start, end - 100)
            for i in range(end - 1, search_start, -1):
                if text[i] in '.!?\n':
                    end = i + 1
                    break
        
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        
        # Move start position with overlap
        start = end - overlap
        if start >= len(text):
            break
    
    return chunks


def chunk_documents(documents: List[dict]) -> List[dict]:
    """
    Chunk a list of documents (from PDF loader).
    
    Args:
        documents: List of document dicts with 'text', 'source', and optionally 'page'
    
    Returns:
        List of chunked documents with metadata
    """
    chunked_docs = []
    
    for doc in documents:
        chunks = chunk_text(doc['text'])
        
        for idx, chunk in enumerate(chunks):
            chunked_docs.append({
                'text': chunk,
                'source': doc['source'],
                'page': doc.get('page', None),
                'chunk_index': idx,
                'total_chunks': len(chunks)
            })
    
    return chunked_docs

