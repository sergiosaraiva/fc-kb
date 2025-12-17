#!/usr/bin/env python3
"""
Create FC-Business-KnowledgeBase.zip with ONLY business data (no technical layers).

Business layer includes:
- direct_consolidation_chunks/ (Allen White's book - 1,332 chunks)
- 02-consolidation-methods/
- 03-core-calculations/
- 04-elimination/
- 05-currency/
- 06-ownership/
- 10-gap-analysis/
- 12-user-knowledge-base/
- 17-troubleshooting/
- 20-appendices/

Excluded (technical):
- 07-database/
- 08-application/
- 09-frontend/
- 11-agent-support/

Usage:
    python create-business-zip.py           # LLM-enhanced (recommended)
    python create-business-zip.py --no-llm  # Fast, rule-based
"""

import argparse
import os
import re
import sys
import zipfile
from pathlib import Path
from typing import List, Tuple

# Script location
SCRIPT_DIR = Path(__file__).parent.resolve()
ZIP_FILE = SCRIPT_DIR / "FC-Business-KnowledgeBase.zip"

# Business layer folders to INCLUDE
BUSINESS_FOLDERS = [
    "02-consolidation-methods",
    "03-core-calculations",
    "04-elimination",
    "05-currency",
    "06-ownership",
    "10-gap-analysis",
    "12-user-knowledge-base",
    "17-troubleshooting",
    "20-appendices",
    "00-index",  # Include index for navigation
]

# Technical folders to EXCLUDE
TECHNICAL_FOLDERS = [
    "07-database",
    "08-application",
    "09-frontend",
    "11-agent-support",
]

# Chunking configuration
TARGET_CHUNK_SIZE = 1200
MIN_CHUNK_SIZE = 200
MAX_CHUNK_SIZE = 2000


def normalize_content(content: str) -> str:
    """Normalize line endings to LF."""
    return content.replace("\r\n", "\n").replace("\r", "\n")


def is_business_path(filepath: str) -> bool:
    """Check if filepath belongs to business layer."""
    filepath_lower = filepath.lower()

    # Exclude technical folders
    for tech_folder in TECHNICAL_FOLDERS:
        if tech_folder in filepath_lower:
            return False

    return True


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
    """Split markdown content into semantic chunks based on headers."""
    chunks = []
    sections = re.split(r'\n(?=## )', content)

    for section_idx, section in enumerate(sections):
        section = section.strip()
        if not section:
            continue

        if len(section) <= MAX_CHUNK_SIZE:
            chunks.append((section, f"{section_idx:03d}"))
            continue

        subsections = re.split(r'\n(?=### )', section)
        current_chunk = ""
        chunk_sub_idx = 0

        for subsection in subsections:
            subsection = subsection.strip()
            if not subsection:
                continue

            if len(current_chunk) + len(subsection) + 2 <= TARGET_CHUNK_SIZE:
                current_chunk += ("\n\n" if current_chunk else "") + subsection
            else:
                if current_chunk.strip():
                    chunks.append((current_chunk, f"{section_idx:03d}_{chunk_sub_idx:02d}"))
                    chunk_sub_idx += 1

                if len(subsection) <= MAX_CHUNK_SIZE:
                    current_chunk = subsection
                else:
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

        if current_chunk.strip():
            chunks.append((current_chunk, f"{section_idx:03d}_{chunk_sub_idx:02d}"))

    if not chunks and content.strip():
        chunks.append((content.strip(), "000"))

    # Merge small chunks
    if len(chunks) > 1:
        merged = []
        i = 0
        while i < len(chunks):
            current_content, current_id = chunks[i]
            while len(current_content) < MIN_CHUNK_SIZE and i + 1 < len(chunks):
                i += 1
                next_content, _ = chunks[i]
                current_content = current_content + "\n\n" + next_content
            merged.append((current_content, current_id))
            i += 1

        if len(merged) > 1 and len(merged[-1][0]) < MIN_CHUNK_SIZE:
            last_content, _ = merged.pop()
            prev_content, prev_id = merged.pop()
            merged.append((prev_content + "\n\n" + last_content, prev_id))

        chunks = merged

    return chunks


def semantic_chunk_yaml(content: str, source_file: str) -> List[Tuple[str, str]]:
    """Split YAML content into semantic chunks."""
    YAML_MAX_CHUNK = 4000

    def split_by_indent(lines: List[str], indent_level: int, base_idx: int, parent_key: str) -> List[Tuple[str, str, str]]:
        indent_str = ' ' * indent_level
        chunks = []
        current_key = parent_key
        current_lines = []
        chunk_idx = base_idx

        for line in lines:
            stripped = line.rstrip()
            if stripped and not stripped.startswith('#'):
                leading_spaces = len(line) - len(line.lstrip())
                if leading_spaces == indent_level and ':' in stripped:
                    if current_lines:
                        chunk_content = '\n'.join(current_lines).strip()
                        if chunk_content:
                            chunks.append((chunk_content, f"{chunk_idx:03d}", current_key))
                            chunk_idx += 1
                    key_name = stripped.split(':')[0].strip()
                    current_key = f"{parent_key}.{key_name}" if parent_key else key_name
                    current_lines = [line]
                else:
                    current_lines.append(line)
            else:
                current_lines.append(line)

        if current_lines:
            chunk_content = '\n'.join(current_lines).strip()
            if chunk_content:
                chunks.append((chunk_content, f"{chunk_idx:03d}", current_key))

        return chunks

    chunks = []
    try:
        lines = content.split('\n')
        first_pass = split_by_indent(lines, 0, 0, "")
        chunk_idx = 0

        for chunk_content, _, key_path in first_pass:
            if len(chunk_content) <= YAML_MAX_CHUNK:
                header = f"# YAML: {source_file}\n## Section: {key_path or 'root'}\n\n"
                chunks.append((header + chunk_content, f"{chunk_idx:03d}"))
                chunk_idx += 1
            else:
                chunk_lines = chunk_content.split('\n')
                second_pass = split_by_indent(chunk_lines, 2, chunk_idx, key_path)
                for sub_content, _, sub_key in second_pass:
                    header = f"# YAML: {source_file}\n## Section: {sub_key or key_path}\n\n"
                    chunks.append((header + sub_content, f"{chunk_idx:03d}"))
                    chunk_idx += 1

    except Exception:
        header = f"# YAML: {source_file}\n\n"
        chunks.append((header + content, "000"))

    if not chunks:
        header = f"# YAML: {source_file}\n\n"
        chunks.append((header + content, "000"))

    return chunks


def extract_doc_title(filepath: str) -> str:
    filename = filepath.split("/")[-1].replace(".md", "").replace("-", " ")
    return filename.title()


def extract_topic_area(filepath: str) -> str:
    topic_map = {
        "02-consolidation-methods": "Consolidation Methods",
        "03-core-calculations": "Core Calculations",
        "04-elimination": "Elimination Entries",
        "05-currency": "Currency Translation",
        "06-ownership": "Ownership Structure",
        "10-gap-analysis": "Gap Analysis",
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
    if section_title and section_title != doc_title:
        return f"This section covers {section_title.lower()} in the context of {doc_title.lower()} ({topic_area.lower()})."
    else:
        return f"This section covers {doc_title.lower()} ({topic_area.lower()})."


def extract_keywords(content: str) -> list:
    keywords = []
    term_patterns = [
        (r"IFRS\s*\d+", "ifrs"),
        (r"IAS\s*\d+", "ias"),
        (r"global integration", "method"),
        (r"equity method", "method"),
        (r"proportional", "method"),
        (r"full consolidation", "method"),
        (r"goodwill", "concept"),
        (r"minority interest|non-controlling interest|NCI", "concept"),
        (r"elimination", "concept"),
        (r"intercompany", "concept"),
        (r"currency translation", "concept"),
        (r"exchange rate", "concept"),
        (r"deferred tax", "concept"),
        (r"acquisition", "concept"),
        (r"disposal|deconsolidation", "concept"),
    ]

    content_lower = content.lower()
    for pattern, _ in term_patterns:
        matches = re.findall(pattern, content_lower, re.IGNORECASE)
        keywords.extend(matches)

    return list(dict.fromkeys([k.strip().upper() for k in keywords if k.strip()]))[:10]


def generate_summary(content: str, section_title: str) -> str:
    lines = content.strip().split('\n')
    for line in lines:
        line = line.strip()
        if not line:
            continue
        if line.startswith('#') or line.startswith('|') or line.startswith('```'):
            continue
        if any(c in line for c in ['─', '│', '┌', '┐', '└', '┘', '├', '┤', '┬', '┴', '┼', '═', '║']):
            continue
        if line.startswith('-') and len(line) < 50:
            continue
        if len(line) > 50:
            summary = line[:200].rsplit(' ', 1)[0] + '...' if len(line) > 200 else line
            return summary
    return f"Information about {section_title.lower()}."


def extract_related_topics(content: str, topic_area: str) -> list:
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

    if topic_area not in related:
        related.append(topic_area)

    return list(dict.fromkeys(related))[:5]


# Global enhancer instance (lazy loaded)
_llm_enhancer = None


def get_llm_enhancer():
    global _llm_enhancer
    if _llm_enhancer is None:
        from llm_chunk_enhancer import get_enhancer
        _llm_enhancer = get_enhancer()
    return _llm_enhancer


def add_chunk_context(chunk_content: str, source_path: str, chunk_idx: int, total_chunks: int, use_llm: bool = False) -> str:
    doc_title = extract_doc_title(source_path)
    topic_area = extract_topic_area(source_path)
    section_title = extract_title(chunk_content)

    if use_llm:
        enhancer = get_llm_enhancer()
        llm_result = enhancer.enhance_chunk(chunk_content, source_path, topic_area)
        summary = llm_result.get("summary", f"Information about {section_title.lower()}.")
        keywords = llm_result.get("keywords", [])
        concepts = llm_result.get("concepts", [])
        questions = llm_result.get("questions", [])
        related_topics = llm_result.get("related_topics", [topic_area])
    else:
        context_sentence = generate_context_sentence(doc_title, section_title, topic_area)
        summary = generate_summary(chunk_content, section_title)
        keywords = extract_keywords(chunk_content)
        concepts = []
        questions = []
        related_topics = extract_related_topics(chunk_content, topic_area)

    header = f"# {section_title}\n\n"
    header += f"**Summary:** {summary}\n\n"

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

    if keywords:
        header += f"**Keywords:** {', '.join(keywords)}\n\n"

    if concepts:
        header += f"**Concepts:** {', '.join(concepts)}\n\n"

    header += f"## Content\n\n"

    footer = f"\n\n## Related Topics\n\n"
    for topic in related_topics:
        footer += f"- {topic}\n"
    footer += f"\n---\n*Chunk {chunk_idx + 1}/{total_chunks} | {section_title}*\n"

    return header + chunk_content + footer


def create_business_zip(use_llm: bool = False):
    """Create the business-only knowledge base ZIP file."""
    print("=" * 60)
    print("FC Knowledge Base - BUSINESS ONLY ZIP")
    if use_llm:
        print("Mode: LLM-ENHANCED")
    else:
        print("Mode: Rule-based (Fast)")
    print("=" * 60)
    print()
    print("Including:")
    print("  - direct_consolidation_chunks/ (Allen White's book)")
    for folder in BUSINESS_FOLDERS:
        print(f"  - {folder}/")
    print()
    print("Excluding:")
    for folder in TECHNICAL_FOLDERS:
        print(f"  - {folder}/ (technical)")
    print()

    src_chunks = SCRIPT_DIR.parent / "direct_consolidation_chunks"
    src_docs = SCRIPT_DIR.parent / "documentation-library"

    stats = {"pre_chunked": 0, "semantic_chunked": 0, "yaml_files": 0, "skipped_technical": 0}

    with zipfile.ZipFile(ZIP_FILE, "w", zipfile.ZIP_DEFLATED) as zf:

        # Source 1: direct_consolidation_chunks (business - Allen White's book)
        if src_chunks.exists():
            print(f"Processing {src_chunks.name}/ (pre-chunked, as-is)...")
            for f in sorted(src_chunks.glob("*.md")):
                if f.name.upper() == "INDEX.MD":
                    continue
                content = read_file(f)
                if content.strip():
                    flat_name = f"direct_consolidation_chunks_{f.name}"
                    zf.writestr(flat_name, content)
                    stats["pre_chunked"] += 1
            print(f"  Added {stats['pre_chunked']} pre-chunked files")

        # Source 2: documentation-library (filter for business only)
        if src_docs.exists():
            print(f"Processing {src_docs.name}/ (business only, semantic chunking)...")

            for filepath in sorted(src_docs.rglob("*")):
                if not filepath.is_file():
                    continue

                rel_path = filepath.relative_to(src_docs)
                rel_path_str = str(rel_path).replace(os.sep, "_")

                # Skip technical folders
                if not is_business_path(str(rel_path)):
                    stats["skipped_technical"] += 1
                    continue

                # YAML files
                if filepath.suffix in (".yaml", ".yml"):
                    content = read_file(filepath)
                    chunks = semantic_chunk_yaml(content, str(rel_path))

                    for idx, (chunk_content, chunk_suffix) in enumerate(chunks):
                        chunk_with_context = add_chunk_context(
                            chunk_content, str(rel_path), idx, len(chunks), use_llm
                        )
                        if use_llm and (idx + 1) % 10 == 0:
                            print(f"    Enhanced {idx + 1}/{len(chunks)} chunks from {filepath.name}")

                        base_name = rel_path_str.replace(".yaml", "").replace(".yml", "")
                        flat_name = f"documentation-library_{base_name}_chunk{chunk_suffix}.yaml"
                        zf.writestr(flat_name, chunk_with_context)
                        stats["yaml_files"] += 1
                    continue

                # Markdown files
                if filepath.suffix == ".md":
                    content = read_file(filepath)
                    chunks = semantic_chunk_markdown(content, str(rel_path))

                    for idx, (chunk_content, chunk_suffix) in enumerate(chunks):
                        chunk_with_context = add_chunk_context(
                            chunk_content, str(rel_path), idx, len(chunks), use_llm
                        )
                        if use_llm and (idx + 1) % 10 == 0:
                            print(f"    Enhanced {idx + 1}/{len(chunks)} chunks from {filepath.name}")

                        base_name = rel_path_str.replace(".md", "")
                        flat_name = f"documentation-library_{base_name}_chunk{chunk_suffix}.md"
                        zf.writestr(flat_name, chunk_with_context)
                        stats["semantic_chunked"] += 1

            print(f"  Added {stats['semantic_chunked']} semantic chunks from .md files")
            print(f"  Added {stats['yaml_files']} semantic chunks from .yaml files")
            print(f"  Skipped {stats['skipped_technical']} technical files")

        total_files = stats["pre_chunked"] + stats["semantic_chunked"] + stats["yaml_files"]

    print()
    print("=" * 60)
    print(f"Created: {ZIP_FILE.name}")
    print(f"Size: {ZIP_FILE.stat().st_size / 1024 / 1024:.1f} MB")
    print("-" * 60)
    print(f"  Pre-chunked (Allen White book):  {stats['pre_chunked']:,}")
    print(f"  Semantic chunks (markdown):      {stats['semantic_chunked']:,}")
    print(f"  Semantic chunks (yaml):          {stats['yaml_files']:,}")
    print(f"  TOTAL:                           {total_files:,}")
    print(f"  Skipped (technical):             {stats['skipped_technical']:,}")
    print("=" * 60)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Create FC Business-Only Knowledge Base ZIP"
    )
    parser.add_argument(
        "--no-llm",
        action="store_true",
        help="Disable LLM enhancement (faster)"
    )
    args = parser.parse_args()

    use_llm = not args.no_llm

    if use_llm:
        print("\nLLM Enhancement enabled - this produces world-class results\n")
    else:
        print("\nFast mode (no LLM) - rule-based enhancement\n")

    create_business_zip(use_llm=use_llm)
