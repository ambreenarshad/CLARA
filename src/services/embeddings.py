"""Embedding service using sentence-transformers."""

from typing import List, Optional

import numpy as np
from sentence_transformers import SentenceTransformer

from src.utils.config import get_config
from src.utils.logging_config import get_logger

logger = get_logger(__name__)


class EmbeddingService:
    """Service for generating text embeddings using sentence-transformers."""

    def __init__(self, model_name: Optional[str] = None):
        """
        Initialize embedding service.

        Args:
            model_name: Name of sentence-transformers model.
                       If None, uses config default.
        """
        config = get_config()
        self.model_name = model_name or config.models.embedding_model
        self.dimension = config.models.embedding_dimension

        logger.info(f"Loading embedding model: {self.model_name}")
        self.model = SentenceTransformer(self.model_name)
        logger.info(f"Embedding model loaded successfully. Dimension: {self.dimension}")

    def generate_embedding(self, text: str) -> List[float]:
        """
        Generate embedding for a single text.

        Args:
            text: Input text to embed

        Returns:
            List[float]: Embedding vector
        """
        if not text or not text.strip():
            logger.warning("Empty text provided for embedding")
            return [0.0] * self.dimension

        try:
            embedding = self.model.encode(text, convert_to_numpy=True)
            return embedding.tolist()
        except Exception as e:
            logger.error(f"Error generating embedding: {str(e)}")
            raise

    def generate_embeddings(
        self,
        texts: List[str],
        batch_size: int = 32,
        show_progress: bool = False,
    ) -> List[List[float]]:
        """
        Generate embeddings for multiple texts.

        Args:
            texts: List of input texts to embed
            batch_size: Batch size for processing
            show_progress: Whether to show progress bar

        Returns:
            List[List[float]]: List of embedding vectors
        """
        if not texts:
            logger.warning("Empty text list provided for embeddings")
            return []

        try:
            logger.info(f"Generating embeddings for {len(texts)} texts")

            # Filter out empty texts and track indices
            valid_texts = []
            valid_indices = []
            for idx, text in enumerate(texts):
                if text and text.strip():
                    valid_texts.append(text)
                    valid_indices.append(idx)

            if not valid_texts:
                logger.warning("No valid texts found after filtering")
                return [[0.0] * self.dimension] * len(texts)

            # Generate embeddings for valid texts
            embeddings = self.model.encode(
                valid_texts,
                batch_size=batch_size,
                show_progress_bar=show_progress,
                convert_to_numpy=True,
            )

            # Create result list with proper ordering
            result = [[0.0] * self.dimension] * len(texts)
            for idx, embedding in zip(valid_indices, embeddings):
                result[idx] = embedding.tolist()

            logger.info(f"Generated {len(valid_texts)} embeddings successfully")
            return result

        except Exception as e:
            logger.error(f"Error generating batch embeddings: {str(e)}")
            raise

    def compute_similarity(self, embedding1: List[float], embedding2: List[float]) -> float:
        """
        Compute cosine similarity between two embeddings.

        Args:
            embedding1: First embedding vector
            embedding2: Second embedding vector

        Returns:
            float: Cosine similarity score (-1 to 1)
        """
        try:
            vec1 = np.array(embedding1)
            vec2 = np.array(embedding2)

            # Compute cosine similarity
            similarity = np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))
            return float(similarity)

        except Exception as e:
            logger.error(f"Error computing similarity: {str(e)}")
            raise

    def compute_similarities(
        self,
        query_embedding: List[float],
        embeddings: List[List[float]],
    ) -> List[float]:
        """
        Compute cosine similarities between a query and multiple embeddings.

        Args:
            query_embedding: Query embedding vector
            embeddings: List of embedding vectors to compare against

        Returns:
            List[float]: List of similarity scores
        """
        try:
            query_vec = np.array(query_embedding)
            embedding_matrix = np.array(embeddings)

            # Compute cosine similarities
            similarities = np.dot(embedding_matrix, query_vec) / (
                np.linalg.norm(embedding_matrix, axis=1) * np.linalg.norm(query_vec)
            )

            return similarities.tolist()

        except Exception as e:
            logger.error(f"Error computing batch similarities: {str(e)}")
            raise

    def get_model_info(self) -> dict:
        """
        Get information about the loaded model.

        Returns:
            dict: Model information
        """
        return {
            "model_name": self.model_name,
            "embedding_dimension": self.dimension,
            "max_seq_length": self.model.max_seq_length,
        }


# Global embedding service instance
_embedding_service: Optional[EmbeddingService] = None


def get_embedding_service() -> EmbeddingService:
    """
    Get global embedding service instance.

    Returns:
        EmbeddingService: Global embedding service
    """
    global _embedding_service
    if _embedding_service is None:
        _embedding_service = EmbeddingService()
    return _embedding_service
