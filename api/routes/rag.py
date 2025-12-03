"""
RAG Routes - Handle Retrieval-Augmented Generation for Q&A
"""
from fastapi import APIRouter, HTTPException
from typing import Dict
import logging

from src.ai.rag import RAGPipeline
from src.ai.qa import answer_question
from api.schemas import (
    RAGIndexRequest, 
    RAGQueryRequest, 
    RAGQueryResponse,
    RAGQueryAllCVsRequest,
    RAGQuerySpecificCVRequest,
    RAGQueryAllCandidatesRequest,
    AllCandidatesQueryResponse
)

router = APIRouter()
logger = logging.getLogger(__name__)

# Initialize RAG pipeline (one per session, or create new per candidate)
rag_pipelines: Dict[str, RAGPipeline] = {}

@router.post("/rag/index")
async def index_cv_for_rag(request: RAGIndexRequest):
    """
    Index a CV document for RAG-based Q&A
    
    Creates a vector store collection for the candidate's CV
    """
    try:
        candidate_id = request.candidateId
        job_id = request.jobId
        
        # Determine collection name
        if job_id:
            # Index into the specific job collection
            collection_name = f"job_{job_id}"
            print(f"DEBUG: Indexing CV for job_id={job_id} into collection={collection_name}")
        else:
            # Fallback to general collection (legacy behavior)
            collection_name = "all_cvs"
            print(f"DEBUG: Indexing CV (no job_id) into collection={collection_name}")
            
        rag_pipeline = RAGPipeline(
            collection_name=collection_name,
            persist_directory="./chroma_db"
        )
        
        # Index the CV document
        rag_pipeline.index_documents(
            documents=[request.cvText],
            metadatas=[{
                "candidate_id": candidate_id,
                "candidate_name": request.candidateName,
                "type": "cv"
            }]
        )
        
        logger.info(f"Successfully indexed CV for candidate: {request.candidateName} into {collection_name}")
        
        return {
            "status": "success",
            "message": f"CV indexed successfully for {request.candidateName}",
            "candidateId": candidate_id
        }
        
    except Exception as e:
        logger.error(f"Error indexing CV: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error indexing CV: {str(e)}")


@router.post("/rag/query", response_model=RAGQueryResponse)
async def query_cv_rag(request: RAGQueryRequest):
    """
    Query indexed CV using RAG
    
    Retrieves relevant context and generates an answer using Gemini
    """
    try:
        candidate_id = request.candidateId
        persona = request.persona
        job_id = request.jobId
        
        print(f"DEBUG: Querying RAG - candidate_id={candidate_id}, job_id={job_id}, persona={persona}")
        
        combined_context = []
        sources = []
        source_names = set()  # Track unique source names
        
        if job_id:
            # --- JOB-SPECIFIC QUERY ---
            # Query the specific job collection which contains the JD and all relevant CVs
            collection_name = f"job_{job_id}"
            pipeline = RAGPipeline(collection_name=collection_name, persist_directory="./chroma_db")
            
            if persona == "candidate":
                # Candidate sees only their own CV + the JD
                # We need to fetch the JD specifically + the candidate's CV
                # 1. Fetch JD (type='job_description')
                jd_results = pipeline.query_with_filter(
                    request.query,
                    metadata_filter={"type": "job_description"},
                    n_results=1
                )
                if jd_results.get('documents'):
                    combined_context.extend(jd_results['documents'][0])
                    sources.extend(jd_results['documents'][0])
                    if jd_results.get('metadatas'):
                        for meta in jd_results['metadatas'][0]:
                            source_names.add(("Job Description", "job_description"))
                
                # 2. Fetch Candidate CV (candidate_id=...)
                cv_results = pipeline.query_with_filter(
                    request.query,
                    metadata_filter={"candidate_id": candidate_id},
                    n_results=2
                )
                if cv_results.get('documents'):
                    combined_context.extend(cv_results['documents'][0])
                    sources.extend(cv_results['documents'][0])
                    if cv_results.get('metadatas'):
                        for meta in cv_results['metadatas'][0]:
                            name = meta.get('candidate_name', 'Unknown Candidate')
                            source_names.add((name, "cv"))
                    
            else:
                # Recruiter sees everything in this job context (JD + All CVs)
                # Just query the collection broadly
                results = pipeline.query(request.query, n_results=30)
                if results.get('documents'):
                    combined_context.extend(results['documents'][0])
                    sources.extend(results['documents'][0])
                    if results.get('metadatas'):
                        for meta in results['metadatas'][0]:
                            if meta.get('type') == 'job_description':
                                source_names.add(("Job Description", "job_description"))
                            else:
                                name = meta.get('candidate_name', 'Unknown Candidate')
                                source_names.add((name, "cv"))
        
        else:
            # --- GLOBAL / LEGACY QUERY ---
            # Initialize pipelines
            cv_pipeline = RAGPipeline(collection_name="all_cvs", persist_directory="./chroma_db")
            jd_pipeline = RAGPipeline(collection_name="job_descriptions", persist_directory="./chroma_db")
            
            # 1. Query CVs
            if persona == "candidate":
                # Candidate sees only their own CV
                cv_results = cv_pipeline.query_with_filter(
                    request.query, 
                    metadata_filter={"candidate_id": candidate_id}, 
                    n_results=2
                )
            else:
                # Recruiter sees all CVs
                cv_results = cv_pipeline.query(request.query, n_results=3)
                
            if cv_results.get('documents'):
                combined_context.extend(cv_results['documents'][0])
                sources.extend(cv_results['documents'][0])
                if cv_results.get('metadatas'):
                    for meta in cv_results['metadatas'][0]:
                        name = meta.get('candidate_name', 'Unknown Candidate')
                        source_names.add((name, "cv"))

            # 2. Query Job Descriptions (Both see relevant JDs)
            jd_results = jd_pipeline.query(request.query, n_results=2)
            if jd_results.get('documents'):
                combined_context.extend(jd_results['documents'][0])
                sources.extend(jd_results['documents'][0])
                source_names.add(("Job Description", "job_description"))
            
        # Create a temporary pipeline with combined context for the answer generation function
        class MockPipeline:
            def query(self, q):
                return {'documents': [combined_context]}
        
        mock_pipeline = MockPipeline()
        
        # Query and get answer
        answer = answer_question(request.query, mock_pipeline, persona=persona)
        
        logger.info(f"Successfully answered query for candidate: {request.candidateName}")
        print("\n=== RAG CONTEXT RETRIEVED ===")
        for i, doc in enumerate(combined_context):
            print(f"[{i+1}] {doc[:200]}...")
        print("=============================\n")
        
        # Create source metadata
        from api.schemas import SourceInfo
        source_metadata = [
            SourceInfo(name=name, type=doc_type, preview=None)
            for name, doc_type in source_names
        ]
        
        return RAGQueryResponse(
            answer=answer,
            sources=sources[:4],  # Return top source snippets (legacy)
            source_metadata=source_metadata  # New structured sources
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error querying RAG: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error querying RAG: {str(e)}")


@router.post("/rag/query-all-cvs", response_model=RAGQueryResponse)
async def query_all_cvs_for_job(request: RAGQueryAllCVsRequest):
    """
    Query all CVs for a specific job description
    
    Retrieves context from all CVs indexed for this job + the job description
    """
    try:
        from api.schemas import RAGQueryAllCVsRequest
        
        job_id = request.jobId
        persona = request.persona
        
        print(f"DEBUG: Querying all CVs for job_id={job_id}, persona={persona}")
        
        # Query the job-specific collection
        collection_name = f"job_{job_id}"
        pipeline = RAGPipeline(collection_name=collection_name, persist_directory="./chroma_db")
        
        # Get all documents in this collection (JD + all CVs)
        results = pipeline.query(request.query, n_results=50)
        
        combined_context = []
        sources = []
        source_names = set()
        
        if results.get('documents'):
            combined_context.extend(results['documents'][0])
            sources.extend(results['documents'][0])
            if results.get('metadatas'):
                for meta in results['metadatas'][0]:
                    if meta.get('type') == 'job_description':
                        source_names.add(("Job Description", "job_description"))
                    else:
                        name = meta.get('candidate_name', 'Unknown Candidate')
                        source_names.add((name, "cv"))
        
        # Create a temporary pipeline for answer generation
        class MockPipeline:
            def query(self, q):
                return {'documents': [combined_context]}
        
        mock_pipeline = MockPipeline()
        answer = answer_question(request.query, mock_pipeline, persona=persona)
        
        logger.info(f"Successfully answered query for all CVs in job: {job_id}")
        print(f"\n=== Retrieved {len(combined_context)} chunks for job {job_id} ===\n")
        
        # Create source metadata
        from api.schemas import SourceInfo
        source_metadata = [
            SourceInfo(name=name, type=doc_type, preview=None)
            for name, doc_type in source_names
        ]
        
        return RAGQueryResponse(
            answer=answer,
            sources=sources[:5],
            source_metadata=source_metadata
        )
        
    except Exception as e:
        logger.error(f"Error querying all CVs: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error querying all CVs: {str(e)}")


@router.post("/rag/query-specific-cv", response_model=RAGQueryResponse)
async def query_specific_cv(request: RAGQuerySpecificCVRequest):
    """
    Query a specific candidate's CV
    
    Retrieves context only from the specified candidate's CV
    """
    try:
        from api.schemas import RAGQuerySpecificCVRequest
        
        candidate_id = request.candidateId
        persona = request.persona
        
        print(f"DEBUG: Querying specific CV for candidate_id={candidate_id}")
        
        # Try both collections: all_cvs and job-specific collections
        combined_context = []
        sources = []
        
        # First try all_cvs collection
        cv_pipeline = RAGPipeline(collection_name="all_cvs", persist_directory="./chroma_db")
        cv_results = cv_pipeline.query_with_filter(
            request.query,
            metadata_filter={"candidate_id": candidate_id},
            n_results=10
        )
        
        if cv_results.get('documents'):
            combined_context.extend(cv_results['documents'][0])
            sources.extend(cv_results['documents'][0])
        
        if not combined_context:
            raise HTTPException(
                status_code=404,
                detail=f"No CV found for candidate ID: {candidate_id}"
            )
        
        # Create a temporary pipeline for answer generation
        class MockPipeline:
            def query(self, q):
                return {'documents': [combined_context]}
        
        mock_pipeline = MockPipeline()
        answer = answer_question(request.query, mock_pipeline, persona=persona)
        
        logger.info(f"Successfully answered query for candidate: {candidate_id}")
        
        return RAGQueryResponse(
            answer=answer,
            sources=sources[:5]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error querying specific CV: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error querying specific CV: {str(e)}")


@router.post("/rag/query-all-candidates")
async def query_all_candidates_with_db(request: RAGQueryAllCandidatesRequest):
    """
    Query all candidates using database + RAG integration
    
    Fetches candidate data from database and enriches with RAG context
    """
    try:
        from api.schemas import RAGQueryAllCandidatesRequest, AllCandidatesQueryResponse
        from api.database import SessionLocal
        from api.models import Candidate, JobDescription
        from sqlalchemy.orm import Session
        
        persona = request.persona
        job_id = request.jobId
        
        print(f"DEBUG: Querying all candidates with DB integration, job_id={job_id}")
        
        # Query database for candidates
        db: Session = SessionLocal()
        try:
            if job_id:
                # Get candidates for specific job
                candidates = db.query(Candidate).filter(
                    Candidate.job_description.has(jd_id=job_id)
                ).all()
            else:
                # Get all candidates
                candidates = db.query(Candidate).all()
        finally:
            db.close()
        
        candidates_found = len(candidates)
        print(f"Found {candidates_found} candidates in database")
        
        # Build structured context from database
        db_context = []
        for candidate in candidates:
            candidate_info = f"""
Candidate: {candidate.name}
Email: {candidate.email}
Role: {candidate.role}
Experience: {candidate.experience_years} years
Match Score: {candidate.match_score}
Grade: {candidate.grade}
Skills: {', '.join(candidate.all_skills or [])}
Matched Skills: {', '.join(candidate.matched_skills or [])}
Missing Skills: {', '.join(candidate.missing_skills or [])}
Strengths: {'; '.join(candidate.strengths or [])}
Weaknesses: {'; '.join(candidate.weaknesses or [])}
"""
            db_context.append(candidate_info.strip())
        
        # Query RAG for additional context
        rag_context = []
        sources = []
        
        if job_id:
            # Query job-specific collection
            collection_name = f"job_{job_id}"
            try:
                pipeline = RAGPipeline(collection_name=collection_name, persist_directory="./chroma_db")
                results = pipeline.query(request.query, n_results=20)
                if results.get('documents'):
                    rag_context.extend(results['documents'][0])
                    sources.extend(results['documents'][0])
            except Exception as e:
                print(f"Warning: Could not query job collection: {e}")
        else:
            # Query all_cvs collection
            try:
                pipeline = RAGPipeline(collection_name="all_cvs", persist_directory="./chroma_db")
                results = pipeline.query(request.query, n_results=20)
                if results.get('documents'):
                    rag_context.extend(results['documents'][0])
                    sources.extend(results['documents'][0])
            except Exception as e:
                print(f"Warning: Could not query CVs collection: {e}")
        
        # Combine database and RAG context
        combined_context = db_context + rag_context
        
        # Create a temporary pipeline for answer generation
        class MockPipeline:
            def query(self, q):
                return {'documents': [combined_context]}
        
        mock_pipeline = MockPipeline()
        answer = answer_question(request.query, mock_pipeline, persona=persona)
        
        logger.info(f"Successfully answered query with {candidates_found} candidates from DB")
        
        return AllCandidatesQueryResponse(
            answer=answer,
            sources=sources[:5],
            candidates_found=candidates_found,
            database_data_included=True
        )
        
    except Exception as e:
        logger.error(f"Error querying all candidates: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error querying all candidates: {str(e)}")

