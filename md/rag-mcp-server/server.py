#!/usr/bin/env python3
"""
MCP Server for Financial Consolidation Knowledge Base RAG
Connects ChromaDB vector database to Claude Code via MCP protocol.
"""

import json
import logging
from pathlib import Path
from typing import Optional

import chromadb
from chromadb.config import Settings
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("fc-knowledge-mcp")

# Initialize MCP server
server = Server("fc-knowledge-base")

# ChromaDB configuration
CHROMA_PERSIST_DIR = Path(__file__).parent / "chroma_db"
BUSINESS_COLLECTION = "business_knowledge"
TECHNICAL_COLLECTION = "technical_knowledge"

# Global ChromaDB client
_chroma_client: Optional[chromadb.PersistentClient] = None


def get_chroma_client() -> chromadb.PersistentClient:
    """Get or create ChromaDB client."""
    global _chroma_client
    if _chroma_client is None:
        _chroma_client = chromadb.PersistentClient(
            path=str(CHROMA_PERSIST_DIR),
            settings=Settings(anonymized_telemetry=False)
        )
    return _chroma_client


def search_collection(
    collection_name: str,
    query: str,
    n_results: int = 5,
    metadata_filter: Optional[dict] = None
) -> list[dict]:
    """Search a ChromaDB collection and return results."""
    client = get_chroma_client()

    try:
        collection = client.get_collection(collection_name)
    except Exception as e:
        logger.error(f"Collection {collection_name} not found: {e}")
        return []

    # Perform search
    kwargs = {
        "query_texts": [query],
        "n_results": n_results,
        "include": ["documents", "metadatas", "distances"]
    }
    if metadata_filter:
        kwargs["where"] = metadata_filter

    results = collection.query(**kwargs)

    # Format results
    formatted = []
    if results and results["documents"]:
        for i, doc in enumerate(results["documents"][0]):
            formatted.append({
                "content": doc,
                "metadata": results["metadatas"][0][i] if results["metadatas"] else {},
                "distance": results["distances"][0][i] if results["distances"] else None,
                "relevance": 1 - (results["distances"][0][i] if results["distances"] else 0)
            })

    return formatted


@server.list_tools()
async def list_tools() -> list[Tool]:
    """List available tools for Claude Code."""
    return [
        Tool(
            name="search_business_knowledge",
            description="""Search the BUSINESS knowledge base for financial consolidation information.

Use this for:
- Consolidation concepts (equity method, global integration, proportional)
- IFRS/IAS standards questions
- How to use the product (step-by-step guides)
- Elimination types and when to use them
- Currency translation questions
- Ownership and control questions
- What features the product supports/doesn't support

Returns relevant passages from theory documents and product help content.""",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The search query - can be a question or keywords"
                    },
                    "num_results": {
                        "type": "integer",
                        "description": "Number of results to return (default: 5, max: 10)",
                        "default": 5
                    },
                    "topic_filter": {
                        "type": "string",
                        "description": "Optional: filter by topic (consolidation-methods, eliminations, currency, ownership, calculations, help)",
                        "enum": ["consolidation-methods", "eliminations", "currency", "ownership", "calculations", "help", "theory"]
                    }
                },
                "required": ["query"]
            }
        ),
        Tool(
            name="search_technical_knowledge",
            description="""Search the TECHNICAL knowledge base for implementation details.

Use this for:
- Stored procedure details (P_CONSO_*, P_CALC_*)
- Database table schemas (TS*, TD*)
- API handler signatures and parameters
- C# service implementations
- TypeScript/Frontend patterns
- Code patterns and templates
- Technical troubleshooting

Returns relevant passages from technical documentation including code examples.""",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The search query - can include procedure names, table names, or technical concepts"
                    },
                    "num_results": {
                        "type": "integer",
                        "description": "Number of results to return (default: 5, max: 10)",
                        "default": 5
                    },
                    "layer_filter": {
                        "type": "string",
                        "description": "Optional: filter by technical layer",
                        "enum": ["database", "application", "frontend", "api"]
                    }
                },
                "required": ["query"]
            }
        ),
        Tool(
            name="get_collection_stats",
            description="Get statistics about the knowledge base collections (document counts, etc.)",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        )
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    """Handle tool calls from Claude Code."""

    if name == "search_business_knowledge":
        query = arguments.get("query", "")
        num_results = min(arguments.get("num_results", 5), 10)
        topic_filter = arguments.get("topic_filter")

        metadata_filter = None
        if topic_filter:
            metadata_filter = {"topic": topic_filter}

        results = search_collection(
            BUSINESS_COLLECTION,
            query,
            n_results=num_results,
            metadata_filter=metadata_filter
        )

        if not results:
            return [TextContent(
                type="text",
                text="No results found in business knowledge base. The database may not be initialized yet."
            )]

        # Format response
        response = f"## Business Knowledge Search Results\n\n**Query**: {query}\n**Results**: {len(results)}\n\n"
        for i, r in enumerate(results, 1):
            source = r["metadata"].get("source", "Unknown")
            topic = r["metadata"].get("topic", "")
            relevance = f"{r['relevance']:.1%}" if r['relevance'] else "N/A"

            response += f"### Result {i} (Relevance: {relevance})\n"
            response += f"**Source**: {source}\n"
            if topic:
                response += f"**Topic**: {topic}\n"
            response += f"\n{r['content'][:2000]}{'...' if len(r['content']) > 2000 else ''}\n\n---\n\n"

        return [TextContent(type="text", text=response)]

    elif name == "search_technical_knowledge":
        query = arguments.get("query", "")
        num_results = min(arguments.get("num_results", 5), 10)
        layer_filter = arguments.get("layer_filter")

        metadata_filter = None
        if layer_filter:
            metadata_filter = {"layer": layer_filter}

        results = search_collection(
            TECHNICAL_COLLECTION,
            query,
            n_results=num_results,
            metadata_filter=metadata_filter
        )

        if not results:
            return [TextContent(
                type="text",
                text="No results found in technical knowledge base. The database may not be initialized yet."
            )]

        # Format response
        response = f"## Technical Knowledge Search Results\n\n**Query**: {query}\n**Results**: {len(results)}\n\n"
        for i, r in enumerate(results, 1):
            source = r["metadata"].get("source", "Unknown")
            layer = r["metadata"].get("layer", "")
            relevance = f"{r['relevance']:.1%}" if r['relevance'] else "N/A"

            response += f"### Result {i} (Relevance: {relevance})\n"
            response += f"**Source**: {source}\n"
            if layer:
                response += f"**Layer**: {layer}\n"
            response += f"\n{r['content'][:2000]}{'...' if len(r['content']) > 2000 else ''}\n\n---\n\n"

        return [TextContent(type="text", text=response)]

    elif name == "get_collection_stats":
        client = get_chroma_client()
        stats = {}

        for coll_name in [BUSINESS_COLLECTION, TECHNICAL_COLLECTION]:
            try:
                coll = client.get_collection(coll_name)
                stats[coll_name] = {
                    "document_count": coll.count(),
                    "name": coll.name
                }
            except Exception:
                stats[coll_name] = {"status": "not initialized"}

        return [TextContent(
            type="text",
            text=f"## Knowledge Base Statistics\n\n```json\n{json.dumps(stats, indent=2)}\n```"
        )]

    return [TextContent(type="text", text=f"Unknown tool: {name}")]


async def main():
    """Run the MCP server."""
    logger.info("Starting FC Knowledge Base MCP Server...")
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
