# UI-to-Theory Bridge

## Overview

This folder bridges the gap between **what users see in the product UI** and **the underlying consolidation theory**. Users often know the screen names and field labels but need to understand the theoretical concepts behind them.

## Document Index

| Document | Purpose |
|----------|---------|
| [screen-glossary.md](screen-glossary.md) | What each screen does and its theoretical basis |
| [field-definitions.md](field-definitions.md) | Field labels mapped to technical terms |
| [workflow-theory-map.md](workflow-theory-map.md) | User workflows mapped to theoretical processes |

## Quick Reference: Screen to Theory

### Data Entry Screens

| Screen | Navigation | Theory Concept |
|--------|------------|----------------|
| Bundles | Data Entry > Bundles | Local subsidiary financial data |
| Local Adjustments | Data Entry > Local Adjustments | Pre-consolidation adjustments |
| Intercompany Entry | Data Entry > Intercompany | IC transaction recording |

### Group Management Screens

| Screen | Navigation | Theory Concept |
|--------|------------|----------------|
| Companies | Group > Companies | Legal entity management |
| Group Structure | Group > Group Structure | Ownership chain definition |
| Exchange Rates | Group > Exchange Rates | Currency translation rates |
| Scope | Group > Scope | Consolidation perimeter |

### Consolidation Screens

| Screen | Navigation | Theory Concept |
|--------|------------|----------------|
| Statusboard | Consolidation > Statusboard | Consolidation status tracking |
| Integrate Bundles | Consolidation > Integrate Bundles | Bundle aggregation |
| Integrate Adjustments | Consolidation > Integrate Adjustments | Adjustment posting |
| Eliminations | Consolidation > Eliminations | Elimination entries |
| IC Matching | Consolidation > IC Matching | Intercompany reconciliation |
| Events | Consolidation > Events | Acquisition/disposal events |

### Reports Screens

| Screen | Navigation | Theory Concept |
|--------|------------|----------------|
| Standard Reports | Reports > Standard | Statutory consolidation reports |
| Consolidation Reports | Reports > Consolidation | Elimination and adjustment detail |
| Analysis Reports | Reports > Analysis | Management reporting |

## Key Terminology Mapping

| UI Term | Technical Term | Theory Concept |
|---------|---------------|----------------|
| Bundle | Local Package | Subsidiary trial balance |
| Conso | Consolidation | Combination of group results |
| IC | Intercompany | Transactions between group entities |
| T-Journal | Consolidation Journal | Elimination entry record |
| S-Code | Elimination Code | Elimination type identifier |
| Flow | Cash Flow Movement | Balance sheet movement |
| Scope | Consolidation Perimeter | Entities included in consolidation |

## Usage for RAG System

When a user asks a question using UI terminology:

1. **Identify UI terms** in the question
2. **Map to theory concepts** using this bridge
3. **Retrieve relevant help content** AND theory chunks
4. **Answer using familiar UI terms** with theory explanation

### Example

**User Question**: "What is the Bundle checkbox for?"

**Mapping Process**:
1. UI Term: "Bundle checkbox" → Screen: Statusboard
2. Theory: Bundle = Local subsidiary financial data
3. Checkbox meaning: Indicates modification requiring re-consolidation

**Answer**: "The Bundle checkbox on the Statusboard indicates that changes have been made to the subsidiary's local financial data (called a 'Bundle' in the product). When checked, it signals that you need to run the Bundle Integration process to incorporate these changes into the consolidated results."

---

*UI-to-Theory Bridge | Version 1.0 | Last Updated: 2024-12-03*
