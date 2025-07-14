# Deployment Guide for KP SEO Auto Commenter

## Overview

This guide covers deploying the KP SEO Auto Commenter application to Render.com. 

**✨ Important: This application is configured to use Google Cloud Vertex AI to access Gemini models, allowing you to utilize your Google Cloud free credits efficiently.**

## Prerequisites

1. **Render Account**: Create an account at [render.com](https://render.com)
2. **GitHub Repository**: Code should be pushed to GitHub
3. **Google Cloud Project**: 
   - Enable Vertex AI API in your Google Cloud Console
   - Download service account credentials (JSON file)
   - Ensure you have Google Cloud free credits available

## Vertex AI Configuration ✨

This application is optimized to use **Google Cloud Vertex AI** which allows you to:
- ✅ Use your **Google Cloud free credits** (up to $300)
- ✅ Access Gemini 2.5 Pro model via Vertex AI
- ✅ Better rate limits and enterprise features
- ✅ No need for separate Gemini API keys

### Current Vertex AI Settings:
- **Model**: `gemini-2.5-pro`
- **Project**: `kp-seo-blog-automator`
- **Location**: `us-central1`
- **Authentication**: Service Account credentials

## Deployment Steps

### 1. Prepare Service Account Credentials

For Vertex AI authentication:
1. **Place your service account JSON file** in the `credentials/` directory
2. **Name it**: `kp-seo-agent-key.json`
3. **Ensure the file is included** in your Docker build (already configured)

**Note**: No additional API keys needed - Vertex AI uses service account authentication!

### 2. Create Render Service

1. Connect your GitHub repository to Render
2. Create a new **Web Service**
3. Select **Docker** as the runtime
4. Use the provided `render.yaml` for configuration

### 3. Database Setup

The `render.yaml` includes a PostgreSQL database configuration:
- Database name: `kp-seo-db`
- Plan: free
- Region: singapore

### 4. Health Check

The application includes a health check endpoint at `/health` that Render will use to monitor the service.

## Key Configuration Changes Made

### 1. Fixed Configuration Issues
- ✅ Added missing `CHROMA_HOST` and `CHROMA_PORT` to Settings class
- ✅ Added missing `PROJECT_VERSION` to Settings class
- ✅ Pinned numpy to version 1.x for ChromaDB compatibility

### 2. Updated Deployment Configuration
- ✅ Added `GEMINI_API_KEY` and `GOOGLE_API_KEY` to render.yaml
- ✅ Updated Dockerfile to include credentials directory
- ✅ Fixed GCP credentials handling for environment variables

### 3. Dependency Fixes
- ✅ Removed `fastapi-cors` dependency that required Python 3.11+
- ✅ Pinned `numpy<2.0` to avoid ChromaDB compatibility issues

## Troubleshooting

### Common Issues

1. **Port Not Detected**
   - Ensure the `startCommand` in render.yaml uses `$PORT`
   - Current command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

2. **ChromaDB Connection Issues**
   - ChromaDB is not available in production (this is expected)
   - The VectorMemory class gracefully handles ChromaDB unavailability
   - Memory features will be disabled but the app will still work

3. **GCP Credentials Issues**
   - Ensure `GOOGLE_APPLICATION_CREDENTIALS` points to the correct file
   - The credentials file should be included in the Docker build
   - For production, consider using environment variables instead of files

4. **API Key Issues**
   - Verify `GEMINI_API_KEY` and `GOOGLE_API_KEY` are set correctly
   - Check that the Vertex AI API is enabled in your GCP project

### Checking Logs

If deployment fails, check the Render logs for:
- Import errors
- Configuration issues
- Missing environment variables
- Port binding problems

## Local Testing

Before deploying, test locally:

```bash
# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Install dependencies
uv pip install -r requirements.txt

# Test import
python -c "from app.main import app; print('App imports successfully')"

# Test health endpoint
python -c "from app.main import app; from fastapi.testclient import TestClient; client = TestClient(app); response = client.get('/health'); print(f'Health check: {response.status_code}')"
```

## Production Considerations

1. **Memory**: The app works without ChromaDB but memory features are disabled
2. **Scaling**: Current setup is for single instance deployment
3. **Security**: API keys should be stored securely in Render's environment variables
4. **Monitoring**: Use Render's built-in monitoring and the `/health` endpoint

## Next Steps

After successful deployment:
1. Test the application endpoints
2. Verify database connectivity
3. Test the agent functionality
4. Monitor logs for any runtime issues
