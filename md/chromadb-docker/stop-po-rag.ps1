# Stop Product Owner RAG and ChromaDB
Write-Host "Stopping FC Knowledge Base - Product Owner RAG..." -ForegroundColor Cyan

# Navigate to script directory
Set-Location $PSScriptRoot

# Stop containers
docker-compose -f docker-compose-with-po-rag.yml down

Write-Host "✓ Services stopped successfully" -ForegroundColor Green

Read-Host "Press Enter to exit"
