#!/bin/bash
# Start Product Owner RAG with ChromaDB
echo "Starting FC Knowledge Base - Product Owner RAG..."

# Navigate to script directory
cd "$(dirname "$0")"

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "Error: Docker is not running. Please start Docker service."
    echo "  Run: sudo service docker start"
    exit 1
fi

# Start both ChromaDB and Product Owner RAG
echo "Starting ChromaDB and Product Owner RAG containers..."
docker compose --profile with-rag up -d

# Wait for services to be healthy
echo "Waiting for services to be healthy..."
sleep 5

# Check ChromaDB health
if docker compose ps | grep -q "chromadb.*healthy"; then
    echo "OK: ChromaDB is healthy"
else
    echo "Warning: ChromaDB is starting... (may take a few seconds)"
fi

# Check Product Owner RAG health
if docker compose ps | grep -q "product-owner-rag.*healthy"; then
    echo "OK: Product Owner RAG is healthy"
else
    echo "Warning: Product Owner RAG is starting... (may take a few seconds)"
fi

echo ""
echo "Services started successfully!"
echo ""
echo "Access the Product Owner Portal at:"
echo "  http://localhost:8501"
echo ""
echo "View logs:"
echo "  docker compose --profile with-rag logs -f product-owner-rag"
echo ""
echo "Stop services:"
echo "  ./stop-po-rag.sh"
echo ""
