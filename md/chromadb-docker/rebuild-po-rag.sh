#!/bin/bash
# Rebuild and restart Product Owner RAG
echo "Rebuilding FC Knowledge Base - Product Owner RAG..."

# Navigate to script directory
cd "$(dirname "$0")"

# Detect docker compose command (V2 plugin or V1 standalone)
if docker compose version &>/dev/null; then
    COMPOSE_CMD="docker compose"
else
    COMPOSE_CMD="docker-compose"
fi

# Stop existing containers
echo "Stopping existing containers..."
$COMPOSE_CMD --profile with-rag down

# Rebuild Product Owner RAG (force rebuild)
echo "Rebuilding Product Owner RAG container..."
$COMPOSE_CMD --profile with-rag build product-owner-rag

# Start services
echo "Starting services..."
$COMPOSE_CMD --profile with-rag up -d

# Wait for services to be healthy
echo "Waiting for services to be healthy..."
sleep 10

echo ""
echo "OK: Rebuild complete!"
echo ""
echo "Access the Product Owner Portal at:"
echo "  http://localhost:8501"
echo ""
