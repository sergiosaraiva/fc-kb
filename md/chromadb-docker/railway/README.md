# Railway Cloud Deployment Guide

This guide explains how to deploy the FC Education Portal (Product Owner RAG) to Railway Cloud.

## Architecture on Railway

```
┌─────────────────────────────────────────────────────────────┐
│                    Railway Project                          │
│                                                             │
│  ┌─────────────────┐         ┌─────────────────────────┐    │
│  │    ChromaDB     │◄───────►│   Product Owner RAG     │    │
│  │    Service      │ private │   (Streamlit Frontend)  │    │
│  │                 │ network │                         │    │
│  │  Port: 8000     │         │   Port: 8501            │    │
│  │  + Volume       │         │   + AWS Credentials     │    │
│  └─────────────────┘         └─────────────────────────┘    │
│         │                              │                    │
│         │                              │                    │
│    (internal)                     (public URL)              │
│  chromadb.railway.internal        *.up.railway.app          │
└─────────────────────────────────────────────────────────────┘
```

## Option 1: Use Railway's ChromaDB Template (Recommended)

### Step 1: Deploy ChromaDB from Template

1. Go to [Railway ChromaDB Template](https://railway.com/template/chromadb)
2. Click "Deploy Now"
3. Configure the environment variables:
   - `IS_PERSISTENT`: `True`
   - `CHROMA_WORKERS`: `1`
4. Note the internal URL: `chromadb.railway.internal:8000`

### Step 2: Deploy the Frontend Service

1. In the same Railway project, click "New Service"
2. Select "GitHub Repo" or "Docker Image"
3. Point to this repository's `railway/frontend` folder
4. Set environment variables (see below)

## Option 2: Deploy Both from This Repository

### Step 1: Create Railway Project

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login
railway login

# Create new project
railway init
```

### Step 2: Deploy ChromaDB Service

```bash
# Link to project
railway link

# Deploy ChromaDB
railway up --service chromadb --dockerfile railway/chromadb/Dockerfile
```

### Step 3: Deploy Frontend Service

```bash
# Deploy Frontend
railway up --service frontend --dockerfile railway/frontend/Dockerfile
```

## Environment Variables

### ChromaDB Service
| Variable | Value | Description |
|----------|-------|-------------|
| `PORT` | `8000` | ChromaDB port |
| `IS_PERSISTENT` | `True` | Enable persistence |
| `CHROMA_HOST_ADDR` | `::` | Listen on all interfaces |
| `ANONYMIZED_TELEMETRY` | `FALSE` | Disable telemetry |
| `CHROMA_SERVER_AUTH_PROVIDER` | `chromadb.auth.token_authn.TokenAuthenticationServerProvider` | Enable token auth |
| `CHROMA_SERVER_AUTH_CREDENTIALS` | `your-secret-token` | Auth token |
| `CHROMA_SERVER_AUTH_TOKEN_TRANSPORT_HEADER` | `X-Chroma-Token` | Auth header |

### Frontend Service
| Variable | Value | Description |
|----------|-------|-------------|
| `PORT` | `8501` | Streamlit port |
| `CHROMADB_HOST` | `chromadb.railway.internal` | Internal DNS name |
| `CHROMADB_PORT` | `8000` | ChromaDB port |
| `CHROMADB_TOKEN` | `${{ chromadb.CHROMA_SERVER_AUTH_CREDENTIALS }}` | Reference ChromaDB token |
| `AWS_ACCESS_KEY_ID` | `your-aws-key` | AWS credentials |
| `AWS_SECRET_ACCESS_KEY` | `your-aws-secret` | AWS credentials |
| `AWS_DEFAULT_REGION` | `us-east-1` | AWS region |

## Volume Configuration

ChromaDB requires persistent storage:

1. In Railway dashboard, click on ChromaDB service
2. Go to "Volumes" tab
3. Click "New Volume"
4. Set mount path: `/chroma/chroma`
5. Click "Create"

## Networking

Railway uses private networking between services:

- **Internal URL**: `chromadb.railway.internal:8000` (only accessible within the project)
- **Public URL**: Generated automatically for the frontend (e.g., `frontend-xxx.up.railway.app`)

The frontend connects to ChromaDB using the internal URL, which:
- Is faster (no internet roundtrip)
- Is more secure (not exposed publicly)
- Has no egress costs

## Data Ingestion

Since ChromaDB on Railway is isolated, you have two options for ingesting data:

### Option A: Temporary Public Access
1. Temporarily expose ChromaDB publicly
2. Run ingestion from your local machine
3. Remove public access after ingestion

### Option B: Railway Shell
```bash
# Connect to frontend service shell
railway shell --service frontend

# Run ingestion script
python ingest-to-chromadb.py
```

### Option C: Include Data in Image
Build the ChromaDB image with pre-loaded data (not recommended for large datasets).

## Cost Estimation

Railway pricing (as of 2024):
- **Hobby Plan**: $5/month includes:
  - 8GB RAM
  - 8 vCPU
  - 100GB bandwidth

Estimated usage for this app:
- ChromaDB: ~512MB RAM
- Frontend: ~256MB RAM
- Storage: ~1GB (knowledge base)

**Estimated cost: $5-10/month**

## Troubleshooting

### Frontend can't connect to ChromaDB
1. Check that both services are in the same project
2. Verify the internal URL: `chromadb.railway.internal`
3. Check ChromaDB logs for auth errors
4. Ensure token matches between services

### ChromaDB data not persisting
1. Verify volume is attached
2. Check mount path is `/chroma/chroma`
3. Look for permission errors in logs

### AWS Bedrock errors
1. Verify AWS credentials are set correctly
2. Check IAM permissions for Bedrock access
3. Ensure region supports Claude models

## Quick Deploy Button

[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/template/YOUR_TEMPLATE_ID)

(Template ID will be available after publishing to Railway)
