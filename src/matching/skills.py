"""
Advanced skill matching with multiple strategies.

This module provides sophisticated skill matching using:
- Synonym/abbreviation mapping
- Fuzzy string matching
- Semantic similarity via embeddings
"""
from typing import List, Tuple, Dict, Set
from fuzzywuzzy import process, fuzz
import numpy as np

from src.utils.embeddings import generate_embeddings
from config import Config


class SkillMatcher:
    """Advanced skill matching with multiple strategies."""
    
    # Skill synonyms and abbreviations
    # Format: canonical_name -> [list of variants]
    SKILL_SYNONYMS = {
        "javascript": ["js", "ecmascript", "javascript", "java script"],
        "python": ["py", "python", "python3", "python 3"],
        "machine learning": ["ml", "machine learning", "mlearning", "machine-learning"],
        "artificial intelligence": ["ai", "artificial intelligence", "a.i."],
        "react": ["react.js", "reactjs", "react"],
        "node": ["node.js", "nodejs", "node"],
        "angular": ["angular.js", "angularjs", "angular"],
        "vue": ["vue.js", "vuejs", "vue"],
        "typescript": ["ts", "typescript", "type script"],
        "postgresql": ["postgres", "postgresql", "psql"],
        "mongodb": ["mongo", "mongodb", "mongo db"],
        "sql": ["sql", "structured query language"],
        "nosql": ["nosql", "no-sql", "no sql"],
        "c++": ["cpp", "c++", "c plus plus"],
        "c#": ["csharp", "c#", "c sharp"],
        "natural language processing": ["nlp", "natural language processing", "text analytics"],
        "deep learning": ["dl", "deep learning", "neural networks"],
        "devops": ["devops", "dev ops", "development operations"],
        "ci/cd": ["cicd", "ci/cd", "continuous integration"],
        "docker": ["docker", "containerization"],
        "kubernetes": ["k8s", "kubernetes", "kube"],
        "aws": ["aws", "amazon web services"],
        "azure": ["azure", "microsoft azure"],
        "gcp": ["gcp", "google cloud platform", "google cloud"],
    }
    
    def __init__(self, fuzzy_threshold: int = None, semantic_threshold: float = None):
        """
        Initialize the SkillMatcher.
        
        Args:
            fuzzy_threshold: Minimum fuzzy match score (0-100). Defaults to config value.
            semantic_threshold: Minimum semantic similarity (0-1). Defaults to config value.
        """
        self.fuzzy_threshold = fuzzy_threshold or Config.FUZZY_MATCH_THRESHOLD
        self.semantic_threshold = semantic_threshold or Config.SEMANTIC_SKILL_THRESHOLD
        self._build_synonym_map()
    
    def _build_synonym_map(self):
        """Create reverse lookup for synonyms."""
        self.synonym_map = {}
        for canonical, variants in self.SKILL_SYNONYMS.items():
            for variant in variants:
                self.synonym_map[variant.lower()] = canonical
    
    def normalize_skill(self, skill: str) -> str:
        """
        Normalize a skill using synonym map.
        
        Args:
            skill: Raw skill string.
            
        Returns:
            Normalized skill name.
        """
        skill_lower = skill.lower().strip()
        return self.synonym_map.get(skill_lower, skill_lower)
    
    def match_skills(
        self, 
        cv_skills: List[str], 
        jd_skills: List[str]
    ) -> Tuple[List[str], List[str], Dict[str, Dict]]:
        """
        Match skills using multiple strategies:
        1. Exact match (after normalization)
        2. Fuzzy string matching
        3. Semantic similarity via embeddings
        
        Args:
            cv_skills: List of skills from the CV.
            jd_skills: List of required skills from the job description.
            
        Returns:
            Tuple of (matched_skills, missing_skills, match_details)
            - matched_skills: Skills from JD that were found in CV
            - missing_skills: Skills from JD not found in CV
            - match_details: Dict mapping each JD skill to match info
        """
        if not jd_skills:
            return [], [], {}
        
        if not cv_skills:
            return [], jd_skills, {}
        
        # Normalize all skills
        cv_normalized = [self.normalize_skill(s) for s in cv_skills]
        jd_normalized = [self.normalize_skill(s) for s in jd_skills]
        
        matched_skills = []
        missing_skills = []
        match_details = {}
        
        for jd_skill_orig, jd_skill_norm in zip(jd_skills, jd_normalized):
            match_found = False
            match_method = None
            match_score = 0.0
            matched_cv_skill = None
            
            # Strategy 1: Exact match (after normalization)
            if jd_skill_norm in cv_normalized:
                match_found = True
                match_method = "exact"
                match_score = 1.0
                idx = cv_normalized.index(jd_skill_norm)
                matched_cv_skill = cv_skills[idx]
            
            # Strategy 2: Fuzzy matching
            if not match_found:
                best_match = process.extractOne(
                    jd_skill_norm, 
                    cv_normalized, 
                    scorer=fuzz.token_sort_ratio,
                    score_cutoff=self.fuzzy_threshold
                )
                if best_match:
                    match_found = True
                    match_method = "fuzzy"
                    match_score = best_match[1] / 100.0
                    idx = cv_normalized.index(best_match[0])
                    matched_cv_skill = cv_skills[idx]
            
            # Strategy 3: Semantic similarity
            if not match_found and len(cv_skills) > 0:
                try:
                    jd_emb = generate_embeddings([jd_skill_orig])[0]
                    cv_embs = generate_embeddings(cv_skills)
                    
                    # Calculate cosine similarities
                    similarities = np.dot(cv_embs, jd_emb) / (
                        np.linalg.norm(cv_embs, axis=1) * np.linalg.norm(jd_emb) + 1e-8
                    )
                    max_sim_idx = np.argmax(similarities)
                    max_sim = similarities[max_sim_idx]
                    
                    if max_sim >= self.semantic_threshold:
                        match_found = True
                        match_method = "semantic"
                        match_score = float(max_sim)
                        matched_cv_skill = cv_skills[max_sim_idx]
                except Exception as e:
                    # If embedding fails, skip semantic matching
                    print(f"Warning: Semantic matching failed for '{jd_skill_orig}': {e}")
            
            if match_found:
                matched_skills.append(jd_skill_orig)
                match_details[jd_skill_orig] = {
                    "method": match_method,
                    "score": round(match_score, 3),
                    "matched_cv_skill": matched_cv_skill
                }
            else:
                missing_skills.append(jd_skill_orig)
                match_details[jd_skill_orig] = {
                    "method": "none",
                    "score": 0.0,
                    "matched_cv_skill": None
                }
        
        return matched_skills, missing_skills, match_details
    
    def get_skill_categories(self, skills: List[str]) -> Dict[str, List[str]]:
        """
        Categorize skills into broad categories.
        
        Args:
            skills: List of skills to categorize.
            
        Returns:
            Dictionary mapping category to list of skills.
        """
        categories = {
            "Programming Languages": [],
            "Frameworks & Libraries": [],
            "Databases": [],
            "Cloud & DevOps": [],
            "AI & Data Science": [],
            "Other": []
        }
        
        programming_langs = {"python", "javascript", "java", "c++", "c#", "typescript", "go", "rust", "php", "ruby"}
        frameworks = {"react", "angular", "vue", "node", "django", "flask", "spring", "express"}
        databases = {"sql", "postgresql", "mongodb", "mysql", "redis", "cassandra"}
        cloud_devops = {"aws", "azure", "gcp", "docker", "kubernetes", "ci/cd", "devops", "terraform"}
        ai_ds = {"machine learning", "deep learning", "nlp", "artificial intelligence", "tensorflow", "pytorch"}
        
        for skill in skills:
            skill_norm = self.normalize_skill(skill)
            
            if skill_norm in programming_langs:
                categories["Programming Languages"].append(skill)
            elif skill_norm in frameworks:
                categories["Frameworks & Libraries"].append(skill)
            elif skill_norm in databases:
                categories["Databases"].append(skill)
            elif skill_norm in cloud_devops:
                categories["Cloud & DevOps"].append(skill)
            elif skill_norm in ai_ds:
                categories["AI & Data Science"].append(skill)
            else:
                categories["Other"].append(skill)
        
        # Remove empty categories
        return {k: v for k, v in categories.items() if v}
