#!/usr/bin/env python3
"""
Product Owner RAG - Business-Focused Knowledge Base Interface

Provides AI-powered Q&A for product owners using the same FC Knowledge Base
as Claude Code MCP, but filtered to business layer only (no technical code).

Uses:
- Same ChromaDB Docker container (localhost:8847)
- Same AWS Bedrock credentials (prophix-devops)
- Titan V1 embeddings (1536 dimensions)
- Claude Sonnet 4.5 via Bedrock for responses
"""

import html
import json
import logging
import os
import random
import re
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional
from urllib.parse import unquote

import streamlit as st
import chromadb
from chromadb.config import Settings

# Add parent directory to path to import shared modules
sys.path.append(str(Path(__file__).parent.parent))

from config import (
    CHROMADB_HOST,
    CHROMADB_PORT,
    CHROMADB_TOKEN,
    FULL_COLLECTION,
    AWS_REGION,
)
from titan_v1_embeddings import get_embedding_function

# Import custom concept map component
from concept_map_component import concept_map

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("product-owner-rag")

# AWS Bedrock for Claude model
import boto3
from botocore.config import Config

# Configuration - Model Selection (3 tiers)
MODEL_TIERS = {
    "Haiku 4.5": {
        "id": "us.anthropic.claude-haiku-4-5-20251001-v1:0",
        "description": "Fast responses",
        "max_tokens": 4000,
    },
    "Sonnet 4": {
        "id": "us.anthropic.claude-sonnet-4-20250514-v1:0",
        "description": "Balanced quality & speed",
        "max_tokens": 6000,
    },
    "Sonnet 4.5": {
        "id": "us.anthropic.claude-sonnet-4-5-20250929-v1:0",
        "description": "Best quality",
        "max_tokens": 8000,
    },
}
CLAUDE_FAST_MODEL_ID = MODEL_TIERS["Haiku 4.5"]["id"]  # Always use fast model for auxiliary calls
DEFAULT_MODEL_TIER = "Haiku 4.5"  # Default to fast model for responsive UX
TEMPERATURE = 0.3            # Reduced for more consistent, reliable answers

# Knowledge mode: "Business" (hide technical details) or "Full (Technical)" (show everything)
DEFAULT_KNOWLEDGE_MODE = os.environ.get("KNOWLEDGE_MODE", "Business")

# Retrieval configuration
BUSINESS_LAYER_RESULTS = 8   # More smaller chunks = better coverage + fast response
RELEVANCE_THRESHOLD = 0.35   # Lowered from 0.55 - more permissive for business users
MAX_CONTEXT_CHUNKS = 10      # Limit chunks sent to Claude (balanced speed vs completeness)


def extract_content_only(chunk_text: str) -> str:
    """
    Extract only the actual content from LLM-enhanced chunks.

    LLM-enhanced chunks have metadata (summary, questions, keywords) that helped
    with embedding quality but shouldn't be sent to Claude as context.
    This function strips the metadata and returns only the core content.
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


# Page configuration
st.set_page_config(
    page_title="FC Knowledge Base - Education Portal",
    page_icon="◆",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Professional CSS styling - single accent color (slate blue)
st.markdown("""
<style>
    /* Main accent color: professional slate blue */
    :root {
        --accent-color: #5B7FFF;
        --accent-hover: #4A6FEE;
        --text-muted: #8B949E;
        --border-color: #30363D;
        --theory-color: #5B7FFF;
        --help-color: #2EA043;
        --impl-color: #A371F7;
        /* Override Streamlit theme colors */
        --primary-color: #5B7FFF !important;
    }

    /* Force Streamlit primary color theme */
    [data-testid="stAppViewContainer"] {
        --primary-color: #5B7FFF;
    }

    /* Hide Streamlit default UI elements and reduce top space */
    #MainMenu {visibility: hidden;}
    .stDeployButton {display: none;}
    header {display: none !important;}
    [data-testid="stHeader"] {display: none !important;}
    [data-testid="stToolbar"] {display: none !important;}
    [data-testid="stStatusWidget"] {display: none !important;}

    /* Streamlit button styling */
    .stButton > button {
        border: 1px solid var(--border-color);
        background-color: transparent;
        transition: all 0.2s ease;
    }
    .stButton > button:hover {
        border-color: var(--accent-color);
        color: var(--accent-color);
    }

    /* Primary button styling - force blue color (override Streamlit red) */
    .stButton > button[kind="primary"],
    .stButton > button[data-testid="baseButton-primary"],
    .stButton > button[class*="primary"],
    button[kind="primary"],
    div[data-testid="stButton"] > button[kind="primary"] {
        background-color: #5B7FFF !important;
        border-color: #5B7FFF !important;
        color: white !important;
    }
    .stButton > button[kind="primary"]:hover,
    .stButton > button[data-testid="baseButton-primary"]:hover,
    .stButton > button[class*="primary"]:hover,
    button[kind="primary"]:hover,
    div[data-testid="stButton"] > button[kind="primary"]:hover {
        background-color: #4A6FEE !important;
        border-color: #4A6FEE !important;
        color: white !important;
    }
    .stButton > button[kind="primary"]:active,
    .stButton > button[kind="primary"]:focus {
        background-color: #5B7FFF !important;
        border-color: #5B7FFF !important;
        color: white !important;
    }

    /* Section headers */
    .sidebar-section {
        font-weight: 600;
        color: var(--accent-color);
        margin-bottom: 0.5rem;
        font-size: 0.9rem;
        letter-spacing: 0.5px;
    }

    /* Expander styling - cleaner look */
    .streamlit-expanderHeader {
        font-weight: 500;
        font-size: 0.95rem;
    }

    /* Remove excessive padding - maximize vertical space */
    .block-container {
        padding-top: 1rem !important;
        padding-bottom: 1rem !important;
    }
    .stApp > header {
        display: none !important;
    }
    section[data-testid="stSidebar"] > div:first-child {
        padding-top: 1rem !important;
    }

    /* Cleaner dividers */
    hr {
        margin: 1.5rem 0;
        border-color: var(--border-color);
        opacity: 0.3;
    }

    /* Sidebar styling */
    section[data-testid="stSidebar"] {
        border-right: 1px solid var(--border-color);
    }

    /* Info box styling */
    .stAlert {
        border-left: 3px solid var(--accent-color);
        background-color: rgba(91, 127, 255, 0.1);
    }

    /* Source tier badges */
    .tier-badge {
        display: inline-block;
        padding: 2px 8px;
        border-radius: 12px;
        font-size: 11px;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-right: 8px;
    }
    .tier-theory {
        background-color: rgba(91, 127, 255, 0.2);
        color: #5B7FFF;
        border: 1px solid rgba(91, 127, 255, 0.4);
    }
    .tier-help {
        background-color: rgba(46, 160, 67, 0.2);
        color: #2EA043;
        border: 1px solid rgba(46, 160, 67, 0.4);
    }
    .tier-impl {
        background-color: rgba(163, 113, 247, 0.2);
        color: #A371F7;
        border: 1px solid rgba(163, 113, 247, 0.4);
    }

    /* Keyboard shortcut hints */
    .kbd {
        display: inline-block;
        padding: 2px 6px;
        font-size: 11px;
        font-family: monospace;
        background-color: rgba(255, 255, 255, 0.1);
        border: 1px solid var(--border-color);
        border-radius: 4px;
        margin-left: 4px;
    }

    /* Progress steps */
    .progress-step {
        display: flex;
        align-items: center;
        padding: 8px 0;
        color: var(--text-muted);
    }
    .progress-step.active {
        color: var(--accent-color);
        font-weight: 500;
    }
    .progress-step.complete {
        color: #2EA043;
    }
    .step-indicator {
        width: 20px;
        height: 20px;
        border-radius: 50%;
        border: 2px solid currentColor;
        margin-right: 10px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 10px;
    }
    .step-indicator.complete::after {
        content: "✓";
    }

    /* Left-aligned buttons for learning paths and glossary (exclude primary) */
    section[data-testid="stSidebar"] .stExpander .stButton button:not([kind="primary"]):not([data-testid="baseButton-primary"]) {
        text-align: left !important;
        justify-content: flex-start !important;
        padding-left: 12px !important;
    }

    /* Center primary buttons in expanders (Enhance with AI) - full width blue */
    section[data-testid="stSidebar"] .stExpander .stButton button[kind="primary"],
    section[data-testid="stSidebar"] .stExpander .stButton button[data-testid="baseButton-primary"],
    section[data-testid="stSidebar"] .stExpander div[data-testid="stButton"] button[kind="primary"] {
        text-align: center !important;
        justify-content: center !important;
        padding-left: 16px !important;
        padding-right: 16px !important;
        width: 100% !important;
        background-color: #5B7FFF !important;
        border-color: #5B7FFF !important;
        color: white !important;
    }

    /* Progress bar styling */
    .progress-bar-container {
        background-color: rgba(255, 255, 255, 0.1);
        border-radius: 4px;
        height: 6px;
        margin: 4px 0 8px 0;
        overflow: hidden;
    }
    .progress-bar-fill {
        background-color: #5B7FFF;
        height: 100%;
        border-radius: 4px;
        transition: width 0.3s ease;
    }
    .progress-text {
        font-size: 11px;
        color: #8B949E;
        margin-bottom: 4px;
    }

    /* Completed item checkmark */
    .completed-check {
        color: #2EA043;
        margin-right: 6px;
    }

    /* Autocomplete suggestions */
    .autocomplete-container {
        position: relative;
    }
    .autocomplete-suggestions {
        background-color: #1E1E1E;
        border: 1px solid var(--border-color);
        border-radius: 4px;
        max-height: 200px;
        overflow-y: auto;
        margin-top: 4px;
    }
    .autocomplete-item {
        padding: 8px 12px;
        cursor: pointer;
        font-size: 14px;
        border-bottom: 1px solid var(--border-color);
    }
    .autocomplete-item:hover {
        background-color: rgba(91, 127, 255, 0.2);
    }
    .autocomplete-item:last-child {
        border-bottom: none;
    }

    /* Audio controls */
    .audio-controls {
        display: flex;
        align-items: center;
        gap: 8px;
        padding: 8px 0;
    }
    .audio-btn {
        background-color: transparent;
        border: 1px solid var(--accent-color);
        color: var(--accent-color);
        padding: 6px 12px;
        border-radius: 4px;
        cursor: pointer;
        font-size: 13px;
        transition: all 0.2s ease;
    }
    .audio-btn:hover {
        background-color: var(--accent-color);
        color: white;
    }
    .audio-btn.playing {
        background-color: var(--accent-color);
        color: white;
    }
    .speed-select {
        background-color: transparent;
        border: 1px solid var(--border-color);
        color: inherit;
        padding: 4px 8px;
        border-radius: 4px;
        font-size: 12px;
    }

    /* Case study cards */
    .case-study-card {
        background-color: rgba(91, 127, 255, 0.1);
        border: 1px solid rgba(91, 127, 255, 0.3);
        border-radius: 8px;
        padding: 12px;
        margin-bottom: 8px;
    }
    .case-study-title {
        font-weight: 600;
        color: var(--accent-color);
        margin-bottom: 4px;
    }
    .case-study-desc {
        font-size: 12px;
        color: var(--text-muted);
    }

    /* Bookmark styles */
    .bookmark-btn {
        background-color: transparent;
        border: 1px solid #F0883E;
        color: #F0883E;
        padding: 6px 12px;
        border-radius: 4px;
        cursor: pointer;
        font-size: 13px;
        transition: all 0.2s ease;
    }
    .bookmark-btn:hover, .bookmark-btn.bookmarked {
        background-color: #F0883E;
        color: white;
    }
    .bookmark-card {
        background-color: rgba(240, 136, 62, 0.1);
        border: 1px solid rgba(240, 136, 62, 0.3);
        border-radius: 8px;
        padding: 10px;
        margin-bottom: 8px;
    }
    .bookmark-question {
        font-weight: 600;
        font-size: 13px;
        margin-bottom: 4px;
    }
    .bookmark-preview {
        font-size: 11px;
        color: var(--text-muted);
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
    }

    /* Adaptive quiz difficulty indicator */
    .difficulty-badge {
        display: inline-block;
        padding: 2px 8px;
        border-radius: 12px;
        font-size: 10px;
        font-weight: 600;
        text-transform: uppercase;
    }
    .difficulty-easy { background-color: rgba(46, 160, 67, 0.2); color: #2EA043; }
    .difficulty-medium { background-color: rgba(240, 136, 62, 0.2); color: #F0883E; }
    .difficulty-hard { background-color: rgba(219, 109, 109, 0.2); color: #DB6D6D; }

    /* Tab styling - use blue instead of red */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: transparent;
        border-radius: 4px;
        padding: 8px 16px;
        font-size: 14px;
    }
    .stTabs [aria-selected="true"] {
        background-color: rgba(91, 127, 255, 0.2) !important;
        color: #5B7FFF !important;
        border-bottom: 2px solid #5B7FFF !important;
    }
    .stTabs [data-baseweb="tab-highlight"] {
        background-color: #5B7FFF !important;
    }
    .stTabs [data-baseweb="tab-border"] {
        background-color: var(--border-color) !important;
    }

    /* Consistent action button styling */
    .action-button {
        background-color: #5B7FFF !important;
        color: white !important;
        border: none !important;
        padding: 8px 16px !important;
        border-radius: 4px !important;
        cursor: pointer !important;
        font-size: 14px !important;
        width: 100% !important;
        transition: background-color 0.2s ease !important;
        text-align: center !important;
        display: inline-block !important;
        box-sizing: border-box !important;
    }
    .action-button:hover {
        background-color: #4A6FEE !important;
    }
</style>
""", unsafe_allow_html=True)


@st.cache_resource
def get_chroma_client():
    """Get ChromaDB client (cached)."""
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


@st.cache_resource
def get_bedrock_client():
    """Get AWS Bedrock client (cached)."""
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


@st.cache_resource
def get_embeddings():
    """Get embedding function (cached)."""
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


def generate_answer_with_claude(query: str, context: str, conversation_history: list = None, explanation_level: str = "Standard", model_tier: str = None, knowledge_mode: str = "Business") -> str:
    """
    Generate answer using AWS Bedrock Claude with selected model tier.

    Args:
        query: User's question
        context: Retrieved context from knowledge base
        conversation_history: List of previous Q&A pairs for context
        explanation_level: "Executive Summary", "Standard", or "Detailed"
        model_tier: "Haiku 4.5", "Sonnet 4", or "Sonnet 4.5" - determines model and max_tokens
        knowledge_mode: "Business" or "Full (Technical)" - controls technical detail filtering

    Returns:
        Claude's response text
    """
    bedrock = get_bedrock_client()

    # Select model based on tier (default to Great if not specified)
    if model_tier is None:
        model_tier = DEFAULT_MODEL_TIER
    model_config = MODEL_TIERS.get(model_tier, MODEL_TIERS[DEFAULT_MODEL_TIER])
    model_id = model_config["id"]
    max_tokens = model_config["max_tokens"]

    # Adjust max_tokens based on explanation level
    # Only limit Executive Summary - streaming makes longer responses fine
    if explanation_level == "Executive Summary":
        max_tokens = min(max_tokens, 1000)  # ~400 words for quick overview

    # Limit conversation history to last 3 exchanges (but with more context per exchange)
    if conversation_history:
        conversation_history = conversation_history[-3:]

    # Level-specific instructions
    level_instructions = {
        "Executive Summary": """
# EXPLANATION LEVEL: EXECUTIVE SUMMARY
You are providing a HIGH-LEVEL OVERVIEW for executives and managers.

**Format Requirements:**
- Keep total response under 400 words
- Focus on business impact and key takeaways
- Use bullet points for quick scanning
- Include ONE key formula or diagram maximum
- Skip edge cases and technical details
- Emphasize "what it means" over "how it works"
- End with 2-3 bullet point summary

**Structure:**
1. One-paragraph concept definition
2. Key business implications (3-4 bullets)
3. Quick reference to IFRS standard
4. Brief Prophix.FC mention (1-2 sentences)
""",
        "Standard": """
# EXPLANATION LEVEL: STANDARD
You are providing a BALANCED EXPLANATION suitable for product owners and consolidation professionals.

**Format Requirements:**
- Provide comprehensive but focused coverage
- Include theory, principles, implementation, and examples
- Use diagrams and formulas where helpful
- Cover common scenarios and main edge cases
- Balance depth with readability
""",
        "Detailed": """
# EXPLANATION LEVEL: DETAILED
You are providing COMPREHENSIVE COVERAGE for consolidation specialists who need complete understanding.

**Format Requirements:**
- Provide exhaustive, in-depth coverage
- Include ALL edge cases and special situations
- Show multiple examples with varying complexity
- Include complete journal entries and calculations
- Reference specific IFRS paragraphs where applicable
- Cover historical context and alternative approaches
- Include troubleshooting guidance and common mistakes
- Provide step-by-step UI instructions with field-level detail
- No length limit - be as thorough as needed
""",
    }

    # System prompt - defines the AI's role and behavior
    # OPTIMIZATION: Use minimal prompt for Executive Summary (faster processing)
    if explanation_level == "Executive Summary":
        system_prompt = """You are a Financial Consolidation Expert. Provide concise, executive-level answers.

RULES:
- Keep response under 400 words
- Focus on business impact and key takeaways
- Use bullet points for quick scanning
- Include ONE formula or diagram maximum
- Skip edge cases and technical details
- Cite relevant IFRS/IAS standard briefly
- End with 2-3 bullet summary

Structure: Definition → Key implications → IFRS reference → Prophix.FC mention"""
    else:
        # Full detailed prompt for Standard/Detailed modes
        system_prompt = f"""{level_instructions.get(explanation_level, level_instructions["Standard"])}

You are a Financial Consolidation Expert and Educator specializing in:
- The Direct Consolidation Framework methodology (the authoritative framework)
- IFRS/IAS accounting standards (IFRS 3, IFRS 10, IFRS 11, IAS 21, IAS 27, IAS 28)
- Prophix.FC financial consolidation software implementation

# YOUR ROLE
You bridge theoretical accounting principles with practical software implementation. Your audience is product owners, financial controllers, and consolidation managers who need to understand both the "why" (accounting standards) and the "how" (system implementation).

# RESPONSE STRUCTURE (MANDATORY)

Your answers MUST follow this hierarchy:

## 1. THEORETICAL FOUNDATION (Always start here)
- Define the concept using the Direct Consolidation Framework
- Cite the governing IFRS/IAS standard(s)
- Explain the business purpose and accounting rationale
- Include the control/ownership thresholds when applicable

## 2. KEY PRINCIPLES & FORMULAS
- Core accounting treatment rules
- Mathematical formulas (use proper notation)
- Journal entry patterns
- Edge cases and special situations

## 3. PROPHIX.CONSO IMPLEMENTATION
- How the system operationalizes the theory
- Relevant screens, workflows, and stored procedures
- Elimination codes and consolidation methods
- User actions and configuration

## 4. HOW TO USE IN THE APPLICATION (UI Workflow)
Provide detailed step-by-step instructions for using the feature in Prophix.FC:
- Navigation path: Menu → Submenu → Screen name
- Field-by-field guidance with business context for each field
- Button actions and what they trigger
- Grid operations (add, edit, delete, refresh)
- Validation rules and error messages users might encounter
- Dependencies between fields or screens
- Workflow sequence (what to do first, second, etc.)
- Where results appear and how to interpret them
- Common user mistakes and how to avoid them

**Example UI instruction format:**
```
To configure equity method investments:

1. Navigate to: Group Management → Ownership Structure → Investments

2. Click "New Investment" button to create a new entry

3. Fill in the following fields:
   - Parent Company: Select the investing entity (must be a legal entity in your group)
   - Investee Company: Select the associate company (ownership 20-50%)
   - Ownership %: Enter the exact ownership percentage (determines equity pickup)
   - Effective Date: Select the acquisition date (controls when equity method begins)
   - Consolidation Method: Select "Equity Method" from dropdown

4. Click "Save" to validate and store the investment relationship

5. Navigate to: Consolidation → Run Consolidation to apply the equity method calculations

The system will automatically calculate your share of the investee's net income based on the ownership percentage.
```

## 5. PRACTICAL EXAMPLES
- Concrete scenarios with numbers
- Step-by-step business scenarios with journal entries
- Before/After examples showing consolidation impact
- Common mistakes to avoid
- Real-world situations financial consolidators encounter

# VISUAL AIDS & DIAGRAMS

Use diagrams liberally to illustrate complex concepts. IMPORTANT: Use only ASCII/text art - NO mermaid syntax.

**Ownership Structures** - Use ASCII art:
```
        [Parent 80%]
             |
             v
        [Subsidiary]

    Multi-level example:
         [Parent]
            |
         100% |
            v
         [Sub A]
            |
         60% |
            v
         [Sub B]
```

**Process Flows** - Use ASCII art:
```
Local Books → Restatements → Translation → Eliminations → Consolidated

Detailed flow:
  Step 1          Step 2         Step 3          Step 4
┌─────────┐    ┌─────────┐    ┌─────────┐    ┌─────────┐
│ Local   │ -> │ Adjust  │ -> │ Currency│ -> │ Elimin- │
│ Books   │    │ IFRS    │    │ Convert │    │ ations  │
└─────────┘    └─────────┘    └─────────┘    └─────────┘
```

**Comparison Tables** - Use markdown:
| Method | Ownership | Standard | Treatment |
|--------|-----------|----------|-----------|
| Global | >50% | IFRS 10 | 100% consolidation |
| Equity | 20-50% | IAS 28 | One-line |

**Formulas** - Use proper notation:
```
Goodwill = Purchase Price - Fair Value of Net Assets Acquired
NCI = Ownership % × Subsidiary Equity
Equity Pickup = Ownership % × Associate Net Income
```

**Journal Entries** - Use T-account or simple format:
```
Dr. Investment Elimination    100
    Cr. Share Capital              100
```

# CITATION STANDARDS

- Always cite the IFRS/IAS standard: "Under IAS 28..."
- Reference Direct Consolidation Framework chunks when using the methodology: "According to the Direct Consolidation Framework..."
- Quote exact elimination codes: "Elimination code S087..."
- Name specific stored procedures: "P_CONSO_ELIM_EQUITYMETHOD..."

# QUALITY CRITERIA

✓ Start with theory, never implementation-first
✓ Always explain "why" before "how"
✓ Include at least one diagram for complex topics
✓ Provide numerical examples when discussing calculations
✓ Cite specific IFRS/IAS paragraphs when available
✓ Distinguish between "control" vs "ownership" vs "significant influence"
✓ Clarify whether something is an accounting requirement vs system configuration choice

# AUDIENCE AWARENESS

Your primary audience is **product owners** and **financial consolidation professionals** including:
- **Product Owners**: Defining requirements, validating features, understanding business value
- **Financial Controllers**: Ensuring IFRS/IAS compliance, validating accounting treatment
- **Consolidation Managers**: Operating the system, understanding workflows, troubleshooting results
- **CFO Office**: Understanding consolidation methodology, reviewing consolidated results
- **External Auditors**: Validating system compliance with accounting standards

They need:
- **Detailed explanations** with comprehensive coverage of the topic
- **Business language** - speak in terms of accounting, not technology
- **Conceptual understanding** before technical implementation details
- **Confidence** that the system is standards-compliant
- **Practical UI guidance** for day-to-day operations
- **Educational foundation** in consolidation theory
- **Context** for why features exist and when to use them

Avoid:
- Code snippets, SQL syntax, or technical implementation details (unless specifically requested)
- Over-technical database jargon
- Assuming they know consolidation theory
- Brief or rushed answers - be thorough and comprehensive
- Skipping the "why" to jump to the "how"

# RESPONSE TONE & DETAIL LEVEL

- **Authoritative yet accessible**: Speak as a seasoned financial consolidation expert
- **Comprehensive and detailed**: Don't rush - provide thorough, complete explanations
- **Business-focused language**: Use accounting and finance terminology, not IT jargon
- **Educational**: Teach the concepts thoroughly, don't assume prior knowledge
- **Precise with terminology**: Distinguish between "control" vs "ownership" vs "significant influence"
- **Patient and thorough**: Product owners need complete understanding to make decisions
- **Practical and actionable**: Always connect theory to real-world usage

**Detail Level Examples:**
- ❌ "Use the Ownership Structure screen"
- ✅ "Navigate to Group Management → Ownership Structure → Investments, where you configure parent-subsidiary relationships that determine which consolidation method applies (global integration for >50% ownership, equity method for 20-50%, or cost method for <20%)"

- ❌ "Enter the ownership percentage"
- ✅ "In the Ownership % field, enter the exact voting rights percentage (not economic interest, unless they differ), as this percentage determines: (1) which consolidation method to apply per IFRS 10/IAS 28, (2) the NCI calculation for >50% ownership, and (3) the equity pickup percentage for 20-50% ownership"

Remember: A product owner or financial consolidator reading your answer should gain **comprehensive understanding** of both the accounting standard and how Prophix implements it, with emphasis on business value, education, and operational guidance."""

    # Add business mode filtering instructions
    if knowledge_mode == "Business":
        system_prompt += """

# BUSINESS MODE RESTRICTIONS (ACTIVE)

You are in BUSINESS MODE. DO NOT include any technical implementation details:

**NEVER mention or include:**
- Stored procedure names (P_CONSO_*, P_CALC_*, P_SYS_*, etc.)
- Database table names (TS_*, TD_*, TM_*, T_*, etc.)
- SQL code or database queries
- C# code, TypeScript code, or any programming code
- API endpoint names or handler names
- Technical column names or field mappings
- Internal system architecture details

**INSTEAD, focus on:**
- Business concepts and accounting principles
- IFRS/IAS standards and their requirements
- User-facing screens and workflows (without technical implementation)
- Business rules and validation logic (described in business terms)
- Practical examples with numbers
- Navigation paths in the UI

When the knowledge base context contains technical details, translate them into business-friendly language or omit them entirely."""
    else:
        system_prompt += """

# FULL TECHNICAL MODE (ACTIVE)

You are in FULL TECHNICAL MODE. You may include all technical implementation details:
- Stored procedure names and their purposes
- Database table names and relationships
- Code snippets when relevant
- API handlers and endpoints
- Technical architecture details

This mode is appropriate for developers, technical consultants, and implementers who need the full technical context."""

    # Build user message with optional conversation history
    user_message_parts = []

    # Add conversation history if available
    if conversation_history:
        user_message_parts.append("=== CONVERSATION HISTORY ===")
        user_message_parts.append("Previous exchanges in this session for context:\n")
        for i, exchange in enumerate(conversation_history, 1):
            user_message_parts.append(f"Q{i}: {exchange['question']}")
            user_message_parts.append(f"A{i}: {exchange['answer'][:600]}...\n")  # Standardized context length
        user_message_parts.append("")

    # Add knowledge base context
    user_message_parts.append("=== KNOWLEDGE BASE CONTEXT ===")
    user_message_parts.append(context)
    user_message_parts.append("")

    # Add current question
    user_message_parts.append("=== CURRENT QUESTION ===")
    user_message_parts.append(query)
    user_message_parts.append("")

    # Add instructions
    user_message_parts.append("=== YOUR ANSWER ===")
    if conversation_history:
        user_message_parts.append("""This is a follow-up question in an ongoing conversation. Consider the conversation history when answering.
If this question refers to previous topics (using words like "it", "that", "how about", "what about"), use the conversation history to understand the context.

Provide a comprehensive answer that:
1. Starts with theoretical foundation (Direct Consolidation Framework + IFRS/IAS) if this is a new topic
2. Explains key principles and formulas
3. Describes Prophix.FC implementation
4. Includes diagrams and examples
5. References previous answers when relevant for continuity

Begin your answer now:""")
    else:
        user_message_parts.append("""Provide a comprehensive answer that:
1. Starts with theoretical foundation (Direct Consolidation Framework + IFRS/IAS)
2. Explains key principles and formulas
3. Describes Prophix.FC implementation
4. Includes diagrams and examples

Begin your answer now:""")

    user_message = "\n".join(user_message_parts)

    # Call Claude via Bedrock with proper system prompt
    body = json.dumps({
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": max_tokens,  # Uses tier-specific max_tokens
        "temperature": TEMPERATURE,
        "system": system_prompt,  # Proper system prompt
        "messages": [
            {
                "role": "user",
                "content": user_message  # Just context + question
            }
        ]
    })

    try:
        response = bedrock.invoke_model(
            modelId=model_id,  # Uses tier-specific model
            body=body,
            contentType="application/json",
            accept="application/json",
        )

        response_body = json.loads(response["body"].read())
        answer = response_body["content"][0]["text"]

        return answer

    except Exception as e:
        logger.error(f"Error calling Claude: {e}")
        return f"Error generating response: {str(e)}"


def generate_answer_streaming(query: str, context: str, conversation_history: list = None,
                               explanation_level: str = "Standard", model_tier: str = None,
                               knowledge_mode: str = "Business"):
    """
    Generate answer using AWS Bedrock Claude with STREAMING response.

    Yields text chunks as they're generated for real-time display.
    First words appear in 1-2 seconds, then streams continuously.
    """
    bedrock = get_bedrock_client()

    # Select model based on tier
    if model_tier is None:
        model_tier = DEFAULT_MODEL_TIER
    model_config = MODEL_TIERS.get(model_tier, MODEL_TIERS[DEFAULT_MODEL_TIER])
    model_id = model_config["id"]
    max_tokens = model_config["max_tokens"]

    # Adjust max_tokens based on explanation level
    # Only limit Executive Summary - streaming makes longer responses fine
    if explanation_level == "Executive Summary":
        max_tokens = min(max_tokens, 1000)  # ~400 words for quick overview

    # Level-specific instructions (matches non-streaming function)
    level_instructions = {
        "Executive Summary": """
# EXPLANATION LEVEL: EXECUTIVE SUMMARY
You are providing a HIGH-LEVEL OVERVIEW for busy executives and managers.

**Format Requirements:**
- Keep total response under 400 words
- Focus on business impact and key takeaways
- Use bullet points for quick scanning
- Include ONE key formula or diagram maximum
- Skip edge cases and technical details
- End with 2-3 bullet point summary
""",
        "Standard": """
# EXPLANATION LEVEL: STANDARD
You are providing a BALANCED EXPLANATION suitable for product owners and consolidation professionals.

**Format Requirements:**
- Provide comprehensive but focused coverage
- Include theory, principles, implementation, and examples
- Use diagrams and formulas where helpful
- Cover common scenarios and main edge cases
- Balance depth with readability
- Keep response under 1500 words
""",
        "Detailed": """
# EXPLANATION LEVEL: DETAILED
You are providing COMPREHENSIVE COVERAGE for consolidation specialists who need complete understanding.

**Format Requirements:**
- Provide exhaustive, in-depth coverage
- Include ALL edge cases and special situations
- Show multiple examples with varying complexity
- Include complete journal entries and calculations
- Reference specific IFRS paragraphs where applicable
- Include troubleshooting guidance and common mistakes
""",
    }

    # Build system prompt based on explanation level
    if explanation_level == "Executive Summary":
        system_prompt = f"""{level_instructions["Executive Summary"]}

You are a Financial Consolidation Expert. Provide concise, executive-level answers.

Structure: Definition → Key implications → IFRS reference → Prophix.FC mention"""
    else:
        system_prompt = f"""{level_instructions.get(explanation_level, level_instructions["Standard"])}

You are a Financial Consolidation Expert and Educator specializing in:
- The Direct Consolidation Framework methodology
- IFRS/IAS accounting standards (IFRS 3, IFRS 10, IFRS 11, IAS 21, IAS 27, IAS 28)
- Prophix.FC financial consolidation software implementation

Provide well-structured answers with theory, formulas, and practical implementation details.
Use markdown formatting and cite specific IFRS standards."""

    # Add business mode filtering instructions
    if knowledge_mode == "Business":
        system_prompt += """

BUSINESS MODE: Do NOT include technical details like stored procedure names (P_CONSO_*, P_CALC_*), database tables (TS_*, TD_*), SQL code, or programming code. Focus on business concepts, IFRS standards, and user-facing workflows only."""
    else:
        system_prompt += """

FULL TECHNICAL MODE: You may include all technical implementation details including stored procedures, database tables, and code snippets."""

    # Build user message
    user_message_parts = []

    if conversation_history:
        user_message_parts.append("=== CONVERSATION HISTORY ===")
        for i, exchange in enumerate(conversation_history[-3:], 1):
            user_message_parts.append(f"Q{i}: {exchange['question']}")
            user_message_parts.append(f"A{i}: {exchange['answer'][:600]}...\n")  # Standardized context length

    user_message_parts.append("=== KNOWLEDGE BASE CONTEXT ===")
    user_message_parts.append(context)
    user_message_parts.append("")
    user_message_parts.append("=== QUESTION ===")
    user_message_parts.append(query)

    user_message = "\n".join(user_message_parts)

    body = json.dumps({
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": max_tokens,
        "temperature": TEMPERATURE,
        "system": system_prompt,
        "messages": [{"role": "user", "content": user_message}]
    })

    try:
        # Use streaming API
        response = bedrock.invoke_model_with_response_stream(
            modelId=model_id,
            body=body,
            contentType="application/json",
            accept="application/json",
        )

        # Process the stream
        stream = response.get("body")
        if stream:
            for event in stream:
                chunk = event.get("chunk")
                if chunk:
                    chunk_bytes = chunk.get("bytes")
                    if not chunk_bytes:
                        continue
                    chunk_data = json.loads(chunk_bytes.decode())

                    # Handle different event types
                    if chunk_data.get("type") == "content_block_delta":
                        delta = chunk_data.get("delta", {})
                        if delta.get("type") == "text_delta":
                            text = delta.get("text", "")
                            if text:
                                yield text

    except Exception as e:
        logger.error(f"Error in streaming Claude call: {e}")
        yield "\n\nAn error occurred generating the response. Please try again."


def get_source_tier(result: Dict) -> tuple:
    """
    Determine the tier of a source based on its metadata.
    Returns (tier_name, tier_class) tuple for display.
    """
    source = result.get("metadata", {}).get("source", "Unknown").lower()
    topic = result.get("metadata", {}).get("topic", "")

    # Tier 1: Theoretical content (Direct Consolidation Framework, IFRS standards)
    if "direct_consolidation_chunks" in source or topic == "theory":
        return ("Theory", "tier-theory")
    # Tier 2: Help/UI content (user guides, how-to, help)
    elif "12-user-knowledge-base" in source or "help" in source or topic == "help":
        return ("Help", "tier-help")
    # Tier 3: Implementation content
    else:
        return ("Implementation", "tier-impl")


def generate_follow_up_questions(query: str, answer: str) -> list:
    """
    Generate smart follow-up questions based on the query and answer.
    Uses Claude to suggest 3 deeper questions for exploration.
    """
    bedrock = get_bedrock_client()

    system_prompt = """You are a Financial Consolidation Education assistant. Based on the user's question and the answer provided, suggest exactly 3 follow-up questions that would help them learn more deeply.

Rules:
- Questions should be specific and actionable
- Progress from the current topic to related deeper concepts
- Each question should be 1 sentence, under 80 characters
- Focus on practical understanding and application
- Return ONLY the 3 questions, one per line, no numbering or bullets"""

    user_message = f"""Question asked: {query}

Answer summary (first 500 chars): {answer[:500]}...

Generate 3 follow-up questions to deepen understanding:"""

    body = json.dumps({
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 300,
        "temperature": 0.7,
        "system": system_prompt,
        "messages": [{"role": "user", "content": user_message}]
    })

    try:
        response = bedrock.invoke_model(
            modelId=CLAUDE_FAST_MODEL_ID,  # Use fast model for auxiliary calls
            body=body,
            contentType="application/json",
            accept="application/json",
        )
        response_body = json.loads(response["body"].read())
        response_text = response_body["content"][0]["text"]

        # Parse questions (one per line)
        questions = [q.strip() for q in response_text.strip().split('\n') if q.strip()]
        # Clean up any numbering or bullets
        cleaned = []
        for q in questions[:3]:
            # Remove common prefixes like "1.", "1)", "-", "*", etc.
            q = q.lstrip('0123456789.-)*• ').strip()
            if q and q.endswith('?'):
                cleaned.append(q)
            elif q:
                cleaned.append(q + '?')
        return cleaned[:3]
    except Exception as e:
        logger.error(f"Error generating follow-up questions: {e}")
        # Return fallback questions based on common patterns
        return get_fallback_follow_ups(query)


def get_fallback_follow_ups(query: str) -> list:
    """Provide fallback follow-up questions when AI generation fails."""
    query_lower = query.lower()

    if "equity" in query_lower:
        return [
            "How is the equity pickup calculated in practice?",
            "What journal entries are needed for equity method?",
            "When does equity method become global integration?"
        ]
    elif "global" in query_lower or "integration" in query_lower:
        return [
            "How is NCI calculated in global integration?",
            "What eliminations are required for global integration?",
            "How does goodwill arise in global integration?"
        ]
    elif "goodwill" in query_lower:
        return [
            "How is goodwill tested for impairment?",
            "What is the difference between full and partial goodwill?",
            "How does NCI measurement affect goodwill?"
        ]
    elif "currency" in query_lower or "translation" in query_lower:
        return [
            "What exchange rates apply to different accounts?",
            "Where do translation adjustments appear?",
            "How does IAS 21 handle hyperinflation?"
        ]
    elif "elimination" in query_lower or "intercompany" in query_lower:
        return [
            "What types of intercompany transactions exist?",
            "How is unrealized profit in inventory eliminated?",
            "How are intercompany dividends handled?"
        ]
    else:
        return [
            "How does this concept apply in practice?",
            "What are common mistakes to avoid?",
            "How does Prophix.FC implement this?"
        ]


def generate_quiz_questions_rag(topic: str = None, count: int = 5, difficulty: str = "medium") -> list:
    """
    Generate quiz questions dynamically using RAG with adaptive difficulty.
    Queries the knowledge base and uses Claude to create multiple-choice questions.
    Returns list of {q, options, answer, explanation, difficulty} dicts.

    difficulty: "easy", "medium", or "hard"
    - easy: Basic recall and definition questions
    - medium: Understanding and application questions
    - hard: Analysis, edge cases, and complex scenarios
    """
    bedrock = get_bedrock_client()

    # Get random content from knowledge base for quiz generation
    topics = ["consolidation methods", "goodwill calculation", "NCI minority interest",
              "currency translation", "intercompany eliminations", "equity method",
              "IFRS 10 control", "IAS 21 currency", "ownership percentage"]

    if topic:
        search_topic = topic
    else:
        search_topic = random.choice(topics)

    # Search knowledge base for content
    results = search_business_layer(search_topic, n_results=5)
    if not results:
        return []

    # Build context from results
    context = "\n\n".join([r["content"][:500] for r in results[:3]])

    # Difficulty-specific instructions
    difficulty_instructions = {
        "easy": """
- Ask about basic definitions and terminology
- Focus on recall of key facts
- Use straightforward language
- Avoid complex scenarios or edge cases""",
        "medium": """
- Test understanding of concepts
- Include application scenarios
- Mix theoretical and practical questions
- Require connecting related concepts""",
        "hard": """
- Focus on complex scenarios and edge cases
- Ask about exceptions to rules
- Require analysis of multi-step problems
- Include questions about interactions between concepts
- Test deep understanding with tricky distractors"""
    }

    system_prompt = f"""You are a Financial Consolidation quiz generator. Create {difficulty.upper()} difficulty multiple-choice questions based on the provided knowledge base content.

Difficulty Guidelines for {difficulty.upper()}:
{difficulty_instructions.get(difficulty, difficulty_instructions["medium"])}

Rules:
- Generate exactly the requested number of questions
- Each question must have exactly 4 options (A, B, C, D)
- Only ONE option should be correct
- Questions should match the {difficulty} difficulty level
- Include a brief explanation for the correct answer
- Format response as valid JSON array"""

    user_message = f"""Based on this knowledge base content about {search_topic}:

{context}

Generate {count} multiple-choice quiz questions. Return ONLY a JSON array with this exact format:
[
  {{
    "q": "Question text here?",
    "options": ["Option A", "Option B", "Option C", "Option D"],
    "answer": 0,
    "explanation": "Brief explanation why this is correct"
  }}
]

The "answer" field is the index (0-3) of the correct option."""

    body = json.dumps({
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 2000,
        "temperature": 0.7,
        "system": system_prompt,
        "messages": [{"role": "user", "content": user_message}]
    })

    try:
        response = bedrock.invoke_model(
            modelId=CLAUDE_FAST_MODEL_ID,
            body=body,
            contentType="application/json",
            accept="application/json",
        )
        response_body = json.loads(response["body"].read())
        response_text = response_body["content"][0]["text"]

        # Parse JSON response
        # Find JSON array in response
        json_match = re.search(r'\[[\s\S]*\]', response_text)
        if json_match:
            questions = json.loads(json_match.group())
            return questions[:count]
        return []
    except Exception as e:
        logger.error(f"Error generating quiz questions: {e}")
        return []


def generate_related_topics_rag(query: str, answer: str) -> list:
    """
    Generate contextually related topics using RAG.
    Uses Claude to analyze query and answer, then suggest related exploration paths.
    Returns list of (label, question) tuples.
    """
    bedrock = get_bedrock_client()

    system_prompt = """You are a Financial Consolidation education assistant. Based on a user's question and the answer they received, suggest 4 related topics they should explore next.

Rules:
- Suggest topics that naturally follow from the current question
- Include a mix of deeper dives and related concepts
- Each suggestion should have a short label (2-4 words) and a search question
- Return ONLY a JSON array, no other text"""

    user_message = f"""User asked: {query}

Answer summary (first 400 chars): {answer[:400]}...

Suggest 4 related topics to explore next. Return ONLY a JSON array:
[
  {{"label": "Short Label", "question": "What is the full question to search?"}},
  ...
]"""

    body = json.dumps({
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 500,
        "temperature": 0.7,
        "system": system_prompt,
        "messages": [{"role": "user", "content": user_message}]
    })

    try:
        response = bedrock.invoke_model(
            modelId=CLAUDE_FAST_MODEL_ID,  # Use fast model for auxiliary calls
            body=body,
            contentType="application/json",
            accept="application/json",
        )
        response_body = json.loads(response["body"].read())
        response_text = response_body["content"][0]["text"]

        # Parse JSON
        json_match = re.search(r'\[[\s\S]*\]', response_text)
        if json_match:
            topics = json.loads(json_match.group())
            return [(t["label"], t["question"]) for t in topics[:4]]
        return []
    except Exception as e:
        logger.error(f"Error generating related topics: {e}")
        return []


@st.cache_data(ttl=3600, show_spinner="Loading glossary terms...")
def generate_glossary_terms_rag() -> dict:
    """
    Generate glossary terms by extracting key concepts from the knowledge base.
    Uses Claude to identify and define important terms.
    Returns dict with categories as keys and list of (term, query) tuples as values.
    """
    bedrock = get_bedrock_client()

    # Search for definitional content
    search_queries = [
        "definition terminology glossary",
        "key concepts consolidation",
        "IFRS standards definitions",
    ]

    all_content = []
    for sq in search_queries:
        results = search_business_layer(sq, n_results=5)
        for r in results:
            all_content.append(r["content"][:400])

    context = "\n\n---\n\n".join(all_content[:10])

    system_prompt = """You are a Financial Consolidation glossary generator. Extract key terms and concepts from the knowledge base content.

Rules:
- Identify 20-30 important terms
- Group them into 3 categories: A-G, H-P, Q-Z (alphabetically)
- Each term should have a short search query
- Return ONLY a JSON object, no other text"""

    user_message = f"""From this financial consolidation knowledge base content:

{context}

Extract key glossary terms. Return ONLY a JSON object:
{{
  "a_g": [{{"term": "Term Name", "query": "What is Term Name in consolidation?"}}],
  "h_p": [...],
  "q_z": [...]
}}"""

    body = json.dumps({
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 2000,
        "temperature": 0.3,
        "system": system_prompt,
        "messages": [{"role": "user", "content": user_message}]
    })

    try:
        response = bedrock.invoke_model(
            modelId=CLAUDE_FAST_MODEL_ID,
            body=body,
            contentType="application/json",
            accept="application/json",
        )
        response_body = json.loads(response["body"].read())
        response_text = response_body["content"][0]["text"]

        # Parse JSON
        json_match = re.search(r'\{[\s\S]*\}', response_text)
        if json_match:
            glossary = json.loads(json_match.group())
            return glossary
        return {"a_g": [], "h_p": [], "q_z": []}
    except Exception as e:
        logger.error(f"Error generating glossary: {e}")
        return {"a_g": [], "h_p": [], "q_z": []}


@st.cache_data(ttl=1800, show_spinner="Loading search suggestions...")
def generate_autocomplete_suggestions_rag() -> list:
    """
    Generate fresh autocomplete suggestions based on knowledge base content.
    Returns list of suggested questions.
    """
    bedrock = get_bedrock_client()

    # Get diverse content from knowledge base
    search_queries = ["consolidation overview", "IFRS standards", "calculations formulas",
                      "eliminations process", "currency translation"]

    all_content = []
    for sq in search_queries:
        results = search_business_layer(sq, n_results=3)
        for r in results:
            all_content.append(r["content"][:300])

    context = "\n\n".join(all_content[:8])

    system_prompt = """You are a Financial Consolidation education assistant. Generate useful search questions that users might want to ask.

Rules:
- Generate 20 diverse questions covering different topics
- Questions should be clear and specific
- Mix beginner and advanced questions
- Return ONLY a JSON array of strings"""

    user_message = f"""Based on this knowledge base content:

{context}

Generate 20 useful questions users might search for. Return ONLY a JSON array:
["Question 1?", "Question 2?", ...]"""

    body = json.dumps({
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 1500,
        "temperature": 0.8,
        "system": system_prompt,
        "messages": [{"role": "user", "content": user_message}]
    })

    try:
        response = bedrock.invoke_model(
            modelId=CLAUDE_FAST_MODEL_ID,
            body=body,
            contentType="application/json",
            accept="application/json",
        )
        response_body = json.loads(response["body"].read())
        response_text = response_body["content"][0]["text"]

        # Parse JSON
        json_match = re.search(r'\[[\s\S]*\]', response_text)
        if json_match:
            questions = json.loads(json_match.group())
            return questions[:20]
        return []
    except Exception as e:
        logger.error(f"Error generating autocomplete suggestions: {e}")
        return []


@st.cache_data(ttl=3600, show_spinner="Generating learning topics...")
def generate_learning_path_topics_rag(path_id: str, path_description: str) -> list:
    """
    Generate learning path topics dynamically using RAG.
    Returns list of (topic_id, label, query) tuples for the specified learning path.

    path_id: "beginner", "methods", "currency", "eliminations", "calculations"
    path_description: Description of the learning path focus
    """
    bedrock = get_bedrock_client()

    # Path-specific search topics for context
    path_search_topics = {
        "beginner": ["consolidation basics", "consolidation introduction", "consolidation methods overview"],
        "methods": ["global integration", "equity method", "proportional consolidation", "consolidation methods comparison"],
        "currency": ["currency translation", "IAS 21", "functional currency", "translation adjustments CTA"],
        "eliminations": ["intercompany eliminations", "participation elimination", "dividend elimination", "unrealized profit"],
        "calculations": ["goodwill calculation", "NCI minority interest", "ownership percentage", "acquisition accounting"],
    }

    search_topics = path_search_topics.get(path_id, ["financial consolidation"])

    # Gather content from knowledge base
    all_content = []
    for topic in search_topics:
        results = search_business_layer(topic, n_results=2)
        for r in results:
            all_content.append(r["content"][:400])

    context = "\n\n".join(all_content[:6])

    # Path-specific instructions
    path_instructions = {
        "beginner": "Create foundational questions that introduce basic consolidation concepts. Progress from 'what is' to 'why' to 'how'.",
        "methods": "Create questions that explore each consolidation method in depth - global integration, equity method, and proportional. Include comparison questions.",
        "currency": "Create questions about currency translation, exchange rates, IAS 21 requirements, and translation adjustments (CTA).",
        "eliminations": "Create questions about intercompany eliminations, participation eliminations, dividend eliminations, and unrealized profit elimination.",
        "calculations": "Create questions about key calculations: goodwill, NCI/minority interest, ownership percentages, and acquisition accounting.",
    }

    system_prompt = f"""You are a Financial Consolidation education curriculum designer. Create a structured learning path with progressive questions.

Path Focus: {path_description}
{path_instructions.get(path_id, '')}

Rules:
- Generate exactly 4 progressive learning topics
- Each topic should build on previous knowledge
- Questions should be clear and educational
- Number topics 1-4 with descriptive labels
- Return valid JSON array"""

    user_message = f"""Based on this knowledge base content:

{context}

Generate 4 learning topics for the "{path_id}" learning path. Return ONLY a JSON array:
[
  {{"id": "{path_id}1", "label": "1. Topic Label", "query": "Educational question about this topic?"}},
  {{"id": "{path_id}2", "label": "2. Topic Label", "query": "Educational question about this topic?"}},
  {{"id": "{path_id}3", "label": "3. Topic Label", "query": "Educational question about this topic?"}},
  {{"id": "{path_id}4", "label": "4. Topic Label", "query": "Educational question about this topic?"}}
]"""

    body = json.dumps({
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 1000,
        "temperature": 0.6,
        "system": system_prompt,
        "messages": [{"role": "user", "content": user_message}]
    })

    try:
        response = bedrock.invoke_model(
            modelId=CLAUDE_FAST_MODEL_ID,
            body=body,
            contentType="application/json",
            accept="application/json",
        )
        response_body = json.loads(response["body"].read())
        response_text = response_body["content"][0]["text"]

        # Parse JSON
        json_match = re.search(r'\[[\s\S]*\]', response_text)
        if json_match:
            topics_data = json.loads(json_match.group())
            # Convert to tuple format (id, label, query)
            return [(t["id"], t["label"], t["query"]) for t in topics_data[:4]]
        return []
    except Exception as e:
        logger.error(f"Error generating learning path topics: {e}")
        return []


def get_related_topics(query: str) -> list:
    """
    Get related topic suggestions based on the current query.
    Returns a list of (label, question) tuples.
    NOTE: This is the legacy hardcoded version, kept as fallback.
    """
    query_lower = query.lower()

    # Define topic relationships
    topic_suggestions = {
        # Consolidation methods
        "equity": [
            ("Global Integration", "How does global integration differ from equity method?"),
            ("Significant Influence", "What defines significant influence under IAS 28?"),
            ("Equity Pickup", "How is the equity pickup calculated?"),
        ],
        "global": [
            ("Equity Method", "How does equity method work for 20-50% ownership?"),
            ("NCI Calculation", "How is minority interest calculated in global integration?"),
            ("Full Consolidation", "What accounts are consolidated line-by-line?"),
        ],
        "proportional": [
            ("Joint Ventures", "What is the difference between joint ventures and associates?"),
            ("IFRS 11", "What does IFRS 11 say about joint arrangements?"),
            ("Global vs Proportional", "When to use global integration vs proportional?"),
        ],
        # Calculations
        "goodwill": [
            ("Impairment Testing", "How is goodwill impairment testing performed?"),
            ("Fair Value", "How is fair value determined in acquisitions?"),
            ("Purchase Price", "What components make up the purchase price?"),
        ],
        "minority": [
            ("NCI Methods", "What are the methods for measuring NCI?"),
            ("Profit Attribution", "How is profit attributed to minority shareholders?"),
            ("Goodwill & NCI", "How does NCI affect goodwill calculation?"),
        ],
        "nci": [
            ("Minority Interest", "What is the difference between NCI and minority interest?"),
            ("Profit Attribution", "How is profit attributed to non-controlling interests?"),
            ("NCI Measurement", "What are full goodwill vs partial goodwill methods?"),
        ],
        # Currency
        "currency": [
            ("IAS 21", "What are the key requirements of IAS 21?"),
            ("Exchange Rates", "What exchange rates are used for different accounts?"),
            ("Translation Adjustments", "Where do translation adjustments appear?"),
        ],
        "translation": [
            ("Functional Currency", "How do you determine functional currency?"),
            ("Hyperinflation", "How does IAS 29 affect currency translation?"),
            ("Rate Types", "What are closing, average, and historical rates?"),
        ],
        # Eliminations
        "elimination": [
            ("Intercompany Types", "What types of intercompany transactions exist?"),
            ("Participation", "How do participation eliminations work?"),
            ("Dividends", "How are intercompany dividends eliminated?"),
        ],
        "intercompany": [
            ("Elimination Process", "What is the intercompany elimination process?"),
            ("Profit in Stock", "How is unrealized profit in inventory eliminated?"),
            ("Reconciliation", "How do you reconcile intercompany balances?"),
        ],
        # Ownership
        "ownership": [
            ("Direct vs Indirect", "How do direct and indirect holdings differ?"),
            ("Control vs Ownership", "What is the difference between control and ownership?"),
            ("Multi-tier Holdings", "How are multi-tier ownership structures handled?"),
        ],
        "control": [
            ("IFRS 10", "What does IFRS 10 say about control?"),
            ("Voting Rights", "How do voting rights affect consolidation?"),
            ("De Facto Control", "What is de facto control?"),
        ],
        # Workflow
        "workflow": [
            ("Data Collection", "What data is collected for consolidation?"),
            ("Validation Steps", "What validation steps are in the workflow?"),
            ("Reports", "What reports are generated after consolidation?"),
        ],
        "consolidat": [
            ("Workflow Steps", "What are the steps in the consolidation workflow?"),
            ("Methods Overview", "What consolidation methods exist?"),
            ("IFRS Standards", "What IFRS standards govern consolidation?"),
        ],
    }

    # Find matching topics
    related = []
    for keyword, suggestions in topic_suggestions.items():
        if keyword in query_lower:
            related.extend(suggestions)

    # Default suggestions if no specific match
    if not related:
        related = [
            ("Consolidation Methods", "What are the different consolidation methods?"),
            ("Key Calculations", "What are the key calculations in consolidation?"),
            ("IFRS Standards", "What IFRS standards apply to consolidation?"),
        ]

    # Return unique suggestions (max 4)
    seen = set()
    unique_related = []
    for item in related:
        if item[0] not in seen:
            seen.add(item[0])
            unique_related.append(item)
            if len(unique_related) >= 4:
                break

    return unique_related


def main():
    """Main Streamlit application."""

    # Check URL params for concept map query (set by concept map link click)
    query_params = st.query_params
    if "cm_query" in query_params:
        cm_query = unquote(query_params["cm_query"])
        # Clear the URL param
        st.query_params.clear()
        # Set the query and trigger search
        st.session_state.query = cm_query
        st.session_state.trigger_search = True
        st.session_state.show_concept_map = False

    # Check URL params for go_deeper (set by Go Deeper button click)
    if "go_deeper" in query_params:
        deeper_query = unquote(query_params["go_deeper"])
        # Clear the URL param
        st.query_params.clear()
        # Set the query and trigger detailed search
        st.session_state.query = deeper_query
        st.session_state.trigger_search = True
        st.session_state.force_detailed = True

    # Initialize session state for conversation history
    if "conversation_history" not in st.session_state:
        st.session_state.conversation_history = []
    if "query" not in st.session_state:
        st.session_state.query = ""
    if "trigger_search" not in st.session_state:
        st.session_state.trigger_search = False
    if "search_history" not in st.session_state:
        st.session_state.search_history = []
    if "learning_progress" not in st.session_state:
        st.session_state.learning_progress = {}
    if "current_learning_topic" not in st.session_state:
        st.session_state.current_learning_topic = None
    if "force_detailed" not in st.session_state:
        st.session_state.force_detailed = False
    if "model_tier" not in st.session_state:
        st.session_state.model_tier = DEFAULT_MODEL_TIER
    if "explanation_level" not in st.session_state:
        st.session_state.explanation_level = "Executive Summary"  # Default
    if "selected_topic" not in st.session_state:
        st.session_state.selected_topic = "All Topics"  # Default
    if "knowledge_mode" not in st.session_state:
        st.session_state.knowledge_mode = DEFAULT_KNOWLEDGE_MODE  # From env var or "Business"

    # Keyboard shortcuts and localStorage JavaScript (injected once)
    keyboard_shortcuts_js = """
    <script>
    // Search History localStorage functions
    const HISTORY_KEY = 'fc_search_history';
    const PROGRESS_KEY = 'fc_learning_progress';
    const MAX_HISTORY = 10;

    function getSearchHistory() {
        try {
            const history = localStorage.getItem(HISTORY_KEY);
            return history ? JSON.parse(history) : [];
        } catch (e) {
            return [];
        }
    }

    function saveToHistory(query) {
        if (!query || query.trim() === '') return;
        try {
            let history = getSearchHistory();
            history = history.filter(q => q.toLowerCase() !== query.toLowerCase());
            history.unshift(query);
            history = history.slice(0, MAX_HISTORY);
            localStorage.setItem(HISTORY_KEY, JSON.stringify(history));
        } catch (e) {
            console.error('Failed to save search history:', e);
        }
    }

    function clearHistory() {
        localStorage.removeItem(HISTORY_KEY);
    }

    // Learning Path Progress functions
    function getLearningProgress() {
        try {
            const progress = localStorage.getItem(PROGRESS_KEY);
            return progress ? JSON.parse(progress) : {};
        } catch (e) {
            return {};
        }
    }

    function markTopicComplete(pathId, topicId) {
        try {
            let progress = getLearningProgress();
            if (!progress[pathId]) {
                progress[pathId] = [];
            }
            if (!progress[pathId].includes(topicId)) {
                progress[pathId].push(topicId);
            }
            localStorage.setItem(PROGRESS_KEY, JSON.stringify(progress));
            return progress;
        } catch (e) {
            console.error('Failed to save progress:', e);
            return {};
        }
    }

    function isTopicComplete(pathId, topicId) {
        const progress = getLearningProgress();
        return progress[pathId] && progress[pathId].includes(topicId);
    }

    function getPathProgress(pathId, totalTopics) {
        const progress = getLearningProgress();
        const completed = progress[pathId] ? progress[pathId].length : 0;
        return {
            completed: completed,
            total: totalTopics,
            percentage: totalTopics > 0 ? Math.round((completed / totalTopics) * 100) : 0
        };
    }

    function clearProgress() {
        localStorage.removeItem(PROGRESS_KEY);
    }

    // Keyboard shortcuts
    document.addEventListener('keydown', function(e) {
        if ((e.ctrlKey && e.key === 'k') || (e.key === '/' && !e.target.matches('input, textarea'))) {
            e.preventDefault();
            const searchInput = document.querySelector('input[data-testid="stTextInput"]') ||
                               document.querySelector('input[type="text"]');
            if (searchInput) {
                searchInput.focus();
                searchInput.select();
            }
        }
        if (e.key === 'Escape') {
            const activeElement = document.activeElement;
            if (activeElement && activeElement.matches('input, textarea')) {
                activeElement.blur();
            }
        }
    });

    // Bookmarks functions
    const BOOKMARKS_KEY = 'fc_bookmarks';

    function getBookmarks() {
        try {
            const bookmarks = localStorage.getItem(BOOKMARKS_KEY);
            return bookmarks ? JSON.parse(bookmarks) : [];
        } catch (e) {
            return [];
        }
    }

    function addBookmark(question, answer, timestamp) {
        try {
            let bookmarks = getBookmarks();
            // Check if already bookmarked
            if (!bookmarks.find(b => b.question === question)) {
                bookmarks.unshift({ question, answer, timestamp, id: Date.now() });
                bookmarks = bookmarks.slice(0, 20); // Keep max 20 bookmarks
                localStorage.setItem(BOOKMARKS_KEY, JSON.stringify(bookmarks));
            }
            return bookmarks;
        } catch (e) {
            console.error('Failed to save bookmark:', e);
            return [];
        }
    }

    function removeBookmark(id) {
        try {
            let bookmarks = getBookmarks();
            bookmarks = bookmarks.filter(b => b.id !== id);
            localStorage.setItem(BOOKMARKS_KEY, JSON.stringify(bookmarks));
            return bookmarks;
        } catch (e) {
            return [];
        }
    }

    function isBookmarked(question) {
        const bookmarks = getBookmarks();
        return bookmarks.some(b => b.question === question);
    }

    function clearBookmarks() {
        localStorage.removeItem(BOOKMARKS_KEY);
    }

    // Quiz Performance Tracking (for adaptive learning)
    const QUIZ_PERFORMANCE_KEY = 'fc_quiz_performance';

    function getQuizPerformance() {
        try {
            const perf = localStorage.getItem(QUIZ_PERFORMANCE_KEY);
            return perf ? JSON.parse(perf) : { totalQuizzes: 0, totalCorrect: 0, totalQuestions: 0, topicScores: {} };
        } catch (e) {
            return { totalQuizzes: 0, totalCorrect: 0, totalQuestions: 0, topicScores: {} };
        }
    }

    function saveQuizResult(score, total, topic) {
        try {
            let perf = getQuizPerformance();
            perf.totalQuizzes += 1;
            perf.totalCorrect += score;
            perf.totalQuestions += total;
            if (topic) {
                if (!perf.topicScores[topic]) {
                    perf.topicScores[topic] = { correct: 0, total: 0 };
                }
                perf.topicScores[topic].correct += score;
                perf.topicScores[topic].total += total;
            }
            localStorage.setItem(QUIZ_PERFORMANCE_KEY, JSON.stringify(perf));
            return perf;
        } catch (e) {
            return {};
        }
    }

    function getQuizDifficulty() {
        const perf = getQuizPerformance();
        if (perf.totalQuestions < 5) return 'medium'; // Not enough data
        const accuracy = perf.totalCorrect / perf.totalQuestions;
        if (accuracy >= 0.8) return 'hard';
        if (accuracy <= 0.4) return 'easy';
        return 'medium';
    }

    function clearQuizPerformance() {
        localStorage.removeItem(QUIZ_PERFORMANCE_KEY);
    }

    // Make functions available globally
    window.fcSearchHistory = {
        get: getSearchHistory,
        save: saveToHistory,
        clear: clearHistory
    };
    window.fcLearningProgress = {
        get: getLearningProgress,
        mark: markTopicComplete,
        isComplete: isTopicComplete,
        getPath: getPathProgress,
        clear: clearProgress
    };
    window.fcBookmarks = {
        get: getBookmarks,
        add: addBookmark,
        remove: removeBookmark,
        isBookmarked: isBookmarked,
        clear: clearBookmarks
    };
    window.fcQuizPerformance = {
        get: getQuizPerformance,
        save: saveQuizResult,
        getDifficulty: getQuizDifficulty,
        clear: clearQuizPerformance
    };
    </script>
    """
    st.components.v1.html(keyboard_shortcuts_js, height=0)

    # Define learning paths data structure with RAG-generated topics and hardcoded fallback
    # Hardcoded fallback topics for each path
    fallback_learning_paths = {
        "beginner": {
            "title": "Beginner Path",
            "description": "Start here if you're new to consolidation",
            "topics": [
                ("b1", "1. What is consolidation?", "What is financial consolidation and why is it needed?"),
                ("b2", "2. Consolidation methods", "What are the different consolidation methods and when to use each?"),
                ("b3", "3. The workflow steps", "What are the steps in the consolidation workflow?"),
                ("b4", "4. Key terminology", "What are the key terms I need to know for financial consolidation?"),
            ]
        },
        "methods": {
            "title": "Consolidation Methods",
            "description": "Deep dive into each method",
            "topics": [
                ("m1", "Global Integration (>50%)", "How does global integration consolidation work in detail?"),
                ("m2", "Equity Method (20-50%)", "How does equity method consolidation work in detail?"),
                ("m3", "Proportional Method", "How does proportional consolidation work and when is it used?"),
                ("m4", "Method comparison", "Compare global integration, equity method, and proportional consolidation"),
            ]
        },
        "currency": {
            "title": "Currency & Translation",
            "description": "Multi-currency consolidation",
            "topics": [
                ("c1", "IAS 21 Overview", "What does IAS 21 say about currency translation in consolidation?"),
                ("c2", "Translation methods", "What are the currency translation methods and exchange rate types?"),
                ("c3", "Translation adjustments", "How do currency translation adjustments work?"),
            ]
        },
        "eliminations": {
            "title": "Eliminations",
            "description": "Intercompany eliminations",
            "topics": [
                ("e1", "Intercompany basics", "What are intercompany eliminations and why are they needed?"),
                ("e2", "Participation eliminations", "How do participation eliminations work?"),
                ("e3", "Dividend eliminations", "How are dividends eliminated in consolidation?"),
            ]
        },
        "calculations": {
            "title": "Calculations",
            "description": "Key consolidation calculations",
            "topics": [
                ("calc1", "Goodwill calculation", "How is goodwill calculated in consolidation?"),
                ("calc2", "Minority interest (NCI)", "How is minority interest (NCI) calculated?"),
                ("calc3", "Ownership percentages", "How are direct and indirect ownership percentages calculated?"),
            ]
        },
    }

    # Use session state to cache learning paths (lazy RAG generation)
    # RAG enhancement only happens when user expands a learning path
    if "learning_paths_initialized" not in st.session_state:
        learning_paths = {}
        for path_id, path_data in fallback_learning_paths.items():
            learning_paths[path_id] = {
                "title": path_data["title"],
                "description": path_data["description"],
                "topics": path_data["topics"],  # Start with fallback
                "rag_enhanced": False,
                "rag_attempted": False  # Track per-path RAG attempts
            }
        st.session_state.learning_paths = learning_paths
        st.session_state.learning_paths_initialized = True

    # Use the session state version (RAG enhancement happens lazily in render_learning_path)
    learning_paths = st.session_state.learning_paths

    # Common questions for autocomplete - use session state to avoid repeated RAG calls
    # Hardcoded fallback questions
    fallback_questions = [
        "What is financial consolidation?",
        "How does the equity method work?",
        "How does global integration work?",
        "What is the difference between consolidation methods?",
        "How is goodwill calculated?",
        "How is minority interest (NCI) calculated?",
        "What are intercompany eliminations?",
        "How does currency translation work?",
        "What does IFRS 10 say about control?",
        "What does IAS 28 say about associates?",
        "What is the consolidation workflow?",
        "How are dividends eliminated?",
        "What is proportional consolidation?",
        "How do participation eliminations work?",
        "What exchange rates are used for translation?",
        "What is cumulative translation adjustment (CTA)?",
        "How are direct and indirect ownership calculated?",
        "What is significant influence?",
        "When does equity method become global integration?",
        "What is goodwill impairment?",
    ]

    # Initialize with fallback (RAG enhancement happens lazily when user searches)
    if "common_questions" not in st.session_state:
        st.session_state.common_questions = fallback_questions
        st.session_state.autocomplete_rag_attempted = False

    # RAG suggestions loaded lazily - not at page load
    common_questions = st.session_state.common_questions

    # Case Studies data - real-world consolidation scenarios
    case_studies = {
        "acquisition": {
            "title": "Company Acquisition",
            "subtitle": "80% acquisition with goodwill",
            "description": "Parent Corp acquires 80% of Target Inc for $800,000. Learn how to calculate goodwill, NCI, and perform the acquisition elimination.",
            "scenario": """**Scenario: Parent Corp acquires Target Inc**

**Given Information:**
- Purchase price: $800,000 for 80% ownership
- Target Inc's book value of equity: $600,000
- Fair value adjustment on PP&E: +$100,000
- Target's identifiable net assets at fair value: $700,000

**Your Task:**
Calculate goodwill and NCI, then determine the elimination journal entry.""",
            "questions": [
                "How is goodwill calculated when acquiring 80% of a company?",
                "What is the NCI calculation for an 80% acquisition?",
                "What elimination entries are needed for a business combination?",
            ]
        },
        "equity_method": {
            "title": "Equity Method Investment",
            "subtitle": "30% associate with equity pickup",
            "description": "Investor Co holds 30% of Associate Ltd. Calculate the equity method pickup when Associate reports net income of $500,000.",
            "scenario": """**Scenario: Investor Co's 30% investment in Associate Ltd**

**Given Information:**
- Ownership: 30% (significant influence, no control)
- Investment cost: $300,000
- Associate's net income for the year: $500,000
- Associate declared dividends: $100,000

**Your Task:**
Calculate the equity pickup and updated investment balance.""",
            "questions": [
                "How is equity method pickup calculated?",
                "How do dividends affect equity method investments?",
                "What journal entries are needed for equity method accounting?",
            ]
        },
        "currency": {
            "title": "Currency Translation",
            "subtitle": "EUR subsidiary in USD group",
            "description": "Translate a EUR-denominated subsidiary's trial balance to USD using IAS 21 principles.",
            "scenario": """**Scenario: Translating EuroSub's financial statements**

**Given Information:**
- Functional currency: EUR
- Presentation currency: USD
- Closing rate (EUR/USD): 1.10
- Average rate (EUR/USD): 1.08
- Historical rate (equity): 1.05
- EuroSub's equity: EUR 1,000,000
- EuroSub's net income: EUR 200,000
- EuroSub's assets: EUR 2,500,000

**Your Task:**
Translate the trial balance and calculate the CTA.""",
            "questions": [
                "What exchange rates apply to different accounts under IAS 21?",
                "How is the cumulative translation adjustment calculated?",
                "Where does the translation adjustment appear in financial statements?",
            ]
        },
        "intercompany": {
            "title": "Intercompany Elimination",
            "subtitle": "Upstream inventory sale",
            "description": "Subsidiary sold inventory to Parent with a 25% markup. $400,000 remains unsold at year-end.",
            "scenario": """**Scenario: Unrealized profit in inventory**

**Given Information:**
- Subsidiary sold goods to Parent for $500,000
- Subsidiary's cost: $400,000 (25% markup)
- Remaining in Parent's inventory at year-end: $400,000
- Parent owns 80% of Subsidiary

**Your Task:**
Calculate the unrealized profit elimination and NCI impact.""",
            "questions": [
                "How is unrealized profit in inventory calculated?",
                "How does NCI share in upstream intercompany profit elimination?",
                "What journal entries eliminate intercompany inventory profit?",
            ]
        },
        "multi_tier": {
            "title": "Multi-Tier Ownership",
            "subtitle": "Indirect holdings calculation",
            "description": "Parent owns 80% of Sub A, which owns 60% of Sub B. Calculate effective ownership and consolidation treatment.",
            "scenario": """**Scenario: Three-tier group structure**

**Given Information:**
- Parent owns 80% of Subsidiary A (direct)
- Subsidiary A owns 60% of Subsidiary B
- Both subsidiaries are controlled entities

**Your Task:**
Calculate effective ownership in Sub B and determine NCI at each level.""",
            "questions": [
                "How is indirect ownership percentage calculated?",
                "How is NCI calculated in multi-tier structures?",
                "What consolidation method applies to indirect subsidiaries?",
            ]
        },
    }

    # Helper function to render progress bar
    def render_progress_bar(path_id, total_topics):
        progress = st.session_state.learning_progress.get(path_id, [])
        completed = len(progress)
        percentage = int((completed / total_topics) * 100) if total_topics > 0 else 0
        st.markdown(f"""
        <div class="progress-text">{completed}/{total_topics} completed ({percentage}%)</div>
        <div class="progress-bar-container">
            <div class="progress-bar-fill" style="width: {percentage}%;"></div>
        </div>
        """, unsafe_allow_html=True)

    # Helper function to render learning path topic button (left-aligned)
    def render_topic_button(path_id, topic_id, label, query):
        progress = st.session_state.learning_progress.get(path_id, [])
        is_complete = topic_id in progress
        check = "✓ " if is_complete else ""
        btn_label = f"{check}{label}"

        if st.button(btn_label, key=f"lp_{path_id}_{topic_id}"):
            # Mark as complete
            if path_id not in st.session_state.learning_progress:
                st.session_state.learning_progress[path_id] = []
            if topic_id not in st.session_state.learning_progress[path_id]:
                st.session_state.learning_progress[path_id].append(topic_id)
            # Save to localStorage
            st.components.v1.html(f"<script>if(window.fcLearningProgress) window.fcLearningProgress.mark('{path_id}', '{topic_id}');</script>", height=0)
            # Trigger search
            st.session_state.query = query
            st.session_state.trigger_search = True
            st.rerun()

    # Sidebar - Learning Paths and About section
    with st.sidebar:
        # Learning Paths header with reset option (single line)
        st.markdown("""
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
            <span style="font-size: 1.1em; font-weight: 600;">Learning Paths</span>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Reset Progress", key="reset_progress", help="Clear all progress", use_container_width=True, type="primary"):
            st.session_state.learning_progress = {}
            st.components.v1.html("<script>if(window.fcLearningProgress) window.fcLearningProgress.clear();</script>", height=0)
            st.rerun()

        # Calculate total progress
        total_topics = sum(len(p["topics"]) for p in learning_paths.values())
        total_completed = sum(len(st.session_state.learning_progress.get(pid, [])) for pid in learning_paths.keys())
        overall_pct = int((total_completed / total_topics) * 100) if total_topics > 0 else 0

        if total_completed > 0:
            st.markdown(f"""
            <div class="progress-text">Overall: {total_completed}/{total_topics} topics ({overall_pct}%)</div>
            <div class="progress-bar-container">
                <div class="progress-bar-fill" style="width: {overall_pct}%;"></div>
            </div>
            """, unsafe_allow_html=True)

        # Render each learning path (with RAG indicator when dynamically generated)
        for path_id, path_data in learning_paths.items():
            progress = st.session_state.learning_progress.get(path_id, [])
            completed = len(progress)
            total = len(path_data["topics"])
            pct = int((completed / total) * 100) if total > 0 else 0

            # Show completion status in expander title (no emojis)
            title_suffix = f" ({completed}/{total})" if completed > 0 else ""
            with st.expander(f"{path_data['title']}{title_suffix}", expanded=False):
                # Show RAG badge if enhanced (inside expander, no emoji)
                if path_data.get("rag_enhanced", False):
                    st.markdown("""<span style="background-color: rgba(91, 127, 255, 0.2); color: #5B7FFF; padding: 2px 8px; border-radius: 8px; font-size: 10px;">AI-Generated</span>""", unsafe_allow_html=True)
                else:
                    # Offer to enhance with AI (lazy loading)
                    if st.button("Enhance with AI", key=f"enhance_{path_id}", help="Generate better topics using AI", use_container_width=True, type="primary"):
                        with st.spinner("Generating topics..."):
                            try:
                                rag_topics = generate_learning_path_topics_rag(path_id, path_data["description"])
                                if rag_topics and len(rag_topics) >= 3:
                                    st.session_state.learning_paths[path_id]["topics"] = rag_topics
                                    st.session_state.learning_paths[path_id]["rag_enhanced"] = True
                                    st.rerun()
                            except Exception:
                                st.warning("Could not generate AI topics")
                st.caption(path_data["description"])
                render_progress_bar(path_id, total)

                for topic_id, label, query in path_data["topics"]:
                    render_topic_button(path_id, topic_id, label, query)

        st.markdown("")  # Spacing

        # Glossary - Quick reference for key terms (lazy RAG loading)
        st.markdown("### Glossary")

        # Initialize glossary in session state with fallback
        if "glossary_initialized" not in st.session_state:
            st.session_state.glossary_ag = [
                ("Associate", "What is an associate in consolidation?"),
                ("Control", "What is control in financial consolidation?"),
                ("Consolidation", "What is financial consolidation?"),
                ("CTA", "What is Cumulative Translation Adjustment (CTA)?"),
                ("Elimination", "What are eliminations in consolidation?"),
                ("Equity Method", "How does the equity method work?"),
                ("Functional Currency", "What is functional currency?"),
                ("Goodwill", "What is goodwill and how is it calculated?"),
                ("Global Integration", "How does global integration consolidation work?"),
            ]
            st.session_state.glossary_hp = [
                ("Hyperinflation", "What is hyperinflation under IAS 29?"),
                ("IFRS 3", "What does IFRS 3 cover?"),
                ("IFRS 10", "What does IFRS 10 say about control?"),
                ("IFRS 11", "What does IFRS 11 say about joint arrangements?"),
                ("IAS 21", "What does IAS 21 say about currency translation?"),
                ("IAS 28", "What does IAS 28 say about associates?"),
                ("Intercompany", "What are intercompany transactions?"),
                ("Joint Venture", "What is a joint venture in consolidation?"),
                ("Minority Interest", "What is minority interest (NCI)?"),
                ("NCI", "How is non-controlling interest calculated?"),
                ("Participation", "What is participation in consolidation?"),
                ("Proportional", "How does proportional consolidation work?"),
            ]
            st.session_state.glossary_rz = [
                ("Restatement", "What is restatement in consolidation?"),
                ("Significant Influence", "What is significant influence under IAS 28?"),
                ("Step Acquisition", "What is a step acquisition?"),
                ("Subsidiary", "What defines a subsidiary?"),
                ("Translation", "How does currency translation work?"),
                ("Translation Adjustment", "What are translation adjustments?"),
                ("Unrealized Profit", "What is unrealized profit elimination?"),
                ("Voting Rights", "How do voting rights affect consolidation?"),
            ]
            st.session_state.glossary_rag_enhanced = False
            st.session_state.glossary_initialized = True

        # Show status and enhance button
        if st.session_state.glossary_rag_enhanced:
            st.caption("AI-generated from knowledge base")
        else:
            if st.button("Enhance with AI", key="enhance_glossary", help="Generate better terms using AI", use_container_width=True, type="primary"):
                with st.spinner("Loading glossary terms..."):
                    try:
                        rag_glossary = generate_glossary_terms_rag()
                        if rag_glossary:
                            rag_ag = [(t["term"], t["query"]) for t in rag_glossary.get("a_g", [])]
                            rag_hp = [(t["term"], t["query"]) for t in rag_glossary.get("h_p", [])]
                            rag_rz = [(t["term"], t["query"]) for t in rag_glossary.get("q_z", [])]
                            if rag_ag:
                                st.session_state.glossary_ag = rag_ag
                            if rag_hp:
                                st.session_state.glossary_hp = rag_hp
                            if rag_rz:
                                st.session_state.glossary_rz = rag_rz
                            st.session_state.glossary_rag_enhanced = True
                            st.rerun()
                    except Exception:
                        st.warning("Could not generate AI glossary")

        # Use session state glossary
        glossary_ag = st.session_state.glossary_ag
        glossary_hp = st.session_state.glossary_hp
        glossary_rz = st.session_state.glossary_rz

        with st.expander("Terms A-G", expanded=False):
            for term, query in glossary_ag:
                if st.button(term, key=f"gl_ag_{term}"):
                    st.session_state.query = query
                    st.session_state.trigger_search = True
                    st.rerun()

        with st.expander("Terms H-P", expanded=False):
            for term, query in glossary_hp:
                if st.button(term, key=f"gl_hp_{term}"):
                    st.session_state.query = query
                    st.session_state.trigger_search = True
                    st.rerun()

        with st.expander("Terms R-Z", expanded=False):
            for term, query in glossary_rz:
                if st.button(term, key=f"gl_rz_{term}"):
                    st.session_state.query = query
                    st.session_state.trigger_search = True
                    st.rerun()

        with st.expander("Key Formulas", expanded=False):
            st.markdown("""
**Goodwill:**
```
Purchase Price - Fair Value of Net Assets
```

**NCI (Full Goodwill):**
```
NCI% × (Subsidiary Equity + Full Goodwill)
```

**NCI (Partial Goodwill):**
```
NCI% × Subsidiary Equity at Fair Value
```

**Equity Pickup:**
```
Ownership% × Associate Net Income
```

**Indirect Holding:**
```
Parent% in Sub A × Sub A% in Sub B
```

**Translation Adjustment:**
```
Closing Rate Assets - Historical Rate Equity
```
            """)

        st.markdown("")  # Spacing

        # Quiz Mode - RAG-generated questions with Adaptive Difficulty
        st.markdown("### Quiz Mode")
        st.caption("Adaptive AI-generated questions from knowledge base")

        # Initialize quiz state
        if "quiz_active" not in st.session_state:
            st.session_state.quiz_active = False
        if "quiz_index" not in st.session_state:
            st.session_state.quiz_index = 0
        if "quiz_score" not in st.session_state:
            st.session_state.quiz_score = 0
        if "quiz_answered" not in st.session_state:
            st.session_state.quiz_answered = False
        if "quiz_questions" not in st.session_state:
            st.session_state.quiz_questions = []
        if "quiz_generating" not in st.session_state:
            st.session_state.quiz_generating = False
        if "quiz_difficulty" not in st.session_state:
            st.session_state.quiz_difficulty = "medium"
        if "quiz_performance_loaded" not in st.session_state:
            st.session_state.quiz_performance_loaded = False

        # JavaScript to load quiz performance and determine adaptive difficulty
        if not st.session_state.quiz_performance_loaded:
            load_perf_js = """
            <script>
            (function() {
                const perf = JSON.parse(localStorage.getItem('fc_quiz_performance') || '{"totalQuestions":0,"totalCorrect":0,"history":[]}');
                let difficulty = 'medium';
                if (perf.totalQuestions >= 5) {
                    const accuracy = perf.totalCorrect / perf.totalQuestions;
                    if (accuracy >= 0.8) difficulty = 'hard';
                    else if (accuracy <= 0.4) difficulty = 'easy';
                }
                // Store in sessionStorage for Python to read via URL params workaround
                sessionStorage.setItem('fc_quiz_difficulty', difficulty);
                // Also dispatch event
                window.parent.postMessage({type: 'quizDifficulty', difficulty: difficulty}, '*');
            })();
            </script>
            """
            st.components.v1.html(load_perf_js, height=0)
            st.session_state.quiz_performance_loaded = True

        # Difficulty badge colors
        difficulty_colors = {
            "easy": ("#2EA043", "Easy"),
            "medium": ("#F0883E", "Medium"),
            "hard": ("#DB6D6D", "Hard")
        }

        if not st.session_state.quiz_active:
            # Show current difficulty level based on performance (styled like buttons)
            diff_color, diff_label = difficulty_colors.get(st.session_state.quiz_difficulty, difficulty_colors["medium"])
            st.markdown(f"""
            <div style="text-align: center; margin-bottom: 10px;">
                <span style="background-color: transparent; color: inherit; padding: 8px 16px; border-radius: 4px; font-size: 14px; font-weight: 400; border: 1px solid #30363D; display: inline-block;">
                    Adaptive Difficulty: <strong style="color: {diff_color};">{diff_label}</strong>
                </span>
            </div>
            """, unsafe_allow_html=True)

            # Allow manual difficulty override (horizontal row)
            st.caption("Select difficulty:")
            diff_col1, diff_col2, diff_col3 = st.columns(3)
            with diff_col1:
                if st.button("Easy", key="set_easy", use_container_width=True):
                    st.session_state.quiz_difficulty = "easy"
                    st.rerun()
            with diff_col2:
                if st.button("Medium", key="set_medium", use_container_width=True):
                    st.session_state.quiz_difficulty = "medium"
                    st.rerun()
            with diff_col3:
                if st.button("Hard", key="set_hard", use_container_width=True):
                    st.session_state.quiz_difficulty = "hard"
                    st.rerun()

            if st.button("Start Adaptive Quiz (5 Questions)", key="start_quiz", use_container_width=True, type="primary"):
                st.session_state.quiz_generating = True
                st.session_state.quiz_active = True
                st.session_state.quiz_index = 0
                st.session_state.quiz_score = 0
                st.session_state.quiz_answered = False
                st.rerun()
        else:
            # Generate questions if needed with adaptive difficulty
            if st.session_state.quiz_generating or not st.session_state.quiz_questions:
                difficulty = st.session_state.quiz_difficulty
                with st.spinner(f"Generating {difficulty.upper()} difficulty questions..."):
                    rag_questions = generate_quiz_questions_rag(count=5, difficulty=difficulty)
                    if rag_questions:
                        # Add difficulty to each question
                        for q in rag_questions:
                            q['difficulty'] = difficulty
                        st.session_state.quiz_questions = rag_questions
                    else:
                        # Fallback to hardcoded questions with difficulty
                        st.session_state.quiz_questions = [
                            {"q": "What ownership % triggers global integration?", "options": ["10-20%", "20-50%", ">50%", "<20%"], "answer": 2, "explanation": "Control (>50%) requires global integration.", "difficulty": difficulty},
                            {"q": "Which IFRS standard covers consolidation?", "options": ["IFRS 3", "IFRS 10", "IAS 21", "IAS 28"], "answer": 1, "explanation": "IFRS 10 covers consolidated financial statements.", "difficulty": difficulty},
                            {"q": "What is the equity method threshold?", "options": ["0-20%", "20-50%", "50-100%", ">90%"], "answer": 1, "explanation": "20-50% ownership indicates significant influence.", "difficulty": difficulty},
                            {"q": "Where do translation adjustments appear?", "options": ["Income Statement", "OCI/Equity", "Cash Flow", "Notes"], "answer": 1, "explanation": "CTA goes to Other Comprehensive Income.", "difficulty": difficulty},
                            {"q": "Goodwill = Purchase Price minus...", "options": ["Book Value", "Fair Value of Net Assets", "Revenue", "EBITDA"], "answer": 1, "explanation": "Goodwill = Price - Fair Value of Identifiable Net Assets.", "difficulty": difficulty},
                        ]
                    st.session_state.quiz_generating = False
                    st.rerun()

            quiz_questions = st.session_state.quiz_questions
            current_difficulty = st.session_state.quiz_difficulty
            diff_color, diff_label = difficulty_colors.get(current_difficulty, difficulty_colors["medium"])

            # Show difficulty badge at top (styled like buttons)
            st.markdown(f"""
            <div style="text-align: center; margin-bottom: 10px;">
                <span style="background-color: transparent; color: inherit; padding: 8px 16px; border-radius: 4px; font-size: 14px; font-weight: 400; border: 1px solid #30363D; display: inline-block;">
                    <strong style="color: {diff_color};">{diff_label}</strong> Mode
                </span>
            </div>
            """, unsafe_allow_html=True)

            # Show current question
            if st.session_state.quiz_index < len(quiz_questions):
                q = quiz_questions[st.session_state.quiz_index]
                st.markdown(f"**Q{st.session_state.quiz_index + 1}/{len(quiz_questions)}:** {q['q']}")

                for i, opt in enumerate(q["options"]):
                    btn_key = f"quiz_opt_{st.session_state.quiz_index}_{i}"
                    if st.button(opt, key=btn_key, use_container_width=True, disabled=st.session_state.quiz_answered):
                        if i == q["answer"]:
                            st.session_state.quiz_score += 1
                            st.success("Correct!")
                        else:
                            st.error(f"Wrong. Answer: {q['options'][q['answer']]}")
                        # Show explanation if available
                        if q.get("explanation"):
                            st.info(f"Explanation: {q['explanation']}")
                        st.session_state.quiz_answered = True

                if st.session_state.quiz_answered:
                    if st.button("Next Question" if st.session_state.quiz_index < len(quiz_questions) - 1 else "See Results", key="quiz_next"):
                        st.session_state.quiz_index += 1
                        st.session_state.quiz_answered = False
                        st.rerun()
            else:
                # Show results
                score = st.session_state.quiz_score
                total = len(quiz_questions)
                percentage = int(score/total*100)
                st.markdown(f"**Score: {score}/{total} ({percentage}%)**")

                if score == total:
                    st.success("Perfect! You're a consolidation expert!")
                elif score >= total * 0.6:
                    st.info("Good job! Keep learning.")
                else:
                    st.warning("Review the learning paths to improve.")

                # Save quiz results to localStorage for adaptive difficulty
                save_results_js = f"""
                <script>
                (function() {{
                    const score = {score};
                    const total = {total};
                    const topic = '{current_difficulty}';

                    // Get existing performance
                    let perf = JSON.parse(localStorage.getItem('fc_quiz_performance') || '{{"totalQuestions":0,"totalCorrect":0,"history":[]}}');

                    // Update totals
                    perf.totalQuestions += total;
                    perf.totalCorrect += score;

                    // Add to history (keep last 10)
                    perf.history.unshift({{
                        score: score,
                        total: total,
                        difficulty: topic,
                        timestamp: new Date().toISOString()
                    }});
                    if (perf.history.length > 10) perf.history = perf.history.slice(0, 10);

                    // Save back
                    localStorage.setItem('fc_quiz_performance', JSON.stringify(perf));

                    // Calculate new difficulty
                    const accuracy = perf.totalCorrect / perf.totalQuestions;
                    let newDifficulty = 'medium';
                    if (accuracy >= 0.8) newDifficulty = 'hard';
                    else if (accuracy <= 0.4) newDifficulty = 'easy';

                    // Show notification
                    console.log('Quiz results saved. Accuracy: ' + (accuracy * 100).toFixed(1) + '%, Next difficulty: ' + newDifficulty);
                }})();
                </script>
                """
                st.components.v1.html(save_results_js, height=0)

                # Show performance stats
                st.markdown("---")
                st.caption("Your quiz performance is tracked for adaptive difficulty")

                if st.button("New Quiz (Regenerate)", key="restart_quiz", use_container_width=True):
                    st.session_state.quiz_active = False
                    st.session_state.quiz_index = 0
                    st.session_state.quiz_questions = []  # Clear to regenerate
                    st.session_state.quiz_score = 0
                    st.session_state.quiz_answered = False
                    st.session_state.quiz_performance_loaded = False  # Reload performance
                    st.rerun()

        st.markdown("")  # Spacing

        # Case Studies - Real-world scenarios
        st.markdown("### Case Studies")
        st.caption("Practice with real-world scenarios")

        # Initialize case study state
        if "active_case_study" not in st.session_state:
            st.session_state.active_case_study = None

        for case_id, case_data in case_studies.items():
            with st.expander(f"{case_data['title']}", expanded=False):
                st.caption(case_data['subtitle'])
                st.markdown(case_data['description'])

                if st.button("Start This Case", key=f"case_{case_id}", use_container_width=True):
                    st.session_state.active_case_study = case_id
                    # Set the first question from the case study
                    st.session_state.query = case_data['questions'][0]
                    st.session_state.trigger_search = True
                    st.rerun()

        # Show active case study details in main area via session state
        if st.session_state.active_case_study:
            active_case = case_studies.get(st.session_state.active_case_study)
            if active_case:
                st.info(f"Active: {active_case['title']}")
                if st.button("Exit Case Study", use_container_width=True):
                    st.session_state.active_case_study = None
                    st.rerun()

        st.markdown("")  # Spacing

        # Concept Map - Interactive knowledge graph
        st.markdown("### Concept Map")
        st.caption("Visual knowledge graph - click to explore")

        # Initialize concept map state
        if "show_concept_map" not in st.session_state:
            st.session_state.show_concept_map = False

        if st.button("Open Concept Map", key="toggle_concept_map", use_container_width=True, type="primary"):
            st.session_state.show_concept_map = True
            st.rerun()

        st.markdown("")  # Spacing

        # Bookmarks Section
        st.markdown("### Bookmarks")
        st.caption("Saved answers for quick reference")

        # Initialize bookmarks in session state
        if "bookmarks" not in st.session_state:
            st.session_state.bookmarks = []

        if st.session_state.bookmarks:
            for idx, bookmark in enumerate(st.session_state.bookmarks[:5]):  # Show max 5
                with st.expander(f"{bookmark['question'][:40]}...", expanded=False):
                    st.markdown(bookmark['answer'][:300] + "..." if len(bookmark['answer']) > 300 else bookmark['answer'])
                    st.caption(f"Saved: {bookmark.get('timestamp', 'N/A')}")
                    col_load, col_remove = st.columns(2)
                    with col_load:
                        if st.button("Load", key=f"load_bm_{idx}", use_container_width=True):
                            st.session_state.query = bookmark['question']
                            st.session_state.trigger_search = True
                            st.rerun()
                    with col_remove:
                        if st.button("Remove", key=f"rm_bm_{idx}", use_container_width=True):
                            st.session_state.bookmarks = [b for b in st.session_state.bookmarks if b['question'] != bookmark['question']]
                            # Also remove from localStorage
                            st.components.v1.html(f"<script>if(window.fcBookmarks) window.fcBookmarks.remove({bookmark.get('id', 0)});</script>", height=0)
                            st.rerun()

            if len(st.session_state.bookmarks) > 5:
                st.caption(f"+{len(st.session_state.bookmarks) - 5} more bookmarks")

            if st.button("Clear All Bookmarks", key="clear_bookmarks", use_container_width=True):
                st.session_state.bookmarks = []
                st.components.v1.html("<script>if(window.fcBookmarks) window.fcBookmarks.clear();</script>", height=0)
                st.rerun()
        else:
            st.caption("No bookmarks yet. Click 'Bookmark' on any answer to save it.")

        st.markdown("")  # Spacing

        # Session Summary / Study Notes
        if st.session_state.conversation_history:
            st.markdown("### Session Summary")
            st.caption(f"{len(st.session_state.conversation_history)} Q&A in session")

            # Generate session summary
            session_date = datetime.now().strftime("%Y-%m-%d")
            session_time = datetime.now().strftime("%H:%M")

            summary_content = f"""# FC Education Session Notes
**Date:** {session_date}
**Time:** {session_time}
**Questions Asked:** {len(st.session_state.conversation_history)}

---

"""
            for i, exchange in enumerate(st.session_state.conversation_history, 1):
                summary_content += f"""## Q{i}: {exchange['question']}

**Level:** {exchange.get('explanation_level', 'Standard')}
**Sources:** {exchange.get('sources_count', 'N/A')}

{exchange['answer']}

---

"""
            summary_content += f"""
## Session Statistics

- Total Questions: {len(st.session_state.conversation_history)}
- Topics Covered: {', '.join(set(e.get('topic_filter', 'All') for e in st.session_state.conversation_history))}

---

*Generated by FC Education Portal v3.0*
"""
            col_sum1, col_sum2 = st.columns(2)
            with col_sum1:
                st.download_button(
                    label="Export Notes",
                    data=summary_content,
                    file_name=f"FC_StudyNotes_{session_date}.md",
                    mime="text/markdown",
                    use_container_width=True,
                )
            with col_sum2:
                if st.button("Clear Session", use_container_width=True, type="primary"):
                    st.session_state.conversation_history = []
                    st.session_state.query = ""
                    st.rerun()

        st.markdown("")  # Spacing

        # About section - condensed
        st.markdown("### About")
        st.caption("""
        AI-powered education portal for financial consolidation.
        Powered by Claude 3.5 Sonnet + ChromaDB.
        """)

        st.caption("Version 3.0 | Education Portal")

    # Header
    st.title("Financial Consolidation Knowledge Base")

    # Show Concept Map modal if activated
    if st.session_state.get("show_concept_map"):
        st.markdown("## Concept Map - Financial Consolidation Knowledge Graph")
        st.caption("Click any node to search for that concept. Drag to pan, scroll to zoom.")

        # Close button
        if st.button("Close Concept Map", key="close_concept_map"):
            st.session_state.show_concept_map = False
            st.rerun()
            return  # Ensure clean exit

        # Bidirectional concept map component - sends clicked query back to Python
        selected_query = concept_map(key="concept_map_component")

        # Handle query selection from concept map
        if selected_query:
            st.session_state.query = selected_query
            st.session_state.show_concept_map = False
            st.session_state.trigger_search = True
            st.rerun()
            return  # Ensure clean exit

        # Quick search buttons organized by category
        st.markdown("#### Quick Search by Category")

        tab_methods, tab_standards, tab_calc, tab_elim, tab_currency = st.tabs(
            ["Methods", "Standards", "Calculations", "Eliminations", "Currency"]
        )

        with tab_methods:
            method_cols = st.columns(4)
            method_queries = [
                ("Consolidation", "What is financial consolidation?"),
                ("Global Integration", "How does global integration consolidation work?"),
                ("Equity Method", "How does equity method consolidation work?"),
                ("Proportional", "How does proportional consolidation work?"),
            ]
            for idx, (label, q) in enumerate(method_queries):
                with method_cols[idx]:
                    if st.button(label, key=f"cm_method_{idx}", use_container_width=True):
                        st.session_state.query = q
                        st.session_state.show_concept_map = False
                        st.session_state.trigger_search = True
                        st.rerun()

        with tab_standards:
            std_cols = st.columns(5)
            std_queries = [
                ("IFRS 10", "What does IFRS 10 say about control?"),
                ("IFRS 3", "What does IFRS 3 cover for business combinations?"),
                ("IFRS 11", "What does IFRS 11 say about joint arrangements?"),
                ("IAS 28", "What does IAS 28 say about associates?"),
                ("IAS 21", "What does IAS 21 say about currency translation?"),
            ]
            for idx, (label, q) in enumerate(std_queries):
                with std_cols[idx]:
                    if st.button(label, key=f"cm_std_{idx}", use_container_width=True):
                        st.session_state.query = q
                        st.session_state.show_concept_map = False
                        st.session_state.trigger_search = True
                        st.rerun()

        with tab_calc:
            calc_cols = st.columns(4)
            calc_queries = [
                ("Goodwill", "How is goodwill calculated in consolidation?"),
                ("NCI", "How is minority interest (NCI) calculated?"),
                ("Ownership %", "How are direct and indirect ownership percentages calculated?"),
                ("Equity Pickup", "How is equity method pickup calculated?"),
            ]
            for idx, (label, q) in enumerate(calc_queries):
                with calc_cols[idx]:
                    if st.button(label, key=f"cm_calc_{idx}", use_container_width=True):
                        st.session_state.query = q
                        st.session_state.show_concept_map = False
                        st.session_state.trigger_search = True
                        st.rerun()

        with tab_elim:
            elim_cols = st.columns(4)
            elim_queries = [
                ("Intercompany", "What are intercompany eliminations?"),
                ("Participation", "How do participation eliminations work?"),
                ("Dividends", "How are dividends eliminated in consolidation?"),
                ("Unrealized Profit", "How is unrealized profit in inventory eliminated?"),
            ]
            for idx, (label, q) in enumerate(elim_queries):
                with elim_cols[idx]:
                    if st.button(label, key=f"cm_elim_{idx}", use_container_width=True):
                        st.session_state.query = q
                        st.session_state.show_concept_map = False
                        st.session_state.trigger_search = True
                        st.rerun()

        with tab_currency:
            curr_cols = st.columns(3)
            curr_queries = [
                ("Translation", "How does currency translation work?"),
                ("CTA", "What is cumulative translation adjustment (CTA)?"),
                ("Exchange Rates", "What exchange rates are used for translation?"),
            ]
            for idx, (label, q) in enumerate(curr_queries):
                with curr_cols[idx]:
                    if st.button(label, key=f"cm_curr_{idx}", use_container_width=True):
                        st.session_state.query = q
                        st.session_state.show_concept_map = False
                        st.session_state.trigger_search = True
                        st.rerun()

        st.markdown("---")
        # Don't render the search interface when concept map is shown - prevents duplication
        return

    # Show active case study scenario in main area
    if st.session_state.get("active_case_study"):
        active_case = case_studies.get(st.session_state.active_case_study)
        if active_case:
            with st.container():
                st.markdown(f"### Case Study: {active_case['title']}")
                st.markdown(active_case['scenario'])

                # Show case study questions as buttons
                st.markdown("**Explore this case:**")
                case_q_cols = st.columns(len(active_case['questions']))
                for idx, case_q in enumerate(active_case['questions']):
                    with case_q_cols[idx]:
                        q_label = case_q[:35] + "..." if len(case_q) > 35 else case_q
                        if st.button(q_label, key=f"case_q_{idx}", use_container_width=True, help=case_q):
                            st.session_state.query = case_q
                            st.session_state.trigger_search = True
                            st.rerun()

                st.markdown("---")

    # Example Questions - randomly select 8 from pool of 128 business questions
    st.markdown("**Try these questions:**")

    all_example_questions = [
        # === CONSOLIDATION METHODS (16 questions) ===
        ("Equity Method", "How does equity method consolidation work?"),
        ("Global Integration", "What is global integration and when is it used?"),
        ("Proportional Method", "How does proportional consolidation work?"),
        ("Cost Method", "When should the cost method be applied?"),
        ("Consolidation Methods", "What are the different consolidation methods?"),
        ("Method Selection", "How do you determine which consolidation method to use?"),
        ("Full Consolidation", "What does full consolidation mean?"),
        ("Line-by-Line", "What is line-by-line consolidation?"),
        ("One-Line Consolidation", "What is one-line consolidation in equity method?"),
        ("Method Thresholds", "What ownership thresholds determine consolidation method?"),
        ("Significant Influence", "What is significant influence in consolidation?"),
        ("Joint Control", "What is joint control and how does it affect consolidation?"),
        ("Control Definition", "How is control defined for consolidation purposes?"),
        ("De Facto Control", "What is de facto control in consolidation?"),
        ("Potential Voting Rights", "How do potential voting rights affect control?"),
        ("Structured Entities", "How are structured entities consolidated?"),

        # === IFRS/IAS STANDARDS (16 questions) ===
        ("IFRS 10 Control", "What defines control under IFRS 10?"),
        ("IFRS 3 Overview", "What does IFRS 3 cover for business combinations?"),
        ("IFRS 11 Joint Arrangements", "What is the difference between joint operations and joint ventures under IFRS 11?"),
        ("IAS 28 Associates", "How does IAS 28 apply to investments in associates?"),
        ("IAS 21 Currency", "What are the key requirements of IAS 21 for currency translation?"),
        ("IAS 27 Separate", "What does IAS 27 require for separate financial statements?"),
        ("IAS 36 Impairment", "How does IAS 36 impairment testing apply to goodwill?"),
        ("IFRS 10 vs IAS 27", "What is the difference between IFRS 10 and IAS 27?"),
        ("IFRS 3 vs IFRS 10", "How do IFRS 3 and IFRS 10 work together?"),
        ("Fair Value IFRS 13", "How is fair value determined under IFRS 13 for acquisitions?"),
        ("Disclosure Requirements", "What are the key disclosure requirements for consolidated statements?"),
        ("First-Time Adoption", "What are the considerations for first-time IFRS adoption in consolidation?"),
        ("Control Assessment", "How do you assess control under IFRS 10?"),
        ("Principal vs Agent", "What is the principal versus agent assessment in IFRS 10?"),
        ("Investment Entities", "What are the special rules for investment entities?"),
        ("Held for Sale", "How are subsidiaries held for sale treated?"),

        # === GOODWILL & PURCHASE ACCOUNTING (16 questions) ===
        ("Goodwill Calculation", "How is goodwill calculated in a business combination?"),
        ("Negative Goodwill", "What is negative goodwill and how is it treated?"),
        ("Goodwill Impairment", "How is goodwill tested for impairment?"),
        ("Bargain Purchase", "What is a bargain purchase in consolidation?"),
        ("Purchase Price Allocation", "What is purchase price allocation?"),
        ("Fair Value Adjustments", "How are fair value adjustments made at acquisition?"),
        ("Identifiable Assets", "What are identifiable net assets in an acquisition?"),
        ("Contingent Consideration", "How is contingent consideration treated in acquisitions?"),
        ("Acquisition Costs", "How are acquisition-related costs treated?"),
        ("Measurement Period", "What is the measurement period for business combinations?"),
        ("Goodwill by Subsidiary", "How is goodwill tracked by subsidiary?"),
        ("Goodwill Amortization", "Is goodwill amortized under IFRS?"),
        ("Acquisition Date", "How is the acquisition date determined?"),
        ("Step Acquisition Goodwill", "How is goodwill calculated in a step acquisition?"),
        ("Full vs Partial Goodwill", "What is the difference between full and partial goodwill methods?"),
        ("Goodwill Allocation", "How is goodwill allocated to cash-generating units?"),

        # === NON-CONTROLLING INTEREST (16 questions) ===
        ("NCI Definition", "What is non-controlling interest?"),
        ("NCI Calculation", "How is non-controlling interest calculated?"),
        ("NCI Presentation", "How is NCI presented in consolidated statements?"),
        ("NCI in Losses", "How are losses allocated to non-controlling interests?"),
        ("NCI Measurement", "What are the options for measuring NCI at acquisition?"),
        ("Minority Interest", "What is minority interest in consolidation?"),
        ("NCI Changes", "How do changes in ownership affect NCI?"),
        ("NCI Dividends", "How are dividends to NCI shareholders treated?"),
        ("NCI in Equity", "Where does NCI appear in consolidated equity?"),
        ("Negative NCI", "Can NCI have a negative balance?"),
        ("NCI Transactions", "How are transactions with NCI shareholders recorded?"),
        ("NCI Put Options", "How do put options over NCI shares affect consolidation?"),
        ("NCI Share of Reserves", "How is NCI's share of reserves calculated?"),
        ("NCI at Disposal", "How is NCI treated when a subsidiary is disposed?"),
        ("Direct vs Indirect NCI", "What is the difference between direct and indirect NCI?"),
        ("NCI Profit Attribution", "How is profit attributed to non-controlling interests?"),

        # === ELIMINATIONS (16 questions) ===
        ("Intercompany Eliminations", "What are intercompany eliminations?"),
        ("Investment Elimination", "How does investment elimination work?"),
        ("Dividend Elimination", "How are intercompany dividends eliminated?"),
        ("Intercompany Sales", "How are intercompany sales eliminated?"),
        ("Unrealized Profit", "How is unrealized profit on intercompany transactions eliminated?"),
        ("Upstream vs Downstream", "What is the difference between upstream and downstream transactions?"),
        ("Intercompany Loans", "How are intercompany loans eliminated?"),
        ("Intercompany Interest", "How is intercompany interest eliminated?"),
        ("Inventory Elimination", "How are intercompany profits in inventory eliminated?"),
        ("Fixed Asset Elimination", "How are intercompany profits in fixed assets eliminated?"),
        ("Service Eliminations", "How are intercompany service charges eliminated?"),
        ("Management Fees", "How are intercompany management fees eliminated?"),
        ("Royalty Eliminations", "How are intercompany royalties eliminated?"),
        ("Elimination Timing", "When should eliminations be recorded?"),
        ("Partial Elimination", "When is partial elimination of unrealized profit required?"),
        ("Elimination Reversal", "When are elimination entries reversed?"),

        # === CURRENCY TRANSLATION (16 questions) ===
        ("Currency Translation", "How does currency translation work in consolidation?"),
        ("Functional Currency", "What is functional currency?"),
        ("Presentation Currency", "What is presentation currency?"),
        ("Translation Method", "What translation method is used under IAS 21?"),
        ("Translation Differences", "What are currency translation differences?"),
        ("CTA Reserve", "What is the cumulative translation adjustment reserve?"),
        ("Exchange Rates", "Which exchange rates are used for translation?"),
        ("Monetary vs Non-Monetary", "What is the monetary/non-monetary method?"),
        ("Temporal Method", "What is the temporal method of translation?"),
        ("Current Rate Method", "What is the current rate method?"),
        ("Hyperinflation", "How does hyperinflation affect currency translation?"),
        ("Foreign Operations", "How are foreign operations translated?"),
        ("Net Investment Hedge", "What is a net investment hedge?"),
        ("Translation of Goodwill", "How is goodwill translated in foreign subsidiaries?"),
        ("Intercompany Foreign Currency", "How are intercompany balances in foreign currency treated?"),
        ("Exchange Differences P&L", "When do exchange differences go to profit or loss?"),

        # === OWNERSHIP & GROUP STRUCTURE (16 questions) ===
        ("Direct Ownership", "What is direct ownership in a group structure?"),
        ("Indirect Ownership", "How is indirect ownership calculated?"),
        ("Effective Ownership", "What is effective ownership percentage?"),
        ("Ownership Changes", "How do ownership changes affect consolidation?"),
        ("Control vs Ownership", "What is the difference between control and ownership?"),
        ("Parent Company", "What defines a parent company?"),
        ("Ultimate Parent", "What is the ultimate parent in a group?"),
        ("Intermediate Holdings", "How are intermediate holding companies treated?"),
        ("Cross Holdings", "How are cross holdings between subsidiaries handled?"),
        ("Circular Ownership", "What are the issues with circular ownership structures?"),
        ("Tiered Structures", "How do multi-tiered group structures affect consolidation?"),
        ("Acquisition of Control", "What happens when control is acquired?"),
        ("Loss of Control", "What happens when control is lost?"),
        ("Retained Interest", "How is a retained interest measured after losing control?"),
        ("Subsidiary Definition", "What defines a subsidiary for consolidation?"),
        ("Associate Definition", "What defines an associate company?"),

        # === BUSINESS COMBINATIONS & ACQUISITIONS (16 questions) ===
        ("Business Combination", "What is a business combination?"),
        ("Acquisition Method", "What is the acquisition method of accounting?"),
        ("Step Acquisition", "What is a step acquisition?"),
        ("Partial Acquisition", "How is a partial acquisition accounted for?"),
        ("Business vs Assets", "How do you distinguish a business from an asset acquisition?"),
        ("Common Control", "What are business combinations under common control?"),
        ("Reverse Acquisition", "What is a reverse acquisition?"),
        ("Acquisition Date Fair Value", "How are assets measured at acquisition date?"),
        ("Intangible Assets Acquired", "How are acquired intangible assets recognized?"),
        ("Contingent Liabilities", "How are contingent liabilities treated in acquisitions?"),
        ("Pre-existing Relationships", "How are pre-existing relationships treated in acquisitions?"),
        ("Reacquired Rights", "What are reacquired rights in a business combination?"),
        ("Share-Based Payments", "How are share-based payments treated in acquisitions?"),
        ("Deferred Tax Acquisition", "How is deferred tax recognized in acquisitions?"),
        ("Successive Acquisitions", "How are successive share purchases accounted for?"),
        ("Put Option Acquisition", "How do put options affect acquisition accounting?"),
    ]

    # Randomly select 8 questions (truly random on each refresh)
    example_questions = random.sample(all_example_questions, 8)

    # Create 2 rows of 4 buttons each
    for row in range(0, len(example_questions), 4):
        cols = st.columns(4)
        for idx, col in enumerate(cols):
            if row + idx < len(example_questions):
                label, question = example_questions[row + idx]
                with col:
                    if st.button(label, key=f"ex_{row}_{idx}", use_container_width=True):
                        st.session_state.query = question
                        st.session_state.trigger_search = True
                        st.rerun()

    st.markdown("")  # Light spacing

    # Search Options Row
    col_level, col_topic = st.columns(2)

    with col_level:
        # Explanation Level Toggle
        st.markdown("**Explanation Level:**")
        # Check if "Go Deeper" was clicked - override to Detailed
        if st.session_state.force_detailed:
            st.session_state.explanation_level = "Detailed"
            st.session_state.force_detailed = False

        level_options = ["Executive Summary", "Standard", "Detailed"]
        current_level_index = level_options.index(st.session_state.explanation_level) if st.session_state.explanation_level in level_options else 0
        explanation_level = st.radio(
            "Select detail level",
            level_options,
            index=current_level_index,
            horizontal=True,
            help="Executive Summary: Brief overview for managers | Standard: Balanced explanation | Detailed: Comprehensive with all edge cases",
            label_visibility="collapsed",
        )
        # Update session state if changed
        if explanation_level != st.session_state.explanation_level:
            st.session_state.explanation_level = explanation_level

    with col_topic:
        # Topic Filter Dropdown
        st.markdown("**Filter by Topic:**")
        topic_options = {
            "All Topics": "all",
            "Financial Consolidation Theory": "theory",
            "Consolidation Methods": "consolidation-methods",
            "Calculations": "calculations",
            "Eliminations": "eliminations",
            "Currency Translation": "currency",
            "Ownership Structure": "ownership",
            "User Help & Guides": "help",
            "Troubleshooting": "troubleshooting",
            "Reference & Glossary": "reference",
        }
        topic_keys = list(topic_options.keys())
        current_topic_index = topic_keys.index(st.session_state.selected_topic) if st.session_state.selected_topic in topic_keys else 0
        selected_topic_label = st.selectbox(
            "Select topic",
            options=topic_keys,
            index=current_topic_index,
            help="Filter results to a specific topic area",
            label_visibility="collapsed",
        )
        # Update session state if changed
        if selected_topic_label != st.session_state.selected_topic:
            st.session_state.selected_topic = selected_topic_label
        topic_filter = topic_options[selected_topic_label]

    # Model tier selector (same style as Explanation Level)
    st.markdown("**Choose AI Model:**")
    model_options = list(MODEL_TIERS.keys())
    current_model_index = model_options.index(st.session_state.model_tier) if st.session_state.model_tier in model_options else 0
    selected_model_name = st.radio(
        "Select AI model",
        model_options,
        index=current_model_index,
        horizontal=True,
        help="Haiku 4.5: Fast responses | Sonnet 4: Balanced | Sonnet 4.5: Best quality",
        label_visibility="collapsed",
    )
    # Update session state if changed
    if selected_model_name != st.session_state.model_tier:
        st.session_state.model_tier = selected_model_name

    st.markdown("")  # Spacing

    # Main query input with keyboard hint
    # Sync query_input with query if trigger_search is set (from concept map or other sources)
    if st.session_state.get("trigger_search") and st.session_state.get("query"):
        st.session_state.query_input = st.session_state.query
    elif "query_input" not in st.session_state:
        st.session_state.query_input = st.session_state.get("query", "")

    col_input, col_hint = st.columns([5, 1])
    with col_input:
        query = st.text_input(
            "Ask your question:",
            placeholder="e.g., How does the equity method work?",
            key="query_input",
        )
    with col_hint:
        st.markdown("")  # Spacing
        st.markdown('<span class="kbd">Ctrl+K</span> <span style="color: #8B949E; font-size: 12px;">to focus</span>', unsafe_allow_html=True)

    # Autocomplete suggestions - show when user types 2+ characters
    if query and len(query) >= 2:
        query_lower = query.lower()
        # Combine common questions with search history for suggestions
        all_suggestions = common_questions + st.session_state.search_history
        # Filter suggestions that contain the query text
        matching = [q for q in all_suggestions if query_lower in q.lower() and q.lower() != query_lower]
        # Remove duplicates while preserving order
        seen = set()
        unique_matching = []
        for q in matching:
            if q.lower() not in seen:
                seen.add(q.lower())
                unique_matching.append(q)
        # Show top 5 suggestions
        if unique_matching[:5]:
            st.caption("Suggestions:")
            suggestion_cols = st.columns(min(len(unique_matching[:5]), 3))
            for idx, suggestion in enumerate(unique_matching[:5]):
                col_idx = idx % 3
                with suggestion_cols[col_idx]:
                    # Truncate long suggestions
                    display_text = suggestion[:40] + "..." if len(suggestion) > 40 else suggestion
                    if st.button(display_text, key=f"suggest_{idx}", use_container_width=True, help=suggestion):
                        st.session_state.query = suggestion
                        st.session_state.trigger_search = True
                        st.rerun()

    # Recent Searches dropdown (populated from session state which syncs with localStorage)
    if st.session_state.search_history:
        with st.expander(f"Recent Searches ({len(st.session_state.search_history)})", expanded=False):
            cols = st.columns([4, 1])
            with cols[1]:
                if st.button("Clear", key="clear_history", use_container_width=True):
                    st.session_state.search_history = []
                    # Also clear localStorage via JS
                    st.components.v1.html("<script>if(window.fcSearchHistory) window.fcSearchHistory.clear();</script>", height=0)
                    st.rerun()
            for i, hist_query in enumerate(st.session_state.search_history[:10]):
                if st.button(f"{hist_query[:60]}{'...' if len(hist_query) > 60 else ''}", key=f"hist_{i}", use_container_width=True):
                    st.session_state.query = hist_query
                    st.session_state.trigger_search = True
                    st.rerun()

    # Search and Clear buttons
    col1, col2, col3 = st.columns([1, 1, 3])
    with col1:
        search_button = st.button("Search", type="primary", use_container_width=True)
    with col2:
        if st.button("Clear Input", use_container_width=True):
            st.session_state.query = ""
            st.session_state.trigger_search = False
            st.rerun()
    with col3:
        shortcuts_hint = '<span style="color: #8B949E; font-size: 12px;"><span class="kbd">Enter</span> search | <span class="kbd">Esc</span> blur</span>'
        if st.session_state.conversation_history:
            history_count = len(st.session_state.conversation_history)
            st.markdown(f'{history_count} question{"s" if history_count != 1 else ""} in conversation &nbsp;&nbsp; {shortcuts_hint}', unsafe_allow_html=True)
        else:
            st.markdown(shortcuts_hint, unsafe_allow_html=True)

    # Check if search was triggered by example button or related topic
    trigger_search = st.session_state.get("trigger_search", False)
    if trigger_search:
        st.session_state.trigger_search = False
        search_button = True  # Simulate button press
        # Use the query from session state (set by button click) if different from text input
        if st.session_state.get("query") and st.session_state.get("query") != query:
            query = st.session_state.query

    # Process query
    if search_button and query:
        # Input validation - limit query length to prevent abuse
        MAX_QUERY_LENGTH = 500
        if len(query) > MAX_QUERY_LENGTH:
            st.warning(f"Query too long ({len(query)} chars). Please limit to {MAX_QUERY_LENGTH} characters.")
            query = query[:MAX_QUERY_LENGTH]

        # Sanitize query - strip excessive whitespace
        query = " ".join(query.split())

        # Save to search history (both session state and localStorage)
        if query not in st.session_state.search_history:
            st.session_state.search_history.insert(0, query)
            st.session_state.search_history = st.session_state.search_history[:10]  # Keep max 10
        else:
            # Move to top if already exists
            st.session_state.search_history.remove(query)
            st.session_state.search_history.insert(0, query)

        # Save to localStorage via JS
        escaped_query = html.escape(query).replace("'", "\\'")
        st.components.v1.html(f"<script>if(window.fcSearchHistory) window.fcSearchHistory.save('{escaped_query}');</script>", height=0)

        # Show active filters
        if topic_filter != "all":
            st.info(f"Filtering by: **{selected_topic_label}**")

        # Progress indicator container
        progress_container = st.container()

        with progress_container:
            # Step 1: Searching
            step1_placeholder = st.empty()
            step1_placeholder.markdown("""
            <div class="progress-step active">
                <div class="step-indicator">1</div>
                <span>Searching knowledge base...</span>
            </div>
            """, unsafe_allow_html=True)

            # Search for relevant context with topic filter
            results = search_business_layer(query, topic_filter=topic_filter)

            if not results:
                step1_placeholder.empty()
                if topic_filter != "all":
                    st.warning(f"No results found for '{query}' in {selected_topic_label}. Try 'All Topics' for broader search.")
                else:
                    st.warning("No relevant information found in the knowledge base.")
                return

            # Mark step 1 complete, show step 2
            step1_placeholder.markdown(f"""
            <div class="progress-step complete">
                <div class="step-indicator complete"></div>
                <span>Found {len(results)} relevant sources</span>
            </div>
            """, unsafe_allow_html=True)

            # Prepare context for Claude
            # Separate into three tiers: Theory, Help/UI, Implementation
            theory_results = []
            help_results = []
            implementation_results = []

            for result in results[:15]:  # Use top 15 results for comprehensive coverage
                source = result["metadata"].get("source", "Unknown").lower()
                topic = result["metadata"].get("topic", "")

                # Tier 1: Theoretical content (Direct Consolidation Framework, IFRS standards)
                if "direct_consolidation_chunks" in source or topic == "theory":
                    theory_results.append(result)
                    result["tier"] = ("Theory", "tier-theory")
                # Tier 2: Help/UI content (user guides, how-to, help)
                elif "12-user-knowledge-base" in source or "help" in source or topic == "help":
                    help_results.append(result)
                    result["tier"] = ("Help", "tier-help")
                # Tier 3: Implementation content
                else:
                    implementation_results.append(result)
                    result["tier"] = ("Implementation", "tier-impl")

            # Show tier breakdown
            tier_summary = []
            if theory_results:
                tier_summary.append(f'<span class="tier-badge tier-theory">Theory: {len(theory_results)}</span>')
            if help_results:
                tier_summary.append(f'<span class="tier-badge tier-help">Help: {len(help_results)}</span>')
            if implementation_results:
                tier_summary.append(f'<span class="tier-badge tier-impl">Impl: {len(implementation_results)}</span>')

            st.markdown(" ".join(tier_summary), unsafe_allow_html=True)

            # Build context: Theory → Help/UI → Implementation
            # OPTIMIZATION: Extract only core content (strip LLM metadata) and limit chunks
            context_parts = []
            chunks_used = 0

            if theory_results and chunks_used < MAX_CONTEXT_CHUNKS:
                context_parts.append("=== THEORETICAL FOUNDATION (Direct Consolidation Framework / IFRS) ===\n")
                for i, result in enumerate(theory_results[:5], 1):  # Max 5 theory chunks
                    if chunks_used >= MAX_CONTEXT_CHUNKS:
                        break
                    source = result["metadata"].get("source", "Unknown")
                    content = extract_content_only(result["content"])  # Extract core content only
                    context_parts.append(f"[Theory Source {i}: {source}]\n{content}")
                    chunks_used += 1

            if help_results and chunks_used < MAX_CONTEXT_CHUNKS:
                context_parts.append("\n=== USER GUIDE & UI INSTRUCTIONS ===\n")
                for i, result in enumerate(help_results[:3], 1):  # Max 3 help chunks
                    if chunks_used >= MAX_CONTEXT_CHUNKS:
                        break
                    source = result["metadata"].get("source", "Unknown")
                    content = extract_content_only(result["content"])  # Extract core content only
                    context_parts.append(f"[Help Source {i}: {source}]\n{content}")
                    chunks_used += 1

            if implementation_results and chunks_used < MAX_CONTEXT_CHUNKS:
                context_parts.append("\n=== PROPHIX.CONSO IMPLEMENTATION ===\n")
                for i, result in enumerate(implementation_results[:3], 1):  # Max 3 impl chunks
                    if chunks_used >= MAX_CONTEXT_CHUNKS:
                        break
                    source = result["metadata"].get("source", "Unknown")
                    content = extract_content_only(result["content"])  # Extract core content only
                    context_parts.append(f"[Implementation Source {i}: {source}]\n{content}")
                    chunks_used += 1

            context = "\n\n---\n\n".join(context_parts)

            # Step 2: Generating with STREAMING
            step2_placeholder = st.empty()
            step2_placeholder.markdown("""
            <div class="progress-step active">
                <div class="step-indicator">2</div>
                <span>Generating answer with Claude (streaming)...</span>
            </div>
            """, unsafe_allow_html=True)

        # Display answer header BEFORE streaming starts
        st.markdown("## Answer")

        # Show conversation context indicator if this is a follow-up
        if len(st.session_state.conversation_history) > 1:
            st.info(f"Answer #{len(st.session_state.conversation_history)} in this conversation (considering previous context)")

        # Generate answer with STREAMING - text appears as it's generated
        _start = time.time()
        logger.info(f"Starting STREAMING Claude call: model={st.session_state.model_tier}, level={explanation_level}, context_chars={len(context)}")

        # Create streaming generator
        stream_generator = generate_answer_streaming(
            query,
            context,
            conversation_history=st.session_state.conversation_history,
            explanation_level=explanation_level,
            model_tier=st.session_state.model_tier,
            knowledge_mode=st.session_state.knowledge_mode
        )

        # Use Streamlit's write_stream to display chunks as they arrive
        # This shows text appearing in real-time
        answer = st.write_stream(stream_generator)

        _elapsed = time.time() - _start
        logger.info(f"Streaming Claude call completed in {_elapsed:.2f}s, answer_chars={len(answer) if answer else 0}")

        # Mark step 2 complete
        step2_placeholder.markdown("""
        <div class="progress-step complete">
            <div class="step-indicator complete"></div>
            <span>Answer generated</span>
        </div>
        """, unsafe_allow_html=True)

        # Store in conversation history
        st.session_state.conversation_history.append({
            "question": query,
            "answer": answer if answer else "",
            "sources_count": len(results),
            "explanation_level": explanation_level,
            "topic_filter": selected_topic_label
        })

        # Limit conversation history to prevent memory growth (keep last 20 exchanges)
        MAX_HISTORY = 20
        if len(st.session_state.conversation_history) > MAX_HISTORY:
            st.session_state.conversation_history = st.session_state.conversation_history[-MAX_HISTORY:]

        # Audio Narration - Web Speech API
        # Strip markdown for cleaner audio reading
        answer_text = answer if answer else ""
        clean_text_for_audio = re.sub(r'[#*`|_\[\]()]', '', answer_text)  # Remove markdown chars
        clean_text_for_audio = re.sub(r'\n{2,}', '. ', clean_text_for_audio)  # Replace multiple newlines with period
        clean_text_for_audio = clean_text_for_audio.replace('\n', ' ')  # Replace single newlines with space
        # Escape for JavaScript
        audio_text = html.escape(clean_text_for_audio).replace("'", "\\'").replace('"', '\\"')

        audio_controls_html = f"""
        <div class="audio-controls">
            <button id="audio-play-btn" class="audio-btn" onclick="toggleAudio()">
                <span id="audio-icon">▶</span> Listen
            </button>
            <button class="audio-btn" onclick="stopAudio()" title="Stop">■ Stop</button>
            <select id="audio-speed" class="speed-select" onchange="updateSpeed()" title="Playback speed">
                <option value="0.75">0.75x</option>
                <option value="1" selected>1x</option>
                <option value="1.25">1.25x</option>
                <option value="1.5">1.5x</option>
            </select>
            <span id="audio-status" style="font-size: 12px; color: #8B949E; margin-left: 8px;"></span>
        </div>
        <script>
        let utterance = null;
        let isPlaying = false;

        function toggleAudio() {{
            if (isPlaying) {{
                window.speechSynthesis.pause();
                isPlaying = false;
                document.getElementById('audio-icon').textContent = '▶';
                document.getElementById('audio-status').textContent = 'Paused';
            }} else if (window.speechSynthesis.paused) {{
                window.speechSynthesis.resume();
                isPlaying = true;
                document.getElementById('audio-icon').textContent = '⏸';
                document.getElementById('audio-status').textContent = 'Playing...';
            }} else {{
                startAudio();
            }}
        }}

        function startAudio() {{
            window.speechSynthesis.cancel();
            const text = `{audio_text}`;
            utterance = new SpeechSynthesisUtterance(text);
            utterance.rate = parseFloat(document.getElementById('audio-speed').value);
            utterance.onstart = function() {{
                isPlaying = true;
                document.getElementById('audio-icon').textContent = '⏸';
                document.getElementById('audio-status').textContent = 'Playing...';
            }};
            utterance.onend = function() {{
                isPlaying = false;
                document.getElementById('audio-icon').textContent = '▶';
                document.getElementById('audio-status').textContent = 'Finished';
            }};
            utterance.onerror = function(e) {{
                isPlaying = false;
                document.getElementById('audio-icon').textContent = '▶';
                document.getElementById('audio-status').textContent = 'Error: ' + e.error;
            }};
            window.speechSynthesis.speak(utterance);
        }}

        function stopAudio() {{
            window.speechSynthesis.cancel();
            isPlaying = false;
            document.getElementById('audio-icon').textContent = '▶';
            document.getElementById('audio-status').textContent = 'Stopped';
        }}

        function updateSpeed() {{
            if (utterance && isPlaying) {{
                // Restart with new speed
                const currentText = utterance.text;
                stopAudio();
                setTimeout(() => startAudio(), 100);
            }}
        }}
        </script>
        """
        st.components.v1.html(audio_controls_html, height=50)

        # Copy to clipboard button - single click copies directly
        answer_id = f"answer_{len(st.session_state.conversation_history)}"
        # Properly escape HTML content
        escaped_answer = html.escape(answer)

        # Download as Markdown - prepare content first
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        filename_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Create formatted Markdown content
        topic_display = selected_topic_label if topic_filter != "all" else "All Topics"
        markdown_content = f"""# {query}

**Generated:** {timestamp}
**Explanation Level:** {explanation_level}
**Topic Filter:** {topic_display}
**Sources Used:** {len(results)}

---

{answer}

---

## Metadata

- **Portal:** Financial Consolidation Knowledge Base - Education Portal
- **Knowledge Base:** Prophix.FC FC Knowledge Base
- **AI Model:** Claude 3.5 Sonnet via AWS Bedrock
- **Question:** {query}
- **Level:** {explanation_level}
- **Topic:** {topic_display}
- **Date:** {timestamp}

---

*Generated by FC Education Portal v3.0*
"""

        # Create safe filename from query
        safe_query = "".join(c if c.isalnum() or c in " -_" else "" for c in query)[:50].strip()
        filename = f"FC_{safe_query}_{filename_timestamp}.md"

        # Action buttons side by side (5 columns with Bookmark)
        btn_col1, btn_col2, btn_col3, btn_col4, btn_col5 = st.columns([1, 1, 1, 1, 1])

        with btn_col1:
            copy_button_html = f"""
            <div style="display: flex; align-items: center; height: 100%;">
            <button onclick="copyToClipboard()" style="
                background-color: #5B7FFF;
                color: white;
                border: 1px solid #5B7FFF;
                padding: 0.25rem 0.75rem;
                border-radius: 0.5rem;
                cursor: pointer;
                font-size: 14px;
                font-weight: 400;
                width: 100%;
                min-height: 38px;
                line-height: 1.6;
                transition: background-color 0.2s ease, border-color 0.2s ease;
            ">
                Copy
            </button>
            </div>
            <span id="copy-status" style="margin-left: 10px; color: #5B7FFF; display: none;">Copied</span>
            <textarea id="{answer_id}" style="position: absolute; left: -9999px;">{escaped_answer}</textarea>
            <script>
            function copyToClipboard() {{
                const text = document.getElementById('{answer_id}').value;
                navigator.clipboard.writeText(text).then(function() {{
                    const status = document.getElementById('copy-status');
                    status.style.display = 'inline';
                    setTimeout(function() {{
                        status.style.display = 'none';
                    }}, 2000);
                }}, function(err) {{
                    alert('Failed to copy text: ' + err);
                }});
            }}
            </script>
            """
            st.components.v1.html(copy_button_html, height=50)

        with btn_col2:
            # Download button as custom HTML for consistent styling
            escaped_markdown = markdown_content.replace('\\', '\\\\').replace('`', '\\`').replace('$', '\\$').replace('\n', '\\n').replace('\r', '\\r')
            download_html = f"""
            <div style="display: flex; align-items: center; height: 100%;">
            <button onclick="downloadMarkdown()" style="
                background-color: #21262D;
                color: #C9D1D9;
                border: 1px solid #30363D;
                padding: 0.25rem 0.75rem;
                border-radius: 0.5rem;
                cursor: pointer;
                font-size: 14px;
                font-weight: 400;
                width: 100%;
                min-height: 38px;
                line-height: 1.6;
                transition: background-color 0.2s ease, border-color 0.2s ease;
            ">
                Download
            </button>
            </div>
            <script>
            function downloadMarkdown() {{
                const content = `{escaped_markdown}`;
                const blob = new Blob([content], {{type: 'text/markdown'}});
                const url = URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = '{filename}';
                document.body.appendChild(a);
                a.click();
                document.body.removeChild(a);
                URL.revokeObjectURL(url);
            }}
            </script>
            """
            st.components.v1.html(download_html, height=50)

        with btn_col3:
            # Print button with clean formatted output (consistent style)
            print_html = f"""
            <div style="display: flex; align-items: center; height: 100%;">
            <button onclick="printAnswer()" style="
                background-color: #5B7FFF;
                color: white;
                border: 1px solid #5B7FFF;
                padding: 0.25rem 0.75rem;
                border-radius: 0.5rem;
                cursor: pointer;
                font-size: 14px;
                font-weight: 400;
                width: 100%;
                min-height: 38px;
                line-height: 1.6;
                transition: background-color 0.2s ease, border-color 0.2s ease;
            ">
                Print
            </button>
            </div>
            <script>
            function printAnswer() {{
                const printContent = `
                    <!DOCTYPE html>
                    <html>
                    <head>
                        <title>{query[:50]} - FC Knowledge Base</title>
                        <style>
                            body {{
                                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                                line-height: 1.6;
                                max-width: 800px;
                                margin: 0 auto;
                                padding: 40px 20px;
                                color: #333;
                            }}
                            h1 {{ color: #1a1a1a; font-size: 24px; border-bottom: 2px solid #5B7FFF; padding-bottom: 10px; }}
                            h2 {{ color: #333; font-size: 20px; margin-top: 30px; }}
                            h3 {{ color: #444; font-size: 16px; }}
                            pre {{ background: #f5f5f5; padding: 15px; border-radius: 4px; overflow-x: auto; font-size: 13px; }}
                            code {{ background: #f0f0f0; padding: 2px 6px; border-radius: 3px; font-size: 13px; }}
                            table {{ border-collapse: collapse; width: 100%; margin: 15px 0; }}
                            th, td {{ border: 1px solid #ddd; padding: 10px; text-align: left; }}
                            th {{ background: #f5f5f5; }}
                            .metadata {{ color: #666; font-size: 12px; margin-top: 40px; padding-top: 20px; border-top: 1px solid #ddd; }}
                            @media print {{
                                body {{ padding: 20px; }}
                                pre {{ white-space: pre-wrap; word-wrap: break-word; }}
                            }}
                        </style>
                    </head>
                    <body>
                        <h1>{query}</h1>
                        <div class="answer">${{document.getElementById('{answer_id}').value.replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/\\n/g, '<br>').replace(/```([\\s\\S]*?)```/g, '<pre>$1</pre>').replace(/\\*\\*([^*]+)\\*\\*/g, '<strong>$1</strong>')}}</div>
                        <div class="metadata">
                            <p><strong>Generated:</strong> {timestamp}</p>
                            <p><strong>Level:</strong> {explanation_level}</p>
                            <p><strong>Topic:</strong> {topic_display}</p>
                            <p><em>FC Education Portal v3.0</em></p>
                        </div>
                    </body>
                    </html>
                `;
                const printWindow = window.open('', '_blank');
                printWindow.document.write(printContent);
                printWindow.document.close();
                printWindow.focus();
                setTimeout(() => {{ printWindow.print(); }}, 250);
            }}
            </script>
            """
            st.components.v1.html(print_html, height=50)

        with btn_col4:
            # Go Deeper button as custom HTML for consistent styling
            escaped_query_deeper = query.replace('\\', '\\\\').replace("'", "\\'").replace('"', '\\"')
            is_detailed = explanation_level == "Detailed"
            go_deeper_html = f"""
            <div style="display: flex; align-items: center; height: 100%;">
            <button onclick="goDeeper()" style="
                background-color: #21262D;
                color: #C9D1D9;
                border: 1px solid #30363D;
                padding: 0.25rem 0.75rem;
                border-radius: 0.5rem;
                cursor: {'not-allowed' if is_detailed else 'pointer'};
                font-size: 14px;
                font-weight: 400;
                width: 100%;
                min-height: 38px;
                line-height: 1.6;
                transition: background-color 0.2s ease, border-color 0.2s ease;
                opacity: {'0.5' if is_detailed else '1'};
            ">
                {'Detailed' if is_detailed else 'Go Deeper'}
            </button>
            </div>
            <script>
            function goDeeper() {{
                {'return;' if is_detailed else ''}
                const baseUrl = window.top.location.href.split('?')[0];
                const url = baseUrl + '?go_deeper=' + encodeURIComponent('{escaped_query_deeper}');
                window.open(url, '_blank');
            }}
            </script>
            """
            st.components.v1.html(go_deeper_html, height=50)

        with btn_col5:
            # Bookmark button - saves to localStorage
            bookmark_id = f"bm_{hash(query) % 10000}"
            is_bookmarked = any(b.get('question') == query for b in st.session_state.get('bookmarks', []))

            # Escape query for JavaScript template literal (must be done outside f-string)
            escaped_query_js = query.replace('\\', '\\\\').replace('`', '\\`').replace('$', '\\$')

            bookmark_html = f"""
            <div style="display: flex; align-items: center; height: 100%;">
            <button id="bookmark-btn-{bookmark_id}" onclick="toggleBookmark()" style="
                background-color: {'#4A6FEE' if is_bookmarked else '#5B7FFF'};
                color: white;
                border: 1px solid {'#4A6FEE' if is_bookmarked else '#5B7FFF'};
                padding: 0.25rem 0.75rem;
                border-radius: 0.5rem;
                cursor: pointer;
                font-size: 14px;
                font-weight: 400;
                width: 100%;
                min-height: 38px;
                line-height: 1.6;
                transition: background-color 0.2s ease, border-color 0.2s ease;
            ">
                {'Saved' if is_bookmarked else 'Save'}
            </button>
            </div>
            <script>
            function toggleBookmark() {{
                const question = `{escaped_query_js}`;
                const answer = document.getElementById('{answer_id}').value;
                const timestamp = new Date().toISOString();

                // Get current bookmarks from localStorage
                let bookmarks = JSON.parse(localStorage.getItem('fc_bookmarks') || '[]');
                const existingIdx = bookmarks.findIndex(b => b.question === question);

                if (existingIdx >= 0) {{
                    // Remove bookmark
                    bookmarks.splice(existingIdx, 1);
                    document.getElementById('bookmark-btn-{bookmark_id}').innerHTML = 'Save';
                    document.getElementById('bookmark-btn-{bookmark_id}').style.backgroundColor = '#5B7FFF';
                    document.getElementById('bookmark-btn-{bookmark_id}').style.borderColor = '#5B7FFF';
                }} else {{
                    // Add bookmark
                    bookmarks.unshift({{
                        id: Date.now(),
                        question: question,
                        answer: answer.substring(0, 2000),  // Limit stored answer size
                        timestamp: timestamp
                    }});
                    // Keep only last 20 bookmarks
                    if (bookmarks.length > 20) bookmarks = bookmarks.slice(0, 20);
                    document.getElementById('bookmark-btn-{bookmark_id}').innerHTML = 'Saved';
                    document.getElementById('bookmark-btn-{bookmark_id}').style.backgroundColor = '#4A6FEE';
                    document.getElementById('bookmark-btn-{bookmark_id}').style.borderColor = '#4A6FEE';
                }}

                localStorage.setItem('fc_bookmarks', JSON.stringify(bookmarks));

                // Dispatch event for Streamlit to potentially pick up
                window.dispatchEvent(new CustomEvent('bookmarkChanged', {{ detail: {{ bookmarks: bookmarks }} }}));
            }}
            </script>
            """
            st.components.v1.html(bookmark_html, height=50)

        # Generate follow-up questions and related topics
        # OPTIMIZATION: Skip for "Executive Summary" mode - users want fast answers
        follow_up_questions = []
        related = []

        if explanation_level == "Executive Summary":
            # Fast mode: use hardcoded suggestions, skip LLM calls
            follow_up_questions = get_fallback_follow_ups(query)
            related = get_related_topics(query)
        else:
            # Standard/Detailed: generate with LLM in parallel
            with st.spinner("Generating suggestions..."):
                with ThreadPoolExecutor(max_workers=2) as executor:
                    future_followup = executor.submit(generate_follow_up_questions, query, answer)
                    future_related = executor.submit(generate_related_topics_rag, query, answer)

                    try:
                        follow_up_questions = future_followup.result(timeout=60)
                    except Exception as e:
                        logger.warning(f"Follow-up generation failed: {e}")
                        follow_up_questions = get_fallback_follow_ups(query)

                    try:
                        related = future_related.result(timeout=60)
                    except Exception:
                        related = []

                # Fallback to hardcoded if RAG fails
                if not related:
                    related = get_related_topics(query)

        # Smart Follow-Up Questions - AI-generated deeper questions
        st.markdown("**Explore Further**")
        st.caption("AI-suggested questions to deepen your understanding")

        if follow_up_questions:
            fu_cols = st.columns(len(follow_up_questions))
            for idx, fu_question in enumerate(follow_up_questions):
                with fu_cols[idx]:
                    # Truncate long questions for button display
                    btn_label = fu_question[:45] + "..." if len(fu_question) > 45 else fu_question
                    if st.button(btn_label, key=f"followup_{idx}", use_container_width=True, help=fu_question):
                        st.session_state.query = fu_question
                        st.session_state.trigger_search = True
                        st.rerun()

        st.markdown("")  # Spacing

        # Related Topics - RAG-generated contextual suggestions
        st.markdown("**Related Topics**")
        st.caption("AI-suggested based on your query")

        if related:
            cols = st.columns(min(len(related), 4))
            for idx, (label, related_query) in enumerate(related[:4]):
                with cols[idx % 4]:
                    if st.button(label, key=f"related_{idx}", use_container_width=True, help=related_query):
                        st.session_state.query = related_query
                        st.session_state.trigger_search = True
                        st.rerun()

        st.markdown("")  # Spacing

        # Display conversation history if exists
        if len(st.session_state.conversation_history) > 1:
            with st.expander(f"Conversation History ({len(st.session_state.conversation_history) - 1} previous)", expanded=False):
                # Show all previous Q&A except the current one
                for i, exchange in enumerate(st.session_state.conversation_history[:-1], 1):
                    st.markdown(f"**Q{i}:** {exchange['question']}")
                    st.markdown(exchange['answer'][:500] + "..." if len(exchange['answer']) > 500 else exchange['answer'])
                    st.caption(f"{exchange['sources_count']} sources used")
                    st.markdown("---")

        # Display sources with tier badges
        with st.expander("View Sources", expanded=False):
            # Legend for tiers
            st.markdown("""
            <div style="margin-bottom: 15px; font-size: 12px;">
                <span class="tier-badge tier-theory">Theory</span> Direct Consolidation Framework / IFRS
                <span class="tier-badge tier-help">Help</span> User guides & UI
                <span class="tier-badge tier-impl">Implementation</span> System details
            </div>
            """, unsafe_allow_html=True)

            for i, result in enumerate(results, 1):
                source = result["metadata"].get("source", "Unknown")
                topic = result["metadata"].get("topic", "")
                relevance = result["relevance"]

                # Get tier info
                tier_name, tier_class = result.get("tier", ("Implementation", "tier-impl"))

                st.markdown(f'<span class="tier-badge {tier_class}">{tier_name}</span> **Source {i}** — Relevance: {relevance:.1%}', unsafe_allow_html=True)
                st.caption(f"Source: {source} | Topic: {topic}")
                st.text_area(
                    label=f"Content {i}",
                    value=result["content"],
                    height=150,
                    key=f"source_{i}",
                    label_visibility="collapsed",
                )
                st.markdown("")  # Light spacing instead of divider

    elif not query and search_button:
        st.info("Please enter a question to search.")


if __name__ == "__main__":
    main()
