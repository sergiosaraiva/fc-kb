#!/usr/bin/env python3
"""
Ingest documents from ZIP files into ChromaDB for the FC Knowledge Base.
Run this once to populate the vector database.
"""

import hashlib
import logging
import os
import re
import zipfile
from pathlib import Path
from typing import Optional

import chromadb
from chromadb.config import Settings

# Optional: Use sentence-transformers for better embeddings
# If not installed, ChromaDB will use its default embedding function
try:
    from sentence_transformers import SentenceTransformer
    HAVE_SENTENCE_TRANSFORMERS = True
except ImportError:
    HAVE_SENTENCE_TRANSFORMERS = False
    print("Note: sentence-transformers not installed. Using ChromaDB default embeddings.")

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Configuration
SCRIPT_DIR = Path(__file__).parent
CHROMA_PERSIST_DIR = SCRIPT_DIR / "chroma_db"
BUSINESS_ZIP = SCRIPT_DIR.parent / "RAG-Business-KnowledgeBase.zip"
TECHNICAL_ZIP = SCRIPT_DIR.parent / "RAG-Technical-KnowledgeBase.zip"

# Chunk configuration
MAX_CHUNK_SIZE = 1500  # characters
CHUNK_OVERLAP = 200


def get_document_id(content: str, source: str) -> str:
    """Generate a unique document ID."""
    hash_input = f"{source}:{content[:500]}"
    return hashlib.md5(hash_input.encode()).hexdigest()


def classify_document(filepath: str) -> dict:
    """Classify document and extract metadata based on path."""
    metadata = {
        "source": filepath,
        "topic": "general",
        "layer": "business",
        "audience": "business"
    }

    filepath_lower = filepath.lower()

    # Classify by folder/path
    if "direct_consolidation_chunks" in filepath_lower:
        metadata["topic"] = "theory"
        metadata["source_type"] = "theory"
    elif "12-user-knowledge-base" in filepath_lower or "help-content" in filepath_lower:
        metadata["topic"] = "help"
        metadata["source_type"] = "help"
    elif "02-consolidation-methods" in filepath_lower:
        metadata["topic"] = "consolidation-methods"
    elif "03-core-calculations" in filepath_lower:
        metadata["topic"] = "calculations"
    elif "04-elimination" in filepath_lower:
        metadata["topic"] = "eliminations"
    elif "05-currency" in filepath_lower:
        metadata["topic"] = "currency"
    elif "06-ownership" in filepath_lower:
        metadata["topic"] = "ownership"
    elif "07-database" in filepath_lower:
        metadata["topic"] = "database"
        metadata["layer"] = "database"
        metadata["audience"] = "technical"
    elif "08-application" in filepath_lower:
        metadata["topic"] = "application"
        metadata["layer"] = "application"
        metadata["audience"] = "technical"
    elif "09-frontend" in filepath_lower:
        metadata["topic"] = "frontend"
        metadata["layer"] = "frontend"
        metadata["audience"] = "technical"
    elif "11-agent-support" in filepath_lower:
        metadata["topic"] = "api"
        metadata["layer"] = "api"
        metadata["audience"] = "technical"
    elif "10-gap-analysis" in filepath_lower:
        metadata["topic"] = "gaps"
    elif "discrepancy" in filepath_lower:
        metadata["topic"] = "discrepancy"
    elif "ui-to-theory" in filepath_lower:
        metadata["topic"] = "ui-mapping"
    elif "troubleshooting" in filepath_lower:
        metadata["topic"] = "troubleshooting"
    elif "appendices" in filepath_lower or "glossary" in filepath_lower:
        metadata["topic"] = "reference"

    # Extract IFRS standards if mentioned
    ifrs_match = re.search(r'(IFRS\s*\d+|IAS\s*\d+)', filepath, re.IGNORECASE)
    if ifrs_match:
        metadata["ifrs_standard"] = ifrs_match.group(1).upper().replace(" ", "")

    return metadata


def chunk_document(content: str, max_size: int = MAX_CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> list[str]:
    """Split document into chunks, trying to respect section boundaries."""
    if len(content) <= max_size:
        return [content]

    chunks = []

    # Try to split on markdown headers first
    sections = re.split(r'\n(#{1,3}\s+[^\n]+)\n', content)

    current_chunk = ""
    for section in sections:
        if len(current_chunk) + len(section) <= max_size:
            current_chunk += section + "\n"
        else:
            if current_chunk:
                chunks.append(current_chunk.strip())
            # If section itself is too large, split by paragraphs
            if len(section) > max_size:
                paragraphs = section.split('\n\n')
                for para in paragraphs:
                    if len(para) <= max_size:
                        if len(current_chunk) + len(para) <= max_size:
                            current_chunk += para + "\n\n"
                        else:
                            if current_chunk:
                                chunks.append(current_chunk.strip())
                            current_chunk = para + "\n\n"
                    else:
                        # Last resort: split by characters with overlap
                        for i in range(0, len(para), max_size - overlap):
                            chunks.append(para[i:i + max_size])
                        current_chunk = ""
            else:
                current_chunk = section + "\n"

    if current_chunk:
        chunks.append(current_chunk.strip())

    return [c for c in chunks if c.strip()]


def process_zip_to_collection(
    zip_path: Path,
    collection_name: str,
    client: chromadb.PersistentClient
) -> int:
    """Extract documents from ZIP and add to ChromaDB collection."""

    logger.info(f"Processing {zip_path.name} into collection '{collection_name}'...")

    # Get or create collection
    try:
        client.delete_collection(collection_name)
        logger.info(f"Deleted existing collection '{collection_name}'")
    except Exception:
        pass

    collection = client.create_collection(
        name=collection_name,
        metadata={"description": f"FC Knowledge Base - {collection_name}"}
    )

    documents = []
    metadatas = []
    ids = []

    with zipfile.ZipFile(zip_path, 'r') as zf:
        file_list = [f for f in zf.namelist() if f.endswith(('.md', '.yaml', '.yml'))]
        logger.info(f"Found {len(file_list)} documents in ZIP")

        for filepath in file_list:
            try:
                content = zf.read(filepath).decode('utf-8', errors='ignore')

                if not content.strip():
                    continue

                # Get metadata
                metadata = classify_document(filepath)

                # Chunk the document
                chunks = chunk_document(content)

                for i, chunk in enumerate(chunks):
                    if not chunk.strip():
                        continue

                    doc_id = get_document_id(chunk, f"{filepath}:{i}")

                    # Add chunk number to metadata if multiple chunks
                    chunk_metadata = metadata.copy()
                    if len(chunks) > 1:
                        chunk_metadata["chunk"] = f"{i+1}/{len(chunks)}"

                    documents.append(chunk)
                    metadatas.append(chunk_metadata)
                    ids.append(doc_id)

            except Exception as e:
                logger.warning(f"Error processing {filepath}: {e}")
                continue

    # Add documents in batches
    batch_size = 500
    total_added = 0

    for i in range(0, len(documents), batch_size):
        batch_docs = documents[i:i + batch_size]
        batch_metas = metadatas[i:i + batch_size]
        batch_ids = ids[i:i + batch_size]

        try:
            collection.add(
                documents=batch_docs,
                metadatas=batch_metas,
                ids=batch_ids
            )
            total_added += len(batch_docs)
            logger.info(f"Added batch {i//batch_size + 1}: {len(batch_docs)} documents (total: {total_added})")
        except Exception as e:
            logger.error(f"Error adding batch: {e}")

    logger.info(f"Collection '{collection_name}' now has {collection.count()} documents")
    return collection.count()


def main():
    """Main ingestion process."""
    logger.info("=" * 60)
    logger.info("FC Knowledge Base - ChromaDB Ingestion")
    logger.info("=" * 60)

    # Verify ZIP files exist
    if not BUSINESS_ZIP.exists():
        logger.error(f"Business ZIP not found: {BUSINESS_ZIP}")
        logger.error("Please ensure RAG-Business-KnowledgeBase.zip exists in the parent directory")
        return

    if not TECHNICAL_ZIP.exists():
        logger.error(f"Technical ZIP not found: {TECHNICAL_ZIP}")
        logger.error("Please ensure RAG-Technical-KnowledgeBase.zip exists in the parent directory")
        return

    # Initialize ChromaDB
    logger.info(f"Initializing ChromaDB at: {CHROMA_PERSIST_DIR}")
    CHROMA_PERSIST_DIR.mkdir(parents=True, exist_ok=True)

    client = chromadb.PersistentClient(
        path=str(CHROMA_PERSIST_DIR),
        settings=Settings(anonymized_telemetry=False)
    )

    # Process Business Knowledge Base
    business_count = process_zip_to_collection(
        BUSINESS_ZIP,
        "business_knowledge",
        client
    )

    # Process Technical Knowledge Base
    technical_count = process_zip_to_collection(
        TECHNICAL_ZIP,
        "technical_knowledge",
        client
    )

    # Summary
    logger.info("=" * 60)
    logger.info("INGESTION COMPLETE")
    logger.info("=" * 60)
    logger.info(f"Business Collection: {business_count} chunks")
    logger.info(f"Technical Collection: {technical_count} chunks")
    logger.info(f"Database Location: {CHROMA_PERSIST_DIR}")
    logger.info("")
    logger.info("Next steps:")
    logger.info("1. Add MCP server to Claude Code settings")
    logger.info("2. Restart Claude Code")
    logger.info("3. Use search_business_knowledge or search_technical_knowledge tools")


if __name__ == "__main__":
    main()
