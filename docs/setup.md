# Setup and Installation Guide

## Prerequisites

### System Requirements
- **Operating System**: Windows, macOS, or Linux
- **Python**: 3.9 or higher
- **Node.js**: 16 or higher
- **npm**: 8 or higher
- **RAM**: Minimum 4GB (8GB recommended)
- **Disk Space**: 2GB free space

### Required Accounts
- **Google AI API Key**: Get from [Google AI Studio](https://makersuite.google.com/app/apikey)

---

## Installation Steps

### 1. Clone the Repository

```bash
git clone <repository_url>
cd SmartRecru
```

### 2. Backend Setup

#### Step 2.1: Create Python Virtual Environment

**Windows**:
```bash
python -m venv venv
.\venv\Scripts\activate
```

**macOS/Linux**:
```bash
python3 -m venv venv
source venv/bin/activate
```

#### Step 2.2: Install Python Dependencies

```bash
pip install -r requirements.txt
```

**Key Dependencies**:
- FastAPI: Web framework
- Uvicorn: ASGI server
- Google Generative AI: LLM access
- ChromaDB: Vector database
- SQLAlchemy: ORM
- PyMuPDF: PDF processing
- python-docx: DOCX processing

#### Step 2.3: Configure Environment Variables

Create a `.env` file in the project root:

```env
# Required
GEMINI_API_KEY=your_api_key_here

# Optional
DATABASE_URL=sqlite:///./recruitment.db
CHROMA_PERSIST_DIR=./chroma_db
```

**Get your Gemini API Key**:
1. Visit [Google AI Studio]( https://makersuite.google.com/app/apikey)
2. Click "Create API Key"
3. Copy the key
4. Paste into `.env` file

#### Step 2.4: Initialize Database

The database will be automatically created on first run. To manually initialize:

```bash
python -c "from api.database import engine, Base; Base.metadata.create_all(bind=engine)"
```

---

### 3. Frontend Setup

#### Step 3.1: Navigate to Frontend Directory

```bash
cd app
```

#### Step 3.2: Install Node Dependencies

```bash
npm install
```

**Key Dependencies**:
- React: UI framework
- TypeScript: Type safety
- Vite: Build tool
- Tailwind CSS: Styling
- Axios: HTTP client
- Recharts: Charting library

#### Step 3.3: Configure Vite Proxy (Optional)

The `vite.config.ts` is already configured to proxy API requests to `http://localhost:8000`.

If you need to change the backend URL, edit `vite.config.ts`:

```typescript
export default defineConfig({
  server: {
    proxy: {
      '/api': {
        target: 'http://localhost:8000',  // Change this
        changeOrigin: true,
      },
    },
  },
});
```

---

## Running the Application

### Development Mode

#### Step 1: Start Backend Server

From the project root (with venv activated):

```bash
uvicorn api.main:app --reload --port 8000
```

**Options**:
- `--reload`: Auto-restart on code changes
- `--port 8000`: Run on port 8000
- `--host 0.0.0.0`: Allow external connections

**Expected Output**:
```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete.
```

#### Step 2: Start Frontend Dev Server

From the `app` directory:

```bash
npm run dev
```

**Expected Output**:
```
  VITE v5.x.x  ready in xxx ms

  ➜  Local:   http://localhost:5173/
  ➜  Network: use --host to expose
```

#### Step 3: Access Application

Open your browser and navigate to:
```
http://localhost:5173
```

---

## Production Deployment

### Backend Deployment

#### Option 1: Uvicorn with Gunicorn (Linux)

```bash
gunicorn api.main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

#### Option 2: Docker

**Create `Dockerfile`**:
```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**Build and Run**:
```bash
docker build -t smart-recruit-api .
docker run -p 8000:8000 --env-file .env smart-recruit-api
```

---

### Frontend Deployment

#### Step 1: Build Production Bundle

```bash
cd app
npm run build
```

This creates an optimized build in `app/dist/`.

#### Step 2: Deploy to Hosting

**Option A: Static Hosting (Netlify, Vercel)**

1. Connect your repository
2. Set build command: `cd app && npm run build`
3. Set publish directory: `app/dist`
4. Configure environment variables (API URL)

**Option B: Nginx**

```nginx
server {
    listen 80;
    server_name yourdomain.com;

    root /var/www/smart-recruit/dist;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }

    location /api {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }
}
```

---

## Verification

### Test Backend API

```bash
curl http://localhost:8000/health
# Expected: {"status": "healthy"}
```

### Test File Upload

```bash
curl -X POST http://localhost:8000/api/upload/cv \
  -F "file=@sample_cv.pdf"
```

### Test RAG Query

```bash
curl -X POST http://localhost:8000/api/rag/query \
  -H "Content-Type: application/json" \
  -d '{
    "candidateId": "test",
    "candidateName": "Test User",
    "query": "What is AI?",
    "persona": "recruiter"
  }'
```

---

## Troubleshooting

### Common Issues

#### 1. Gemini API Key Not Working

**Symptoms**: `401 Unauthorized` errors

**Solution**:
- Verify API key is correct in `.env`
- Check if .env file is in project root
- Ensure no extra spaces in API key
- Test key at [Google AI Studio](https://makersuite.google.com/)

---

#### 2. ChromaDB Connection Errors

**Symptoms**: `sqlite3.OperationalError`

**Solution**:
```bash
# Delete and recreate ChromaDB
rm -rf chroma_db
# Restart backend - ChromaDB will reinitialize
```

---

#### 3. Frontend Can't Connect to Backend

**Symptoms**: Network errors, CORS issues

**Solution**:
- Ensure backend is running on port 8000
- Check Vite proxy configuration
- Verify no firewall blocking

---

#### 4. Module Import Errors

**Symptoms**: `ModuleNotFoundError`

**Solution**:
```bash
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

---

#### 5. Port Already in Use

**Symptoms**: `Address already in use`

**Solution**:
```bash
# Find process using port
# Windows
netstat -ano | findstr :8000

# macOS/Linux
lsof -i :8000

# Kill the process
kill -9 <PID>
```

---

## Development Tips

### Hot Reload

Both frontend and backend support hot reload:
- **Frontend**: Vite automatically updates on file save
- **Backend**: Uvicorn `--reload` flag restarts on changes

### Debugging

#### Backend Debugging
```bash
# Run with debug logs
uvicorn api.main:app --reload --log-level debug
```

#### Frontend Debugging
- Open Browser DevTools (F12)
- Check Network tab for API calls
- View Console for errors

### Testing

#### Run Python Tests
```bash
pytest tests/ -v
```

#### Run Type Checking
```bash
# Frontend
cd app
npm run type-check

# Backend
mypy api/
```

---

## Environment Variables Reference

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `GEMINI_API_KEY` | ✓ | - | Google AI API key |
| `DATABASE_URL` | ✗ | `sqlite:///./recruitment.db` | Database connection string |
| `CHROMA_PERSIST_DIR` | ✗ | `./chroma_db` | ChromaDB storage path |
| `MAX_UPLOAD_SIZE` | ✗ | `10485760` (10MB) | Max file upload size |
| `CORS_ORIGINS` | ✗ | `["http://localhost:5173"]` | Allowed CORS origins |

---

## Next Steps

After successful installation:

1. **Explore Features**: See [Features Documentation](./features.md)
2. **API Reference**: See [API Documentation](./api.md)
3. **Architecture**: See [Architecture Overview](./architecture.md)
4. **RAG System**: See [RAG Documentation](./rag.md)

---

