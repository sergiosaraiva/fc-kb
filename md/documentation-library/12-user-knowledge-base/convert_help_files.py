#!/usr/bin/env python3
"""
Help File Converter for PATH D Knowledge Base

This script converts the help files from docs/DC/help/ into markdown format
suitable for RAG retrieval. It:
1. Parses content and Q&A files
2. Deduplicates Q&A pairs
3. Generates markdown with proper structure
4. Adds theory references and related documentation links

Usage:
    python convert_help_files.py

The script expects:
- Content files: {index} - {title}.txt
- Q&A files: {index} - {title} - QA.txt

Output:
- Markdown files in help-content/ folder
"""

import os
import re
from pathlib import Path
from collections import OrderedDict

# Configuration
HELP_SOURCE_DIR = Path(__file__).parent.parent.parent.parent / "help"
OUTPUT_DIR = Path(__file__).parent / "help-content"

# Theory reference mapping (index -> theory reference)
THEORY_REFS = {
    "0101": "Allen White 'Direct Consolidation' - Chapters 1-3",
    "0102": None,  # Getting started - no direct theory
    "0210": None,  # Basics - no direct theory
    "0301": "Reporting Periods",
    "0303": "IAS 21 (Foreign Exchange)",
    "0306": "IFRS 10 (Consolidation Scope), IAS 27",
    "0309": None,
    "0312": "Pre-consolidation Adjustments",
    "0314": None,
    "0321": None,
    "0325": None,
    "0332": "Data Validation",
    "0340": "Intercompany Eliminations",
    "0350": "Consolidation Adjustments",
    "0360": "IFRS 3 (Business Combinations), Consolidation Events",
    "0370": "Direct Consolidation - Chapters 8-12",
    "0380": "Equity Roll-Forward, IFRS 10",
    "0390": "Consolidated Financial Statements",
    "0391": "Elimination Reporting",
    "0392": None,
    "0393": None,
    "0394": None,
    "0395": None,
    "0398": None,
    "0399": "Cash Flow (IAS 7)",
    "0510": None,
}

# Category mapping (index -> category)
CATEGORIES = {
    "0101": "Overview",
    "0102": "Overview",
    "0210": "Foundation",
    "0301": "Setup",
    "0303": "Setup",
    "0306": "Setup",
    "0309": "Setup",
    "0312": "Data Entry",
    "0314": "Data Entry",
    "0321": "Data Entry",
    "0325": "Data Entry",
    "0332": "Validation",
    "0340": "Validation",
    "0350": "Processing",
    "0360": "Processing",
    "0370": "Processing",
    "0380": "Processing",
    "0390": "Reporting",
    "0391": "Reporting",
    "0392": "Reporting",
    "0393": "Reporting",
    "0394": "Reporting",
    "0395": "Reporting",
    "0398": "Reporting",
    "0399": "Reporting",
    "0510": "Reference",
}


def parse_help_file(content_text):
    """Parse a help content file and extract structured data."""
    sections = {
        "topics": "",
        "keywords": "",
        "summary": "",
        "contents": ""
    }

    current_section = None
    content_lines = []

    for line in content_text.split('\n'):
        line = line.strip()

        if line.startswith("Topics:"):
            current_section = "topics"
            sections["topics"] = line[7:].strip()
        elif line.startswith("Keywords:"):
            current_section = "keywords"
            sections["keywords"] = line[9:].strip()
        elif line.startswith("Summary:"):
            current_section = "summary"
            sections["summary"] = line[8:].strip()
        elif line.startswith("Contents:"):
            current_section = "contents"
        elif current_section == "contents":
            content_lines.append(line)
        elif current_section in ["topics", "keywords", "summary"] and line:
            sections[current_section] += " " + line

    sections["contents"] = "\n".join(content_lines).strip()

    return sections


def parse_qa_file(qa_text):
    """Parse a Q&A file and extract question-answer pairs."""
    qa_pairs = []
    current_question = None

    for line in qa_text.split('\n'):
        line = line.strip()

        if line.startswith("Question:"):
            current_question = line[9:].strip()
        elif line.startswith("Answer:") and current_question:
            answer = line[7:].strip()
            qa_pairs.append((current_question, answer))
            current_question = None

    return qa_pairs


def deduplicate_qa(qa_pairs):
    """Remove duplicate Q&A pairs, keeping first occurrence."""
    seen_questions = set()
    deduplicated = []

    for question, answer in qa_pairs:
        # Normalize question for comparison
        normalized = question.lower().strip().rstrip('?')

        if normalized not in seen_questions:
            seen_questions.add(normalized)
            deduplicated.append((question, answer))

    return deduplicated


def categorize_qa(qa_pairs):
    """Group Q&A pairs by topic/category for better organization."""
    categories = OrderedDict()

    for question, answer in qa_pairs:
        # Simple categorization based on keywords
        q_lower = question.lower()

        if any(word in q_lower for word in ["access", "navigate", "where"]):
            cat = "Navigation"
        elif any(word in q_lower for word in ["what is", "what does", "indicate", "mean"]):
            cat = "Concepts"
        elif any(word in q_lower for word in ["how do", "how to", "steps"]):
            cat = "How-To"
        else:
            cat = "General"

        if cat not in categories:
            categories[cat] = []
        categories[cat].append((question, answer))

    return categories


def generate_markdown(index, title, sections, qa_pairs, theory_ref, category):
    """Generate markdown content from parsed data."""
    md_lines = [f"# {title}", ""]

    # Metadata section
    md_lines.extend([
        "## Metadata",
        f"- **Index**: {index}",
        f"- **Topics**: {sections['topics']}",
        f"- **Keywords**: {sections['keywords']}"
    ])

    if theory_ref:
        md_lines.append(f"- **Theory Reference**: {theory_ref}")

    md_lines.extend(["", "## Summary", "", sections['summary'], ""])

    # Main content
    md_lines.extend(["---", "", "## User Guide", ""])

    # Process contents - add markdown formatting
    contents = sections['contents']
    # Convert numbered lists
    contents = re.sub(r'^(\d+)\.\s+', r'\1. ', contents, flags=re.MULTILINE)
    # Convert bullet points
    contents = re.sub(r'^-\s+', r'- ', contents, flags=re.MULTILINE)

    md_lines.extend([contents, ""])

    # Q&A section
    if qa_pairs:
        categorized = categorize_qa(qa_pairs)

        md_lines.extend(["---", "", "## Frequently Asked Questions", ""])

        for cat_name, pairs in categorized.items():
            md_lines.extend([f"### {cat_name}", ""])

            for question, answer in pairs:
                md_lines.extend([
                    f"**{question}**",
                    answer,
                    ""
                ])

    # Footer
    md_lines.extend([
        "---",
        "",
        f"*Help Topic {index} | Category: {category} | Last Updated: 2024-12-03*"
    ])

    return "\n".join(md_lines)


def convert_file_pair(content_file, qa_file, output_dir):
    """Convert a pair of content and Q&A files to markdown."""
    # Extract index and title from filename
    filename = content_file.stem
    match = re.match(r"(\d{4})\s*-\s*(.+)", filename)

    if not match:
        print(f"  Skipping: {filename} (invalid format)")
        return None

    index = match.group(1)
    title = match.group(2).strip()

    # Read content file
    with open(content_file, 'r', encoding='utf-8') as f:
        content_text = f.read()

    sections = parse_help_file(content_text)

    # Read Q&A file if exists
    qa_pairs = []
    if qa_file and qa_file.exists():
        with open(qa_file, 'r', encoding='utf-8') as f:
            qa_text = f.read()
        qa_pairs = parse_qa_file(qa_text)
        qa_pairs = deduplicate_qa(qa_pairs)

    # Get theory reference and category
    theory_ref = THEORY_REFS.get(index)
    category = CATEGORIES.get(index, "General")

    # Generate markdown
    markdown = generate_markdown(index, title, sections, qa_pairs, theory_ref, category)

    # Write output file
    output_filename = f"{index}-{title.lower().replace(' ', '-').replace('/', '-')}.md"
    output_path = output_dir / output_filename

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(markdown)

    return {
        "index": index,
        "title": title,
        "output": output_filename,
        "qa_count": len(qa_pairs),
        "category": category
    }


def main():
    """Main conversion process."""
    print("=" * 60)
    print("Help File Converter for PATH D Knowledge Base")
    print("=" * 60)

    # Ensure output directory exists
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Find all content files
    content_files = sorted(HELP_SOURCE_DIR.glob("*.txt"))
    content_files = [f for f in content_files if "- QA" not in f.name]

    print(f"\nFound {len(content_files)} content files in {HELP_SOURCE_DIR}")
    print(f"Output directory: {OUTPUT_DIR}\n")

    results = []

    for content_file in content_files:
        # Find matching Q&A file
        qa_filename = content_file.stem + " - QA.txt"
        qa_file = content_file.parent / qa_filename

        print(f"Processing: {content_file.name}")

        result = convert_file_pair(content_file, qa_file, OUTPUT_DIR)

        if result:
            results.append(result)
            print(f"  -> {result['output']} ({result['qa_count']} Q&A pairs)")

    # Summary
    print("\n" + "=" * 60)
    print("CONVERSION SUMMARY")
    print("=" * 60)
    print(f"Files converted: {len(results)}")
    print(f"Total Q&A pairs: {sum(r['qa_count'] for r in results)}")

    print("\nBy category:")
    categories = {}
    for r in results:
        cat = r['category']
        categories[cat] = categories.get(cat, 0) + 1

    for cat, count in sorted(categories.items()):
        print(f"  {cat}: {count}")

    print("\n" + "=" * 60)
    print("Conversion complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()
