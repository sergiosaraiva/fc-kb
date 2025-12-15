#!/bin/bash
# Ingest FC Knowledge Base into ChromaDB (one-time setup)
echo "============================================================"
echo "FC Knowledge Base - Ingestion"
echo "============================================================"
echo ""

# Navigate to script directory
cd "$(dirname "$0")"

# Check if ChromaDB is running
if ! docker compose ps | grep -q "chromadb.*Up"; then
    echo "Error: ChromaDB is not running."
    echo "Please run ./start-chromadb.sh first."
    exit 1
fi

# Check if ZIP file exists
if [ ! -f "FC-Full-KnowledgeBase.zip" ]; then
    echo "Error: FC-Full-KnowledgeBase.zip not found."
    echo "Please ensure the ZIP file is in the same directory."
    exit 1
fi

# Check for Python venv
VENV_PATH="../../venv"
if [ ! -f "$VENV_PATH/bin/python" ]; then
    echo "Error: Python virtual environment not found."
    echo ""
    echo "Please create a venv:"
    echo "  cd /mnt/c/Work/direct-consolidation-docs"
    echo "  python3 -m venv venv"
    echo "  ./venv/bin/pip install chromadb boto3"
    echo ""
    exit 1
fi

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "Error: .env file not found."
    echo "Please copy .env.example to .env and fill in your AWS credentials."
    exit 1
fi

# Load environment variables from .env file
export $(grep -v '^#' .env | xargs)

# Check AWS credentials are set
if [ -z "$AWS_ACCESS_KEY_ID" ]; then
    echo "Error: AWS_ACCESS_KEY_ID not set in .env file."
    exit 1
fi

echo ""
echo "Starting ingestion (this may take several minutes)..."
echo ""

# Set environment variables for local ChromaDB
export CHROMADB_HOST=localhost
export CHROMADB_PORT=8847
export CHROMADB_TOKEN=fc-knowledge-base-token

# Run ingestion
$VENV_PATH/bin/python ingest-to-chromadb.py

echo ""
echo "============================================================"
echo "Ingestion complete!"
echo "============================================================"
echo ""
