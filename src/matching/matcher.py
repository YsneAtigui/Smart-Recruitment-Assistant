"""
Advanced matching system with multi-dimensional scoring.

This module provides sophisticated matching between CVs and Job Descriptions
using multiple dimensions: semantic similarity, skills, experience, and education.
"""
from typing import Dict, List, Optional
import numpy as np

from src.models import CV, JobDescription, MatchResult
from src.matching.skills import SkillMatcher
from src.matching.scoring import calculate_fit_score
from config import Config


class AdvancedMatcher:
    """Advanced matching system with multiple dimensions."""
    
    def __init__(self, weights: Optional[Dict[str, float]] = None):
        """
        Initialize the AdvancedMatcher.
        
        Args:
            weights: Custom weights for different matching dimensions.
                     If None, uses default weights from config.
        """
        self.skill_matcher = SkillMatcher()
        self.weights = weights or Config.get_matching_weights()
        
        # Validate weights
        total = sum(self.weights.values())
        if abs(total - 1.0) > 0.01:
            raise ValueError(f"Weights must sum to 1.0, got {total}")
    
    def match(self, cv: CV, jd: JobDescription) -> MatchResult:
        """
        Perform multi-dimensional matching.
        
        Dimensions:
        - Semantic similarity (whole document embeddings)
        - Skill matching (with advanced fuzzy + semantic)
        - Experience level matching
        - Education matching
        
        Args:
            cv: Candidate's CV entity.
            jd: Job Description entity.
            
        Returns:
            MatchResult with comprehensive scoring and analysis.
        """
        # 1. Semantic similarity
        semantic_score = self._calculate_semantic_score(cv, jd)
        
        # 2. Advanced skill matching
        matched_skills, missing_skills, match_details = self.skill_matcher.match_skills(
            cv.normalize_skills(), jd.normalize_skills()
        )
        skill_ratio = len(matched_skills) / len(jd.skills) if jd.skills else 0.0
        
        # 3. Experience matching
        experience_score = self._match_experience(cv, jd)
        
        # 4. Education matching
        education_score = self._match_education(cv, jd)
        
        # Calculate weighted total
        total_score = (
            semantic_score * self.weights["semantic"] +
            skill_ratio * self.weights["skills"] +
            experience_score * self.weights["experience"] +
            education_score * self.weights["education"]
        ) * 100
        
        # Generate strengths, weaknesses, and recommendations
        strengths = self._generate_strengths(
            matched_skills, semantic_score, experience_score, education_score
        )
        weaknesses = self._generate_weaknesses(
            missing_skills, experience_score, education_score
        )
        recommendations = self._generate_recommendations(
            matched_skills, missing_skills, experience_score, education_score
        )
        
        return MatchResult(
            cv=cv,
            job_description=jd,
            total_score=round(total_score, 2),
            semantic_score=round(semantic_score, 4),
            skill_match_ratio=round(skill_ratio, 4),
            matched_skills=matched_skills,
            missing_skills=missing_skills,
            experience_score=round(experience_score, 4),
            education_score=round(education_score, 4),
            strengths=strengths,
            weaknesses=weaknesses,
            recommendations=recommendations,
            match_details=match_details
        )
    
    def _calculate_semantic_score(self, cv: CV, jd: JobDescription) -> float:
        """Calculate semantic similarity score."""
        if cv.embedding is None or jd.embedding is None:
            return 0.0
        
        return calculate_fit_score(cv.embedding, jd.embedding)
    
    def _match_experience(self, cv: CV, jd: JobDescription) -> float:
        """
        Match experience levels (0.0 to 1.0).
        
        Compares candidate's years of experience against job requirements.
        """
        cv_years = cv.get_years_of_experience()
        jd_years = jd.get_required_years_of_experience()
        
        # If we can't determine either, return neutral score
        if cv_years is None or jd_years is None:
            return 0.5
        
        # Perfect match
        if cv_years >= jd_years:
            # Give bonus for meeting requirements
            if cv_years == jd_years:
                return 1.0
            # Slight penalty for being overqualified (max 10% penalty)
            over_qualified_penalty = min(0.1, (cv_years - jd_years) * 0.02)
            return max(0.9, 1.0 - over_qualified_penalty)
        else:
            # Under-qualified: exponential decay
            gap = jd_years - cv_years
            # More forgiving for junior positions
            if jd_years <= 2:
                return max(0.3, 1.0 - (gap * 0.2))
            else:
                return max(0.1, 1.0 - (gap * 0.15))
    
    def _match_education(self, cv: CV, jd: JobDescription) -> float:
        """
        Match education requirements (0.0 to 1.0).
        
        Uses keyword matching on education and diploma fields.
        """
        # If no education requirements, return perfect score
        if not jd.education_requirements:
            return 1.0
        
        # If CV has no education info, return low score
        if not cv.education and not cv.diplomas:
            return 0.3
        
        # Combine CV education fields
        cv_edu_text = " ".join(cv.education + cv.diplomas).lower()
        
        # Check for common education levels
        education_keywords = {
            "phd": ["phd", "doctorate", "doctoral", "doctorat"],
            "master": ["master", "msc", "m.sc", "masters", "mastère"],
            "bachelor": ["bachelor", "bsc", "b.sc", "licence", "undergraduate"],
            "associate": ["associate", "dut", "bts"],
        }
        
        # Get required level from JD
        jd_edu_text = " ".join(jd.education_requirements).lower()
        required_level = None
        
        for level, keywords in education_keywords.items():
            if any(kw in jd_edu_text for kw in keywords):
                required_level = level
                break
        
        # If we can't determine level, use fuzzy match
        if not required_level:
            # Check if any JD education requirement appears in CV
            matches = sum(
                1 for req in jd.education_requirements 
                if req.lower() in cv_edu_text
            )
            return min(1.0, matches / len(jd.education_requirements))
        
        # Check if CV meets required level
        cv_has_level = {}
        for level, keywords in education_keywords.items():
            cv_has_level[level] = any(kw in cv_edu_text for kw in keywords)
        
        # Education hierarchy
        hierarchy = ["associate", "bachelor", "master", "phd"]
        
        if required_level in hierarchy:
            required_idx = hierarchy.index(required_level)
            
            # Check if candidate meets or exceeds requirement
            for i in range(required_idx, len(hierarchy)):
                if cv_has_level.get(hierarchy[i], False):
                    return 1.0
            
            # Check if candidate is one level below
            if required_idx > 0 and cv_has_level.get(hierarchy[required_idx - 1], False):
                return 0.7
            
            # Otherwise, lower score
            return 0.4
        
        return 0.5
    
    def _generate_strengths(
        self, 
        matched_skills: List[str],
        semantic_score: float,
        experience_score: float,
        education_score: float
    ) -> List[str]:
        """Generate list of candidate's strengths."""
        strengths = []
        
        if len(matched_skills) >= 5:
            strengths.append(
                f"Strong skill alignment with {len(matched_skills)} matching required skills"
            )
        elif len(matched_skills) >= 3:
            strengths.append(
                f"Good skill match with {len(matched_skills)} key skills aligned"
            )
        
        if semantic_score >= 0.8:
            strengths.append(
                "Excellent semantic match - profile closely aligns with job description"
            )
        elif semantic_score >= 0.65:
            strengths.append(
                "Good overall fit based on profile content"
            )
        
        if experience_score >= 0.85:
            strengths.append(
                "Experience level highly suitable for this role"
            )
        
        if education_score >= 0.9:
            strengths.append(
                "Educational background exceeds or meets requirements"
            )
        
        return strengths
    
    def _generate_weaknesses(
        self,
        missing_skills: List[str],
        experience_score: float,
        education_score: float
    ) -> List[str]:
        """Generate list of candidate's weaknesses."""
        weaknesses = []
        
        if len(missing_skills) >= 5:
            weaknesses.append(
                f"Significant skill gap: {len(missing_skills)} required skills not found in CV"
            )
        elif len(missing_skills) >= 3:
            weaknesses.append(
                f"Notable skill gap: Missing {len(missing_skills)} required skills"
            )
        
        if experience_score < 0.5:
            weaknesses.append(
                "Experience level may not fully meet job requirements"
            )
        
        if education_score < 0.5:
            weaknesses.append(
                "Educational background may not meet stated requirements"
            )
        
        return weaknesses
    
    def _generate_recommendations(
        self,
        matched_skills: List[str],
        missing_skills: List[str],
        experience_score: float,
        education_score: float
    ) -> List[str]:
        """Generate actionable recommendations."""
        recs = []
        
        if missing_skills:
            # Show top 5 missing skills
            top_missing = missing_skills[:5]
            recs.append(
                f"Consider acquiring these key skills: {', '.join(top_missing)}"
            )
        
        if experience_score < 0.5:
            recs.append(
                "Gain more relevant work experience in this domain through projects or internships"
            )
        
        if education_score < 0.5:
            recs.append(
                "Consider additional certifications or formal education to meet requirements"
            )
        
        if len(matched_skills) >= 3 and len(missing_skills) <= 2:
            recs.append(
                "Strong candidate - highlight matching skills prominently in interview"
            )
        
        return recs
