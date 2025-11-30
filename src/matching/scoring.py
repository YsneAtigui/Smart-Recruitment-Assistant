from sklearn.metrics.pairwise import cosine_similarity
from fuzzywuzzy import process
import numpy as np

def calculate_fit_score(cv_embedding, job_offer_embedding):
    """
    Calculates the semantic fit score between a CV and a job offer using cosine similarity.

    Args:
        cv_embedding (numpy.ndarray): The embedding of the CV.
        job_offer_embedding (numpy.ndarray): The embedding of the job offer.

    Returns:
        float: The fit score (0.0 to 1.0).
    """
    # Ensure embeddings are 2D arrays for cosine_similarity
    # Reshape 1D arrays to (1, -1) and keep 2D arrays as is
    if cv_embedding.ndim == 1:
        cv_embedding = cv_embedding.reshape(1, -1)
    if job_offer_embedding.ndim == 1:
        job_offer_embedding = job_offer_embedding.reshape(1, -1)

    fit_score = cosine_similarity(cv_embedding, job_offer_embedding)[0][0]
    return float(fit_score)

def skill_gap_analysis(cv_skills, job_offer_skills, score_cutoff=80):
    """
    Performs a skill gap analysis between a CV and a job offer.

    Args:
        cv_skills (list[str]): A list of skills from the CV.
        job_offer_skills (list[str]): A list of skills from the job offer.
        score_cutoff (int): The minimum similarity score to consider a skill as a match.

    Returns:
        tuple[list[str], list[str]]: A tuple containing two lists:
                                     - missing_skills: Skills in job offer but not in CV.
                                     - matched_skills: Skills in job offer that are also in CV.
    """
    missing_skills = []
    matched_skills = []
    
    # Normalize to lower case for better matching if needed, but fuzzywuzzy handles it well.
    # We iterate over job skills to see if they exist in CV.
    for skill in job_offer_skills:
        # extractOne returns (match, score) or None
        best_match = process.extractOne(skill, cv_skills, score_cutoff=score_cutoff)
        if best_match:
            matched_skills.append(skill)
        else:
            missing_skills.append(skill)
            
    return missing_skills, matched_skills

def calculate_hybrid_score(cv_embedding, job_embedding, cv_skills, job_skills, semantic_weight=0.7, skill_weight=0.3):
    """
    Calculates a hybrid fit score combining semantic similarity and skill matching.

    Formula:
        Final Score = (Semantic Score * semantic_weight) + (Skill Match Ratio * skill_weight)

    Args:
        cv_embedding (numpy.ndarray): Embedding of the CV.
        job_embedding (numpy.ndarray): Embedding of the Job Description.
        cv_skills (list[str]): List of skills extracted from CV.
        job_skills (list[str]): List of skills extracted from Job Description.
        semantic_weight (float): Weight for the semantic cosine similarity (default 0.7).
        skill_weight (float): Weight for the skill match ratio (default 0.3).

    Returns:
        dict: A dictionary containing:
            - "total_score": The final hybrid score (0-100).
            - "semantic_score": The raw cosine similarity (0-1).
            - "skill_match_ratio": The ratio of matched skills (0-1).
            - "matched_skills": List of matched skills.
            - "missing_skills": List of missing skills.
    """
    # 1. Calculate Semantic Score
    semantic_score = calculate_fit_score(cv_embedding, job_embedding)
    
    # 2. Calculate Skill Match Score
    if not job_skills:
        # If no skills are required in JD, we assume 100% skill match or ignore it?
        # Let's assume 1.0 to avoid penalizing for empty requirements, 
        # or 0.0 if strict. Let's go with 0.0 if empty to be safe, or handle edge case.
        # Better: If no skills required, rely 100% on semantic score.
        skill_ratio = 0.0
        actual_skill_weight = 0.0
        actual_semantic_weight = 1.0
    else:
        missing, matched = skill_gap_analysis(cv_skills, job_skills)
        skill_ratio = len(matched) / len(job_skills)
        actual_skill_weight = skill_weight
        actual_semantic_weight = semantic_weight

    # 3. Combine Scores
    # Normalize weights to sum to 1 if needed, but assuming user provides valid weights.
    # If job_skills was empty, we effectively use 100% semantic.
    
    weighted_score = (semantic_score * actual_semantic_weight) + (skill_ratio * actual_skill_weight)
    
    return {
        "total_score": round(weighted_score * 100, 2), # Return as percentage
        "semantic_score": round(semantic_score, 4),
        "skill_match_ratio": round(skill_ratio, 4),
        "matched_skills": matched if job_skills else [],
        "missing_skills": missing if job_skills else []
    }
