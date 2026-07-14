# GarutVON v2 — Deployment Guide

This document describes how to deploy **GarutVON v2** to production servers, specifically utilizing **Vercel** for the static frontend assets and **Railway / Render** for the Python API services.

## Architecture

To satisfy premium SaaS standards, the application features a decoupled architecture:
1. **Frontend (`frontend/`):** Deployed as a ultra-fast static website on **Vercel**. All form operations and data requests communicate with the dynamic Python backend.
2. **Backend Engine (`backend/`):** Runs Gunicorn/Uvicorn workers on **Railway** or **Render**.
3. **Database:** Powered by a high-performance **Neon PostgreSQL** server.
4. **Emails:** Transferred securely via **Mailjet**.

---

## 1. Frontend Deployment (Vercel)

Vercel hosts the responsive, interactive 3D frontend. 

### Step 1: Create a `vercel.json`
Define static routing rules and API proxies to prevent CORS blocks:
```json
{
  "version": 2,
  "public": true,
  "cleanUrls": true,
  "rewrites": [
    {
      "source": "/api/(.*)",
      "destination": "https://your-backend-server.railway.app/api/$1"
    },
    {
      "source": "/(.*)",
      "destination": "/$1"
    }
  ]
}
```

### Step 2: Deploy
1. Push your code to GitHub.
2. Link your repository in the Vercel Dashboard.
3. Configure the root directory to point to `frontend/` (or leave as root and use rewrites).
4. Click **Deploy**.

---

## 2. Backend Deployment (Railway / Render)

The backend runs both Flask and FastAPI processes.

### Step 1: Create a `Dockerfile`
Deploying via Docker guarantees package consistency across clusters:
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system utilities for Pillow image manipulations
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000
EXPOSE 8000

# Start Flask on port 5000 and FastAPI on port 8000 using run.py
CMD ["python", "run.py"]
```

### Step 2: Push to Railway / Render
1. Create a new service on Railway/Render connected to your GitHub repository.
2. Configure environment variables (see `.env.example`).
3. Deploy! Railway will read the Dockerfile or launch `python run.py` automatically.

---

## 3. Database Deployment (Neon PostgreSQL)

1. Create a free PostgreSQL cluster on [Neon.tech](https://neon.tech).
2. Copy your Connection String:
   ```env
   DATABASE_URL=postgresql://your_user:your_password@ep-cool-breeze.us-east-2.aws.neon.tech/neondb?sslmode=require
   ```
3. Pass this URL to your Backend Service environment variables. SQLAlchemy ORM automatically handles table schemas creation and seeding on startup.
