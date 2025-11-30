"""
Helper functions to integrate new entity-based matching system.

This module provides utilities to convert between old dict-based format
and new entity classes, making it easy to integrate the new system.
"""
from typing import Dict, Any
import numpy as np

from src.models import CV, JobDescription, MatchResult
from src.extraction import (
    extract_information_from_cv_gemini,
    extract_information_from_jd_gemini
)
from src.utils.embeddings import generate_embeddings
from src.utils.validation import EntityValidator, SkillValidator
from config import Config


def dict_to_cv(data: Dict[str, Any], raw_text: str) -> CV:
    """
    Convert dictionary from extraction pipeline to CV entity.
    
    Args:
        data: Dictionary from extraction functions.
        raw_text: Raw text of the CV.
        
    Returns:
        CV entity.
    """
    # Handle different dict formats
    contact = data.get("contact", {})
    
    # Clean and validate skills
    skills = data.get("skills", [])
    if isinstance(skills, str):
        # If skills is a string, split by common delimiters
        skills = [s.strip() for s in skills.replace('\n', ',').split(',')]
    skills = SkillValidator.clean_skills(skills)
    skills = SkillValidator.deduplicate_skills(skills)
    
    cv = CV(
        raw_text=raw_text,
        name=data.get("name"),
        contact=contact,
        skills=skills,
        education=data.get("education", []) if isinstance(data.get("education"), list) else [data.get("education", "")],
        experience=data.get("experience", []) if isinstance(data.get("experience"), list) else [data.get("experience", "")],
        academic_projects=data.get("academic_projects", []),
        diplomas=data.get("diplomas", []),
    )
    
    return cv


def dict_to_jd(data: Dict[str, Any], raw_text: str) -> JobDescription:
    """
    Convert dictionary from extraction pipeline to JobDescription entity.
    
    Args:
        data: Dictionary from extraction functions.
        raw_text: Raw text of the job description.
        
    Returns:
        JobDescription entity.
    """
    # Clean and validate skills
    skills = data.get("skills", [])
    if isinstance(skills, str):
        skills = [s.strip() for s in skills.replace('\n', ',').split(',')]
    skills = SkillValidator.clean_skills(skills)
    skills = SkillValidator.deduplicate_skills(skills)
    
    jd = JobDescription(
        raw_text=raw_text,
        job_title=data.get("job_title"),
        company_name=data.get("company_name"),
        location=data.get("location"),
        job_type=data.get("job_type"),
        responsibilities=data.get("responsibilities", []),
        skills=skills,
        experience_level=data.get("experience_level"),
        education_requirements=data.get("education_requirements", []),
    )
    
    return jd


def extract_cv_to_entity(cv_text: str, use_gemini: bool = None) -> CV:
    """
    Extract CV text and convert to CV entity with embedding.
    
    Args:
        cv_text: Raw CV text.
        use_gemini: Deprecated. Gemini is now the only extraction method.
        
    Returns:
        CV entity with embedding.
        
    Raises:
        RuntimeError: If Gemini extraction fails.
    """
    if use_gemini is False:
        raise ValueError(
            "Traditional extraction is no longer supported. "
            "This application now uses Gemini API exclusively for entity extraction."
        )
    
    # Extract structured data using Gemini
    data = extract_information_from_cv_gemini(cv_text)
    
    # Convert to entity
    cv = dict_to_cv(data, cv_text)
    
    # Generate embedding
    cv.embedding = generate_embeddings([cv_text])[0]
    
    return cv


def extract_jd_to_entity(jd_text: str, use_gemini: bool = None) -> JobDescription:
    """
    Extract JD text and convert to JobDescription entity with embedding.
    
    Args:
        jd_text: Raw job description text.
        use_gemini: Deprecated. Gemini is now the only extraction method.
        
    Returns:
        JobDescription entity with embedding.
        
    Raises:
        RuntimeError: If Gemini extraction fails.
    """
    if use_gemini is False:
        raise ValueError(
            "Traditional extraction is no longer supported. "
            "This application now uses Gemini API exclusively for entity extraction."
        )
    
    # Extract structured data using Gemini
    data = extract_information_from_jd_gemini(jd_text)
    
    # Convert to entity
    jd = dict_to_jd(data, jd_text)
    
    # Generate embedding
    jd.embedding = generate_embeddings([jd_text])[0]
    
    return jd


def validate_entities(cv: CV, jd: JobDescription) -> Dict[str, Any]:
    """
    Validate CV and JD entities and return comprehensive report.
    
    Args:
        cv: CV entity.
        jd: JobDescription entity.
        
    Returns:
        Validation report with warnings and status.
    """
    report = EntityValidator.validate_and_report(cv, jd)
    report["is_valid_for_matching"] = EntityValidator.is_valid_for_matching(cv, jd)
    
    return report


def match_cv_to_jd(cv: CV, jd: JobDescription, weights: Dict[str, float] = None) -> MatchResult:
    """
    High-level function to match CV to JD using advanced matcher.
    
    Args:
        cv: CV entity (must have embedding).
        jd: JobDescription entity (must have embedding).
        weights: Optional custom weights for matching dimensions.
        
    Returns:
        MatchResult with comprehensive analysis.
    """
    from src.matching.matcher import AdvancedMatcher
    
    matcher = AdvancedMatcher(weights=weights)
    result = matcher.match(cv, jd)
    
    return result


def quick_match(cv_text: str, jd_text: str, use_gemini: bool = None) -> MatchResult:
    """
    Convenience function to match CV and JD texts in one call.
    
    This handles extraction, entity creation, and matching automatically.
    
    Args:
        cv_text: Raw CV text.
        jd_text: Raw job description text.
        use_gemini: Whether to use Gemini extraction.
        
    Returns:
        MatchResult.
    """
    # Extract entities
    cv = extract_cv_to_entity(cv_text, use_gemini=use_gemini)
    jd = extract_jd_to_entity(jd_text, use_gemini=use_gemini)
    
    # Match
    result = match_cv_to_jd(cv, jd)
    
    return result
