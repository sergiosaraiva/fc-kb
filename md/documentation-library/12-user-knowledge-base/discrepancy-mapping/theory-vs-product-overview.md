# Theory vs Product: Executive Overview

## Document Purpose

This document provides an executive summary of how Prophix.Conso implements Allen White's "Direct Consolidation" framework, highlighting key areas where the product differs from pure theory and explaining the rationale behind these differences.

## The Direct Consolidation Approach

Both Allen White's theory and Prophix.Conso follow the **Direct Consolidation** methodology, which differs from the traditional "step-by-step" approach:

| Approach | Description |
|----------|-------------|
| **Traditional (Step-by-Step)** | Consolidate subsidiaries bottom-up, level by level |
| **Direct Consolidation** | Consolidate all subsidiaries directly to the parent in one pass |

**Why Direct?**
- Simpler to understand and audit
- More efficient for large groups
- Better handles complex ownership structures

---

## Summary of Key Differences

### ✅ Aligned with Theory

| Area | Implementation |
|------|---------------|
| Consolidation Methods | G, P, E, N methods match theory |
| Elimination Types | Standard eliminations (IC, participation, dividends) |
| Currency Translation | Current rate method with AC/CC rates |
| Minority Interest | Calculated at each subsidiary level |
| Journal Structure | T-journals mirror theoretical entries |

### ⚠️ Simplified from Theory

| Area | Theory | Product | Rationale |
|------|--------|---------|-----------|
| **Goodwill Calculation** | Full fair value allocation | Simplified acquisition cost - book value | Performance, typical use case |
| **Step Acquisitions** | Layer-by-layer recalculation | Single recalculation | Complexity reduction |
| **Circular Ownership** | Iterative mathematical solution | Simplified percentage handling | Rare use case |
| **Hyperinflation** | Full IAS 29 restatement | Adjustment entry approach | Flexibility |

### ❌ Not Implemented (See Gap Analysis)

| Feature | Theory Reference | Status |
|---------|-----------------|--------|
| Bargain Purchase | IFRS 3 | Manual adjustment required |
| Contingent Consideration | IFRS 3 | Manual tracking |
| Put Option Liability | Complex instruments | Manual adjustment |
| Dual Control Test | IFRS 10 | Simplified threshold |

---

## Detailed Comparison by Module

### 1. Group Structure & Ownership

**Theory (Allen White)**:
- Detailed analysis of control vs ownership
- Voting rights analysis for method determination
- Complex circular ownership algorithms
- Potential voting rights consideration

**Product (Prophix.Conso)**:
- Percentage-based method determination (>50% = G, 20-50% = E/P)
- Financial rights and voting rights stored separately
- Automatic percentage calculation with manual override
- Group structure defined in `TS015S0` table

**Key Screens**: `Group > Companies`, `Group > Group Structure`

### 2. Consolidation Methods

**Theory**:
| Method | Criteria | Treatment |
|--------|----------|-----------|
| Global (G) | Control (>50% voting) | 100% assets/liabilities, minority interest |
| Proportional (P) | Joint control (contractual) | Share of assets/liabilities |
| Equity (E) | Significant influence (20-50%) | Single line investment |
| Not Consolidated (N) | No influence (<20%) | Cost method |

**Product**: Same methods, but:
- Method stored per company per period (allows changes)
- Automatic vs manual determination configurable
- Override allowed for exceptions

### 3. Elimination Processing

**Theory (Sequential)**:
```
1. Participation eliminations (acquisition accounting)
2. Dividend eliminations (intercompany dividends)
3. IC transaction eliminations (revenue/cost)
4. IC balance eliminations (receivables/payables)
5. Profit-in-stock eliminations (unrealized profit)
```

**Product (S-Code Based)**:
```
Eliminations executed by S-code order:
S001-S020: Participation eliminations
S021-S040: Equity adjustments
S041-S060: IC eliminations
S061-S080: Dividend handling
S081-S094: Special eliminations
U###: User-defined eliminations
```

**Key Difference**: Product uses configurable elimination codes rather than fixed sequence, allowing flexibility but requiring proper setup.

### 4. Currency Translation

**Theory (IAS 21)**:
- Functional currency determination
- Current rate method (most subsidiaries)
- Temporal method (integrated operations)
- Translation of goodwill at acquisition rate

**Product**:
- Four rate types: CC (Closing), AC (Average), MC (Manual Closing), HC (Historical)
- Account-level rate assignment
- Automatic translation during consolidation
- Translation adjustments to equity

**Rate Application**:
| Account Type | Theory Rate | Product Rate |
|--------------|-------------|--------------|
| Balance Sheet | Closing | CC |
| Income Statement | Average | AC |
| Equity | Historical | HC |
| Fixed Assets | Various | Configurable |

### 5. Intercompany Handling

**Theory**:
- Full matching required
- Differences investigated and resolved
- Timing differences tracked

**Product**:
- Threshold-based tolerance (`Threshold` field)
- Automatic elimination below threshold
- Three adjustment types for differences:
  - Transfer Difference
  - Reclassify Difference
  - Book Difference
- IC rules define elimination behavior

**Key Screen**: `Consolidation > Consolidation > Intercompany Matching`

---

## Implementation Implications

### For New Implementations

1. **Configure elimination codes** to match client's consolidation approach
2. **Set appropriate thresholds** for IC matching
3. **Define rate types** per account category
4. **Document any manual workarounds** for unsupported features

### For Migrations from Other Systems

1. **Map elimination types** to S-codes
2. **Verify percentage calculations** match expected results
3. **Test currency translation** with known scenarios
4. **Compare minority interest** calculations

### For Auditors

1. **Request S-code configuration** to understand elimination logic
2. **Verify threshold settings** for IC eliminations
3. **Test percentage calculations** for complex structures
4. **Review manual adjustments** for unsupported features

---

## Frequently Asked Questions

**Q: Does the product follow IFRS?**
A: Yes, Prophix.Conso implements IFRS-compliant consolidation for standard scenarios. Some complex IFRS 3 requirements (bargain purchase, contingent consideration) require manual adjustments.

**Q: Can I customize elimination sequences?**
A: Yes, elimination codes (S-codes) determine execution order. Custom eliminations can be created with U-prefix codes.

**Q: Why don't my percentages match manual calculation?**
A: Check for circular ownership, treasury shares, or indirect holdings affecting the calculation. The product handles these automatically.

**Q: How do I handle features not in the product?**
A: Use manual adjustment journals. Document the adjustment purpose and link to the theoretical requirement.

---

## Related Documents

- [Elimination Differences](elimination-differences.md) - Detailed elimination comparison
- [Ownership Differences](ownership-differences.md) - Percentage calculation details
- [Currency Differences](currency-differences.md) - Translation method details
- [Simplifications Summary](simplifications-summary.md) - Complete list of simplifications

---

*Theory vs Product Overview | Version 1.0 | Last Updated: 2024-12-03*
