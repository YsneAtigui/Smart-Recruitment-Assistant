"""
Entity classes for Smart Recruitment Assistant.

This module defines the core data structures for CVs, Job Descriptions, and Match Results.
"""
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
import numpy as np
import re
from numpy.typing import NDArray


@dataclass
class CV:
    """Represents a candidate's CV with extracted information."""
    
    raw_text: str
    name: Optional[str] = None
    contact: Dict[str, Any] = field(default_factory=dict)
    skills: List[str] = field(default_factory=list)
    education: List[str] = field(default_factory=list)
    experience: List[str] = field(default_factory=list)
    academic_projects: List[str] = field(default_factory=list)
    diplomas: List[str] = field(default_factory=list)
    embedding: Optional[NDArray[np.float64]] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def normalize_skills(self) -> List[str]:
        """
        Normalize skills to lowercase and remove duplicates.
        
        Returns:
            List of normalized, unique skills.
        """
        if not self.skills:
            return []
        return list(set([s.lower().strip() for s in self.skills if s and s.strip()]))
    
    def get_years_of_experience(self) -> Optional[int]:
        """
        Extract total years of experience from experience entries.
        
        Uses regex to find year mentions like "2 years", "3 ans", etc.
        
        Returns:
            Total years of experience or None if cannot be determined.
        """
        if not self.experience:
            return None
        
        total_years = 0
        year_patterns = [
            r'(\d+)\s*(?:years?|ans?)',  # "2 years", "3 ans"
            r'(\d{4})\s*-\s*(\d{4})',    # "2020-2022"
            r'(\d{4})\s*-\s*(?:present|now|aujourd\'hui|actuel)',  # "2020-present"
        ]
        
        current_year = 2025  # Update as needed or use datetime
        
        for exp in self.experience:
            exp_lower = exp.lower()
            
            # Try to find explicit year mentions
            for pattern in year_patterns[:1]:
                matches = re.findall(pattern, exp_lower)
                if matches:
                    total_years += sum(int(m) for m in matches if m.isdigit())
            
            # Try to find year ranges
            range_matches = re.findall(year_patterns[1], exp)
            for start_year, end_year in range_matches:
                total_years += int(end_year) - int(start_year)
            
            # Try to find ongoing positions
            ongoing_matches = re.findall(year_patterns[2], exp_lower)
            for start_year in ongoing_matches:
                if start_year and start_year.isdigit():
                    total_years += current_year - int(start_year)
        
        return total_years if total_years > 0 else None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert CV to dictionary representation."""
        return {
            "name": self.name,
            "contact": self.contact,
            "skills": self.skills,
            "education": self.education,
            "experience": self.experience,
            "academic_projects": self.academic_projects,
            "diplomas": self.diplomas,
            "metadata": self.metadata,
        }


@dataclass
class JobDescription:
    """Represents a job offer/description with extracted requirements."""
    
    raw_text: str
    job_title: Optional[str] = None
    company_name: Optional[str] = None
    location: Optional[str] = None
    job_type: Optional[str] = None
    responsibilities: List[str] = field(default_factory=list)
    skills: List[str] = field(default_factory=list)
    experience_level: Optional[str] = None
    education_requirements: List[str] = field(default_factory=list)
    embedding: Optional[NDArray[np.float64]] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def normalize_skills(self) -> List[str]:
        """
        Normalize skills to lowercase and remove duplicates.
        
        Returns:
            List of normalized, unique skills.
        """
        if not self.skills:
            return []
        return list(set([s.lower().strip() for s in self.skills if s and s.strip()]))
    
    def get_required_years_of_experience(self) -> Optional[int]:
        """
        Extract required years of experience from experience_level field.
        
        Returns:
            Required years of experience or None if cannot be determined.
        """
        if not self.experience_level:
            return None
        
        exp_lower = self.experience_level.lower()
        
        # Common patterns
        patterns = [
            r'(\d+)\+?\s*(?:years?|ans?)',  # "3+ years", "5 ans"
            r'(\d+)\s*-\s*(\d+)\s*(?:years?|ans?)',  # "3-5 years"
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, exp_lower)
            if matches:
                if isinstance(matches[0], tuple):
                    # Range found, take minimum
                    return int(matches[0][0])
                else:
                    return int(matches[0])
        
        # Check for level keywords
        if any(keyword in exp_lower for keyword in ['junior', 'débutant', 'entry']):
            return 0
        elif any(keyword in exp_lower for keyword in ['mid', 'intermediate', 'confirmé']):
            return 3
        elif any(keyword in exp_lower for keyword in ['senior', 'expert', 'lead']):
            return 7
        
        return None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert JobDescription to dictionary representation."""
        return {
            "job_title": self.job_title,
            "company_name": self.company_name,
            "location": self.location,
            "job_type": self.job_type,
            "responsibilities": self.responsibilities,
            "skills": self.skills,
            "experience_level": self.experience_level,
            "education_requirements": self.education_requirements,
            "metadata": self.metadata,
        }


@dataclass
class MatchResult:
    """Represents the result of matching a CV against a Job Description."""
    
    cv: CV
    job_description: JobDescription
    total_score: float
    semantic_score: float
    skill_match_ratio: float
    matched_skills: List[str]
    missing_skills: List[str]
    experience_score: float = 0.5
    education_score: float = 0.5
    strengths: List[str] = field(default_factory=list)
    weaknesses: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    match_details: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert MatchResult to dictionary representation."""
        return {
            "cv_name": self.cv.name,
            "job_title": self.job_description.job_title,
            "total_score": self.total_score,
            "semantic_score": self.semantic_score,
            "skill_match_ratio": self.skill_match_ratio,
            "experience_score": self.experience_score,
            "education_score": self.education_score,
            "matched_skills": self.matched_skills,
            "missing_skills": self.missing_skills,
            "strengths": self.strengths,
            "weaknesses": self.weaknesses,
            "recommendations": self.recommendations,
            "match_details": self.match_details,
        }
    
    def get_grade(self) -> str:
        """
        Get letter grade for the match.
        
        Returns:
            Letter grade (A+ to F).
        """
        if self.total_score >= 90:
            return "A+"
        elif self.total_score >= 85:
            return "A"
        elif self.total_score >= 80:
            return "A-"
        elif self.total_score >= 75:
            return "B+"
        elif self.total_score >= 70:
            return "B"
        elif self.total_score >= 65:
            return "B-"
        elif self.total_score >= 60:
            return "C+"
        elif self.total_score >= 55:
            return "C"
        elif self.total_score >= 50:
            return "C-"
        else:
            return "F"
    
    def get_match_quality(self) -> str:
        """
        Get qualitative assessment of match.
        
        Returns:
            Match quality description.
        """
        if self.total_score >= 85:
            return "Excellent Match"
        elif self.total_score >= 70:
            return "Good Match"
        elif self.total_score >= 55:
            return "Fair Match"
        else:
            return "Poor Match"
