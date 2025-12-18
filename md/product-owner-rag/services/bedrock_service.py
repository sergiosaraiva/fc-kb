"""
AWS Bedrock Service for Product Owner RAG Application.

Provides AWS Bedrock client initialization with proper configuration
for Claude model invocations.
"""

import logging
import os

import boto3
import streamlit as st
from botocore.config import Config

# Import AWS region from config
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))
from config import AWS_REGION

# Configure logging
logger = logging.getLogger("product-owner-rag.bedrock")


@st.cache_resource
def get_bedrock_client():
    """
    Get AWS Bedrock client (cached).

    Initializes a boto3 client for AWS Bedrock Runtime with proper
    configuration for Claude model invocations. Uses environment
    variables for credentials if available, otherwise falls back
    to AWS profile.

    Returns:
        boto3.client: Bedrock Runtime client, or None if initialization fails.
    """
    try:
        # Prefer environment variables over AWS profile
        if os.environ.get("AWS_ACCESS_KEY_ID") and os.environ.get("AWS_SECRET_ACCESS_KEY"):
            session = boto3.Session()
            logger.info("Using AWS credentials from environment variables")
        else:
            aws_profile = os.environ.get("AWS_PROFILE", "prophix-devops")
            session = boto3.Session(profile_name=aws_profile)
            logger.info(f"Using AWS profile: {aws_profile}")

        config = Config(
            region_name=AWS_REGION,
            retries={"max_attempts": 5, "mode": "adaptive"},
            read_timeout=300,  # 5 minute timeout for Sonnet 4.5 long responses
            connect_timeout=30,  # 30 seconds for initial connection
        )
        return session.client("bedrock-runtime", config=config)
    except Exception as e:
        logger.error(f"Failed to initialize AWS Bedrock client: {e}")
        st.error("AI service unavailable. Please check AWS credentials.")
        return None
