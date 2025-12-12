@echo off
REM Rebuild and restart Product Owner RAG
echo Rebuilding FC Knowledge Base - Product Owner RAG...

REM Navigate to script directory
cd /d "%~dp0"

REM Stop existing containers
echo Stopping existing containers...
docker-compose -f docker-compose-with-po-rag.yml down

REM Rebuild Product Owner RAG (force rebuild)
echo Rebuilding Product Owner RAG container...
docker-compose -f docker-compose-with-po-rag.yml build --no-cache product-owner-rag

REM Start services
echo Starting services...
docker-compose -f docker-compose-with-po-rag.yml up -d

REM Wait for services to be healthy
echo Waiting for services to be healthy...
timeout /t 10 /nobreak >nul

echo.
echo OK: Rebuild complete!
echo.
echo Access the Product Owner Portal at:
echo   http://localhost:8501
echo.
pause
