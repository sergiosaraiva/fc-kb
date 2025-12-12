# Equity Reconciliation: Movement Analysis and Reserves Tracking

## Document Metadata
- **Category**: Core Calculations
- **Theory Source**: Implementation-specific (Equity movement reporting)
- **Implementation Files**:
  - `Sigma.Database/dbo/Stored Procedures/P_REPORT_CONSOLIDATED_EQUITY.sql` - Consolidated equity report
  - `Sigma.Database/dbo/Stored Procedures/P_REPORT_EQUITY_VALUE_ANALYSIS.sql` - Equity value analysis
  - `Sigma.Database/dbo/Stored Procedures/P_REPORT_EQUITY_VALUE_ANALYSIS_HEADER.sql` - Report header
  - `Sigma.Database/dbo/Stored Procedures/P_CONSO_ELIM_EQUITYCAPITAL.sql` - Equity capital elimination
  - `Sigma.Database/dbo/Stored Procedures/P_CONSO_ELIM_EQUITYMETHOD.sql` - Equity method processing
- **Last Updated**: 2024-12-01
- **Completeness**: 95% (Full equity reconciliation documented)
- **Compliance Status**: IAS 1 - Statement of Changes in Equity

## Executive Summary

Equity reconciliation in Prophix.Conso tracks the movement in group equity from opening to closing balance, analyzing contributions from each journal type (local, adjustments, eliminations). The system provides multiple reporting views including consolidated equity analysis, equity value analysis for equity method companies, and journal-by-journal movement breakdown.

## Equity Movement Architecture

### Movement Categories

```
┌─────────────────────────────────────────────────────────────────┐
│                    Equity Movement Flow                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Opening Equity (Reference Period)                               │
│  │                                                               │
│  ├── + Current Period Profit/Loss                               │
│  │     └── From P&L closing entries                             │
│  │                                                               │
│  ├── + Dividend Declarations                                    │
│  │     └── DIVIDENDS, INTERIMDIVIDENDS flows                    │
│  │                                                               │
│  ├── + Capital Changes                                          │
│  │     └── Share issues, buybacks                               │
│  │                                                               │
│  ├── + Reserves Adjustments                                     │
│  │     └── ReservesAdj flow movements                           │
│  │                                                               │
│  ├── + Translation Differences                                  │
│  │     └── CTA account movements                                │
│  │                                                               │
│  ├── + Elimination Impacts                                      │
│  │     └── Participation, dividend, IC eliminations             │
│  │                                                               │
│  └── = Closing Equity (Current Period)                          │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Journal Type Analysis

| Journal Type | Code | Equity Impact |
|--------------|------|---------------|
| Local | L | Local company equity |
| Adjustments | A | Manual adjustments |
| Conversions | C | Currency translation |
| Transfers | T | Group currency transfers |
| Eliminations | E | Consolidation eliminations |

## P_REPORT_CONSOLIDATED_EQUITY Implementation

### Purpose

Generates equity movement analysis by company, journal type, and account.

### Key Parameters

```sql
CREATE procedure [dbo].[P_REPORT_CONSOLIDATED_EQUITY]
    @CustomerID int,
    @CompanyIDs varchar(max),    -- Companies to analyze
    @ConsoID int,                -- Current period
    @RefConsoID int,             -- Reference (opening) period
    @DataLanguageLCID int,
    @ReportNr smallint,          -- Not used
    @ReportType smallint         -- Not used
```

### Processing Flow

```
1. Parameter Validation
   │
   ▼
2. Build #Companies temp table
   - Current period companies
   - Reference period matching
   │
   ▼
3. Build #Accounts temp table
   - Equity accounts used
   - Account descriptions
   │
   ▼
4. Build #JournalTypes temp table
   - All journal types used
   - Journal categories
   │
   ▼
5. Collect Current Period Amounts
   - From TD035C2 (closing amounts)
   - Group by Company, Account, Journal
   │
   ▼
6. Collect Reference Period Amounts
   - Same structure as current
   - For movement calculation
   │
   ▼
7. Return Combined Result Set
   - Company | Account | JournalType | Amount | RefAmount
```

### Temp Table Structure

```sql
-- Company list
create table #Companies (
    CompanyId int,
    CompanyCode nvarchar(12),
    CompanyName nvarchar(255),
    RefCompanyId int
)

-- Accounts used
create table #Accounts (
    Account nvarchar(12),
    [Description] nvarchar(max),
    IncludeSign int,
    AccountID int,
    RefAccountID int
)

-- Amount storage
create table #CurrentAmount (
    CompanyCode nvarchar(12),
    Account nvarchar(12),
    JournalType char(1),
    JournalCategory nvarchar(3),
    JournalEntry bigint,
    JournalText nvarchar(max),
    Amount decimal(24,6),
    MinorityFlag bit
)
```

## P_REPORT_EQUITY_VALUE_ANALYSIS Implementation

### Purpose

Analyzes equity value for equity method (E) companies, showing the investment value reconciliation.

### Key Features

```sql
-- Parameters
@FlagEquityFilter bit = 0  -- Filter to equity method companies only

-- Key accounts retrieved
@EquityValAccountID int    -- Special account for equity value
@ElimJournalTypeID int     -- S001 elimination journal
```

### Analysis Structure

```
Equity Value Analysis:
│
├── Opening Investment Value
│   └── Reference period EquityVal account
│
├── Share of Profit/Loss
│   └── Equity method P&L pickup
│
├── Dividend Received
│   └── Reduces investment value
│
├── Other Movements
│   └── Reserves adjustments, CTA
│
└── Closing Investment Value
    └── Current period EquityVal account
```

## Special Accounts for Equity

### Required Configuration

| Special Account | Usage |
|-----------------|-------|
| EquityVal | Equity method investment value |
| RetainedEarnings | Accumulated retained earnings |
| PLBAL | P&L to balance sheet link |
| PLINC | P&L income impact |
| CTA | Cumulative translation adjustment |
| MinorityEquity | Non-controlling interest equity |

### Retrieval Pattern

```sql
-- From P_REPORT_EQUITY_VALUE_ANALYSIS
select @EquityValAccountID = dbo.UDF_GET_SPECIAL_ACCOUNT(@ConsoID, 'EquityVal')
```

## Equity Elimination Processing

### P_CONSO_ELIM_EQUITYCAPITAL

Eliminates subsidiary equity against parent investment:

```
Parent Investment (Assets)
    Dr. Subsidiary Equity
    Cr. Investment in Subsidiary

Result: Removes double-counting of subsidiary net assets
```

### P_CONSO_ELIM_EQUITYMETHOD

Processes equity method companies:

```
Opening Investment
    + Share of Profit (GroupPerc × Subsidiary P&L)
    - Dividends Received
    = Closing Investment Value

Elimination Entry:
    Dr. Investment (EquityVal account)
    Cr. Share of Profit (P&L)
```

## Movement Flow Types

### Special Flows for Equity

| Flow Code | Purpose |
|-----------|---------|
| ThisPeriodProfitLoss | Current period P&L |
| OpeningBalance | Opening equity balance |
| ClosingBalance | Closing equity balance |
| DIVIDENDS | Dividend distributions |
| INTERIMDIVIDENDS | Interim dividend distributions |
| ReservesAdj | Reserves adjustment movements |

### Flow-Based Movement Tracking

```sql
-- Movement calculation
SELECT
    AccountID,
    FlowID,
    SUM(Amount) as Movement
FROM TD045C2
WHERE ConsoID = @ConsoID
    AND FlowID IN (
        @DividendsFlowID,
        @ReservesAdjFlowID,
        @ProfitFlowID
    )
GROUP BY AccountID, FlowID
```

## Minority Interest Equity

### NCI Movement Analysis

```
Opening NCI Equity
│
├── + NCI Share of Profit
│     (MinorPerc × Subsidiary P&L)
│
├── + NCI Share of Reserves
│     (MinorPerc × Reserves movements)
│
├── - NCI Dividends
│     (MinorPerc × Dividends paid)
│
└── = Closing NCI Equity
```

### MinorityFlag Usage

```sql
-- From #CurrentAmount
MinorityFlag bit  -- 0 = Group share, 1 = Minority share

-- Separation in reporting
SELECT
    SUM(CASE WHEN MinorityFlag = 0 THEN Amount ELSE 0 END) as GroupEquity,
    SUM(CASE WHEN MinorityFlag = 1 THEN Amount ELSE 0 END) as MinorityEquity
FROM #CurrentAmount
```

## Reconciliation Validation

### Balance Checks

```
Assets = Liabilities + Equity (Balance sheet equation)

Where Equity includes:
- Share Capital
- Share Premium
- Retained Earnings
- Current Year P&L
- Translation Reserves
- Other Reserves
- Non-Controlling Interest
```

### Validation Query Pattern

```sql
-- Total equity check
SELECT
    SUM(CASE WHEN AccountType = 'A' THEN Amount ELSE 0 END) as TotalAssets,
    SUM(CASE WHEN AccountType = 'L' THEN Amount ELSE 0 END) as TotalLiabilities,
    SUM(CASE WHEN AccountType = 'E' THEN Amount ELSE 0 END) as TotalEquity
FROM TD035C2
WHERE ConsoID = @ConsoID
-- Should balance: Assets = Liabilities + Equity
```

## Report Output Structure

### Consolidated Equity Report Format

```
Company | Account | Description | JournalType | CurAmount | RefAmount | Movement
--------|---------|-------------|-------------|-----------|-----------|----------
ABC     | 3000    | Share Cap   | L           | 1,000,000 | 1,000,000 | 0
ABC     | 3100    | Ret Earn    | L           | 500,000   | 400,000   | 100,000
ABC     | 3100    | Ret Earn    | E           | -50,000   | -40,000   | -10,000
```

### Equity Value Analysis Format

```
Company | ConsoMethod | OpeningValue | ShareOfProfit | Dividends | ClosingValue
--------|-------------|--------------|---------------|-----------|-------------
SUB1    | E           | 800,000      | 120,000       | -40,000   | 880,000
SUB2    | E           | 500,000      | 75,000        | -25,000   | 550,000
```

## Performance Considerations

### Temp Table Usage

```sql
-- Standard pattern for equity reports
create table #Companies (...)
create table #Accounts (...)
create table #CurrentAmount (...)
create table #RefAmount (...)

-- Index for performance on large datasets
CREATE INDEX IX_CurrentAmount ON #CurrentAmount (CompanyCode, Account)
```

### Collation Handling

```sql
-- Database collation compatibility
CompanyCode nvarchar(12) collate database_default
```

## API Reference

### Primary API Handlers
| Handler | YAML File | Purpose | Status |
|---------|-----------|---------|--------|
| `Report_ExecuteReport` | [api-reports-endpoints.yaml](../11-agent-support/api-reports-endpoints.yaml) | Execute P_REPORT_CONSOLIDATED_EQUITY | ✅ IMPLEMENTED |
| `Report_ExecuteReport` | [api-reports-endpoints.yaml](../11-agent-support/api-reports-endpoints.yaml) | Execute P_REPORT_EQUITY_VALUE_ANALYSIS | ✅ IMPLEMENTED |

### Supporting API Handlers
| Handler | YAML File | Purpose |
|---------|-----------|---------|
| `Company_GetCompanies` | [api-company-endpoints.yaml](../11-agent-support/api-company-endpoints.yaml) | Filter companies for report |
| `Elimination_GetEliminations` | [api-elimination-endpoints.yaml](../11-agent-support/api-elimination-endpoints.yaml) | Get equity eliminations |
| `Flow_GetFlows` | [api-data-entry-endpoints.yaml](../11-agent-support/api-data-entry-endpoints.yaml) | Get flow definitions for movement analysis |

### API Workflow
```
Equity Reconciliation via API:

1. Company_GetCompanies → Select companies to analyze
2. Report_ExecuteReport (ConsolidatedEquity) → P_REPORT_CONSOLIDATED_EQUITY:
   - Opening equity (reference period)
   - Movement by journal type (L/A/C/T/E)
   - Closing equity (current period)
3. Report_ExecuteReport (EquityValueAnalysis) → P_REPORT_EQUITY_VALUE_ANALYSIS:
   - Equity method investment values
   - Share of profit/loss
   - Dividend impact
```

### Stored Procedure Reference
| Procedure | Purpose |
|-----------|---------|
| P_REPORT_CONSOLIDATED_EQUITY | Equity movement by company/journal |
| P_REPORT_EQUITY_VALUE_ANALYSIS | Equity method investment values |
| P_CONSO_ELIM_EQUITYCAPITAL | Equity capital elimination |
| P_CONSO_ELIM_EQUITYMETHOD | Equity method processing |

### Related API Documentation
- [API Index](../11-agent-support/api-index.yaml) - Master handler catalog
- [Gap Analysis](../11-agent-support/gap-analysis-report.yaml) - **FULLY IMPLEMENTED (95%)**

---

## Related Documentation

- [Minority Interest](minority-interest.md) - NCI calculation details
- [Equity Method](../02-consolidation-methods/equity-method.md) - Equity method processing
- [Journal Types](../07-database-implementation/journal-types.md) - Journal classification
- [Flow Management](flow-management.md) - Special flow handling
- [Dividend Calculation Logic](../04-elimination-entries/dividend-calculation-logic.md) - Dividend flow processing

---
*Document 46 of 50+ | Batch 16: System Mechanics & Adjustment Processing | Last Updated: 2024-12-01*
