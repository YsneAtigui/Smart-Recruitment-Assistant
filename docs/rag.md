# RAG System Documentation

## Overview

The Smart Recruitment Assistant uses Retrieval-Augmented Generation (RAG) to provide intelligent, context-aware answers about candidates and job descriptions.

---

## RAG Architecture

### Components

```
User Query → Query Router → Vector Search → Context Assembly → LLM → Formatted Response
                ↓              ↓                ↓               ↓
            [Mode Logic]  [ChromaDB]      [Metadata]      [Gemini 2.0]
```

### Technology Stack
- **Embeddings**: Google `text-embedding-004`
- **Vector Store**: ChromaDB
- **LLM**: Google Gemini 2.0 Flash Experimental
- **Chunking**: RecursiveCharacterTextSplitter (500 chars)

---

## Document Processing Pipeline

### 1. Text Extraction

**Source**: `src/pipelines/extraction.py`

**Supported Formats**:
- PDF → PyMuPDF (fitz)
- DOCX → python-docx
- TXT → Direct read

**Process**:
```python
file → extract_text() → cleaned_text
```

### 2. Text Chunking

**Source**: `src/ai/rag.py`

**Configuration**:
```python
chunk_size = 500       # Characters per chunk
chunk_overlap = 50     # Overlap between chunks
```

**Why These Values?**:
- **500 chars**: Optimal for semantic coherence
- **50 overlap**: Prevents context loss at boundaries

**Example**:
```
Original: "John Doe has 5 years experience in Python development. He worked at Tech Corp..."

Chunks:
[1] "John Doe has 5 years experience in Python development. He worked at..."
[2] "...worked at Tech Corp as Senior Developer focusing on backend systems..."
```

### 3. Embedding Generation

**Model**: `models/text-embedding-004`

**Process**:
```python
text_chunks → embed_documents() → vectors (768 dimensions)
```

**Characteristics**:
- Dimension: 768
- Normalized: Yes
- Batch size: 100 chunks

### 4. Vector Storage

**Collections Structure**:

#### a) `all_cvs`
- Contains: All candidate CVs
- Metadata: `candidate_id`, `candidate_name`, `type="cv"`
- Purpose: Global candidate search

#### b) `job_descriptions`
- Contains: All job descriptions
- Metadata: `job_id`, `type="job_description"`
- Purpose: JD reference and context

#### c) `job_{job_id}`
- Contains: Job description + related CVs
- Metadata: Same as above + `type` field
- Purpose: Job-specific queries

**Metadata Schema**:
```json
{
  "candidate_id": "cand_xyz789",
  "candidate_name": "John Doe",
  "type": "cv",  // or "job_description"
  "chunk_index": 0
}
```

---

## Query Processing

### Query Modes

#### 1. Specific Candidate Mode
**Endpoint**: `POST /api/rag/query`

**How it Works**:
1. Filter by `candidate_id` in metadata
2. Retrieve top-k relevant chunks from candidate's CV
3. Optionally include job description if `jobId` provided
4. Generate persona-aware answer

**Use Cases**:
- "Does John have AWS experience?"
- "What are Sarah's main projects?"

#### 2. All CVs for Job Mode
**Endpoint**: `POST /api/rag/query-all-cvs`

**How it Works**:
1. Query `job_{job_id}` collection
2. Retrieve chunks from all CVs + JD
3. Rank by relevance to query
4. Generate comparative answer

**Use Cases**:
- "Who has the most Python experience?"
- "Compare top 3 candidates"

#### 3. All Candidates Database Mode
**Endpoint**: `POST /api/rag/query-all-candidates`

**How it Works**:
1. Query SQL database for structured data
2. Query `all_cvs` collection for semantic context
3. Combine structured + unstructured data
4. Generate comprehensive answer

**Use Cases**:
- "Which candidates have A-grade matches?"
- "Show me candidates with 5+ years and Python"

---

## Retrieval Strategy

### Similarity Search

**Algorithm**: Cosine similarity on L2-normalized vectors

**Process**:
```python
query → embed_query() → query_vector → 
cosine_similarity(query_vector, doc_vectors) → 
top_k_results
```

**Parameters**:
- `n_results`: Number of chunks to retrieve
  - Specific candidate: 2-10
  - All CVs: 30-50
  - All database: 20-30

### Metadata Filtering

**Example**:
```python
# Get only John's CV chunks
filter = {"candidate_id": "cand_xyz789"}
results = collection.query(
    query_embeddings=query_vector,
    where=filter,
    n_results=10
)
```

### Re-ranking

Currently, ChromaDB returns results sorted by similarity. Future enhancement: implement re-ranking with cross-encoder.

---

## Answer Generation

### Prompt Engineering

**Recruiter Persona**:
```
You are an expert recruiter assistant. Given the following CV excerpts, 
answer the question professionally and concisely.

Context:
{context}

Question: {query}

Answer:
```

**Candidate Persona**:
```
You are a friendly career coach helping a job seeker. Based on their CV 
and the target job description, provide encouraging and actionable advice.

Context:
{context}

Question: {query}

Answer:
```

### Context Assembly

**Structure**:
```
Context = [
    "Chunk 1: John Doe has 5 years...",
    "Chunk 2: Worked at Tech Corp...",
    "Chunk 3: Job Description: We are looking for...",
    ...
]
```

**Max Context Length**: ~8000 tokens (model dependent)

### Response Formatting

**Features**:
- Markdown support (`**bold**`)
- Bullet points (auto-formatted)
- Numbered lists
- Source attribution

---

## Source Metadata

### Extraction

During retrieval, extract metadata from each chunk:

```python
{
    "name": "John Doe",  # candidate_name from metadata
    "type": "cv",        # or "job_description"
    "preview": None      # Optional text preview
}
```

### Deduplication

Remove duplicate sources (same candidate appears multiple times):

```python
source_names = set()  # Track unique (name, type) pairs
for metadata in results['metadatas']:
    name = metadata.get('candidate_name', 'Unknown')
    doc_type = metadata.get('type', 'cv')
    source_names.add((name, doc_type))
```

### Display

**Frontend Rendering**:
```tsx
{source_metadata.map((source, idx) => (
  <span className={source.type === 'cv' ? 'badge-blue' : 'badge-purple'}>
    {source.type === 'cv' ? '📄' : '💼'} {source.name}
  </span>
))}
```

---

## Performance Optimization

### 1. Batching

**Embedding Generation**:
```python
# Process 100 chunks at a time
batch_size = 100
for i in range(0, len(chunks), batch_size):
    batch = chunks[i:i+batch_size]
    embeddings = embed_model.embed_documents(batch)
```

### 2. Caching

**Recommended**: Cache frequently asked queries

```python
from functools import lru_cache

@lru_cache(maxsize=100)
def cached_query(query_text, candidate_id):
    return rag_pipeline.query(query_text, candidate_id)
```

### 3. Index Optimization

**ChromaDB Settings**:
```python
collection = client.create_collection(
    name="all_cvs",
    metadata={"hnsw:space": "cosine"}  # Cosine similarity
)
```

---

## Monitoring & Debugging

### Logging

**Enable Debug Logging**:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

logger.debug(f"Retrieved {len(results)} chunks")
logger.debug(f"Top result similarity: {results['distances'][0][0]}")
```

### Metrics to Track

1. **Query Latency**
   - Embedding generation: ~200ms
   - Vector search: ~50-100ms
   - LLM response: ~1-3s
   - Total: ~1.5-3.5s

2. **Chunk Retrieval**
   - Number of chunks retrieved
   - Average similarity score
   - Source diversity

3. **Answer Quality**
   - Response length
   - Source coverage
   - User feedback (implement thumbs up/down)

### Verification Script

**Location**: `tests/verify_chunks.py`

**Usage**:
```bash
python tests/verify_chunks.py
```

**Output**:
```
=== Collection: all_cvs ===
Total chunks: 150
Unique candidates: 10
Average chunk length: 485 chars

=== Sample Query Test ===
Query: "Python experience"
Top 3 results:
1. "John Doe has 7 years of Python..." (score: 0.89)
2. "Sarah Johnson specializes in Python..." (score: 0.85)
3. "Mike Chen built Python applications..." (score: 0.82)
```

---

## Best Practices

### 1. Chunking Strategy

**Do**:
- Keep chunks semantically coherent
- Maintain context with overlap
- Include metadata for filtering

**Don't**:
- Make chunks too small (< 200 chars)
- Make chunks too large (> 1000 chars)
- Split in middle of sentences

### 2. Query Formulation

**Good Queries**:
- "What machine learning experience does John have?"
- "Compare React skills across all candidates"
- "Which candidates have AWS certifications?"

**Poor Queries**:
- "Tell me about it" (vague)
- "asdf" (nonsense)
- "Yes or no" (too short)

### 3. Collection Management

**Recommendations**:
- Clear old collections periodically
- Re-index when documents update
- Monitor collection size (ChromaDB can handle millions)

---

## Troubleshooting

### Issue: Poor Search Results

**Symptoms**: Irrelevant chunks returned

**Solutions**:
1. Check chunk quality: `tests/verify_chunks.py`
2. Increase `n_results` parameter
3. Verify embeddings are generating correctly
4. Check metadata filtering logic

### Issue: Slow Queries

**Symptoms**: Queries take > 5 seconds

**Solutions**:
1. Reduce `n_results`
2. Enable result caching
3. Use smaller chunks
4. Check ChromaDB index health

### Issue: Source Metadata Missing

**Symptoms**: Sources show `"Unknown Candidate"`

**Solutions**:
1. Verify metadata added during indexing
2. Check `candidate_name` field in metadata
3. Re-index documents with correct metadata

---

## Future Enhancements

### Planned Features

1. **Hybrid Search**: Combine vector + keyword search
2. **Re-ranking**: Cross-encoder for better results
3. **Query Expansion**: Automatic query reformulation
4. **Conversation Memory**: Multi-turn dialogue context
5. **Feedback Loop**: Learn from user ratings

### Research Areas

- Fine-tuned embeddings for recruitment domain
- Custom chunking strategies for CVs
- Multi-lingual support
- Privacy-preserving RAG

---

**Related Documentation**:
- [API Reference](./api.md) - RAG endpoints
- [Architecture](./architecture.md) - System overview
- [Features](./features.md) - User-facing RAG features
