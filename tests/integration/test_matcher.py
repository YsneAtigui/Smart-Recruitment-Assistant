"""
Integration tests for AdvancedMatcher.
"""
import pytest
from src.matching.matcher import AdvancedMatcher


@pytest.mark.integration
class TestAdvancedMatcher:
    """Tests for AdvancedMatcher class."""
    
    def test_matcher_initialization(self):
        """Test matcher initialization with default weights."""
        matcher = AdvancedMatcher()
        assert matcher is not None
        assert matcher.weights is not None
        assert sum(matcher.weights.values()) == pytest.approx(1.0, abs=0.01)
        
    def test_matcher_custom_weights(self):
        """Test matcher with custom weights."""
        custom_weights = {
            "semantic": 0.4,
            "skills": 0.4,
            "experience": 0.1,
            "education": 0.1
        }
        matcher = AdvancedMatcher(weights=custom_weights)
        assert matcher.weights == custom_weights
        
    def test_matcher_invalid_weights(self):
        """Test that invalid weights raise an error."""
        invalid_weights = {
            "semantic": 0.5,
            "skills": 0.3,
            "experience": 0.1,
            "education": 0.05  # Sum is 0.95, not 1.0
        }
        
        with pytest.raises(ValueError):
            AdvancedMatcher(weights=invalid_weights)
            
    def test_match_basic(self, sample_cv_entity, sample_jd_entity):
        """Test basic matching functionality."""
        matcher = AdvancedMatcher()
        result = matcher.match(sample_cv_entity, sample_jd_entity)
        
        assert result is not None
        assert isinstance(result.total_score, float)
        assert 0 <= result.total_score <= 100
        assert isinstance(result.matched_skills, list)
        assert isinstance(result.missing_skills, list)
        
    def test_match_semantic_score(self, sample_cv_entity, sample_jd_entity):
        """Test that semantic score is calculated."""
        matcher = AdvancedMatcher()
        result = matcher.match(sample_cv_entity, sample_jd_entity)
        
        assert 0 <= result.semantic_score <= 1
        
    def test_match_skill_ratio(self, sample_cv_entity, sample_jd_entity):
        """Test that skill match ratio is calculated."""
        matcher = AdvancedMatcher()
        result = matcher.match(sample_cv_entity, sample_jd_entity)
        
        assert 0 <= result.skill_match_ratio <= 1
        assert len(result.matched_skills) + len(result.missing_skills) == len(sample_jd_entity.skills)
        
    def test_match_experience_score(self, sample_cv_entity, sample_jd_entity):
        """Test that experience score is calculated."""
        matcher = AdvancedMatcher()
        result = matcher.match(sample_cv_entity, sample_jd_entity)
        
        assert 0 <= result.experience_score <= 1
        
    def test_match_education_score(self, sample_cv_entity, sample_jd_entity):
        """Test that education score is calculated."""
        matcher = AdvancedMatcher()
        result = matcher.match(sample_cv_entity, sample_jd_entity)
        
        assert 0 <= result.education_score <= 1
        
    def test_match_generates_analysis(self, sample_cv_entity, sample_jd_entity):
        """Test that match generates analysis (strengths, weaknesses, recommendations)."""
        matcher = AdvancedMatcher()
        result = matcher.match(sample_cv_entity, sample_jd_entity)
        
        assert isinstance(result.strengths, list)
        assert isinstance(result.weaknesses, list)
        assert isinstance(result.recommendations, list)
        
    def test_match_details(self, sample_cv_entity, sample_jd_entity):
        """Test that match includes skill-level details."""
        matcher = AdvancedMatcher()
        result = matcher.match(sample_cv_entity, sample_jd_entity)
        
        assert isinstance(result.match_details, dict)
        # Should have details for all JD skills
        for skill in sample_jd_entity.skills:
            assert skill in result.match_details or skill.lower() in [s.lower() for s in result.match_details.keys()]
