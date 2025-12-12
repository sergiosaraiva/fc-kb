# Simplifications Summary: What Theory Covers That Product Simplifies

## Overview

This document provides a comprehensive list of consolidation concepts from Allen White's "Direct Consolidation" and IFRS standards that Prophix.Conso either simplifies or does not implement automatically. Understanding these simplifications helps consultants set expectations and consolidators know when manual intervention is required.

---

## Classification System

| Category | Description |
|----------|-------------|
| ✅ **Fully Implemented** | Product handles per theory |
| 🔶 **Simplified** | Product handles but with reduced complexity |
| 🔸 **Partially Supported** | Some features, manual workaround for others |
| ❌ **Not Implemented** | Manual process required |

---

## 1. Acquisition Accounting (IFRS 3)

| Feature | Status | Theory | Product | Workaround |
|---------|--------|--------|---------|------------|
| **Basic Participation Elimination** | ✅ | Eliminate investment vs equity | S088-S094 codes | - |
| **Goodwill Calculation** | 🔶 | FV of consideration - FV of net assets | Cost - Book value | Manual FV adjustments |
| **Purchase Price Allocation (PPA)** | ❌ | Allocate to identifiable assets at FV | Not automated | Manual adjustment journals |
| **Intangible Recognition** | ❌ | Customer lists, brands, technology | Not automated | Manual identification and entry |
| **Bargain Purchase Gain** | ❌ | Recognize gain in P&L | Not automated | Manual journal entry |
| **Contingent Consideration** | ❌ | Fair value, remeasure each period | Not tracked | Manual tracking and adjustment |
| **Acquisition Costs** | 🔸 | Expense as incurred | Manual handling | Adjustment journals |
| **Step Acquisitions** | 🔶 | Remeasure at FV on control | S094 basic handling | Manual FV remeasurement |
| **Business Combination Achieved in Stages** | 🔶 | Complex layered treatment | Simplified recalculation | Document methodology |

---

## 2. Consolidation Methods (IFRS 10/11/28)

| Feature | Status | Theory | Product | Workaround |
|---------|--------|--------|---------|------------|
| **Global Integration** | ✅ | 100% of assets/liabilities + NCI | Method G | - |
| **Equity Method** | ✅ | Single-line investment | Method E | - |
| **Proportional Method** | ✅ | Pro-rata share | Method P | - |
| **Control Assessment** | 🔶 | Qualitative + quantitative | Primarily >50% test | Manual override |
| **De Facto Control** | 🔸 | Control possible < 50% | Manual override only | Document rationale |
| **Joint Arrangement Classification** | 🔶 | JV vs JO determination | Simplified P method | Manual classification |
| **Significant Influence Test** | 🔶 | Qualitative factors | 20-50% presumption | Override if needed |
| **Potential Voting Rights** | ❌ | Consider if substantive | Not automatic | Manual percentage adjustment |
| **Principal vs Agent** | ❌ | Complex analysis | Not assessed | Document in procedures |
| **Variable Interest Entities** | ❌ | Complex analysis | Not automatic | Manual determination |

---

## 3. Ownership Calculations

| Feature | Status | Theory | Product | Workaround |
|---------|--------|--------|---------|------------|
| **Direct Holdings** | ✅ | Straightforward calculation | TS015S0 table | - |
| **Indirect Holdings** | ✅ | Chain multiplication | Automatic calculation | - |
| **Circular Ownership** | 🔶 | Iterative mathematical solution | Matrix propagation | Verify complex cases |
| **Treasury Shares** | 🔸 | Deduct from issued | Manual adjustment | Reduce issued share count |
| **NCI Calculation** | 🔶 | FV or proportionate option | Proportionate only | Manual for FV method |
| **Multi-Class Shares** | 🔸 | Complex treatment | Basic rights tracking | Manual classification |
| **Preference Shares** | 🔸 | Depends on characteristics | Limited support | Manual treatment |
| **Convertible Instruments** | ❌ | Potential voting rights | Not tracked | Manual if substantive |

---

## 4. Elimination Entries

| Feature | Status | Theory | Product | Workaround |
|---------|--------|--------|---------|------------|
| **Participation Elimination** | ✅ | Investment vs equity | S088-S094 | - |
| **IC Revenue/Expense** | ✅ | Eliminate IC P&L | S083 | - |
| **IC Receivable/Payable** | ✅ | Eliminate IC balances | S082 | - |
| **IC Dividend Elimination** | ✅ | Eliminate dividend income | Dividend procedures | - |
| **Unrealized Profit in Inventory** | 🔶 | Eliminate downstream/upstream | S-code available | May need adjustment |
| **Unrealized Profit in Fixed Assets** | 🔶 | Eliminate over asset life | Basic support | Manual depreciation adj |
| **IC Threshold Tolerance** | 🔶 | Full reconciliation required | Threshold-based | Review threshold level |
| **Profit-in-Stock by Method** | 🔸 | Different treatment by method | Simplified | Manual for E method |

---

## 5. Currency Translation (IAS 21)

| Feature | Status | Theory | Product | Workaround |
|---------|--------|--------|---------|------------|
| **Current Rate Method** | ✅ | Standard translation | CC/AC rates | - |
| **Temporal Method** | 🔸 | For integrated operations | Manual configuration | Set HC rates per account |
| **Translation to OCI** | ✅ | CTA to equity | Translation reserve | - |
| **Goodwill Translation** | 🔶 | Closing rate per IAS 21.47 | Configurable | Set account to CC |
| **Hyperinflation (IAS 29)** | 🔸 | Full restatement | Manual adjustments | Calculate externally |
| **Net Investment Hedging** | ❌ | Hedge accounting | Not supported | Manual tracking |
| **Recycling on Disposal** | 🔸 | Reclassify CTA to P&L | Manual process | Adjustment journal |
| **Functional Currency Determination** | 🔶 | Detailed IAS 21 guidance | User-defined | Document determination |

---

## 6. Scope Changes

| Feature | Status | Theory | Product | Workaround |
|---------|--------|--------|---------|------------|
| **Acquisition Entry** | ✅ | Add to consolidation | Period-based scope | - |
| **Disposal Entry** | 🔶 | Remove + recognize gain/loss | Basic removal | Manual gain/loss calc |
| **Partial Disposal (Retain Control)** | 🔶 | Equity transaction | Simplified | Manual NCI adjustment |
| **Partial Disposal (Lose Control)** | 🔸 | Complex treatment | Basic support | Manual FV remeasurement |
| **Mid-Period Transactions** | 🔶 | Pro-rata treatment | Period-based | Adjustment for timing |
| **Business Combination under Common Control** | 🔸 | Various methods allowed | No specific support | Manual methodology |

---

## 7. Non-Controlling Interest

| Feature | Status | Theory | Product | Workaround |
|---------|--------|--------|---------|------------|
| **NCI Recognition** | ✅ | Proportionate share | Automatic | - |
| **NCI Share of Profit** | ✅ | Allocate P&L to NCI | Automatic | - |
| **NCI Share of OCI** | 🔶 | Allocate OCI to NCI | Simplified | Verify allocation |
| **NCI at Fair Value Option** | ❌ | Full goodwill method | Not supported | Manual calculation |
| **NCI Put Options** | ❌ | Complex liability treatment | Not tracked | Manual adjustment |
| **Changes in NCI** | 🔶 | Equity transaction | Basic support | Verify journal entries |
| **Losses Exceeding NCI** | 🔶 | Attribution rules | Simplified | Verify allocation |

---

## 8. Specific IFRS Requirements

| Feature | IFRS | Status | Workaround |
|---------|------|--------|------------|
| **Impairment Testing (IAS 36)** | IAS 36 | 🔸 | External calculation, manual entry |
| **Deferred Tax (IAS 12)** | IAS 12 | 🔸 | Manual calculation for consolidation adjustments |
| **Share-Based Payments (IFRS 2)** | IFRS 2 | ❌ | Manual tracking and entry |
| **Employee Benefits (IAS 19)** | IAS 19 | 🔸 | Manual aggregation and adjustments |
| **Fair Value Measurement (IFRS 13)** | IFRS 13 | 🔸 | External valuations, manual entry |
| **Financial Instruments (IFRS 9)** | IFRS 9 | 🔸 | Manual classification and measurement |
| **Leases (IFRS 16)** | IFRS 16 | 🔸 | Subsidiary-level application, aggregate |
| **Revenue Recognition (IFRS 15)** | IFRS 15 | 🔸 | Subsidiary-level application, eliminate IC |

---

## 9. Reporting and Disclosure

| Feature | Status | Theory | Product | Workaround |
|---------|--------|--------|---------|------------|
| **Standard Financial Statements** | ✅ | BS, P&L, Cash Flow | Report templates | - |
| **Segment Reporting (IFRS 8)** | 🔸 | Detailed segment analysis | Dimension-based | Configure dimensions |
| **Related Party Disclosures** | 🔸 | Detailed disclosures | IC reports | Additional manual analysis |
| **Subsidiary List Disclosure** | ✅ | List of subsidiaries | Structure reports | - |
| **NCI Disclosures** | 🔸 | Detailed NCI info | Basic reports | Manual compilation |
| **Business Combination Disclosures** | ❌ | Detailed IFRS 3 disclosures | Not automated | Manual preparation |

---

## 10. Summary Statistics

| Category | Fully Implemented | Simplified | Partially Supported | Not Implemented |
|----------|-------------------|------------|---------------------|-----------------|
| Acquisition Accounting | 1 | 3 | 1 | 4 |
| Consolidation Methods | 3 | 3 | 1 | 3 |
| Ownership Calculations | 2 | 2 | 3 | 1 |
| Elimination Entries | 4 | 3 | 1 | 0 |
| Currency Translation | 2 | 3 | 3 | 1 |
| Scope Changes | 1 | 3 | 2 | 0 |
| Non-Controlling Interest | 2 | 3 | 0 | 2 |
| Specific IFRS | 0 | 0 | 7 | 1 |
| **TOTAL** | **15** | **20** | **18** | **12** |

---

## 11. Recommendations by User Type

### For Consultants

**Priority Items to Document**:
1. Purchase price allocation methodology
2. De facto control assessment criteria
3. Treasury share handling procedures
4. Hyperinflation restatement process
5. IC threshold justification

### For Auditors

**Focus Areas**:
1. Verify manual PPA calculations
2. Check control assessment documentation
3. Validate NCI calculations
4. Review translation methodology
5. Test IC threshold appropriateness

### For Consolidators

**Regular Manual Processes**:
1. Maintain PPA schedules externally
2. Track contingent consideration manually
3. Calculate deferred tax on consolidation adjustments
4. Monitor scope change transactions
5. Prepare disclosure information separately

---

## 12. Future Enhancement Recommendations

Based on gap analysis, priority enhancements:

| Priority | Feature | Business Impact |
|----------|---------|-----------------|
| High | Automated PPA tracking | Reduce manual effort, improve accuracy |
| High | Treasury share detection | Improve percentage accuracy |
| Medium | Full goodwill NCI option | IFRS compliance |
| Medium | Hyperinflation automation | Reduce complexity |
| Low | Potential voting rights | Edge case handling |
| Low | Hedge accounting | Specialized requirement |

---

## Related Documentation

- [Theory vs Product Overview](theory-vs-product-overview.md)
- [Elimination Differences](elimination-differences.md)
- [Ownership Differences](ownership-differences.md)
- [Currency Differences](currency-differences.md)
- [Gap Analysis](../../10-gap-analysis/missing-features.md)

---

*Simplifications Summary | Version 1.0 | Last Updated: 2024-12-03*
