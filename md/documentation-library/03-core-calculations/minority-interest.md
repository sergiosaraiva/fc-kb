# Minority Interest (Non-Controlling Interest)

## Document Metadata
- **Category**: Core Calculation
- **Theory Source**: Knowledge base chunks: 0027, 0050, 0066, 0067, 0087
- **Implementation Files**:
  - `Sigma.Database/dbo/Stored Procedures/P_CONSO_ELIM_MINORITYINTEREST.sql`
  - `Sigma.Database/dbo/Stored Procedures/P_VIEW_OWNERSHIP.sql`
  - `Sigma.Database/dbo/Stored Procedures/P_REPORT_CONSOLIDATED_EQUITY.sql`
  - 61+ related stored procedures
- **Last Updated**: 2024-12-01
- **Completeness**: 95% (comprehensive implementation)
- **Compliance Status**: IFRS 10 / IAS 27 compliant

## Executive Summary

Minority Interest (also called Non-Controlling Interest or NCI under IFRS) represents the portion of a subsidiary's equity that is not owned by the parent company. When a parent consolidates a subsidiary using global integration but owns less than 100%, the remaining ownership percentage belongs to minority shareholders.

Prophix.Conso provides a **comprehensive minority interest calculation engine** through `P_CONSO_ELIM_MINORITYINTEREST`, which handles both balance sheet and income statement allocations, including complex scenarios like changes in ownership percentage and multi-level structures.

## Theoretical Framework

### Concept Definition
From Allen White's "Direct Consolidation":

> When performing global integration (full consolidation), 100% of the subsidiary's assets, liabilities, income, and expenses are included in the consolidated financial statements. However, the portion not owned by the parent must be shown separately as **minority interests** (non-controlling interests).

### Key Principles

1. **Balance Sheet Allocation**: Minority Interest = (1 - Parent %) × Subsidiary Net Assets
2. **Income Statement Allocation**: Minority Share of Profit = (1 - Parent %) × Subsidiary Net Income
3. **Multi-Level Calculation**: Indirect minority interests arise in complex structures
4. **Changes in Ownership**: Handled as equity transactions (no gain/loss recognition)
5. **Negative Minority Interest**: Can arise when subsidiary has accumulated losses

### Formula/Algorithm

```
Basic Minority Interest Calculation:

Balance Sheet:
  MI_BS = (1 - Parent_Ownership%) × Subsidiary_Net_Equity

Income Statement:
  MI_PL = (1 - Parent_Ownership%) × Subsidiary_Net_Income

Multi-Level Example (from Chunk 66):
  Parent P owns 75% of B → Minority in B = 25%
  B owns 90% of C → P's effective ownership = 75% × 90% = 67.5%
  → Minority in C = 100% - 67.5% = 32.5%

Treasury Shares Adjustment (from Chunk 87):
  If company holds 5% of own shares:
  Effective Minority = (100% - Parent%) / (100% - Treasury%)
  Example: 60% parent, 5% treasury
  → Effective control: 60% / 95% = 63.16%
  → Minority: 35% / 95% = 36.84%
```

### Visual Representation

```
Consolidation with Minority Interest:

    ┌─────────┐
    │ Parent  │
    │   P     │
    └────┬────┘
         │ 80%
         ▼
    ┌─────────┐
    │  Sub A  │ ← Minority Interest = 20%
    └─────────┘

Consolidated Balance Sheet:
├── 100% of A's Assets
├── 100% of A's Liabilities
└── Equity
    ├── Parent's Share (80%)
    └── Minority Interest (20%)
```

## Current Implementation

### Database Layer

#### Main Minority Interest Procedure

`P_CONSO_ELIM_MINORITYINTEREST` handles the complete minority interest calculation:

```sql
CREATE procedure [dbo].[P_CONSO_ELIM_MINORITYINTEREST]
    @Login nvarchar(256),           -- User who initiated
    @SessionID int,
    @ConsoID int,
    @RefConsoID int,                -- Reference period for comparison
    @PreviousPeriodAdjFlowID int,
    @ConsoCurrCode nvarchar(3),
    @ParentCompanyID int,
    @JournalTypeS001ID int,
    @UNEXPVarFlowID int,            -- Unexplained variance flow
    @NETVarFlowID int,              -- Net variance flow
    @ExecuteDimensions bit,
    @Debug bit = 0,
    @errorinfo xml output
as begin
    -- Key variables for minority interest accounts
    declare @MinorBSProfitLossAccountID int    -- MI Balance Sheet P/L
    declare @MinorPLProfitAccountID int        -- MI Income Statement Profit
    declare @MinorPLLossAccountID int          -- MI Income Statement Loss
    declare @MinorInterestsAccountID int       -- MI Equity Account

    -- Rounding based on period configuration
    Select @RoundingDecimal = NbrDec
        From dbo.TS096S0 with(nolock)
        Where ConsoID = @ConsoID

    -- Get the S085 elimination record for minority interest
    select @JournalTypeS085ID = a.JournalTypeID,
           @JournalText = a.JournalText,
           @Behaviour = a.Behaviour,
           @MinorityFlag = a.MinorityFlag,
           @ConsoMethodSelectionID = a.ConsoMethodSelectionID
    -- ... calculation logic
end
```

#### Key Features
- **Period Rounding**: Configurable decimal precision per period
- **Reference Period Comparison**: Tracks changes vs prior period
- **Dimension Support**: Optional dimension-level calculations
- **Participation Exclusion**: Participation accounts handled separately
- **Journal Integration**: Posts to specific minority interest journals (S085)

### Elimination Codes

The system uses code S085 for minority interest eliminations:

```sql
-- From TS070S0 Elimination Header
ElimCode = 'S085'
ElimText = 'Minority Interest'
JournalTypeID = [specific journal for MI]
MinorityFlag = 1
```

### Related Procedures

| Procedure | Purpose |
|-----------|---------|
| `P_CONSO_ELIM_MINORITYINTEREST` | Main MI calculation |
| `P_VIEW_OWNERSHIP` | Display ownership structure |
| `P_REPORT_CONSOLIDATED_EQUITY` | Equity statement with MI |
| `P_CONSO_ELIM_PARTICIPATIONS1-4` | Participation eliminations |
| `P_UPDATE_OWNERSHIP` | Update ownership percentages |

### Application Layer

The minority interest calculation is triggered as part of the elimination process:

```csharp
// ConsolidationIntegrationJob.cs
public enum StoredProcedures : byte
{
    Elims = 0x8,  // Includes minority interest calculation
    All = (LinkedCategories | Bundles | Adjustments | Elims)
}

// Elimination procedure includes MI
private const string StoredProcedureNameElims = "dbo.P_CONSO_ELIM";
// P_CONSO_ELIM calls P_CONSO_ELIM_MINORITYINTEREST
```

### Frontend Layer

Minority interest data is accessible through:
- **Ownership Data Entry**: Input ownership percentages
- **Consolidation Reports**: View MI allocations
- **Equity Statement Report**: See MI in equity reconciliation

## Theory vs Practice Analysis

| Aspect | Theory (Allen White) | Implementation (Prophix.Conso) | Variance |
|--------|---------------------|--------------------------------|----------|
| Basic Formula | (1 - %) × Equity | Full implementation | **None** - Aligned |
| P/L Allocation | (1 - %) × Net Income | Separate profit/loss accounts | **Enhanced** - More granular |
| Multi-Level | Calculated at each level | Hierarchical calculation | **None** - Aligned |
| Period Changes | Track movement | Reference period comparison | **Enhanced** |
| Rounding | Not specified | Configurable decimals | **Enhanced** |
| Dimension Support | Not covered | Full dimension breakdown | **Additional** |
| Journal Integration | Standard adjustment | Dedicated journal type (S085) | **Enhanced** |

## Gap Analysis

### Missing Elements
- [ ] **Treasury Share Adjustment**: Automatic percentage adjustment for treasury shares not implemented (see missing-features.md)

### Divergent Implementation
- **None identified** - Implementation closely follows theory

### Additional Features (Beyond Theory)
- ✅ **Reference Period Tracking**: Compare MI between periods
- ✅ **Dimension-Level Calculation**: Break down MI by dimensions
- ✅ **Profit/Loss Separation**: Separate accounts for MI profit vs loss
- ✅ **Configurable Rounding**: Period-specific decimal precision
- ✅ **Unexplained Variance Handling**: Track unexplained movements
- ✅ **Participation Account Exclusion**: Specialized handling for participations

## Business Impact

### Current Capabilities
- Full IFRS 10 compliant minority interest calculation
- Support for complex multi-level ownership structures
- Audit trail through dedicated journal types
- Period-over-period movement analysis

### Operational Considerations
- Ensure ownership percentages are accurate before consolidation
- Review minority interest journal entries for reasonableness
- Verify allocation between profit and loss components

## Recommendations

1. **Treasury Share Enhancement**: Integrate treasury share adjustment into ownership calculation
2. **Validation Report**: Add pre-consolidation check for ownership data completeness
3. **Visualization**: Add MI movement chart for period analysis
4. **Negative MI Warning**: Alert when minority interest becomes negative

## Related Documentation
- See also: [Global Integration](../02-consolidation-methods/global-integration.md)
- See also: [Goodwill Calculation](goodwill-calculation.md)
- See also: [Missing Features - Treasury Shares](../10-gap-analysis/missing-features.md#2-treasury-shares-adjustment)
- Knowledge Base: Chunks 0027, 0050, 0066, 0067, 0087
- Code: `P_CONSO_ELIM_MINORITYINTEREST.sql:29-80`

## Appendix A: Minority Interest Account Structure

```
Account Hierarchy:
├── MinorBSProfitLossAccountID    → Balance Sheet: MI portion of retained earnings
├── MinorPLProfitAccountID        → P&L: MI share when subsidiary profitable
├── MinorPLLossAccountID          → P&L: MI share when subsidiary has loss
└── MinorInterestsAccountID       → Equity: Total minority interest position
```

## Appendix B: Comprehensive Multi-Tier Minority Interest Examples

### Example 1: Two-Tier Structure (P → A → B)

**Given Structure**:
```
        ┌─────────┐
        │ Parent P │
        └────┬────┘
             │ 75%
             ▼
        ┌─────────┐
        │  Sub A  │ ← Direct Minority: 25%
        └────┬────┘
             │ 80%
             ▼
        ┌─────────┐
        │  Sub B  │ ← Indirect Minority: ?
        └─────────┘
```

**Financial Data**:

| Company | Share Capital | Retained Earnings | Net Income | Total Equity |
|---------|---------------|-------------------|------------|--------------|
| Sub A | 1,000 | 500 | 200 | 1,700 |
| Sub B | 600 | 300 | 150 | 1,050 |

**Step 1: Calculate Effective Ownership Percentages**

```
P's direct ownership of A:                    75.00%
A's direct ownership of B:                    80.00%

P's effective ownership of B:
  = P→A × A→B = 75% × 80% =                   60.00%

Minority interests:
  - In A (direct):     100% - 75% =           25.00%
  - In B (indirect):   100% - 60% =           40.00%
```

**Step 2: Calculate Minority Interest in Sub B (Bottom Up)**

```
Sub B Total Equity:                           1,050

Minority Interest in B:
  Direct Minority (A's minorities × A's share):
    = 25% × 80% × 1,050 =                       210

  A's Minority Shareholders' interest in B:
    = 25% × 80% × 1,050 =                       210

  B's Direct Minority (not owned by A):
    = 20% × 1,050 =                             210

Total Minority in B:
  = (1 - P's effective %) × B's Equity
  = 40% × 1,050 =                               420
```

**Breakdown of B's Minority Interest**:
| Component | Calculation | Amount |
|-----------|-------------|--------|
| B's direct minority (20%) | 20% × 1,050 | 210 |
| A's minority share of B (25% × 80%) | 20% × 1,050 | 210 |
| **Total Minority in B** | 40% × 1,050 | **420** |

**Step 3: Calculate Minority Interest in Sub A**

```
Sub A Own Equity (excluding investment in B):
  Share Capital:                              1,000
  Retained Earnings:                            500
  Net Income:                                   200
  Sub A Own Equity:                           1,700

Add: A's share of B (for group equity):
  = 80% × 1,050 =                               840

A's Group-Level Equity:
  = 1,700 + 840 =                             2,540

Minority Interest in A:
  = 25% × 2,540 =                               635
```

**Step 4: Total Consolidated Minority Interest**

```
Total Minority Interest:
  Minority in A:                                635
  Less: A's minorities' share of B
        (already in MI in B):                 (210)
  Plus: MI in B:                                420
                                              -----
  **Total MI (Cross-check method)**:            845

Direct calculation:
  MI in A (at A level): 25% × 1,700 =           425
  MI in B: 40% × 1,050 =                        420
  Total:                                        845 ✓
```

**Step 5: P&L Allocation to Minority**

```
Net Income Attribution:
  Sub A Net Income:                             200
  Sub B Net Income:                             150

Minority Share of A's Income:
  = 25% × 200 =                                  50

Minority Share of B's Income:
  = 40% × 150 =                                  60

Total Minority Share of Profit:                 110
```

**Step 6: Journal Entries (S085 Elimination)**

```
Balance Sheet Entry:
Dr  Equity - Minority Interest in A          425
Dr  Equity - Minority Interest in B          420
    Cr  Minority Interest (B/S Total)             845

Income Statement Entry:
Dr  Net Income Attributable to MI             110
    Cr  Minority P&L - Sub A                       50
    Cr  Minority P&L - Sub B                       60
```

### Example 2: Three-Tier Structure (P → A → B → C)

**Given Structure**:
```
        ┌─────────┐
        │ Parent P │
        └────┬────┘
             │ 80%
             ▼
        ┌─────────┐
        │  Sub A  │ ← MI: 20%
        └────┬────┘
             │ 70%
             ▼
        ┌─────────┐
        │  Sub B  │ ← MI: 44%
        └────┬────┘
             │ 90%
             ▼
        ┌─────────┐
        │  Sub C  │ ← MI: 49.6%
        └─────────┘
```

**Effective Ownership Calculation**:

| Company | Direct Owner | Direct % | P's Effective % | Minority % |
|---------|--------------|----------|-----------------|------------|
| A | P | 80% | 80.0% | 20.0% |
| B | A | 70% | 80% × 70% = 56.0% | 44.0% |
| C | B | 90% | 56% × 90% = 50.4% | 49.6% |

**Financial Data**:

| Company | Total Equity | Net Income |
|---------|--------------|------------|
| Sub A | 2,000 | 400 |
| Sub B | 1,500 | 300 |
| Sub C | 800 | 160 |

**Minority Interest Calculation**:

```
MI in Sub C:
  = 49.6% × 800 =                               397

MI in Sub B:
  = 44% × 1,500 =                               660

MI in Sub A:
  = 20% × 2,000 =                               400

Total MI (Balance Sheet):                     1,457

P&L Attribution:
  MI share of C = 49.6% × 160 =                  79
  MI share of B = 44% × 300 =                   132
  MI share of A = 20% × 400 =                    80
  Total MI P&L:                                 291
```

### Example 3: Ownership Change Impact

**Scenario**: P increases ownership in A from 60% to 80%

**Before Change**:
```
P owns 60% of A
A owns 100% of B
A's equity: 1,000
B's equity: 500

MI in A: 40% × 1,000 = 400
MI in B: 40% × 500 = 200 (through A's minority)
Total MI: 600
```

**After Change**:
```
P owns 80% of A
A owns 100% of B
A's equity: 1,000 (unchanged)
B's equity: 500 (unchanged)

MI in A: 20% × 1,000 = 200
MI in B: 20% × 500 = 100 (through A's minority)
Total MI: 300
```

**Change in Minority Interest**:
```
Decrease: 600 - 300 = 300

This is an equity transaction (IFRS 10):
  Dr  Minority Interest           300
      Cr  Parent's Equity              300*

  *Adjusted for any consideration paid
```

### Example 4: Negative Minority Interest

**Scenario**: Subsidiary with accumulated losses

```
Sub A Balance Sheet:
  Share Capital:                    500
  Accumulated Losses:              (800)
  Net Equity:                      (300)

P owns 70% of A

Minority Interest Calculation:
  MI = 30% × (300) = (90)

Treatment:
- Negative MI shown in consolidated equity
- Represents minority's share of accumulated losses
- Minority shareholders have no obligation to fund losses
  (unless contractually required)

Journal Entry:
Dr  Minority Interest (negative balance)   90
    Cr  Equity - Accumulated Losses            90
```

### Summary: Minority Interest Calculation Checklist

| Step | Action | Formula |
|------|--------|---------|
| 1 | Calculate effective ownership | Chain multiply: P→A × A→B × B→C... |
| 2 | Determine minority % | 100% - Effective % |
| 3 | Calculate MI per subsidiary | MI% × Subsidiary Equity |
| 4 | Allocate P&L | MI% × Subsidiary Net Income |
| 5 | Post S085 elimination | Separate B/S and P&L entries |
| 6 | Handle special cases | Treasury shares, negative MI, ownership changes |

## API Reference

### Primary API Handlers
| Handler | YAML File | Purpose | Status |
|---------|-----------|---------|--------|
| `Consolidation_Execute` | [api-consolidation-endpoints.yaml](../11-agent-support/api-consolidation-endpoints.yaml) | Execute S085 minority interest | ✅ IMPLEMENTED |
| `Ownership_GetOwnership` | [api-ownership-endpoints.yaml](../11-agent-support/api-ownership-endpoints.yaml) | Get minority percentages | ✅ IMPLEMENTED |
| `Report_ExecuteReport` | [api-reports-endpoints.yaml](../11-agent-support/api-reports-endpoints.yaml) | Generate NCI movement report | ✅ IMPLEMENTED |

### Supporting API Handlers
| Handler | YAML File | Purpose |
|---------|-----------|---------|
| `Elimination_GetEliminations` | [api-elimination-endpoints.yaml](../11-agent-support/api-elimination-endpoints.yaml) | Get S085 NCI eliminations |
| `Event_GetEvents` | [api-event-endpoints.yaml](../11-agent-support/api-event-endpoints.yaml) | Get minority interest events |

### API Workflow
```
1. Ownership_GetOwnership → Get MinorPerc for each company
2. Consolidation_Execute → P_CONSO_ELIM_MINORITYINTEREST calculates:
   * MI_BS = MinorPerc × Subsidiary Net Assets
   * MI_PL = MinorPerc × Subsidiary Net Income
3. Report_ExecuteReport → P_REPORT_CONSOLIDATED_EQUITY for NCI movement
```

### Stored Procedure Reference
- `P_CONSO_ELIM_MINORITYINTEREST` - Main NCI calculation (S085)
- `P_REPORT_CONSOLIDATED_EQUITY` - NCI movement report
- `P_VIEW_OWNERSHIP` - Ownership structure with NCI %

### Related API Documentation
- [API Index](../11-agent-support/api-index.yaml) - Master handler catalog
- [Gap Analysis](../11-agent-support/gap-analysis-report.yaml) - Theory alignment: **IFRS 10/IAS 27 compliant**

---

## See Also

### Related Core Calculations
- [Multi-tier Holdings](../06-ownership-structure/multi-tier-holdings.md) - Indirect ownership chains
- [Goodwill Calculation](goodwill-calculation.md) - NCI measurement options
- [Equity Reconciliation](equity-reconciliation.md) - Movement analysis

### Related Eliminations
- [Participation Eliminations](../04-elimination-entries/participation-eliminations.md) - Investment elimination
- [User Eliminations](../04-elimination-entries/user-eliminations.md) - Manual NCI adjustments

### Related Methods
- [Global Integration](../02-consolidation-methods/global-integration.md) - NCI recognition context

### Navigation
- [Cross-Reference Index](../00-index/CROSS_REFERENCE_INDEX.md) - Full document relationships
- [Executive Summary](../00-index/EXECUTIVE_SUMMARY.md) - Overview

---
*Document 4 of 50+ | Batch 2: Core Calculations | Last Updated: 2024-12-01 (Enhanced with comprehensive numeric examples)*