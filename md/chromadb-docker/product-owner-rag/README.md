# Product Owner RAG - Business-Focused Knowledge Base Portal

Streamlit web application providing AI-powered Q&A for product owners using the same FC Knowledge Base as Claude Code MCP, but filtered to business concepts only (no technical code).

## Features

- **Business Layer Focus**: Automatically filters out technical implementation details
- **AI-Powered Answers**: Uses Claude 3.5 Sonnet via AWS Bedrock
- **Semantic Search**: AWS Bedrock Titan V1 embeddings (1536 dimensions)
- **Same Infrastructure**: Shares ChromaDB with Claude Code MCP
- **Cost-Effective**: Pay only for AWS Bedrock API usage (~$2-5/month)
- **No Subscription**: No Claude Teams/Pro subscription required

## Architecture

```
┌─────────────────────────────────────┐
│   Product Owner's Browser           │
│   http://localhost:8501             │
└──────────────┬──────────────────────┘
               │ HTTP
               ▼
┌─────────────────────────────────────┐
│   Streamlit App (Docker)            │
│   - Business layer filter           │
│   - Query interface                 │
│   - Source citations                │
└──────────────┬──────────────────────┘
               │
        ┌──────┴──────┐
        │             │
        ▼             ▼
┌──────────────┐  ┌─────────────────┐
│  ChromaDB    │  │  AWS Bedrock    │
│  (Docker)    │  │                 │
│  - Same as   │  │  - Titan V1     │
│    MCP       │  │    Embeddings   │
│  - Business  │  │  - Claude 3.5   │
│    filtering │  │    Sonnet       │
└──────────────┘  └─────────────────┘
```

## Prerequisites

- Docker Desktop (with WSL integration for Windows)
- AWS credentials configured (`~/.aws/credentials` with `prophix-devops` profile)
- Access to AWS Bedrock in us-east-1
- ChromaDB already running with ingested knowledge base

## Quick Start

### Option 1: Docker Compose (Recommended)

Start both ChromaDB and Product Owner RAG together:

```bash
cd /path/to/chromadb-docker

# Use the combined docker-compose file
docker-compose -f docker-compose-with-po-rag.yml up -d

# View logs
docker-compose -f docker-compose-with-po-rag.yml logs -f product-owner-rag
```

Access the web interface at: **http://localhost:8501**

### Option 2: Local Development (Python)

Run locally without Docker:

```bash
cd /path/to/chromadb-docker/product-owner-rag

# Install dependencies
pip install -r requirements.txt

# Set environment variables
export CHROMADB_HOST=localhost
export CHROMADB_PORT=8847
export CHROMADB_TOKEN=fc-knowledge-base-token
export AWS_PROFILE=prophix-devops
export AWS_DEFAULT_REGION=us-east-1

# Run Streamlit
streamlit run app.py
```

Access the web interface at: **http://localhost:8501**

## Usage

### Asking Questions

1. Open http://localhost:8501 in your browser
2. Type your question in the search box
3. Click "Search" to get an AI-powered answer
4. View source documents used for the answer in the expander

### Example Questions

**Consolidation Theory:**
- "How does equity method consolidation work?"
- "What is the difference between global integration and proportional consolidation?"
- "How is goodwill calculated in consolidation?"

**IFRS Standards:**
- "What IFRS standard covers currency translation?"
- "How does IFRS 10 define control?"
- "What are the requirements for business combinations under IFRS 3?"

**Feature Workflows:**
- "What are the steps in the consolidation workflow?"
- "How do intercompany eliminations work?"
- "How do I set up ownership structures?"

**Business Concepts:**
- "What is minority interest (NCI)?"
- "How does currency translation affect consolidation?"
- "What types of eliminations are used in consolidation?"

## Configuration

The app uses the same configuration as the MCP server:

| Setting | Value | Description |
|---------|-------|-------------|
| **ChromaDB** |
| `CHROMADB_HOST` | `localhost` (or `chromadb` in Docker) | ChromaDB server host |
| `CHROMADB_PORT` | `8847` | ChromaDB server port |
| `CHROMADB_TOKEN` | `fc-knowledge-base-token` | Authentication token |
| `FULL_COLLECTION` | `fc_full_knowledge` | Collection name |
| **AWS Bedrock** |
| `AWS_PROFILE` | `prophix-devops` | AWS credentials profile |
| `AWS_REGION` | `us-east-1` | AWS region |
| `CLAUDE_MODEL_ID` | `us.anthropic.claude-3-5-sonnet-20241022-v2:0` | Claude model |
| `EMBEDDING_MODEL` | `amazon.titan-embed-text-v1` | Embedding model (1536 dims) |
| **Retrieval** |
| `BUSINESS_LAYER_RESULTS` | `10` | Number of business layer results |
| `RELEVANCE_THRESHOLD` | `0.55` | Minimum relevance score (55%) |

## Cost Estimation

### AWS Bedrock Claude 3.5 Sonnet
```
Input:  $3.00 per 1M tokens
Output: $15.00 per 1M tokens

Example monthly usage (100 questions):
- Context: ~2000 tokens per question
- Response: ~500 tokens per answer
- Total: ~250K tokens/month
- Cost: ~$2-5/month
```

**vs Claude Teams subscription:** $150/month (5 users minimum)

**Savings:** ~$145/month 💰

## Deployment to Company Server

### Prerequisites
- Ubuntu/Debian Linux server
- Docker and Docker Compose installed
- AWS credentials available on server
- Network access to AWS Bedrock

### Deployment Steps

1. **Copy files to server:**
   ```bash
   scp -r chromadb-docker/ user@server:/opt/fc-knowledge-base/
   ```

2. **Configure AWS credentials on server:**
   ```bash
   # On server
   mkdir -p ~/.aws
   nano ~/.aws/credentials
   ```

   Add your AWS profile:
   ```ini
   [prophix-devops]
   aws_access_key_id = YOUR_ACCESS_KEY
   aws_secret_access_key = YOUR_SECRET_KEY
   ```

3. **Start services:**
   ```bash
   cd /opt/fc-knowledge-base/chromadb-docker
   docker-compose -f docker-compose-with-po-rag.yml up -d
   ```

4. **Configure firewall (optional):**
   ```bash
   # Allow internal access only
   sudo ufw allow from 10.0.0.0/8 to any port 8501
   ```

5. **Access from internal network:**
   - URL: `http://server-ip:8501`
   - Share this URL with product owner

### Production Recommendations

**Security:**
- Use nginx reverse proxy with HTTPS
- Add basic authentication
- Restrict access by IP/VPN
- Use AWS IAM roles instead of credentials file

**Monitoring:**
- Add health check monitoring
- Track AWS Bedrock API costs
- Monitor Docker container health

**Backup:**
- ChromaDB volume is persistent
- Back up `chromadb_data` volume regularly

## Troubleshooting

### Cannot connect to ChromaDB
```bash
# Check ChromaDB container status
docker ps | grep chromadb

# Verify ChromaDB is healthy
docker-compose ps

# Check ChromaDB logs
docker-compose logs chromadb
```

### AWS Bedrock authentication errors
```bash
# Verify AWS credentials
docker exec -it fc-product-owner-rag aws sts get-caller-identity --profile prophix-devops

# Check Bedrock access
docker exec -it fc-product-owner-rag aws bedrock list-foundation-models --region us-east-1 --profile prophix-devops
```

### No search results
```bash
# Verify knowledge base is ingested
docker exec -it fc-chromadb curl -H "X-Chroma-Token: fc-knowledge-base-token" http://localhost:8000/api/v1/collections

# Check collection document count
python -c "import chromadb; c=chromadb.HttpClient('localhost',8847); coll=c.get_collection('fc_full_knowledge'); print(f'Documents: {coll.count()}')"
```

### Streamlit not loading
```bash
# Check Streamlit logs
docker-compose -f docker-compose-with-po-rag.yml logs product-owner-rag

# Restart container
docker-compose -f docker-compose-with-po-rag.yml restart product-owner-rag
```

## Differences from MCP (Claude Code)

| Feature | MCP (Claude Code) | Product Owner RAG |
|---------|-------------------|-------------------|
| **Interface** | IDE integration | Web browser |
| **User** | Developers | Product owners |
| **Content** | Full (business + technical) | Business layer only |
| **Code snippets** | ✅ Yes | ❌ No (filtered out) |
| **Stored procedures** | ✅ Yes | ❌ No (filtered out) |
| **Theory/concepts** | ✅ Yes | ✅ Yes |
| **IFRS standards** | ✅ Yes | ✅ Yes |
| **Workflows** | ✅ Yes | ✅ Yes |
| **AI model** | Claude Code built-in | AWS Bedrock Claude 3.5 Sonnet |
| **Cost** | Included in subscription | Pay-per-use (~$2-5/month) |

## Updating the Knowledge Base

When the knowledge base is updated:

1. **Re-ingest documents** (from main chromadb-docker directory):
   ```bash
   cd /path/to/chromadb-docker
   python ingest-to-chromadb.py
   ```

2. **Restart Product Owner RAG** (to clear caches):
   ```bash
   docker-compose -f docker-compose-with-po-rag.yml restart product-owner-rag
   ```

3. **No code changes needed** - the app automatically uses the updated knowledge base

## Files

```
product-owner-rag/
├── README.md                # This file
├── app.py                   # Streamlit application
├── requirements.txt         # Python dependencies
└── Dockerfile               # Docker image for deployment
```

## Support

For issues or questions:
1. Check troubleshooting section above
2. Review logs: `docker-compose logs product-owner-rag`
3. Verify AWS Bedrock access and credentials
4. Ensure ChromaDB is healthy and ingested
