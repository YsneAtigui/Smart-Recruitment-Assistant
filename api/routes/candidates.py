"""
API routes for candidate management (CRUD operations)
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from api.database import get_db
from api.models import Candidate, JobDescription
from api.schemas import CandidateResponse

router = APIRouter(prefix="/api/candidates", tags=["candidates"])


@router.get("", response_model=List[dict])
def get_all_candidates(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get all candidates from database"""
    candidates = db.query(Candidate).offset(skip).limit(limit).all()
    
    result = []
    for candidate in candidates:
        # Get job description title
        job_title = None
        if candidate.job_description:
            job_title = candidate.job_description.title
        
        result.append({
            "id": candidate.candidate_id,
            "db_id": candidate.id,
            "name": candidate.name,
            "email": candidate.email,
            "role": candidate.role,
            "matchScore": candidate.match_score,
            "grade": candidate.grade,
            "jobTitle": job_title,  # Add job title
            "scores": {
                "semantic": candidate.semantic_score,
                "skills": candidate.skills_score,
                "experience": candidate.experience_score,
                "education": candidate.education_score
            },
            "matchedSkills": candidate.matched_skills or [],
            "missingSkills": candidate.missing_skills or [],
            "allSkills": candidate.all_skills or [],
            "strengths": candidate.strengths or [],
            "weaknesses": candidate.weaknesses or [],
            "recommendations": candidate.recommendations or [],
            "experience": candidate.experience or [],
            "education": candidate.education or [],
            "summary": candidate.summary,
            "experienceYears": candidate.experience_years,
            "uploadDate": candidate.upload_date.isoformat() if candidate.upload_date else None,
            "cvFilename": candidate.cv_filename,
            "jobDescriptionId": candidate.job_description_id
        })
    
    return result


@router.get("/{candidate_id}", response_model=dict)
def get_candidate(candidate_id: str, db: Session = Depends(get_db)):
    """Get specific candidate by ID"""
    candidate = db.query(Candidate).filter(Candidate.candidate_id == candidate_id).first()
    
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
    
    return {
        "id": candidate.candidate_id,
        "db_id": candidate.id,
        "name": candidate.name,
        "email": candidate.email,
        "role": candidate.role,
        "matchScore": candidate.match_score,
        "grade": candidate.grade,
        "scores": {
            "semantic": candidate.semantic_score,
            "skills": candidate.skills_score,
            "experience": candidate.experience_score,
            "education": candidate.education_score
        },
        "matchedSkills": candidate.matched_skills or [],
        "missingSkills": candidate.missing_skills or [],
        "allSkills": candidate.all_skills or [],
        "strengths": candidate.strengths or [],
        "weaknesses": candidate.weaknesses or [],
        "recommendations": candidate.recommendations or [],
        "experience": candidate.experience or [],
        "education": candidate.education or [],
        "summary": candidate.summary,
        "rawText": candidate.raw_text,
        "experienceYears": candidate.experience_years,
        "uploadDate": candidate.upload_date.isoformat() if candidate.upload_date else None,
        "cvFilename": candidate.cv_filename,
        "jobDescriptionId": candidate.job_description_id
    }


@router.delete("/{candidate_id}")
def delete_candidate(candidate_id: str, db: Session = Depends(get_db)):
    """Delete a candidate"""
    candidate = db.query(Candidate).filter(Candidate.candidate_id == candidate_id).first()
    
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
    
    db.delete(candidate)
    db.commit()
    
    return {"status": "success", "message": f"Candidate {candidate.name} deleted"}


@router.get("/job-descriptions/all", response_model=List[dict])
def get_all_job_descriptions(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get all job descriptions from database"""
    job_descriptions = db.query(JobDescription).offset(skip).limit(limit).all()
    
    result = []
    for jd in job_descriptions:
        result.append({
            "id": jd.jd_id,
            "db_id": jd.id,
            "title": jd.title,
            "company": jd.company,
            "requiredSkills": jd.required_skills or [],
            "minExperience": jd.min_experience,
            "rawText": jd.raw_text,
            "uploadDate": jd.upload_date.isoformat() if jd.upload_date else None,
            "jdFilename": jd.jd_filename,
            "candidateCount": len(jd.candidates) if jd.candidates else 0
        })
    
    return result
