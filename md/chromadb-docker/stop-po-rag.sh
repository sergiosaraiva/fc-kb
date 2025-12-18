#!/bin/bash
# Stop Product Owner RAG and ChromaDB
echo "Stopping FC Knowledge Base - Product Owner RAG..."

# Navigate to script directory
cd "$(dirname "$0")"

# Detect docker compose command (V2 plugin or V1 standalone)
if docker compose version &>/dev/null; then
    COMPOSE_CMD="docker compose"
else
    COMPOSE_CMD="docker-compose"
fi

# Stop containers (including profile services)
$COMPOSE_CMD --profile with-rag down

echo "OK: Services stopped successfully"
