from typing import List, Dict
from .embedding_generator import EmbeddingGenerator
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

class RAGPipeline:
    def __init__(self, embedding_generator: EmbeddingGenerator):
        """
        Initializes the RAGPipeline with an EmbeddingGenerator.

        Args:
            embedding_generator: An instance of EmbeddingGenerator.
        """
        self.embedding_generator = embedding_generator
        self.documents = []  # Stores original documents
        self.document_embeddings = []  # Stores embeddings of documents

    def add_documents(self, documents: List[str]):
        """
        Adds documents to the RAG pipeline and generates their embeddings.

        Args:
            documents: A list of strings, where each string is a document.
        """
        self.documents.extend(documents)
        new_embeddings = self.embedding_generator.generate_embeddings(documents)
        self.document_embeddings.extend(new_embeddings)

    def retrieve(self, query: str, k: int = 5) -> List[str]:
        """
        Retrieves the top-k most relevant documents for a given query.

        Args:
            query: The search query.
            k: The number of top documents to retrieve.

        Returns:
            A list of the retrieved document strings.
        """
        query_embedding = self.embedding_generator.generate_embeddings([query])[0]
        
        if not self.document_embeddings:
            return []

        similarities = cosine_similarity(
            np.array([query_embedding]), np.array(self.document_embeddings)
        )[0]

        # Get indices of top-k most similar documents
        top_k_indices = np.argsort(similarities)[::-1][:k]
        
        retrieved_documents = [self.documents[i] for i in top_k_indices]
        return retrieved_documents

    def generate_response(self, query: str, retrieved_documents: List[str]) -> str:
        """
        Generates a response based on the query and retrieved documents.
        This is a placeholder and would typically involve an LLM call.

        Args:
            query: The original query.
            retrieved_documents: A list of documents retrieved by the pipeline.

        Returns:
            A generated response string.
        """
        context = "\n".join(retrieved_documents)
        # In a real application, you would send this context and query to an LLM
        # For now, we'll just return a simple concatenated string.
        if context:
            return f"Query: {query}\n\nContext:\n{context}\n\n(Response from LLM would go here)"
        else:
            return f"Query: {query}\n\n(No relevant context found. Response from LLM would go here)"
