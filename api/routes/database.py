"""
Database Management Routes - Handle ChromaDB database operations
"""
from fastapi import APIRouter, HTTPException
from typing import Dict, List, Any
import logging

from src.utils.db_manager import db_manager
from api.schemas import (
    DatabaseStatsResponse, 
    CollectionInfoResponse,
    IndexedDocumentResponse,
    ClearCollectionResponse
)

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/database/stats", response_model=DatabaseStatsResponse)
async def get_database_stats():
    """
    Get comprehensive ChromaDB database statistics
    
    Returns statistics about all collections, total documents, etc.
    """
    try:
        stats = db_manager.get_database_stats()
        return DatabaseStatsResponse(**stats)
    except Exception as e:
        logger.error(f"Error getting database stats: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error getting database stats: {str(e)}")


@router.get("/database/collections")
async def list_collections():
    """
    List all collections in the database
    
    Returns list of collection names with their metadata
    """
    try:
        stats = db_manager.get_database_stats()
        collections = stats.get("collections", [])
        
        return {
            "collections": collections,
            "total": len(collections)
        }
    except Exception as e:
        logger.error(f"Error listing collections: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error listing collections: {str(e)}")


@router.get("/database/collections/{collection_name}")
async def get_collection_info(collection_name: str):
    """
    Get detailed information about a specific collection
    """
    try:
        info = db_manager.get_collection_info(collection_name)
        
        if not info.get("exists", False):
            raise HTTPException(status_code=404, detail=f"Collection '{collection_name}' not found")
        
        return CollectionInfoResponse(**info)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting collection info: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error getting collection info: {str(e)}")


@router.get("/database/collections/{collection_name}/documents")
async def get_collection_documents(collection_name: str, limit: int = 100):
    """
    Get indexed documents from a specific collection
    
    Returns documents with their metadata
    """
    try:
        documents = db_manager.get_indexed_documents(collection_name, limit=limit)
        
        return {
            "collection_name": collection_name,
            "documents": documents,
            "count": len(documents)
        }
    except Exception as e:
        logger.error(f"Error getting documents: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error getting documents: {str(e)}")


@router.delete("/database/collections/{collection_name}")
async def clear_collection(collection_name: str):
    """
    Clear all documents from a collection (keeps the collection itself)
    """
    try:
        from src.ai.rag import RAGPipeline
        
        # Use RAGPipeline to clear the collection
        rag = RAGPipeline(collection_name=collection_name)
        success = rag.clear_collection()
        
        if success:
            return ClearCollectionResponse(
                status="success",
                message=f"Successfully cleared collection '{collection_name}'",
                collection_name=collection_name
            )
        else:
            raise HTTPException(status_code=500, detail="Failed to clear collection")
            
    except Exception as e:
        logger.error(f"Error clearing collection: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error clearing collection: {str(e)}")


@router.post("/database/collections/{collection_name}/reindex")
async def reindex_collection(collection_name: str):
    """
    Placeholder for reindexing a collection
    
    This would require access to the original documents
    """
    return {
        "status": "not_implemented",
        "message": "Reindexing requires access to original source documents"
    }
