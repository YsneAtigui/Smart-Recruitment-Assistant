"""
RAG Routes - Handle Retrieval-Augmented Generation for Q&A
"""
from fastapi import APIRouter, HTTPException
from typing import Dict
import logging

from src.ai.rag import RAGPipeline
from src.ai.qa import answer_question
from api.schemas import RAGIndexRequest, RAGQueryRequest, RAGQueryResponse

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
        
        # Create or get RAG pipeline for this candidate
        collection_name = f"cv_{candidate_id.replace('-', '_')}"
        rag_pipeline = RAGPipeline(
            collection_name=collection_name,
            persist_directory="./chroma_db"
        )
        
        # Index the CV document
        rag_pipeline.index_documents(
            documents=[request.cvText],
            metadatas=[{
                "candidate_id": candidate_id,
                "candidate_name": request.candidateName
            }]
        )
        
        # Store pipeline for later queries
        rag_pipelines[candidate_id] = rag_pipeline
        
        logger.info(f"Successfully indexed CV for candidate: {request.candidateName}")
        
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
        
        # Get or create RAG pipeline for this candidate
        if candidate_id not in rag_pipelines:
            # Try to load existing collection
            collection_name = f"cv_{candidate_id.replace('-', '_')}"
            try:
                rag_pipeline = RAGPipeline(
                    collection_name=collection_name,
                    persist_directory="./chroma_db"
                )
                rag_pipelines[candidate_id] = rag_pipeline
            except Exception as e:
                raise HTTPException(
                    status_code=404,
                    detail=f"CV not indexed for candidate {request.candidateName}. Please index first."
                )
        
        rag_pipeline = rag_pipelines[candidate_id]
        
        # Query and get answer
        answer = answer_question(request.query, rag_pipeline)
        
        # Get source documents for transparency
        retrieved_results = rag_pipeline.query(request.query, n_results=2)
        sources = retrieved_results.get('documents', [[]])[0] if retrieved_results.get('documents') else []
        
        logger.info(f"Successfully answered query for candidate: {request.candidateName}")
        
        return RAGQueryResponse(
            answer=answer,
            sources=sources[:2]  # Return top 2 source snippets
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error querying RAG: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error querying RAG: {str(e)}")
