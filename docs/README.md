# Documentation Index

Welcome to the Smart Recruitment Assistant documentation. This guide will help you understand, set up, and use the platform effectively.

## Getting Started

**New to the project?** Start here:

1. **[README](../README.md)** - Project overview and quick start
2. **[Setup Guide](./setup.md)** - Installation and configuration
3. **[Features](./features.md)** - What the platform can do

## Documentation Structure

### Core Documentation

#### 📚 [Architecture Overview](./architecture.md)
Comprehensive system architecture documentation covering:
- High-level system design
- Technology stack (React, FastAPI, Gemini, ChromaDB)
- Component descriptions (Frontend, Backend, AI, Data layers)
- Data flow diagrams
- Deployment architecture
- Performance and scalability considerations

**Read this if you want to**:
- Understand how the system works
- Contribute to the codebase
- Deploy the application
- Optimize performance

---

#### 🔌 [API Documentation](./api.md)
Complete API reference with all endpoints:
- Upload endpoints (CV, Job Description)
- Matching endpoint
- RAG query endpoints (3 modes)
- Summarization endpoints
- Candidate management endpoints
- Database management endpoints
- Request/response schemas
- Error handling
- Code examples (curl)

**Read this if you want to**:
- Integrate with the API
- Build custom clients
- Understand data models
- Debug API issues

---

#### ⭐ [Features Documentation](./features.md)
Detailed feature descriptions for both user roles:
- **Recruiter Features**: CV upload, matching, analytics, RAG Q&A, candidate database
- **Candidate Features**: Fit analysis, skill gaps, recommendations, AI career coach
- **Shared Features**: Summarization, multi-format support, responsive design
- Feature comparison matrix
- Use case examples

**Read this if you want to**:
- Learn what the platform offers
- Understand user workflows
- Plan feature usage
- Train users

---

#### ⚙️ [Setup Guide](./setup.md)
Step-by-step installation and deployment:
- Prerequisites and system requirements
- Backend setup (Python, venv, dependencies)
- Frontend setup (Node.js, npm, Vite)
- Environment configuration
- Running in development mode
- Production deployment (Uvicorn, Gunicorn, Docker, Nginx)
- Troubleshooting common issues
- Environment variables reference

**Read this if you want to**:
- Install the application
- Deploy to production
- Troubleshoot setup issues
- Configure the environment

---

#### 🤖 [RAG System Documentation](./rag.md)
In-depth RAG implementation details:
- RAG architecture and components
- Document processing pipeline
- Text chunking strategy (500 chars, 50 overlap)
- Embedding generation (text-embedding-004)
- Vector storage (ChromaDB collections)
- Query processing (3 modes)
- Retrieval strategies and optimization
- Source metadata extraction
- Performance optimization
- Monitoring and debugging

**Read this if you want to**:
- Understand RAG internals
- Optimize query performance
- Debug RAG issues
- Extend RAG capabilities
- Implement similar systems

---

## Quick Reference

### Common Tasks

| Task | Documentation |
|------|---------------|
| Install the platform | [Setup Guide](./setup.md) |
| Use the recruiter dashboard | [Features - Recruiter](./features.md#recruiter-features) |
| Use the candidate dashboard | [Features - Candidate](./features.md#candidate-features) |
| Query the API | [API Documentation](./api.md) |
| Understand RAG queries | [RAG - Query Processing](./rag.md#query-processing) |
| Deploy to production | [Setup - Production](./setup.md#production-deployment) |
| Fix common errors | [Setup - Troubleshooting](./setup.md#troubleshooting) |
| Understand system design | [Architecture](./architecture.md) |

### Key Concepts

| Concept | Documentation Link |
|---------|-------------------|
| CV-JD Matching Algorithm | [Features - Matching](./features.md#3-intelligent-cv-jd-matching) |
| RAG Query Modes | [RAG - Query Modes](./rag.md#query-modes) |
| Vector Embeddings | [RAG - Embedding Generation](./rag.md#3-embedding-generation) |
| ChromaDB Collections | [RAG - Vector Storage](./rag.md#4-vector-storage) |
| API Endpoints | [API Reference](./api.md#api-endpoints) |
| Source Attribution | [Features - Source Attribution](./features.md#1-source-attribution) |

---

## Technology Reference

### Frontend Stack
- **Framework**: React 18 + TypeScript
- **Build Tool**: Vite
- **Styling**: Tailwind CSS
- **Charts**: Recharts
- **HTTP**: Axios

📖 [Architecture - Frontend Layer](./architecture.md#1-frontend-layer)

### Backend Stack
- **Framework**: FastAPI (Python)
- **Database**: SQLite + SQLAlchemy
- **Vector DB**: ChromaDB
- **LLM**: Google Gemini 2.0 Flash
- **Embeddings**: text-embedding-004

📖 [Architecture - Backend Layer](./architecture.md#2-backend-layer)

### AI Components
- **Matching**: Semantic similarity + skill analysis
- **Summarization**: Gemini-based text generation
- **RAG**: ChromaDB + Gemini

📖 [Architecture - AI Layer](./architecture.md#3-ai-processing-layer)

---

## Documentation for Different Roles

### For End Users
1. Start with [Features](./features.md)
2. See role-specific sections:
   - [Recruiter Features](./features.md#recruiter-features)
   - [Candidate Features](./features.md#candidate-features)

### For Developers
1. Read [Architecture Overview](./architecture.md)
2. Follow [Setup Guide](./setup.md)
3. Explore [API Documentation](./api.md)
4. Deep dive into [RAG System](./rag.md)

### For DevOps/System Admins
1. Review [Architecture - Deployment](./architecture.md#deployment-architecture)
2. Follow [Setup - Production Deployment](./setup.md#production-deployment)
3. Check [Setup - Troubleshooting](./setup.md#troubleshooting)
4. Monitor with [RAG - Monitoring](./rag.md#monitoring--debugging)

### For API Consumers
1. Start with [API Documentation](./api.md)
2. See [API Examples](./api.md#request-examples-curl)
3. Review [Error Responses](./api.md#error-responses)

---

## Contributing

Interested in contributing? Here's how:

1. **Understand the System**: Read [Architecture](./architecture.md)
2. **Set Up Dev Environment**: Follow [Setup - Development](./setup.md#development-mode)
3. **Choose a Feature**: See [Features](./features.md) for ideas
4. **Check API Contracts**: Review [API Documentation](./api.md)
5. **Understand RAG**: If working on AI features, read [RAG System](./rag.md)

---

## Additional Resources

### External Links
- [Google Gemini API](https://ai.google.dev/)
- [ChromaDB Documentation](https://docs.trychroma.com/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [React Documentation](https://react.dev/)
- [Tailwind CSS](https://tailwindcss.com/)

---


## Document Map

```
docs/
├── README.md (this file)       # Documentation index and guide
├── architecture.md             # System architecture and design
├── api.md                      # Complete API reference
├── features.md                 # User features and capabilities
├── setup.md                    # Installation and deployment
└── rag.md                      # RAG system deep dive
```

---

