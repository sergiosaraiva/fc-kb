# Start Product Owner RAG with ChromaDB
Write-Host "Starting FC Knowledge Base - Product Owner RAG..." -ForegroundColor Cyan

# Check if Docker is running
try {
    docker info | Out-Null
} catch {
    Write-Host "Error: Docker is not running. Please start Docker Desktop." -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

# Navigate to script directory
Set-Location $PSScriptRoot

# Start both ChromaDB and Product Owner RAG
Write-Host "Starting ChromaDB and Product Owner RAG containers..." -ForegroundColor Yellow
docker-compose -f docker-compose-with-po-rag.yml up -d

# Wait for services to be healthy
Write-Host "Waiting for services to be healthy..." -ForegroundColor Yellow
Start-Sleep -Seconds 5

# Check ChromaDB health
$chromaStatus = docker-compose -f docker-compose-with-po-rag.yml ps | Select-String "chromadb.*healthy"
if ($chromaStatus) {
    Write-Host "✓ ChromaDB is healthy" -ForegroundColor Green
} else {
    Write-Host "⚠ ChromaDB is starting... (may take a few seconds)" -ForegroundColor Yellow
}

# Check Product Owner RAG health
$ragStatus = docker-compose -f docker-compose-with-po-rag.yml ps | Select-String "product-owner-rag.*healthy"
if ($ragStatus) {
    Write-Host "✓ Product Owner RAG is healthy" -ForegroundColor Green
} else {
    Write-Host "⚠ Product Owner RAG is starting... (may take a few seconds)" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Services started successfully!" -ForegroundColor Green
Write-Host ""
Write-Host "Access the Product Owner Portal at:" -ForegroundColor Cyan
Write-Host "  🌐 http://localhost:8501" -ForegroundColor White
Write-Host ""
Write-Host "View logs:" -ForegroundColor Cyan
Write-Host "  docker-compose -f docker-compose-with-po-rag.yml logs -f product-owner-rag" -ForegroundColor White
Write-Host ""
Write-Host "Stop services:" -ForegroundColor Cyan
Write-Host "  .\stop-po-rag.ps1  (or stop-po-rag.bat)" -ForegroundColor White
Write-Host ""

Read-Host "Press Enter to exit"
