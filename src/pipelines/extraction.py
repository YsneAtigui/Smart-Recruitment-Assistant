"""
This module provides functions to extract structured information from CVs and job descriptions.

Prerequisites:
- spaCy models must be downloaded before using this module.
  Run the following commands in your terminal:
  python -m spacy download en_core_web_sm
  python -m spacy download fr_core_news_sm
"""
import re
import spacy
import os
import json
from dotenv import load_dotenv
import google.generativeai as genai

# --- Model Configurations ---

# spaCy
# Load spaCy models.
nlp_en = spacy.load("en_core_web_sm")
nlp_fr = spacy.load("fr_core_news_sm")

# Gemini
load_dotenv()
try:
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY not found in .env file or environment variables.")
    genai.configure(api_key=api_key)
    genai_model = genai.GenerativeModel('gemini-2.5-flash')
except (ValueError, ImportError) as e:
    print(f"Warning: Gemini model could not be configured. Gemini-based functions will be disabled. Error: {e}")
    genai_model = None

# --- spaCy & Regex Based Extraction ---

def detect_language(text):
    """Detects if the text is primarily English or French."""
    # This is a very simplistic language detection.
    # A more robust method would be to use a library like langdetect.
    if any(word in text.lower() for word in ['experience', 'education', 'skills']):
        return 'en'
    if any(word in text.lower() for word in ['expérience', 'formation', 'compétences']):
        return 'fr'
    return 'en' # Default to English

def extract_name(text, nlp):
    """Extracts the name from the text using spaCy's NER."""
    doc = nlp(text)
    for ent in doc.ents:
        if ent.label_ == "PERSON":
            return ent.text
    # If no PERSON entity is found, take the first line if it's short.
    first_line = text.split('\n')[0].strip()
    if len(first_line.split()) < 4:
        return first_line
    return None

def extract_contact(text):
    """Extracts contact information (email and phone) from text using regex."""
    email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    phone_pattern = r'(\+\d{1,3}\s?)?\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}'

    emails = re.findall(email_pattern, text)
    phones = re.findall(phone_pattern, text)

    return {"emails": emails, "phones": phones}

def extract_section_content(text, section_keywords):
    """Extracts content from a specific section of the text."""
    
    start_pattern = r'(?i)^\s*(' + '|'.join(section_keywords) + r')\s*$'
    
    all_headers = [
        'skills', 'compétences', 'education', 'formation', 'experience', 'expérience',
        'projects', 'projets', 'publications', 'certifications', 'diplomas', 'diplômes',
        'awards', 'references', 'summary', 'profil', 'contact', 'personal details'
    ]
    end_pattern = r'(?i)^\s*(' + '|'.join(all_headers) + r')\s*$'

    lines = text.split('\n')
    content = []
    in_section = False

    for line in lines:
        is_start_header = re.match(start_pattern, line.strip())
        # Check if the current line is another section header
        is_another_header = re.match(end_pattern, line.strip())

        if is_start_header:
            in_section = True
            continue

        if in_section and is_another_header and not is_start_header:
            # We've reached a new section, so we stop.
            break
        
        if in_section and line.strip():
            content.append(line.strip())
            
    return "\n".join(content)


def extract_information_from_cv(cv_text):
    """
    Extracts structured information from the text of a CV.
    
    Args:
        cv_text (str): The raw text content of the CV.
        
    Returns:
        dict: A dictionary containing extracted information.
    """
    
    lang = detect_language(cv_text)
    nlp = nlp_fr if lang == 'fr' else nlp_en
    
    name = extract_name(cv_text, nlp)
    contact = extract_contact(cv_text)
    
    section_keywords = {
        "skills": ["Skills", "Compétences", "Technical Skills", "Savoir-faire"],
        "education": ["Education", "Formation", "Academic Background", "Parcours Académique"],
        "experience": ["Experience", "Expérience", "Professional Experience", "Expérience Professionnelle"],
        "projects": ["Projects", "Projets", "Academic Projects", "Projets Académiques"],
        "diplomas": ["Diplomas", "Diplômes", "Certifications"]
    }
    
    extracted_data = {
        "name": name,
        "contact": contact,
        "skills": extract_section_content(cv_text, section_keywords["skills"]),
        "education": extract_section_content(cv_text, section_keywords["education"]),
        "experience": extract_section_content(cv_text, section_keywords["experience"]),
        "academic_projects": extract_section_content(cv_text, section_keywords["projects"]),
        "diplomas": extract_section_content(cv_text, section_keywords["diplomas"]),
    }
    
    return extracted_data

def extract_information_from_job_description(job_text):
    """
    Extracts structured information from the text of a job description.
    """
    
    skills_keywords = ["skills", "requirements", "qualifications", "compétences", "exigences", "profil recherché", "what you'll need"]
    
    extracted_data = {
        "skills_and_requirements": extract_section_content(job_text, skills_keywords)
    }
    
    return extracted_data

# --- Gemini Based Extraction ---

def extract_information_from_cv_gemini(cv_text):
    """
    Extracts structured information from a CV using the Gemini LLM.

    Args:
        cv_text (str): The raw text content of the CV.

    Returns:
        dict: A dictionary containing extracted information, or None if an error occurs.
    """
    if not genai_model:
        print("Gemini model is not configured. Please check your API key.")
        return None

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
        
        return json.loads(cleaned_response)
    except Exception as e:
        print(f"An error occurred during Gemini extraction: {e}")
        print("--- Raw Gemini Response ---")
        print(response.text if 'response' in locals() else "No response received.")
        print("--------------------------")
        return None

def extract_information_from_jd_gemini(jd_text):
    """
    Extrait des informations structurées d'une fiche de poste (Job Description) 
    en utilisant le LLM Gemini.

    Args:
        jd_text (str): Le texte brut de la fiche de poste.

    Returns:
        dict: Un dictionnaire contenant les informations extraites, 
              ou None si une erreur survient.
    """
    if not genai_model:
        print("Le modèle Gemini n'est pas configuré. Veuillez vérifier votre clé API.")
        return None

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
        
        return json.loads(cleaned_response)
    except Exception as e:
        print(f"Une erreur est survenue lors de l'extraction Gemini : {e}")
        print("--- Réponse brute de Gemini ---")
        print(response.text if 'response' in locals() else "Pas de réponse reçue.")
        print("--------------------------")
        return None

