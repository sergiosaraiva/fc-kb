#!/usr/bin/env python3
"""
MCP Server for FC Knowledge Base RAG with AWS Bedrock Embeddings

This server connects Claude Code to the ChromaDB knowledge base using the
Model Context Protocol (MCP). It provides semantic search over the full
FC knowledge base including business concepts and technical implementation.

Uses AWS Bedrock Titan embeddings for high-quality semantic search.
"""

import json
import logging
from typing import Optional, Dict, List, Any

import chromadb
from chromadb.config import Settings
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

import re

from config import (
    CHROMADB_HOST,
    CHROMADB_PORT,
    CHROMADB_TOKEN,
    FULL_COLLECTION,
    RETRIEVAL_CANDIDATE_COUNT,
    RETRIEVAL_MIN_RESULTS,
    RETRIEVAL_MAX_RESULTS,
    RELEVANCE_THRESHOLD,
)
from titan_v1_embeddings import get_embedding_function


def extract_content_only(chunk_text: str) -> str:
    """
    Extract only the actual content from LLM-enhanced chunks.

    LLM-enhanced chunks have metadata (summary, questions, keywords) that helped
    with embedding quality but is redundant when displaying results.
    This function extracts only the core content section.
    """
    # Try to find the "## Content" section (LLM-enhanced chunks)
    content_match = re.search(r'## Content\s*\n(.*?)(?=\n## Related Topics|\n---|\Z)', chunk_text, re.DOTALL)
    if content_match:
        return content_match.group(1).strip()

    # Fallback: try to find content after Keywords section
    context_end = re.search(r'\*\*Keywords:\*\*.*?\n\n(.*?)(?=\n## Related Topics|\n---|\Z)', chunk_text, re.DOTALL)
    if context_end:
        return context_end.group(1).strip()

    # If no markers found, return full content (pre-chunked or different format)
    return chunk_text

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("fc-knowledge-mcp")

# Initialize MCP server
server = Server("fc-knowledge-base")

# Global state
_chroma_client: Optional[chromadb.HttpClient] = None
_embedding_function = None


def get_chroma_client() -> chromadb.HttpClient:
    """Get or create ChromaDB client."""
    global _chroma_client
    if _chroma_client is None:
        _chroma_client = chromadb.HttpClient(
            host=CHROMADB_HOST,
            port=CHROMADB_PORT,
            settings=Settings(
                anonymized_telemetry=False,
                chroma_client_auth_provider="chromadb.auth.token_authn.TokenAuthClientProvider",
                chroma_client_auth_credentials=CHROMADB_TOKEN,
            ),
        )
    return _chroma_client


def get_embeddings():
    """Get embedding function (lazy init)."""
    global _embedding_function
    if _embedding_function is None:
        _embedding_function = get_embedding_function()
    return _embedding_function


def search_collection(
    collection_name: str,
    query: str,
    metadata_filter: Optional[Dict[str, Any]] = None,
    min_relevance: float = RELEVANCE_THRESHOLD,
) -> List[Dict]:
    """
    Search a ChromaDB collection using dynamic relevance-based retrieval.

    Fetches more candidates than needed, then filters by relevance threshold
    to return only high-quality results. This prevents returning irrelevant
    results while ensuring good matches aren't missed.

    Args:
        collection_name: Name of the collection to search
        query: Search query text
        metadata_filter: Optional metadata filter (e.g., {"layer": "database"})
        min_relevance: Minimum relevance score (0-1) to include in results

    Returns:
        List of result dictionaries with content, metadata, and relevance scores
        Sorted by relevance (best first), filtered by threshold
    """
    client = get_chroma_client()
    embedding_func = get_embeddings()

    try:
        collection = client.get_collection(
            name=collection_name,
            embedding_function=embedding_func,
        )
    except Exception as e:
        logger.error(f"Collection {collection_name} not found: {e}")
        return []

    # Generate query embedding using Cohere (optimized for queries)
    query_embedding = embedding_func.embed_query(query)

    # Fetch more candidates than we'll return for quality filtering
    kwargs = {
        "query_embeddings": [query_embedding],
        "n_results": RETRIEVAL_CANDIDATE_COUNT,
        "include": ["documents", "metadatas", "distances"],
    }
    if metadata_filter:
        kwargs["where"] = metadata_filter

    results = collection.query(**kwargs)

    # Format and filter results by relevance
    formatted = []
    if results and results["documents"]:
        for i, doc in enumerate(results["documents"][0]):
            distance = results["distances"][0][i] if results["distances"] else 0
            # Convert distance to relevance (cosine distance: 0=identical, 2=opposite)
            relevance = max(0, 1 - (distance / 2))

            formatted.append({
                "content": doc,
                "metadata": results["metadatas"][0][i] if results["metadatas"] else {},
                "distance": distance,
                "relevance": relevance,
            })

    # Sort by relevance (best first)
    formatted.sort(key=lambda x: x["relevance"], reverse=True)

    # Apply dynamic filtering
    # 1. Always include results above threshold
    # 2. Ensure minimum results (even if below threshold)
    # 3. Cap at maximum results
    above_threshold = [r for r in formatted if r["relevance"] >= min_relevance]

    if len(above_threshold) >= RETRIEVAL_MIN_RESULTS:
        # Enough good results - return up to max
        return above_threshold[:RETRIEVAL_MAX_RESULTS]
    else:
        # Not enough above threshold - return at least min results
        return formatted[:max(RETRIEVAL_MIN_RESULTS, len(above_threshold))]


@server.list_tools()
async def list_tools() -> List[Tool]:
    """List available tools for Claude Code."""
    return [
        Tool(
            name="search_fc_full",
            description="""Search the FC knowledge base for financial consolidation information.

Use this for:
- Consolidation concepts (equity method, global integration, proportional)
- IFRS/IAS standards questions (IFRS 3, IFRS 10, IAS 21, etc.)
- Allen White's Direct Consolidation theory
- Elimination types and when to use them
- Currency translation questions
- Ownership and control questions
- Stored procedure details (P_CONSO_*, P_CALC_*, P_SYS_*)
- Database table schemas (TS*, TD*, TM_*)
- API handler signatures and parameters
- C# service implementations
- TypeScript/Frontend patterns
- Code patterns and templates
- Technical troubleshooting

Returns relevant passages including code examples.
Uses AWS Bedrock Titan V1 (1536 dimensions) for high-quality semantic search.
Results are dynamically filtered by relevance - returns 3-15 results based on quality.""",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The search query - can include procedure names, table names, or technical concepts",
                    },
                    "layer_filter": {
                        "type": "string",
                        "description": "Optional: filter by technical layer",
                        "enum": ["business", "database", "application", "frontend", "api"],
                    },
                },
                "required": ["query"],
            },
        ),
        Tool(
            name="get_fc_kb_stats",
            description="Get statistics about the FC Knowledge Base collection (document counts, etc.)",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": [],
            },
        ),
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict) -> List[TextContent]:
    """Handle tool calls from Claude Code."""

    if name == "search_fc_full":
        query = arguments.get("query", "")
        layer_filter = arguments.get("layer_filter")

        metadata_filter = None
        if layer_filter:
            metadata_filter = {"layer": layer_filter}

        results = search_collection(
            FULL_COLLECTION,
            query,
            metadata_filter=metadata_filter,
        )

        if not results:
            return [
                TextContent(
                    type="text",
                    text="No results found in FC knowledge base. The database may not be initialized yet.\n\nRun: ./start-chromadb.sh && python ingest-to-chromadb.py",
                )
            ]

        # Format response with dynamic result count info
        above_threshold = sum(1 for r in results if r["relevance"] >= RELEVANCE_THRESHOLD)
        response = f"## FC Knowledge Search Results\n\n"
        response += f"**Query**: {query}\n"
        response += f"**Results**: {len(results)} ({above_threshold} above {RELEVANCE_THRESHOLD:.0%} threshold)\n\n"

        for i, r in enumerate(results, 1):
            source = r["metadata"].get("source", "Unknown")
            layer = r["metadata"].get("layer", "")
            topic = r["metadata"].get("topic", "")
            relevance = r["relevance"]
            relevance_str = f"{relevance:.1%}"

            # Visual indicator for result quality
            if relevance >= 0.75:
                quality = "HIGH"
            elif relevance >= RELEVANCE_THRESHOLD:
                quality = "GOOD"
            else:
                quality = "LOW"

            response += f"### Result {i} (Relevance: {relevance_str} - {quality})\n"
            response += f"**Source**: {source}\n"
            if layer:
                response += f"**Layer**: {layer}\n"
            if topic:
                response += f"**Topic**: {topic}\n"
            # Extract core content only (strip LLM enhancement metadata)
            content = extract_content_only(r["content"])
            response += f"\n{content}\n\n---\n\n"

        return [TextContent(type="text", text=response)]

    elif name == "get_fc_kb_stats":
        client = get_chroma_client()
        stats = {}

        try:
            coll = client.get_collection(FULL_COLLECTION)
            stats[FULL_COLLECTION] = {
                "document_count": coll.count(),
                "name": coll.name,
            }
        except Exception:
            stats[FULL_COLLECTION] = {"status": "not initialized"}

        return [
            TextContent(
                type="text",
                text=f"## FC Knowledge Base Statistics\n\n```json\n{json.dumps(stats, indent=2)}\n```",
            )
        ]

    return [TextContent(type="text", text=f"Unknown tool: {name}")]


async def main():
    """Run the MCP server."""
    logger.info("Starting FC Knowledge Base MCP Server...")
    logger.info(f"ChromaDB: {CHROMADB_HOST}:{CHROMADB_PORT}")
    logger.info("Using AWS Bedrock Titan V1 (1536 dimensions)")
    logger.info(f"Dynamic retrieval: {RETRIEVAL_MIN_RESULTS}-{RETRIEVAL_MAX_RESULTS} results, {RELEVANCE_THRESHOLD:.0%} threshold")

    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
