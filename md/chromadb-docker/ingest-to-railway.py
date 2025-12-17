#!/usr/bin/env python3
"""
Ingest FC Knowledge Base documents into Railway-hosted ChromaDB.

This script:
1. Connects to ChromaDB on Railway (HTTPS)
2. Extracts pre-chunked documents from the KB ZIP file
3. Generates embeddings using AWS Bedrock Titan V1
4. Stores in ChromaDB

Usage:
    python ingest-to-railway.py                           # Use FC-Business-KnowledgeBase.zip
    python ingest-to-railway.py --zip FC-Full-KnowledgeBase.zip  # Use specific ZIP

Environment variables required:
    CHROMADB_HOST=fc-kb-chromadb.up.railway.app
    CHROMADB_TOKEN=your-token
    AWS_ACCESS_KEY_ID=your-key
    AWS_SECRET_ACCESS_KEY=your-secret
    AWS_DEFAULT_REGION=us-east-1
"""

import argparse
import hashlib
import logging
import os
import re
import sys
import time
import zipfile
from pathlib import Path
from typing import Dict

import chromadb
from chromadb.config import Settings

from config import (
    FULL_COLLECTION,
    BATCH_SIZE,
    TOPICS,
    LAYERS,
)
from titan_v1_embeddings import get_embedding_function

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Paths
SCRIPT_DIR = Path(__file__).parent
DEFAULT_ZIP = SCRIPT_DIR / "FC-Business-KnowledgeBase.zip"

# Railway ChromaDB settings (override from env)
RAILWAY_HOST = os.environ.get("CHROMADB_HOST", "fc-kb-chromadb.up.railway.app")
RAILWAY_PORT = int(os.environ.get("CHROMADB_PORT", "443"))
RAILWAY_TOKEN = os.environ.get("CHROMADB_TOKEN", "fc-knowledge-base-token")


def get_chromadb_client() -> chromadb.HttpClient:
    """Connect to ChromaDB on Railway via HTTPS."""
    logger.info(f"Connecting to ChromaDB at {RAILWAY_HOST}:{RAILWAY_PORT} (SSL)...")

    client = chromadb.HttpClient(
        host=RAILWAY_HOST,
        port=RAILWAY_PORT,
        ssl=True,  # Railway uses HTTPS
        settings=Settings(
            anonymized_telemetry=False,
            chroma_client_auth_provider="chromadb.auth.token_authn.TokenAuthClientProvider",
            chroma_client_auth_credentials=RAILWAY_TOKEN,
        ),
    )

    # Test connection
    try:
        heartbeat = client.heartbeat()
        logger.info(f"Connected to ChromaDB (heartbeat: {heartbeat})")
    except Exception as e:
        logger.error(f"Failed to connect to ChromaDB: {e}")
        logger.error(f"Host: {RAILWAY_HOST}")
        logger.error(f"Port: {RAILWAY_PORT}")
        logger.error("Check CHROMADB_HOST, CHROMADB_PORT, and CHROMADB_TOKEN env vars")
        sys.exit(1)

    return client


def get_document_id(content: str, source: str) -> str:
    """Generate unique document ID from content and source."""
    hash_input = f"{source}:{content[:500]}"
    return hashlib.md5(hash_input.encode()).hexdigest()


def classify_document(filepath: str, content: str) -> Dict[str, str]:
    """Extract metadata from document path and content."""
    metadata = {
        "source": filepath,
        "topic": "general",
        "layer": "business",
        "audience": "business",
    }

    filepath_lower = filepath.lower()

    # Determine topic
    for topic, patterns in TOPICS.items():
        if any(p in filepath_lower for p in patterns):
            metadata["topic"] = topic
            break

    # Determine layer
    for layer, patterns in LAYERS.items():
        if any(p in filepath_lower for p in patterns):
            metadata["layer"] = layer
            if layer in ["database", "application", "frontend", "api"]:
                metadata["audience"] = "technical"
            break

    # Extract IFRS standard if mentioned
    ifrs_match = re.search(r"(IFRS\s*\d+|IAS\s*\d+)", content, re.IGNORECASE)
    if ifrs_match:
        metadata["ifrs_standard"] = ifrs_match.group(1).upper().replace(" ", "")

    # Extract document title
    title_match = re.search(r"^\*\*Document:\*\*\s*(.+?)(?:\s*$|\s{2})", content, re.MULTILINE)
    if title_match:
        metadata["document"] = title_match.group(1).strip()

    # Extract section
    section_match = re.search(r"^#\s+(.+?)$", content, re.MULTILINE)
    if section_match:
        metadata["section"] = section_match.group(1).strip()[:100]

    # Extract keywords
    keywords_match = re.search(r"^\*\*Keywords:\*\*\s*(.+?)$", content, re.MULTILINE)
    if keywords_match:
        metadata["keywords"] = keywords_match.group(1).strip()[:200]

    return metadata


def process_zip(
    zip_path: Path,
    collection_name: str,
    client: chromadb.HttpClient,
    embedding_function,
) -> int:
    """
    Extract documents from ZIP and add to ChromaDB collection.
    Returns number of documents added.
    """
    logger.info(f"Processing {zip_path.name} into collection '{collection_name}'...")

    if not zip_path.exists():
        logger.error(f"ZIP file not found: {zip_path}")
        logger.error("Run create-business-zip.py first")
        return 0

    # Delete existing collection if present
    try:
        client.delete_collection(collection_name)
        logger.info(f"Deleted existing collection '{collection_name}'")
    except Exception:
        pass

    # Create new collection with Bedrock embeddings
    collection = client.create_collection(
        name=collection_name,
        embedding_function=embedding_function,
        metadata={
            "description": f"FC Knowledge Base - {collection_name}",
            "hnsw:space": "cosine",
        },
    )

    documents = []
    metadatas = []
    ids = []

    # Extract and process documents
    with zipfile.ZipFile(zip_path, "r") as zf:
        file_list = [f for f in zf.namelist() if f.endswith((".md", ".yaml", ".yml"))]
        logger.info(f"Found {len(file_list)} pre-chunked files in ZIP")

        for filepath in file_list:
            try:
                content = zf.read(filepath).decode("utf-8", errors="ignore")
                content = content.replace('\r\n', '\n').replace('\r', '\n')
                if not content.strip():
                    continue

                metadata = classify_document(filepath, content)
                doc_id = get_document_id(content, filepath)

                documents.append(content)
                metadatas.append(metadata)
                ids.append(doc_id)

            except Exception as e:
                logger.warning(f"Error processing {filepath}: {e}")
                continue

    # Add documents in batches
    total_added = 0
    logger.info(f"Adding {len(documents)} semantic chunks in batches of {BATCH_SIZE}...")

    for i in range(0, len(documents), BATCH_SIZE):
        batch_docs = documents[i : i + BATCH_SIZE]
        batch_metas = metadatas[i : i + BATCH_SIZE]
        batch_ids = ids[i : i + BATCH_SIZE]

        retry_count = 0
        max_retries = 3

        while retry_count < max_retries:
            try:
                collection.add(
                    documents=batch_docs,
                    metadatas=batch_metas,
                    ids=batch_ids,
                )
                total_added += len(batch_docs)
                logger.info(f"  Batch {i // BATCH_SIZE + 1}: added {len(batch_docs)} chunks (total: {total_added})")
                time.sleep(0.5)  # Rate limiting
                break

            except Exception as e:
                retry_count += 1
                wait_time = 2 ** retry_count
                logger.warning(f"Batch failed (attempt {retry_count}): {e}")
                if retry_count < max_retries:
                    logger.info(f"  Retrying in {wait_time}s...")
                    time.sleep(wait_time)
                else:
                    logger.error(f"  Batch failed after {max_retries} attempts")

    final_count = collection.count()
    logger.info(f"Collection '{collection_name}' now has {final_count} documents")
    return final_count


def main():
    parser = argparse.ArgumentParser(
        description="Ingest FC Knowledge Base into Railway ChromaDB"
    )
    parser.add_argument(
        "--zip",
        type=str,
        default=str(DEFAULT_ZIP),
        help=f"ZIP file to ingest (default: {DEFAULT_ZIP.name})"
    )
    args = parser.parse_args()

    zip_path = Path(args.zip)
    if not zip_path.is_absolute():
        zip_path = SCRIPT_DIR / zip_path

    logger.info("=" * 60)
    logger.info("FC Knowledge Base - Railway ChromaDB Ingestion")
    logger.info(f"Target: https://{RAILWAY_HOST}")
    logger.info(f"ZIP: {zip_path.name}")
    logger.info("=" * 60)

    # Initialize embedding function
    logger.info("Initializing Titan V1 embedding function...")
    embedding_function = get_embedding_function()

    # Connect to Railway ChromaDB
    client = get_chromadb_client()

    # Process ZIP
    count = process_zip(
        zip_path,
        FULL_COLLECTION,
        client,
        embedding_function,
    )

    # Summary
    logger.info("=" * 60)
    logger.info("INGESTION COMPLETE")
    logger.info("=" * 60)
    logger.info(f"  Collection: {FULL_COLLECTION}")
    logger.info(f"  Documents: {count}")
    logger.info(f"  Target: https://{RAILWAY_HOST}")
    logger.info("=" * 60)


if __name__ == "__main__":
    main()
