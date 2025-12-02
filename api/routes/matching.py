"""
Matching Routes - Handle CV to Job Description matching
"""
from fastapi import APIRouter, HTTPException, Body, Depends
from sqlalchemy.orm import Session
from typing import Dict, Any
import logging
import uuid

from src.models import CV, JobDescription, MatchResult
from src.matching.matcher import AdvancedMatcher
from src.utils.embeddings import generate_embeddings
from api.schemas import CandidateResponse, ScoresResponse, GradeEnum
from api.database import get_db
from api.models import Candidate, JobDescription as JobDescriptionDB

router = APIRouter()
logger = logging.getLogger(__name__)

# Initialize matcher
matcher = AdvancedMatcher()

def map_grade_to_enum(grade_str: str) -> GradeEnum:
    """Map grade string to enum"""
    grade_map = {
        "A+": GradeEnum.A_PLUS,
        "A": GradeEnum.A,
        "A-": GradeEnum.A,
        "B+": GradeEnum.B,
        "B": GradeEnum.B,
        "B-": GradeEnum.B,
        "C+": GradeEnum.C,
        "C": GradeEnum.C,
        "C-": GradeEnum.C,
        "D": GradeEnum.D,
        "F": GradeEnum.D
    }
    return grade_map.get(grade_str, GradeEnum.C)

@router.post("/match", response_model=CandidateResponse)
async def match_cv_to_job(
    cv_data: Dict[str, Any] = Body(...),
    jd_data: Dict[str, Any] = Body(...),
    db: Session = Depends(get_db)
):
    """
    Match a CV against a Job Description
    
    Expects:
    - cv_data: Extracted CV information
    - jd_data: Extracted Job Description information
    
    Returns comprehensive match analysis
    """
    try:
        # Create CV entity
        cv = CV(
            raw_text=cv_data.get("raw_text", ""),
            name=cv_data.get("name", "Unknown"),
            contact=cv_data.get("contact", {}),
            skills=cv_data.get("skills", []),
            education=cv_data.get("education", []),
            experience=cv_data.get("experience", []),
            academic_projects=cv_data.get("academic_projects", []),
            diplomas=cv_data.get("diplomas", []),
        )
        
        # Generate CV embedding
        cv.embedding = generate_embeddings([cv.raw_text])[0]
        
        # Create Job Description entity
        jd = JobDescription(
            raw_text=jd_data.get("raw_text", jd_data.get("rawText", "")),
            job_title=jd_data.get("job_title", jd_data.get("title", "Unknown")),
            company_name=jd_data.get("company_name", jd_data.get("company", "Unknown")),
            location=jd_data.get("location", ""),
            job_type=jd_data.get("job_type", ""),
            responsibilities=jd_data.get("responsibilities", []),
            skills=jd_data.get("skills", jd_data.get("requiredSkills", [])),
            experience_level=jd_data.get("experience_level", ""),
            education_requirements=jd_data.get("education_requirements", []),
        )
        
        # Generate JD embedding
        jd.embedding = generate_embeddings([jd.raw_text])[0]
        
        # Perform matching
        match_result: MatchResult = matcher.match(cv, jd)
        
        # Extract years of experience
        years_of_experience = cv.get_years_of_experience() or 0
        
        # Generate candidate ID
        candidate_id = str(uuid.uuid4())
        
        # Get role from experience
        role = cv.experience[0] if cv.experience else "Unknown Role"
        
        # Map grade
        grade = map_grade_to_enum(match_result.get_grade())
        
        # Get or create JobDescription in database
        jd_id = jd_data.get("jd_id", str(uuid.uuid4()))
        db_jd = db.query(JobDescriptionDB).filter(JobDescriptionDB.jd_id == jd_id).first()
        
        if not db_jd:
            db_jd = JobDescriptionDB(
                jd_id=jd_id,
                title=jd.job_title,
                company=jd.company_name,
                required_skills=jd.skills,
                min_experience=int(jd_data.get("minExperience", 0)),
                raw_text=jd.raw_text,
                jd_filename=jd_data.get("filename", "")
            )
            db.add(db_jd)
            db.commit()
            db.refresh(db_jd)
        
        # Get AI-generated summary if provided, otherwise use generic summary
        cv_summary = cv_data.get("cv_summary") or f"{cv.name} is a candidate with {years_of_experience} years of experience. Match quality: {match_result.get_match_quality()}"
        
        # Save candidate to database
        db_candidate = Candidate(
            candidate_id=candidate_id,
            name=cv.name or "Unknown Candidate",
            email=cv.contact.get("email", ""),
            role=role,
            experience_years=years_of_experience,
            match_score=round(match_result.total_score, 2),
            grade=str(grade.value),
            semantic_score=round(match_result.semantic_score * 100, 2),
            skills_score=round(match_result.skill_match_ratio * 100, 2),
            experience_score=round(match_result.experience_score * 100, 2),
            education_score=round(match_result.education_score * 100, 2),
            matched_skills=match_result.matched_skills,
            missing_skills=match_result.missing_skills,
            all_skills=cv.skills,  # Save all skills from CV
            strengths=match_result.strengths,
            weaknesses=match_result.weaknesses,
            recommendations=match_result.recommendations,
            experience=cv.experience,
            education=cv.education,
            summary=cv_summary,
            raw_text=cv.raw_text,
            cv_filename=cv_data.get("filename", ""),
            job_description_id=db_jd.id
        )
        
        db.add(db_candidate)
        db.commit()
        db.refresh(db_candidate)
        
        # Get email safely with fallback
        candidate_email = cv.contact.get("email", "") or ""
        
        # Map to frontend format
        response = CandidateResponse(
            id=candidate_id,
            name=cv.name or "Unknown Candidate",
            email=candidate_email,
            matchScore=round(match_result.total_score, 2),
            grade=grade,
            scores=ScoresResponse(
                semantic=round(match_result.semantic_score * 100, 2),
                skills=round(match_result.skill_match_ratio * 100, 2),
                experience=round(match_result.experience_score * 100, 2),
                education=round(match_result.education_score * 100, 2)
            ),
            matchedSkills=match_result.matched_skills,
            missingSkills=match_result.missing_skills,
            strengths=match_result.strengths,
            weaknesses=match_result.weaknesses,
            recommendations=match_result.recommendations,
            summary=cv_summary,
            experienceYears=years_of_experience,
            role=role
        )
        
        logger.info(f"Successfully matched and saved CV: {cv.name} with score {match_result.total_score}")
        
        return response
        
    except Exception as e:
        logger.error(f"Error during matching: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error during matching: {str(e)}")
