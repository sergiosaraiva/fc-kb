# Elimination Differences: Theory vs Product

## Overview

This document details how Prophix.Conso implements elimination entries compared to Allen White's "Direct Consolidation" theoretical framework. Understanding these differences is crucial for consultants configuring eliminations and auditors validating consolidation results.

---

## Executive Summary

| Aspect | Theory (Allen White) | Product (Prophix.Conso) |
|--------|---------------------|------------------------|
| **Organization** | By elimination type (sequential phases) | By S-code (configurable order) |
| **Execution** | Multi-pass with dependencies | Single-pass by S-code sequence |
| **IC Matching** | Full reconciliation required | Threshold-based tolerance |
| **Goodwill** | Full fair value allocation | Simplified acquisition cost - book value |
| **Customization** | Fixed types | User-defined eliminations (U###) |

---

## 1. Elimination Type Organization

### Theory Approach

Allen White describes elimination entries organized by **type and purpose**, executed in a specific sequence:

```
Phase 1: Participation Eliminations
  - Eliminate investment in subsidiary
  - Recognize goodwill/bargain purchase
  - Allocate to fair values

Phase 2: Equity Adjustments
  - Post-acquisition reserves
  - Retained earnings allocation

Phase 3: Intercompany Eliminations
  - Revenue/expense eliminations
  - Receivable/payable eliminations
  - Intercompany profits

Phase 4: Dividend Eliminations
  - Intercompany dividends
  - Dividend receivable/payable

Phase 5: Translation Adjustments
  - Currency translation differences
  - OCI reclassification
```

### Product Implementation

Prophix.Conso organizes eliminations by **S-code** (system-defined) or **U-code** (user-defined), with configurable execution order:

| S-Code Range | Category | Description |
|--------------|----------|-------------|
| **S001** | Base | Standard consolidation journal |
| **S065-S066** | EPU | Earnings per unit related |
| **S072** | Method Change | Consolidation method transitions |
| **S074** | Analysis | Consolidation difference analysis |
| **S075** | Translation | Currency translation adjustment |
| **S077** | Not Consolidated | Non-consolidated entities |
| **S079** | Proportional | Proportional consolidation |
| **S081** | Equity Method | Equity method eliminations |
| **S082** | IC Netting | Intercompany balance netting |
| **S083** | IC Elimination | Intercompany transaction elimination |
| **S084** | IC Non-Elimination | IC transactions not eliminated |
| **S085** | Minority Interest | NCI eliminations |
| **S087** | Equity Capital | Equity elimination |
| **S088-S094** | Participation | Participation eliminations (Types 0-4) |
| **S183** | 100% Subsidiary | Fully-owned subsidiary handling |
| **U###** | User-Defined | Custom elimination rules |

### Key Difference

> **Theory**: Sequential phases with dependencies (Phase 2 depends on Phase 1 results)
>
> **Product**: Parallel processing by S-code, with execution order determined by code number

**Implication**: Users must configure S-codes correctly to ensure proper elimination sequence. The product doesn't enforce theoretical dependencies automatically.

---

## 2. Participation Eliminations

### Theory (IFRS 3 / Allen White)

Full acquisition accounting with fair value allocation:

```
Investment in Subsidiary          XXX
  Less: Fair Value of Net Assets   (XXX)
  = Goodwill                       XXX

Journal Entry:
Dr  Goodwill                       XXX
Dr  Fair Value Adjustments         XXX
    Cr  Investment in Subsidiary   XXX
    Cr  Non-controlling Interest   XXX
```

Key elements:
- **Purchase Price Allocation (PPA)**: Fair values for all identifiable assets/liabilities
- **Bargain Purchase**: Gain recognized if FV > consideration
- **Contingent Consideration**: Fair value at acquisition, remeasured

### Product Implementation

Simplified participation elimination using book values:

| S-Code | Participation Type | Description |
|--------|-------------------|-------------|
| **S088** | Type 0 | Basic participation elimination |
| **S089** | Type 1 | With goodwill calculation |
| **S090** | Type 2 | With minority interest |
| **S093** | Type 3 | Complex ownership |
| **S094** | Type 4 | Step acquisition |

**Simplified Calculation**:
```
Goodwill = Acquisition Cost - (Book Value of Equity × Ownership %)
```

### Key Differences

| Aspect | Theory | Product | Gap |
|--------|--------|---------|-----|
| **Fair Value Allocation** | Required for all assets | Not automatic | Manual PPA journal required |
| **Bargain Purchase** | Gain in P&L | Not automatic | Manual adjustment required |
| **Contingent Consideration** | Remeasured each period | Not tracked | Manual tracking required |
| **Intangible Recognition** | Customer relationships, brands, etc. | Not automatic | Manual entry required |

**Workaround**: Use adjustment journals (Adjustments > Journal Entry) to record fair value adjustments and other IFRS 3 requirements not automated.

---

## 3. Intercompany Eliminations

### Theory Approach

Full matching and elimination of:
1. **Revenue/Cost of Sales**: Intercompany sales must match purchases
2. **Receivables/Payables**: IC balances must net to zero
3. **Unrealized Profit**: Eliminate profit in inventory/fixed assets
4. **Interest/Dividends**: Eliminate IC financial transactions

Strict reconciliation requirement - differences must be investigated and resolved.

### Product Implementation

**S-codes for IC Eliminations**:

| S-Code | Purpose |
|--------|---------|
| **S082** | IC Netting - Balance sheet matching |
| **S083** | IC Elimination - P&L transactions |
| **S084** | IC Non-Elimination - Flagged as IC but not eliminated |

**Threshold-Based Tolerance**:

The product allows configurable thresholds below which IC differences are automatically eliminated:

```
Navigation: Consolidation > Intercompany Matching
Field: Threshold
```

| Threshold Type | Description |
|----------------|-------------|
| **Per Rule** | Different threshold per IC elimination rule |
| **Per Company** | Different tolerance per company pair |
| **Global** | Single threshold for all IC transactions |

### Key Differences

| Aspect | Theory | Product | Impact |
|--------|--------|---------|--------|
| **Matching Requirement** | 100% matching | Threshold tolerance | Small differences auto-eliminated |
| **Difference Handling** | Must investigate | Three auto-adjustment types | May hide timing issues |
| **Currency Impact** | Full reconciliation | Simplified reclassification | Translation differences simplified |

**Adjustment Types for IC Differences**:

| Type | Purpose | Use Case |
|------|---------|----------|
| **Transfer Difference** | Move difference to/from out-of-group | Genuine external transaction |
| **Reclassify Difference** | Reclassify P&L IC difference | Currency translation difference |
| **Book Difference** | Book difference to translation account | Balance sheet IC difference |

---

## 4. Dividend Eliminations

### Theory Approach

Intercompany dividends must be:
1. Eliminated from consolidated P&L (dividend income)
2. Eliminated from consolidated dividend receivable/payable
3. Adjusted for timing differences
4. Split between parent share and NCI share

### Product Implementation

Dividend handling through S-codes and specific elimination procedures:

- **P_CONSO_ELIM_DIVIDENDS**: Main dividend elimination procedure
- Automatic split between parent and minority portions
- Tracks dividend history by company and period

### Key Differences

| Aspect | Theory | Product | Notes |
|--------|--------|---------|-------|
| **Dividend Timing** | Record when declared | Period-based processing | Timing differences possible |
| **Partial Dividends** | Pro-rata by holding date | Simplified full-period | May need adjustment for mid-period changes |
| **Preferred Dividends** | Specific treatment | Limited support | Manual tracking recommended |

---

## 5. Translation Adjustments

### Theory (IAS 21)

Currency translation differences arise from:
1. Translating net assets at different rates (historical vs current)
2. Translating income at average vs closing rates
3. Hedging relationships

Should be recognized in:
- Other Comprehensive Income (OCI)
- Reclassified to P&L on disposal

### Product Implementation

**S075**: Translation Adjustment handling

- Automatic calculation during consolidation
- Posted to designated translation reserve account
- Tracks by company and period

### Key Differences

| Aspect | Theory | Product | Notes |
|--------|--------|---------|-------|
| **OCI Classification** | Specific OCI component | Single reserve account | Less granular reporting |
| **Recycling on Disposal** | Reclassify to P&L | Manual process | Requires user intervention |
| **Hedge Accounting** | Complex matching | Not supported | Manual tracking required |

---

## 6. User-Defined Eliminations (U-codes)

### Product Feature

Prophix.Conso supports custom elimination rules through U-codes:

```
U### - User-defined elimination codes
```

**Configuration**: Configuration > Eliminations

**Capabilities**:
- Define custom elimination logic
- Set execution order
- Configure accounts and percentages
- Link to specific company combinations

### When to Use

| Scenario | Approach |
|----------|----------|
| **Non-standard IC transaction** | Create U-code with specific accounts |
| **Industry-specific elimination** | Configure custom rule |
| **Client-specific requirement** | Build tailored elimination |
| **IFRS requirements not automated** | Manual elimination via U-code |

---

## 7. Practical Implications

### For Consultants

1. **During Implementation**:
   - Configure S-codes to match client's elimination needs
   - Set appropriate IC thresholds (recommend starting conservative)
   - Create U-codes for non-standard requirements
   - Document any manual processes for IFRS compliance

2. **Training Users**:
   - Explain S-code execution order
   - Train on IC matching and threshold behavior
   - Document adjustment journal procedures

### For Auditors

1. **Verification Points**:
   - Review S-code configuration for completeness
   - Verify threshold settings are appropriate
   - Check for manual adjustments covering IFRS gaps
   - Validate goodwill calculations manually

2. **Common Issues**:
   - IC thresholds set too high (hiding material differences)
   - Missing fair value adjustments
   - Incomplete dividend elimination

### For Consolidators

1. **Daily Operations**:
   - Review IC matching before running eliminations
   - Investigate differences above threshold
   - Post manual adjustments as needed
   - Document elimination rationale

---

## 8. Frequently Asked Questions

**Q: Why don't my elimination entries match the textbook examples?**
A: The product uses simplified calculations (book value vs fair value) and S-code organization instead of theoretical phases. Use adjustment journals to supplement automatic eliminations for full IFRS compliance.

**Q: Can I change the elimination execution order?**
A: Eliminations execute in S-code numerical order. To change sequence, you may need to reconfigure S-code assignments or use U-codes.

**Q: How do I handle fair value adjustments?**
A: Create manual adjustment journals (Adjustments > Journal Entry) for purchase price allocation entries not generated automatically.

**Q: What happens if IC doesn't match?**
A: Differences below threshold are auto-eliminated. Differences above threshold require manual resolution using the three adjustment types (Transfer, Reclassify, Book).

**Q: Can I create custom eliminations?**
A: Yes, use U-codes (User-defined eliminations) through Configuration > Eliminations.

---

## Related Documentation

- [Theory vs Product Overview](theory-vs-product-overview.md)
- [Ownership Differences](ownership-differences.md)
- [Help: Consolidate](../help-content/0370-consolidate.md)
- [Help: Reconcile Intercompany](../help-content/0340-reconcile-intercompany-data.md)
- [Technical: Participation Eliminations](../../04-elimination-entries/participation-eliminations.md)

---

*Elimination Differences | Version 1.0 | Last Updated: 2024-12-03*
