from sentence_transformers import SentenceTransformer
from typing import List

class EmbeddingGenerator:
    def __init__(self, model_name: str = 'all-MiniLM-L6-v2'):
        """
        Initializes the EmbeddingGenerator with a pre-trained SentenceTransformer model.

        Args:
            model_name: The name of the pre-trained model to use.
        """
        self.model = SentenceTransformer(model_name)

    def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """
        Generates embeddings for a list of texts.

        Args:
            texts: A list of strings to generate embeddings for.

        Returns:
            A list of embeddings, where each embedding is a list of floats.
        """
        embeddings = self.model.encode(texts).tolist()
        return embeddings
