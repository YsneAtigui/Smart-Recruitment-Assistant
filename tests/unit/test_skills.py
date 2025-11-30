"""
Unit tests for skill matching.
"""
import pytest
from src.matching.skills import SkillMatcher


@pytest.mark.unit
class TestSkillMatcher:
    """Tests for SkillMatcher class."""
    
    def test_initialization(self):
        """Test SkillMatcher initialization."""
        matcher = SkillMatcher()
        assert matcher is not None
        assert matcher.fuzzy_threshold > 0
        assert matcher.semantic_threshold > 0
        
    def test_normalize_skill(self):
        """Test skill normalization."""
        matcher = SkillMatcher()
        
        # Test synonym mapping
        assert matcher.normalize_skill("JS") == "javascript"
        assert matcher.normalize_skill("Python3") == "python"
        assert matcher.normalize_skill("React.js") == "react"
        
        # Test unknown skills (should lowercase)
        assert matcher.normalize_skill("UnknownSkill") == "unknownskill"
        
    def test_match_skills_exact_match(self):
        """Test exact skill matching."""
        matcher = SkillMatcher()
        cv_skills = ["Python", "JavaScript", "Docker"]
        jd_skills = ["Python", "JavaScript", "Docker"]
        
        matched, missing, details = matcher.match_skills(cv_skills, jd_skills)
        
        assert len(matched) == 3
        assert len(missing) == 0
        assert all(details[skill]["method"] == "exact" for skill in matched)
        
    def test_match_skills_no_match(self):
        """Test with no matching skills."""
        matcher = SkillMatcher()
        cv_skills = ["Python", "Django"]
        jd_skills = ["Java", "Spring"]
        
        matched, missing, details = matcher.match_skills(cv_skills, jd_skills)
        
        assert len(matched) == 0
        assert len(missing) == 2
        
    def test_match_skills_fuzzy_match(self):
        """Test fuzzy skill matching."""
        matcher = SkillMatcher()
        cv_skills = ["JavaScript", "React.js", "PostgreSQL"]
        jd_skills = ["JS", "ReactJS", "Postgres"]
        
        matched, missing, details = matcher.match_skills(cv_skills, jd_skills)
        
        # Should match most skills via fuzzy or exact matching
        assert len(matched) >= 2
        
    def test_match_skills_empty_cv(self):
        """Test with empty CV skills."""
        matcher = SkillMatcher()
        cv_skills = []
        jd_skills = ["Python", "JavaScript"]
        
        matched, missing, details = matcher.match_skills(cv_skills, jd_skills)
        
        assert len(matched) == 0
        assert len(missing) == 2
        
    def test_match_skills_empty_jd(self):
        """Test with empty JD skills."""
        matcher = SkillMatcher()
        cv_skills = ["Python", "JavaScript"]
        jd_skills = []
        
        matched, missing, details = matcher.match_skills(cv_skills, jd_skills)
        
        assert len(matched) == 0
        assert len(missing) == 0
        
    def test_match_details_structure(self):
        """Test match details structure."""
        matcher = SkillMatcher()
        cv_skills = ["Python", "JavaScript"]
        jd_skills = ["Python"]
        
        matched, missing, details = matcher.match_skills(cv_skills, jd_skills)
        
        assert "Python" in details
        assert "method" in details["Python"]
        assert "score" in details["Python"]
        assert "matched_cv_skill" in details["Python"]
        
    def test_get_skill_categories(self):
        """Test skill categorization."""
        matcher = SkillMatcher()
        skills = ["Python", "JavaScript", "React", "PostgreSQL", "Docker", "AWS", "Machine Learning"]
        
        categories = matcher.get_skill_categories(skills)
        
        assert isinstance(categories, dict)
        assert "Programming Languages" in categories
        assert "Python" in categories["Programming Languages"]
        assert "JavaScript" in categories["Programming Languages"]
