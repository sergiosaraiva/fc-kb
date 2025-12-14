#!/bin/bash
# Create LLM-enhanced knowledge base ZIP
# This produces world-class RAG quality using Bedrock Claude

echo "============================================================"
echo "FC Knowledge Base - LLM-Enhanced ZIP Creation"
echo "============================================================"
echo ""
echo "This will process ~1,400 documentation chunks through Bedrock Claude"
echo "to generate semantic summaries, keywords, and hypothetical questions."
echo ""
echo "Estimated time: 3-4 hours (using Claude Sonnet 4.5 for best quality)"
echo "Estimated cost: ~\$20-30"
echo ""

cd "$(dirname "$0")"

# Load .env
set -a
source .env
set +a

# Use venv Python
PYTHON="../../venv/bin/python"

if [ ! -f "$PYTHON" ]; then
    echo "Error: Python venv not found at $PYTHON"
    exit 1
fi

# Check AWS credentials
if [ -z "$AWS_ACCESS_KEY_ID" ]; then
    echo "Error: AWS_ACCESS_KEY_ID not set in .env"
    exit 1
fi

echo "Starting LLM-enhanced ZIP creation..."
echo ""

# Run with LLM enhancement (default - no flags needed)
$PYTHON create-knowledge-zip.py

echo ""
echo "Done! The ZIP now contains world-class semantic chunks."
echo ""
