# Help Content Knowledge Base

## Overview

This folder contains 27 converted help files from the Prophix.Conso product documentation, organized for RAG (Retrieval-Augmented Generation) system consumption. Each file has been enhanced with merged Q&A pairs for improved searchability and answer retrieval.

## Contents by Workflow Phase

### Overview & Getting Started
| File | Topic | Q&A Pairs |
|------|-------|-----------|
| `0101-financial-consolidation-overview.md` | Financial consolidation fundamentals | High-level concepts |
| `0102-getting-started.md` | Initial setup and orientation | Navigation basics |
| `0210-basics.md` | Core terminology and concepts | Foundation knowledge |

### Setup & Configuration
| File | Topic | Q&A Pairs |
|------|-------|-----------|
| `0301-select-a-consolidation-period.md` | Period selection and management | Period configuration |
| `0303-input-the-currency-rates.md` | Currency rate entry and types | Rate types (CC/AC/MC) |
| `0306-input-the-consolidation-scope.md` | Scope definition and company inclusion | Perimeter management |
| `0309-local-amounts.md` | Local currency data entry | Source data handling |

### Data Entry & Adjustments
| File | Topic | Q&A Pairs |
|------|-------|-----------|
| `0312-local-adjustments.md` | Local-level adjustments | Pre-consolidation adjustments |
| `0314-manual-data-entry.md` | Manual data input processes | Direct data entry |
| `0321-use-excel-consolidation-bundles.md` | Excel bundle workflows | Bundle import/export |
| `0325-import-export-data.md` | Data import/export operations | Data transfer |

### Validation & Reconciliation
| File | Topic | Q&A Pairs |
|------|-------|-----------|
| `0332-bundle-validation.md` | Data validation rules | Validation checks |
| `0340-reconcile-intercompany-data.md` | IC reconciliation process | IC matching |

### Consolidation Processing
| File | Topic | Q&A Pairs |
|------|-------|-----------|
| `0350-introduce-the-consolidation-adjustments.md` | Consolidation adjustments | Group-level adjustments |
| `0360-generate-the-consolidation-events.md` | Event generation | Ownership events |
| `0370-consolidate.md` | Consolidation execution | Main process |
| `0380-check-and-justify-the-consolidated-equity.md` | Equity reconciliation | Proof of equity |

### Reporting
| File | Topic | Q&A Pairs |
|------|-------|-----------|
| `0390-standard-reports.md` | Standard report types | Out-of-box reports |
| `0391-consolidation-reports.md` | Consolidation-specific reports | Group reports |
| `0392-user-reports.md` | Custom user reports | Report customization |
| `0393-analysis-reports.md` | Analysis and drill-down | Analytical tools |
| `0394-pivot-reports.md` | Pivot table reports | Multi-dimensional analysis |
| `0395-additional-reports.md` | Additional report types | Specialized reports |
| `0398-use-the-general-ledger-of-accounts.md` | GL account navigation | Account ledger |
| `0399-use-the-general-ledger-of-the-flows.md` | GL flow navigation | Flow ledger |

### Reference
| File | Topic | Q&A Pairs |
|------|-------|-----------|
| `0510-faq.md` | Frequently asked questions | Common queries |

## Statistics

| Metric | Value |
|--------|-------|
| Total Files | 27 |
| Total Q&A Pairs | 2,125 (deduplicated) |
| Workflow Phases Covered | 7 |
| IFRS References | Cross-linked throughout |

## Usage for RAG System

### Retrieval Strategy

1. **Question Classification**: Identify question type (how-to, what-is, troubleshooting)
2. **Keyword Extraction**: Match UI terms, process names, IFRS references
3. **File Selection**: Route to appropriate help file based on workflow phase
4. **Answer Assembly**: Combine help content with discrepancy mapping if needed

### Example Queries

| Query | Primary File |
|-------|--------------|
| "How do I run a consolidation?" | `0370-consolidate.md` |
| "What are bundle validation rules?" | `0332-bundle-validation.md` |
| "How to enter currency rates?" | `0303-input-the-currency-rates.md` |
| "What reports are available?" | `0390-standard-reports.md` |

## Related Documentation

- [Parent README](../_index-user-knowledge-base.md) - User knowledge base overview
- [Help Index](../help-index.md) - Master index with question routing
- [Help Metadata](../help-metadata.yaml) - RAG retrieval configuration
- [Discrepancy Mapping](../discrepancy-mapping/) - Theory vs product differences
- [UI-to-Theory Bridge](../ui-to-theory/) - Screen and field definitions

---

*Help Content Knowledge Base | Version 1.0 | Last Updated: 2024-12-05*
