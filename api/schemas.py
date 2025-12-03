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
    id: str
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
    experience: Optional[List[str]] = []
    education: Optional[List[str]] = []
    allSkills: Optional[List[str]] = []

class SourceInfo(BaseModel):
    """Source information with metadata"""
    name: str  # Candidate name or document name
    type: str  # 'cv' or 'job_description'
    preview: Optional[str] = None  # Short preview text

class RAGQueryResponse(BaseModel):
    """Response for RAG query"""
    answer: str
    sources: Optional[List[str]] = []  # Legacy text sources
    source_metadata: Optional[List[SourceInfo]] = []  # New structured sources

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
    jobId: Optional[str] = None

class RAGQueryRequest(BaseModel):
    """Request to query RAG"""
    candidateId: str
    candidateName: str
    query: str
    persona: Optional[str] = "recruiter"
    jobId: Optional[str] = None

class RAGQueryAllCVsRequest(BaseModel):
    """Request to query all CVs for a specific job"""
    jobId: str
    query: str
    persona: Optional[str] = "recruiter"

class RAGQuerySpecificCVRequest(BaseModel):
    """Request to query a specific CV"""
    candidateId: str
    query: str
    persona: Optional[str] = "recruiter"

class RAGQueryAllCandidatesRequest(BaseModel):
    """Request to query all candidates with database integration"""
    query: str
    jobId: Optional[str] = None
    persona: Optional[str] = "recruiter"

class ChunkInfo(BaseModel):
    """Information about a document chunk"""
    id: str
    content: str
    metadata: Dict[str, Any]
    chunk_index: int

class AllCandidatesQueryResponse(BaseModel):
    """Response for querying all candidates"""
    answer: str
    sources: List[str]
    candidates_found: int
    database_data_included: bool

# ========== Database Management Schemas ==========
class CollectionInfoResponse(BaseModel):
    """Collection information response"""
    name: str
    document_count: int
    metadata: Optional[Dict[str, Any]] = {}
    exists: bool = True

class IndexedDocumentResponse(BaseModel):
    """Indexed document information"""
    id: str
    metadata: Dict[str, Any]
    preview: Optional[str] = None

class DatabaseStatsResponse(BaseModel):
    """Database statistics response"""
    total_collections: int
    total_documents: int
    collections: List[CollectionInfoResponse]
    persist_directory: Optional[str] = None

class ClearCollectionResponse(BaseModel):
    """Response for clearing a collection"""
    status: str
    message: str
    collection_name: str
