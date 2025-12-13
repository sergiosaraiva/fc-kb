#!/bin/bash
# Rebuild and restart Product Owner RAG
echo "Rebuilding FC Knowledge Base - Product Owner RAG..."

# Navigate to script directory
cd "$(dirname "$0")"

# Stop existing containers
echo "Stopping existing containers..."
docker-compose --profile with-rag down

# Rebuild Product Owner RAG (force rebuild)
echo "Rebuilding Product Owner RAG container..."
docker-compose --profile with-rag build --no-cache product-owner-rag

# Start services
echo "Starting services..."
docker-compose --profile with-rag up -d

# Wait for services to be healthy
echo "Waiting for services to be healthy..."
sleep 10

echo ""
echo "OK: Rebuild complete!"
echo ""
echo "Access the Product Owner Portal at:"
echo "  http://localhost:8501"
echo ""
