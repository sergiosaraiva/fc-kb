@echo off
REM Stop Product Owner RAG and ChromaDB
echo Stopping FC Knowledge Base - Product Owner RAG...

REM Navigate to script directory
cd /d "%~dp0"

REM Stop containers (including profile services)
docker-compose --profile with-rag down

echo OK: Services stopped successfully
