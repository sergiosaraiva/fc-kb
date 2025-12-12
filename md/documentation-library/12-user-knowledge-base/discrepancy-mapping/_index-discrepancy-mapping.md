# Discrepancy Mapping: Theory vs Product

## Overview

This folder documents the differences between **Allen White's "Direct Consolidation" theoretical framework** and **Prophix.Conso's actual implementation**. Understanding these discrepancies is crucial for:

- **Consultants**: Setting correct expectations during implementation
- **Consolidators**: Understanding why results may differ from textbook examples
- **Auditors**: Validating that discrepancies are documented and intentional

## Why Discrepancies Exist

Prophix.Conso is a production software system that must balance:

1. **Theoretical Purity** - Following consolidation standards accurately
2. **Practical Usability** - Simplifying complex workflows for users
3. **Performance** - Processing large groups efficiently
4. **Flexibility** - Accommodating diverse customer requirements
5. **Maintainability** - Keeping code manageable over time

These trade-offs result in intentional simplifications and variations from pure theory.

## Document Index

| Document | Focus Area | Key Discrepancies |
|----------|------------|-------------------|
| [theory-vs-product-overview.md](theory-vs-product-overview.md) | Executive summary | High-level differences |
| [elimination-differences.md](elimination-differences.md) | Elimination entries | S-codes, execution order, IC handling |
| [ownership-differences.md](ownership-differences.md) | Ownership calculations | Circular ownership, method determination |
| [currency-differences.md](currency-differences.md) | Currency translation | Rate types, translation adjustments |
| [simplifications-summary.md](simplifications-summary.md) | Simplifications | What theory covers that product doesn't |

## Quick Reference: Major Discrepancies

### 1. Consolidation Method Determination

| Aspect | Theory (Allen White) | Product (Prophix.Conso) |
|--------|---------------------|------------------------|
| Method Options | Global, Proportional, Equity, Not Consolidated | G, P, E, N (same codes) |
| Determination | Complex voting rights analysis | Simplified percentage thresholds |
| Override | N/A | Manual override allowed |

### 2. Elimination Processing

| Aspect | Theory | Product |
|--------|--------|---------|
| Sequence | Multi-pass with dependencies | Single-pass with S-code ordering |
| IC Matching | Full reconciliation required | Threshold-based tolerance |
| Goodwill | Detailed fair value allocation | Simplified calculation |

### 3. Ownership Calculations

| Aspect | Theory | Product |
|--------|--------|---------|
| Circular Ownership | Complex iterative algorithm | Simplified handling |
| Indirect Holdings | Full chain calculation | Pre-calculated percentages |
| Treasury Shares | Detailed treatment | Simplified deduction |

### 4. Currency Translation

| Aspect | Theory | Product |
|--------|--------|---------|
| Rate Types | Many specific rates | CC, AC, MC, HC |
| Translation Method | Current rate vs Temporal | Current rate primary |
| Hyperinflation | IAS 29 detailed rules | Simplified adjustment |

## How to Use This Documentation

### For Consultants

1. **During Sales/Scoping**: Reference [simplifications-summary.md](simplifications-summary.md) to set expectations
2. **During Implementation**: Use specific discrepancy docs to explain product behavior
3. **During Training**: Highlight where UI terms differ from textbook terms

### For Consolidators

1. **When Results Differ**: Check if discrepancy explains the variance
2. **When Configuring**: Understand product's implementation approach
3. **When Reporting**: Know what calculations the product performs automatically

### For Auditors

1. **During Audit**: Verify that discrepancies are documented and intentional
2. **For Compliance**: Understand IFRS implementation approach
3. **For Testing**: Focus testing on areas with known simplifications

## Mapping to Theory Chunks

Each discrepancy document references specific chunks from the Allen White book:

```
Theory Location: direct_consolidation_chunks/financial_consolidation_XXXX.md
```

This enables RAG systems to retrieve both:
- The theoretical explanation (from chunks)
- The product implementation (from discrepancy mapping)

## Update Process

When product behavior changes:
1. Update the relevant discrepancy document
2. Note the version where change occurred
3. Update related help content if needed

---

## Related Documentation

- **Allen White Book** - Complete theory reference (available in `direct_consolidation_chunks/`)
- [Theory Chunks](../../direct_consolidation_chunks/) - Searchable theory (1,333 chunks)
- [Gap Analysis](../../10-gap-analysis/missing-features.md) - Features not yet implemented
- [Help Content](../help-content/) - User-facing documentation

---

*Discrepancy Mapping | Version 1.0 | Last Updated: 2024-12-03*
