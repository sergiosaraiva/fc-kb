# Proportional Integration Method

## Document Metadata
- **Category**: Consolidation Methods
- **Theory Source**: Knowledge base chunks: 0054, 0055, 0166-0172, 0197, 0359, 0363
- **Implementation Files**:
  - `Sigma.Database/dbo/Stored Procedures/P_CONSO_ELIM_PROPORTIONAL.sql` - S079: Proportional elimination
  - `Sigma.Database/dbo/Stored Procedures/P_CALC_OWNERSHIP_INDIRECT_PERCENTAGES.sql` - Method determination
  - `Sigma.Database/dbo/Tables/TS014C0.sql` - ConsoMethod = 'P'
  - `Sigma.Database/dbo/Tables/T_CONFIG.sql` - CALC_NO_PROPORTIONAL setting
- **Last Updated**: 2024-12-01
- **Completeness**: 95% (Full proportional integration with IFRS 11 option)
- **Compliance Status**: IAS 31 (Proportional) / IFRS 11 (Equity option for JVs)

## Executive Summary

Proportional integration consolidates a jointly controlled entity by including the parent's share of each asset, liability, income, and expense line item rather than 100%. This method applies to joint ventures where exactly 50% control is held. Prophix.Conso implements proportional integration through the S079 elimination code (`P_CONSO_ELIM_PROPORTIONAL`), with a configuration option to disable proportional method for IFRS 11 compliance (where joint ventures use equity method instead).

## Theoretical Framework

### Concept Definition

From Allen White's "Direct Consolidation" (Chunk 166):

> "According to the method of proportional integration, the Assets, Liabilities, Expenses and Income of a joint subsidiary are included in the consolidated financial statements in proportion to the percentage held by the parent company."

### When to Use Proportional Method

| Control Level | Percentage | Method | Rationale |
|--------------|------------|--------|-----------|
| **Exclusive Control** | >50% | Global Integration | Full control |
| **Joint Control** | =50% | Proportional (IAS 31) | Shared decision-making |
| **Joint Control** | =50% | Equity (IFRS 11) | Joint venture alternative |
| **Significant Influence** | 20-50% | Equity Method | No control |

### Key Characteristics

```
Proportional Integration (50% ownership):
┌─────┐              ┌─────┐
│  P  │─────50%─────→│  S  │
└─────┘              └─────┘

Include in consolidated statements:
- 50% of S's assets
- 50% of S's liabilities
- 50% of S's income
- 50% of S's expenses
- NO minority interest (unlike Global)
```

### Comparison: Global vs Proportional

| Aspect | Global Integration | Proportional Integration |
|--------|-------------------|-------------------------|
| Assets included | 100% | Ownership % |
| Liabilities included | 100% | Ownership % |
| Minority Interest | Yes (for NCI share) | No |
| Control requirement | >50% exclusive | =50% joint |
| Profit/Loss | 100% then NCI allocation | Only group share |

### Example (from Chunks 167-172)

**Scenario**: P owns 50% of S (joint venture)

**S's Balance Sheet**:
```
Assets:          1,000
Liabilities:       400
Equity:            600
```

**Proportional Consolidation** (50%):
```
Assets:            500 (50% × 1,000)
Liabilities:       200 (50% × 400)
Net contribution:  300 (50% × 600)
```

**No minority interest** - only group's proportionate share is included.

## Current Implementation

### Elimination Code

| ElimCode | Description | Procedure |
|----------|-------------|-----------|
| S079 | Proportional Eliminations | P_CONSO_ELIM_PROPORTIONAL |

### Method Determination

From `P_CALC_OWNERSHIP_INDIRECT_PERCENTAGES.sql` (lines 484-518):

```sql
-- Check if Proportional Method is used or not
select @NoProportionalMethod = [dbo].[UDF_GET_CONFIG]('CALC_NO_PROPORTIONAL', NULL, @ConsoID)

If ISNULL(@NoProportionalMethod, 0) = 0
Begin
    -- Standard thresholds WITH proportional method
    Update #Companies
    Set ConsoMethod =
        Case
            When (GroupCtrlPerc > @ConsoMethP OR CompanyID = @ParentID) then 'G'
            -- Proportional: exactly 50% (joint control)
            When (GroupCtrlPerc = @ConsoMethP AND CompanyID <> @ParentID) then 'P'
            When (GroupCtrlPerc >= @ConsoMethN AND GroupCtrlPerc < @ConsoMethP) then 'E'
            When (GroupCtrlPerc < @ConsoMethN) then 'N'
            Else 'N'
        End
END
Else
BEGIN
    -- IFRS 11: No proportional method - 50% goes to equity
    Update #Companies
    Set ConsoMethod =
        Case
            When (GroupCtrlPerc > @ConsoMethP OR CompanyID = @ParentID) then 'G'
            -- Note: 50% now goes to equity method, not proportional
            When (GroupCtrlPerc >= @ConsoMethN AND GroupCtrlPerc <= @ConsoMethP) then 'E'
            When (GroupCtrlPerc < @ConsoMethN) then 'N'
            Else 'N'
        End
END
```

### Proportional Elimination Procedure

From `P_CONSO_ELIM_PROPORTIONAL.sql` (lines 109-144):

```sql
-- Calculate proportional elimination
-- Formula: Amount × (100 - GroupPerc - MinorPerc) / 100
-- This removes the non-group share from all accounts

insert into dbo.TMP_TD035C2 (...)
select  @SessionID,
        a.CompanyID,
        @JournalTypeS079ID,
        b.JournalEntry,
        1 as JournalSequence,
        a.AccountID,
        a.PartnerCompanyID,
        @ConsoCurrCode,
        -- Remove non-group portion: -1 × Amount × (100 - Group% - Minor%) / 100
        ISNULL (-1 * (Amount * (100 - (ISNULL(b.GroupPerc, 0) + ISNULL(b.MinorPerc, 0))) / 100), 0) as Amount,
        ...
from (  select  a.CompanyID,
                b.AccountID,
                b.PartnerCompanyID,
                b.TransactionCurrCode,
                sum (b.Amount) as Amount
        from    #SelectedCompanies a
                cross apply dbo.UDF_CONSO_ELIM_TD035C2 (...) b
        where   b.MinorityFlag = 0
                and (b.JournalType <> 'T' or b.JournalTypeID = @JournalTypeS001ID)
        group by a.CompanyID, b.AccountID, b.PartnerCompanyID, b.TransactionCurrCode
     ) a
     inner join #AllCompanies b on (b.CompanyID = a.CompanyID)
```

**Key Formula**:
```
Elimination Amount = -1 × Original Amount × (100 - GroupPerc - MinorPerc) / 100

Example (50% ownership):
- GroupPerc = 50, MinorPerc = 0
- Elimination = -1 × Amount × (100 - 50 - 0) / 100
- Elimination = -50% of Amount
- Result: Only 50% remains in consolidated figures
```

### Percentage Change Handling

The system handles changes between reference and current period percentages:

```sql
-- Reference Period: Use RefGroupPerc and RefMinorPerc
insert into dbo.TMP_TD045C2 (...)
select  ...
        ISNULL (-1 * (Amount * (100 - (ISNULL(b.RefGroupPerc, 0) + ISNULL(b.RefMinorPerc, 0))) / 100), 0) as Amount,
        ...
where   b.FlowID = @PreviousPeriodAdjFlowID

-- Percentage Change Impact: Send to VarPercInteg flow
insert into dbo.TMP_TD045C2 (...)
select  ...
        @VarPercIntegFlowID as FlowID,
        ISNULL (1 * (Amount * (ISNULL(b.GroupPerc, 0) + ISNULL(b.MinorPerc, 0)
                             - ISNULL(b.RefGroupPerc, 0) - ISNULL(b.RefMinorPerc, 0)) / 100), 0) as Amount,
        ...
```

### Company Selection

```sql
-- Select companies with ConsoMethod = 'P' for proportional elimination
insert into #SelectedCompanies (CompanyID)
    select  a.CompanyID
    from    #AllCompanies a
            inner join dbo.TS070S2 b
                on (b.ConsoMethodSelectionID = @ConsoMethodSelectionID
                    and b.ConsoMethod = a.ConsoMethod)
    where   a.IncludedInCompanySelection = 1
```

### Dimension Support

```sql
-- Proportional elimination also applies to dimensional data
if @ExecuteDimensions = 1
begin
    Insert into TMP_TD055C2 (...)
    select
        ...
        sum(ISNULL (-1 * (dimdata.Amount * (100 - (cpy.GroupPerc + cpy.MinorPerc)) / 100), 0)) as Amount,
        ...
    From cte55 dimdata
        inner join cte35 consodataS079 on (...)
        inner join TS014C0 cpy on (...)
    ...
end
```

### IFRS 11 Configuration

**Config Key**: `CALC_NO_PROPORTIONAL`

| Value | Effect |
|-------|--------|
| 0 (default) | Use proportional method for 50% JVs |
| 1 | Disable proportional; 50% JVs use equity method |

```sql
-- Check configuration
Select TOP 1 @NoProportionalMethod = CASE when [Value] = '0' then 0 else 1 end
From [dbo].[T_CONFIG]
Where [Key] = 'CALC_NO_PROPORTIONAL'
AND ([CustomerID] is null or [CustomerID] = @CustomerID)
Order by [CustomerID] DESC
```

## Theory vs Practice Analysis

| Aspect | Theory (IAS 31/IFRS 11) | Prophix.Conso Implementation | Alignment |
|--------|------------------------|------------------------------|-----------|
| 50% = Proportional | IAS 31 permits | ConsoMethod = 'P' | Full |
| Line-by-line integration | Required | All accounts at ownership % | Full |
| No minority interest | Required | MinorityFlag handling | Full |
| IFRS 11 option | JVs use equity | CALC_NO_PROPORTIONAL config | Full |
| Percentage change | Flow explanation | VarPercInteg flow | Full |
| Joint operation distinction | Required by IFRS 11 | Not explicit | Gap |

## Gap Analysis

### Missing Elements

1. **Joint Operation vs Joint Venture**: IFRS 11 distinguishes between joint operations (proportional) and joint ventures (equity); system uses threshold-based only
2. **Unanimous Consent Check**: Joint control requires unanimous consent; not explicitly modeled
3. **Contractual Arrangement**: No explicit tracking of JV agreements

### Divergent Implementation

1. **Threshold-Based Assignment**: System uses exactly 50% threshold; actual joint control assessment may differ

### Additional Features (Beyond Theory)

1. **IFRS 11 Toggle**: Configuration to switch between IAS 31 and IFRS 11 approaches
2. **Dimension Support**: Proportional elimination at dimensional level
3. **Percentage Change Flow**: Explicit tracking via VarPercInteg

## Business Impact

### Current Capabilities

1. **Full Proportional Consolidation**: All line items integrated at ownership %
2. **IAS 31 Compliance**: Standard proportional method available
3. **IFRS 11 Support**: Can disable proportional for JV equity treatment
4. **Flow Explanation**: Percentage changes tracked separately

### Operational Considerations

1. **Configuration Decision**: Choose IAS 31 vs IFRS 11 approach at setup
2. **Intercompany**: IC eliminations still apply at proportional %
3. **Ownership Changes**: Monitor VarPercInteg for % change impacts

## Recommendations

1. **Add JV Agreement Tracking**: Document contractual basis for joint control
2. **Joint Operation Support**: Explicit handling for IFRS 11 joint operations
3. **Unanimous Consent**: Add workflow for documenting joint control decisions

## API Reference

### Primary API Handlers
| Handler | YAML File | Purpose | Status |
|---------|-----------|---------|--------|
| `Consolidation_Execute` | [api-consolidation-endpoints.yaml](../11-agent-support/api-consolidation-endpoints.yaml) | Execute consolidation (includes S079) | ✅ IMPLEMENTED |
| `Ownership_GetOwnership` | [api-ownership-endpoints.yaml](../11-agent-support/api-ownership-endpoints.yaml) | Get 50% joint control ownership | ✅ IMPLEMENTED |
| `Company_SaveCompany` | [api-company-endpoints.yaml](../11-agent-support/api-company-endpoints.yaml) | Set ConsoMethod='P' | ✅ IMPLEMENTED |

### Supporting API Handlers
| Handler | YAML File | Purpose |
|---------|-----------|---------|
| `Elimination_GetEliminations` | [api-elimination-endpoints.yaml](../11-agent-support/api-elimination-endpoints.yaml) | Get S079 proportional eliminations |
| `IntercoDataEntry_GetData` | [api-interco-endpoints.yaml](../11-agent-support/api-interco-endpoints.yaml) | Intercompany at proportional % |

### API Workflow
```
1. Company_SaveCompany (ConsoMethod='P') → Set proportional method
2. Ownership_SaveOwnership → Record 50% ownership
3. Consolidation_Execute → S079 proportional eliminations
4. Report_ExecuteReport → Line-items at ownership %
```

### IFRS 11 Configuration
- **Config Key**: `CALC_NO_PROPORTIONAL` (set via admin)
- When `= 1`: 50% JVs use equity method (E) instead of proportional (P)

### Related API Documentation
- [API Index](../11-agent-support/api-index.yaml) - Master handler catalog
- [Gap Analysis](../11-agent-support/gap-analysis-report.yaml) - Theory alignment: **IAS 31/IFRS 11 compliant**

---

## See Also

### Related Consolidation Methods
- [Global Integration](global-integration.md) - >50% control (full consolidation)
- [Equity Method](equity-method.md) - Alternative for JVs under IFRS 11
- [Method Determination](consolidation-method-determination.md) - Threshold-based assignment

### Related Calculations & Eliminations
- [Step Acquisition](../03-core-calculations/step-acquisition.md) - P→G method transitions
- [Intercompany Transactions](../04-elimination-entries/intercompany-transactions.md) - IC eliminations at proportional %

### Related Ownership
- [Ownership Percentages](../06-ownership-structure/ownership-percentages.md) - Financial vs control %
- [Control vs Ownership](../06-ownership-structure/control-vs-ownership.md) - Joint control assessment

### Navigation
- [Cross-Reference Index](../00-index/CROSS_REFERENCE_INDEX.md) - Full document relationships
- [Executive Summary](../00-index/EXECUTIVE_SUMMARY.md) - Overview

### Technical References
- Knowledge Base: Chunks 0054-0055, 0166-0172, 0197, 0359-0363
- Code: `P_CONSO_ELIM_PROPORTIONAL.sql`

---
*Document 19 of 50+ | Batch 7: Standard Progression | Last Updated: 2024-12-01*
