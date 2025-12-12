@echo off
REM Start Product Owner RAG with ChromaDB
echo Starting FC Knowledge Base - Product Owner RAG...

REM Check if Docker is running
docker info >nul 2>&1
if errorlevel 1 (
    echo Error: Docker is not running. Please start Docker Desktop.
    exit /b 1
)

REM Navigate to script directory
cd /d "%~dp0"

REM Start both ChromaDB and Product Owner RAG
echo Starting ChromaDB and Product Owner RAG containers...
docker-compose --profile with-rag up -d

REM Wait for services to be healthy
echo Waiting for services to be healthy...
timeout /t 5 /nobreak >nul

REM Check ChromaDB health
docker-compose ps | findstr "chromadb" | findstr "healthy" >nul
if errorlevel 1 (
    echo Warning: ChromaDB is starting... ^(may take a few seconds^)
) else (
    echo OK: ChromaDB is healthy
)

REM Check Product Owner RAG health
docker-compose ps | findstr "product-owner-rag" | findstr "healthy" >nul
if errorlevel 1 (
    echo Warning: Product Owner RAG is starting... ^(may take a few seconds^)
) else (
    echo OK: Product Owner RAG is healthy
)

echo.
echo Services started successfully!
echo.
echo Access the Product Owner Portal at:
echo   http://localhost:8501
echo.
echo View logs:
echo   docker-compose --profile with-rag logs -f product-owner-rag
echo.
echo Stop services:
echo   stop-po-rag.bat
echo.
