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

def answer_question(question, rag_pipeline):
    """
    Answers a question using the RAG pipeline.

    Args:
        question (str): The question to answer.
        rag_pipeline (RAGPipeline): The RAG pipeline instance.

    Returns:
        str: The generated answer.
    """
    if not genai_model:
        return "Q&A is disabled because the Gemini model is not configured."

    # Retrieve relevant context from the RAG pipeline
    retrieved_results = rag_pipeline.query(question)
    context = "\n".join(retrieved_results['documents'][0])

    prompt = f"""
    You are a helpful assistant. Answer the following question based only on the provided context.
    If the answer is not in the context, say 'The answer is not available in the provided context.'

    **Question:**
    {question}

    **Context:**
    {context}
    """

    try:
        response = genai_model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"An error occurred during answer generation: {e}"
