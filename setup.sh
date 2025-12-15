#!/bin/bash
# FC Knowledge Base - One-time Setup Script
# Run this after cloning the repository

set -e

echo "============================================================"
echo "FC Knowledge Base - Setup"
echo "============================================================"
echo ""

# Get the directory where the script is located
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

# Check prerequisites
echo "Checking prerequisites..."
echo ""

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed."
    echo "Please install Python 3.10+ and try again."
    exit 1
fi
echo "  [OK] Python 3 found: $(python3 --version)"

# Check Docker
if ! command -v docker &> /dev/null; then
    echo "Error: Docker is not installed."
    echo "Please install Docker Desktop and try again."
    exit 1
fi
echo "  [OK] Docker found"

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo ""
    echo "Warning: Docker is not running."
    echo "Please start Docker Desktop before running the knowledge base."
fi

# Check AWS CLI (optional but recommended)
if command -v aws &> /dev/null; then
    echo "  [OK] AWS CLI found"
else
    echo "  [--] AWS CLI not found (optional - you can use .env file instead)"
fi

echo ""
echo "------------------------------------------------------------"
echo "Step 1: Creating Python virtual environment..."
echo "------------------------------------------------------------"

if [ -d "venv" ]; then
    echo "  Virtual environment already exists. Skipping creation."
else
    python3 -m venv venv
    echo "  [OK] Virtual environment created"
fi

echo ""
echo "------------------------------------------------------------"
echo "Step 2: Installing Python dependencies..."
echo "------------------------------------------------------------"

./venv/bin/pip install --upgrade pip -q
./venv/bin/pip install -r md/chromadb-docker/requirements.txt -q
echo "  [OK] Dependencies installed (chromadb, boto3, mcp)"

echo ""
echo "------------------------------------------------------------"
echo "Step 3: Configuring AWS credentials..."
echo "------------------------------------------------------------"

ENV_FILE="md/chromadb-docker/.env"
ENV_EXAMPLE="md/chromadb-docker/.env.example"

if [ -f "$ENV_FILE" ]; then
    echo "  .env file already exists."
else
    if [ -f "$ENV_EXAMPLE" ]; then
        cp "$ENV_EXAMPLE" "$ENV_FILE"
        echo "  Created .env file from template."
        echo ""
        echo "  IMPORTANT: Edit md/chromadb-docker/.env with your AWS credentials:"
        echo "    AWS_ACCESS_KEY_ID=your_key"
        echo "    AWS_SECRET_ACCESS_KEY=your_secret"
        echo ""
    fi
fi

echo ""
echo "------------------------------------------------------------"
echo "Step 4: Creating MCP configuration..."
echo "------------------------------------------------------------"

MCP_CONFIG=".mcp.json"
if [ -f "$MCP_CONFIG" ]; then
    echo "  .mcp.json already exists. Skipping."
else
    cat > "$MCP_CONFIG" << 'EOF'
{
  "mcpServers": {
    "fc-knowledge-base": {
      "command": "md/chromadb-docker/run-mcp-server.sh",
      "args": ["venv/bin/python", "md/chromadb-docker/mcp-server.py"],
      "env": {
        "CHROMADB_HOST": "localhost",
        "CHROMADB_PORT": "8847",
        "CHROMADB_TOKEN": "fc-knowledge-base-token"
      }
    }
  }
}
EOF
    echo "  [OK] Created .mcp.json for Claude Code"
fi

echo ""
echo "============================================================"
echo "Setup Complete!"
echo "============================================================"
echo ""
echo "Next steps:"
echo ""
echo "  1. Configure AWS credentials in md/chromadb-docker/.env:"
echo "     AWS_ACCESS_KEY_ID=your_key"
echo "     AWS_SECRET_ACCESS_KEY=your_secret"
echo ""
echo "  2. Start ChromaDB:"
echo "     cd md/chromadb-docker && ./start-chromadb.sh"
echo ""
echo "  3. Ingest the knowledge base (one-time):"
echo "     cd md/chromadb-docker && ./ingest.sh"
echo ""
echo "  4. Start Claude Code in this directory"
echo ""
echo "For daily use, just run:"
echo "  cd md/chromadb-docker && ./start-chromadb.sh"
echo ""
