#!/usr/bin/env python3
"""
Ingest FC Knowledge Base documents into ChromaDB with AWS Bedrock embeddings.

This script:
1. Extracts documents from the full KB ZIP file
2. Chunks documents intelligently (respecting markdown structure)
3. Generates high-quality embeddings using AWS Bedrock Titan V1 (1536 dimensions)
4. Stores in ChromaDB running in Docker

Usage:
    python ingest-to-chromadb.py
"""

import hashlib
import logging
import re
import sys
import time
import zipfile
from pathlib import Path
from typing import List, Dict

import chromadb
from chromadb.config import Settings

from config import (
    CHROMADB_HOST,
    CHROMADB_PORT,
    CHROMADB_TOKEN,
    FULL_COLLECTION,
    MAX_CHUNK_SIZE,
    CHUNK_OVERLAP,
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
FULL_ZIP = SCRIPT_DIR / "FC-Full-KnowledgeBase.zip"


def get_chromadb_client() -> chromadb.HttpClient:
    """Connect to ChromaDB Docker container."""
    logger.info(f"Connecting to ChromaDB at {CHROMADB_HOST}:{CHROMADB_PORT}...")

    client = chromadb.HttpClient(
        host=CHROMADB_HOST,
        port=CHROMADB_PORT,
        settings=Settings(
            anonymized_telemetry=False,
            chroma_client_auth_provider="chromadb.auth.token_authn.TokenAuthClientProvider",
            chroma_client_auth_credentials=CHROMADB_TOKEN,
        ),
    )

    # Test connection
    try:
        heartbeat = client.heartbeat()
        logger.info(f"Connected to ChromaDB (heartbeat: {heartbeat})")
    except Exception as e:
        logger.error(f"Failed to connect to ChromaDB: {e}")
        logger.error("Make sure ChromaDB is running: ./start-chromadb.sh")
        sys.exit(1)

    return client


def get_document_id(content: str, source: str) -> str:
    """Generate unique document ID from content and source."""
    hash_input = f"{source}:{content[:500]}"
    return hashlib.md5(hash_input.encode()).hexdigest()


def classify_document(filepath: str) -> Dict[str, str]:
    """Extract metadata from document path."""
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
    ifrs_match = re.search(r"(IFRS\s*\d+|IAS\s*\d+)", filepath, re.IGNORECASE)
    if ifrs_match:
        metadata["ifrs_standard"] = ifrs_match.group(1).upper().replace(" ", "")

    return metadata


def chunk_document(content: str, max_size: int = MAX_CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> List[str]:
    """
    Split document into chunks, respecting markdown structure.

    Tries to split on:
    1. Markdown headers (## or ###)
    2. Paragraph breaks
    3. Character boundaries (last resort)
    """
    if len(content) <= max_size:
        return [content]

    chunks = []

    # Try to split on markdown headers
    sections = re.split(r"\n(#{1,3}\s+[^\n]+)\n", content)

    current_chunk = ""
    for section in sections:
        if len(current_chunk) + len(section) <= max_size:
            current_chunk += section + "\n"
        else:
            if current_chunk.strip():
                chunks.append(current_chunk.strip())

            # Handle oversized sections
            if len(section) > max_size:
                paragraphs = section.split("\n\n")
                for para in paragraphs:
                    if len(para) <= max_size:
                        if len(current_chunk) + len(para) <= max_size:
                            current_chunk += para + "\n\n"
                        else:
                            if current_chunk.strip():
                                chunks.append(current_chunk.strip())
                            current_chunk = para + "\n\n"
                    else:
                        # Character split with overlap
                        for i in range(0, len(para), max_size - overlap):
                            chunks.append(para[i : i + max_size])
                        current_chunk = ""
            else:
                current_chunk = section + "\n"

    if current_chunk.strip():
        chunks.append(current_chunk.strip())

    return [c for c in chunks if c.strip()]


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
        logger.error("Run ./create-knowledge-zips.sh first")
        return 0

    # Delete existing collection if present
    try:
        client.delete_collection(collection_name)
        logger.info(f"Deleted existing collection '{collection_name}'")
    except Exception:
        pass

    # Create new collection with Bedrock embeddings and COSINE distance
    collection = client.create_collection(
        name=collection_name,
        embedding_function=embedding_function,
        metadata={
            "description": f"FC Knowledge Base - {collection_name}",
            "hnsw:space": "cosine",  # CRITICAL: Use cosine distance for semantic search
        },
    )

    documents = []
    metadatas = []
    ids = []

    # Extract and process documents
    with zipfile.ZipFile(zip_path, "r") as zf:
        file_list = [f for f in zf.namelist() if f.endswith((".md", ".yaml", ".yml"))]
        logger.info(f"Found {len(file_list)} files in ZIP")

        for filepath in file_list:
            try:
                content = zf.read(filepath).decode("utf-8", errors="ignore")
                if not content.strip():
                    continue

                metadata = classify_document(filepath)
                chunks = chunk_document(content)

                for i, chunk in enumerate(chunks):
                    if not chunk.strip():
                        continue

                    doc_id = get_document_id(chunk, f"{filepath}:{i}")

                    chunk_metadata = metadata.copy()
                    if len(chunks) > 1:
                        chunk_metadata["chunk"] = f"{i + 1}/{len(chunks)}"

                    documents.append(chunk)
                    metadatas.append(chunk_metadata)
                    ids.append(doc_id)

            except Exception as e:
                logger.warning(f"Error processing {filepath}: {e}")
                continue

    # Add documents in batches (Bedrock has rate limits)
    total_added = 0
    logger.info(f"Adding {len(documents)} chunks in batches of {BATCH_SIZE}...")

    for i in range(0, len(documents), BATCH_SIZE):
        batch_docs = documents[i : i + BATCH_SIZE]
        batch_metas = metadatas[i : i + BATCH_SIZE]
        batch_ids = ids[i : i + BATCH_SIZE]

        try:
            collection.add(
                documents=batch_docs,
                metadatas=batch_metas,
                ids=batch_ids,
            )
            total_added += len(batch_docs)
            logger.info(f"  Batch {i // BATCH_SIZE + 1}: added {len(batch_docs)} chunks (total: {total_added})")

            # Small delay to avoid rate limiting
            time.sleep(0.5)

        except Exception as e:
            logger.error(f"Error adding batch: {e}")
            # Retry with exponential backoff
            time.sleep(2)
            try:
                collection.add(
                    documents=batch_docs,
                    metadatas=batch_metas,
                    ids=batch_ids,
                )
                total_added += len(batch_docs)
                logger.info(f"  Batch {i // BATCH_SIZE + 1}: retry succeeded")
            except Exception as e2:
                logger.error(f"Retry failed: {e2}")

    final_count = collection.count()
    logger.info(f"Collection '{collection_name}' now has {final_count} documents")
    return final_count


def main():
    logger.info("=" * 60)
    logger.info("FC Knowledge Base - ChromaDB Ingestion")
    logger.info("Using Titan V1 (1536 dimensions)")
    logger.info("=" * 60)

    # Initialize embedding function
    logger.info("Initializing Titan V1 embedding function...")
    embedding_function = get_embedding_function()

    # Connect to ChromaDB
    client = get_chromadb_client()

    # Process Full Knowledge Base
    count = process_zip(
        FULL_ZIP,
        FULL_COLLECTION,
        client,
        embedding_function,
    )

    # Summary
    logger.info("=" * 60)
    logger.info("INGESTION COMPLETE")
    logger.info("=" * 60)
    logger.info(f"  Full Collection: {count} chunks")
    logger.info("")
    logger.info("ChromaDB URL: http://localhost:8847")
    logger.info("")
    logger.info("Next steps:")
    logger.info("  1. Add MCP server to Claude Code settings")
    logger.info("  2. Restart Claude Code")
    logger.info("  3. Use search_fc_full tool")


if __name__ == "__main__":
    main()
