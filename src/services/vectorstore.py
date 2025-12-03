"""Vector store service using ChromaDB."""

from typing import Dict, List, Optional, Tuple

import chromadb
from chromadb.config import Settings

from src.services.embeddings import get_embedding_service
from src.utils.config import get_config
from src.utils.logging_config import get_logger

logger = get_logger(__name__)


class VectorStoreService:
    """Service for managing vector embeddings using ChromaDB."""

    def __init__(
        self,
        persist_directory: Optional[str] = None,
        collection_name: Optional[str] = None,
    ):
        """
        Initialize vector store service.

        Args:
            persist_directory: Directory for persisting ChromaDB data.
                             If None, uses config default.
            collection_name: Name of the collection. If None, uses config default.
        """
        config = get_config()
        self.persist_directory = persist_directory or config.chromadb.persist_directory
        self.collection_name = collection_name or config.chromadb.collection_name

        logger.info(f"Initializing ChromaDB at: {self.persist_directory}")

        # Initialize ChromaDB client with persistence
        self.client = chromadb.PersistentClient(
            path=self.persist_directory,
            settings=Settings(
                anonymized_telemetry=False,
                allow_reset=True,
            ),
        )

        # Get or create collection
        self.collection = self.client.get_or_create_collection(
            name=self.collection_name,
            metadata={"description": "Feedback embeddings for RAG system"},
        )

        self.embedding_service = get_embedding_service()

        logger.info(
            f"ChromaDB initialized. Collection: {self.collection_name}, "
            f"Documents: {self.collection.count()}"
        )

    def add_documents(
        self,
        documents: List[str],
        metadata: Optional[List[Dict]] = None,
        ids: Optional[List[str]] = None,
    ) -> List[str]:
        """
        Add documents to the vector store.

        Args:
            documents: List of text documents to add
            metadata: Optional list of metadata dicts for each document
            ids: Optional list of custom IDs. If None, auto-generated.

        Returns:
            List[str]: List of document IDs
        """
        if not documents:
            logger.warning("No documents provided to add")
            return []

        try:
            # Generate embeddings
            logger.info(f"Adding {len(documents)} documents to vector store")
            embeddings = self.embedding_service.generate_embeddings(documents)

            # Generate IDs if not provided
            if ids is None:
                existing_count = self.collection.count()
                ids = [f"doc_{existing_count + i}" for i in range(len(documents))]

            # Prepare metadata
            if metadata is None:
                metadata = [{"text": doc} for doc in documents]

            # Add to collection
            self.collection.add(
                embeddings=embeddings,
                documents=documents,
                metadatas=metadata,
                ids=ids,
            )

            logger.info(f"Successfully added {len(documents)} documents")
            return ids

        except Exception as e:
            logger.error(f"Error adding documents to vector store: {str(e)}")
            raise

    def search(
        self,
        query: str,
        n_results: int = 5,
        where: Optional[Dict] = None,
    ) -> Dict:
        """
        Search for similar documents using a query string.

        Args:
            query: Query text
            n_results: Number of results to return
            where: Optional metadata filter

        Returns:
            Dict: Search results with documents, distances, and metadata
        """
        if not query or not query.strip():
            logger.warning("Empty query provided for search")
            return {"documents": [], "distances": [], "metadatas": [], "ids": []}

        try:
            # Generate query embedding
            query_embedding = self.embedding_service.generate_embedding(query)

            # Search in collection
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=n_results,
                where=where,
            )

            logger.info(f"Search completed. Found {len(results['ids'][0])} results")

            return {
                "documents": results["documents"][0],
                "distances": results["distances"][0],
                "metadatas": results["metadatas"][0],
                "ids": results["ids"][0],
            }

        except Exception as e:
            logger.error(f"Error searching vector store: {str(e)}")
            raise

    def search_by_embedding(
        self,
        embedding: List[float],
        n_results: int = 5,
        where: Optional[Dict] = None,
    ) -> Dict:
        """
        Search for similar documents using an embedding vector.

        Args:
            embedding: Query embedding vector
            n_results: Number of results to return
            where: Optional metadata filter

        Returns:
            Dict: Search results with documents, distances, and metadata
        """
        try:
            results = self.collection.query(
                query_embeddings=[embedding],
                n_results=n_results,
                where=where,
            )

            return {
                "documents": results["documents"][0],
                "distances": results["distances"][0],
                "metadatas": results["metadatas"][0],
                "ids": results["ids"][0],
            }

        except Exception as e:
            logger.error(f"Error searching by embedding: {str(e)}")
            raise

    def get_document(self, doc_id: str) -> Optional[Dict]:
        """
        Get a specific document by ID.

        Args:
            doc_id: Document ID

        Returns:
            Optional[Dict]: Document data or None if not found
        """
        try:
            result = self.collection.get(ids=[doc_id])

            if not result["ids"]:
                return None

            return {
                "id": result["ids"][0],
                "document": result["documents"][0],
                "metadata": result["metadatas"][0],
                "embedding": result["embeddings"][0] if result["embeddings"] else None,
            }

        except Exception as e:
            logger.error(f"Error getting document {doc_id}: {str(e)}")
            raise

    def delete_documents(self, ids: List[str]) -> None:
        """
        Delete documents by IDs.

        Args:
            ids: List of document IDs to delete
        """
        try:
            self.collection.delete(ids=ids)
            logger.info(f"Deleted {len(ids)} documents")

        except Exception as e:
            logger.error(f"Error deleting documents: {str(e)}")
            raise

    def get_all_documents(self, limit: Optional[int] = None) -> Dict:
        """
        Get all documents from the collection.

        Args:
            limit: Optional limit on number of documents to return

        Returns:
            Dict: All documents with metadata
        """
        try:
            result = self.collection.get(limit=limit)

            return {
                "ids": result["ids"],
                "documents": result["documents"],
                "metadatas": result["metadatas"],
            }

        except Exception as e:
            logger.error(f"Error getting all documents: {str(e)}")
            raise

    def count(self) -> int:
        """
        Get count of documents in collection.

        Returns:
            int: Number of documents
        """
        return self.collection.count()

    def clear(self) -> None:
        """Clear all documents from the collection."""
        try:
            # Get all document IDs
            all_docs = self.collection.get()
            if all_docs["ids"]:
                self.collection.delete(ids=all_docs["ids"])
            logger.info("Cleared all documents from collection")

        except Exception as e:
            logger.error(f"Error clearing collection: {str(e)}")
            raise

    def get_stats(self) -> Dict:
        """
        Get statistics about the vector store.

        Returns:
            Dict: Statistics including document count
        """
        return {
            "collection_name": self.collection_name,
            "document_count": self.count(),
            "persist_directory": self.persist_directory,
        }


# Global vector store service instance
_vector_store_service: Optional[VectorStoreService] = None


def get_vector_store_service() -> VectorStoreService:
    """
    Get global vector store service instance.

    Returns:
        VectorStoreService: Global vector store service
    """
    global _vector_store_service
    if _vector_store_service is None:
        _vector_store_service = VectorStoreService()
    return _vector_store_service
