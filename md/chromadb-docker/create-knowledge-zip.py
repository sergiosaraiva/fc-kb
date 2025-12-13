#!/usr/bin/env python3
"""
Create FC-Full-KnowledgeBase.zip with semantic chunks.

- direct_consolidation_chunks/: Already pre-chunked, use as-is
- documentation-library/: Apply semantic chunking by markdown headers

All chunks are normalized (CRLF -> LF) for WSL compatibility.

Features:
- LLM-powered enhancement using AWS Bedrock Claude (--enhance flag)
- Semantic summaries, keywords, hypothetical questions (HyDE)
- World-class RAG quality

Usage:
  python create-knowledge-zip.py           # Fast, rule-based
  python create-knowledge-zip.py --enhance # LLM-enhanced (recommended)
"""

import argparse
import os
import re
import sys
import zipfile
from pathlib import Path
from typing import List, Tuple, Optional, Dict

# Script location
SCRIPT_DIR = Path(__file__).parent.resolve()
ZIP_FILE = SCRIPT_DIR / "FC-Full-KnowledgeBase.zip"

# Chunking configuration
TARGET_CHUNK_SIZE = 2000  # Target chars per chunk (good for complex/technical content)
MIN_CHUNK_SIZE = 300      # Merge smaller chunks with neighbors
MAX_CHUNK_SIZE = 4000     # Split if section exceeds this


def normalize_content(content: str) -> str:
    """Normalize line endings to LF."""
    return content.replace("\r\n", "\n").replace("\r", "\n")


def semantic_chunk_yaml(content: str, source_file: str) -> List[Tuple[str, str]]:
    """
    Split YAML content into semantic chunks based on YAML keys at multiple levels.

    Strategy:
    1. First try splitting by top-level keys
    2. If any chunk > MAX_CHUNK_SIZE, split by 2-space indented keys
    3. If still too large, split by 4-space indented keys

    Returns list of (chunk_content, chunk_id_suffix) tuples.
    """
    YAML_MAX_CHUNK = 8000  # YAML chunks target max (API docs need more context)

    def split_by_indent(lines: List[str], indent_level: int, base_idx: int,
                        parent_key: str) -> List[Tuple[str, str]]:
        """Split lines by keys at the specified indent level."""
        indent_str = ' ' * indent_level
        chunks = []
        current_key = parent_key
        current_lines = []
        chunk_idx = base_idx

        for line in lines:
            # Check for key at this indent level (exact indent, has :)
            stripped = line.rstrip()
            if stripped and not stripped.startswith('#'):
                # Count leading spaces
                leading_spaces = len(line) - len(line.lstrip())

                # Key at our target indent level
                if leading_spaces == indent_level and ':' in stripped:
                    # Save previous chunk
                    if current_lines:
                        chunk_content = '\n'.join(current_lines).strip()
                        if chunk_content:
                            chunks.append((chunk_content, f"{chunk_idx:03d}", current_key))
                            chunk_idx += 1

                    # Start new section
                    key_name = stripped.split(':')[0].strip()
                    current_key = f"{parent_key}.{key_name}" if parent_key else key_name
                    current_lines = [line]
                else:
                    current_lines.append(line)
            else:
                current_lines.append(line)

        # Don't forget last chunk
        if current_lines:
            chunk_content = '\n'.join(current_lines).strip()
            if chunk_content:
                chunks.append((chunk_content, f"{chunk_idx:03d}", current_key))

        return chunks

    chunks = []
    try:
        lines = content.split('\n')

        # First pass: split by top-level keys (0 indent)
        first_pass = split_by_indent(lines, 0, 0, "")

        chunk_idx = 0
        for chunk_content, _, key_path in first_pass:
            # If chunk is small enough, keep it
            if len(chunk_content) <= YAML_MAX_CHUNK:
                header = f"# YAML: {source_file}\n## Section: {key_path or 'root'}\n\n"
                chunks.append((header + chunk_content, f"{chunk_idx:03d}"))
                chunk_idx += 1
            else:
                # Chunk too large - split by 2-space indented keys
                chunk_lines = chunk_content.split('\n')
                second_pass = split_by_indent(chunk_lines, 2, chunk_idx, key_path)

                for sub_content, _, sub_key in second_pass:
                    if len(sub_content) <= YAML_MAX_CHUNK:
                        header = f"# YAML: {source_file}\n## Section: {sub_key or key_path}\n\n"
                        chunks.append((header + sub_content, f"{chunk_idx:03d}"))
                        chunk_idx += 1
                    else:
                        # Still too large - split by 4-space indented keys
                        sub_lines = sub_content.split('\n')
                        third_pass = split_by_indent(sub_lines, 4, chunk_idx, sub_key)

                        for deep_content, _, deep_key in third_pass:
                            header = f"# YAML: {source_file}\n## Section: {deep_key or sub_key}\n\n"
                            chunks.append((header + deep_content, f"{chunk_idx:03d}"))
                            chunk_idx += 1

    except Exception as e:
        # If parsing fails, use whole file
        header = f"# YAML: {source_file}\n\n"
        chunks.append((header + content, "000"))

    # If no chunks created, use whole file
    if not chunks:
        header = f"# YAML: {source_file}\n\n"
        chunks.append((header + content, "000"))

    # Merge small chunks with neighbors
    if len(chunks) > 1:
        merged = []
        i = 0
        while i < len(chunks):
            current_content, current_id = chunks[i]

            # If current chunk is small, merge with next
            while len(current_content) < MIN_CHUNK_SIZE and i + 1 < len(chunks):
                i += 1
                next_content, _ = chunks[i]
                current_content = current_content + "\n\n---\n\n" + next_content

            merged.append((current_content, current_id))
            i += 1

        chunks = merged

    return chunks


def read_file(filepath: Path) -> str:
    """Read file and normalize line endings."""
    with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
        return normalize_content(f.read())


def extract_title(content: str) -> str:
    """Extract first heading or first line as title."""
    lines = content.strip().split("\n")
    for line in lines[:5]:
        if line.startswith("#"):
            return line.lstrip("#").strip()
    return lines[0][:50] if lines else "Untitled"


def semantic_chunk_markdown(content: str, source_file: str) -> List[Tuple[str, str]]:
    """
    Split markdown content into semantic chunks based on headers.

    Returns list of (chunk_content, chunk_id_suffix) tuples.
    """
    chunks = []

    # Split by level 2 headers (##) as primary sections
    # Keep level 3+ headers (###) within their parent section
    sections = re.split(r'\n(?=## )', content)

    for section_idx, section in enumerate(sections):
        section = section.strip()
        if not section:
            continue

        # If section is small enough, use as-is (will merge small ones later)
        if len(section) <= MAX_CHUNK_SIZE:
            chunks.append((section, f"{section_idx:03d}"))
            continue

        # Section too large - split by level 3 headers
        subsections = re.split(r'\n(?=### )', section)

        current_chunk = ""
        chunk_sub_idx = 0

        for subsection in subsections:
            subsection = subsection.strip()
            if not subsection:
                continue

            # If adding this subsection keeps us under target, accumulate
            if len(current_chunk) + len(subsection) + 2 <= TARGET_CHUNK_SIZE:
                current_chunk += ("\n\n" if current_chunk else "") + subsection
            else:
                # Save current chunk (will merge small ones later)
                if current_chunk.strip():
                    chunks.append((current_chunk, f"{section_idx:03d}_{chunk_sub_idx:02d}"))
                    chunk_sub_idx += 1

                # Start new chunk with this subsection
                if len(subsection) <= MAX_CHUNK_SIZE:
                    current_chunk = subsection
                else:
                    # Subsection itself is too large - split by paragraphs
                    paragraphs = subsection.split("\n\n")
                    current_chunk = ""

                    for para in paragraphs:
                        if len(current_chunk) + len(para) + 2 <= TARGET_CHUNK_SIZE:
                            current_chunk += ("\n\n" if current_chunk else "") + para
                        else:
                            if current_chunk.strip():
                                chunks.append((current_chunk, f"{section_idx:03d}_{chunk_sub_idx:02d}"))
                                chunk_sub_idx += 1
                            current_chunk = para

        # Don't forget the last chunk (will merge small ones later)
        if current_chunk.strip():
            chunks.append((current_chunk, f"{section_idx:03d}_{chunk_sub_idx:02d}"))

    # If no chunks created (file has no headers), treat whole file as one chunk
    if not chunks and content.strip():
        chunks.append((content.strip(), "000"))

    # Merge small chunks with neighbors for better context
    if len(chunks) > 1:
        merged = []
        i = 0
        while i < len(chunks):
            current_content, current_id = chunks[i]

            # If current chunk is small, merge with next
            while len(current_content) < MIN_CHUNK_SIZE and i + 1 < len(chunks):
                i += 1
                next_content, _ = chunks[i]
                current_content = current_content + "\n\n" + next_content

            merged.append((current_content, current_id))
            i += 1

        # Handle case where last chunk is small - merge with previous
        if len(merged) > 1 and len(merged[-1][0]) < MIN_CHUNK_SIZE:
            last_content, _ = merged.pop()
            prev_content, prev_id = merged.pop()
            merged.append((prev_content + "\n\n" + last_content, prev_id))

        chunks = merged

    return chunks


def extract_doc_title(filepath: str) -> str:
    """Extract document title from filepath."""
    # Convert path like "03-core-calculations/goodwill-calculation.md" to "Goodwill Calculation"
    filename = filepath.split("/")[-1].replace(".md", "").replace("-", " ")
    return filename.title()


def extract_topic_area(filepath: str) -> str:
    """Extract topic area from filepath."""
    topic_map = {
        "02-consolidation-methods": "Consolidation Methods",
        "03-core-calculations": "Core Calculations",
        "04-elimination": "Elimination Entries",
        "05-currency": "Currency Translation",
        "06-ownership": "Ownership Structure",
        "07-database": "Database Implementation",
        "08-application": "Application Layer",
        "09-frontend": "Frontend Implementation",
        "10-gap-analysis": "Gap Analysis",
        "11-agent-support": "Agent Support / API",
        "12-user-knowledge-base": "User Help / Knowledge Base",
        "17-troubleshooting": "Troubleshooting",
        "20-appendices": "Reference / Appendices",
        "00-index": "Index / Overview",
    }
    for key, value in topic_map.items():
        if key in filepath:
            return value
    return "Financial Consolidation"


def generate_context_sentence(doc_title: str, section_title: str, topic_area: str) -> str:
    """Generate a context sentence explaining what this chunk covers."""
    # Create a natural language description
    if section_title and section_title != doc_title:
        return f"This section covers {section_title.lower()} in the context of {doc_title.lower()} ({topic_area.lower()})."
    else:
        return f"This section covers {doc_title.lower()} ({topic_area.lower()})."


def extract_keywords(content: str) -> list:
    """Extract key terms for hybrid search."""
    # Important consolidation terms to look for
    keywords = []
    term_patterns = [
        # IFRS/IAS standards
        (r"IFRS\s*\d+", "ifrs"),
        (r"IAS\s*\d+", "ias"),
        # Consolidation methods
        (r"global integration", "method"),
        (r"equity method", "method"),
        (r"proportional", "method"),
        (r"full consolidation", "method"),
        # Key concepts
        (r"goodwill", "concept"),
        (r"minority interest|non-controlling interest|NCI", "concept"),
        (r"elimination", "concept"),
        (r"intercompany", "concept"),
        (r"currency translation", "concept"),
        (r"exchange rate", "concept"),
        (r"deferred tax", "concept"),
        (r"acquisition", "concept"),
        (r"disposal|deconsolidation", "concept"),
        # Technical terms
        (r"stored procedure|P_CONSO|P_CALC", "technical"),
        (r"T_[A-Z_]+|TS_[A-Z_]+|TD_[A-Z_]+", "database"),
    ]

    content_lower = content.lower()
    for pattern, category in term_patterns:
        import re
        matches = re.findall(pattern, content_lower, re.IGNORECASE)
        keywords.extend(matches)

    # Deduplicate and clean
    return list(dict.fromkeys([k.strip().upper() for k in keywords if k.strip()]))[:10]


def generate_summary(content: str, section_title: str) -> str:
    """Generate a one-line summary for better embedding."""
    # Use first non-header, non-diagram paragraph as summary
    lines = content.strip().split('\n')
    for line in lines:
        line = line.strip()
        # Skip headers, tables, code blocks, ASCII art, empty lines
        if not line:
            continue
        if line.startswith('#') or line.startswith('|') or line.startswith('```'):
            continue
        if any(c in line for c in ['─', '│', '┌', '┐', '└', '┘', '├', '┤', '┬', '┴', '┼', '═', '║']):
            continue
        if line.startswith('-') and len(line) < 50:  # Skip short list items
            continue
        if len(line) > 50:
            # Clean and truncate
            summary = line[:200].rsplit(' ', 1)[0] + '...' if len(line) > 200 else line
            return summary
    return f"Information about {section_title.lower()}."


def extract_related_topics(content: str, topic_area: str) -> list:
    """Extract related topics based on content keywords."""
    topic_keywords = {
        "goodwill": ["Participation Elimination", "Acquisition Accounting", "IFRS 3"],
        "elimination": ["Intercompany Transactions", "Consolidation Adjustments"],
        "currency": ["Exchange Rates", "Translation Differences", "IAS 21"],
        "ownership": ["Control", "Minority Interest", "Consolidation Scope"],
        "equity method": ["Associates", "Joint Ventures", "IAS 28"],
        "global integration": ["Full Consolidation", "Control", "IFRS 10"],
        "proportional": ["Joint Control", "Joint Ventures"],
        "minority": ["Non-Controlling Interest", "NCI", "Partial Ownership"],
        "dividend": ["Profit Distribution", "Intercompany Dividends"],
        "deferred tax": ["Tax Adjustments", "IAS 12"],
    }

    related = []
    content_lower = content.lower()
    for keyword, topics in topic_keywords.items():
        if keyword in content_lower:
            related.extend(topics)

    # Add topic area as related
    if topic_area not in related:
        related.append(topic_area)

    # Deduplicate and limit
    return list(dict.fromkeys(related))[:5]


# Global enhancer instance (lazy loaded)
_llm_enhancer = None


def get_llm_enhancer():
    """Get LLM enhancer instance (lazy loaded)."""
    global _llm_enhancer
    if _llm_enhancer is None:
        from llm_chunk_enhancer import get_enhancer
        _llm_enhancer = get_enhancer()
    return _llm_enhancer


def add_chunk_context(
    chunk_content: str,
    source_path: str,
    chunk_idx: int,
    total_chunks: int,
    use_llm: bool = False
) -> str:
    """Add rich context to chunk for better retrieval and understanding."""
    # Extract context elements
    doc_title = extract_doc_title(source_path)
    topic_area = extract_topic_area(source_path)
    section_title = extract_title(chunk_content)

    if use_llm:
        # Use LLM for world-class quality
        enhancer = get_llm_enhancer()
        llm_result = enhancer.enhance_chunk(chunk_content, source_path, topic_area)

        summary = llm_result.get("summary", f"Information about {section_title.lower()}.")
        keywords = llm_result.get("keywords", [])
        concepts = llm_result.get("concepts", [])
        questions = llm_result.get("questions", [])
        related_topics = llm_result.get("related_topics", [topic_area])
    else:
        # Fall back to rule-based enhancement
        context_sentence = generate_context_sentence(doc_title, section_title, topic_area)
        summary = generate_summary(chunk_content, section_title)
        keywords = extract_keywords(chunk_content)
        concepts = []
        questions = []
        related_topics = extract_related_topics(chunk_content, topic_area)

    # Build rich context header
    header = f"# {section_title}\n\n"

    # Summary first - most important for embedding quality
    header += f"**Summary:** {summary}\n\n"

    # Hypothetical questions (HyDE) - powerful for retrieval
    if questions:
        header += f"## Questions This Answers\n\n"
        for q in questions:
            header += f"- {q}\n"
        header += "\n"

    header += f"## Context\n\n"
    if not use_llm:
        context_sentence = generate_context_sentence(doc_title, section_title, topic_area)
        header += f"{context_sentence}\n\n"

    header += f"**Topic Area:** {topic_area}  \n"
    header += f"**Document:** {doc_title}  \n"
    header += f"**Source:** {source_path} (Chunk {chunk_idx + 1}/{total_chunks})\n\n"

    # Keywords for hybrid search
    if keywords:
        header += f"**Keywords:** {', '.join(keywords)}\n\n"

    # Key concepts
    if concepts:
        header += f"**Concepts:** {', '.join(concepts)}\n\n"

    header += f"## Content\n\n"

    # Add related topics footer
    footer = f"\n\n## Related Topics\n\n"
    for topic in related_topics:
        footer += f"- {topic}\n"
    footer += f"\n---\n*Chunk {chunk_idx + 1}/{total_chunks} | {section_title}*\n"

    return header + chunk_content + footer


def create_zip(use_llm: bool = False):
    """Create the knowledge base ZIP file with semantic chunks."""
    print("=" * 60)
    print("FC Knowledge Base - Semantic ZIP Creation")
    if use_llm:
        print("Mode: LLM-ENHANCED (World-Class Quality)")
    else:
        print("Mode: Rule-based (Fast)")
    print("=" * 60)
    print()

    src_chunks = SCRIPT_DIR.parent / "direct_consolidation_chunks"
    src_docs = SCRIPT_DIR.parent / "documentation-library"

    total_files = 0
    stats = {"pre_chunked": 0, "semantic_chunked": 0, "yaml_files": 0}

    with zipfile.ZipFile(ZIP_FILE, "w", zipfile.ZIP_DEFLATED) as zf:

        # Source 1: direct_consolidation_chunks (already semantic, use ALL as-is)
        # EXCEPT INDEX.md which is metadata, not content
        if src_chunks.exists():
            print(f"Processing {src_chunks.name}/ (pre-chunked, as-is)...")
            for f in sorted(src_chunks.glob("*.md")):
                # Skip INDEX.md - it's metadata listing chunks, not actual content
                if f.name.upper() == "INDEX.MD":
                    print(f"  Skipping {f.name} (metadata file)")
                    continue
                content = read_file(f)
                if content.strip():  # Include all non-empty files
                    flat_name = f"direct_consolidation_chunks_{f.name}"
                    zf.writestr(flat_name, content)
                    stats["pre_chunked"] += 1
            print(f"  Added {stats['pre_chunked']} pre-chunked files")

        # Source 2: documentation-library (apply semantic chunking)
        if src_docs.exists():
            print(f"Processing {src_docs.name}/ (semantic chunking)...")

            for filepath in sorted(src_docs.rglob("*")):
                if not filepath.is_file():
                    continue

                rel_path = filepath.relative_to(src_docs)
                rel_path_str = str(rel_path).replace(os.sep, "_")

                # YAML files: apply semantic chunking by top-level keys
                if filepath.suffix in (".yaml", ".yml"):
                    content = read_file(filepath)
                    chunks = semantic_chunk_yaml(content, str(rel_path))

                    for idx, (chunk_content, chunk_suffix) in enumerate(chunks):
                        # Add context to YAML chunk (with optional LLM enhancement)
                        chunk_with_context = add_chunk_context(
                            chunk_content, str(rel_path), idx, len(chunks), use_llm
                        )

                        # Progress indicator for LLM mode
                        if use_llm and (idx + 1) % 10 == 0:
                            print(f"    Enhanced {idx + 1}/{len(chunks)} chunks from {filepath.name}")

                        # Create filename
                        base_name = rel_path_str.replace(".yaml", "").replace(".yml", "")
                        flat_name = f"documentation-library_{base_name}_chunk{chunk_suffix}.yaml"

                        zf.writestr(flat_name, chunk_with_context)
                        stats["yaml_files"] += 1
                    continue

                # Markdown files: apply semantic chunking
                if filepath.suffix == ".md":
                    content = read_file(filepath)
                    chunks = semantic_chunk_markdown(content, str(rel_path))

                    for idx, (chunk_content, chunk_suffix) in enumerate(chunks):
                        # Add context to chunk (with optional LLM enhancement)
                        chunk_with_context = add_chunk_context(
                            chunk_content, str(rel_path), idx, len(chunks), use_llm
                        )

                        # Progress indicator for LLM mode
                        if use_llm and (idx + 1) % 10 == 0:
                            print(f"    Enhanced {idx + 1}/{len(chunks)} chunks from {filepath.name}")

                        # Create filename: folder_file_chunkXXX.md
                        base_name = rel_path_str.replace(".md", "")
                        flat_name = f"documentation-library_{base_name}_chunk{chunk_suffix}.md"

                        zf.writestr(flat_name, chunk_with_context)
                        stats["semantic_chunked"] += 1

            print(f"  Added {stats['semantic_chunked']} semantic chunks from .md files")
            print(f"  Added {stats['yaml_files']} semantic chunks from .yaml files")

        total_files = stats["pre_chunked"] + stats["semantic_chunked"] + stats["yaml_files"]

    print()
    print("=" * 60)
    print(f"Created: {ZIP_FILE.name}")
    print(f"Size: {ZIP_FILE.stat().st_size / 1024 / 1024:.1f} MB")
    print("-" * 60)
    print(f"  Pre-chunked (direct_consolidation):  {stats['pre_chunked']:,}")
    print(f"  Semantic chunks (markdown):          {stats['semantic_chunked']:,}")
    print(f"  Semantic chunks (yaml):              {stats['yaml_files']:,}")
    print(f"  TOTAL:                               {total_files:,}")
    print("=" * 60)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Create FC Knowledge Base ZIP with semantic chunks",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python create-knowledge-zip.py            # Fast, rule-based
  python create-knowledge-zip.py --enhance  # LLM-enhanced (recommended for best quality)
        """
    )
    parser.add_argument(
        "--no-llm",
        action="store_true",
        help="Disable LLM enhancement (faster but lower quality)"
    )
    args = parser.parse_args()

    use_llm = not args.no_llm

    if use_llm:
        print("\n🚀 LLM Enhancement enabled (default) - this produces world-class results\n")
    else:
        print("\n⚡ Fast mode (no LLM) - rule-based enhancement\n")

    create_zip(use_llm=use_llm)
