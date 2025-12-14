# Flow Management: Special Flows and Movement Analysis

## Document Metadata
- **Category**: Core Calculations
- **Theory Source**: Knowledge base chunks: 1287, 1296, 1308, 1318 (terminology references)
- **Implementation Files**:
  - `Sigma.Database/dbo/Tables/TS011S0.sql` - Flow definitions
  - `Sigma.Database/dbo/Tables/TS011C0.sql` - Special flow mapping per consolidation
  - `Sigma.Database/dbo/Tables/TS011C1.sql` - Special flow code lookup
  - `Sigma.Database/dbo/Functions/UDF_GET_SPECIAL_FLOW.sql` - Flow retrieval function
  - `Sigma.Database/dbo/Stored Procedures/P_SYS_FLOW_MANAGEMENT.sql` - Flow operations
- **Last Updated**: 2024-12-01
- **Completeness**: 95% (Full flow framework with extensive special codes)
- **Compliance Status**: IAS 1 - Statement of Changes in Equity, IAS 7 - Cash Flow

## Executive Summary

Flows in Prophix.Conso represent movements that explain changes in balance sheet accounts between periods. The system provides 28 predefined special flow codes covering profit allocation, dividends, acquisitions/disposals, currency translation, method changes, and adjustments. Flows are essential for equity roll-forward analysis, cash flow statement preparation, and consolidation adjustment tracking.

## Theoretical Framework

### Concept Definition

A flow represents a movement or change that explains how a balance sheet position changed from opening to closing:

```
Opening Balance + Flows = Closing Balance

Where Flows include:
- Period profit/loss
- Dividends paid/received
- Acquisitions/disposals
- Currency translation adjustments
- Ownership changes
- Reserves adjustments
```

### Flow Categories

| Category | Purpose | Example Flows |
|----------|---------|---------------|
| **Profit Allocation** | Track P&L to equity | ThisPeriodProfitLoss, ProfitToReserves |
| **Dividend Flows** | Dividend distributions | Dividends, InterimDividends |
| **Scope Changes** | Entry/exit of entities | CompanyAcquired, CompanyDisposed |
| **Method Changes** | Consolidation transitions | VarConsoMeth_GE, VarConsoMeth_EP |
| **Currency** | FX movements | TransAdj, PreviousTransAdj |
| **Adjustments** | Period corrections | ReservesAdj, PreviousPeriodAdj |
| **Variance** | Unexplained/balancing | UnexpVar, DifferenceOnOpening |
| **Ownership** | Percentage changes | VarPercInteg |

## Current Implementation

### Database Schema

#### TS011S0 - Flow Definitions

```sql
CREATE TABLE [dbo].[TS011S0] (
    [FlowID]              INT          IDENTITY NOT NULL,
    [Flow]                NVARCHAR (3) NOT NULL,      -- Flow code (e.g., 'A01')
    [ConsoID]             INT          NOT NULL,
    [DefaultSign]         SMALLINT     DEFAULT 1,     -- 1, -1, or 0
    [InputSign]           SMALLINT     DEFAULT 1,     -- Data entry sign
    [FlagConso]           BIT          DEFAULT 0,     -- Consolidation-specific flow
    [PercentageType]      TINYINT      DEFAULT 1,     -- 1=Group, 2=Company
    [RateType1]           CHAR (2)     DEFAULT 'AC',  -- Currency rate type
    [RateFlowID1]         INT          NULL,          -- Reference flow for rate
    [FlagHistoricalRate1] BIT          DEFAULT 0,     -- Use historical rate
    [HistoricalFlowID1]   INT          NULL,          -- Historical reference
    [RateType2]           CHAR (2)     DEFAULT 'AC',  -- Secondary rate
    [FlagCash]            BIT          DEFAULT 1,     -- Include in cash flow
    [FlowDescriptionID]   INT          NOT NULL
);
```

**Rate Types**:
| Code | Description |
|------|-------------|
| AC | Average Calculated |
| CC | Closing Calculated |
| AR | Average Rate |
| CR | Closing Rate |
| MR | Month Rate |
| MC | Month Calculated |
| NR | No Rate (historical) |

#### TS011C0 - Special Flow Mapping

```sql
CREATE TABLE [dbo].[TS011C0] (
    [ConsolidationFlowID] INT           IDENTITY NOT NULL,
    [ConsoID]             INT           NOT NULL,
    [FlowID]              INT           NOT NULL,
    [SpecFlowCode]        NVARCHAR (20) NOT NULL
);

-- Links a consolidation's flow to a special flow code
-- Example: ConsoID 25685, FlowID 377359 → 'ThisPeriodProfitLoss'
```

#### TS011C1 - Special Flow Codes

```sql
CREATE TABLE [dbo].[TS011C1] (
    [SpecFlowID]          INT           IDENTITY NOT NULL,
    [Sequence]            SMALLINT      NOT NULL,      -- Display order
    [SpecFlowCode]        NVARCHAR (20) NOT NULL,
    [SpecFlowDescription] NVARCHAR (50) NULL
);
```

### Complete Special Flow Code Reference

| ID | Sequence | SpecFlowCode | Description | Usage |
|----|----------|--------------|-------------|-------|
| 13 | 1 | **ThisPeriodProfitLoss** | Profit/Loss of the period | Primary P&L allocation |
| 2 | 2 | **Appropriation** | Appropriation flow | Retained earnings |
| 10 | 3 | **Dividends** | Dividends | Final dividend paid |
| 14 | 4 | **InterimDividends** | Prepaid dividends | Interim distributions |
| 21 | 5 | **NetVar** | Net variation | General movements |
| 15 | 6 | **ProfitLossAdj** | Profit/Loss adjustment | P&L corrections |
| 26 | 7 | **ProfitToReserves** | Profit to reserves | Allocation to reserves |
| 23 | 8 | **ReservesAdj** | Reserves adjustment | Reserves corrections |
| 24 | 9 | **PreviousPeriodAdj** | Previous periods adjustments | Prior period changes |
| 11 | 10 | **Transfer** | Transfer between accounts | Reclassifications |
| 9 | 11 | **DifferenceOnOpening** | Difference on opening | Opening balance variance |
| 5 | 12 | **CompanyAcquired** | Acquisition of a Company | Entry to scope |
| 8 | 13 | **CompanyDisposed** | Disposal of a Company | Exit from scope |
| 4 | 14 | **Merge** | Merge flow | Company merger |
| 3 | 15 | **PreviousTransAdj** | Previous periods translation adjustment | Historical FX |
| 7 | 16 | **TransAdj** | Translation adjustment | Current CTA |
| 18 | 17 | **RoundedErrors** | Rounded errors | Rounding differences |
| 25 | 18 | **UnexpVar** | Unexplained variation | Balancing item |
| 1 | 19 | **VarPercInteg** | Variation of % integration | Ownership % changes |
| 19 | 20 | **VarConsoMeth_GE** | Variation G→E | Global to Equity |
| 20 | 21 | **VarConsoMeth_EG** | Variation E→G | Equity to Global |
| 22 | 22 | **VarConsoMeth_PE** | Variation P→E | Proportional to Equity |
| 6 | 23 | **VarConsoMeth_EP** | Variation E→P | Equity to Proportional |
| 17 | 24 | **VarConsoMeth_PG** | Variation P→G | Proportional to Global |
| 12 | 25 | **VarConsoMeth_GP** | Variation G→P | Global to Proportional |
| 16 | 26 | **VarConsoMeth_CE** | Variation C→E | Cost to Equity |
| 27 | 27 | **DefTaxFlowDT** | DefTaxFlowDT | Deferred tax (debit) |
| 28 | 28 | **DefTaxFlowCT** | DefTaxFlowCT | Deferred tax (credit) |

### Special Flow Retrieval Function

```sql
CREATE FUNCTION [dbo].[UDF_GET_SPECIAL_FLOW] (@ConsoID int, @SpecFlowCode nvarchar(20))
RETURNS int
AS
BEGIN
    RETURN (SELECT FlowID
            FROM dbo.TS011C0 WITH(NOLOCK)
            WHERE ConsoID = @ConsoID
              AND SpecFlowCode = @SpecFlowCode)
END

-- Usage:
SELECT @DividendsFlowID = dbo.UDF_GET_SPECIAL_FLOW(@ConsoID, 'Dividends')
SELECT @VarPercIntegFlowID = dbo.UDF_GET_SPECIAL_FLOW(@ConsoID, 'VarPercInteg')
SELECT @ProfitFlowID = dbo.UDF_GET_SPECIAL_FLOW(@ConsoID, 'ThisPeriodProfitLoss')
```

### Flow Operations

From `P_SYS_FLOW_MANAGEMENT.sql`:

| Operation | Code | Description |
|-----------|------|-------------|
| Book Difference | 1 | Post remaining variance |
| Set to Zero | 2 | Clear flow amounts |
| Merge | 3 | Combine flows |
| Recompute Specific | 4 | Recalculate special flows |
| Force Historical Rate | 5 | Override with historical rate |

```sql
-- Flow operation options
@FlowOperation tinyInt,  -- 1=book diff, 2=zero, 3=merge, 4=recompute, 5=historical
@FlowOption tinyInt,     -- For Op=2: 1=All, 2=only ID, 3=All but ID
                         -- For Op=3: 1=Replace, 2=Add
```

### Flow Usage in Eliminations

**Dividend Elimination (P_CONSO_ELIM_DIVIDEND)**:
```sql
SELECT @DividendsFlowID       = dbo.UDF_GET_SPECIAL_FLOW(@ConsoID, 'DIVIDENDS')
SELECT @InterimDividendsFlowID = dbo.UDF_GET_SPECIAL_FLOW(@ConsoID, 'INTERIMDIVIDENDS')
SELECT @ProfitFlowID          = dbo.UDF_GET_SPECIAL_FLOW(@ConsoID, 'ThisPeriodProfitLoss')
SELECT @ReservesAdjFlowID     = dbo.UDF_GET_SPECIAL_FLOW(@ConsoID, 'ReservesAdj')
```

**Proportional/Percentage Changes**:
```sql
-- VarPercInteg flow captures impact of ownership percentage changes
SELECT @VarPercIntegFlowID = dbo.UDF_GET_SPECIAL_FLOW(@ConsoID, 'VarPercInteg')

-- Calculate impact:
ROUND(-1 * ISNULL(a.Amount, 0) *
      ((ISNULL(b.GroupPerc, 0) - ISNULL(b.RefGroupPerc, 0) +
        ISNULL(b.MinorPerc, 0) - ISNULL(b.RefMinorPerc, 0)) / 100),
      @RoundingDecimal) as Amount
```

### Flow Summations

```sql
-- TS011G0 - Flow Summation Groups
CREATE TABLE [dbo].[TS011G0] (
    [FlowSummationID]            INT           IDENTITY NOT NULL,
    [FlowSummationCode]          NVARCHAR (15) NOT NULL,
    [ConsoID]                    INT           NOT NULL,
    [FlowSummationDescriptionID] INT           NOT NULL,
    [IsDirty]                    SMALLINT      NOT NULL,  -- Recalc needed
    [IsAvailableForOLAP]         BIT           DEFAULT 0
);

-- TS011G1 - Summation definitions
-- TS011G2 - Summation details (which flows belong to which summation)
-- TS011G3 - Summation filters
```

### Currency Translation on Flows

Each flow can have its own currency translation rate:

```sql
[RateType1]           CHAR (2)  DEFAULT 'AC',  -- Primary rate type
[RateFlowID1]         INT       NULL,          -- Use rate from another flow
[FlagHistoricalRate1] BIT       DEFAULT 0,     -- Historical rate flag
[HistoricalFlowID1]   INT       NULL,          -- Reference for historical
[RateType2]           CHAR (2)  DEFAULT 'AC',  -- Secondary translation
```

**Rate Application**:
- AC (Average Calculated): Weighted average rate
- CR (Closing Rate): Period-end rate
- Historical: Rate at transaction date

## Flow Roll-Forward Analysis

### Standard Equity Roll-Forward

```
Opening Equity (from reference period)
+ ThisPeriodProfitLoss
- Dividends
- InterimDividends
+/- TransAdj (Currency)
+/- VarPercInteg (Ownership changes)
+/- CompanyAcquired
+/- CompanyDisposed
+/- ReservesAdj
+/- PreviousPeriodAdj
+/- UnexpVar (balancing)
= Closing Equity
```

### Method Change Flows

When consolidation method changes, the impact flows to specific flows:

| Transition | Flow Code | Description |
|------------|-----------|-------------|
| G → E | VarConsoMeth_GE | Deconsolidate to equity method |
| E → G | VarConsoMeth_EG | Step acquisition |
| P → E | VarConsoMeth_PE | JV loses joint control |
| E → P | VarConsoMeth_EP | JV gains joint control |
| G → P | VarConsoMeth_GP | Lose exclusive control, retain joint |
| P → G | VarConsoMeth_PG | Gain exclusive from joint |

## Theory vs Practice Analysis

| Aspect | Theory (IAS 1/7) | Prophix.Conso Implementation | Alignment |
|--------|-----------------|------------------------------|-----------|
| Movement Analysis | Required | 28 special flow codes | Full |
| Profit Allocation | Required | ThisPeriodProfitLoss, ProfitToReserves | Full |
| Dividend Tracking | Required | Dividends, InterimDividends flows | Full |
| CTA Separation | Required | TransAdj, PreviousTransAdj | Full |
| Method Change Impact | Required | VarConsoMeth_XX flows | Full |
| Scope Change Impact | Required | CompanyAcquired, CompanyDisposed | Full |
| Unexplained Variance | Reconciliation | UnexpVar flow | Full |

## Gap Analysis

### Missing Elements

None significant - comprehensive flow framework covers all standard requirements.

### Additional Features (Beyond Theory)

1. **28 Pre-defined Flow Codes**: Extensive coverage
2. **Flexible Rate Assignment**: Per-flow currency translation
3. **Flow Summations**: Custom groupings for reporting
4. **Historical Rate Support**: Flow-level historical tracking
5. **Method Change Flows**: Six directional transition codes

## Business Impact

### Current Capabilities

1. **Complete Roll-Forward**: Full equity movement analysis
2. **Cash Flow Basis**: FlagCash for CF statement
3. **Audit Trail**: Each movement tracked separately
4. **Period Comparison**: Reference vs current period flows

### Operational Considerations

1. **Flow Mapping**: Map flows during consolidation setup
2. **Rate Configuration**: Configure appropriate rate types
3. **Summation Setup**: Define flow groups for reporting
4. **Variance Resolution**: Monitor UnexpVar for data quality

## API Reference

### Primary API Handlers
| Handler | YAML File | Purpose | Status |
|---------|-----------|---------|--------|
| `Flow_GetFlows` | [api-data-entry-endpoints.yaml](../11-agent-support/api-data-entry-endpoints.yaml) | Get flow definitions | ✅ IMPLEMENTED |
| `Flow_SaveFlows` | [api-data-entry-endpoints.yaml](../11-agent-support/api-data-entry-endpoints.yaml) | Save flow configuration | ✅ IMPLEMENTED |
| `Consolidation_Execute` | [api-consolidation-endpoints.yaml](../11-agent-support/api-consolidation-endpoints.yaml) | Process flows during consolidation | ✅ IMPLEMENTED |

### Supporting API Handlers
| Handler | YAML File | Purpose |
|---------|-----------|---------|
| `Report_ExecuteReport` | [api-reports-endpoints.yaml](../11-agent-support/api-reports-endpoints.yaml) | Generate equity movement reports |
| `Event_GetEvents` | [api-event-endpoints.yaml](../11-agent-support/api-event-endpoints.yaml) | Get flow-related events |

### API Workflow
```
1. Flow_GetFlows → Retrieve TS011S0 flow definitions
2. Configure special flows via TS011C0 mapping
3. UDF_GET_SPECIAL_FLOW → Retrieve specific flow IDs
4. Consolidation_Execute → Process flows:
   - P_CONSO_ELIM_DIVIDEND uses DIVIDENDS, INTERIMDIVIDENDS
   - P_CONSO_ELIM_CHANGE_METHOD uses VarConsoMeth_XX
   - All eliminations use VarPercInteg
5. Report_ExecuteReport → Equity movement analysis
```

### Stored Procedure Reference
| Procedure | Flow Usage |
|-----------|------------|
| P_CONSO_ELIM_DIVIDEND | DIVIDENDS, INTERIMDIVIDENDS, ThisPeriodProfitLoss |
| P_CONSO_ELIM_CHANGE_METHOD | VarConsoMeth_GE/EG/PE/EP/PG/GP |
| P_CONSO_ELIM_MINORITYINTEREST | VarPercInteg |
| P_SYS_FLOW_MANAGEMENT | All flow operations |

### Related API Documentation
- [API Index](../11-agent-support/api-index.yaml) - Master handler catalog
- [Gap Analysis](../11-agent-support/gap-analysis-report.yaml) - **FULLY IMPLEMENTED (95%)**

---

## See Also

### Related Core Calculations
- [Equity Reconciliation](equity-reconciliation.md) - Movement analysis
- [Scope Changes](scope-changes.md) - Entry/exit flows
- [Step Acquisition](step-acquisition.md) - VarConsoMeth flows

### Related Currency
- [Translation Adjustments](../05-currency-translation/translation-adjustments.md) - CTA flows

### Related Eliminations
- [Dividend Eliminations](../04-elimination-entries/dividend-eliminations.md) - Dividend flows

### Related Database
- [Journal Types](../07-database-implementation/journal-types.md) - Journal/flow relationship
- [Data Tables Catalog](../07-database-implementation/data-tables-catalog.md) - TS011C0/C1 tables

### Technical References
- Knowledge Base: Chunks 1287, 1296, 1308, 1318
- Code: `UDF_GET_SPECIAL_FLOW.sql`, `TS011C0.sql`, `TS011C1.sql`

### Navigation
- [Cross-Reference Index](../00-index/CROSS_REFERENCE_INDEX.md) - Full document relationships
- [Executive Summary](../00-index/EXECUTIVE_SUMMARY.md) - Overview

---
*Document 22 of 50+ | Batch 8: Core System Mechanics | Last Updated: 2024-12-01*
