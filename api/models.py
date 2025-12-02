"""
Database models for storing candidate and job description data
"""
from sqlalchemy import Column, Integer, String, Float, Text, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from api.database import Base

class Candidate(Base):
    __tablename__ = "candidates"
    
    # Primary key
    id = Column(Integer, primary_key=True, index=True)
    
    # Basic information
    candidate_id = Column(String, unique=True, index=True)  # UUID from frontend
    name = Column(String, nullable=False, index=True)
    email = Column(String, index=True)
    role = Column(String)
    experience_years = Column(Integer)
    
    # Scores
    match_score = Column(Float)
    grade = Column(String)
    semantic_score = Column(Float)
    skills_score = Column(Float)
    experience_score = Column(Float)
    education_score = Column(Float)
    
    # Skills (stored as JSON)
    matched_skills = Column(JSON)  # List of matched skills
    missing_skills = Column(JSON)  # List of missing skills
    all_skills = Column(JSON)  # List of all skills from CV
    
    # Analysis results (stored as JSON)
    strengths = Column(JSON)  # List of strengths
    weaknesses = Column(JSON)  # List of weaknesses
    recommendations = Column(JSON)  # List of recommendations
    
    # Experience and Education (stored as JSON)
    experience = Column(JSON)  # List of experience entries
    education = Column(JSON)  # List of education entries
    
    # Text fields
    summary = Column(Text)
    raw_text = Column(Text)  # Original CV text
    
    # File information
    cv_filename = Column(String)
    cv_path = Column(String)
    
    # Metadata
    upload_date = Column(DateTime, default=datetime.utcnow)
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Foreign key to job description
    job_description_id = Column(Integer, ForeignKey("job_descriptions.id"))
    
    # Relationships
    job_description = relationship("JobDescription", back_populates="candidates")


class JobDescription(Base):
    __tablename__ = "job_descriptions"
    
    # Primary key
    id = Column(Integer, primary_key=True, index=True)
    
    # Job information
    jd_id = Column(String, unique=True, index=True)  # UUID
    title = Column(String, nullable=False, index=True)
    company = Column(String, index=True)
    
    # Requirements
    required_skills = Column(JSON)  # List of required skills
    min_experience = Column(Integer)
    
    # Text
    raw_text = Column(Text)
    
    # File information
    jd_filename = Column(String)
    jd_path = Column(String)
    
    # Metadata
    upload_date = Column(DateTime, default=datetime.utcnow)
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    candidates = relationship("Candidate", back_populates="job_description")
