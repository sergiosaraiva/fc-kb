#!/bin/bash
# Start ChromaDB for FC Knowledge Base MCP Server
echo "Starting ChromaDB (FC Knowledge Base)..."

# Navigate to script directory
cd "$(dirname "$0")"

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "Error: Docker is not running. Please start Docker service."
    echo "  Run: sudo service docker start"
    exit 1
fi

# Start ChromaDB only (without product-owner-rag profile)
echo "Starting ChromaDB container..."
docker compose up -d chromadb

# Wait for health check
echo "Waiting for ChromaDB to be healthy..."
sleep 5

# Check ChromaDB health
if docker compose ps | grep -q "chromadb.*healthy"; then
    echo "OK: ChromaDB is healthy"
else
    echo "Warning: ChromaDB is starting... (may take a few seconds)"
fi

echo ""
echo "ChromaDB is running!"
echo "  Port: 8847"
echo "  Token: fc-knowledge-base-token"
echo ""
echo "For Claude Code MCP, add to .mcp.json:"
echo "  CHROMADB_HOST=localhost"
echo "  CHROMADB_PORT=8847"
echo ""
echo "Stop: ./stop-chromadb.sh"
echo ""
