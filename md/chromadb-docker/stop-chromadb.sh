#!/bin/bash
# Stop ChromaDB
echo "Stopping ChromaDB..."

# Navigate to script directory
cd "$(dirname "$0")"

# Stop container
docker compose down

echo "OK: ChromaDB stopped"
