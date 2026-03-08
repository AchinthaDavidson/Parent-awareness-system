"""
Embeddings generation module for RAG pipeline.
Generates vector embeddings for text chunks.
Supports multilingual queries (Sinhala + English).
"""

from typing import List
from sentence_transformers import SentenceTransformer
from parentdashboard.config import EMBEDDING_MODEL


class EmbeddingGenerator:
    """Generates embeddings for text using sentence transformers."""

    def __init__(self, model_name: str = EMBEDDING_MODEL):
        """
        Initialize the embedding model.

        Args:
            model_name: Name of the sentence transformer model
        """
        print(f"Loading embedding model: {model_name}")
        self.model = SentenceTransformer(model_name)
        print("Embedding model loaded successfully")

    def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for document passages (PDF chunks).

        Args:
            texts: List of text strings to embed

        Returns:
            List of embedding vectors
        """
        if not texts:
            return []

        # REQUIRED for multilingual-e5 models
        passages = [f"passage: {text}" for text in texts]

        embeddings = self.model.encode(
            passages,
            show_progress_bar=True,
            convert_to_numpy=True,
            normalize_embeddings=True
        )

        return embeddings.tolist()

    def generate_embedding(self, text: str) -> List[float]:
        """
        Generate embedding for a user query (Sinhala or English).

        Args:
            text: User question

        Returns:
            Embedding vector
        """
        # REQUIRED for multilingual-e5 models
        query = f"query: {text}"

        embedding = self.model.encode(
            query,
            convert_to_numpy=True,
            normalize_embeddings=True
        )

        return embedding.tolist()
