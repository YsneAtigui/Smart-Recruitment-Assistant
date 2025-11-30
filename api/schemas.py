"""
Pydantic schemas for request/response validation
These match the TypeScript types in the React frontend
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from enum import Enum

# ========== Enums ==========
class GradeEnum(str, Enum):
    A_PLUS = "A+"
    A = "A"
    B = "B"
    C = "C"
    D = "D"

# ========== Response Schemas ==========
class ScoresResponse(BaseModel):
    """Score breakdown for matching"""
    semantic: float = Field(..., ge=0, le=100, description="Semantic similarity score")
    skills: float = Field(..., ge=0, le=100, description="Skills match score")
    experience: float = Field(..., ge=0, le=100, description="Experience match score")
    education: float = Field(..., ge=0, le=100, description="Education match score")

class JobDescriptionResponse(BaseModel):
    """Job description response"""
    title: str
    company: str
    requiredSkills: List[str]
    minExperience: int
    rawText: str

class CandidateResponse(BaseModel):
    """Candidate match response - matches frontend Candidate interface"""
    id: str
    name: str
    email: str
    matchScore: float = Field(..., ge=0, le=100)
    grade: GradeEnum
    scores: ScoresResponse
    matchedSkills: List[str]
    missingSkills: List[str]
    strengths: List[str]
    weaknesses: List[str]
    recommendations: List[str]
    summary: str
    experienceYears: int
    role: str

class RAGQueryResponse(BaseModel):
    """Response for RAG query"""
    answer: str
    sources: Optional[List[str]] = []

class SummarizationResponse(BaseModel):
    """Response for summarization"""
    summary: str

class UploadStatusResponse(BaseModel):
    """Upload status response"""
    status: str
    message: str
    filename: Optional[str] = None
    extractedData: Optional[Dict[str, Any]] = None

# ========== Request Schemas ==========
class RAGIndexRequest(BaseModel):
    """Request to index document for RAG"""
    candidateId: str
    candidateName: str
    cvText: str

class RAGQueryRequest(BaseModel):
    """Request to query RAG"""
    candidateId: str
    candidateName: str
    query: str
