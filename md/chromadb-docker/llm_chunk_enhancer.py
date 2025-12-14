#!/usr/bin/env python3
"""
LLM-powered chunk enhancement for world-class RAG quality.

Uses AWS Bedrock Claude to generate:
- Semantic summaries
- Key concepts and keywords
- Related topics with context
- Hypothetical questions (HyDE approach)

This produces significantly better embeddings and retrieval than rule-based approaches.
"""

import json
import logging
import os
import time
from typing import Dict, List, Optional

import boto3
from botocore.config import Config

logger = logging.getLogger(__name__)

# Bedrock configuration
# Using Sonnet 4.5 for best quality (slower but produces world-class results)
BEDROCK_MODEL = "us.anthropic.claude-sonnet-4-5-20250929-v1:0"  # Best quality
BEDROCK_REGION = os.environ.get("AWS_DEFAULT_REGION", "us-east-1")
MAX_RETRIES = 5
RETRY_DELAY = 3


class ChunkEnhancer:
    """Enhance chunks using LLM for better RAG quality."""

    def __init__(self):
        self._client = None
        self._request_count = 0
        self._last_request_time = 0
        self._failed_chunks = []  # Track failed chunks for retry
        self._success_count = 0
        self._fallback_count = 0

    @property
    def client(self):
        """Lazy initialization of Bedrock client."""
        if self._client is None:
            # Prefer environment variables over profile
            if os.environ.get("AWS_ACCESS_KEY_ID") and os.environ.get("AWS_SECRET_ACCESS_KEY"):
                session = boto3.Session()
                auth_method = "environment variables"
            else:
                session = boto3.Session(profile_name="prophix-devops")
                auth_method = "profile 'prophix-devops'"

            config = Config(
                region_name=BEDROCK_REGION,
                retries={"max_attempts": MAX_RETRIES, "mode": "adaptive"},
                read_timeout=120,  # 2 minutes for response
                connect_timeout=30,  # 30 seconds to connect
            )
            self._client = session.client("bedrock-runtime", config=config)
            logger.info(f"Initialized Bedrock client with {auth_method} for chunk enhancement")

        return self._client

    def _rate_limit(self):
        """Simple rate limiting to avoid throttling."""
        self._request_count += 1
        # Add small delay every 10 requests
        if self._request_count % 10 == 0:
            time.sleep(0.5)

    def _call_claude(self, prompt: str, max_tokens: int = 1000) -> Optional[str]:
        """Call Claude via Bedrock."""
        self._rate_limit()

        body = json.dumps({
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": max_tokens,
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": 0.3,  # Low temperature for consistent outputs
        })

        for attempt in range(MAX_RETRIES):
            try:
                response = self.client.invoke_model(
                    modelId=BEDROCK_MODEL,
                    body=body,
                    contentType="application/json",
                    accept="application/json",
                )

                response_body = json.loads(response["body"].read())
                return response_body["content"][0]["text"]

            except Exception as e:
                logger.warning(f"Bedrock call failed (attempt {attempt + 1}): {e}")
                if attempt < MAX_RETRIES - 1:
                    time.sleep(RETRY_DELAY * (attempt + 1))
                else:
                    logger.error(f"Failed after {MAX_RETRIES} attempts")
                    return None

    def enhance_chunk(self, content: str, source_path: str, topic_area: str) -> Dict:
        """
        Enhance a chunk with LLM-generated metadata.

        Returns dict with:
        - summary: 1-2 sentence summary
        - keywords: List of key terms
        - concepts: Key consolidation concepts covered
        - questions: Hypothetical questions this chunk answers (HyDE)
        - related_topics: Related topics with brief explanation
        """
        prompt = f"""You are an expert in financial consolidation and IFRS accounting standards.

Analyze this documentation chunk and provide structured metadata to improve search and retrieval.

SOURCE: {source_path}
TOPIC AREA: {topic_area}

CONTENT:
{content[:4000]}

Respond in this exact JSON format (no markdown, just JSON):
{{
    "summary": "A clear 1-2 sentence summary of what this chunk covers and why it matters.",
    "keywords": ["keyword1", "keyword2", "keyword3", "keyword4", "keyword5"],
    "concepts": ["concept1", "concept2", "concept3"],
    "questions": [
        "What question does this chunk answer?",
        "Another question this content addresses?",
        "A third relevant question?"
    ],
    "related_topics": [
        "Related Topic 1: brief explanation of connection",
        "Related Topic 2: brief explanation of connection"
    ]
}}

Guidelines:
- Summary: Focus on the main point and practical relevance
- Keywords: Include IFRS standards (e.g., IFRS 10, IAS 21), technical terms, procedure names, table names
- Concepts: Core consolidation concepts (e.g., "goodwill calculation", "minority interest", "currency translation")
- Questions: Write questions a user might ask that this chunk answers - be specific
- Related Topics: Connect to other consolidation areas

Respond with ONLY the JSON, no other text."""

        response = self._call_claude(prompt, max_tokens=800)

        if not response or not response.strip():
            logger.warning("Empty LLM response, queuing for retry")
            self._failed_chunks.append((content, source_path, topic_area))
            self._fallback_count += 1
            return self._fallback_enhancement(content, source_path, topic_area)

        try:
            # Parse JSON response
            # Handle potential markdown code blocks
            response = response.strip()
            if response.startswith("```"):
                response = response.split("```")[1]
                if response.startswith("json"):
                    response = response[4:]
            response = response.strip()

            # Try to extract JSON if there's extra text
            import re
            json_match = re.search(r'\{[\s\S]*\}', response)
            if json_match:
                response = json_match.group()

            result = json.loads(response)

            # Validate required fields
            required = ["summary", "keywords", "concepts", "questions", "related_topics"]
            for field in required:
                if field not in result:
                    result[field] = []

            self._success_count += 1
            return result

        except json.JSONDecodeError as e:
            logger.warning(f"Failed to parse LLM response: {e}")
            self._failed_chunks.append((content, source_path, topic_area))
            self._fallback_count += 1
            return self._fallback_enhancement(content, source_path, topic_area)

    def _fallback_enhancement(self, content: str, source_path: str, topic_area: str) -> Dict:
        """Fallback to rule-based enhancement if LLM fails."""
        import re

        # Extract first meaningful line as summary
        lines = content.strip().split('\n')
        summary = f"Documentation about {topic_area.lower()}."
        for line in lines:
            line = line.strip()
            if line and not line.startswith('#') and len(line) > 50:
                summary = line[:200]
                break

        # Extract keywords with regex
        keywords = []
        patterns = [
            r"IFRS\s*\d+", r"IAS\s*\d+",
            r"goodwill", r"elimination", r"consolidation",
            r"minority interest", r"NCI", r"currency",
        ]
        for pattern in patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            keywords.extend([m.upper() for m in matches])
        keywords = list(dict.fromkeys(keywords))[:10]

        return {
            "summary": summary,
            "keywords": keywords,
            "concepts": [topic_area],
            "questions": [f"What is {topic_area.lower()}?"],
            "related_topics": [topic_area],
        }

    def get_stats(self) -> Dict:
        """Get enhancement statistics."""
        return {
            "success": self._success_count,
            "fallback": self._fallback_count,
            "pending_retry": len(self._failed_chunks),
        }

    def retry_failed_chunks(self) -> int:
        """
        Retry all failed chunks with longer delays.
        Returns number of successfully retried chunks.
        """
        if not self._failed_chunks:
            return 0

        logger.info(f"Retrying {len(self._failed_chunks)} failed chunks...")
        retry_success = 0
        still_failed = []

        for content, source_path, topic_area in self._failed_chunks:
            # Longer delay between retries
            time.sleep(5)

            # Try again
            prompt = f"""You are an expert in financial consolidation and IFRS accounting standards.

Analyze this documentation chunk and provide structured metadata to improve search and retrieval.

SOURCE: {source_path}
TOPIC AREA: {topic_area}

CONTENT:
{content[:3500]}

Respond in this exact JSON format (no markdown, just JSON):
{{
    "summary": "A clear 1-2 sentence summary.",
    "keywords": ["keyword1", "keyword2", "keyword3"],
    "concepts": ["concept1", "concept2"],
    "questions": ["Question 1?", "Question 2?"],
    "related_topics": ["Topic 1", "Topic 2"]
}}

Respond with ONLY the JSON, no other text."""

            response = self._call_claude(prompt, max_tokens=600)

            if response and response.strip():
                try:
                    import re
                    response = response.strip()
                    json_match = re.search(r'\{[\s\S]*\}', response)
                    if json_match:
                        json.loads(json_match.group())  # Validate JSON
                        retry_success += 1
                        logger.info(f"Retry succeeded for: {source_path}")
                        continue
                except:
                    pass

            still_failed.append((content, source_path, topic_area))
            logger.warning(f"Retry failed for: {source_path}")

        self._failed_chunks = still_failed
        self._success_count += retry_success
        self._fallback_count -= retry_success

        logger.info(f"Retry complete: {retry_success} succeeded, {len(still_failed)} still failed")
        return retry_success


def get_enhancer() -> ChunkEnhancer:
    """Get singleton enhancer instance."""
    return ChunkEnhancer()


# Test
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    enhancer = get_enhancer()

    test_content = """
    ## Goodwill Calculation

    Goodwill is calculated as the difference between the acquisition price and the
    parent's share of the subsidiary's net assets at fair value.

    Formula: Goodwill = Acquisition Price - (Ownership % × Net Assets)

    Under IFRS 3, goodwill must be tested for impairment annually.
    """

    result = enhancer.enhance_chunk(
        test_content,
        "03-core-calculations/goodwill-calculation.md",
        "Core Calculations"
    )

    print(json.dumps(result, indent=2))
