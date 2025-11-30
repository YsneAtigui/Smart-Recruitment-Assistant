"""
Unit tests for embedding generation.
"""
import pytest
import numpy as np
from src.utils.embeddings import generate_embeddings


@pytest.mark.unit
@pytest.mark.slow
class TestEmbeddings:
    """Tests for embedding generation."""
    
    def test_generate_single_embedding(self):
        """Test generating a single embedding."""
        texts = ["This is a test sentence."]
        embeddings = generate_embeddings(texts)
        
        assert len(embeddings) == 1
        assert isinstance(embeddings[0], np.ndarray)
        assert embeddings[0].shape == (384,)  # all-MiniLM-L6-v2 dimension
        
    def test_generate_multiple_embeddings(self):
        """Test generating multiple embeddings."""
        texts = [
            "First test sentence.",
            "Second test sentence.",
            "Third test sentence."
        ]
        embeddings = generate_embeddings(texts)
        
        assert len(embeddings) == 3
        assert all(isinstance(emb, np.ndarray) for emb in embeddings)
        assert all(emb.shape == (384,) for emb in embeddings)
        
    def test_embedding_reproducibility(self):
        """Test that same text produces same embedding."""
        text = "Reproducibility test"
        emb1 = generate_embeddings([text])[0]
        emb2 = generate_embeddings([text])[0]
        
        np.testing.assert_array_almost_equal(emb1, emb2)
        
    def test_different_texts_different_embeddings(self):
        """Test that different texts produce different embeddings."""
        text1 = "Python programming language"
        text2 = "Java programming language"
        
        emb1 = generate_embeddings([text1])[0]
        emb2 = generate_embeddings([text2])[0]
        
        # Should not be identical, but similar
        assert not np.array_equal(emb1, emb2)
        
        # Calculate similarity
        similarity = np.dot(emb1, emb2) / (np.linalg.norm(emb1) * np.linalg.norm(emb2))
        # Similar texts should have similarity > 0.5
        assert similarity > 0.5
        
    def test_empty_text(self):
        """Test with empty text."""
        texts = [""]
        embeddings = generate_embeddings(texts)
        
        assert len(embeddings) == 1
        assert isinstance(embeddings[0], np.ndarray)
