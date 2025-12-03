# Google Cloud Run Deployment Guide

## Prerequisites

1. **Google Cloud Account**: [Sign up here](https://cloud.google.com/) (New users get $300 credit)
2. **Google Cloud CLI**: [Install gcloud CLI](https://cloud.google.com/sdk/docs/install)
3. **Billing Enabled**: Required even for free tier (you won't be charged if within limits)

---

## Deployment Steps

### 1. Initialize Google Cloud

Open your terminal and login:

```bash
gcloud auth login
gcloud init
```
- Create a new project (e.g., `smart-recruit-app`)
- Select a region (e.g., `us-central1`)

### 2. Enable Services

Enable the necessary APIs:

```bash
gcloud services enable run.googleapis.com \
    cloudbuild.googleapis.com \
    artifactregistry.googleapis.com
```

### 3. Deploy Backend

Run this single command to build and deploy:

```bash
gcloud run deploy smartrecruit-api \
    --source . \
    --region us-central1 \
    --allow-unauthenticated \
    --memory 1Gi \
    --set-env-vars GEMINI_API_KEY="your_api_key_here" \
    --set-env-vars PYTHON_VERSION="3.10.13" \
    --set-env-vars DATABASE_URL="sqlite:///./recruitment.db" \
    --set-env-vars CHROMA_PERSIST_DIR="./chroma_db"
```

**Explanation of flags:**
- `--source .`: Builds container from source code (using Dockerfile)
- `--memory 1Gi`: Allocates 1GB RAM (Perfect for PyTorch!)
- `--allow-unauthenticated`: Makes the API public

### 4. Get Backend URL

After deployment, you'll see a URL like:
`https://smartrecruit-api-xyz-uc.a.run.app`

### 5. Deploy Frontend (Firebase Hosting)

Google Cloud works great with Firebase Hosting for the frontend.

1.  **Install Firebase CLI**:
    ```bash
    npm install -g firebase-tools
    ```

2.  **Login**:
    ```bash
    firebase login
    ```

3.  **Initialize**:
    ```bash
    cd app
    firebase init hosting
    ```
    - Select your Google Cloud project
    - Public directory: `dist`
    - Configure as single-page app: **Yes**
    - Set up automatic builds: **No**

4.  **Build Frontend**:
    Set your backend URL (from Step 4):
    
    **Windows (PowerShell)**:
    ```powershell
    $env:VITE_API_URL="https://smartrecruit-api-xyz-uc.a.run.app"; npm run build
    ```
    
    **Mac/Linux**:
    ```bash
    VITE_API_URL="https://smartrecruit-api-xyz-uc.a.run.app" npm run build
    ```

5.  **Deploy**:
    ```bash
    firebase deploy
    ```

---

## Managing Costs (Free Tier)

Cloud Run Free Tier (Monthly):
- 180,000 vCPU-seconds
- 360,000 GB-seconds (Memory)
- 2 million requests

**With 1GB RAM:**
- You get ~100 hours of active runtime per month for free.
- **Scale to Zero**: Cloud Run automatically stops your container when not used.
- **Cold Starts**: First request after idle takes ~5-10 seconds.

**Tips:**
- Do **not** set "Minimum instances" to 1 (this keeps it running 24/7 and will cost money).
- Keep "Minimum instances" at 0 (default).

## Troubleshooting

**Build Fails**:
- Check `gcloud builds log`
- Ensure `.dockerignore` excludes `venv` and `node_modules` to speed up upload.

**App Crashes**:
- View logs: `gcloud logging read "resource.type=cloud_run_revision" --limit 20`
- Check memory usage. If 1GB isn't enough, try `--memory 2Gi` (reduces free hours to ~50).

