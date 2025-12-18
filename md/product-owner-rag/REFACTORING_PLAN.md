# App.py Refactoring Plan

## Goal
Break `app.py` (~2100 lines) into smaller, maintainable modules while keeping the app functional after each step.

## Guiding Principles
1. **One step at a time** - Complete and test each step before moving to the next
2. **No functionality changes** - Pure refactoring, behavior stays identical
3. **Backward compatible imports** - Old imports continue to work during transition
4. **Test after each step** - Run the app and verify it works

---

## Step-by-Step Plan

### Phase 1: Zero-Risk Extractions (No behavior change possible)

#### Step 1: Extract Prompts to `prompts.py`
**Risk: VERY LOW** | **Impact: HIGH** | **Lines removed: ~400**

Extract all system prompt strings. These are pure string constants with no logic.

**What to extract:**
- `level_instructions` dict (lines 683-734)
- Executive Summary system prompt (lines 740-751)
- Main system prompt template (lines 754-967)
- Follow-up questions prompt (lines 1236-1250)
- Quiz generation prompt (lines 1380-1408)
- Related topics prompt (lines 1447-1465)
- Glossary prompt (lines 1518-1535)
- Autocomplete prompt (lines 1586-1600)
- Learning path prompt (lines 1670-1693)

**New file:** `prompts.py`
```python
# All prompt constants
LEVEL_INSTRUCTIONS = {...}
EXECUTIVE_SUMMARY_PROMPT = "..."
MAIN_SYSTEM_PROMPT = "..."
# etc.
```

**Change in app.py:**
```python
from prompts import LEVEL_INSTRUCTIONS, EXECUTIVE_SUMMARY_PROMPT, ...
```

**Test:** Run app, ask a question, verify response format is identical.

---

#### Step 2: Extract JavaScript to `ui/components.py`
**Risk: VERY LOW** | **Impact: MEDIUM** | **Lines removed: ~150**

Extract the large JavaScript string block used for keyboard shortcuts and localStorage.

**What to extract:**
- `keyboard_shortcuts_js` string (lines 1897-2100+)

**New file:** `ui/__init__.py` + `ui/components.py`
```python
KEYBOARD_SHORTCUTS_JS = """..."""
```

**Change in app.py:**
```python
from ui.components import KEYBOARD_SHORTCUTS_JS
```

**Test:** Run app, verify Ctrl+K focuses search, localStorage saves history.

---

### Phase 2: Low-Risk Service Extractions

#### Step 3: Extract Bedrock Client to `services/bedrock_service.py`
**Risk: LOW** | **Impact: MEDIUM** | **Lines removed: ~30**

Extract AWS Bedrock client initialization. This is a stateless factory function.

**What to extract:**
- `get_bedrock_client()` function (lines 539-563)

**New file:** `services/__init__.py` + `services/bedrock_service.py`
```python
import boto3
from botocore.config import Config

def get_bedrock_client():
    ...
```

**Change in app.py:**
```python
from services.bedrock_service import get_bedrock_client
```

**Test:** Run app, ask a question, verify Claude responds.

---

#### Step 4: Extract ChromaDB Service to `services/chroma_service.py`
**Risk: LOW** | **Impact: MEDIUM** | **Lines removed: ~150**

Extract ChromaDB client and search functions.

**What to extract:**
- `get_chroma_client()` (lines 514-537)
- `get_embeddings()` (lines 565-568)
- `search_business_layer()` (lines 570-653)
- `extract_content_only()` (lines 87-130) - utility used by search

**New file:** `services/chroma_service.py`
```python
from config import CHROMADB_HOST, CHROMADB_PORT, ...
from titan_v1_embeddings import get_embedding_function

def get_chroma_client(): ...
def get_embeddings(): ...
def search_business_layer(): ...
def extract_content_only(): ...
```

**Change in app.py:**
```python
from services.chroma_service import search_business_layer, extract_content_only
```

**Test:** Run app, search for "goodwill", verify results appear.

---

### Phase 3: Medium-Risk Service Extractions

#### Step 5: Extract LLM Service to `services/llm_service.py`
**Risk: MEDIUM** | **Impact: HIGH** | **Lines removed: ~600**

This is the largest extraction. Extract all Claude LLM interaction functions.

**What to extract:**
- `generate_answer_with_claude()` (lines 655-1064)
- `generate_answer_streaming()` (lines 1066-1217)
- `get_source_tier()` (lines 1219-1236)

**Dependencies:**
- Needs `get_bedrock_client` from `services/bedrock_service.py`
- Needs prompts from `prompts.py`
- Needs config constants

**New file:** `services/llm_service.py`
```python
from services.bedrock_service import get_bedrock_client
from prompts import LEVEL_INSTRUCTIONS, ...
from config import MODEL_TIERS, TEMPERATURE, ...

def generate_answer_with_claude(): ...
def generate_answer_streaming(): ...
def get_source_tier(): ...
```

**Change in app.py:**
```python
from services.llm_service import generate_answer_with_claude, generate_answer_streaming
```

**Test:**
- Ask a question with each explanation level (Executive, Standard, Detailed)
- Test streaming responses
- Verify source citations appear correctly

---

#### Step 6: Extract Quiz Service to `services/quiz_service.py`
**Risk: MEDIUM** | **Impact: LOW** | **Lines removed: ~120**

Extract quiz generation functions.

**What to extract:**
- `generate_quiz_questions_rag()` (lines 1338-1446)

**New file:** `services/quiz_service.py`
```python
from services.bedrock_service import get_bedrock_client
from services.chroma_service import search_business_layer
from prompts import QUIZ_PROMPT

def generate_quiz_questions_rag(): ...
```

**Test:** Use the Quiz feature, verify questions generate correctly.

---

#### Step 7: Extract Learning Service to `services/learning_service.py`
**Risk: MEDIUM** | **Impact: LOW** | **Lines removed: ~350**

Extract learning-related functions.

**What to extract:**
- `generate_follow_up_questions()` (lines 1238-1294)
- `get_fallback_follow_ups()` (lines 1296-1336)
- `generate_related_topics_rag()` (lines 1448-1502)
- `generate_glossary_terms_rag()` (lines 1504-1574)
- `generate_autocomplete_suggestions_rag()` (lines 1576-1638)
- `generate_learning_path_topics_rag()` (lines 1640-1731)
- `get_related_topics()` (lines 1733-1846)

**New file:** `services/learning_service.py`

**Test:**
- Verify follow-up questions appear after answers
- Test learning paths feature
- Test autocomplete suggestions

---

### Phase 4: Final Cleanup

#### Step 8: Move Model Configuration to `config.py`
**Risk: LOW** | **Impact: LOW** | **Lines removed: ~30**

Move model tier configuration to centralized config.

**What to move:**
- `MODEL_TIERS` dict (lines 57-73)
- `CLAUDE_FAST_MODEL_ID` (line 74)
- `DEFAULT_MODEL_TIER` (line 75)
- `TEMPERATURE` (line 76)
- `DEFAULT_KNOWLEDGE_MODE` (line 79)
- Retrieval config constants (lines 82-84)

**Test:** Verify model selection dropdown works, responses use correct model.

---

#### Step 9: Clean Up app.py
**Risk: LOW** | **Impact: HIGH**

Final cleanup of `app.py`:
- Remove all extracted code
- Organize remaining imports
- Add docstrings
- Verify all features work

**Final app.py structure (~400 lines):**
```python
"""Product Owner RAG - Main Streamlit Application"""
import streamlit as st
from services.chroma_service import search_business_layer
from services.llm_service import generate_answer_with_claude, generate_answer_streaming
from services.learning_service import generate_follow_up_questions, ...
from services.quiz_service import generate_quiz_questions_rag
from ui.components import KEYBOARD_SHORTCUTS_JS
from prompts import ...
from config import ...

def main():
    # All UI code stays here
    ...

if __name__ == "__main__":
    main()
```

---

## Final File Structure

```
md/product-owner-rag/
├── app.py                      # ~400 lines (UI only)
├── config.py                   # ~80 lines (all configuration)
├── prompts.py                  # ~400 lines (all LLM prompts)
├── titan_v1_embeddings.py      # Unchanged
├── services/
│   ├── __init__.py
│   ├── bedrock_service.py      # ~50 lines
│   ├── chroma_service.py       # ~180 lines
│   ├── llm_service.py          # ~600 lines
│   ├── quiz_service.py         # ~120 lines
│   └── learning_service.py     # ~350 lines
└── ui/
    ├── __init__.py
    └── components.py           # ~200 lines
```

---

## Execution Checklist

| Step | Description | Risk | Test Command | Status |
|------|-------------|------|--------------|--------|
| 1 | Extract prompts.py | VERY LOW | `streamlit run app.py` + ask question | [x] DONE |
| 2 | Extract ui/components.py | VERY LOW | Test Ctrl+K shortcut | [x] DONE |
| 3 | Extract bedrock_service.py | LOW | Ask question, verify response | [x] DONE |
| 4 | Extract chroma_service.py | LOW | Search, verify results | [x] DONE |
| 5 | Extract llm_service.py | MEDIUM | Test all explanation levels | [ ] |
| 6 | Extract quiz_service.py | MEDIUM | Generate quiz | [ ] |
| 7 | Extract learning_service.py | MEDIUM | Test follow-ups, learning paths | [ ] |
| 8 | Move config to config.py | LOW | Test model selection | [ ] |
| 9 | Final cleanup | LOW | Full regression test | [ ] |

---

## Rollback Strategy

If any step breaks the app:
1. `git checkout app.py` to restore original
2. Delete newly created files
3. Investigate issue before retrying

## Time Estimate

- Steps 1-2: ~30 minutes each
- Steps 3-4: ~45 minutes each
- Steps 5-7: ~1 hour each
- Steps 8-9: ~30 minutes each

**Total: ~6-8 hours** (with testing between steps)
