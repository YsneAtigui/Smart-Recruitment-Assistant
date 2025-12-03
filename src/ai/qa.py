import os
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
    print(f"Warning: Gemini model could not be configured. Q&A functions will be disabled. Error: {e}")
    genai_model = None

def answer_question(question, rag_pipeline, persona="recruiter"):
    """
    Answers a question using the RAG pipeline.

    Args:
        question (str): The question to answer.
        rag_pipeline (RAGPipeline): The RAG pipeline instance.
        persona (str): The persona to adopt ('recruiter' or 'candidate').

    Returns:
        str: The generated answer.
    """
    if not genai_model:
        return "Q&A is disabled because the Gemini model is not configured."

    # Retrieve relevant context from the RAG pipeline
    retrieved_results = rag_pipeline.query(question)
    context = "\n".join(retrieved_results['documents'][0])

    if persona == "candidate":
        prompt = f"""
        You are an Expert Career Coach and Recruitment Assistant. 
        Your goal is to help candidates improve their profiles and recruiters evaluate candidates.
        
        **Context:**
        {context}
        
        **Question:**
        {question}
        
        **Instructions:**
        1. Answer the question based on the provided context (CV/Job Description).
        2. If the user asks for advice (e.g., "How to improve?", "What is missing?"), analyze the context to identify gaps or areas for improvement and provide actionable recommendations.
        3. You can use your general knowledge about recruitment standards to give advice, but always ground it in the specific details from the context.
        4. Be encouraging, professional, and specific.
        5. If the question is completely unrelated to the candidate's profile or recruitment, politely say you can only assist with career and recruitment topics.
        """
    else:  # Default to recruiter
        prompt = f"""
        You are an Expert Recruitment Assistant. Your goal is to help recruiters evaluate candidates and make informed decisions.
        
        **Context:**
        The following text contains information from one or more Candidate CVs and potentially a Job Description.
        {context}
        
        **Question:**
        {question}
        
        **Instructions:**
        1. Answer the question based ONLY on the provided context.
        2. The context may contain details for MULTIPLE candidates. Identify them by name.
        3. If the user asks about a specific candidate (e.g., "Amine"), look for their details in the context.
        4. If the user asks to compare candidates, use the details provided for each to make a comparison.
        5. If the answer is not in the context, say 'The answer is not available in the provided context.'
        """

    try:
        response = genai_model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"An error occurred during answer generation: {e}"
