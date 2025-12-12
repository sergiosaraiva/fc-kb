"""
Configuration for FC Knowledge Base ChromaDB Integration
Uses AWS Bedrock for high-quality embeddings via Prophix AWS infrastructure
"""

import os

# =============================================================================
# ChromaDB Server Configuration
# =============================================================================
CHROMADB_HOST = os.environ.get("CHROMADB_HOST", "localhost")
CHROMADB_PORT = int(os.environ.get("CHROMADB_PORT", "8000"))  # Default 8000, local Docker uses 8847
CHROMADB_TOKEN = os.environ.get("CHROMADB_TOKEN", "fc-knowledge-base-token")

# Collection names (single unified collection)
FULL_COLLECTION = "fc_full_knowledge"

# =============================================================================
# AWS Bedrock Configuration (Prophix Infrastructure)
# =============================================================================
# Uses your existing AWS profile: prophix-devops
AWS_PROFILE = os.environ.get("AWS_PROFILE", "prophix-devops")
AWS_REGION = os.environ.get("AWS_DEFAULT_REGION", "us-east-1")

# Embedding model: Amazon Titan Text Embeddings V1 (1536 dimensions)
# First-party Amazon model - no marketplace subscription required
BEDROCK_EMBEDDING_MODEL = "amazon.titan-embed-text-v1"

# Embedding dimensions (1536 for Titan V1, fixed)
EMBEDDING_DIMENSIONS = 1536

# Alternative models (require marketplace access):
# - "cohere.embed-v4:0" (1536 dimensions, best quality - needs marketplace)
# - "cohere.embed-english-v3" (1024 dimensions - needs marketplace)
# - "amazon.titan-embed-text-v2:0" (1024 dimensions, no marketplace needed)

# =============================================================================
# Dynamic Retrieval Configuration
# =============================================================================
# Fetch more candidates than needed, then filter by relevance
RETRIEVAL_CANDIDATE_COUNT = 25  # Fetch this many candidates
RETRIEVAL_MIN_RESULTS = 3       # Always return at least this many
RETRIEVAL_MAX_RESULTS = 15      # Never return more than this
RELEVANCE_THRESHOLD = 0.55      # Minimum relevance score (0-1) to include

# =============================================================================
# Chunking Configuration
# =============================================================================
MAX_CHUNK_SIZE = 1500  # Characters per chunk
CHUNK_OVERLAP = 200    # Overlap between chunks
BATCH_SIZE = 25        # Documents per batch (Bedrock has rate limits)

# =============================================================================
# Metadata Configuration
# =============================================================================
# Topic classifications for search filtering
TOPICS = {
    "theory": ["direct_consolidation_chunks"],
    "consolidation-methods": ["02-consolidation-methods"],
    "calculations": ["03-core-calculations"],
    "eliminations": ["04-elimination"],
    "currency": ["05-currency"],
    "ownership": ["06-ownership"],
    "database": ["07-database"],
    "application": ["08-application"],
    "frontend": ["09-frontend"],
    "gaps": ["10-gap-analysis"],
    "agent-support": ["11-agent-support"],
    "help": ["12-user-knowledge-base"],
    "troubleshooting": ["17-troubleshooting"],
    "reference": ["20-appendices", "glossary"],
}

# Layer classifications
LAYERS = {
    "business": ["direct_consolidation_chunks", "02-", "03-", "04-", "05-", "06-", "10-", "12-", "17-", "20-"],
    "database": ["07-database"],
    "application": ["08-application"],
    "frontend": ["09-frontend"],
    "api": ["11-agent-support"],
}
