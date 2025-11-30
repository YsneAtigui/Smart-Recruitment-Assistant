"""
Unit tests for scoring functions.
"""
import pytest
import numpy as np
from src.matching.scoring import calculate_fit_score, skill_gap_analysis, calculate_hybrid_score


@pytest.mark.unit
class TestCalculateFitScore:
    """Tests for calculate_fit_score function."""
    
    def test_identical_embeddings(self):
        """Test score with identical embeddings."""
        embedding = np.random.rand(384)
        score = calculate_fit_score(embedding, embedding)
        
        assert isinstance(score, float)
        assert score == pytest.approx(1.0, abs=0.01)  # Should be very close to 1.0
        
    def test_orthogonal_embeddings(self):
        """Test score with orthogonal embeddings."""
        emb1 = np.zeros(384)
        emb1[0] = 1.0
        emb2 = np.zeros(384)
        emb2[1] = 1.0
        
        score = calculate_fit_score(emb1, emb2)
        assert score == pytest.approx(0.0, abs=0.1)
        
    def test_1d_embeddings(self):
        """Test with 1D arrays."""
        emb1 = np.random.rand(384)
        emb2 = np.random.rand(384)
        
        score = calculate_fit_score(emb1, emb2)
        assert 0.0 <= score <= 1.0
        
    def test_2d_embeddings(self):
        """Test with 2D arrays."""
        emb1 = np.random.rand(1, 384)
        emb2 = np.random.rand(1, 384)
        
        score = calculate_fit_score(emb1, emb2)
        assert 0.0 <= score <= 1.0


@pytest.mark.unit
class TestSkillGapAnalysis:
    """Tests for skill_gap_analysis function."""
    
    def test_perfect_match(self):
        """Test with perfect skill match."""
        cv_skills = ["Python", "JavaScript", "Docker"]
        jd_skills = ["Python", "JavaScript", "Docker"]
        
        missing, matched = skill_gap_analysis(cv_skills, jd_skills)
        
        assert len(missing) == 0
        assert len(matched) == 3
        
    def test_partial_match(self):
        """Test with partial skill match."""
        cv_skills = ["Python", "JavaScript"]
        jd_skills = ["Python", "JavaScript", "Docker", "Kubernetes"]
        
        missing, matched = skill_gap_analysis(cv_skills, jd_skills)
        
        assert len(matched) == 2
        assert len(missing) == 2
        assert "Docker" in missing
        assert "Kubernetes" in missing
        
    def test_no_match(self):
        """Test with no skill match."""
        cv_skills = ["Python", "Django"]
        jd_skills = ["Java", "Spring"]
        
        missing, matched = skill_gap_analysis(cv_skills, jd_skills)
        
        assert len(matched) == 0
        assert len(missing) == 2
        
    def test_fuzzy_matching(self):
        """Test fuzzy matching capability."""
        cv_skills = ["JavaScript", "React.js", "Node.js"]
        jd_skills = ["JS", "ReactJS", "NodeJS"]
        
        missing, matched = skill_gap_analysis(cv_skills, jd_skills, score_cutoff=70)
        
        # Should match most or all due to fuzzy matching
        assert len(matched) >= 2


@pytest.mark.unit
class TestCalculateHybridScore:
    """Tests for calculate_hybrid_score function."""
    
    def test_hybrid_score_calculation(self):
        """Test hybrid score with both semantic and skill matching."""
        cv_emb = np.random.rand(384)
        jd_emb = np.random.rand(384)
        cv_skills = ["Python", "JavaScript", "Docker"]
        jd_skills = ["Python", "JavaScript", "Kubernetes"]
        
        result = calculate_hybrid_score(cv_emb, jd_emb, cv_skills, jd_skills)
        
        assert "total_score" in result
        assert "semantic_score" in result
        assert "skill_match_ratio" in result
        assert "matched_skills" in result
        assert "missing_skills" in result
        
        assert 0 <= result["total_score"] <= 100
        assert 0 <= result["semantic_score"] <= 1
        assert 0 <= result["skill_match_ratio"] <= 1
        
    def test_hybrid_score_no_jd_skills(self):
        """Test hybrid score when JD has no skills."""
        cv_emb = np.random.rand(384)
        jd_emb = np.random.rand(384)
        cv_skills = ["Python", "JavaScript"]
        jd_skills = []
        
        result = calculate_hybrid_score(cv_emb, jd_emb, cv_skills, jd_skills)
        
        # When no skills required, should rely on semantic score only
        assert result["skill_match_ratio"] == 0.0
        assert result["total_score"] > 0  # Still has semantic component
        
    def test_custom_weights(self):
        """Test hybrid score with custom weights."""
        cv_emb = np.random.rand(384)
        jd_emb = np.random.rand(384)
        cv_skills = ["Python"]
        jd_skills = ["Python"]
        
        result = calculate_hybrid_score(
            cv_emb, jd_emb, cv_skills, jd_skills,
            semantic_weight=0.3,
            skill_weight=0.7
        )
        
        assert isinstance(result["total_score"], float)
