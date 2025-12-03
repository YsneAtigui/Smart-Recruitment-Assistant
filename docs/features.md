# Features Documentation

## Overview

Smart Recruitment Assistant provides AI-powered tools for both recruiters and job seekers to streamline the hiring process.

---

## Recruiter Features

### 1. CV Upload and Parsing

**Description**: Upload resumes in PDF, DOCX, or TXT format for automated parsing and analysis.

**How it works**:
1. Drag and drop or select CV file(s)
2. System extracts text using PyMuPDF/python-docx
3. AI analyzes content and extracts:
   - Candidate name and contact info
   - Skills and technologies
   - Work experience
   - Education background
4. Candidate profile is created and stored

**Supported Formats**: PDF, DOCX, TXT

---

### 2. Job Description Management

**Description**: Create and manage job descriptions for candidate matching.

**Features**:
- Upload JD from file or paste text
- AI extraction of requirements
- Automatic skill identification
- Min experience parsing

---

### 3. Intelligent CV-JD Matching

**Description**: AI-powered matching that provides multi-dimensional scoring.

**Scoring Components**:
- **Semantic Similarity** (40%): Overall profile-role alignment
- **Skills Match** (30%): Technical and soft skills overlap
- **Experience** (20%): Years and relevance
- **Education** (10%): Degree and institution match

**Output**:
- Overall Match Score (0-100%)
- Letter Grade (A+, A, B, C, D)
- Detailed breakdown of all scores
- Matched skills (✓)
- Missing skills (⚠️)

 **Example**:
```
Match Score: 87%
Grade: A

Scores:
├─ Semantic: 90%
├─ Skills: 85%
├─ Experience: 88%
└─ Education: 85%

Matched Skills:
✓ Python ✓ React ✓ Docker

Missing Skills:
⚠️ AWS ⚠️ Kubernetes
```

---

### 4. Candidate Analytics Dashboard

**Description**: Visual analytics for candidate pipeline management.

**Charts and Metrics**:
- **Match Score Distribution**: Bar chart showing score ranges
- **Pipeline Summary**: Total candidates, average score, interview-ready count
- **Skill Analysis**: Common vs. rare skills
- **Grade Distribution**: A+/A/B/C/D breakdown

**Visualizations**:
- Bar charts (Recharts)
- Radar charts for skill profiles
- Progress indicators

---

### 5. Ask AI - RAG-Powered Q&A

**Description**: Natural language queries about candidates using RAG technology.

**Query Modes**:

#### a) Specific Candidate Mode
Ask questions about a single candidate's profile.

**Examples**:
- "Does John have cloud certifications?"
- "What projects has Sarah worked on?"
- "Summarize Mike's leadership experience"

#### b) All CVs for Job Mode (Default)
Query all candidates for a specific job opening.

**Examples**:
- "Who has the most React experience?"
- "Compare the top 3 candidates"
- "Which candidates have startup experience?"

#### c) All Candidates Database Mode
Query across entire candidate database with structured data + RAG.

**Examples**:
- "Who are the A-grade candidates?"
- "Which candidates have Python AND React?"
- "Show me candidates with 5+ years experience"

**Features**:
- Context-aware responses
- Source attribution with document names
- Markdown-formatted answers
- Conversation history

---

### 6. Candidate Comparison

**Description**: Side-by-side comparison of multiple candidates.

**Features**:
- Select up to 3 candidates
- Compare match scores
- Skills overlap visualization
- Strengths and weaknesses
- Experience comparison

---

### 7. Candidate Database Management

**Description**: Centralized database of all uploaded candidates.

**Features**:
- Grid view of all candidates
- Filter by job, grade, or skills
- Search by name or email
- Delete candidates
- View detailed profiles
- "Ask AI About All Candidates" button

---

## Candidate Features

### 1. Job Fit Analysis

**Description**: Get an instant analysis of how well you fit a job opening.

**Process**:
1. Upload your CV
2. Upload target job description
3. Receive detailed fit analysis

**Output**:
- Overall Fit Score
- Letter Grade
- Radar chart of scores
- Skill gap analysis
- Actionable recommendations

---

### 2. Skill Gap Analysis

**Description**: Identify which skills you have and which you need to develop.

**Visualization**:
- ✅ **Skills You Have**: Green badges
- ⚠️ **Skills to Improve**: Amber badges

**Example**:
```
✅ Skills You Have:
[Python] [JavaScript] [React] [Git]

⚠️ Skills to Improve:
[AWS] [Kubernetes] [TypeScript]
```

---

### 3. Personalized Recommendations

**Description**: AI-generated suggestions for improving your candidacy.

**Recommendation Types**:
- Certifications to pursue
- Skills to learn
- Resume improvements
- Experience highlights
- Timeline estimates

**Example**:
```
1. Complete AWS Solutions Architect certification
   Timeline: 2-4 weeks
   
2. Add leadership examples to your summary
   Timeline: 1 week
```

---

### 4. AI Career Coach

**Description**: Chat with an AI assistant about your career.

**Features**:
- Persona-aware responses (candidate perspective)
- Context includes both CV and target JD
- Markdown-formatted responses
- Source citations
- Suggested questions

**Example Questions**:
- "What are my top 3 strengths for this role?"
- "How can I improve my resume?"
- "Is my experience relevant for this position?"
- "What skills should I prioritize learning?"

---

### 5. Experience & Education Display

**Description**: Detailed breakdown of your professional journey.

**Sections**:
- **Professional Experience**: Extracted positions and companies
- **Education**: Degrees and institutions
- **Career Summary**: Total years, expertise areas

**Visual Elements**:
- Timeline indicators
- Icons for companies and schools
- Verification badges

---

### 6. Learning Resources

**Description**: Quick links to courses and materials for missing skills.

**Features**:
- Auto-generated based on skill gaps
- Course platform suggestions (Coursera, Udemy, etc.)
- Estimated time commitments

---

## Shared Features

### 1. Profile Summarization

**Description**: AI-generated summaries of CVs and job descriptions.

**Use Cases**:
- Quick candidate overview
- Job requirement snapshot
- Match analysis summary

**Technology**: Gemini 2.0 Flash with specialized prompts

---

### 2. ChromaDB Vector Indexing

**Description**: Automatic indexing of all documents for semantic search.

**How it works**:
1. Documents are chunked (500 chars, 50 overlap)
2. Embeddings generated via Google AI
3. Stored in ChromaDB collections
4. Indexed with metadata (candidate_id, type, etc.)

**Collections**:
- `all_cvs`: Global CV index
- `job_descriptions`: All JDs
- `job_{id}`: Job-specific index (JD + relevant CVs)

---

### 3. Multi-Format Support

**Supported File Types**:
- PDF (`.pdf`)
- Microsoft Word (`.docx`)
- Plain Text (`.txt`)

**Max File Size**: Configured in backend (default: 10 MB)

---

### 4. Real-Time Processing

**Description**: Near-instant file processing and analysis.

**Performance**:
- CV parsing: < 2 seconds
- Matching: < 5 seconds
- RAG queries: < 3 seconds

**Optimization**:
- Caching for repeated queries
- Batch processing for multiple files
- Lazy loading for large datasets

---

### 5. Responsive Design

**Description**: Works seamlessly across devices.

**Breakpoints**:
- Desktop: Full multi-column layouts
- Tablet: Responsive grid
- Mobile: Single-column, optimized touch targets

**Features**:
- Tailwind CSS responsive utilities
- Mobile-first approach
- Touch-friendly buttons and inputs

---

## Advanced Features

### 1. Source Attribution

**Description**: All AI responses include source document references.

**Display**:
- Document name badges
- Color-coded by type (CV = blue, JD = purple)
- Truncated text previews (optional)

**Example**:
```
Sources:
[📄 John Doe] [💼 Job Description]
```

---

### 2. Markdown Formatting

**Description**: AI responses support rich text formatting.

**Supported**:
- **Bold text**: `**text**` → **text**
- Bullet points: `• item` → • item
- Numbered lists: `1. item` → 1. item
- Line breaks and paragraphs

---

### 3. Context Switching

**Description**: Seamlessly switch between query contexts.

**Modes**:
- Specific candidate → All candidates for job
- All candidates for job → All database
- Clear context and restart

---

### 4. Database Management

**Description**: Admin tools for managing vector database.

**Features**:
- View collection statistics
- Clear specific collections
- Monitor document count
- Refresh indices

---

## Feature Comparison Matrix

| Feature | Recruiter | Candidate |
|---------|-----------|-----------|
| Upload CV | ✓ (Multiple) | ✓ (Single) |
| Upload JD | ✓ | ✓ |
| Match Scoring | ✓ | ✓ |
| Skill Analysis | ✓ | ✓ |
| RAG Q&A | ✓ (All modes) | ✓ (Personal) |
| Analytics Dashboard | ✓ | ✗ |
| Candidate Database | ✓ | ✗ |
| Comparison Tool | ✓ | ✗ |
| Recommendations | ✓ | ✓ |
| Learning Resources | ✗ | ✓ |
| AI Career Coach | ✗ | ✗ |

---

**Next**: See [Setup Guide](./setup.md) for installation instructions.
