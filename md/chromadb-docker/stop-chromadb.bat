@echo off
REM Stop ChromaDB
echo Stopping ChromaDB...

REM Navigate to script directory
cd /d "%~dp0"

REM Stop container
docker-compose -f docker-compose.yml down

echo OK: ChromaDB stopped
