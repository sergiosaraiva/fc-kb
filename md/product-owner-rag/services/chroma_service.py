"""
ChromaDB Service for Product Owner RAG Application.

Provides ChromaDB client initialization and search functionality
for the FC Knowledge Base.
"""

import logging
import os
import re
from typing import List, Dict

import chromadb
import streamlit as st
from chromadb.config import Settings

# Import configuration and embeddings
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))
from config import (
    CHROMADB_HOST,
    CHROMADB_PORT,
    CHROMADB_TOKEN,
    FULL_COLLECTION,
)
from titan_v1_embeddings import get_embedding_function

# Configure logging
logger = logging.getLogger("product-owner-rag.chroma")

# Retrieval configuration
BUSINESS_LAYER_RESULTS = 8   # More smaller chunks = better coverage + fast response
RELEVANCE_THRESHOLD = 0.35   # Lowered from 0.55 - more permissive for business users


def extract_content_only(chunk_text: str) -> str:
    """
    Extract only the actual content from LLM-enhanced chunks.

    LLM-enhanced chunks have metadata (summary, questions, keywords) that helped
    with embedding quality but shouldn't be sent to Claude as context.
    This function strips the metadata and returns only the core content.

    Args:
        chunk_text: Raw chunk text that may contain LLM-enhanced metadata.

    Returns:
        Cleaned content string without metadata sections.
    """
    # Try to find the "## Content" section (LLM-enhanced chunks)
    content_match = re.search(r'## Content\s*\n(.*?)(?=\n## Related Topics|\n---|\Z)', chunk_text, re.DOTALL)
    if content_match:
        return content_match.group(1).strip()

    # Fallback: try to find content after "## Context" section ends
    context_end = re.search(r'\*\*Keywords:\*\*.*?\n\n(.*?)(?=\n## Related Topics|\n---|\Z)', chunk_text, re.DOTALL)
    if context_end:
        return context_end.group(1).strip()

    # If no markers found, return FULL original content (pre-chunked or different format)
    # No truncation - preserve all information
    return chunk_text


@st.cache_resource(show_spinner=False)
def get_chroma_client():
    """
    Get ChromaDB client (cached).

    Initializes a ChromaDB HTTP client with proper authentication
    and SSL configuration based on the port.

    Returns:
        chromadb.HttpClient: ChromaDB client, or None if connection fails.
    """
    try:
        # Use SSL for port 443 (Railway/cloud) or when explicitly set
        use_ssl = CHROMADB_PORT == 443 or os.environ.get("CHROMADB_SSL", "").lower() == "true"
        client = chromadb.HttpClient(
            host=CHROMADB_HOST,
            port=CHROMADB_PORT,
            ssl=use_ssl,
            settings=Settings(
                anonymized_telemetry=False,
                chroma_client_auth_provider="chromadb.auth.token_authn.TokenAuthClientProvider",
                chroma_client_auth_credentials=CHROMADB_TOKEN,
            ),
        )
        # Test connection
        client.heartbeat()
        return client
    except Exception as e:
        logger.error(f"Failed to connect to ChromaDB at {CHROMADB_HOST}:{CHROMADB_PORT}: {e}")
        st.error("Knowledge base unavailable. Please ensure ChromaDB is running.")
        return None


@st.cache_resource(show_spinner=False)
def get_embeddings():
    """
    Get embedding function (cached).

    Returns the Titan V1 embedding function for query embedding generation.

    Returns:
        Embedding function callable.
    """
    return get_embedding_function()


def search_business_layer(query: str, n_results: int = BUSINESS_LAYER_RESULTS, topic_filter: str = None) -> List[Dict]:
    """
    Search ChromaDB for business layer content only.

    Filters out technical implementation details (code, stored procedures, etc.)
    and returns only business concepts, theory, and user-facing information.

    Args:
        query: Search query text
        n_results: Number of results to retrieve
        topic_filter: Optional topic to filter results (e.g., "theory", "calculations")

    Returns:
        List of result dictionaries with content, metadata, and relevance scores
    """
    client = get_chroma_client()
    embedding_func = get_embeddings()

    if client is None:
        return []

    try:
        collection = client.get_collection(
            name=FULL_COLLECTION,
            embedding_function=embedding_func,
        )
    except Exception as e:
        logger.error(f"Collection not found: {e}")
        st.error("Knowledge base not initialized. Please contact administrator.")
        return []

    # Generate query embedding
    query_embedding = embedding_func.embed_query(query)

    # Build where filter
    if topic_filter and topic_filter != "all":
        # Combine layer and topic filters
        where_filter = {
            "$and": [
                {"layer": "business"},
                {"topic": topic_filter}
            ]
        }
    else:
        # Business layer only
        where_filter = {"layer": "business"}

    # Query with filters
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=n_results,
        where=where_filter,
        include=["documents", "metadatas", "distances"],
    )

    # Format results
    formatted = []
    all_results = []  # Track all results for debugging

    if results and results["documents"]:
        for i, doc in enumerate(results["documents"][0]):
            distance = results["distances"][0][i] if results["distances"] else 0
            relevance = max(0, 1 - (distance / 2))  # Convert distance to relevance

            result = {
                "content": doc,
                "metadata": results["metadatas"][0][i] if results["metadatas"] else {},
                "relevance": relevance,
                "distance": distance,
            }
            all_results.append(result)

            # Only include results above threshold
            if relevance >= RELEVANCE_THRESHOLD:
                formatted.append(result)

    # Debug logging
    logger.info(f"Query: '{query}' | Total results: {len(all_results)} | Above threshold: {len(formatted)}")
    if all_results and not formatted:
        max_relevance = max(r["relevance"] for r in all_results)
        logger.warning(f"All results filtered out! Max relevance: {max_relevance:.2f}, Threshold: {RELEVANCE_THRESHOLD:.2f}")

    # Sort by relevance
    formatted.sort(key=lambda x: x["relevance"], reverse=True)

    return formatted
