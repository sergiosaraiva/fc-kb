# Intercompany Dividend Eliminations

## Document Metadata
- **Category**: Elimination Entries
- **Theory Source**: Knowledge base chunks: 1185-1195, 1256, 1265, 1267, 1280
- **Implementation Files**:
  - `Sigma.Database/dbo/Stored Procedures/P_CONSO_ELIM_DIVIDEND.sql` - S020: Dividend elimination
- **Last Updated**: 2024-12-01
- **Completeness**: 95% (Full dividend elimination with POV support)
- **Compliance Status**: IAS 27, IFRS 10 - Intercompany dividend treatment

## Executive Summary

Intercompany dividends received from subsidiaries must be eliminated in consolidation to avoid double-counting income. Prophix.Conso implements a comprehensive dividend elimination (S020) that processes both final and interim dividends, distinguishes between dividends from Global/Proportional vs Equity method companies, and supports Point of View (POV) based elimination routing.

### Visual: 4-Line Dividend Elimination Pattern

```
┌─────────────────────────────────────────────────────────────────────────────┐
│              DIVIDEND ELIMINATION JOURNAL PATTERN (S020)                     │
└─────────────────────────────────────────────────────────────────────────────┘

  BEFORE CONSOLIDATION                    AFTER ELIMINATION
  ─────────────────────                   ─────────────────────

  PARENT P&L:                             PARENT P&L:
  ┌─────────────────────┐                 ┌─────────────────────┐
  │ Dividend Income: 80 │      ───►       │ Dividend Income: 0  │  (Eliminated)
  │ Other Income:   200 │                 │ Other Income:   200 │
  │ Total:          280 │                 │ Total:          200 │
  └─────────────────────┘                 └─────────────────────┘

  4-LINE ELIMINATION JOURNAL:
  ┌───────┬──────────────────────┬─────────────────┬─────────┬───────────────┐
  │ Line  │ Account              │ Flow            │ Amount  │ Purpose       │
  ├───────┼──────────────────────┼─────────────────┼─────────┼───────────────┤
  │   1   │ DivReceived (P&L)    │ -               │  Dr 80  │ Remove income │
  │   2   │ PLINC                │ -               │  Cr 80  │ P&L bridge    │
  │   3   │ PLBAL                │ ThisPeriodProfit│  Dr 80  │ B/S bridge    │
  │   4   │ RetainedEarnings     │ DIVIDENDS       │  Cr 80  │ Restore res.  │
  └───────┴──────────────────────┴─────────────────┴─────────┴───────────────┘
                                        │
                                        │ Net Effect = 0 (Balanced)
                                        ▼

  FLOW OF FUNDS (Conceptual):
  ┌─────────────────┐         ┌─────────────────┐         ┌─────────────────┐
  │   SUBSIDIARY    │  ───►   │   INTERCOMPANY  │  ───►   │     PARENT      │
  │ Declares div    │  cash   │   ELIMINATION   │ remove  │ Shows income    │
  │ Reduces equity  │         │   (S020 Entry)  │         │ Double-counted! │
  └─────────────────┘         └─────────────────┘         └─────────────────┘
         │                            │                          │
         │ Retained earnings          │ 4-line journal           │ Dividend income
         │ already reduced            │ removes both             │ should not exist
         ▼                            ▼                          ▼
  ┌─────────────────────────────────────────────────────────────────────────┐
  │              CONSOLIDATED RESULT: Profit counted once only              │
  └─────────────────────────────────────────────────────────────────────────┘

  PERCENTAGE CALCULATION:
  ┌───────────────────────────────────────────────────────────────────────┐
  │ Elimination Amount = Dividend × Direct FinPercentage                  │
  │                                                                       │
  │ Example: Sub declares 100 dividend, Parent owns 80%                   │
  │ Elimination = 100 × 80% = 80 (Parent's share of dividend)             │
  └───────────────────────────────────────────────────────────────────────┘
```

## Theoretical Framework

### Concept Definition

When a subsidiary declares a dividend:
1. **Subsidiary**: Records dividend payable and reduction in retained earnings
2. **Parent**: Records dividend receivable and dividend income
3. **Consolidation**: Both entries must be eliminated as they represent intra-group transfers

### Why Eliminate Dividends?

```
Without Elimination:
- Parent shows dividend income: 100
- Subsidiary shows profit that generated dividend: 100
- Group would show: 200 (double-counted)

With Elimination:
- Dividend income removed from Parent P&L
- Profit retained only once in consolidated retained earnings
- Group shows: 100 (correct)
```

### Key Principles

1. **Timing**: Dividends from prior year profits affect opening retained earnings
2. **Interim vs Final**: Different flows for interim and final dividends
3. **Method-Specific**: Global/Proportional use DivReceived; Equity uses DivReceivedEquity
4. **Percentage**: Eliminate at direct ownership percentage (FinPercentage)

## Current Implementation

### Elimination Code

| ElimCode | Description | Procedure |
|----------|-------------|-----------|
| S020 | Dividend Elimination | P_CONSO_ELIM_DIVIDEND |

### Special Accounts and Flows

From `P_CONSO_ELIM_DIVIDEND.sql` (lines 154-176):

```sql
-- Special Accounts
select @DividendReceived       = dbo.UDF_GET_SPECIAL_ACCOUNT(@ConsoID, 'DivReceived')      -- G/P companies
select @DividendReceivedEquity = dbo.UDF_GET_SPECIAL_ACCOUNT(@ConsoID, 'DivReceivedEquity') -- E companies
select @RetainedEarnings       = dbo.UDF_GET_SPECIAL_ACCOUNT(@ConsoID, 'RetainedEarnings')
select @PLBALCur               = dbo.UDF_GET_SPECIAL_ACCOUNT(@ConsoID, 'PLBAL')
select @PLINCCur               = dbo.UDF_GET_SPECIAL_ACCOUNT(@ConsoID, 'PLINC')

-- Special Flows
select @DividendsFlowID        = dbo.UDF_GET_SPECIAL_FLOW(@ConsoID, 'DIVIDENDS')
select @InterimDividendsFlowID = dbo.UDF_GET_SPECIAL_FLOW(@ConsoID, 'INTERIMDIVIDENDS')
select @ProfitFlowID           = dbo.UDF_GET_SPECIAL_FLOW(@ConsoID, 'ThisPeriodProfitLoss')
select @ReservesAdjFlowID      = dbo.UDF_GET_SPECIAL_FLOW(@ConsoID, 'ReservesAdj')
```

### Four-Line Elimination Entry

The elimination creates a balanced 4-line journal entry:

| Line | Account | Flow | Amount | Description |
|------|---------|------|--------|-------------|
| 1 | DivReceived (P&L) | - | +Amt | Remove dividend income |
| 2 | PLINC | - | -Amt | Reverse P&L impact |
| 3 | PLBAL | ProfitFlowID | +Amt | Bridge to B/S |
| 4 | RetainedEarnings | DividendsFlow | -Amt | Restore to reserves |

### Final Dividend Processing

From lines 267-338:

```sql
-- Retrieve data for Final Dividend (Global + Proportional)
Insert into #ELIM_DIVIDENDS (...)
Select
    @ConsoID as [ConsoID],
    o.CurCompanyID as [SelectedCompanyID],
    1 as [LineNr],
    o.CurCompanyID as [ToCompanyID],
    -- Account selection based on method
    Case when ISNULL(MAX(o.CurConsoMethodOwned), 'N') <> 'E'
         then @DividendReceived
         else @DividendReceivedEquity
    end as [ToAccountID],
    d.CompanyID as [ToPartnerCompanyID],
    -- Calculate at reference period percentage
    sum(d.Amount) * ISNULL(o.RefCompanyFinPerc, 0) / 100 as [Amount],
    @DividendsFlowID as [FromFlowID]
From
    #Ownership o
    inner join dbo.TD045C2 d
        on (d.ConsoID = @ConsoID
            AND d.CompanyID = o.CurCompanyOwnedID
            AND d.FlowID = @DividendsFlowID)
    inner join @JournalTable j on (j.JournalID = d.JournalTypeID)
Where d.CurrCode = @ConsoCurrCode
Group By o.CurCompanyID, d.CompanyID, o.RefCompanyFinPerc
```

### Interim Dividend Processing

Interim dividends use current period percentage (lines 340-411):

```sql
-- Interim Dividend uses CurCompanyFinPerc (current percentage)
sum(d.Amount) * ISNULL(o.CurCompanyFinPerc, 0) / 100 as [Amount],
@InterimDividendsFlowID as [FromFlowID]
```

### POV-Based Elimination

Supports multi-level legal structure elimination (lines 628-804):

```sql
If @POVConfig = 1  -- POV configuration enabled
Begin
    -- Build POV hierarchy tree
    ;with tbParent as (...)

    -- Route elimination to appropriate journal based on POV level
    Update a
        set a.JournalTypeID = b.TargetJournalTypeID
    From dbo.TMP_TD035C2 a
         inner join @AlternateTarget b on b.CompanyID = a.CompanyID
                                      and b.PartnerCompanyID = a.PartnerCompanyID
    Where a.SessionID = @SessionID
      and a.Step = 120
      and b.TargetJournalTypeID is not null
End
```

### Ownership Tracking

The procedure tracks ownership changes between periods:

```sql
create table #Ownership (
    CurCompanyID int,           -- Current period owner
    RefCompanyID int,           -- Reference period owner
    CurConsoMethod char(1),     -- Current consolidation method
    RefConsoMethod char(1),     -- Reference period method
    CurCompanyOwnedID int,      -- Current owned company
    RefCompanyOwnedID int,      -- Reference owned company
    CurCompanyFinPerc decimal,  -- Current financial percentage
    RefCompanyFinPerc decimal   -- Reference financial percentage
)
```

## Theory vs Practice Analysis

| Aspect | Theory | Prophix.Conso Implementation | Alignment |
|--------|--------|------------------------------|-----------|
| Dividend Income Elimination | Remove from parent P&L | DivReceived/DivReceivedEquity accounts | Full |
| Retained Earnings | Restore to reserves | RetainedEarnings flow-level adjustment | Full |
| Interim vs Final | Different timing | Separate flows (DIVIDENDS, INTERIMDIVIDENDS) | Full |
| Method Distinction | G/P vs E treatment | Account selection by ConsoMethod | Full |
| Ownership % | Use direct financial % | FinPercentage from TS015S0 | Full |
| Period Changes | Handle % changes | RefCompanyFinPerc vs CurCompanyFinPerc | Full |

## Gap Analysis

### Missing Elements

1. **Dividend History**: No explicit tracking of dividend declaration history

### Additional Features (Beyond Theory)

1. **POV Support**: Multi-level legal structure routing
2. **Dual Percentage Handling**: Reference vs current period percentages
3. **Equity Method Separation**: Distinct account for equity method dividends

## Business Impact

1. **Accurate P&L**: Prevents double-counting of dividend income
2. **Flow Analysis**: Clear dividend flow tracking
3. **Method Compliance**: Correct treatment per consolidation method

## Appendix: Comprehensive Dividend Elimination Examples

### Example 1: Basic Final Dividend Elimination (Global Integration)

**Scenario**:
- Parent P owns 80% of Subsidiary S
- S declares final dividend of 500 from prior year profits
- P's share of dividend = 80% × 500 = 400

**Before Elimination - Entity Level**:

| Company | Account | Amount | Description |
|---------|---------|--------|-------------|
| Sub S | Dividends Payable | 500 | Liability to shareholders |
| Sub S | Retained Earnings | (500) | Reduction in reserves |
| Parent P | Dividend Receivable | 400 | Asset for dividend due |
| Parent P | Dividend Income (P&L) | 400 | Income recognition |

**Problem**: P's consolidated P&L shows 400 dividend income PLUS S's underlying profit already consolidated = double counting.

**Four-Line Elimination Entry (S020)**:

```
Line 1: Remove dividend income from Parent P&L
Dr  DivReceived (P&L account)                400
    Flow: (-)

Line 2: Reverse P&L impact on profit for the period
    Cr  PLINC (P&L result bridge)                 400
    Flow: (-)

Line 3: Bridge to Balance Sheet
Dr  PLBAL (B/S result bridge)                400
    Flow: ThisPeriodProfitLoss

Line 4: Restore to retained earnings (where dividend originated)
    Cr  RetainedEarnings                          400
    Flow: DIVIDENDS
```

**Verification**:
```
Debits:   400 (Line 1) + 400 (Line 3) = 800
Credits:  400 (Line 2) + 400 (Line 4) = 800
Balance:  ✓

P&L Impact: +400 - 400 = 0 (dividend income fully reversed)
B/S Impact: +400 - 400 = 0 (retained earnings restored via flow)
```

### Example 2: Multi-Tier Dividend Elimination

**Scenario**:
```
        ┌─────────┐
        │ Parent P │
        └────┬────┘
             │ 75%
             ▼
        ┌─────────┐
        │  Sub A  │
        └────┬────┘
             │ 80%
             ▼
        ┌─────────┐
        │  Sub B  │  Declares dividend of 1,000
        └─────────┘
```

**Dividend Flow**:
```
B declares dividend:                        1,000
  → A receives (80%):                         800
  → External minority receives (20%):         200

A may then distribute to P:
  → P receives (75% of A):                    600
  → A's external minority (25%):              200

But for elimination purposes, we trace direct ownership:
  P's effective ownership of B: 75% × 80% =    60%
  P's share of B's dividend: 60% × 1,000 =    600
```

**Elimination Entries**:

**Entry 1: Eliminate A's dividend income from B**
```
Dr  DivReceived (A)                          800
    Cr  PLINC (A)                                 800
Dr  PLBAL (A)                                800
    Cr  RetainedEarnings (B via A)               800
```

**Entry 2: Eliminate P's dividend income from A** (if A distributed)
```
Dr  DivReceived (P)                          600
    Cr  PLINC (P)                                 600
Dr  PLBAL (P)                                600
    Cr  RetainedEarnings (A via P)               600
```

**Note**: The system processes at each ownership level, not effective percentage.

### Example 3: Interim vs Final Dividend Treatment

**Scenario**:
- Ownership changed mid-year: 60% → 80%
- Sub S declares:
  - Final dividend (prior year): 500
  - Interim dividend (current year): 200

**Reference Period Percentage**: 60% (for final dividend from prior year)
**Current Period Percentage**: 80% (for interim dividend)

**Final Dividend Elimination** (uses RefCompanyFinPerc):
```
P's share: 60% × 500 = 300

Dr  DivReceived                              300
    Cr  PLINC                                     300
Dr  PLBAL                                    300
    Cr  RetainedEarnings (DIVIDENDS flow)        300
```

**Interim Dividend Elimination** (uses CurCompanyFinPerc):
```
P's share: 80% × 200 = 160

Dr  DivReceived                              160
    Cr  PLINC                                     160
Dr  PLBAL                                    160
    Cr  RetainedEarnings (INTERIMDIVIDENDS flow) 160
```

### Example 4: Equity Method Dividend Elimination

**Scenario**:
- Parent P has 30% stake in Associate A (Equity Method)
- A declares dividend of 1,000
- P's share: 30% × 1,000 = 300

**Key Difference**: Uses `DivReceivedEquity` account instead of `DivReceived`.

**Elimination Entry**:
```
Dr  DivReceivedEquity (P&L account)          300
    Cr  PLINC                                     300
Dr  PLBAL                                    300
    Cr  RetainedEarnings (DIVIDENDS flow)        300
```

**Why Separate Account?**:
- Equity method already recognizes share of associate's profit
- Dividend is return of investment, not additional income
- Separate account allows clear audit trail and reporting

### Example 5: POV-Based Dividend Routing

**Scenario**: Multi-level legal structure with POV
```
        ┌─────────────┐
        │  Group G    │  (Reporting Entity)
        └──────┬──────┘
               │
    ┌──────────┼──────────┐
    ▼          ▼          ▼
┌───────┐  ┌───────┐  ┌───────┐
│ H1    │  │ H2    │  │ H3    │  (Sub-holding companies)
│ (POV1)│  │ (POV2)│  │ (POV3)│
└───┬───┘  └───┬───┘  └───┬───┘
    │          │          │
    ▼          ▼          ▼
┌───────┐  ┌───────┐  ┌───────┐
│ Op1   │  │ Op2   │  │ Op3   │  (Operating companies)
└───────┘  └───────┘  └───────┘
```

**POV Routing**: When Op1 pays dividend to H1, elimination routes to H1's journal:
```sql
-- POV routing logic (simplified)
If dividend is paid to POV entity (H1, H2, H3):
    Route elimination to POV entity's journal
Else:
    Route to standard consolidation journal
```

**Benefit**: Allows sub-consolidation reporting at each POV level.

### Summary: Dividend Elimination Journal Entry Structure

| Line | Direction | Account | Flow | Purpose |
|------|-----------|---------|------|---------|
| 1 | Debit | DivReceived / DivReceivedEquity | - | Remove dividend income from P&L |
| 2 | Credit | PLINC | - | Reverse P&L profit bridge |
| 3 | Debit | PLBAL | ThisPeriodProfitLoss | Bridge to B/S |
| 4 | Credit | RetainedEarnings | DIVIDENDS / INTERIMDIVIDENDS | Restore reserves at source |

**Key Points**:
- Lines 1+2 neutralize P&L impact
- Lines 3+4 handle B/S bridge via flows
- Final dividends use reference period %
- Interim dividends use current period %
- Equity method uses separate DivReceivedEquity account

## API Reference

### Primary API Handlers
| Handler | YAML File | Purpose | Status |
|---------|-----------|---------|--------|
| `Consolidation_Execute` | [api-consolidation-endpoints.yaml](../11-agent-support/api-consolidation-endpoints.yaml) | Trigger P_CONSO_ELIM_DIVIDEND | ✅ IMPLEMENTED |
| `Elimination_GetEliminations` | [api-elimination-endpoints.yaml](../11-agent-support/api-elimination-endpoints.yaml) | Get dividend elimination details | ✅ IMPLEMENTED |

### Supporting API Handlers
| Handler | YAML File | Purpose |
|---------|-----------|---------|
| `DataEntry_GetData` | [api-data-entry-endpoints.yaml](../11-agent-support/api-data-entry-endpoints.yaml) | Get dividend flow amounts |
| `FlowData_SaveData` | [api-flow-endpoints.yaml](../11-agent-support/api-flow-endpoints.yaml) | Enter dividend flows (DIVIDENDS, INTERIMDIVIDENDS) |
| `Ownership_GetOwnership` | [api-ownership-endpoints.yaml](../11-agent-support/api-ownership-endpoints.yaml) | Get FinPercentage for elimination |

### Elimination Code Reference
| Code | Handler | Procedure | Purpose |
|------|---------|-----------|---------|
| S020 | Dividend Elimination | P_CONSO_ELIM_DIVIDEND | Eliminate intercompany dividends |

### API Workflow
```
Dividend Elimination via API:

1. DATA ENTRY
   FlowData_SaveData → Enter dividend amounts with flows:
     - DIVIDENDS (final)
     - INTERIMDIVIDENDS (interim)

2. OWNERSHIP VERIFICATION
   Ownership_GetOwnership → Verify FinPercentage:
     - CurCompanyFinPerc (for interim)
     - RefCompanyFinPerc (for final)

3. ELIMINATION EXECUTION
   Consolidation_Execute → P_CONSO_ELIM → P_CONSO_ELIM_DIVIDEND:
     - Account selection by ConsoMethod (G/P/E)
     - 4-line journal entry creation
     - POV routing (if configured)

4. VERIFICATION
   Elimination_GetEliminations → Verify S020 entries:
     - Line 1: Dr DivReceived/DivReceivedEquity
     - Line 2: Cr PLINC
     - Line 3: Dr PLBAL (ThisPeriodProfitLoss)
     - Line 4: Cr RetainedEarnings (DIVIDENDS)
```

### Implementation Status
| Feature | Status | Notes |
|---------|--------|-------|
| Final dividend elimination | ✅ IMPLEMENTED | Uses RefCompanyFinPerc |
| Interim dividend elimination | ✅ IMPLEMENTED | Uses CurCompanyFinPerc |
| Method-specific accounts | ✅ IMPLEMENTED | DivReceived vs DivReceivedEquity |
| POV-based routing | ✅ IMPLEMENTED | Multi-level legal structure |
| 4-line balanced entry | ✅ IMPLEMENTED | P&L and B/S impact |

### Related API Documentation
- [API Index](../11-agent-support/api-index.yaml) - Master handler catalog
- [Gap Analysis](../11-agent-support/gap-analysis-report.yaml) - **FULLY IMPLEMENTED (95%)**

---

## Related Documentation

- [Participation Eliminations](participation-eliminations.md) - Investment eliminations
- [Intercompany Transactions](intercompany-transactions.md) - General IC eliminations
- [Equity Method](../02-consolidation-methods/equity-method.md) - Equity method specifics
- [Dividend Calculation Logic](dividend-calculation-logic.md) - FinPercentage calculation

### Navigation
- [Cross-Reference Index](../00-index/CROSS_REFERENCE_INDEX.md) - Find related documents
- [Quick Reference Card](../20-appendices/quick-reference-card.md) - S020 elimination code
- [Troubleshooting Guide](../17-troubleshooting/common-issues.md) - Dividend issues
- [Glossary](../20-appendices/glossary.md) - Term definitions

---
*Document 17 of 50+ | Batch 6: Elimination Entries | Last Updated: 2024-12-01 (Enhanced with comprehensive numeric examples)*
