"""
Configuration settings for Smart Recruitment Assistant.
"""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Config:
    """Application configuration."""
    
    # ==================== API Keys ====================
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    
    # ==================== Model Configuration ====================
    # Embedding model for semantic similarity
    EMBEDDING_MODEL = "all-MiniLM-L6-v2"
    
    # Gemini LLM model
    GEMINI_MODEL = "gemini-2.5-flash"
    
    # ==================== Matching Configuration ====================
    # Default weights for hybrid scoring
    DEFAULT_SEMANTIC_WEIGHT = 0.35
    DEFAULT_SKILL_WEIGHT = 0.40
    DEFAULT_EXPERIENCE_WEIGHT = 0.15
    DEFAULT_EDUCATION_WEIGHT = 0.10
    
    # Skill matching thresholds
    FUZZY_MATCH_THRESHOLD = 80  # Minimum similarity score (0-100)
    SEMANTIC_SKILL_THRESHOLD = 0.75  # Minimum cosine similarity (0-1)
    
    # ==================== RAG Configuration ====================
    # ChromaDB settings
    CHROMA_PERSIST_DIR = "./chroma_db"
    CHROMA_COLLECTION_NAME = "cv_collection"
    
    # Text chunking parameters
    RAG_CHUNK_SIZE = 1000
    RAG_CHUNK_OVERLAP = 200
    RAG_TOP_K = 3  # Number of chunks to retrieve
    
    # ==================== Paths ====================
    DATA_DIR = "data"
    CV_DIR = os.path.join(DATA_DIR, "cvs")
    JD_DIR = os.path.join(DATA_DIR, "job_offers")
    OUTPUT_DIR = "output"
    
    
    # ==================== Document Processing ====================
    # OCR settings
    OCR_DPI = 250
    
    # Supported file formats
    SUPPORTED_FORMATS = [".pdf", ".docx", ".txt", ".html"]
    
    # Language detection
    DEFAULT_LANGUAGE = "en"
    
    @classmethod
    def validate(cls):
        """Validate configuration settings."""
        errors = []
        
        if not cls.GEMINI_API_KEY:
            errors.append("GEMINI_API_KEY is not set in environment variables")
        
        # Validate weights sum to 1.0
        total_weight = (
            cls.DEFAULT_SEMANTIC_WEIGHT +
            cls.DEFAULT_SKILL_WEIGHT +
            cls.DEFAULT_EXPERIENCE_WEIGHT +
            cls.DEFAULT_EDUCATION_WEIGHT
        )
        if abs(total_weight - 1.0) > 0.01:
            errors.append(f"Matching weights sum to {total_weight}, should be 1.0")
        
        if errors:
            raise ValueError("Configuration errors:\n" + "\n".join(f"  - {e}" for e in errors))
        
        return True
    
    @classmethod
    def get_matching_weights(cls):
        """Get matching weights as a dictionary."""
        return {
            "semantic": cls.DEFAULT_SEMANTIC_WEIGHT,
            "skills": cls.DEFAULT_SKILL_WEIGHT,
            "experience": cls.DEFAULT_EXPERIENCE_WEIGHT,
            "education": cls.DEFAULT_EDUCATION_WEIGHT,
        }
