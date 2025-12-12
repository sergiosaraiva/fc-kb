# Cleanup chromadb-docker folder for Windows-only usage
# Removes Linux scripts, unused Python files, and diagnostic scripts

Write-Host "====================================================================" -ForegroundColor Cyan
Write-Host "CLEANING UP CHROMADB-DOCKER FOLDER" -ForegroundColor Yellow
Write-Host "====================================================================" -ForegroundColor Cyan
Write-Host ""

Set-Location $PSScriptRoot

# Files to delete
$filesToDelete = @(
    # Linux/Mac shell scripts (not needed on Windows)
    "bootstrap-full.sh",
    "bootstrap.sh",
    "run-mcp-server.sh",
    "start-po-rag.sh",
    "stop-po-rag.sh",

    # Old/unused PowerShell bootstrap scripts
    "bootstrap-full.ps1",
    "bootstrap.ps1",

    # Old Windows setup script (replaced by simpler scripts)
    "setup-windows.bat",

    # Unused embedding implementations
    "bedrock_embeddings.py",

    # Diagnostic/test scripts (not needed for production)
    "test-embeddings.py",
    "test-import.py",
    "test-metadata.py",
    "test-rag-connection.bat",

    # Business-only ZIP (if you only use full knowledge base)
    # "FC-Business-KnowledgeBase.zip"  # Uncomment to delete
)

Write-Host "The following files will be deleted:" -ForegroundColor Yellow
Write-Host ""

$foundFiles = @()
foreach ($file in $filesToDelete) {
    if (Test-Path $file) {
        $foundFiles += $file
        Write-Host "  ❌ $file" -ForegroundColor Red
    } else {
        Write-Host "  ⚠  $file (already deleted)" -ForegroundColor Gray
    }
}

if ($foundFiles.Count -eq 0) {
    Write-Host ""
    Write-Host "No files to delete. Folder is already clean!" -ForegroundColor Green
    Read-Host "Press Enter to exit"
    exit 0
}

Write-Host ""
Write-Host "Files to keep:" -ForegroundColor Green
Write-Host ""

$keepFiles = @(
    "README.md",
    "PRODUCT-OWNER-RAG-SETUP.md",
    "WINDOWS-QUICK-START.md",
    "Dockerfile",
    "docker-compose.yml",
    "docker-compose-with-po-rag.yml",
    "config.py",
    "titan_v1_embeddings.py",
    "ingest-to-chromadb.py",
    "mcp-server.py",
    "mcp-config.json",
    "requirements.txt",
    "fix-and-reingest.bat",
    "fix-and-reingest.ps1",
    "rebuild-po-rag.bat",
    "rebuild-po-rag.ps1",
    "start-po-rag.bat",
    "start-po-rag.ps1",
    "stop-po-rag.bat",
    "stop-po-rag.ps1",
    "FC-Full-KnowledgeBase.zip",
    "FC-Business-KnowledgeBase.zip"
)

foreach ($file in $keepFiles) {
    if (Test-Path $file) {
        Write-Host "  ✓ $file" -ForegroundColor Green
    }
}

Write-Host ""
$confirmation = Read-Host "Delete $($foundFiles.Count) files? (Y/N)"

if ($confirmation -ne 'Y' -and $confirmation -ne 'y') {
    Write-Host "Cancelled." -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 0
}

Write-Host ""
Write-Host "Deleting files..." -ForegroundColor Yellow

$deletedCount = 0
foreach ($file in $foundFiles) {
    try {
        Remove-Item $file -Force
        Write-Host "  ✓ Deleted: $file" -ForegroundColor Green
        $deletedCount++
    } catch {
        Write-Host "  ✗ Failed to delete: $file - $_" -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "====================================================================" -ForegroundColor Green
Write-Host "CLEANUP COMPLETE" -ForegroundColor Green
Write-Host "====================================================================" -ForegroundColor Green
Write-Host ""
Write-Host "Deleted: $deletedCount files" -ForegroundColor White
Write-Host ""
Write-Host "Remaining structure:" -ForegroundColor Cyan
Write-Host ""
Write-Host "  Documentation:" -ForegroundColor Yellow
Write-Host "    - README.md" -ForegroundColor White
Write-Host "    - PRODUCT-OWNER-RAG-SETUP.md" -ForegroundColor White
Write-Host "    - WINDOWS-QUICK-START.md" -ForegroundColor White
Write-Host ""
Write-Host "  Docker:" -ForegroundColor Yellow
Write-Host "    - Dockerfile" -ForegroundColor White
Write-Host "    - docker-compose.yml" -ForegroundColor White
Write-Host "    - docker-compose-with-po-rag.yml" -ForegroundColor White
Write-Host ""
Write-Host "  Python Scripts:" -ForegroundColor Yellow
Write-Host "    - config.py" -ForegroundColor White
Write-Host "    - titan_v1_embeddings.py" -ForegroundColor White
Write-Host "    - ingest-to-chromadb.py" -ForegroundColor White
Write-Host "    - mcp-server.py" -ForegroundColor White
Write-Host ""
Write-Host "  Windows Scripts:" -ForegroundColor Yellow
Write-Host "    - fix-and-reingest.bat/.ps1" -ForegroundColor White
Write-Host "    - rebuild-po-rag.bat/.ps1" -ForegroundColor White
Write-Host "    - start-po-rag.bat/.ps1" -ForegroundColor White
Write-Host "    - stop-po-rag.bat/.ps1" -ForegroundColor White
Write-Host ""
Write-Host "  Data:" -ForegroundColor Yellow
Write-Host "    - FC-Full-KnowledgeBase.zip" -ForegroundColor White
Write-Host "    - FC-Business-KnowledgeBase.zip" -ForegroundColor White
Write-Host ""
Write-Host "  Config:" -ForegroundColor Yellow
Write-Host "    - mcp-config.json" -ForegroundColor White
Write-Host "    - requirements.txt" -ForegroundColor White
Write-Host ""

Read-Host "Press Enter to exit"
