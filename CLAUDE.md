# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a knowledge base for building AI agents and RAG systems for financial consolidation in Prophix.Conso. It maps Allen White's "Direct Consolidation" theoretical framework to the actual implementation.

The repository contains:
- 1,333 theory chunks from "Direct Consolidation" book
- 169 documentation files covering database, application, and frontend layers
- Two pre-packaged RAG knowledge bases (Business and Technical)
- MCP server implementations for Claude Code integration

## Development Commands

### RAG MCP Server (Basic - Local Embeddings)

```bash
cd md/rag-mcp-server

# Setup
python -m venv venv
source venv/bin/activate  # Linux/Mac
pip install -r requirements.txt

# Ingest documents into ChromaDB
python ingest.py

# Server runs via MCP protocol (configured in .mcp.json)
```

### ChromaDB Docker Setup (Advanced - AWS Bedrock Embeddings)

```bash
cd md/chromadb-docker

# Start ChromaDB container
./start-chromadb.sh

# Create knowledge base ZIP files
./create-knowledge-zips.sh

# Install dependencies
pip install -r requirements.txt

# Ingest documents (uses Cohere Embed v4 via AWS Bedrock)
python ingest-to-chromadb.py

# Stop container
./stop-chromadb.sh
```

**Prerequisites for Docker setup:**
- Docker Desktop with WSL integration
- AWS credentials (`~/.aws/credentials` with `prophix-devops` profile)
- Access to AWS Bedrock in us-east-1

## Architecture

### Knowledge Base Structure

```
md/
├── direct_consolidation_chunks/     # 1,333 theory chunks (source material)
├── documentation-library/
│   ├── 00-index/                    # Navigation and cross-references
│   ├── 02-06/                       # Business: methods, calculations, eliminations
│   ├── 07-database-implementation/  # 65 stored procedures, 120+ tables
│   ├── 08-application-layer/        # C# services, jobs
│   ├── 09-frontend-implementation/  # TypeScript/React patterns
│   ├── 10-gap-analysis/             # Missing features with workarounds
│   ├── 11-agent-support/            # 55 YAML files for AI agent development
│   └── 12-user-knowledge-base/      # 27 help files, 2,125 Q&A pairs
├── rag-mcp-server/                  # Local MCP server (sentence-transformers)
└── chromadb-docker/                 # Docker MCP server (AWS Bedrock + Cohere)
```

### Two RAG Deployment Options

1. **Local (rag-mcp-server/)**: Uses sentence-transformers, no external dependencies
2. **Docker (chromadb-docker/)**: Uses AWS Bedrock Cohere Embed v4 (1536 dimensions), better semantic search

### MCP Configuration

Add to project `.mcp.json` for local server:
```json
{
  "mcpServers": {
    "fc-knowledge-base": {
      "command": "python",
      "args": ["md/rag-mcp-server/server.py"]
    }
  }
}
```

For Docker server with AWS Bedrock:
```json
{
  "mcpServers": {
    "fc-knowledge-base": {
      "command": "python",
      "args": ["md/chromadb-docker/mcp-server.py"],
      "env": {
        "AWS_PROFILE": "prophix-devops",
        "AWS_DEFAULT_REGION": "us-east-1"
      }
    }
  }
}
```

## Key Resources

| Resource | Location |
|----------|----------|
| API index (525 handlers) | `11-agent-support/api-index.yaml` |
| Stored procedures (65 P_CONSO_*) | `07-database-implementation/stored-procedures-catalog.md` |
| Database tables (120+) | `07-database-implementation/data-tables-catalog.md` |
| Code patterns | `11-agent-support/code-pattern-library.yaml` |
| Help content | `12-user-knowledge-base/help-content/` |

## IFRS Standards Covered

IFRS 3 (Business Combinations), IFRS 10 (Consolidated Financial Statements), IFRS 11 (Joint Arrangements), IAS 21 (Foreign Exchange), IAS 27 (Separate Financial Statements), IAS 28 (Associates and Joint Ventures), IAS 29 (Hyperinflationary Economies), IAS 36 (Impairment of Assets)
