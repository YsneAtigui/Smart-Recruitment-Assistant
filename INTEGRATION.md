# Connecting React App to Python Backend

## Quick Start Guide

### 1. Backend Setup (FastAPI)

Install Python dependencies:
```bash
cd c:\Users\yassi\Desktop\SmartRecru
pip install -r requirements.txt
```

Start the FastAPI server:
```bash
python -m uvicorn api.main:app --reload --port 8000
```

The API will be available at `http://localhost:8000`
- API Documentation: `http://localhost:8000/docs`
- Health Check: `http://localhost:8000/health`

### 2. Frontend Setup (React + Vite)

Install Node.js dependencies:
```bash
cd c:\Users\yassi\Desktop\SmartRecru\app
npm install
```

Start the React dev server:
```bash
npm run dev
```

The React app will be available at `http://localhost:3000`

### 3. Environment Variables

Make sure you have `GEMINI_API_KEY` set in:
- Root `.env` file (for Python backend)
- `app/.env.local` file (for React frontend, if needed)

## Architecture

```
React Frontend (Port 3000)
         ↓
    Vite Proxy (/api/*)
         ↓
FastAPI Backend (Port 8000)
         ↓
   Python Backend (src/)
         ↓
   Gemini API + ChromaDB
```

## API Endpoints

### Upload
- `POST /api/upload/cv` - Upload CV file
- `POST /api/upload/job` - Upload job description file

### Matching
- `POST /api/match` - Match CV to job description

### RAG (Question & Answer)
- `POST /api/rag/index` - Index CV for Q&A
- `POST /api/rag/query` - Query indexed CV

### Summarization
- `POST /api/summarize/cv` - Summarize CV
- `POST /api/summarize/jd` - Summarize job description
- `POST /api/summarize/analysis` - Generate match analysis

## What Changed

### Backend (New)
- Created `api/` directory with FastAPI application
- Created route handlers: `upload.py`, `matching.py`, `rag.py`, `summarization.py`
- Added CORS middleware for React dev server
- Updated `requirements.txt` with FastAPI dependencies

### Frontend (Updated)
- Created `app/services/apiBackend.ts` - Real API client using axios
- Updated `app/package.json` - Added axios dependency
- Updated `app/vite.config.ts` - Added proxy configuration
- Kept `mockBackend.ts` for reference but components should now use `apiBackend.ts`

## Testing

1. Start both servers (backend on 8000, frontend on 3000)
2. Open React app at `http://localhost:3000`
3. Upload a CV and job description
4. Verify that real API calls are being made (check Network tab in DevTools)
5. Test matching, RAG Q&A, and other features

## Notes

- The frontend proxy forwards `/api/*` requests to `http://localhost:8000`
- Both servers must be running simultaneously
- Axios will be installed when you run `npm install`
- The backend stores data in memory (use a database for production)
