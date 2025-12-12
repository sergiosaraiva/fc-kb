@echo off
REM Fix and re-ingest the knowledge base with correct distance metric
echo ===================================================================
echo FIXING KNOWLEDGE BASE - RE-INGESTION REQUIRED
echo ===================================================================
echo.
echo Problem: Collection was created with L2 distance instead of cosine.
echo Solution: Re-ingest with correct distance metric.
echo.
echo This will:
echo 1. Delete the existing collection
echo 2. Re-create it with COSINE distance
echo 3. Re-embed all 5,400+ documents (takes ~10-15 minutes)
echo.
echo AWS Bedrock rate limits may slow this down.
echo.
pause

REM Navigate to script directory
cd /d "%~dp0"

REM Activate virtual environment
echo.
echo Activating virtual environment...
call venv-win\Scripts\activate.bat

REM Run ingestion
echo.
echo Starting re-ingestion...
echo.
python ingest-to-chromadb.py

if errorlevel 1 (
    echo.
    echo ERROR: Ingestion failed!
    echo Check the output above for errors.
    pause
    exit /b 1
)

echo.
echo ===================================================================
echo SUCCESS! Knowledge base re-ingested with cosine distance
echo ===================================================================
echo.
echo Next steps:
echo 1. Restart Product Owner RAG: rebuild-po-rag.bat
echo 2. Test at http://localhost:8501
echo.
pause
