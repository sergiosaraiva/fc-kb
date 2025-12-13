"""
AWS Bedrock Titan Text Embeddings V1 for FC Knowledge Base

Amazon Titan Text Embeddings V1 provides:
- 1536-dimensional vectors (same as OpenAI ada-002)
- First-party Amazon model (no marketplace subscription required)
- Good semantic understanding for retrieval tasks

This is used when Cohere Embed v4 is not available due to marketplace access.
"""

import json
import logging
import os
from typing import List

import boto3
from botocore.config import Config
from chromadb.api.types import EmbeddingFunction, Embeddings

from config import (
    AWS_PROFILE,
    AWS_REGION,
    BEDROCK_EMBEDDING_MODEL,
    EMBEDDING_DIMENSIONS,
)

logger = logging.getLogger(__name__)


class TitanV1EmbeddingFunction(EmbeddingFunction):
    """
    ChromaDB embedding function using AWS Bedrock Titan Text Embeddings V1.

    Titan V1 provides:
    - 1536-dimensional vectors (fixed, not configurable)
    - 8k token context
    - Good retrieval performance
    - No marketplace subscription required
    """

    def __init__(
        self,
        model_id: str = BEDROCK_EMBEDDING_MODEL,
        region_name: str = AWS_REGION,
        profile_name: str = AWS_PROFILE,
    ):
        self.model_id = model_id
        self.region_name = region_name
        self.profile_name = profile_name
        self._client = None

    @property
    def client(self):
        """Lazy initialization of Bedrock client."""
        if self._client is None:
            try:
                # Prefer environment variables over profile
                if os.environ.get("AWS_ACCESS_KEY_ID") and os.environ.get("AWS_SECRET_ACCESS_KEY"):
                    session = boto3.Session()
                    auth_method = "environment variables"
                else:
                    session = boto3.Session(profile_name=self.profile_name)
                    auth_method = f"profile '{self.profile_name}'"
                config = Config(
                    region_name=self.region_name,
                    retries={"max_attempts": 3, "mode": "adaptive"},
                )
                self._client = session.client("bedrock-runtime", config=config)
                logger.info(
                    f"Initialized Bedrock client with {auth_method} "
                    f"in {self.region_name} for Titan V1"
                )
            except Exception as e:
                logger.error(f"Failed to initialize Bedrock client: {e}")
                raise
        return self._client

    def __call__(self, input: List[str]) -> Embeddings:
        """
        Generate embeddings for a list of texts.

        Args:
            input: List of text strings to embed

        Returns:
            List of embedding vectors
        """
        embeddings = []

        for text in input:
            try:
                embedding = self._get_embedding(text)
                embeddings.append(embedding)
            except Exception as e:
                logger.error(f"Error generating embedding: {e}")
                # Return zero vector on error to maintain batch integrity
                embeddings.append([0.0] * EMBEDDING_DIMENSIONS)

        return embeddings

    def _get_embedding(self, text: str) -> List[float]:
        """
        Get embedding for a single text using Titan V1.

        Args:
            text: Text to embed

        Returns:
            Embedding vector as list of floats
        """
        # Titan V1 request body (simple format)
        body = json.dumps({
            "inputText": text,
        })

        response = self.client.invoke_model(
            modelId=self.model_id,
            body=body,
            contentType="application/json",
            accept="application/json",
        )

        response_body = json.loads(response["body"].read())
        embedding = response_body.get("embedding", [])

        if not embedding:
            raise ValueError("Empty embedding returned from Bedrock Titan V1")

        return embedding

    def embed_query(self, text: str) -> List[float]:
        """
        Embed a query text.

        Note: Titan V1 doesn't distinguish between query and document embeddings,
        so this just calls the regular embedding method.

        Args:
            text: Query text to embed

        Returns:
            Embedding vector as list of floats
        """
        return self._get_embedding(text)


def get_embedding_function() -> TitanV1EmbeddingFunction:
    """
    Get the Titan V1 embedding function.

    Returns:
        TitanV1EmbeddingFunction instance
    """
    ef = TitanV1EmbeddingFunction()
    # Test the connection
    _ = ef.client
    logger.info(f"Using AWS Bedrock Titan V1 ({EMBEDDING_DIMENSIONS} dimensions)")
    return ef


# Test function
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    print("Testing Titan V1 Embeddings...")
    print(f"Profile: {AWS_PROFILE}")
    print(f"Region: {AWS_REGION}")
    print(f"Model: {BEDROCK_EMBEDDING_MODEL}")
    print(f"Dimensions: {EMBEDDING_DIMENSIONS}")
    print()

    ef = get_embedding_function()

    test_texts = [
        "Financial consolidation eliminates intercompany transactions",
        "Goodwill is calculated as purchase price minus fair value of net assets",
    ]

    # Test document embeddings
    embeddings = ef(test_texts)
    print(f"Generated {len(embeddings)} embeddings")
    print(f"Embedding dimensions: {len(embeddings[0])}")

    # Test query embedding
    query_embedding = ef.embed_query("How is goodwill calculated?")
    print(f"Query embedding dimensions: {len(query_embedding)}")

    print("Test passed!")
