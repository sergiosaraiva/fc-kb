# FC Knowledge Base

Financial Consolidation Knowledge Base for Claude Code MCP integration.

## Quick Start

### Prerequisites

- **Docker Desktop** with WSL2 backend (Windows) or Docker Engine (Linux/Mac)
- **Python 3.10+**
- **AWS credentials** with access to Bedrock in us-east-1

### Setup (One-Time)

```bash
# 1. Clone the repository
git clone https://github.com/sergiosaraiva/fc-kb.git
cd fc-kb

# 2. Run setup script
chmod +x setup.sh
./setup.sh

# 3. Configure AWS credentials (needed for ingest + search queries)

# Option A: Edit .env file (used by ingest.sh and app)
nano md/chromadb-docker/.env
# Fill in AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY

# Option B: Use AWS CLI profile (used by MCP server)
aws configure --profile prophix-devops
# Region: us-east-1

# 4. Start ChromaDB
cd md/chromadb-docker
./start-chromadb.sh

# 5. Ingest knowledge base (one-time, takes a few minutes)
./ingest.sh

# 6. Start Claude Code in the project directory
cd ../..
claude
```

### Daily Usage

```bash
# Start ChromaDB before using Claude Code
cd md/chromadb-docker
./start-chromadb.sh

# When done, stop ChromaDB
./stop-chromadb.sh
```

## Available Scripts

All scripts are in `md/chromadb-docker/`:

| Script | Description |
|--------|-------------|
| `start-chromadb.sh` | Start ChromaDB container |
| `stop-chromadb.sh` | Stop ChromaDB container |
| `ingest.sh` | Populate knowledge base (one-time) |
| `start-po-rag.sh` | Start ChromaDB + Web UI (optional) |
| `stop-po-rag.sh` | Stop ChromaDB + Web UI |

## Using the MCP Server

Once configured, Claude Code provides the `search_fc_full` tool:

```
Search for:
- Consolidation methods (global integration, equity method)
- IFRS standards (IFRS 3, IFRS 10, IAS 21)
- Database procedures (P_CONSO_*, P_CALC_*)
- Application patterns and code examples
```

Example queries:
- "How does equity method consolidation work?"
- "What is the P_CONSO_CALCULATE procedure?"
- "Explain IAS 21 currency translation"

## Architecture

```
ChromaDB (Docker) <-> MCP Server <-> Claude Code
     |
     v
AWS Bedrock Titan V1 (embeddings)
```

- **ChromaDB**: Vector database on port 8847
- **AWS Bedrock Titan V1**: 1536-dimension embeddings
- **MCP Server**: Claude Code integration via `.mcp.json`

### Why AWS Credentials Are Required

AWS Bedrock Titan V1 generates embeddings (1536-dimensional vectors) for semantic search. Credentials are needed in **two places**:

| Component | When | Purpose |
|-----------|------|---------|
| **Ingest script** | One-time setup | Convert 1,500+ documents into vectors |
| **App / MCP Server** | Every search query | Convert your query into a vector to find matches |

The app calls AWS Bedrock on every search to embed the query text. Cost is minimal (~$0.0001 per 1K tokens).

## Troubleshooting

### MCP server shows "failed" status

1. Ensure ChromaDB is running:
   ```bash
   docker ps | grep chromadb
   ```

2. Test ChromaDB health:
   ```bash
   curl http://localhost:8847/api/v2/heartbeat
   ```

3. Verify AWS credentials:
   ```bash
   aws sts get-caller-identity --profile prophix-devops
   ```

4. Check Python venv exists:
   ```bash
   ls venv/bin/python
   ```

### Ingestion fails

1. Ensure `FC-Full-KnowledgeBase.zip` exists:
   ```bash
   ls md/chromadb-docker/FC-Full-KnowledgeBase.zip
   ```

2. Check `.env` file has valid AWS credentials

3. Verify Bedrock access in us-east-1 region

### Docker not running (WSL)

```bash
sudo service docker start
```

## Project Structure

```
fc-kb/
├── setup.sh                          # One-time setup script
├── .mcp.json                         # Claude Code MCP config (auto-generated)
├── venv/                             # Python virtual environment
└── md/
    ├── chromadb-docker/              # MCP server and Docker setup
    │   ├── start-chromadb.sh         # Start database
    │   ├── stop-chromadb.sh          # Stop database
    │   ├── ingest.sh                 # Populate knowledge base
    │   ├── mcp-server.py             # MCP server for Claude Code
    │   ├── .env                      # AWS credentials (not in git)
    │   └── FC-Full-KnowledgeBase.zip # Pre-packaged content
    ├── direct_consolidation_chunks/  # 1,333 theory chunks
    └── documentation-library/        # 169 documentation files
```

## Knowledge Base Contents

- **1,333 theory chunks** from Allen White's "Direct Consolidation" book
- **169 documentation files** covering database, application, and frontend layers
- **IFRS standards**: IFRS 3, IFRS 10, IFRS 11, IAS 21, IAS 27, IAS 28, IAS 29, IAS 36
- **65 stored procedures** (P_CONSO_*, P_CALC_*, P_SYS_*)
- **120+ database tables** documented
- **525 API handlers** indexed
