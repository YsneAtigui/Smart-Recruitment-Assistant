# API Documentation

## Base URL

**Development**: `http://localhost:8000`  
**Production**: Configure via environment

## API Endpoints

### Upload Endpoints

#### Upload Job Description
```http
POST /api/upload/job
Content-Type: multipart/form-data
```

**Request**:
- `file`: File (PDF, DOCX, or TXT)

**Response** (200 OK):
```json
{
  "id": "job_abc123",
  "title": "Senior Software Engineer",
  "company": "Tech Corp",
  "requiredSkills": ["Python", "React", "AWS"],
  "minExperience": 5,
  "rawText": "Full job description text..."
}
```

**Errors**:
- `400`: Invalid file format
- `500`: Processing error

---

#### Upload CV
```http
POST /api/upload/cv
Content-Type: multipart/form-data
```

**Request**:
- `file`: File (PDF, DOCX, or TXT)

**Response** (200 OK):
```json
{
  "candidate_id": "cand_xyz789",
  "name": "John Doe",
  "email": "john@example.com",
  "skills": ["Python", "JavaScript", "Docker"],
  "experience_years": 7,
  "rawText": "Full CV text..."
}
```

---

### Matching Endpoints

#### Match CV to Job Description
```http
POST /api/match
Content-Type: application/json
```

**Request**:
```json
{
  "cv_data": {
    "candidate_id": "cand_xyz789",
    "name": "John Doe",
    "rawText": "CV text...",
    ...
  },
  "jd_data": {
    "id": "job_abc123",
    "title": "Senior Software Engineer",
    "rawText": "JD text...",
    ...
  }
}
```

**Response** (200 OK):
```json
{
  "id": "cand_xyz789",
  "name": "John Doe",
  "email": "john@example.com",
  "matchScore": 87,
  "grade": "A",
  "scores": {
    "semantic": 90,
    "skills": 85,
    "experience": 88,
    "education": 85
  },
  "matchedSkills": ["Python", "React", "Docker"],
  "missingSkills": ["AWS", "Kubernetes"],
  "allSkills": ["Python", "JavaScript", "React", "Docker", "Git"],
  "strengths": [
    "Strong Python and backend experience",
    "Excellent problem-solving skills"
  ],
  "weaknesses": [
    "Limited cloud platform experience",
    "No Kubernetes exposure"
  ],
  "recommendations": [
    "Complete AWS certification",
    "Build Kubernetes project for portfolio"
  ],
  "summary": "Highly qualified candidate with strong technical skills...",
  "experienceYears": 7,
  "role": "Full Stack Developer",
  "experience": ["Software Engineer at Company A (3 years)", ...],
  "education": ["BS Computer Science, University X"],
  "jobTitle": "Senior Software Engineer"
}
```

---

### RAG (Ask AI) Endpoints

#### Query Specific Candidate
```http
POST /api/rag/query
Content-Type: application/json
```

**Request**:
```json
{
  "candidateId": "cand_xyz789",
  "candidateName": "John Doe",
  "query": "Does this candidate have cloud experience?",
  "persona": "recruiter",
  "jobId": "job_abc123"
}
```

**Parameters**:
- `candidateId` (string, required): Candidate identifier
- `candidateName` (string, required): Candidate name
- `query` (string, required): Natural language question
- `persona` (string, optional): "recruiter" or "candidate" (default: "recruiter")
- `jobId` (string, optional): Job context for the query

**Response** (200 OK):
```json
{
  "answer": "Yes, John has experience with AWS and Azure cloud platforms, primarily focusing on serverless architectures and containerization.",
  "sources": ["CV chunk 1...", "CV chunk 2..."],
  "source_metadata": [
    {
      "name": "John Doe",
      "type": "cv",
      "preview": null
    },
    {
      "name": "Job Description",
      "type": "job_description",
      "preview": null
    }
  ]
}
```

---

#### Query All CVs for a Job
```http
POST /api/rag/query-all-cvs
Content-Type: application/json
```

**Request**:
```json
{
  "jobId": "job_abc123",
  "query": "Who has the most Python experience?",
  "persona": "recruiter"
}
```

**Response** (200 OK):
```json
{
  "answer": "Among all candidates, Sarah Johnson has the most extensive Python experience with 8 years, followed by John Doe with 7 years...",
  "sources": [...],
  "source_metadata": [...]
}
```

---

#### Query All Candidates (Database + RAG)
```http
POST /api/rag/query-all-candidates
Content-Type: application/json
```

**Request**:
```json
{
  "query": "Which candidates have A-grade matches?",
  "jobId": "job_abc123",
  "persona": "recruiter"
}
```

**Response** (200 OK):
```json
{
  "answer": "There are 3 candidates with A-grade matches: John Doe (A, 87%), Sarah Johnson (A+, 94%), and Mike Chen (A, 89%)...",
  "sources": [...],
  "source_metadata": [...],
  "candidates_found": 3,
  "database_data_included": true
}
```

---

### Summarization Endpoints

#### Summarize CV
```http
POST /api/summarize/cv
Content-Type: application/json
```

**Request**:
```json
{
  "cv_text": "Full CV text content..."
}
```

**Response** (200 OK):
```json
{
  "summary": "Experienced software engineer with 7 years in full-stack development, specializing in Python, React, and cloud technologies..."
}
```

---

#### Summarize Job Description
```http
POST /api/summarize/jd
Content-Type: application/json
```

**Request**:
```json
{
  "jd_text": "Full job description text..."
}
```

**Response** (200 OK):
```json
{
  "summary": "Senior position requiring 5+ years experience in Python, React, and AWS, focusing on scalable microservices architecture..."
}
```

---

### Candidate Management Endpoints

#### Get All Candidates
```http
GET /api/candidates
```

**Response** (200 OK):
```json
[
  {
    "id": "cand_xyz789",
    "name": "John Doe",
    "email": "john@example.com",
    "matchScore": 87,
    "grade": "A",
    ...
  },
  ...
]
```

---

#### Get Candidate by ID
```http
GET /api/candidates/{candidate_id}
```

**Response** (200 OK):
```json
{
  "id": "cand_xyz789",
  "name": "John Doe",
  ...
}
```

---

#### Delete Candidate
```http
DELETE /api/candidates/{candidate_id}
```

**Response** (200 OK):
```json
{
  "message": "Candidate deleted successfully",
  "candidate_id": "cand_xyz789"
}
```

---

### Database Management Endpoints

#### Get Database Statistics
```http
GET /api/database/stats
```

**Response** (200 OK):
```json
{
  "total_collections": 4,
  "total_documents": 150,
  "collections": [
    {
      "name": "all_cvs",
      "document_count": 50
    },
    {
      "name": "job_descriptions",
      "document_count": 10
    },
    {
      "name": "job_abc123",
      "document_count": 45
    }
  ],
  "persist_directory": "./chroma_db"
}
```

---

#### Clear Collection
```http
DELETE /api/database/collections/{collection_name}
```

**Response** (200 OK):
```json
{
  "message": "Collection cleared successfully",
  "collection_name": "job_abc123"
}
```

---

## Error Responses

All endpoints follow a consistent error format:

```json
{
  "detail": "Error message describing what went wrong"
}
```

### Common HTTP Status Codes
- `200`: Success
- `400`: Bad Request (invalid input)
- `404`: Not Found (resource doesn't exist)
- `422`: Unprocessable Entity (validation error)
- `500`: Internal Server Error

---

## Rate Limiting

- **Gemini API**: Subject to Google's quota (see Google AI documentation)
- **Recommendation**: Implement caching for frequently asked questions

---

## Authentication

Currently, the API does not require authentication. For production deployment:
1. Implement JWT-based authentication
2. Add API key validation
3. Use role-based access control (RBAC)

---

## Request Examples (curl)

### Upload and Match Workflow
```bash
# 1. Upload Job Description
curl -X POST http://localhost:8000/api/upload/job \
  -F "file=@job.pdf"

# 2. Upload CV
curl -X POST http://localhost:8000/api/upload/cv \
  -F "file=@resume.pdf"

# 3. Match CV to JD
curl -X POST http://localhost:8000/api/match \
  -H "Content-Type: application/json" \
  -d '{
    "cv_data": {...},
    "jd_data": {...}
  }'
```

### RAG Query
```bash
curl -X POST http://localhost:8000/api/rag/query \
  -H "Content-Type: application/json" \
  -d '{
    "candidateId": "cand_xyz789",
    "candidateName": "John Doe",
    "query": "What are the candidate'\''s main strengths?",
    "persona": "recruiter"
  }'
```

---

**Next**: See [Features Documentation](./features.md) for detailed feature descriptions.
