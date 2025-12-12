# Product Owner RAG Setup Guide

## Executive Summary

You now have a **dual-access RAG system** that provides:

1. **Claude Code MCP** (for developers) - Full technical + business content
2. **Product Owner Portal** (web-based) - Business content only, filtered to remove code

**Key Benefits:**
- ✅ No Claude Teams subscription required ($150/month saved)
- ✅ Uses your existing AWS Bedrock credentials
- ✅ Same ChromaDB infrastructure (no duplication)
- ✅ Pay-per-use pricing (~$2-5/month for 100 questions)
- ✅ Business layer filtering (no technical code noise)

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│              FC Knowledge Base (ChromaDB Docker)                 │
│                   fc_full_knowledge collection                   │
│                      5,400+ documents                             │
└────────────┬──────────────────────────┬─────────────────────────┘
             │                          │
             ▼                          ▼
┌──────────────────────────┐  ┌──────────────────────────────────┐
│   MCP Server (stdio)     │  │   Product Owner RAG (Web)        │
│                          │  │                                  │
│   Users: Developers      │  │   Users: Product Owners          │
│   Interface: Claude Code │  │   Interface: Web Browser         │
│   Content: Full          │  │   Content: Business layer only   │
│   Filters: All layers    │  │   Filters: layer="business"      │
│                          │  │                                  │
│   Tools:                 │  │   Features:                      │
│   - search_fc_full       │  │   - AI Q&A (Claude 3.5)          │
│   - get_fc_kb_stats      │  │   - Source citations             │
│   - layer_filter option  │  │   - Example questions            │
│                          │  │   - No code snippets             │
└──────────────────────────┘  └──────────────────────────────────┘
             │                          │
             └──────────┬───────────────┘
                        ▼
              ┌─────────────────────┐
              │   AWS Bedrock       │
              │   (prophix-devops)  │
              │                     │
              │   - Titan V1        │
              │     Embeddings      │
              │     (1536 dims)     │
              │                     │
              │   - Claude 3.5      │
              │     Sonnet          │
              │     (for PO RAG)    │
              └─────────────────────┘
```

---

## Quick Start

### 1. Test Your Current MCP Setup (Verify Everything Works)

```bash
# Ensure ChromaDB is running
cd /mnt/c/Work/Prophix.Conso.2026.1/docs/DC/md/chromadb-docker
docker ps | grep chromadb

# If not running, start it
docker-compose up -d
```

Open Claude Code and test the MCP:
```
Search the FC knowledge base for: "How is goodwill calculated?"
```

If this works, you're ready to deploy the Product Owner portal!

### 2. Start Product Owner RAG

```bash
cd /mnt/c/Work/Prophix.Conso.2026.1/docs/DC/md/chromadb-docker

# Start both ChromaDB and Product Owner RAG
./start-po-rag.sh
```

### 3. Access the Portal

Open your browser and navigate to:
**http://localhost:8501**

Try asking: "How does equity method consolidation work?"

### 4. Stop Services (when done)

```bash
./stop-po-rag.sh
```

---

## What Was Created

### New Files

```
docs/DC/md/chromadb-docker/
├── product-owner-rag/
│   ├── README.md               # Comprehensive documentation
│   ├── app.py                  # Streamlit application
│   ├── requirements.txt        # Python dependencies
│   └── Dockerfile              # Docker image
├── docker-compose-with-po-rag.yml  # Combined deployment
├── start-po-rag.sh             # Start script
├── stop-po-rag.sh              # Stop script
└── PRODUCT-OWNER-RAG-SETUP.md  # This file
```

### Architecture Changes

**Before:**
```
ChromaDB Docker → MCP Server → Claude Code (developers only)
```

**After:**
```
                    ┌→ MCP Server → Claude Code (developers)
ChromaDB Docker ────┤
                    └→ Product Owner RAG → Web UI (product owners)
```

---

## How It Works

### Business Layer Filtering

The Product Owner RAG automatically filters content:

**Included (Business Layer):**
- ✅ Allen White's Direct Consolidation theory
- ✅ IFRS/IAS standards and interpretations
- ✅ Consolidation methods (equity, global integration, proportional)
- ✅ Business rules and workflows
- ✅ Feature descriptions and usage guides
- ✅ Currency translation concepts
- ✅ Ownership structure handling

**Excluded (Technical Layers):**
- ❌ C# code snippets
- ❌ SQL stored procedures
- ❌ TypeScript implementations
- ❌ Database schema details
- ❌ API handler signatures
- ❌ Technical troubleshooting

### Query Process

1. **User asks question** in web interface
2. **Generate embedding** using AWS Bedrock Titan V1
3. **Search ChromaDB** with `layer="business"` filter
4. **Retrieve top 10 results** above 55% relevance threshold
5. **Build context** from top 5 results
6. **Call Claude 3.5 Sonnet** via AWS Bedrock to generate answer
7. **Display answer** with source citations

---

## Cost Analysis

### AWS Bedrock Pricing (Pay-per-use)

**Claude 3.5 Sonnet:**
- Input: $3.00 per 1M tokens
- Output: $15.00 per 1M tokens

**Titan V1 Embeddings:**
- $0.10 per 1M tokens (negligible)

**Example Monthly Cost:**

| Usage | Questions/Month | Tokens/Month | Cost/Month |
|-------|----------------|--------------|------------|
| Light | 50 | ~125K | $1-3 |
| Medium | 100 | ~250K | $2-5 |
| Heavy | 500 | ~1.25M | $10-25 |

**vs Claude Teams:** $150/month (minimum 5 users)

**Savings:** $125-145/month 💰

---

## Deployment to Company Server

### Option 1: Internal Server (Recommended)

Deploy on company's internal server for product owner access:

```bash
# 1. Copy files to server
scp -r chromadb-docker/ user@company-server:/opt/fc-knowledge-base/

# 2. On server, configure AWS credentials
ssh user@company-server
mkdir -p ~/.aws
nano ~/.aws/credentials
# Add [prophix-devops] profile

# 3. Start services
cd /opt/fc-knowledge-base/chromadb-docker
./start-po-rag.sh

# 4. Access from internal network
# URL: http://company-server-ip:8501
```

**Share this URL with your product owner.**

### Option 2: Cloud Deployment (AWS/Azure)

Deploy on cloud VM with restricted access:

1. Provision Ubuntu VM (t3.medium or similar)
2. Install Docker and Docker Compose
3. Copy files and start services
4. Configure security groups (allow 8501 from office IP only)
5. Optional: Add nginx with HTTPS and authentication

### Option 3: Local Access Only

Product owner connects to your local machine:

1. Start services on your machine: `./start-po-rag.sh`
2. Find your local IP: `hostname -I`
3. Share URL: `http://your-local-ip:8501`
4. Firewall: Allow port 8501 from product owner's IP

---

## Usage Guide for Product Owner

### Example Questions

**Consolidation Theory:**
```
- How does equity method consolidation work?
- What is the difference between global integration and proportional consolidation?
- How is goodwill calculated in direct consolidation?
- What is minority interest (NCI) and how is it handled?
```

**IFRS Standards:**
```
- What IFRS standard covers currency translation?
- How does IFRS 10 define control over subsidiaries?
- What are the requirements for business combinations under IFRS 3?
- How does IAS 21 handle exchange rate differences?
```

**Workflows:**
```
- What are the steps in the consolidation workflow?
- How do I set up intercompany eliminations?
- How do ownership structures work in the system?
- What types of adjustments can be made during consolidation?
```

**Business Rules:**
```
- How are intercompany transactions eliminated?
- What are the rules for currency translation?
- How does the system calculate ownership percentages?
- What happens when ownership changes during the period?
```

### Tips for Best Results

1. **Be specific** - "How does equity method work?" vs "Tell me about consolidation"
2. **Use proper terms** - Use IFRS terminology when applicable
3. **Check sources** - Expand the "View Sources" section to see where info came from
4. **Iterate** - Ask follow-up questions to drill deeper

---

## Troubleshooting

### Cannot access http://localhost:8501

**Solution:**
```bash
# Check if container is running
docker ps | grep product-owner-rag

# If not running, start it
./start-po-rag.sh

# Check logs for errors
docker-compose -f docker-compose-with-po-rag.yml logs product-owner-rag
```

### "No results found in knowledge base"

**Solution:**
```bash
# Verify ChromaDB has data
python -c "import chromadb; c=chromadb.HttpClient('localhost',8847); coll=c.get_collection('fc_full_knowledge'); print(f'Documents: {coll.count()}')"

# If 0 documents, re-ingest
python ingest-to-chromadb.py
```

### AWS Bedrock authentication errors

**Solution:**
```bash
# Verify AWS credentials
docker exec -it fc-product-owner-rag aws sts get-caller-identity --profile prophix-devops

# If fails, check ~/.aws/credentials file
cat ~/.aws/credentials
```

### "Error generating response"

**Solution:**
```bash
# Check if Claude model is accessible
aws bedrock list-foundation-models --region us-east-1 --profile prophix-devops | grep -A5 "claude-3-5-sonnet"

# Verify Bedrock permissions in IAM
```

---

## Comparison: MCP vs Product Owner RAG

| Feature | MCP (Developers) | Product Owner RAG |
|---------|------------------|-------------------|
| **Interface** | Claude Code IDE | Web Browser |
| **Authentication** | None (local) | Optional (can add) |
| **Content** | Full (all layers) | Business layer only |
| **Code snippets** | ✅ Yes | ❌ No |
| **Database schemas** | ✅ Yes | ❌ No |
| **Business theory** | ✅ Yes | ✅ Yes |
| **IFRS standards** | ✅ Yes | ✅ Yes |
| **Workflows** | ✅ Yes | ✅ Yes |
| **AI responses** | Claude Code built-in | Claude 3.5 Sonnet |
| **Cost** | Included | ~$2-5/month |
| **Sharing** | Cannot share | Share URL |

---

## Next Steps

1. **Test locally** - Start services and test at http://localhost:8501
2. **Gather feedback** - Share with product owner and iterate
3. **Deploy to server** - Move to company server for permanent access
4. **Add authentication** - Optional: Add nginx reverse proxy with basic auth
5. **Monitor costs** - Track AWS Bedrock usage in first month
6. **Expand access** - Share URL with other non-technical stakeholders

---

## Maintenance

### Updating Knowledge Base

When you add new documentation:

```bash
# 1. Re-ingest documents (in main chromadb-docker directory)
cd /mnt/c/Work/Prophix.Conso.2026.1/docs/DC/md/chromadb-docker
python ingest-to-chromadb.py

# 2. Restart Product Owner RAG (clears caches)
docker-compose -f docker-compose-with-po-rag.yml restart product-owner-rag
```

### Monitoring Costs

Check AWS Bedrock usage:
```bash
# View Bedrock invocations (last 7 days)
aws cloudwatch get-metric-statistics \
  --namespace AWS/Bedrock \
  --metric-name Invocations \
  --dimensions Name=ModelId,Value=us.anthropic.claude-3-5-sonnet-20241022-v2:0 \
  --start-time $(date -u -d '7 days ago' +%Y-%m-%dT%H:%M:%S) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
  --period 86400 \
  --statistics Sum \
  --profile prophix-devops
```

---

## Support

For questions or issues:

1. **Documentation:** See `product-owner-rag/README.md`
2. **Logs:** `docker-compose -f docker-compose-with-po-rag.yml logs product-owner-rag`
3. **Health check:** http://localhost:8501/_stcore/health
4. **ChromaDB status:** `docker ps | grep chromadb`

---

## Summary

✅ **Created:** Streamlit web app for product owner Q&A
✅ **Reuses:** Your existing ChromaDB and AWS Bedrock infrastructure
✅ **Filters:** Business layer only (no technical code)
✅ **Cost:** ~$2-5/month (vs $150/month for Claude Teams)
✅ **Access:** Web browser (no Claude subscription needed)

**To start:** `./start-po-rag.sh`
**To access:** http://localhost:8501

**Next:** Deploy to company server and share URL with product owner! 🚀
