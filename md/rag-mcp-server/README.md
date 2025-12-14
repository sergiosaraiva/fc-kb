# FC Knowledge Base RAG - MCP Server

ChromaDB-based RAG system for Financial Consolidation knowledge, integrated with Claude Code via MCP (Model Context Protocol).

## Overview

This MCP server provides two knowledge bases:
- **Business Knowledge**: Consolidation concepts, IFRS standards, product usage, troubleshooting
- **Technical Knowledge**: Database schemas, stored procedures, API handlers, code patterns

## Prerequisites

- Python 3.10+
- ChromaDB
- The ZIP knowledge base files in parent directory:
  - `RAG-Business-KnowledgeBase.zip`
  - `RAG-Technical-KnowledgeBase.zip`

## Installation

```bash
# Navigate to server directory
cd docs/DC/md/rag-mcp-server

# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or: venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt
```

## Step 1: Ingest Documents

Run the ingestion script to populate ChromaDB:

```bash
python ingest.py
```

This will:
1. Extract documents from both ZIP files
2. Chunk documents intelligently (respecting markdown sections)
3. Add metadata classification (topic, layer, audience)
4. Store in ChromaDB collections: `business_knowledge` and `technical_knowledge`

Expected output:
```
FC Knowledge Base - ChromaDB Ingestion
Processing RAG-Business-KnowledgeBase.zip into collection 'business_knowledge'...
Found ~1400 documents in ZIP
Collection 'business_knowledge' now has ~2000 chunks

Processing RAG-Technical-KnowledgeBase.zip into collection 'technical_knowledge'...
Found ~1500 documents in ZIP
Collection 'technical_knowledge' now has ~3000 chunks
```

## Step 2: Configure Claude Code

Add the MCP server to your Claude Code configuration.

### Option A: Project-level configuration

Create/edit `.mcp.json` in your project root:

```json
{
  "mcpServers": {
    "fc-knowledge-base": {
      "command": "python",
      "args": ["docs/DC/md/rag-mcp-server/server.py"],
      "env": {}
    }
  }
}
```

### Option B: User-level configuration

Edit `~/.claude/mcp_servers.json` (create if doesn't exist):

```json
{
  "fc-knowledge-base": {
    "command": "python",
    "args": ["/full/path/to/docs/DC/md/rag-mcp-server/server.py"],
    "env": {}
  }
}
```

### Option C: Claude Desktop configuration

Edit `~/Library/Application Support/Claude/claude_desktop_config.json` (Mac) or `%APPDATA%\Claude\claude_desktop_config.json` (Windows):

```json
{
  "mcpServers": {
    "fc-knowledge-base": {
      "command": "python",
      "args": ["/full/path/to/docs/DC/md/rag-mcp-server/server.py"]
    }
  }
}
```

## Step 3: Restart Claude Code

After configuration, restart Claude Code to load the MCP server.

## Available Tools

Once configured, Claude Code will have access to:

### `search_business_knowledge`
Search consolidation concepts, IFRS standards, product usage guides.

Parameters:
- `query` (required): Search query
- `num_results` (optional): Number of results (default: 5, max: 10)
- `topic_filter` (optional): Filter by topic
  - `consolidation-methods`
  - `eliminations`
  - `currency`
  - `ownership`
  - `calculations`
  - `help`
  - `theory`

### `search_technical_knowledge`
Search database schemas, stored procedures, API handlers, code patterns.

Parameters:
- `query` (required): Search query
- `num_results` (optional): Number of results (default: 5, max: 10)
- `layer_filter` (optional): Filter by technical layer
  - `database`
  - `application`
  - `frontend`
  - `api`

### `get_collection_stats`
Get document counts and collection statistics.

## Example Usage in Claude Code

Once configured, you can ask Claude questions like:

**Business questions:**
- "How does equity method consolidation work?"
- "What IFRS standard covers goodwill impairment?"
- "How do I set up intercompany eliminations in the product?"

**Technical questions:**
- "What stored procedures handle ownership calculations?"
- "Show me the database schema for consolidation adjustments"
- "What API handlers are available for currency translation?"

## Troubleshooting

### "Collection not found" errors
Run `python ingest.py` to populate the database.

### Server won't start
1. Check Python version: `python --version` (needs 3.10+)
2. Verify dependencies: `pip install -r requirements.txt`
3. Check ChromaDB path permissions

### No results returned
1. Verify ingestion completed successfully
2. Check `chroma_db/` directory exists and has content
3. Try broader search terms

## Directory Structure

```
rag-mcp-server/
├── README.md           # This file
├── requirements.txt    # Python dependencies
├── server.py          # MCP server implementation
├── ingest.py          # Document ingestion script
└── chroma_db/         # ChromaDB storage (created by ingest.py)
    ├── business_knowledge/
    └── technical_knowledge/
```

## Updating the Knowledge Base

To update after adding new documentation:

1. Update the source ZIP files
2. Re-run ingestion: `python ingest.py`
3. Restart Claude Code

The ingestion script will replace existing collections with fresh data.
