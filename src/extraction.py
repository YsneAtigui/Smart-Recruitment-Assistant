"""
This module provides functions to extract structured information from CVs and job descriptions using Gemini API.

Prerequisites:
- GEMINI_API_KEY must be set in .env file or environment variables
"""
import re
import os
import json
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
    print(f"Error: Gemini model could not be configured. Error: {e}")
    genai_model = None

# --- Gemini Based Extraction ---

def extract_information_from_cv_gemini(cv_text):
    """
    Extracts structured information from a CV using the Gemini LLM.

    Args:
        cv_text (str): The raw text content of the CV.

    Returns:
        dict: A dictionary containing extracted information.
        
    Raises:
        RuntimeError: If Gemini model is not configured or extraction fails.
    """
    if not genai_model:
        raise RuntimeError(
            "Gemini API is not configured. Please set GEMINI_API_KEY in your .env file. "
            "Get your API key from https://makersuite.google.com/app/apikey"
        )

    prompt = f'''
    Vous êtes un expert en analyse (parsing) de CV et de résumés. Votre tâche est d'analyser le texte fourni et d'en extraire les informations clés dans un format JSON structuré.

    Veuillez extraire les champs suivants :
    - "name" : Le nom complet du candidat.
    - "contact" : Un objet contenant :
        - "email" : L'adresse e-mail du candidat (sous forme de chaîne de caractères).
        - "phone" : Le numéro de téléphone du candidat (sous forme de chaîne de caractères).
    - "education" : Une liste de chaînes de caractères, où chaque chaîne est une entrée de formation (par ex., "Master en Informatique, Université de Paris (2020 - 2022) (2 ans)").
    - "experience" : Une liste de chaînes de caractères, où chaque chaîne est une entrée d'expérience professionnelle.
    - "skills" : Une liste de chaînes de caractères, où chaque chaîne est une compétence.
    - "academic_projects" : Une liste de chaînes de caractères pour tout projet académique ou personnel mentionné.
    - "diplomas" : Une liste de chaînes de caractères pour tout diplôme ou certification mentionné.

    Règles :
    - La sortie entière doit être un unique objet JSON valide.
    - N'incluez aucun texte, explication ou formatage markdown comme ```json avant ou après l'objet JSON.
    - Si une section ou une information n'est pas trouvée, utilisez une liste vide `[]` pour les champs de type liste ou `null` pour les champs de type chaîne/objet.
    - Nettoyez le texte extrait pour supprimer les sauts de ligne ou la mise en forme inutiles à l'intérieur des chaînes de caractères.

    Voici le texte du CV à analyser :
    ---
    {cv_text}
    ---
    '''

    try:
        response = genai_model.generate_content(prompt)
        
        # Clean the response to get only the JSON part.
        # The model sometimes includes ```json markdown.
        cleaned_response = re.sub(r'```json\n(.*?)\n```', r'\1', response.text, flags=re.DOTALL)
        
        extracted_data = json.loads(cleaned_response)
        return extracted_data
    except json.JSONDecodeError as e:
        error_msg = f"Failed to parse JSON from Gemini response: {e}"
        if 'response' in locals():
            error_msg += f"\n--- Raw Response ---\n{response.text}\n-------------------"
        raise RuntimeError(error_msg)
    except Exception as e:
        error_msg = f"Gemini API error during CV extraction: {str(e)}"
        if 'response' in locals() and hasattr(response, 'text'):
            error_msg += f"\n--- Response Text ---\n{response.text}\n-------------------"
        raise RuntimeError(error_msg)

def extract_information_from_jd_gemini(jd_text):
    """
    Extrait des informations structurées d'une fiche de poste (Job Description) 
    en utilisant le LLM Gemini.

    Args:
        jd_text (str): Le texte brut de la fiche de poste.

    Returns:
        dict: Un dictionnaire contenant les informations extraites.
        
    Raises:
        RuntimeError: If Gemini model is not configured or extraction fails.
    """
    if not genai_model:
        raise RuntimeError(
            "Gemini API is not configured. Please set GEMINI_API_KEY in your .env file. "
            "Get your API key from https://makersuite.google.com/app/apikey"
        )

    prompt = f'''
    Vous êtes un expert en recrutement et un analyste de fiches de poste. Votre tâche est d'analyser le texte de l'offre d'emploi fournie et d'en extraire les informations clés dans un format JSON structuré.

    Veuillez extraire les champs suivants :
    - "job_title": Le titre exact du poste (par ex., "Développeur Full-Stack Senior").
    - "company_name": Le nom de l'entreprise qui recrute (si mentionné).
    - "location": Le lieu de travail (par ex., "Paris, France", "Télétravail complet", "Hybride (Lyon)").
    - "job_type": Le type de contrat (par ex., "CDI", "CDD", "Stage", "Freelance", "Temps partiel").
    - "responsibilities": Une liste de chaînes de caractères, où chaque chaîne est une responsabilité ou une mission clé.
    - "skills" : Une liste de chaînes de caractères, où chaque chaîne est une compétence.
    - "experience_level": Une description textuelle du niveau d'expérience requis (par ex., "Junior", "Senior", "3-5 ans d'expérience", "Débutant accepté").
    - "education_requirements": Une liste de chaînes pour les diplômes ou niveaux d'étude requis (par ex., "Bac +5 en informatique", "Diplôme d'ingénieur").

    Règles :
    - La sortie entière doit être un unique objet JSON valide.
    - N'incluez aucun texte, explication ou formatage markdown comme ```json avant ou après l'objet JSON.
    - Si une section ou une information n'est pas trouvée, utilisez une liste vide `[]` pour les champs de type liste ou `null` pour les champs de type chaîne/objet.
    - Nettoyez le texte extrait pour supprimer les sauts de ligne ou la mise en forme inutiles à l'intérieur des chaînes de caractères.

    Voici le texte de la fiche de poste à analyser :
    ---
    {jd_text}
    ---
    '''

    try:
        response = genai_model.generate_content(prompt)
        
        # Nettoie la réponse pour n'obtenir que le JSON.
        # Le modèle inclut parfois le markdown ```json.
        cleaned_response = re.sub(r'```json\n(.*?)\n```', r'\1', response.text, flags=re.DOTALL)
        
        extracted_data = json.loads(cleaned_response)
        return extracted_data
    except json.JSONDecodeError as e:
        error_msg = f"Failed to parse JSON from Gemini response: {e}"
        if 'response' in locals():
            error_msg += f"\n--- Raw Response ---\n{response.text}\n-------------------"
        raise RuntimeError(error_msg)
    except Exception as e:
        error_msg = f"Gemini API error during job description extraction: {str(e)}"
        if 'response' in locals() and hasattr(response, 'text'):
            error_msg += f"\n--- Response Text ---\n{response.text}\n-------------------"
        raise RuntimeError(error_msg)

