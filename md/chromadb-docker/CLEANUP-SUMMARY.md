# Cleanup Summary - Windows-Only Optimization

## Files to be REMOVED (13 files)

### Linux/Mac Shell Scripts (Not needed on Windows)
- ❌ `bootstrap-full.sh`
- ❌ `bootstrap.sh`
- ❌ `run-mcp-server.sh`
- ❌ `start-po-rag.sh`
- ❌ `stop-po-rag.sh`

### Old/Unused PowerShell Scripts
- ❌ `bootstrap-full.ps1` (replaced by simpler scripts)
- ❌ `bootstrap.ps1` (replaced by simpler scripts)

### Old Windows Scripts
- ❌ `setup-windows.bat` (replaced by simpler scripts)

### Unused Python Files
- ❌ `bedrock_embeddings.py` (alternative embedding not in use)

### Diagnostic/Test Scripts (Not needed for production)
- ❌ `test-embeddings.py`
- ❌ `test-import.py`
- ❌ `test-metadata.py`
- ❌ `test-rag-connection.bat`

---

## Files to KEEP (26 files + folders)

### Documentation (3 files)
- ✅ `README.md` - Main documentation
- ✅ `PRODUCT-OWNER-RAG-SETUP.md` - Product Owner RAG setup guide
- ✅ `WINDOWS-QUICK-START.md` - Windows quick start

### Docker Configuration (3 files)
- ✅ `Dockerfile` - ChromaDB Docker image
- ✅ `docker-compose.yml` - ChromaDB only
- ✅ `docker-compose-with-po-rag.yml` - ChromaDB + Product Owner RAG

### Core Python Scripts (4 files)
- ✅ `config.py` - Configuration settings
- ✅ `titan_v1_embeddings.py` - AWS Bedrock Titan V1 embeddings (in use)
- ✅ `ingest-to-chromadb.py` - Knowledge base ingestion
- ✅ `mcp-server.py` - MCP server for Claude Code

### Windows Scripts (8 files - Batch + PowerShell pairs)
- ✅ `fix-and-reingest.bat` / `fix-and-reingest.ps1` - Fix distance metric and re-ingest
- ✅ `rebuild-po-rag.bat` / `rebuild-po-rag.ps1` - Rebuild Product Owner RAG container
- ✅ `start-po-rag.bat` / `start-po-rag.ps1` - Start services
- ✅ `stop-po-rag.bat` / `stop-po-rag.ps1` - Stop services

### Data Files (2 files)
- ✅ `FC-Full-KnowledgeBase.zip` - Full knowledge base (5,400+ docs)
- ✅ `FC-Business-KnowledgeBase.zip` - Business layer subset (optional)

### Configuration Files (2 files)
- ✅ `mcp-config.json` - MCP configuration example
- ✅ `requirements.txt` - Python dependencies

### Folders
- ✅ `product-owner-rag/` - Product Owner RAG application
- ✅ `venv/` or `venv-win/` - Python virtual environment
- ✅ `__pycache__/` - Python cache (auto-generated)

---

## After Cleanup - Clean Folder Structure

```
chromadb-docker/
│
├── 📄 Documentation
│   ├── README.md
│   ├── PRODUCT-OWNER-RAG-SETUP.md
│   └── WINDOWS-QUICK-START.md
│
├── 🐳 Docker
│   ├── Dockerfile
│   ├── docker-compose.yml
│   └── docker-compose-with-po-rag.yml
│
├── 🐍 Python Core
│   ├── config.py
│   ├── titan_v1_embeddings.py
│   ├── ingest-to-chromadb.py
│   ├── mcp-server.py
│   └── requirements.txt
│
├── 🪟 Windows Scripts
│   ├── fix-and-reingest.bat/.ps1
│   ├── rebuild-po-rag.bat/.ps1
│   ├── start-po-rag.bat/.ps1
│   └── stop-po-rag.bat/.ps1
│
├── 📦 Data
│   ├── FC-Full-KnowledgeBase.zip
│   └── FC-Business-KnowledgeBase.zip
│
├── ⚙️ Config
│   └── mcp-config.json
│
└── 📁 Folders
    ├── product-owner-rag/
    ├── venv/ or venv-win/
    └── __pycache__/
```

---

## Why Remove These Files?

### Linux/Mac Scripts (.sh files)
- **Reason:** You're on Windows with PowerShell
- **Impact:** None - these don't work on Windows anyway

### Old Bootstrap Scripts
- **Reason:** Replaced by simpler `fix-and-reingest` and `start-po-rag` scripts
- **Impact:** None - no longer needed

### Unused Embedding Implementations
- **Reason:** `bedrock_embeddings.py` is an old/alternative implementation
- **Current:** Using `titan_v1_embeddings.py`
- **Impact:** None - not referenced anywhere

### Test/Diagnostic Scripts
- **Reason:** Only used for troubleshooting during development
- **Impact:** None - production systems don't need these
- **Note:** If issues arise, they can be recreated easily

---

## How to Run Cleanup

### Option 1: PowerShell (Recommended)
```powershell
cd C:\Work\Prophix.Conso.2026.1\docs\DC\md\chromadb-docker
.\cleanup-folder.ps1
```

### Option 2: Batch File
```cmd
cd C:\Work\Prophix.Conso.2026.1\docs\DC\md\chromadb-docker
cleanup-folder.bat
```

### Option 3: Manual (if you prefer)
Just delete the 13 files listed in the "Files to be REMOVED" section above.

---

## Safety

✅ **Safe to run** - Only removes unused/redundant files
✅ **No data loss** - Knowledge base ZIPs are preserved
✅ **No config loss** - All configuration files kept
✅ **Reversible** - Can recreate test scripts if needed later

---

## After Cleanup

Your folder will be:
- ✅ **Cleaner** - Only Windows-compatible files
- ✅ **Simpler** - No confusion about which scripts to use
- ✅ **Faster** - Less clutter when browsing
- ✅ **Windows-optimized** - Only .bat and .ps1 scripts

All functionality preserved - just cleaner organization!
