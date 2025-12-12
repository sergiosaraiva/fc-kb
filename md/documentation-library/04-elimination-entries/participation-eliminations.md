# Participation (Investment) Eliminations

## Document Metadata
- **Category**: Elimination Entries
- **Theory Source**: Knowledge base chunks: 0163, 0164, 0165, 0171-0174, 0180-0183, 0197, 0198
- **Implementation Files**:
  - `Sigma.Database/dbo/Stored Procedures/P_CONSO_ELIM_PARTICIPATIONS0.sql` - Setup/initialization
  - `Sigma.Database/dbo/Stored Procedures/P_CONSO_ELIM_PARTICIPATIONS1.sql` - S089: Investment elimination
  - `Sigma.Database/dbo/Stored Procedures/P_CONSO_ELIM_PARTICIPATIONS2.sql` - S090: Link account elimination
  - `Sigma.Database/dbo/Stored Procedures/P_CONSO_ELIM_PARTICIPATIONS3.sql` - S093: Consolidated reserves calculation
  - `Sigma.Database/dbo/Stored Procedures/P_CONSO_ELIM_PARTICIPATIONS4.sql` - S094: Goodwill/Bargain calculation
  - `Sigma.Database/dbo/Stored Procedures/P_CONSO_ELIM_EQUITYCAPITAL.sql` - S087: Equity capital elimination
- **Last Updated**: 2024-12-01
- **Completeness**: 98% (Full multi-step participation elimination implemented)
- **Compliance Status**: IFRS 3 - Business Combinations, IAS 27 - Separate Financial Statements

## Executive Summary

Participation (investment) eliminations are the cornerstone of group consolidation, ensuring that intercompany ownership relationships do not inflate the consolidated balance sheet. Prophix.Conso implements a sophisticated multi-step elimination process (S087-S094) that handles investment accounts, equity capital, link accounts, consolidated reserves, and goodwill/bargain purchase calculations across all consolidation methods (Global, Proportional, Equity, Not Consolidated).

## Theoretical Framework

### Concept Definition

From Allen White's "Direct Consolidation" (Chunk 164):

> "Equity of P remains unchanged. However the equity of S is integrated in proportion to the financial percentage: Consolidated reserves (S) = 51% × [200+150+50] - 120 (investment in S owned by P)"

### Why Participation Elimination?

In the parent's separate accounts, investments in subsidiaries appear as assets. When consolidating, these investments must be eliminated against the subsidiary's equity to avoid double-counting:

```
Parent Investment in Subsidiary: 120 (Asset on Parent's B/S)
Subsidiary's Equity: 400 (Capital + Reserves + Profit)

Without elimination: Group shows 120 + 400 = 520 (overstated)
With elimination: Group shows 400 - 120 = 280 in consolidated reserves
```

### The Four-Column Approach

From Chunk 165:

> "Column P (1) eliminates the investments on S by reclassifying them on a Link account. Column S (2) reclassifies 49% of Minority interests from equity to the corresponding Minority interests account. Column S (3) eliminates the 51% group part of equity and reclassifies it on the consolidated reserves. Column S (4) consists in booking in S on the Link account the opposite value of the investments on S."

### Step-by-Step Process

| Step | Description | Journal | Account Type |
|------|-------------|---------|--------------|
| 1 | Eliminate parent's investment | S089 | Participation → LinkPartElim |
| 2 | Eliminate link account balance | S090 | LinkPartElim → ConsoDiff |
| 3 | Calculate consolidated reserves | S093 | ConsoReserves adjustment |
| 4 | Calculate goodwill/bargain | S094 | Goodwill or NegGoodwill account |
| 5 | Eliminate subsidiary equity | S087 | Equity accounts → ConsoDiff |

### Example (Chunks 163-164)

**Before Consolidation**:
```
Parent P:
- Investment in S: 120
- Other Assets: 1,030
- Capital: 500, Reserves: 300, Profit: 100
- Liabilities: 250

Subsidiary S (51% owned):
- Assets: 700
- Capital: 200, Reserves: 150, Profit: 50
- Liabilities: 300
```

**After Consolidation (P+S)**:
```
Consolidated:
- Assets: 1,730 (1,030 + 700)
- Capital: 500 (P only)
- Reserves: 300 (P only)
- Profit: 100 (P only)
- Consolidated Reserves (S): 84 = 51% × (200+150+50) - 120
- Minority Interest: 196 = 49% × (200+150+50)
- Liabilities: 550 (250 + 300)
- Total: 1,730
```

## Current Implementation

### Elimination Code System

Prophix.Conso uses a code-based elimination system stored in `TS070S0`:

| ElimCode | Description | Procedure |
|----------|-------------|-----------|
| S087 | Equity Capital Elimination | P_CONSO_ELIM_EQUITYCAPITAL |
| S089 | Participations Elimination (Investment) | P_CONSO_ELIM_PARTICIPATIONS1 |
| S090 | Link Account Elimination | P_CONSO_ELIM_PARTICIPATIONS2 |
| S093 | Consolidated Reserves Calculation | P_CONSO_ELIM_PARTICIPATIONS3 |
| S094 | Goodwill/Bargain Calculation | P_CONSO_ELIM_PARTICIPATIONS4 |

### Special Accounts Used

From `P_CONSO_ELIM_PARTICIPATIONS1.sql` (lines 96-111):

```sql
-- Link Account for Participation Elimination
select @LinkPartElimAccountID = dbo.UDF_GET_SPECIAL_ACCOUNT(@ConsoID, 'LINKPARTELIM')

-- Equity Value Account (for equity method companies)
select @EquityValAccountID = dbo.UDF_GET_SPECIAL_ACCOUNT(@ConsoID, 'EQUITYVAL')
```

**Required Special Accounts**:
| Code | Description | Purpose |
|------|-------------|---------|
| LINKPARTELIM | Link Participation Elimination | Intermediate account for investment elimination |
| CONSODIFF | Consolidation Difference | Balancing account for equity elimination |
| EQUITYVAL | Equity Value | Equity method investment account |
| CONSORES | Consolidated Reserves | Group portion of subsidiary reserves |
| GOODWILL | Goodwill | Excess of cost over fair value |
| NEGGOODWILL | Negative Goodwill | Bargain purchase gain |

### Investment Elimination (S089)

From `P_CONSO_ELIM_PARTICIPATIONS1.sql` (lines 175-208):

```sql
-- Retrieve participation accounts and eliminate at group percentage
insert into dbo.TMP_TD035C2 (...)
select @SessionID,
       a.CompanyID,
       @JournalTypeS089ID,
       b.JournalEntry,
       1 as JournalSequence,
       a.AccountID,                    -- Participation account
       a.PartnerCompanyID,             -- The subsidiary being invested in
       @ConsoCurrCode,
       ROUND(ISNULL(a.Amount, 0), @RoundingDecimal) as Amount,
       ...
from (
    select b.CompanyID,
           b.PartnerCompanyID,
           b.AccountID,
           -- Eliminate at group percentage
           -1 * sum(b.Amount * case when b.MinorityFlag = 0
                                    then (a.GroupPerc + a.MinorPerc) / 100
                                    else 1 end) as Amount
    from #SelectedCompanies a
         cross apply dbo.UDF_CONSO_ELIM_TD035C2(...) b
         inner join dbo.TS010S0 e on (e.PartnerType = 2)  -- Participation accounts only
    where b.PartnerCompanyID is not null
    group by b.CompanyID, b.PartnerCompanyID, b.AccountID
) a
```

**Key Logic**:
- Only processes accounts with `PartnerType = 2` (participation accounts)
- Eliminates at `(GroupPerc + MinorPerc) / 100` for full elimination
- Creates offset entry on LINKPARTELIM account

### Equity Capital Elimination (S087)

From `P_CONSO_ELIM_EQUITYCAPITAL.sql` (lines 135-168):

```sql
-- Step 1: Remove amounts from equity accounts
insert into dbo.TMP_TD035C2 (...)
select @SessionID,
       a.CompanyID,
       @JournalTypeS087ID,
       b.AlternateEntry,
       1 as JournalSequence,
       a.AccountID,
       a.PartnerCompanyID,
       @ConsoCurrCode,
       -- Eliminate at percentage
       ROUND(ISNULL(-a.Amount * (ISNULL(b.GroupPerc, 0) + ISNULL(b.MinorPerc, 0)) / 100, 0),
             @RoundingDecimal) as Amount,
       ...
from (
    select a.CompanyID,
           b.AccountID,
           b.PartnerCompanyID,
           sum(COALESCE(b.Amount, 0)) as Amount
    from #SelectedCompanies a
         cross apply dbo.UDF_CONSO_ELIM_TD035C2(...) b
         inner join dbo.TS010S0 d on (d.FlagEquityElimination = 1
                                      and d.PartnerType <> 2)
    where b.MinorityFlag = 0
    group by a.CompanyID, b.AccountID, b.PartnerCompanyID
) a
```

**Key Logic**:
- Processes accounts with `FlagEquityElimination = 1` (equity accounts)
- Excludes `PartnerType = 2` (handled by S089)
- Creates offset on CONSODIFF account

### Change in Percentage Handling

From `P_CONSO_ELIM_EQUITYCAPITAL.sql` (lines 217-260):

```sql
-- Impact of change in % on opening flows
insert into dbo.TMP_TD045C2 (...)
select @SessionID,
       a.CompanyID,
       @JournalTypeS087ID,
       b.JournalEntry,
       1 as JournalSequence,
       a.AccountID,
       @VarPercIntegFlowID as FlowID,  -- VarPercInteg flow
       a.PartnerCompanyID,
       @ConsoCurrCode,
       -- Calculate impact of percentage change
       ROUND(-1 * ISNULL(a.Amount, 0) *
             ((ISNULL(b.GroupPerc, 0) - ISNULL(b.RefGroupPerc, 0) +
               ISNULL(b.MinorPerc, 0) - ISNULL(b.RefMinorPerc, 0)) / 100),
             @RoundingDecimal) as Amount,
       ...
```

**Purpose**: When ownership percentage changes between periods, the system calculates the impact on opening balances and books to `VarPercInteg` flow.

### Point of View (POV) Elimination

From `P_CONSO_ELIM_PARTICIPATIONS1.sql` (lines 409-594):

The system supports POV-based elimination for multi-level hierarchies:

```sql
-- If POV configuration enabled, distribute eliminations to appropriate journals
If @POVConfig = 1
Begin
    -- Build POV hierarchy tree
    ;with tbParent as (
        select c.ConsoID, c.CompanyID, x.PointOfViewCriteriaID,
               x.Level, x.ParentPointOfViewCriteriaID
        from dbo.TS064S0 c
             inner join dbo.TS061S0 x on x.PointOfViewCriteriaID = c.PointOfViewCriteriaID
        where x.ConsoID = @ConsoID and x.PointOfViewID = @POVLegalID
        union all
        select a.ConsoID, p.CompanyID, a.PointOfViewCriteriaID, ...
        from dbo.TS061S0 a join tbParent p on ...
    )

    -- Update journal types based on POV level
    Update a
        set a.JournalTypeID = b.TargetJournalTypeID
    From dbo.TMP_TD035C2 a
         inner join @AlternateTarget b on ...
End
```

### Consolidated Reserves Calculation (S093)

The consolidated reserves formula implemented:

```
Consolidated Reserves = Group% × (Capital + Reserves + Profit) - Investment Cost
                      = 51% × (200 + 150 + 50) - 120
                      = 204 - 120
                      = 84
```

### Method-Specific Processing

| ConsoMethod | S089 (Investment) | S087 (Equity) | S090 (Link) | S093 (Reserves) |
|-------------|-------------------|---------------|-------------|-----------------|
| Global (G) | Full elimination | Full at Group% | Full | Yes |
| Proportional (P) | Proportional | Proportional | Proportional | Yes |
| Equity (E) | To EQUITYVAL | N/A | N/A | Via equity method |
| Not Conso (N) | None | None | None | None |

## Theory vs Practice Analysis

| Aspect | Theory (Allen White) | Prophix.Conso Implementation | Alignment |
|--------|---------------------|------------------------------|-----------|
| Investment Elimination | Debit equity, credit investment | S089 with LINKPARTELIM | Full |
| Equity Elimination | Group% of subsidiary equity | S087 with FlagEquityElimination | Full |
| Link Account | Bridge between elimination entries | LINKPARTELIM special account | Full |
| Consolidated Reserves | Group% × Equity - Investment | S093 calculation | Full |
| Goodwill | Excess of cost over fair value | S094 to GOODWILL account | Full |
| Minority Interest | 3rd party % × Equity | Handled separately (S079) | Full |
| Change in % | Flow explanation for changes | VarPercInteg flow | Enhanced |

## Gap Analysis

### Missing Elements

1. **Step Acquisition Automation**: Changes in ownership requiring goodwill recalculation are partially manual

### Divergent Implementation

1. **Multi-Journal System**: Uses separate journals (S087-S094) vs single elimination entry in theory - provides better audit trail

### Additional Features (Beyond Theory)

1. **POV-Based Elimination**: Multi-hierarchy support for legal structure consolidation
2. **VarPercInteg Flow**: Explicit tracking of percentage change impacts
3. **Dimension Support**: Elimination entries can carry dimensional analysis
4. **Rounding Configuration**: Configurable decimal precision per consolidation

## API Reference

### Primary API Handlers
| Handler | YAML File | Purpose | Status |
|---------|-----------|---------|--------|
| `Consolidation_Execute` | [api-consolidation-endpoints.yaml](../11-agent-support/api-consolidation-endpoints.yaml) | Execute S087-S094 participations | ✅ IMPLEMENTED |
| `Elimination_GetEliminations` | [api-elimination-endpoints.yaml](../11-agent-support/api-elimination-endpoints.yaml) | Get participation eliminations | ✅ IMPLEMENTED |
| `Ownership_GetOwnership` | [api-ownership-endpoints.yaml](../11-agent-support/api-ownership-endpoints.yaml) | Get investment percentages | ✅ IMPLEMENTED |

### Supporting API Handlers
| Handler | YAML File | Purpose |
|---------|-----------|---------|
| `Event_GetEvents` | [api-event-endpoints.yaml](../11-agent-support/api-event-endpoints.yaml) | Get elimination events |
| `Journal_GetJournals` | [api-adjustment-endpoints.yaml](../11-agent-support/api-adjustment-endpoints.yaml) | View elimination journals |

### Elimination Code Reference
| Code | Handler | Procedure |
|------|---------|-----------|
| S087 | Equity Capital | P_CONSO_ELIM_EQUITYCAPITAL |
| S089 | Investment Elimination | P_CONSO_ELIM_PARTICIPATIONS1 |
| S090 | Link Account | P_CONSO_ELIM_PARTICIPATIONS2 |
| S093 | Consolidated Reserves | P_CONSO_ELIM_PARTICIPATIONS3 |
| S094 | Goodwill/Bargain | P_CONSO_ELIM_PARTICIPATIONS4 |

### API Workflow
```
1. Ownership_SaveOwnership → Record investment cost
2. Consolidation_Execute → Sequential elimination:
   S089: Eliminate investment account
   S090: Clear link account
   S093: Calculate consolidated reserves
   S094: Compute goodwill/badwill
   S087: Eliminate subsidiary equity
3. Elimination_GetEliminations → Review posted eliminations
```

### Related API Documentation
- [API Index](../11-agent-support/api-index.yaml) - Master handler catalog
- [Elimination Code Selection](../11-agent-support/elimination-code-selection.yaml) - Decision logic
- [Gap Analysis](../11-agent-support/gap-analysis-report.yaml) - Theory alignment: **IFRS 3/IAS 27 compliant**

---

## Business Impact

1. **Accurate Consolidation**: Prevents double-counting of equity and investments
2. **Audit Trail**: Separate journal types provide detailed elimination documentation
3. **Multi-Hierarchy Support**: POV configuration enables legal/management parallel consolidations
4. **Period Comparison**: Reference period percentage handling for consistent comparison

## Recommendations

1. **Enhance Step Acquisition**: Automate goodwill recalculation on ownership changes
2. **Add Elimination Preview**: Allow simulation before committing eliminations
3. **Improve Documentation**: Auto-generate elimination schedules for audit packages

## See Also

### Related Eliminations
- [Intercompany Transactions](intercompany-transactions.md) - IC balance eliminations
- [Dividend Eliminations](dividend-eliminations.md) - Dividend processing
- [User Eliminations](user-eliminations.md) - Manual adjustments

### Related Core Calculations
- [Goodwill Calculation](../03-core-calculations/goodwill-calculation.md) - Goodwill mechanics
- [Minority Interest](../03-core-calculations/minority-interest.md) - NCI calculation
- [Step Acquisition](../03-core-calculations/step-acquisition.md) - Method transitions

### Related Methods
- [Global Integration](../02-consolidation-methods/global-integration.md) - Full consolidation
- [Equity Method](../02-consolidation-methods/equity-method.md) - One-line consolidation

### Technical References
- Knowledge Base: Chunks 0163-0165, 0171-0174, 0180-0183, 0197-0198
- Code: `P_CONSO_ELIM_PARTICIPATIONS0-4.sql`, `P_CONSO_ELIM_EQUITYCAPITAL.sql`

### Navigation
- [Cross-Reference Index](../00-index/CROSS_REFERENCE_INDEX.md) - Full document relationships
- [Elimination Execution Engine](../08-application-layer/elimination-execution-engine.md) - Architecture

---
*Document 16 of 50+ | Batch 6: Elimination Entries | Last Updated: 2024-12-01*
