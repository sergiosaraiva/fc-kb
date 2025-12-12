# Rebuild and restart Product Owner RAG
Write-Host "Rebuilding FC Knowledge Base - Product Owner RAG..." -ForegroundColor Cyan

# Navigate to script directory
Set-Location $PSScriptRoot

# Stop existing containers
Write-Host "Stopping existing containers..." -ForegroundColor Yellow
docker-compose -f docker-compose-with-po-rag.yml down

# Rebuild Product Owner RAG (force rebuild)
Write-Host "Rebuilding Product Owner RAG container..." -ForegroundColor Yellow
docker-compose -f docker-compose-with-po-rag.yml build --no-cache product-owner-rag

# Start services
Write-Host "Starting services..." -ForegroundColor Yellow
docker-compose -f docker-compose-with-po-rag.yml up -d

# Wait for services to be healthy
Write-Host "Waiting for services to be healthy..." -ForegroundColor Yellow
Start-Sleep -Seconds 10

Write-Host ""
Write-Host "✓ Rebuild complete!" -ForegroundColor Green
Write-Host ""
Write-Host "Access the Product Owner Portal at:" -ForegroundColor Cyan
Write-Host "  🌐 http://localhost:8501" -ForegroundColor White
Write-Host ""

Read-Host "Press Enter to exit"
