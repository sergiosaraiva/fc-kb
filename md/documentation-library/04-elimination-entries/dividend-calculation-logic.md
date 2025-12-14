# Dividend Calculation Logic: Elimination Processing Details

## Document Metadata
- **Category**: Elimination Entries
- **Theory Source**: Knowledge base chunks: 1185-1195, 1256, 1265, 1267, 1280
- **Implementation Files**:
  - `Sigma.Database/dbo/Stored Procedures/P_CONSO_ELIM_DIVIDEND.sql` - S020 elimination
  - `Sigma.Database/dbo/Tables/TS070S0.sql` - Elimination header
  - `Sigma.Database/dbo/Tables/TS070S1.sql` - Company selection
  - `Sigma.Database/dbo/Functions/UDF_GET_SPECIAL_ACCOUNT.sql` - Special account lookup
  - `Sigma.Database/dbo/Functions/UDF_GET_SPECIAL_FLOW.sql` - Special flow lookup
- **Last Updated**: 2024-12-01
- **Completeness**: 100% (Full calculation logic documented)
- **Compliance Status**: IAS 27, IFRS 10 - Intercompany dividend treatment

## Executive Summary

The dividend elimination (S020) in Prophix.Conso processes intercompany dividends received from subsidiaries to prevent double-counting of income. The calculation logic distinguishes between Global/Proportional and Equity method companies, handles both final and interim dividends, and applies direct ownership percentages (FinPercentage) from the ownership structure.

## Calculation Architecture

### Processing Flow

```
P_CONSO_ELIM_DIVIDEND
        │
        ▼
┌─────────────────────────────────────────────────────────────────┐
│  Step 1: Configuration Retrieval                                 │
│  - Get S020 elimination definition from TS070S0                 │
│  - Load special accounts: DivReceived, DivReceivedEquity        │
│  - Load special flows: DIVIDENDS, INTERIMDIVIDENDS              │
└─────────────────────────────────────────────────────────────────┘
        │
        ▼
┌─────────────────────────────────────────────────────────────────┐
│  Step 2: Ownership Data Collection                               │
│  - Build #Ownership temp table                                   │
│  - Get direct FinPercentage from TS015S0                        │
│  - Map current/reference period ownership                        │
└─────────────────────────────────────────────────────────────────┘
        │
        ▼
┌─────────────────────────────────────────────────────────────────┐
│  Step 3: Dividend Amount Calculation                             │
│  - Read dividend flows from TD045C2                              │
│  - Calculate elimination amount = Dividend × FinPercentage      │
│  - Handle both DIVIDENDS and INTERIMDIVIDENDS flows             │
└─────────────────────────────────────────────────────────────────┘
        │
        ▼
┌─────────────────────────────────────────────────────────────────┐
│  Step 4: Journal Entry Generation                                │
│  - Create 4-line balanced entry in #ELIM_DIVIDENDS              │
│  - Route to appropriate accounts based on consolidation method  │
│  - Post to TMP_TD035C2 / TMP_TD045C2                            │
└─────────────────────────────────────────────────────────────────┘
```

## Special Accounts and Flows

### Required Special Accounts

| Code | Description | Usage |
|------|-------------|-------|
| DivReceived | Dividend Income (P&L) | G/P method companies |
| DivReceivedEquity | Dividend Income for Equity | E method companies |
| RetainedEarnings | Retained Earnings | Equity impact |
| PLBAL | P&L to Balance | Balance sheet tie-out |
| PLINC | P&L Income Impact | Result transfer |

### Required Special Flows

| Code | Description | Usage |
|------|-------------|-------|
| DIVIDENDS | Final Dividends | Year-end dividends |
| INTERIMDIVIDENDS | Interim Dividends | Mid-year dividends |
| ThisPeriodProfitLoss | Current Period P&L | Result flow |
| ReservesAdj | Reserves Adjustment | Equity adjustments |

### Configuration Retrieval

```sql
-- From P_CONSO_ELIM_DIVIDEND (lines 154-176)
select @DividendReceived       = dbo.UDF_GET_SPECIAL_ACCOUNT(@ConsoID, 'DivReceived')
select @DividendReceivedEquity = dbo.UDF_GET_SPECIAL_ACCOUNT(@ConsoID, 'DivReceivedEquity')
select @RetainedEarnings       = dbo.UDF_GET_SPECIAL_ACCOUNT(@ConsoID, 'RetainedEarnings')
select @PLBALCur               = dbo.UDF_GET_SPECIAL_ACCOUNT(@ConsoID, 'PLBAL')
select @PLINCCur               = dbo.UDF_GET_SPECIAL_ACCOUNT(@ConsoID, 'PLINC')

select @DividendsFlowID        = dbo.UDF_GET_SPECIAL_FLOW(@ConsoID, 'DIVIDENDS')
select @InterimDividendsFlowID = dbo.UDF_GET_SPECIAL_FLOW(@ConsoID, 'INTERIMDIVIDENDS')
select @ProfitFlowID           = dbo.UDF_GET_SPECIAL_FLOW(@ConsoID, 'ThisPeriodProfitLoss')
select @ReservesAdjFlowID      = dbo.UDF_GET_SPECIAL_FLOW(@ConsoID, 'ReservesAdj')
```

## Ownership Data Structure

### #Ownership Temp Table

```sql
create table #Ownership (
    pk int identity,
    CurCompanyID int,              -- Parent receiving dividend
    RefCompanyID int,
    CurConsoMethod char(1),        -- G/P/E/N
    RefConsoMethod char(1),
    CurCompanyOwnedID int,         -- Subsidiary paying dividend
    RefCompanyOwnedID int,
    CurConsoMethodOwned char(1),
    RefConsoMethodOwned char(1),
    CurCompanyFinPerc decimal(24,6),  -- Direct ownership %
    RefCompanyFinPerc decimal(24,6)
)
```

### Ownership Percentage Source

```sql
-- Direct ownership from TS015S0
SELECT
    CompanyID,           -- Owner
    CompanyOwnedID,      -- Owned subsidiary
    FinPercentage        -- Direct financial %
FROM TS015S0
WHERE ConsoID = @ConsoID
```

## Elimination Amount Calculation

### Basic Formula

```
Elimination Amount = Dividend Received × Direct Ownership Percentage
```

### Method-Specific Routing

| Consolidation Method | Dividend Account | Logic |
|---------------------|------------------|-------|
| G (Global) | DivReceived | Full elimination |
| P (Proportional) | DivReceived | Proportional elimination |
| E (Equity) | DivReceivedEquity | Equity method treatment |

### Flow-Based Calculation

```sql
-- Dividend amount from flows
SELECT
    CompanyID,
    PartnerCompanyID,
    FlowID,
    Amount
FROM TD045C2
WHERE ConsoID = @ConsoID
    AND FlowID IN (@DividendsFlowID, @InterimDividendsFlowID)
    AND JournalTypeID IN (SELECT JournalID FROM @JournalTable)
```

## Four-Line Journal Entry

### Entry Structure

```
Journal Entry: S020 - Dividend Elimination
────────────────────────────────────────────────────────────────
Line 1: Dr. DivReceived (P&L)              +Amount
        Remove dividend income from parent P&L

Line 2: Cr. PLINC                          -Amount
        Reverse income statement impact

Line 3: Dr. RetainedEarnings (via Flow)    +Amount (Reference)
        Adjust opening retained earnings

Line 4: Cr. Reserves Adjustment            -Amount (Reference)
        Balance equity movement
────────────────────────────────────────────────────────────────
Net Balance: 0 (Balanced entry)
```

### Entry Storage Structure

```sql
create table #ELIM_DIVIDENDS (
    ConsoID int,
    ElimHeaderID int,
    ElimDetailID int,
    SelectedCompanyID int,
    LineNr int,
    ToType tinyint,
    ToCompanyID int,
    ToAccountID int,
    ToFlowID int,
    ToPartnerCompanyID int,
    ToDimensionGroupID int,
    ToDim1DetailID int,
    ToDim2DetailID int,
    ToDim3DetailID int,
    Amount decimal(24,6),
    FromFlowID int
)
```

## Period-Specific Logic

### Current vs Reference Period

| Period | Treatment | Flow |
|--------|-----------|------|
| Current | Eliminate current year dividends | DIVIDENDS |
| Reference | Reverse prior year impact | ReservesAdj |

### Behaviour Setting

The S020 elimination typically uses `Behaviour = 3` (Both periods separately):
- Process reference period elimination first
- Then process current period elimination
- Ensures proper carry-forward of prior year impact

## Validation and Error Handling

### Required Configuration Checks

```sql
-- Validate special accounts exist
if @DividendReceived is null
    set @errorinfo = dbo.AddError2('SPECIFIC_ACCOUNT_NOT_FOUND',
        'DivReceived', 'Dividend Received', @errorinfo)

-- Validate special flows exist
if @DividendsFlowID is null
    set @errorinfo = dbo.AddError2('SPECIFIC_FLOW_NOT_FOUND',
        'DIVIDENDS', 'Dividend paid', @errorinfo)

-- Check for S020 elimination definition
if @@rowcount = 0
    raiserror ('Elimination with code S020 not found', 16, 1)
```

### Error Exit Pattern

```sql
if dbo.HasError(@errorinfo) = 1
    goto CleanupAndEnd
```

## Point of View (POV) Support

### POV-Based Routing

The dividend elimination supports POV-based posting:
- `PostingCompanyType = 'C'`: Post to company receiving dividend
- `PostingCompanyType = 'P'`: Post to partner (subsidiary)

### POV Configuration

```sql
-- From TS070S0 elimination header
@PostingCompanyType char(1)  -- C=Company, P=Partner
@PostingCompanyID int        -- Specific company if applicable
```

## Practical Example

### Scenario

```
Parent A owns 80% of Subsidiary B
Subsidiary B declares dividend of 1,000,000
Parent A receives 800,000 (80% × 1,000,000)
```

### Elimination Entry

```
Before Elimination:
- Parent A shows: Dividend Income = 800,000
- Subsidiary B shows: Retained Earnings reduced by 1,000,000
- Group P&L double-counts the income

Elimination Entry:
  Dr. Dividend Received (P&L)     800,000
    Cr. PLINC                     800,000

  (Reference period - opening reserves adjustment)
  Dr. Retained Earnings (Opening) 800,000
    Cr. Reserves Adjustment       800,000

After Elimination:
- Group P&L correctly shows Subsidiary B's profit only once
- Dividend income removed from Parent A
- Retained earnings properly stated at group level
```

## API Reference

### Primary API Handlers
| Handler | YAML File | Purpose | Status |
|---------|-----------|---------|--------|
| `Consolidation_Execute` | [api-consolidation-endpoints.yaml](../11-agent-support/api-consolidation-endpoints.yaml) | Execute P_CONSO_ELIM_DIVIDEND calculation | ✅ IMPLEMENTED |
| `FlowData_GetData` | [api-flow-endpoints.yaml](../11-agent-support/api-flow-endpoints.yaml) | Get dividend flow amounts from TD045C2 | ✅ IMPLEMENTED |

### Supporting API Handlers
| Handler | YAML File | Purpose |
|---------|-----------|---------|
| `Ownership_GetOwnership` | [api-ownership-endpoints.yaml](../11-agent-support/api-ownership-endpoints.yaml) | Get FinPercentage from TS015S0 |
| `Account_GetAccounts` | [api-account-endpoints.yaml](../11-agent-support/api-account-endpoints.yaml) | Get special accounts (DivReceived, PLINC, PLBAL) |
| `Flow_GetFlows` | [api-flow-endpoints.yaml](../11-agent-support/api-flow-endpoints.yaml) | Get special flows (DIVIDENDS, INTERIMDIVIDENDS) |

### API Workflow
```
Dividend Calculation Logic via API:

1. CONFIGURATION RETRIEVAL
   Account_GetAccounts → Get special accounts:
     - DivReceived, DivReceivedEquity
     - RetainedEarnings, PLBAL, PLINC
   Flow_GetFlows → Get special flows:
     - DIVIDENDS, INTERIMDIVIDENDS, ThisPeriodProfitLoss

2. OWNERSHIP DATA
   Ownership_GetOwnership → Build #Ownership structure:
     - CurCompanyFinPerc (current period %)
     - RefCompanyFinPerc (reference period %)
     - ConsoMethod (G/P/E for account routing)

3. DIVIDEND AMOUNT CALCULATION
   FlowData_GetData → Read TD045C2:
     - Filter: FlowID IN (DIVIDENDS, INTERIMDIVIDENDS)
     - Calculate: Amount × FinPercentage

4. JOURNAL ENTRY
   Consolidation_Execute → P_CONSO_ELIM_DIVIDEND:
     - Creates 4-line balanced entry
     - Posts to TMP_TD035C2, TMP_TD045C2
```

### Related API Documentation
- [API Index](../11-agent-support/api-index.yaml) - Master handler catalog
- [Gap Analysis](../11-agent-support/gap-analysis-report.yaml) - **FULLY IMPLEMENTED (100%)**

---

## Related Documentation

- [Intercompany Dividend Eliminations](dividend-eliminations.md) - Theory and overview
- [Elimination Execution Engine](../08-application-layer/elimination-execution-engine.md) - Processing framework
- [Elimination Templates](elimination-templates.md) - Configuration patterns
- [Ownership Percentages](../06-ownership-structure/ownership-percentages.md) - FinPercentage source

---
*Document 43 of 50+ | Batch 15: Advanced Eliminations & Database Patterns | Last Updated: 2024-12-01*
