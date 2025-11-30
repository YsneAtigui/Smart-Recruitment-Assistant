"""
Upload Routes - Handle file uploads for CVs and Job Descriptions
"""
from fastapi import APIRouter, UploadFile, File, HTTPException
from typing import Dict, Any
import tempfile
import os
import logging

from src.utils.documents import extract_text
from src.extraction import extract_information_from_cv_gemini, extract_information_from_jd_gemini
from api.schemas import UploadStatusResponse, JobDescriptionResponse

router = APIRouter()
logger = logging.getLogger(__name__)

# Store parsed data in memory (in production, use a database)
cv_storage: Dict[str, Dict[str, Any]] = {}
jd_storage: Dict[str, Dict[str, Any]] = {}

@router.post("/upload/cv", response_model=UploadStatusResponse)
async def upload_cv(file: UploadFile = File(...)):
    """
    Upload and parse a CV file (PDF, DOCX, TXT)
    
    Returns extracted information from the CV
    """
    try:
        # Validate file type
        allowed_extensions = ['.pdf', '.docx', '.txt']
        file_ext = os.path.splitext(file.filename)[1].lower()
        
        if file_ext not in allowed_extensions:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file type. Allowed: {', '.join(allowed_extensions)}"
            )
        
        # Save file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_ext) as tmp_file:
            content = await file.read()
            tmp_file.write(content)
            tmp_file_path = tmp_file.name
        
        try:
            # Extract text from document
            extraction_result = extract_text(tmp_file_path)
            
            if not extraction_result:
                raise HTTPException(
                    status_code=400,
                    detail="Failed to extract text from document"
                )
            
            cv_text = extraction_result["text"]
            
            # Extract structured information using Gemini
            cv_data = extract_information_from_cv_gemini(cv_text)
            cv_data["raw_text"] = cv_text
            cv_data["metadata"] = extraction_result["meta"]
            
            # Store in memory with filename as key
            cv_id = file.filename
            cv_storage[cv_id] = cv_data
            
            logger.info(f"Successfully processed CV: {file.filename}")
            
            return UploadStatusResponse(
                status="success",
                message="CV uploaded and processed successfully",
                filename=file.filename,
                extractedData=cv_data
            )
            
        finally:
            # Clean up temporary file
            if os.path.exists(tmp_file_path):
                os.unlink(tmp_file_path)
                
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing CV upload: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing CV: {str(e)}")


@router.post("/upload/job", response_model=JobDescriptionResponse)
async def upload_job_description(file: UploadFile = File(...)):
    """
    Upload and parse a Job Description file (PDF, DOCX, TXT)
    
    Returns extracted job requirements
    """
    try:
        # Validate file type
        allowed_extensions = ['.pdf', '.docx', '.txt']
        file_ext = os.path.splitext(file.filename)[1].lower()
        
        if file_ext not in allowed_extensions:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file type. Allowed: {', '.join(allowed_extensions)}"
            )
        
        # Save file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_ext) as tmp_file:
            content = await file.read()
            tmp_file.write(content)
            tmp_file_path = tmp_file.name
        
        try:
            # Extract text from document
            extraction_result = extract_text(tmp_file_path)
            
            if not extraction_result:
                raise HTTPException(
                    status_code=400,
                    detail="Failed to extract text from document"
                )
            
            jd_text = extraction_result["text"]
            
            # Extract structured information using Gemini
            jd_data = extract_information_from_jd_gemini(jd_text)
            jd_data["raw_text"] = jd_text
            jd_data["metadata"] = extraction_result["meta"]
            
            # Store in memory
            jd_id = file.filename
            jd_storage[jd_id] = jd_data
            
            logger.info(f"Successfully processed JD: {file.filename}")
            
            # Map to frontend format
            return JobDescriptionResponse(
                title=jd_data.get("job_title", "Unknown Position"),
                company=jd_data.get("company_name", "Unknown Company"),
                requiredSkills=jd_data.get("skills", []),
                minExperience=jd_data.get("experience_level", 0) if isinstance(jd_data.get("experience_level"), int) else 0,
                rawText=jd_text
            )
            
        finally:
            # Clean up temporary file
            if os.path.exists(tmp_file_path):
                os.unlink(tmp_file_path)
                
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing JD upload: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing Job Description: {str(e)}")


@router.get("/storage/cv/{filename}")
async def get_cv_data(filename: str):
    """Get stored CV data by filename"""
    if filename not in cv_storage:
        raise HTTPException(status_code=404, detail="CV not found")
    return cv_storage[filename]


@router.get("/storage/jd/{filename}")
async def get_jd_data(filename: str):
    """Get stored JD data by filename"""
    if filename not in jd_storage:
        raise HTTPException(status_code=404, detail="Job Description not found")
    return jd_storage[filename]
