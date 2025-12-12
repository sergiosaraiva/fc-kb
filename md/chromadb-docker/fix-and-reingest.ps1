# Fix and re-ingest the knowledge base with correct distance metric
Write-Host "===================================================================" -ForegroundColor Cyan
Write-Host "FIXING KNOWLEDGE BASE - RE-INGESTION REQUIRED" -ForegroundColor Yellow
Write-Host "===================================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Problem: Collection was created with L2 distance instead of cosine." -ForegroundColor Red
Write-Host "Solution: Re-ingest with correct distance metric." -ForegroundColor Green
Write-Host ""
Write-Host "This will:" -ForegroundColor White
Write-Host "1. Delete the existing collection" -ForegroundColor White
Write-Host "2. Re-create it with COSINE distance" -ForegroundColor White
Write-Host "3. Re-embed all 5,400+ documents (takes ~10-15 minutes)" -ForegroundColor White
Write-Host ""
Write-Host "AWS Bedrock rate limits may slow this down." -ForegroundColor Yellow
Write-Host ""

$confirmation = Read-Host "Continue? (Y/N)"
if ($confirmation -ne 'Y' -and $confirmation -ne 'y') {
    Write-Host "Cancelled." -ForegroundColor Red
    exit 1
}

# Navigate to script directory
Set-Location $PSScriptRoot

# Activate virtual environment
Write-Host ""
Write-Host "Activating virtual environment..." -ForegroundColor Yellow
& "venv-win\Scripts\Activate.ps1"

# Run ingestion
Write-Host ""
Write-Host "Starting re-ingestion..." -ForegroundColor Yellow
Write-Host ""
python ingest-to-chromadb.py

if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "ERROR: Ingestion failed!" -ForegroundColor Red
    Write-Host "Check the output above for errors." -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host ""
Write-Host "===================================================================" -ForegroundColor Green
Write-Host "SUCCESS! Knowledge base re-ingested with cosine distance" -ForegroundColor Green
Write-Host "===================================================================" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "1. Restart Product Owner RAG: .\rebuild-po-rag.ps1" -ForegroundColor White
Write-Host "2. Test at http://localhost:8501" -ForegroundColor White
Write-Host ""

Read-Host "Press Enter to exit"
