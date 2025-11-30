"""
Integration tests for integration helpers.
"""
import pytest
from src.utils.integration import (
    dict_to_cv,
    dict_to_jd,
    validate_entities,
    match_cv_to_jd,
    quick_match
)


@pytest.mark.integration
class TestIntegrationHelpers:
    """Tests for integration helper functions."""
    
    def test_dict_to_cv(self, sample_cv_data, sample_cv_text):
        """Test converting dictionary to CV entity."""
        cv = dict_to_cv(sample_cv_data, sample_cv_text)
        
        assert cv.name == sample_cv_data["name"]
        assert cv.contact == sample_cv_data["contact"]
        assert len(cv.skills) > 0
        assert cv.raw_text == sample_cv_text
        
    def test_dict_to_jd(self, sample_jd_data, sample_jd_text):
        """Test converting dictionary to JD entity."""
        jd = dict_to_jd(sample_jd_data, sample_jd_text)
        
        assert jd.job_title == sample_jd_data["job_title"]
        assert jd.company_name == sample_jd_data["company_name"]
        assert len(jd.skills) > 0
        assert jd.raw_text == sample_jd_text
        
    def test_dict_to_cv_skill_cleaning(self):
        """Test that skills are cleaned during CV creation."""
        data = {
            "name": "Test",
            "contact": {},
            "skills": ["Python", "", "JavaScript", "  ", "X"],  # Has empty/short skills
            "experience": [],
            "education": [],
            "diplomas": [],
            "academic_projects": []
        }
        
        cv = dict_to_cv(data, "test")
        
        # Empty and very short skills should be removed
        assert "" not in cv.skills
        assert "X" not in cv.skills
        assert "Python" in cv.skills
        
    def test_validate_entities(self, sample_cv_entity, sample_jd_entity):
        """Test entity validation."""
        report = validate_entities(sample_cv_entity, sample_jd_entity)
        
        assert "cv_warnings" in report
        assert "jd_warnings" in report
        assert "is_valid_for_matching" in report
        assert isinstance(report["is_valid_for_matching"], bool)
        
    def test_match_cv_to_jd(self, sample_cv_entity, sample_jd_entity):
        """Test matching CV to JD."""
        result = match_cv_to_jd(sample_cv_entity, sample_jd_entity)
        
        assert result is not None
        assert hasattr(result, "total_score")
        assert hasattr(result, "matched_skills")
        assert hasattr(result, "missing_skills")
        assert 0 <= result.total_score <= 100


@pytest.mark.integration
@pytest.mark.slow
class TestQuickMatch:
    """Tests for quick_match function (end-to-end)."""
    
    def test_quick_match_with_gemini_mock(
        self,
        mocker,
        sample_cv_text,
        sample_jd_text,
        mock_gemini_cv_response,
        mock_gemini_jd_response
    ):
        """Test quick match with mocked Gemini responses."""
        # Mock Gemini API calls
        mock_response_cv = mocker.Mock()
        mock_response_cv.text = mock_gemini_cv_response
        
        mock_response_jd = mocker.Mock()
        mock_response_jd.text = mock_gemini_jd_response
        
        # Mock the generate_content method
        mocker.patch(
            'src.extraction.genai_model.generate_content',
            side_effect=[mock_response_cv, mock_response_jd]
        )
        
        # Run quick match
        result = quick_match(sample_cv_text, sample_jd_text)
        
        assert result is not None
        assert result.total_score >= 0
        assert result.total_score <= 100
        assert isinstance(result.matched_skills, list)
        assert isinstance(result.missing_skills, list)
