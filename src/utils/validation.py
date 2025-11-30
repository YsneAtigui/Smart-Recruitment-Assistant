"""
Data validation utilities for Smart Recruitment Assistant.
"""
from typing import List, Dict
from src.models import CV, JobDescription


class EntityValidator:
    """Validates extracted entity data."""
    
    @staticmethod
    def validate_cv(cv: CV) -> List[str]:
        """
        Validate CV and return list of warnings.
        
        Args:
            cv: CV entity to validate.
            
        Returns:
            List of warning messages.
        """
        warnings = []
        
        # Check skills
        if not cv.skills or len(cv.skills) < 3:
            warnings.append(
                "Very few skills extracted. Consider using Gemini-based extraction "
                "for better results."
            )
        
        # Check experience
        if not cv.experience or len(cv.experience) < 1:
            warnings.append("No experience entries found.")
        
        # Check name
        if not cv.name:
            warnings.append("Name not extracted from CV.")
        
        # Check contact info
        if not cv.contact.get("emails") and not cv.contact.get("email"):
            warnings.append("No email address found in CV.")
        
        # Check embedding
        if cv.embedding is None:
            warnings.append(
                "Embedding not generated. Cannot perform semantic matching."
            )
        
        # Check education
        if not cv.education and not cv.diplomas:
            warnings.append("No education or diploma information found.")
        
        # Check raw text length
        if len(cv.raw_text.strip()) < 100:
            warnings.append(
                "CV text is very short. Document extraction may have failed."
            )
        
        return warnings
    
    @staticmethod
    def validate_jd(jd: JobDescription) -> List[str]:
        """
        Validate Job Description and return list of warnings.
        
        Args:
            jd: JobDescription entity to validate.
            
        Returns:
            List of warning messages.
        """
        warnings = []
        
        # Check skills
        if not jd.skills or len(jd.skills) < 3:
            warnings.append(
                "Very few required skills found. Consider using Gemini-based "
                "extraction for better results."
            )
        
        # Check job title
        if not jd.job_title:
            warnings.append("Job title not extracted.")
        
        # Check embedding
        if jd.embedding is None:
            warnings.append(
                "Embedding not generated. Cannot perform semantic matching."
            )
        
        # Check responsibilities
        if not jd.responsibilities or len(jd.responsibilities) < 1:
            warnings.append("No job responsibilities found.")
        
        # Check experience level
        if not jd.experience_level:
            warnings.append("Experience level requirement not specified.")
        
        # Check raw text length
        if len(jd.raw_text.strip()) < 100:
            warnings.append(
                "Job description text is very short. Document extraction may have failed."
            )
        
        return warnings
    
    @staticmethod
    def validate_and_report(cv: CV, jd: JobDescription) -> Dict[str, List[str]]:
        """
        Validate both CV and JD and return combined report.
        
        Args:
            cv: CV entity to validate.
            jd: JobDescription entity to validate.
            
        Returns:
            Dictionary with 'cv_warnings' and 'jd_warnings' keys.
        """
        return {
            "cv_warnings": EntityValidator.validate_cv(cv),
            "jd_warnings": EntityValidator.validate_jd(jd),
        }
    
    @staticmethod
    def is_valid_for_matching(cv: CV, jd: JobDescription) -> bool:
        """
        Check if CV and JD are valid enough for matching.
        
        Args:
            cv: CV entity to check.
            jd: JobDescription entity to check.
            
        Returns:
            True if both have minimum required data for matching.
        """
        # Minimum requirements
        has_cv_embedding = cv.embedding is not None
        has_jd_embedding = jd.embedding is not None
        has_cv_skills = cv.skills and len(cv.skills) >= 1
        has_jd_skills = jd.skills and len(jd.skills) >= 1
        has_cv_text = len(cv.raw_text.strip()) >= 50
        has_jd_text = len(jd.raw_text.strip()) >= 50
        
        return all([
            has_cv_embedding,
            has_jd_embedding,
            has_cv_skills,
            has_jd_skills,
            has_cv_text,
            has_jd_text
        ])


class SkillValidator:
    """Validates skill lists."""
    
    @staticmethod
    def clean_skills(skills: List[str]) -> List[str]:
        """
        Clean and validate skill list.
        
        Args:
            skills: Raw skill list.
            
        Returns:
            Cleaned skill list.
        """
        if not skills:
            return []
        
        cleaned = []
        for skill in skills:
            if not skill:
                continue
            
            # Strip whitespace
            skill = skill.strip()
            
            # Skip empty or very short skills
            if len(skill) < 2:
                continue
            
            # Skip non-alphanumeric skills (likely parsing errors)
            if not any(c.isalnum() for c in skill):
                continue
            
            cleaned.append(skill)
        
        return cleaned
    
    @staticmethod
    def deduplicate_skills(skills: List[str]) -> List[str]:
        """
        Remove duplicate skills (case-insensitive).
        
        Args:
            skills: Skill list with potential duplicates.
            
        Returns:
            Deduplicated skill list.
        """
        seen = set()
        result = []
        
        for skill in skills:
            skill_lower = skill.lower()
            if skill_lower not in seen:
                seen.add(skill_lower)
                result.append(skill)
        
        return result
