"""
Unit tests for entity models (CV, JobDescription, MatchResult).
"""
import pytest
import numpy as np
from src.models import CV, JobDescription, MatchResult


@pytest.mark.unit
class TestCV:
    """Tests for CV entity."""
    
    def test_cv_creation(self, sample_cv_data, sample_cv_text):
        """Test creating a CV entity."""
        cv = CV(
            raw_text=sample_cv_text,
            name=sample_cv_data["name"],
            contact=sample_cv_data["contact"],
            skills=sample_cv_data["skills"],
            education=sample_cv_data["education"],
            experience=sample_cv_data["experience"],
            diplomas=sample_cv_data["diplomas"],
            academic_projects=sample_cv_data["academic_projects"]
        )
        
        assert cv.name == "John Doe"
        assert cv.contact["email"] == "john.doe@example.com"
        assert len(cv.skills) == 7
        assert len(cv.experience) == 2
        
    def test_cv_normalize_skills(self, sample_cv_entity):
        """Test skill normalization."""
        normalized = sample_cv_entity.normalize_skills()
        assert isinstance(normalized, list)
        assert all(isinstance(s, str) for s in normalized)
        assert all(s.islower() for s in normalized)
    
    def test_cv_get_years_of_experience(self, sample_cv_entity):
        """Test years of experience extraction."""
        years = sample_cv_entity.get_years_of_experience()
        assert years is not None
        assert years >= 5  # 3 + 2 years
        
    def test_cv_with_embedding(self, sample_cv_entity, mock_embedding):
        """Test CV with embedding."""
        assert sample_cv_entity.embedding is not None
        assert sample_cv_entity.embedding.shape == (384,)


@pytest.mark.unit
class TestJobDescription:
    """Tests for JobDescription entity."""
    
    def test_jd_creation(self, sample_jd_data, sample_jd_text):
        """Test creating a JobDescription entity."""
        jd = JobDescription(
            raw_text=sample_jd_text,
            job_title=sample_jd_data["job_title"],
            company_name=sample_jd_data["company_name"],
            location=sample_jd_data["location"],
            job_type=sample_jd_data["job_type"],
            responsibilities=sample_jd_data["responsibilities"],
            skills=sample_jd_data["skills"],
            experience_level=sample_jd_data["experience_level"],
            education_requirements=sample_jd_data["education_requirements"]
        )
        
        assert jd.job_title == "Senior Full-Stack Developer"
        assert jd.company_name == "InnovateTech Solutions"
        assert len(jd.skills) == 6
        assert jd.experience_level == "4-6 years"
        
    def test_jd_normalize_skills(self, sample_jd_entity):
        """Test skill normalization."""
        normalized = sample_jd_entity.normalize_skills()
        assert isinstance(normalized, list)
        assert all(isinstance(s, str) for s in normalized)
        
    def test_jd_get_required_years(self, sample_jd_entity):
        """Test required years extraction."""
        years = sample_jd_entity.get_required_years_of_experience()
        assert years is not None
        assert years >= 4


@pytest.mark.unit
class TestMatchResult:
    """Tests for MatchResult entity."""
    
    def test_match_result_creation(self, sample_cv_entity, sample_jd_entity):
        """Test creating a MatchResult."""
        result = MatchResult(
            cv=sample_cv_entity,
            job_description=sample_jd_entity,
            total_score=75.5,
            semantic_score=0.82,
            skill_match_ratio=0.7,
            matched_skills=["Python", "JavaScript", "React"],
            missing_skills=["TypeScript"],
            experience_score=0.85,
            education_score=0.9,
            strengths=["Strong technical skills"],
            weaknesses=["Missing TypeScript"],
            recommendations=["Learn TypeScript"],
            match_details={}
        )
        
        assert result.total_score == 75.5
"""
Unit tests for entity models (CV, JobDescription, MatchResult).
"""
import pytest
import numpy as np
from src.models import CV, JobDescription, MatchResult


@pytest.mark.unit
class TestCV:
    """Tests for CV entity."""
    
    def test_cv_creation(self, sample_cv_data, sample_cv_text):
        """Test creating a CV entity."""
        cv = CV(
            raw_text=sample_cv_text,
            name=sample_cv_data["name"],
            contact=sample_cv_data["contact"],
            skills=sample_cv_data["skills"],
            education=sample_cv_data["education"],
            experience=sample_cv_data["experience"],
            diplomas=sample_cv_data["diplomas"],
            academic_projects=sample_cv_data["academic_projects"]
        )
        
        assert cv.name == "John Doe"
        assert cv.contact["email"] == "john.doe@example.com"
        assert len(cv.skills) == 7
        assert len(cv.experience) == 2
        
    def test_cv_normalize_skills(self, sample_cv_entity):
        """Test skill normalization."""
        normalized = sample_cv_entity.normalize_skills()
        assert isinstance(normalized, list)
        assert all(isinstance(s, str) for s in normalized)
        assert all(s.islower() for s in normalized)
    
    def test_cv_get_years_of_experience(self, sample_cv_entity):
        """Test years of experience extraction."""
        years = sample_cv_entity.get_years_of_experience()
        assert years is not None
        assert years >= 5  # 3 + 2 years
        
    def test_cv_with_embedding(self, sample_cv_entity, mock_embedding):
        """Test CV with embedding."""
        assert sample_cv_entity.embedding is not None
        assert sample_cv_entity.embedding.shape == (384,)


@pytest.mark.unit
class TestJobDescription:
    """Tests for JobDescription entity."""
    
    def test_jd_creation(self, sample_jd_data, sample_jd_text):
        """Test creating a JobDescription entity."""
        jd = JobDescription(
            raw_text=sample_jd_text,
            job_title=sample_jd_data["job_title"],
            company_name=sample_jd_data["company_name"],
            location=sample_jd_data["location"],
            job_type=sample_jd_data["job_type"],
            responsibilities=sample_jd_data["responsibilities"],
            skills=sample_jd_data["skills"],
            experience_level=sample_jd_data["experience_level"],
            education_requirements=sample_jd_data["education_requirements"]
        )
        
        assert jd.job_title == "Senior Full-Stack Developer"
        assert jd.company_name == "InnovateTech Solutions"
        assert len(jd.skills) == 6
        assert jd.experience_level == "4-6 years"
        
    def test_jd_normalize_skills(self, sample_jd_entity):
        """Test skill normalization."""
        normalized = sample_jd_entity.normalize_skills()
        assert isinstance(normalized, list)
        assert all(isinstance(s, str) for s in normalized)
        
    def test_jd_get_required_years(self, sample_jd_entity):
        """Test required years extraction."""
        years = sample_jd_entity.get_required_years_of_experience()
        assert years is not None
        assert years >= 4


@pytest.mark.unit
class TestMatchResult:
    """Tests for MatchResult entity."""
    
    def test_match_result_creation(self, sample_cv_entity, sample_jd_entity):
        """Test creating a MatchResult."""
        result = MatchResult(
            cv=sample_cv_entity,
            job_description=sample_jd_entity,
            total_score=75.5,
            semantic_score=0.82,
            skill_match_ratio=0.7,
            matched_skills=["Python", "JavaScript", "React"],
            missing_skills=["TypeScript"],
            experience_score=0.85,
            education_score=0.9,
            strengths=["Strong technical skills"],
            weaknesses=["Missing TypeScript"],
            recommendations=["Learn TypeScript"],
            match_details={}
        )
        
        assert result.total_score == 75.5
        assert result.semantic_score == 0.82
        assert len(result.matched_skills) == 3
        assert len(result.missing_skills) == 1
        
    def test_get_grade(self, sample_cv_entity, sample_jd_entity):
        """Test grade calculation."""
        # Test A+ grade (90+)
        result = MatchResult(
            cv=sample_cv_entity,
            job_description=sample_jd_entity,
            total_score=92.0,
            semantic_score=0.9,
            skill_match_ratio=0.9,
            matched_skills=[],
            missing_skills=[],
            experience_score=0.9,
            education_score=0.9,
            strengths=[],
            weaknesses=[],
            recommendations=[],
            match_details={}
        )
        assert result.get_grade() == "A+"
        
        # Test A grade (85-89)
        result.total_score = 85.0
        assert result.get_grade() == "A"
        
        # Test B+ grade (75-79)
        result.total_score = 75.0
        assert result.get_grade() == "B+"
        
    def test_get_match_quality(self, sample_cv_entity, sample_jd_entity):
        """Test match quality assessment."""
        result = MatchResult(
            cv=sample_cv_entity,
            job_description=sample_jd_entity,
            total_score=92.0,
            semantic_score=0.9,
            skill_match_ratio=0.9,
            matched_skills=[],
            missing_skills=[],
            experience_score=0.9,
            education_score=0.9,
            strengths=[],
            weaknesses=[],
            recommendations=[],
            match_details={}
        )
        
        quality = result.get_match_quality()
        assert quality in ["Excellent Match", "Good Match", "Fair Match", "Poor Match"]
        assert quality == "Excellent Match"  # 92% score
