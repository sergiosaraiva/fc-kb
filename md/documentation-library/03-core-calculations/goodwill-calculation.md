# Goodwill Calculation

## Document Metadata
- **Category**: Core Calculation
- **Theory Source**: Knowledge base chunks: 0041, 0269, 0731, 1120, 1206, 1281
- **Implementation Files**:
  - `Sigma.Database/dbo/Stored Procedures/P_REPORT_GOODWILL.sql`
  - `Sigma.Database/dbo/Stored Procedures/P_REPORT_GOODWILL_HEADER.sql`
  - `Sigma.Database/dbo/Tables/TS010P0.sql` (Participation Accounts)
  - `Sigma.Database/dbo/Views/V_ACCOUNT_PARTICIPATION.sql`
- **Last Updated**: 2024-12-01
- **Completeness**: 85% (reporting implemented, manual adjustment workflow)
- **Compliance Status**: IFRS 3 (Business Combinations) aligned

## Executive Summary

Goodwill represents the excess of the acquisition price paid for a subsidiary over the fair value of its identifiable net assets. It arises when a parent company acquires control of a subsidiary and pays more than the book value of the acquired company's equity, typically reflecting intangible factors like market position, synergies, or brand value.

Prophix.Conso implements goodwill tracking through a **reporting and adjustment workflow** rather than automatic calculation. The system provides a comprehensive goodwill report (`P_REPORT_GOODWILL`) that calculates goodwill based on acquisition values and equity positions, with adjustments managed through consolidation journals.

## Theoretical Framework

### Concept Definition
From Allen White's "Direct Consolidation" (Chunk 0041):

> We consider the parent company acquiring 100% of a new company for a price of 100. Equity of the acquired company is 80.
>
> There will be a **goodwill of 20**, which is the difference between the acquisition price of 100 and 100% of the equity of 80.
>
> In parent company, we have to book a goodwill of 20 and, depending on the evaluation rules, to depreciate this goodwill or to book an impairment on this goodwill.

### Key Principles

1. **Basic Formula**: Goodwill = Acquisition Price - (Ownership % × Fair Value of Net Assets)
2. **Fair Value Adjustments**: Before calculating goodwill, the acquired company's assets must be adjusted to fair value
3. **Impairment Testing**: Under IFRS, goodwill is not depreciated but must be tested annually for impairment
4. **Persistence**: Goodwill adjustments remain in consolidation accounting for long periods and must be well documented
5. **Transfer on Disposal**: When ownership changes within the group, goodwill must be transferred to the new owner

### Visual: Goodwill Calculation Flow

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    GOODWILL CALCULATION OVERVIEW                             │
└─────────────────────────────────────────────────────────────────────────────┘

  ACQUISITION SCENARIO:
  ┌─────────────────────────────────────────────────────────────────────────┐
  │ Parent P acquires 80% of Subsidiary S for 120 cash                      │
  │ Subsidiary S has book equity of 100                                     │
  └─────────────────────────────────────────────────────────────────────────┘

  STEP 1: Calculate Share of Net Assets        STEP 2: Calculate Goodwill
  ───────────────────────────────────          ──────────────────────────────

  ┌───────────────────────────┐                ┌───────────────────────────┐
  │ Subsidiary S Equity       │                │ GOODWILL FORMULA          │
  ├───────────────────────────┤                ├───────────────────────────┤
  │ Share Capital:      50    │                │                           │
  │ Retained Earnings:  50    │                │ Acquisition Price    120  │
  │ ─────────────────────     │                │ Less: Share of Net   (80) │
  │ Total Equity:      100    │                │ Assets (80% × 100)        │
  └───────────────────────────┘                │ ─────────────────────     │
           │                                    │ GOODWILL              40  │
           │ × 80% ownership                    └───────────────────────────┘
           ▼
  ┌───────────────────────────┐
  │ Parent's Share:     80    │
  └───────────────────────────┘

  CONSOLIDATION ENTRY (Participation Elimination - S050):
  ┌───────┬──────────────────────────┬─────────┬───────────────────────────┐
  │ Line  │ Account                  │ Dr/(Cr) │ Purpose                   │
  ├───────┼──────────────────────────┼─────────┼───────────────────────────┤
  │   1   │ Share Capital (Sub)      │   (50)  │ Eliminate Sub equity      │
  │   2   │ Retained Earnings (Sub)  │   (50)  │ Eliminate Sub equity      │
  │   3   │ Investment in Sub (Par)  │  (120)  │ Eliminate investment      │
  │   4   │ Goodwill                 │    40   │ Record goodwill           │
  │   5   │ NCI (20% × 100)          │   (20)  │ Recognize NCI             │
  └───────┴──────────────────────────┴─────────┴───────────────────────────┘
                                         │
                                         │ Total = 0 (Balanced)
                                         ▼

  NCI CALCULATION (Minority Interest):
  ┌───────────────────────────────────────────────────────────────────────┐
  │ NCI = (100% - Parent %) × Subsidiary Equity                          │
  │ NCI = (100% - 80%) × 100 = 20                                        │
  │                                                                       │
  │ Options under IFRS 3:                                                 │
  │ • Full goodwill method: NCI at fair value (includes NCI goodwill)    │
  │ • Partial goodwill: NCI at share of net assets (no NCI goodwill)     │
  └───────────────────────────────────────────────────────────────────────┘

  IMPAIRMENT (IAS 36 - Annual Test Required):
  ┌─────────────────────────────────────────────────────────────────────────┐
  │ If Recoverable Amount < Carrying Amount → Impairment Loss              │
  │ Impairment reduces Goodwill (P&L expense) - CANNOT be reversed         │
  │                                                                         │
  │ ⚠️ GAP: Automatic impairment testing not implemented in Prophix.Conso  │
  │         Workaround: Manual user elimination journal                     │
  └─────────────────────────────────────────────────────────────────────────┘
```

### Formula/Algorithm

```
Basic Goodwill Calculation:

Goodwill = [A] - [B]

Where:
[A] = Acquisition Value (Purchase Price)
[B] = Equity Value at Acquisition

Detailed Breakdown:
[B] = (Bundle Value + Pre-acquisition Adjustments + Revaluation of Assets)
      × Ownership %
      + Post-acquisition Adjustments

Example from Theory:
- Acquisition Price: 100
- Ownership: 100%
- Net Assets (Equity): 80
- Goodwill = 100 - (100% × 80) = 20
```

### Advanced Scenarios (from Chunk 0731)

**Goodwill Transfer on Group Transactions:**
- When subsidiary ownership transfers within the group, goodwill follows
- Gross goodwill maintained at original value (not adjusted for new owner's percentage)
- All depreciation/impairment adjustments must also transfer
- Historical reserves transfer with goodwill

## Current Implementation

### Database Layer

#### Goodwill Report Structure

`P_REPORT_GOODWILL` calculates goodwill using a structured approach:

```sql
/*
Report Structure:
  SectionNr1  SectionNr2  Definition
  1           1           Acquired Company info
  2           1           Owner company info
  3           1           [Acquisition value]               [A]
  4           1           DATA - Bundle value                    (1)
  4           2           DATA - Adjustment before thirds        (2)
  4           3           Total equity before 3rd               (3) = (1)+(2)
  4           4           Revaluation of assets                 (4)
  4           5           Total before 3rd                      (5) = (3)+(4)
  4           6           % acquired                            (6)
  4           7           Equity acquired                       (7) = (5) * (6)/100
  4           8           DATA - Adjustments after 3rd          (8)
  4           9           Total equity                    [B]   = (7)+(8)
  5           1           Goodwill/Badwill            = [A]-[B]
*/

CREATE procedure [dbo].[P_REPORT_GOODWILL]
    @UserID                 int,
    @CustomerID             int,
    @ConsoID                int,
    @RefConsoID             int,           -- Reference period for comparison
    @DataLanguageLCID       int,
    @JournalViewCode        nvarchar(25),
    @OwnerCompanyIDs        nvarchar(max), -- Filter by owner companies
    @OwnedCompanyIDs        nvarchar(max), -- Filter by owned companies
    @AcquisitionFlowCode    nvarchar(3),
    @RevaluationOfAssetsCode nvarchar(12),
    @ProfitAtAcquisitionCode nvarchar(12),
    @ReportNr               int,
    @ReportType             int
```

#### Participation Accounts Table

`TS010P0` links accounts for participation tracking:

```sql
CREATE TABLE [dbo].[TS010P0] (
    [ParticipationAccountID] INT IDENTITY (1, 1) NOT NULL,
    [ConsoID]                INT NOT NULL,
    [AccountID]              INT NOT NULL,
    [Sequence]               INT NOT NULL,
    [AttachedAccountID]      INT NOT NULL,
    CONSTRAINT [PK_TS010P0] PRIMARY KEY CLUSTERED ([ConsoID], [ParticipationAccountID])
);
```

### Application Layer

Goodwill is managed through:
1. **Consolidation Adjustments**: Manual journal entries for goodwill booking
2. **Goodwill Report**: Analysis tool for goodwill calculations
3. **Journal Types**: Dedicated journals for goodwill-related adjustments

### Frontend Layer

The goodwill workflow is exposed through:
- **Goodwill Report Screen**: Multi-parameter report for analyzing goodwill positions
- **Adjustment Entry Screens**: For booking goodwill journals
- **Ownership Data Entry**: For recording acquisition prices and dates

## Theory vs Practice Analysis

| Aspect | Theory (Allen White) | Implementation (Prophix.Conso) | Variance |
|--------|---------------------|--------------------------------|----------|
| Basic Formula | Price - (% × Net Assets) | Full multi-step calculation | **Enhanced** - More detailed |
| Automatic Calculation | Implied | Report-based, manual adjustment | **Different** - More control |
| Fair Value Adjustment | Required before goodwill | Section 4 in report structure | **Aligned** |
| Depreciation | Not for IFRS | Manual impairment adjustments | **Aligned** |
| Transfer on Disposal | Detailed rules | Manual adjustment workflow | **Partial** - Requires expertise |
| Reference Period | Single period | Current vs Reference comparison | **Enhanced** |
| Multi-company Analysis | Not discussed | OwnerCompanyIDs/OwnedCompanyIDs filters | **Enhanced** |

## Gap Analysis

### Missing Elements
- [ ] **Automatic Goodwill Calculation**: Currently requires manual adjustment entry
- [ ] **Goodwill Impairment Testing Workflow**: No automated impairment test module
- [ ] **Step Acquisition Support**: Remeasurement of previous holdings not automated
- [ ] **Bargain Purchase (Negative Goodwill)**: Limited automation for gain recognition

### Divergent Implementation
- **Report-Based vs Automatic**: Theory implies automatic calculation; implementation uses reporting with manual adjustments for flexibility and audit control
- **Complexity Handling**: Implementation provides more granularity (before/after third party adjustments) than basic theory

### Additional Features (Beyond Theory)
- ✅ **Reference Period Comparison**: Compare goodwill between periods
- ✅ **Multi-company Filtering**: Analyze specific owner/owned combinations
- ✅ **Revaluation Tracking**: Separate tracking of asset revaluations
- ✅ **Acquisition Flow Codes**: Configurable acquisition event tracking
- ✅ **Profit at Acquisition**: Separate handling of acquired profits

## Business Impact

### Current Capabilities
- Full visibility into goodwill components
- Audit trail through journal-based adjustments
- Flexible reporting with multiple parameters
- Support for complex group structures

### Limitations
- Manual expertise required for goodwill booking
- Risk of inconsistency without automated calculation
- Impairment testing must be performed outside system

### Recommended Workflow
1. Record acquisition in ownership data entry
2. Run Goodwill Report to calculate initial goodwill
3. Book goodwill adjustment journal
4. Periodically run impairment analysis (external)
5. Book impairment adjustments as needed

## Recommendations

1. **Automation**: Consider adding automatic goodwill calculation on acquisition entry
2. **Impairment Module**: Build annual impairment testing workflow
3. **Step Acquisition**: Add remeasurement logic for incremental acquisitions
4. **Validation**: Add validation to ensure goodwill is booked for all acquisitions
5. **Documentation**: Enhance in-system help with IFRS 3 requirements

## Related Documentation
- See also: [Global Integration](../02-consolidation-methods/global-integration.md)
- See also: [Minority Interest](minority-interest.md)
- Knowledge Base: Chunks 0041, 0269, 0731
- Code: `P_REPORT_GOODWILL.sql:68-80`

## Appendix: Goodwill Calculation Examples

### Example 1: Basic Acquisition (80% Control)

**Scenario**:
- Parent P acquires 80% of Subsidiary S
- Acquisition price: 1,000
- S's book equity: 800
- Fair value adjustment on assets: +200

**Calculation**:
```
[A] Acquisition Value:                    1,000

[B] Equity Value Calculation:
    (1) Bundle value (book equity):         800
    (2) Pre-acquisition adjustments:          0
    (3) Total before revaluation:           800
    (4) Revaluation of assets:              200
    (5) Total before ownership %:         1,000
    (6) Ownership percentage:               80%
    (7) Equity acquired (5 × 6):            800
    (8) Post-acquisition adjustments:         0
    [B] Total equity value:                 800

Goodwill = [A] - [B] = 1,000 - 800 = 200
Minority Interest = 20% × 1,000 = 200
```

### Example 2: Comprehensive Acquisition with NCI Options (IFRS 3)

**Scenario**:
- Parent P acquires 75% of Target T on January 1, 2024
- Cash paid: 3,000
- T's balance sheet at acquisition:

| Item | Book Value | Fair Value | FV Adjustment |
|------|------------|------------|---------------|
| Property, Plant & Equipment | 1,500 | 2,000 | +500 |
| Intangible Assets (Brand) | 0 | 300 | +300 |
| Inventory | 400 | 450 | +50 |
| Receivables | 300 | 300 | 0 |
| Cash | 200 | 200 | 0 |
| **Total Assets** | **2,400** | **3,250** | **+850** |
| Liabilities | (600) | (600) | 0 |
| Deferred Tax on FV Adj | 0 | (212) | (212) |
| **Net Assets** | **1,800** | **2,438** | **+638** |

**Step 1: Calculate Goodwill - Proportionate NCI Method (Option A)**
```
Consideration transferred:                           3,000
NCI at proportionate share (25% × 2,438):             610
                                                    ------
Total:                                               3,610
Less: Fair value of net assets:                     (2,438)
                                                    ------
Goodwill:                                            1,172
```

**Step 2: Calculate Goodwill - Full Goodwill Method (Option B)**
```
Consideration transferred:                           3,000
NCI at fair value (assume market value):              950
                                                    ------
Total:                                               3,950
Less: Fair value of net assets:                     (2,438)
                                                    ------
Full Goodwill:                                       1,512

Of which:
  - Attributable to Parent (75%):                    1,134
  - Attributable to NCI (25%):                         378
```

**Step 3: Consolidated Balance Sheet Impact**

| Item | Option A (Proportionate) | Option B (Full Goodwill) |
|------|--------------------------|--------------------------|
| Goodwill | 1,172 | 1,512 |
| NCI | 610 | 950 |
| Group Equity Impact | Same | Same |

**Step 4: Record in Prophix.Conso**

```sql
-- Step 4a: Goodwill Adjustment Journal (using User Elimination)
INSERT INTO TS070S0 (ConsoID, ElimCode, ElimType, ElimText, Active, ...)
VALUES (@ConsoID, 'U001', 'U',
    'Goodwill on acquisition of Target T - 75% - Acq Date 2024-01-01 - Ref: ACQ-2024-001',
    1, ...);

-- Step 4b: Journal Detail Lines
-- Line 1: Recognize Goodwill Asset
INSERT INTO TS071S0 (EliminationHeaderID, LineNr, FromType, FromAccountID,
    ToAccountID, ToSign, ...)
VALUES (@HeaderID, 1, 1, @PlaceholderAccount, @GoodwillAccount, 1, ...);
-- Amount: 1,172 (or 1,512 for full goodwill method)

-- Step 4c: Fair Value Adjustment Elimination
INSERT INTO TS070S0 (ConsoID, ElimCode, ElimType, ElimText, ...)
VALUES (@ConsoID, 'U002', 'U',
    'FV Adjustments - Target T - PPE +500, Brand +300, Inventory +50, DTL -212', ...);
```

**Step 5: Verify with Goodwill Report**

Run `P_REPORT_GOODWILL` to confirm:
```
Section 3: Acquisition Value [A]:           3,000
Section 4:
  (1) Bundle value:                         1,800
  (4) Revaluation of assets:                  638
  (5) Total before %:                       2,438
  (6) % acquired:                             75%
  (7) Equity acquired:                      1,828
  [B] Total equity:                         1,828
Section 5: Goodwill = [A]-[B]:              1,172
```

### Example 3: Bargain Purchase (Negative Goodwill)

**Scenario**:
- Parent acquires 100% of distressed company D
- Cash paid: 500
- D's fair value net assets: 700

**Calculation**:
```
Consideration:                                500
Less: FV net assets × 100%:                 (700)
                                           ------
Negative Goodwill (Bargain Purchase):       (200)
```

**IFRS 3 Treatment**:
- Reassess identification of assets and measurement
- If still negative, recognize gain immediately in P&L

**System Entry**:
```sql
-- Bargain purchase gain elimination
INSERT INTO TS070S0 (ConsoID, ElimCode, ElimType, ElimText, ...)
VALUES (@ConsoID, 'U003', 'U',
    'Bargain Purchase Gain - Company D - IFRS 3.34 - P&L recognition', ...);

-- Debit: Equity/Investment | Credit: P&L Gain
```

### Goodwill Calculation Decision Tree

```
                    ┌─────────────────────────────────────┐
                    │   Acquisition Price vs FV Net Assets │
                    └─────────────────────────────────────┘
                                      │
                    ┌─────────────────┴─────────────────┐
                    │                                   │
              Price > FV × %                      Price < FV × %
                    │                                   │
                    ▼                                   ▼
            ┌──────────────┐                   ┌──────────────┐
            │   GOODWILL   │                   │   BARGAIN    │
            │  (positive)  │                   │   PURCHASE   │
            └──────────────┘                   └──────────────┘
                    │                                   │
        ┌───────────┴───────────┐              Recognize gain
        │                       │              immediately in P&L
   Option A              Option B
 Proportionate NCI     Full Goodwill NCI
        │                       │
   Lower NCI,            Higher NCI,
   Lower Goodwill        Higher Goodwill
```

## API Reference

### Primary API Handlers
| Handler | YAML File | Purpose | Status |
|---------|-----------|---------|--------|
| `Report_ExecuteReport` | [api-reports-endpoints.yaml](../11-agent-support/api-reports-endpoints.yaml) | Execute P_REPORT_GOODWILL | ✅ IMPLEMENTED |
| `Journal_SaveJournal` | [api-adjustment-endpoints.yaml](../11-agent-support/api-adjustment-endpoints.yaml) | Book goodwill adjustment | ✅ IMPLEMENTED |
| `Ownership_GetOwnership` | [api-ownership-endpoints.yaml](../11-agent-support/api-ownership-endpoints.yaml) | Get acquisition percentages | ✅ IMPLEMENTED |

### Supporting API Handlers
| Handler | YAML File | Purpose |
|---------|-----------|---------|
| `Elimination_GetEliminations` | [api-elimination-endpoints.yaml](../11-agent-support/api-elimination-endpoints.yaml) | Get S094 goodwill elimination |
| `Event_GetEvents` | [api-event-endpoints.yaml](../11-agent-support/api-event-endpoints.yaml) | Get acquisition events |
| `BundleStandard_GetDataEntry` | [api-data-entry-endpoints.yaml](../11-agent-support/api-data-entry-endpoints.yaml) | Get subsidiary net assets |

### API Workflow
```
1. Ownership_SaveOwnership → Record acquisition price
2. Report_ExecuteReport (GoodwillReport) → Calculate goodwill
3. Journal_SaveJournal → Book goodwill adjustment
4. Consolidation_Execute → S094 processes goodwill
```

### Implementation Status
| Feature | Status | Gap Reference |
|---------|--------|---------------|
| Goodwill Calculation | ✅ Report-based | - |
| Automatic Booking | ⚠️ PARTIAL | gap-analysis-report.yaml |
| Impairment Testing | ❌ NOT_IMPLEMENTED | Severity 8, IAS 36 |
| Step Acquisition | ❌ NOT_IMPLEMENTED | Severity 8, IFRS 3 |

### Related API Documentation
- [API Index](../11-agent-support/api-index.yaml) - Master handler catalog
- [Gap Analysis](../11-agent-support/gap-analysis-report.yaml) - **PARTIAL implementation (85%)**

---

## See Also

### Related Core Calculations
- [Step Acquisition](step-acquisition.md) - Goodwill on method transitions
- [Impairment Testing](impairment-testing.md) - Goodwill impairment
- [Minority Interest](minority-interest.md) - NCI measurement options
- [Deconsolidation](deconsolidation.md) - Goodwill release on disposal

### Related Eliminations
- [Participation Eliminations](../04-elimination-entries/participation-eliminations.md) - S050-S054 investment elimination
- [User Eliminations](../04-elimination-entries/user-eliminations.md) - Manual goodwill adjustments

### Related Methods
- [Global Integration](../02-consolidation-methods/global-integration.md) - Full consolidation context

### Navigation
- [Cross-Reference Index](../00-index/CROSS_REFERENCE_INDEX.md) - Full document relationships
- [Executive Summary](../00-index/EXECUTIVE_SUMMARY.md) - Overview

---
*Document 2 of 50+ | Batch 1: Foundation | Last Updated: 2024-12-01 (Enhanced with comprehensive numeric examples)*