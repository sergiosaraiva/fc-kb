@echo off
REM Ingest FC Knowledge Base into ChromaDB (one-time setup)
echo ============================================================
echo FC Knowledge Base - Ingestion
echo ============================================================
echo.

REM Navigate to script directory
cd /d "%~dp0"

REM Check if ChromaDB is running
docker-compose -f docker-compose.yml ps | findstr "chromadb" | findstr "Up" >nul
if errorlevel 1 (
    echo Error: ChromaDB is not running.
    echo Please run start-chromadb.bat first.
    exit /b 1
)

REM Check if ZIP file exists
if not exist "FC-Full-KnowledgeBase.zip" (
    echo Error: FC-Full-KnowledgeBase.zip not found.
    echo Please ensure the ZIP file is in the same directory.
    exit /b 1
)

REM Check for Python venv (Windows venv first, then WSL venv)
if exist "..\..\venv-win\Scripts\python.exe" (
    set PYTHON=..\..\venv-win\Scripts\python.exe
) else if exist "..\..\venv\Scripts\python.exe" (
    set PYTHON=..\..\venv\Scripts\python.exe
) else (
    echo Error: Python virtual environment not found.
    echo.
    echo Please create a Windows venv:
    echo   cd C:\Work\direct-consolidation-docs
    echo   python -m venv venv-win
    echo   .\venv-win\Scripts\pip install chromadb boto3
    echo.
    exit /b 1
)

REM Check AWS credentials
echo Checking AWS credentials...
aws sts get-caller-identity --profile prophix-devops >nul 2>&1
if errorlevel 1 (
    echo Error: AWS credentials not configured.
    echo Please configure AWS profile: prophix-devops
    echo Run: aws configure --profile prophix-devops
    exit /b 1
)

echo.
echo Starting ingestion (this may take several minutes)...
echo.

REM Set environment variables for local ChromaDB
set CHROMADB_HOST=localhost
set CHROMADB_PORT=8847
set CHROMADB_TOKEN=fc-knowledge-base-token
set AWS_PROFILE=prophix-devops
set AWS_DEFAULT_REGION=us-east-1

REM Run ingestion
%PYTHON% ingest-to-chromadb.py

echo.
echo ============================================================
echo Ingestion complete!
echo ============================================================
echo.
