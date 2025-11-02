import os
import re
from dotenv import load_dotenv
import google.generativeai as genai

# --- Gemini Configuration ---
load_dotenv()
try:
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY not found in .env file or environment variables.")
    genai.configure(api_key=api_key)
    genai_model = genai.GenerativeModel('gemini-2.5-flash')
except (ValueError, ImportError) as e:
    print(f"Warning: Gemini model could not be configured. Summarization functions will be disabled. Error: {e}")
    genai_model = None

def summarize_cv(cv_text):
    """
    Generates a summary for a given CV text using the Gemini model.

    Args:
        cv_text (str): The text of the CV to summarize.

    Returns:
        str: The generated summary, or an error message if summarization fails.
    """
    if not genai_model:
        return "Summarization is disabled because the Gemini model is not configured."

    prompt_instruction = "Résumez ce CV en quelques phrases, en mettant en évidence l'expérience et les compétences clés du candidat."
    prompt = f"{prompt_instruction}\n\n---\n{cv_text}\n---"

    try:
        response = genai_model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"An error occurred during CV summarization: {e}"

def summarize_jd(jd_text):
    """
    Generates a summary for a given job description text using the Gemini model.

    Args:
        jd_text (str): The text of the job description to summarize.

    Returns:
        str: The generated summary, or an error message if summarization fails.
    """
    if not genai_model:
        return "Summarization is disabled because the Gemini model is not configured."

    prompt_instruction = "Résumez cette description de poste en quelques phrases, en soulignant les principales responsabilités et les qualifications requises."
    prompt = f"{prompt_instruction}\n\n---\n{jd_text}\n---"

    try:
        response = genai_model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"An error occurred during job description summarization: {e}"

def generate_strengths_and_weaknesses_summary(cv_text, job_offer_text, matched_skills, missing_skills):
    """
    Generates a summary of a candidate's strengths and weaknesses for a specific role.

    Args:
        cv_text (str): The text of the CV.
        job_offer_text (str): The text of the job offer.
        matched_skills (list[str]): A list of skills that match the job offer.
        missing_skills (list[str]): A list of skills that are missing from the CV.

    Returns:
        str: A summary of the candidate's strengths and weaknesses.
    """
    if not genai_model:
        return "Summarization is disabled because the Gemini model is not configured."

    prompt = f"""
    En tant que recruteur expert, analysez le CV et l'offre d'emploi fournis afin de dresser un résumé des points forts et des points faibles du candidat pour ce poste spécifique.

    **Job Offer:**
    {job_offer_text}

    **Candidate's CV:**
    {cv_text}

    **Analysis:**
    - Matched Skills: {', '.join(matched_skills)}
    - Missing Skills: {', '.join(missing_skills)}

    À partir de ces informations, veuillez fournir un résumé concis mettant en évidence:

1. **Points forts :** En quoi le candidat correspond au poste, en vous concentrant sur son expérience et ses compétences requises.
2. **Points faibles :** Quelles compétences ou expériences le candidat ne possède pas pour ce poste, en vous basant sur les compétences manquantes.
    """

    try:
        response = genai_model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"An error occurred during summarization: {e}"
