"""
Services module for Product Owner RAG application.
Contains service layer functions for AWS Bedrock, ChromaDB, and LLM interactions.
"""

from .bedrock_service import get_bedrock_client
from .chroma_service import (
    get_chroma_client,
    get_embeddings,
    search_business_layer,
    extract_content_only,
)

__all__ = [
    'get_bedrock_client',
    'get_chroma_client',
    'get_embeddings',
    'search_business_layer',
    'extract_content_only',
]
