"""
Summarization Routes - Handle CV and JD summarization
"""
from fastapi import APIRouter, HTTPException, Body
from typing import Dict, Any
import logging

from src.ai.summarization import (
    summarize_cv,
    summarize_jd,
    generate_strengths_and_weaknesses_summary
)
from api.schemas import SummarizationResponse

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/summarize/cv", response_model=SummarizationResponse)
async def summarize_candidate_cv(data: Dict[str, Any] = Body(...)):
    """
    Generate a summary of a candidate's CV
    
    Expects:
    - cv_text: Raw CV text
    """
    try:
        cv_text = data.get("cv_text") or data.get("cvText")
        
        if not cv_text:
            raise HTTPException(status_code=400, detail="cv_text is required")
        
        summary = summarize_cv(cv_text)
        
        logger.info("Successfully generated CV summary")
        
        return SummarizationResponse(summary=summary)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error summarizing CV: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error summarizing CV: {str(e)}")


@router.post("/summarize/jd", response_model=SummarizationResponse)
async def summarize_job_description(data: Dict[str, Any] = Body(...)):
    """
    Generate a summary of a job description
    
    Expects:
    - jd_text: Raw job description text
    """
    try:
        jd_text = data.get("jd_text") or data.get("jdText")
        
        if not jd_text:
            raise HTTPException(status_code=400, detail="jd_text is required")
        
        summary = summarize_jd(jd_text)
        
        logger.info("Successfully generated JD summary")
        
        return SummarizationResponse(summary=summary)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error summarizing JD: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error summarizing JD: {str(e)}")


@router.post("/summarize/analysis", response_model=SummarizationResponse)
async def summarize_match_analysis(data: Dict[str, Any] = Body(...)):
    """
    Generate strengths and weaknesses summary for a match
    
    Expects:
    - cv_text: Raw CV text
    - jd_text: Raw JD text
    - matched_skills: List of matched skills
    - missing_skills: List of missing skills
    """
    try:
        cv_text = data.get("cv_text") or data.get("cvText")
        jd_text = data.get("jd_text") or data.get("jdText") or data.get("job_offer_text")
        matched_skills = data.get("matched_skills") or data.get("matchedSkills", [])
        missing_skills = data.get("missing_skills") or data.get("missingSkills", [])
        
        if not cv_text or not jd_text:
            raise HTTPException(
                status_code=400,
                detail="Both cv_text and jd_text are required"
            )
        
        summary = generate_strengths_and_weaknesses_summary(
            cv_text=cv_text,
            job_offer_text=jd_text,
            matched_skills=matched_skills,
            missing_skills=missing_skills
        )
        
        logger.info("Successfully generated match analysis summary")
        
        return SummarizationResponse(summary=summary)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating match analysis: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error generating analysis: {str(e)}")
