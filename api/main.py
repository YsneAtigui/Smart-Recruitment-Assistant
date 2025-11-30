"""
FastAPI Application - Smart Recruitment Assistant
Main entry point for the REST API
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

from api.routes import upload, matching, rag, summarization

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Smart Recruitment Assistant API",
    description="REST API for CV and Job Description matching, analysis, and Q&A",
    version="1.0.0"
)

# Configure CORS for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # React dev server
        "http://localhost:5173",  # Vite dev server
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(upload.router, prefix="/api", tags=["Upload"])
app.include_router(matching.router, prefix="/api", tags=["Matching"])
app.include_router(rag.router, prefix="/api", tags=["RAG"])
app.include_router(summarization.router, prefix="/api", tags=["Summarization"])

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Smart Recruitment Assistant API",
        "version": "1.0.0",
        "docs": "/docs"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
