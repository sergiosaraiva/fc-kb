#!/bin/bash
# Stop Product Owner RAG and ChromaDB
echo "Stopping FC Knowledge Base - Product Owner RAG..."

# Navigate to script directory
cd "$(dirname "$0")"

# Stop containers (including profile services)
docker compose --profile with-rag down

echo "OK: Services stopped successfully"
