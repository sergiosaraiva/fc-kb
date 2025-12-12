# FC Knowledge Base - ChromaDB with AWS Bedrock Embeddings

ChromaDB-based RAG system for Financial Consolidation knowledge, integrated with Claude Code via MCP. Uses **AWS Bedrock Cohere Embed v4** (1536 dimensions) for best-in-class semantic search.

## Overview

This setup provides:
- **ChromaDB** running in Docker for vector storage
- **AWS Bedrock Cohere Embed v4** (1536 dimensions) for best-in-class semantic search
- **Dynamic relevance-based retrieval** - returns 3-15 results based on quality, not fixed count
- **Single unified collection**: `fc_full_knowledge` with 5,400+ documents
- **MCP integration** for Claude Code semantic queries

## Prerequisites

- Docker Desktop (with WSL integration enabled)
- Python 3.10+
- AWS credentials configured (`~/.aws/credentials` with `prophix-devops` profile)
- Access to AWS Bedrock in us-east-1

## Quick Start

### 1. Start ChromaDB Docker

```bash
cd docs/DC/md/chromadb-docker
chmod +x *.sh
./start-chromadb.sh
```

### 2. Create Knowledge Base ZIP Files

```bash
./create-knowledge-zips.sh
```

This creates:
- `FC-Business-KnowledgeBase.zip` - Theory + user help (non-technical)
- `FC-Full-KnowledgeBase.zip` - Business + technical implementation

### 3. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 4. Ingest Documents into ChromaDB

```bash
python ingest-to-chromadb.py
```

This will:
1. Connect to ChromaDB Docker container
2. Extract documents from ZIP files
3. Generate Cohere Embed v4 embeddings (1536 dimensions)
4. Store in ChromaDB collection with metadata for filtering

### 5. Configure Claude Code MCP

Add to your project's `.mcp.json`:

```json
{
  "mcpServers": {
    "fc-knowledge-base": {
      "command": "python",
      "args": ["docs/DC/md/chromadb-docker/mcp-server.py"],
      "env": {
        "AWS_PROFILE": "prophix-devops",
        "AWS_DEFAULT_REGION": "us-east-1"
      }
    }
  }
}
```

### 6. Restart Claude Code

After configuration, restart Claude Code to load the MCP server.

## Available Tools in Claude Code

### `search_fc_full`

Search the unified FC knowledge base (5,400+ documents) with dynamic relevance-based retrieval.

**Use for:**
- Consolidation concepts (equity method, global integration, proportional)
- IFRS/IAS standards (IFRS 3, IFRS 10, IAS 21, etc.)
- Allen White's Direct Consolidation theory
- Database schemas (TS*, TD*, TM_*)
- Stored procedures (P_CONSO_*, P_CALC_*, P_SYS_*)
- C# service implementations
- TypeScript/Frontend patterns
- API handlers and message handlers

**Parameters:**
- `query` (required): Search text
- `layer_filter` (optional): Filter by layer
  - `business`, `database`, `application`, `frontend`, `api`

**Dynamic Result Count:**
- Fetches 25 candidates, filters by 55% relevance threshold
- Returns 3-15 results based on quality (not fixed)
- Results tagged as HIGH (≥75%), GOOD (≥55%), or LOW

### `get_fc_kb_stats`

Get document counts and collection statistics.

## Example Queries in Claude Code

**Business queries:**
```
"How does equity method consolidation work according to IFRS?"
"What are the steps to set up intercompany eliminations?"
"How is goodwill calculated in direct consolidation?"
"What IFRS standard covers currency translation?"
```

**Technical queries:**
```
"What stored procedures handle ownership calculation?"
"Show me the database schema for consolidation adjustments"
"How does the ConsolidationService.cs process eliminations?"
"What API handlers are available for currency translation?"
```

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        Claude Code                               │
│                                                                  │
│  ┌──────────────────┐                                           │
│  │   MCP Client     │                                           │
│  └────────┬─────────┘                                           │
└───────────┼──────────────────────────────────────────────────────┘
            │ MCP Protocol (stdio)
            ▼
┌─────────────────────────────────────────────────────────────────┐
│                    mcp-server.py                                 │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │        search_fc_full        │      get_fc_kb_stats         ││
│  └─────────────────────────────────────────────────────────────┘│
│            │                                                     │
│            ▼                                                     │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │         Dynamic Relevance-Based Retrieval                    ││
│  │    (fetch 25 → filter by 55% threshold → return 3-15)       ││
│  └─────────────────────────────────────────────────────────────┘│
│            │                                                     │
│            ▼                                                     │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │              Cohere Embedding Function                       ││
│  │            (Cohere Embed v4 via AWS Bedrock)                 ││
│  │           1536 dimensions, best-in-class quality             ││
│  └─────────────────────────────────────────────────────────────┘│
└───────────┼──────────────────────────────────────────────────────┘
            │ HTTP + Auth Token
            ▼
┌─────────────────────────────────────────────────────────────────┐
│                ChromaDB Docker Container                         │
│                    (localhost:8847)                              │
│         ┌─────────────────────────────────────┐                 │
│         │        fc_full_knowledge            │                 │
│         │      (5,400+ documents unified)     │                 │
│         └─────────────────────────────────────┘                 │
│                                                                  │
│               Docker Volume: chromadb_data                       │
└─────────────────────────────────────────────────────────────────┘
            ▲
            │ Bedrock API (HTTPS)
            ▼
┌─────────────────────────────────────────────────────────────────┐
│                 AWS Bedrock (us-east-1)                          │
│                  cohere.embed-v4:0                               │
│                 (via prophix-devops profile)                     │
└─────────────────────────────────────────────────────────────────┘
```

## Why Cohere Embed v4?

The default ChromaDB embeddings (all-MiniLM-L6-v2) are limited:
- 384 dimensions
- General-purpose training

**Cohere Embed v4** provides:
- **1536 dimensions** - richest semantic representation available
- **8K token context** - can embed longer documents
- **Multimodal support** - text and images
- **State-of-the-art retrieval** - trained specifically for search tasks
- **Separate query vs document embeddings** - optimized for retrieval asymmetry

This results in significantly better semantic search accuracy compared to both default embeddings and Titan v2 (1024 dimensions).

## Files

```
chromadb-docker/
├── README.md                  # This file
├── Dockerfile                 # ChromaDB Docker image
├── docker-compose.yml         # Docker Compose configuration
├── start-chromadb.sh          # Start Docker container
├── stop-chromadb.sh           # Stop Docker container
├── create-knowledge-zips.sh   # Create ZIP files from docs
├── requirements.txt           # Python dependencies
├── config.py                  # Configuration settings (embedding model, retrieval params)
├── cohere_embeddings.py       # Cohere Embed v4 embedding function (1536 dims)
├── bedrock_embeddings.py      # [Legacy] Titan embedding function (1024 dims)
├── ingest-to-chromadb.py      # Document ingestion script
├── mcp-server.py              # MCP server for Claude Code
└── mcp-config.json            # MCP configuration example
```

## Troubleshooting

### Docker not starting
```bash
# Check Docker status
docker info

# If not running, start Docker Desktop
```

### ChromaDB connection refused
```bash
# Check container status
docker-compose ps

# View logs
docker-compose logs -f
```

### Bedrock authentication errors
```bash
# Verify AWS credentials
aws sts get-caller-identity --profile prophix-devops

# Check Bedrock access
aws bedrock list-foundation-models --profile prophix-devops --region us-east-1
```

### No search results
```bash
# Verify collections were created
python -c "import chromadb; c=chromadb.HttpClient('localhost',8847); print([col.name for col in c.list_collections()])"

# Re-run ingestion
python ingest-to-chromadb.py
```

### Using fallback embeddings
If Bedrock is unavailable, the system will fall back to sentence-transformers:
```bash
python ingest-to-chromadb.py --use-fallback
```

## Updating Knowledge Base

After adding new documentation:

1. Re-create ZIP files:
   ```bash
   ./create-knowledge-zips.sh
   ```

2. Re-ingest (replaces existing data):
   ```bash
   python ingest-to-chromadb.py
   ```

3. Restart Claude Code to refresh MCP connection

## Re-Ingestion Required

**Important:** Re-ingestion is required when:
- Changing embedding models (e.g., Titan → Cohere)
- Changing embedding dimensions
- Adding/updating documentation content
- Modifying chunking strategy

**Re-ingestion process:**
```bash
# 1. Ensure ChromaDB is running
./start-chromadb.sh

# 2. Re-create the knowledge base ZIP
./create-knowledge-zips.sh

# 3. Re-ingest (this DELETES existing collection and re-creates with new embeddings)
python ingest-to-chromadb.py

# 4. Verify document count
python -c "import chromadb; c=chromadb.HttpClient('localhost',8847); coll=c.get_collection('fc_full_knowledge'); print(f'Documents: {coll.count()}')"

# 5. Restart Claude Code (or reload MCP servers)
```

**Time estimate:** ~10-15 minutes for 5,400+ documents (rate-limited by Bedrock API)

## Configuration Reference

Key settings in `config.py`:

| Setting | Value | Description |
|---------|-------|-------------|
| `BEDROCK_EMBEDDING_MODEL` | `cohere.embed-v4:0` | AWS Bedrock model ID |
| `EMBEDDING_DIMENSIONS` | `1536` | Vector dimensions (max for Cohere v4) |
| `RETRIEVAL_CANDIDATE_COUNT` | `25` | Fetch this many candidates |
| `RETRIEVAL_MIN_RESULTS` | `3` | Always return at least this many |
| `RETRIEVAL_MAX_RESULTS` | `15` | Never return more than this |
| `RELEVANCE_THRESHOLD` | `0.55` | Minimum relevance (55%) to include |
