#!/bin/bash
# Stop ChromaDB
echo "Stopping ChromaDB..."

# Navigate to script directory
cd "$(dirname "$0")"

# Detect docker compose command (V2 plugin or V1 standalone)
if docker compose version &>/dev/null; then
    COMPOSE_CMD="docker compose"
else
    COMPOSE_CMD="docker-compose"
fi

# Stop container
$COMPOSE_CMD down

echo "OK: ChromaDB stopped"
