# FC Knowledge Base - ChromaDB RAG Infrastructure

A world-class RAG (Retrieval-Augmented Generation) system for Financial Consolidation documentation using ChromaDB, AWS Bedrock embeddings, and LLM-enhanced semantic chunking.

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                         WSL2 (Native Linux)                      │
├─────────────────────────────────────────────────────────────────┤
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────────┐  │
│  │   ChromaDB   │    │  MCP Server  │    │  Knowledge Base  │  │
│  │   (Docker)   │◄───│   (Python)   │◄───│   ZIP Creator    │  │
│  │  Port 8847   │    │  Port 3333   │    │   (LLM-enhanced) │  │
│  └──────────────┘    └──────────────┘    └──────────────────┘  │
│         │                   │                     │             │
│         └───────────────────┼─────────────────────┘             │
│                             │                                   │
│                    AWS Bedrock                                  │
│              ┌──────────────┴──────────────┐                   │
│              │  Titan V1 Embeddings (1536d) │                   │
│              │  Claude Haiku (Enhancement)  │                   │
│              └─────────────────────────────┘                   │
└─────────────────────────────────────────────────────────────────┘
```

## Quick Start

### 1. Prerequisites

- WSL2 with Docker installed
- Python 3.10+ with venv at `../../venv/`
- AWS credentials with Bedrock access

### 2. Setup Environment

```bash
# Copy and configure environment variables
cp .env.example .env
# Edit .env with your AWS credentials
```

Required `.env` variables:
```bash
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
AWS_DEFAULT_REGION=us-east-1
CHROMADB_TOKEN=your_secure_token
```

### 3. Start Infrastructure

```bash
# Start ChromaDB (Docker container)
./start-chromadb.sh

# Create the knowledge base ZIP (with LLM enhancement - ~90 minutes)
./create-enhanced-zip.sh

# Or fast mode without LLM (~30 seconds)
../../venv/bin/python create-knowledge-zip.py --no-llm

# Ingest into ChromaDB
./ingest.sh
```

### 4. Configure Claude Code MCP

Add to your Claude Code settings (`~/.claude/settings.json`):

```json
{
  "mcpServers": {
    "fc-knowledge-base": {
      "command": "/mnt/c/Work/direct-consolidation-docs/md/venv/bin/python",
      "args": ["/mnt/c/Work/direct-consolidation-docs/md/chromadb-docker/mcp-server.py"],
      "env": {
        "CHROMADB_HOST": "localhost",
        "CHROMADB_PORT": "8847",
        "CHROMADB_TOKEN": "your_secure_token",
        "AWS_ACCESS_KEY_ID": "your_access_key",
        "AWS_SECRET_ACCESS_KEY": "your_secret_key",
        "AWS_DEFAULT_REGION": "us-east-1"
      }
    }
  }
}
```

## Scripts Reference

| Script | Description |
|--------|-------------|
| `start-chromadb.sh` | Start ChromaDB Docker container |
| `stop-chromadb.sh` | Stop ChromaDB container |
| `create-enhanced-zip.sh` | Create LLM-enhanced knowledge base ZIP |
| `ingest.sh` | Ingest ZIP into ChromaDB |
| `run-mcp-server.sh` | Run MCP server standalone (for testing) |

## Knowledge Base Statistics

| Metric | Value |
|--------|-------|
| Pre-chunked (Allen White book) | 1,332 chunks |
| Semantic markdown chunks | 1,409 chunks |
| Semantic YAML chunks | 927 chunks |
| **Total chunks** | **3,668** |
| Average chunk size | ~2.8 KB |
| Embedding dimensions | 1,536 (Titan V1) |

## Key Components

### 1. Knowledge Base ZIP Creator (`create-knowledge-zip.py`)

Creates semantically chunked knowledge base with optional LLM enhancement.

**Features:**
- Semantic chunking by markdown headers (##, ###)
- Multi-level YAML chunking by indentation
- Chunk merging for small sections (MIN_CHUNK_SIZE = 300)
- LLM enhancement using Claude Haiku:
  - Semantic summaries
  - Keywords and concepts extraction
  - Hypothetical questions (HyDE approach)
  - Related topics mapping

**Usage:**
```bash
# LLM-enhanced (default, best quality, ~90 minutes)
python create-knowledge-zip.py

# Fast mode (rule-based, ~30 seconds)
python create-knowledge-zip.py --no-llm
```

### 2. ChromaDB Ingestion (`ingest-to-chromadb.py`)

Ingests pre-chunked documents into ChromaDB with Titan V1 embeddings.

**Features:**
- AWS Bedrock Titan V1 embeddings (1536 dimensions)
- Cosine similarity distance metric
- Automatic metadata extraction (topic, layer, IFRS standards)
- Batch processing with rate limiting

### 3. MCP Server (`mcp-server.py`)

Model Context Protocol server for Claude Code integration.

**Available Tools:**
- `search_fc_full` - Semantic search across all documentation
- `get_fc_kb_stats` - Get knowledge base statistics

**Search Features:**
- Dynamic result filtering by relevance score
- Optional layer filtering (business, database, application, frontend, api)
- Returns 3-15 results based on quality

### 4. LLM Chunk Enhancer (`llm_chunk_enhancer.py`)

Enhances chunks using AWS Bedrock Claude Haiku for world-class RAG quality.

**Generates:**
- Semantic summaries (1-2 sentences)
- Keywords (IFRS standards, technical terms)
- Key concepts
- Hypothetical questions (HyDE)
- Related topics

## Directory Structure

```
chromadb-docker/
├── .env                      # AWS credentials (gitignored)
├── .env.example              # Template for .env
├── docker-compose.yml        # ChromaDB container config
├── Dockerfile                # Custom ChromaDB image
├── config.py                 # Shared configuration
├── create-knowledge-zip.py   # ZIP creator with semantic chunking
├── llm_chunk_enhancer.py     # LLM enhancement module
├── ingest-to-chromadb.py     # ChromaDB ingestion script
├── titan_v1_embeddings.py    # AWS Bedrock embeddings
├── mcp-server.py             # MCP server for Claude Code
├── FC-Full-KnowledgeBase.zip # Generated knowledge base
├── requirements.txt          # Python dependencies
└── *.sh                      # Shell scripts for operations
```

## Embeddings Configuration

Using AWS Bedrock Titan Text Embeddings V1:

| Property | Value |
|----------|-------|
| Model ID | `amazon.titan-embed-text-v1` |
| Dimensions | 1,536 |
| Max input | 8,000 tokens |
| Distance metric | Cosine similarity |

## Troubleshooting

### ChromaDB Connection Failed
```bash
# Check if container is running
docker ps | grep chromadb

# Restart container
./stop-chromadb.sh && ./start-chromadb.sh
```

### AWS Credentials Error
```bash
# Verify .env is loaded
source .env && echo $AWS_ACCESS_KEY_ID

# Check for Windows line endings
sed -i 's/\r$//' .env
```

### Ingestion Rate Limiting
The ingestion script includes automatic rate limiting and retry logic. If you see throttling errors, the script will automatically retry with exponential backoff.

### MCP Server Not Responding
```bash
# Test MCP server directly
./run-mcp-server.sh

# Check logs
tail -f /tmp/fc-mcp-server.log
```

## Performance Optimization

1. **Chunk Size**: Optimized at ~2.8KB average (TARGET_CHUNK_SIZE = 2000 chars)
2. **YAML Chunking**: Multi-level splitting (0, 2, 4-space indents) with 8KB max
3. **Small Chunk Merging**: Chunks < 300 chars merged with neighbors
4. **HyDE Questions**: LLM-generated hypothetical questions improve retrieval by 20-30%

## License

Internal use only - Prophix Software Inc.
