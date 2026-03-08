"""
End-to-end RAG pipeline module.
Orchestrates the complete RAG workflow from PDF loading to retrieval.
"""
from typing import List, Dict
from parentdashboard.rag.loader import load_pdfs, load_single_pdf
from parentdashboard.rag.chunker import chunk_documents
from parentdashboard.rag.embeddings import EmbeddingGenerator
from parentdashboard.rag.vector_store import VectorStore
from parentdashboard.rag.retriever import Retriever


class RAGPipeline:
    """Complete RAG pipeline for document processing and retrieval."""
    
    def __init__(self):
        """Initialize the RAG pipeline components."""
        self.embedding_generator = EmbeddingGenerator()
        self.vector_store = VectorStore()
        self.retriever = Retriever(self.vector_store, self.embedding_generator)
        self._is_initialized = False
    
    def initialize(self, force_reload: bool = False) -> None:
        """
        Initialize the RAG pipeline by loading and indexing PDFs.
        
        Args:
            force_reload: If True, reload PDFs even if vector store has data
        """
        # Check if vector store already has data
        if not force_reload and self.vector_store.get_count() > 0:
            print("Vector store already has data. Skipping initialization.")
            self._is_initialized = True
            return
        
        print("Initializing RAG pipeline...")
        
        # Load PDFs
        print("Loading PDFs...")
        documents = load_pdfs()
        
        if not documents:
            print("No PDFs found in the knowledge base directory.")
            self._is_initialized = True
            return
        
        print(f"Loaded {len(documents)} document pages")
        
        # Chunk documents
        print("Chunking documents...")
        chunked_docs = chunk_documents(documents)
        print(f"Created {len(chunked_docs)} chunks")
        
        # Generate embeddings
        print("Generating embeddings...")
        texts = [doc['text'] for doc in chunked_docs]
        embeddings = self.embedding_generator.generate_embeddings(texts)
        
        # Prepare metadata
        metadatas = [
            {
                'source': doc['source'],
                'page': doc.get('page'),
                'chunk_index': doc.get('chunk_index'),
                'total_chunks': doc.get('total_chunks')
            }
            for doc in chunked_docs
        ]
        
        # Clear existing data if force_reload
        if force_reload:
            self.vector_store.delete_all()
        
        # Add to vector store
        print("Adding to vector store...")
        self.vector_store.add_documents(texts, embeddings, metadatas)
        
        self._is_initialized = True
        print("RAG pipeline initialized successfully!")
    
    def retrieve_context(self, query: str, top_k: int = 3) -> List[Dict]:
        """
        Retrieve relevant context for a query.
        
        Args:
            query: User's question
            top_k: Number of chunks to retrieve
        
        Returns:
            List of relevant chunks with metadata
        """
        if not self._is_initialized:
            self.initialize()
        
        return self.retriever.retrieve(query, top_k)
    
    def get_retriever(self) -> Retriever:
        """Get the retriever instance."""
        if not self._is_initialized:
            self.initialize()
        return self.retriever
    
    def add_single_pdf(self, filename: str) -> None:
        """
        Add a single PDF to the vector store without reloading everything.
        This is much faster than reloading the entire knowledge base.
        
        Args:
            filename: Name of the PDF file to add
        """
        print(f"Adding single PDF: {filename}")
        
        # Load the single PDF
        documents = load_single_pdf(filename)
        
        if not documents:
            print(f"No content found in PDF {filename}")
            return
        
        print(f"Loaded {len(documents)} document pages from {filename}")
        
        # Chunk documents
        chunked_docs = chunk_documents(documents)
        print(f"Created {len(chunked_docs)} chunks from {filename}")
        
        # Generate embeddings
        texts = [doc['text'] for doc in chunked_docs]
        embeddings = self.embedding_generator.generate_embeddings(texts)
        
        # Prepare metadata
        metadatas = [
            {
                'source': doc['source'],
                'page': doc.get('page'),
                'chunk_index': doc.get('chunk_index'),
                'total_chunks': doc.get('total_chunks')
            }
            for doc in chunked_docs
        ]
        
        # Remove any existing documents with this source (in case of re-upload)
        self.vector_store.delete_by_source(filename)
        
        # Add to vector store
        self.vector_store.add_documents(texts, embeddings, metadatas)
        
        print(f"Successfully added {filename} to vector store")
    
    def remove_single_pdf(self, filename: str) -> None:
        """
        Remove a single PDF from the vector store without reloading everything.
        This is much faster than reloading the entire knowledge base.
        
        Args:
            filename: Name of the PDF file to remove
        """
        print(f"Removing single PDF: {filename}")
        
        # Remove documents with this source from vector store
        self.vector_store.delete_by_source(filename)
        
        print(f"Successfully removed {filename} from vector store")

