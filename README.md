# FC Knowledge Base

Financial Consolidation Knowledge Base for Claude Code MCP integration.

## Quick Start

### Prerequisites
- **Docker Desktop** (Windows with WSL2 backend)
- **AWS CLI** configured with `prophix-devops` profile
- **Python 3.10+** (both Windows and WSL)

### Setup Steps

1. **Clone the repository**
   ```powershell
   git clone https://github.com/sergiosaraiva/fc-kb.git
   cd fc-kb
   ```

2. **Create Python virtual environments**

   Two venvs are needed because Claude Code runs in WSL while batch scripts run in Windows:

   **WSL venv** (for MCP server - Claude Code runs in WSL):
   ```bash
   cd /mnt/c/Work/direct-consolidation-docs
   python3 -m venv venv
   ./venv/bin/pip install chromadb boto3 mcp
   ```

   **Windows venv** (for batch scripts):
   ```powershell
   cd C:\Work\direct-consolidation-docs
   python -m venv venv-win
   .\venv-win\Scripts\pip install chromadb boto3
   ```

3. **Configure AWS credentials**

   AWS credentials are needed for Bedrock embeddings. Since we have two Python environments, credentials must be accessible from both:

   **Option A: Configure in both environments**
   ```powershell
   # Windows (for ingest.bat)
   aws configure --profile prophix-devops
   # Region: us-east-1
   ```
   ```bash
   # WSL (for MCP server)
   aws configure --profile prophix-devops
   # Region: us-east-1
   ```

   **Option B: Symlink WSL to Windows credentials (recommended)**
   ```bash
   # In WSL - link to Windows credentials (replace {username} with your Windows username)
   rm -rf ~/.aws
   ln -s /mnt/c/Users/{username}/.aws ~/.aws
   ```
   Then only configure once from Windows.

   **Credential locations:**
   | Environment | Path |
   |-------------|------|
   | Windows | `C:\Users\{username}\.aws\credentials` |
   | WSL | `~/.aws/credentials` |

4. **Start ChromaDB** (from Windows CMD or PowerShell)
   ```cmd
   cd md\chromadb-docker
   start-chromadb.bat
   ```

5. **Ingest the knowledge base** (one-time, from Windows)
   ```cmd
   cd md\chromadb-docker
   ingest.bat
   ```

6. **Configure Claude Code MCP**

   Create `.mcp.json` in your project root:
   ```json
   {
     "mcpServers": {
       "fc-knowledge-base": {
         "command": "/mnt/c/Work/direct-consolidation-docs/venv/bin/python",
         "args": ["md/chromadb-docker/mcp-server.py"],
         "cwd": "/mnt/c/Work/direct-consolidation-docs",
         "env": {
           "AWS_PROFILE": "prophix-devops",
           "AWS_DEFAULT_REGION": "us-east-1",
           "CHROMADB_HOST": "localhost",
           "CHROMADB_PORT": "8847",
           "CHROMADB_TOKEN": "fc-knowledge-base-token"
         }
       }
     }
   }
   ```

   > **Note**: Uses WSL paths and WSL Python (`venv/bin/python`). Adjust paths to match your installation.

7. **Restart Claude Code** to load the MCP server

## Available Scripts

| Script | Purpose |
|--------|---------|
| `start-chromadb.bat` | Start ChromaDB (required for MCP) |
| `stop-chromadb.bat` | Stop ChromaDB |
| `ingest.bat` | Populate knowledge base (one-time) |
| `start-po-rag.bat` | Start ChromaDB + Web UI (optional) |
| `stop-po-rag.bat` | Stop ChromaDB + Web UI |
| `rebuild-po-rag.bat` | Rebuild containers |

All scripts are in `md/chromadb-docker/`.

## Usage in Claude Code

Once configured, the MCP server provides `search_fc_full` tool:

```
Use search_fc_full to search for:
- Consolidation methods (global integration, equity method)
- IFRS standards (IFRS 3, IFRS 10, IAS 21)
- Database procedures (P_CONSO_*, P_CALC_*)
- Application patterns and code examples
```

## Architecture

- **ChromaDB**: Vector database (port 8847)
- **AWS Bedrock Titan V1**: Embeddings (1536 dimensions)
- **MCP Server**: Claude Code integration

### Why Two Virtual Environments?

| venv | Location | Purpose |
|------|----------|---------|
| `venv/` | WSL Python | MCP server (Claude Code runs in WSL) |
| `venv-win/` | Windows Python | Batch scripts (run from PowerShell/CMD) |

Claude Code runs inside WSL, so the MCP server needs WSL Python. The batch scripts run from Windows, so they need Windows Python.

## Troubleshooting

### MCP server shows "failed" status
1. Ensure ChromaDB is running: `docker ps | grep chromadb`
2. Check Python path matches your venv location
3. Verify AWS credentials: `aws sts get-caller-identity --profile prophix-devops`

### Ingestion fails
1. Ensure `FC-Full-KnowledgeBase.zip` exists in `md/chromadb-docker/`
2. Check AWS Bedrock access in us-east-1 region
3. Verify ChromaDB is healthy: `curl http://localhost:8847/api/v2/heartbeat`
