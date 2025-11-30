"""
Unit tests for validation utilities.
"""
import pytest
from src.utils.validation import EntityValidator, SkillValidator
from src.models import CV, JobDescription


@pytest.mark.unit
class TestSkillValidator:
    """Tests for SkillValidator."""
    
    def test_clean_skills_removes_empty(self):
        """Test that empty skills are removed."""
        skills = ["Python", "", "JavaScript", " ", "Docker"]
        cleaned = SkillValidator.clean_skills(skills)
        assert len(cleaned) == 3
        assert "" not in cleaned
        assert " " not in cleaned
        
    def test_clean_skills_removes_short(self):
        """Test that very short skills are removed."""
        skills = ["Python", "A", "JavaScript", "X"]
        cleaned = SkillValidator.clean_skills(skills)
        assert "A" not in cleaned
        assert "X" not in cleaned
        assert "Python" in cleaned
        
    def test_clean_skills_removes_non_alphanumeric(self):
        """Test that non-alphanumeric skills are removed."""
        skills = ["Python", "!!!", "JavaScript", "###"]
        cleaned = SkillValidator.clean_skills(skills)
        assert "!!!" not in cleaned
        assert "###" not in cleaned
        
    def test_deduplicate_skills_case_insensitive(self):
        """Test case-insensitive deduplication."""
        skills = ["Python", "python", "PYTHON", "JavaScript", "javascript"]
        deduped = SkillValidator.deduplicate_skills(skills)
        
        # Should keep first occurrence
        assert len(deduped) == 2
        assert "Python" in deduped
        assert "JavaScript" in deduped
        
    def test_deduplicate_skills_preserves_order(self):
        """Test that order is preserved."""
        skills = ["Python", "JavaScript", "Docker", "Python"]
        deduped = SkillValidator.deduplicate_skills(skills)
        assert deduped == ["Python", "JavaScript", "Docker"]


@pytest.mark.unit
class TestEntityValidator:
    """Tests for EntityValidator."""
    
    def test_validate_cv_with_good_data(self, sample_cv_entity):
        """Test CV validation with good data."""
        warnings = EntityValidator.validate_cv(sample_cv_entity)
        # Should have minimal warnings
        assert isinstance(warnings, list)
        
    def test_validate_cv_missing_skills(self):
        """Test CV validation with missing skills."""
        cv = CV(
            raw_text="Test CV",
            name="John Doe",
            contact={"email": "test@test.com"},
            skills=[],  # No skills
            education=[],
            experience=[],
            diplomas=[],
            academic_projects=[]
        )
        
        warnings = EntityValidator.validate_cv(cv)
        assert any("skills" in w.lower() for w in warnings)
        
    def test_validate_cv_no_experience(self):
        """Test CV validation with no experience."""
        cv = CV(
            raw_text="Test CV",
            name="John Doe",
            contact={"email": "test@test.com"},
            skills=["Python", "JavaScript", "Docker"],
            education=[],
            experience=[],  # No experience
            diplomas=[],
            academic_projects=[]
        )
        
        warnings = EntityValidator.validate_cv(cv)
        assert any("experience" in w.lower() for w in warnings)
        
    def test_validate_jd_with_good_data(self, sample_jd_entity):
        """Test JD validation with good data."""
        warnings = EntityValidator.validate_jd(sample_jd_entity)
        assert isinstance(warnings, list)
        
    def test_is_valid_for_matching_good_entities(self, sample_cv_entity, sample_jd_entity):
        """Test validity check with good entities."""
        is_valid = EntityValidator.is_valid_for_matching(sample_cv_entity, sample_jd_entity)
        assert is_valid is True
        
    def test_is_valid_for_matching_no_embedding(self, sample_cv_entity, sample_jd_entity):
        """Test validity check without embeddings."""
        sample_cv_entity.embedding = None
        is_valid = EntityValidator.is_valid_for_matching(sample_cv_entity, sample_jd_entity)
        assert is_valid is False
        
    def test_validate_and_report(self, sample_cv_entity, sample_jd_entity):
        """Test combined validation report."""
        report = EntityValidator.validate_and_report(sample_cv_entity, sample_jd_entity)
        
        assert "cv_warnings" in report
        assert "jd_warnings" in report
        assert isinstance(report["cv_warnings"], list)
        assert isinstance(report["jd_warnings"], list)
