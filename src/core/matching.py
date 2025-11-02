from sklearn.metrics.pairwise import cosine_similarity
from fuzzywuzzy import process

def calculate_fit_score(cv_embedding, job_offer_embedding):
    """
    Calculates the fit score between a CV and a job offer using cosine similarity.

    Args:
        cv_embedding (numpy.ndarray): The embedding of the CV.
        job_offer_embedding (numpy.ndarray): The embedding of the job offer.

    Returns:
        float: The fit score, which is the cosine similarity between the two embeddings.
    """
    # The embeddings are 2D arrays, so we need to reshape them to be 1D
    if cv_embedding.ndim > 1:
        cv_embedding = cv_embedding.reshape(1, -1)
    if job_offer_embedding.ndim > 1:
        job_offer_embedding = job_offer_embedding.reshape(1, -1)

    fit_score = cosine_similarity(cv_embedding, job_offer_embedding)[0][0]
    return fit_score

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
    for skill in job_offer_skills:
        best_match = process.extractOne(skill, cv_skills, score_cutoff=score_cutoff)
        if best_match:
            matched_skills.append(skill)
        else:
            missing_skills.append(skill)
    return missing_skills, matched_skills
