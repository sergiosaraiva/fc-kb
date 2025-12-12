@echo off
REM Start ChromaDB for FC Knowledge Base MCP Server
echo Starting ChromaDB (FC Knowledge Base)...

REM Check if Docker is running
docker info >nul 2>&1
if errorlevel 1 (
    echo Error: Docker is not running. Please start Docker Desktop.
    exit /b 1
)

REM Navigate to script directory
cd /d "%~dp0"

REM Start ChromaDB only
echo Starting ChromaDB container...
docker-compose -f docker-compose.yml up -d

REM Wait for health check
echo Waiting for ChromaDB to be healthy...
timeout /t 5 /nobreak >nul

REM Check ChromaDB health
docker-compose -f docker-compose.yml ps | findstr "chromadb" | findstr "healthy" >nul
if errorlevel 1 (
    echo Warning: ChromaDB is starting... ^(may take a few seconds^)
) else (
    echo OK: ChromaDB is healthy
)

echo.
echo ChromaDB is running!
echo   Port: 8847
echo   Token: fc-knowledge-base-token
echo.
echo For Claude Code MCP, add to .mcp.json:
echo   CHROMADB_HOST=localhost
echo   CHROMADB_PORT=8847
echo.
echo Stop: stop-chromadb.bat
echo.
