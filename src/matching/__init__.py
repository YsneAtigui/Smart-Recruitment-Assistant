"""
Matching module for Smart Recruitment Assistant.

This module provides matching functionality including:
- Advanced CV-to-JD matching
- Skill matching
- Scoring calculations
"""

from src.matching.matcher import AdvancedMatcher
from src.matching.skills import SkillMatcher
from src.matching.scoring import calculate_fit_score

__all__ = ['AdvancedMatcher', 'SkillMatcher', 'calculate_fit_score']
