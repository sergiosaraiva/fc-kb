# RAG Performance Optimization Plan

## Problem Statement

Current RAG responses take 15-60 seconds due to:
1. **Large context size:** 10-15 chunks × ~2500 chars = ~25,000-35,000 chars (~8,000 tokens)
2. **LLM metadata bloat:** Each chunk includes summary, questions, keywords (meant for embedding, not for Claude)
3. **No intelligent selection:** Same amount of context regardless of question complexity or explanation level

## Solution: Smart Summary-Based Retrieval

### Core Insight

LLM-enhanced chunks already contain two useful sections:
- `**Summary:**` - ~100-200 chars, captures essence
- `## Content` - ~1000-2000 chars, full detail

**Use summaries by default, full content selectively.**

---

## Implementation Phases

### Phase 1: Extract Summary Function

**File:** `app.py` (and `mcp-server.py`)

Add function to extract just the summary from LLM-enhanced chunks:

```python
def extract_summary_only(chunk_text: str) -> str:
    """
    Extract only the summary from LLM-enhanced chunks.
    Returns ~100-200 chars vs ~2000+ for full content.
    """
    import re

    # Try to find the Summary field
    summary_match = re.search(r'\*\*Summary:\*\*\s*(.+?)(?=\n\n|\n##)', chunk_text, re.DOTALL)
    if summary_match:
        return summary_match.group(1).strip()

    # Fallback: first 200 chars of content
    content = extract_content_only(chunk_text)
    return content[:200] + "..." if len(content) > 200 else content
```

**Effort:** 30 minutes
**Risk:** Low

---

### Phase 2: Intelligent Context Builder

**File:** `app.py`

Replace current context building with smart selection:

```python
def build_smart_context(results: List[Dict], explanation_level: str, model_tier: str) -> str:
    """
    Build context intelligently based on mode and tier.

    Strategy:
    - Executive Summary: Summaries only (fast)
    - Standard: Summaries + top 2-3 full content
    - Detailed: Summaries + top 5 full content
    """

    # Configuration based on mode
    config = {
        "Executive Summary": {"max_chunks": 5, "full_content_count": 0},
        "Standard": {"max_chunks": 8, "full_content_count": 3},
        "Detailed": {"max_chunks": 12, "full_content_count": 5},
    }

    settings = config.get(explanation_level, config["Standard"])

    # Further reduce for "Good" tier (speed priority)
    if model_tier == "Good":
        settings["full_content_count"] = min(settings["full_content_count"], 1)

    context_parts = []

    for i, result in enumerate(results[:settings["max_chunks"]]):
        source = result["metadata"].get("source", "Unknown")

        if i < settings["full_content_count"]:
            # Top results get full content
            content = extract_content_only(result["content"])
            context_parts.append(f"[Source {i+1}: {source}]\n{content}")
        else:
            # Remaining results get summary only
            summary = extract_summary_only(result["content"])
            context_parts.append(f"[Source {i+1}: {source}] {summary}")

    return "\n\n---\n\n".join(context_parts)
```

**Effort:** 1-2 hours
**Risk:** Medium (need to test quality of answers)

---

### Phase 3: Token Budget System

**File:** `app.py`

Implement a token budget approach instead of fixed chunk counts:

```python
# Configuration
TOKEN_BUDGETS = {
    "Executive Summary": {"context": 1000, "output": 800},   # ~4K chars context
    "Standard": {"context": 3000, "output": 2000},           # ~12K chars context
    "Detailed": {"context": 6000, "output": 4000},           # ~24K chars context
}

def build_context_with_budget(results: List[Dict], explanation_level: str) -> str:
    """
    Build context up to a token budget.
    Prioritizes summaries, adds full content only if budget allows.
    """
    budget = TOKEN_BUDGETS.get(explanation_level, TOKEN_BUDGETS["Standard"])
    char_budget = budget["context"] * 4  # ~4 chars per token

    context_parts = []
    chars_used = 0

    # First pass: add all summaries (cheap)
    for i, result in enumerate(results):
        summary = extract_summary_only(result["content"])
        source = result["metadata"].get("source", "Unknown")
        entry = f"[{i+1}. {source}] {summary}"

        if chars_used + len(entry) > char_budget:
            break

        context_parts.append({"index": i, "entry": entry, "has_full": False})
        chars_used += len(entry)

    # Second pass: upgrade top results to full content if budget allows
    for item in context_parts[:3]:  # Top 3 candidates
        result = results[item["index"]]
        full_content = extract_content_only(result["content"])
        additional_chars = len(full_content) - len(extract_summary_only(result["content"]))

        if chars_used + additional_chars <= char_budget:
            source = result["metadata"].get("source", "Unknown")
            item["entry"] = f"[{item['index']+1}. {source}]\n{full_content}"
            item["has_full"] = True
            chars_used += additional_chars

    return "\n\n---\n\n".join([item["entry"] for item in context_parts])
```

**Effort:** 2-3 hours
**Risk:** Medium

---

### Phase 4: Apply to MCP Server

**File:** `mcp-server.py`

Apply same optimizations to the MCP server for Claude Code usage:

```python
def format_results_smart(results: List[Dict], max_chars: int = 8000) -> str:
    """
    Format results with smart truncation.
    Uses summaries by default, full content for top results.
    """
    response_parts = []
    chars_used = 0

    for i, r in enumerate(results):
        source = r["metadata"].get("source", "Unknown")
        relevance = r["relevance"]

        # Top 3 results: full content, rest: summaries
        if i < 3:
            content = extract_content_only(r["content"])
        else:
            content = extract_summary_only(r["content"])

        entry = f"### Result {i+1} (Relevance: {relevance:.1%})\n"
        entry += f"**Source**: {source}\n\n{content}\n\n---\n"

        if chars_used + len(entry) > max_chars:
            break

        response_parts.append(entry)
        chars_used += len(entry)

    return "\n".join(response_parts)
```

**Effort:** 1 hour
**Risk:** Low

---

### Phase 5: UI Feedback for Speed

**File:** `app.py`

Add visual feedback showing context size and expected speed:

```python
# Show context stats to user
st.caption(f"Context: {len(context)//1000}K chars (~{len(context)//4} tokens) | "
           f"Chunks: {chunks_used} ({full_content_count} full, {summary_count} summaries)")
```

**Effort:** 30 minutes
**Risk:** None

---

## Expected Results

| Mode | Current | Optimized | Improvement |
|------|---------|-----------|-------------|
| Executive Summary | ~25K chars, 15-30s | ~2K chars, 3-8s | **4-5x faster** |
| Standard | ~30K chars, 20-40s | ~8K chars, 8-15s | **2-3x faster** |
| Detailed | ~35K chars, 30-60s | ~15K chars, 15-25s | **2x faster** |

---

## Testing Checklist

- [ ] Executive Summary answers are still accurate with summaries only
- [ ] Standard mode maintains answer quality with hybrid approach
- [ ] Detailed mode provides comprehensive answers
- [ ] MCP server responses are faster and still useful
- [ ] No regression in answer quality for complex questions
- [ ] Edge cases: questions requiring info from multiple chunks

---

## Rollback Plan

If quality suffers:
1. Increase `full_content_count` for each mode
2. Increase token budgets
3. Revert to full content extraction (current state)

All changes are in context building, not in the knowledge base itself.

---

## Alternative: Regenerate with Smaller Chunks

If summary approach is insufficient, consider regenerating knowledge base:

**Changes to `create-knowledge-zip.py`:**
```python
TARGET_CHUNK_SIZE = 600   # Down from 1200
MAX_CHUNK_SIZE = 1000     # Down from 2000
```

**Pros:** More focused chunks
**Cons:** 3-4 hour regeneration, might need more chunks per query

**Recommendation:** Try summary approach first (no regeneration needed).

---

## Implementation Order

1. **Phase 1** - Extract summary function (30 min) - Foundation
2. **Phase 2** - Smart context builder (2 hr) - Main impact
3. **Phase 5** - UI feedback (30 min) - User visibility
4. **Phase 3** - Token budget (2-3 hr) - Refinement
5. **Phase 4** - MCP server (1 hr) - Consistency

**Total estimated effort:** 5-7 hours

---

## Notes

- No knowledge base regeneration required
- All changes are in how we BUILD context, not how we STORE it
- LLM metadata (summaries, questions, keywords) remains valuable for embeddings
- Can be implemented incrementally and tested at each phase
