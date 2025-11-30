"""
AI module for Smart Recruitment Assistant.

This module provides AI-powered features including:
- Question answering (Q&A) with RAG
- CV and job description summarization
- RAG pipeline for document indexing and retrieval
"""

from src.ai.qa import answer_question
from src.ai.summarization import summarize_cv, summarize_jd, generate_strengths_and_weaknesses_summary
from src.ai.rag import RAGPipeline

__all__ = [
    'answer_question',
    'summarize_cv',
    'summarize_jd',
    'generate_strengths_and_weaknesses_summary',
    'RAGPipeline'
]
