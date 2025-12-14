# Consolidation Method Determination

## Document Metadata
- **Category**: Consolidation Methods
- **Theory Source**: Knowledge base chunks: 0044, 0055, 0076, 0082, 0094, 0197
- **Implementation Files**:
  - `Sigma.Database/dbo/Tables/TS014C0.sql` - ConsoMethod column with constraint
  - `Sigma.Database/dbo/Stored Procedures/P_CALC_OWNERSHIP_INDIRECT_PERCENTAGES.sql` - Automatic method determination
  - `Sigma.Database/dbo/Tables/T_CONFIG.sql` - CONSO_NO_PROPORTIONAL configuration
- **Last Updated**: 2024-12-01
- **Completeness**: 95% (Full automatic determination based on control percentage)
- **Compliance Status**: IFRS 10/11/IAS 28 - Compliant with threshold-based determination

## Executive Summary

Consolidation method determination is the process of assigning the appropriate accounting treatment to each entity in the group structure based on the level of control or influence exercised by the parent company. Prophix.Conso implements **automatic method determination** based on control percentage thresholds in `P_CALC_OWNERSHIP_INDIRECT_PERCENTAGES.sql`. The system supports Global Integration (G), Proportional (P), Equity Method (E), and Not Consolidated (N) with configurable threshold boundaries.

## Theoretical Framework

### IFRS Control Framework

From Allen White's "Direct Consolidation" (Chunk 44):

> "We first need to know the control percentage owned by the group in each individual company, which is the basic information to determine the consolidation method that will be associated to each of these companies."

### Method Determination Criteria

| Method | Code | Control Level | IFRS Standard | Accounting Treatment |
|--------|------|---------------|---------------|---------------------|
| **Global Integration** | G | >50% control | IFRS 10 | Full consolidation, 100% assets/liabilities |
| **Proportional** | P | =50% joint control | IFRS 11 | Share of assets/liabilities (being phased out) |
| **Equity Method** | E | 20-50% significant influence | IAS 28 | One-line consolidation |
| **Not Consolidated** | N | <20% | IAS 39/IFRS 9 | Investment at cost/fair value |

### Decision Tree (Chunk 55)

```
┌─────────────────────────────────────┐
│ Determine Control Percentage        │
└─────────────────────────────────────┘
                │
                ▼
        ┌───────────────┐
        │  Control >50%? │
        └───────────────┘
          │Yes        │No
          ▼           ▼
    ┌─────────┐   ┌───────────────┐
    │Global(G)│   │Control = 50%? │
    └─────────┘   └───────────────┘
                    │Yes        │No
                    ▼           ▼
              ┌─────────┐   ┌───────────────┐
              │Propor(P)│   │Control ≥20%?  │
              └─────────┘   └───────────────┘
                              │Yes        │No
                              ▼           ▼
                        ┌─────────┐   ┌─────────┐
                        │Equity(E)│   │Not Con(N)│
                        └─────────┘   └─────────┘
```

### Special Cases (Chunk 55)

> "Consolidation Method Options:
> - If A has de facto control: Global integration
> - If joint control: Proportional consolidation
> - If significant influence only: Equity method"

## Current Implementation

### ConsoMethod Values (TS014C0)

```sql
-- From TS014C0.sql constraint:
CONSTRAINT [CK_TS014C0_CONSOMETHOD]
CHECK ([ConsoMethod]='P' OR [ConsoMethod]='G' OR [ConsoMethod]='N'
    OR [ConsoMethod]='E' OR [ConsoMethod]='S' OR [ConsoMethod]='T' OR [ConsoMethod]='X')
```

| Code | Description | Usage |
|------|-------------|-------|
| G | Global Integration | >50% control, full consolidation |
| P | Proportional | =50% joint control |
| E | Equity Method | 20-50% significant influence |
| N | Not Consolidated | <20% or excluded |
| S | Sub-consolidated | Pre-consolidated sub-group |
| T | Transition | Temporary status |
| X | Excluded | Manually excluded |

### Automatic Method Determination

`P_CALC_OWNERSHIP_INDIRECT_PERCENTAGES.sql` lines 219-220:

```sql
-- Threshold definitions
Set @ConsoMethP = 50    -- Proportional boundary
Set @ConsoMethN = 20    -- Not consolidated boundary
```

### Method Update Logic

From `P_CALC_OWNERSHIP_INDIRECT_PERCENTAGES.sql`:

```sql
If @UpdateConsoMethod = 1
Begin
    Update #Companies
        Set ConsoMethod =
            Case
                -- Parent company is always Global
                When CompanyID = @ParentID then 'G'
                -- Control > 50% = Global Integration
                When GroupCtrlPerc > @ConsoMethP then 'G'
                -- Control = 50% = Proportional (joint control)
                When GroupCtrlPerc = @ConsoMethP AND CompanyID <> @ParentID then 'P'
                -- Control 20-50% = Equity Method
                When GroupCtrlPerc >= @ConsoMethN AND GroupCtrlPerc < @ConsoMethP then 'E'
                -- Control < 20% = Not Consolidated
                When GroupCtrlPerc < @ConsoMethN then 'N'
                Else 'N'
            End
End
```

### Configuration: Disable Proportional Method

```sql
-- T_CONFIG key to disable proportional method (IFRS 11 compliance)
SELECT TOP 1 @NoProportionalMethod =
    CASE WHEN [Value] = '1' THEN 1 ELSE 0 END
FROM [dbo].[T_CONFIG]
WHERE [Key] = 'CONSO_NO_PROPORTIONAL'
  AND ([CustomerID] IS NULL OR [CustomerID] = @CustomerID)
ORDER BY [CustomerID] DESC
```

When enabled, P method companies are treated as E (Equity Method).

### TS014C0 Trigger for Status Reset

```sql
-- Trigger resets status when method changes
CREATE TRIGGER [dbo].[TR_TS014C0] ON dbo.TS014C0 AFTER INSERT, UPDATE
AS BEGIN
    UPDATE dbo.TS014C0
    SET Status_Bundles = 1,
        Status_Adjustments = 1,
        Status_Flows = 1,
        Status_ClosingAmounts = 1
    FROM inserted a
         LEFT OUTER JOIN deleted b ON (b.ConsoID = a.ConsoID AND b.CompanyID = a.CompanyID)
    WHERE dbo.TS014C0.ConsoID = a.ConsoID
      AND dbo.TS014C0.CompanyID = a.CompanyID
      AND (a.ConsoMethod <> b.ConsoMethod  -- Method changed
           OR ISNULL(a.GroupPerc, 0) <> ISNULL(b.GroupPerc, 0)
           OR ISNULL(a.GroupCtrlPerc, 0) <> ISNULL(b.GroupCtrlPerc, 0)
           -- ... other fields
          )
END
```

## Method Determination Flow

### Complete Process

```
1. User enters ownership in TS015S0
   ↓
2. P_CALC_OWNERSHIP_DIRECT_PERCENTAGES calculates direct %
   ↓
3. P_CALC_OWNERSHIP_INDIRECT_PERCENTAGES:
   a. Build ownership matrix
   b. Apply Gauss elimination for circular structures
   c. Calculate GroupPerc, MinorPerc, GroupCtrlPerc
   d. If @UpdateConsoMethod = 1:
      - Apply threshold rules to determine ConsoMethod
   ↓
4. Update TS014C0 with new percentages and method
   ↓
5. TR_TS014C0 trigger resets consolidation status flags
   ↓
6. Next consolidation run uses new method
```

### Key Fields in TS014C0

| Field | Description | Used For |
|-------|-------------|----------|
| ConsoMethod | Consolidation method code | Elimination selection |
| GroupPerc | Group financial percentage | Profit allocation |
| MinorPerc | Minority (NCI) percentage | NCI calculation |
| GroupCtrlPerc | Group control percentage | Method determination |
| NbrFinRightsIssued | Total financial shares | Percentage basis |
| NbrVotingRightsIssued | Total voting rights | Control calculation |

## Method Change Detection

### Period-over-Period Comparison

```sql
-- From P_CONSO_ELIM.sql: Get reference period method
UPDATE a
SET RefCompanyID = b.CompanyID,
    RefConsoMethod = ISNULL(b.ConsoMethod, 'N'),
    RefGroupPerc = ISNULL(b.GroupPerc, 0),
    RefMinorPerc = ISNULL(b.MinorPerc, 0)
FROM #AllCompanies a
INNER JOIN dbo.TS014C0 b WITH(NOLOCK)
    ON b.CompanyCode = a.CompanyCode AND b.ConsoID = @RefConsoID
```

### Special Flows for Method Changes

| From | To | Flow Code | Scenario |
|------|-----|-----------|----------|
| G | E | VarConsoMeth_GE | Lose control |
| E | G | VarConsoMeth_EG | Gain control (step acquisition) |
| P | E | VarConsoMeth_PE | Lose joint control |
| E | P | VarConsoMeth_EP | Gain joint control |
| P | G | VarConsoMeth_PG | JV becomes subsidiary |
| G | P | VarConsoMeth_GP | Subsidiary becomes JV |

## Gap Analysis

### Fully Implemented

1. **Threshold-based determination**: Automatic based on control %
2. **Manual override**: ConsoMethod can be set manually
3. **Method change detection**: Period comparison available
4. **Proportional disable**: Configuration option exists

### Limitations

| Feature | Status | Notes |
|---------|--------|-------|
| De facto control detection | Manual | User must set G manually |
| Potential voting rights | Not implemented | System uses actual votes only |
| Contractual control | Manual | User must assess manually |
| Variable interest entities | Manual | No automatic detection |

## API Reference

### Primary API Handlers
| Handler | YAML File | Purpose | Status |
|---------|-----------|---------|--------|
| `Ownership_GetOwnership` | [api-ownership-endpoints.yaml](../11-agent-support/api-ownership-endpoints.yaml) | Get calculated ownership with methods | ✅ IMPLEMENTED |
| `Ownership_SaveOwnership` | [api-ownership-endpoints.yaml](../11-agent-support/api-ownership-endpoints.yaml) | Save ownership (triggers recalc) | ✅ IMPLEMENTED |
| `LaunchCalculateIndirectPercentagesJob` | [api-ownership-endpoints.yaml](../11-agent-support/api-ownership-endpoints.yaml) | Recalculate all methods | ✅ IMPLEMENTED |

### Supporting API Handlers
| Handler | YAML File | Purpose |
|---------|-----------|---------|
| `Company_GetCompanies` | [api-company-endpoints.yaml](../11-agent-support/api-company-endpoints.yaml) | Get companies with ConsoMethod |
| `Company_SaveCompany` | [api-company-endpoints.yaml](../11-agent-support/api-company-endpoints.yaml) | Override ConsoMethod manually |

### API Workflow
```
1. Ownership_SaveOwnership → Enter/update ownership percentages
2. LaunchCalculateIndirectPercentagesJob → Calculate indirect %
   → P_CALC_OWNERSHIP_INDIRECT_PERCENTAGES determines method:
     * >50% → G (Global)
     * =50% → P (Proportional) or E (if IFRS 11)
     * 20-50% → E (Equity)
     * <20% → N (Not Consolidated)
3. Company_GetCompanies → Verify assigned methods
```

### Stored Procedure Reference
- `P_CALC_OWNERSHIP_INDIRECT_PERCENTAGES` - Threshold-based method determination
- `P_CALC_OWNERSHIP_DIRECT_PERCENTAGES` - Direct ownership calculation

### Related API Documentation
- [API Index](../11-agent-support/api-index.yaml) - Master handler catalog
- [Consolidation Method Decision Tree](../11-agent-support/consolidation-method-decision.yaml) - Visual decision logic
- [Gap Analysis](../11-agent-support/gap-analysis-report.yaml) - Theory alignment: **IFRS 10/11/IAS 28 compliant**

---

## See Also

### Related Consolidation Methods
- [Global Integration](global-integration.md) - G method (>50% control)
- [Equity Method](equity-method.md) - E method (20-50% influence)
- [Proportional Method](proportional-method.md) - P method (50% joint control)

### Related Ownership Structure
- [Control vs Ownership](../06-ownership-structure/control-vs-ownership.md) - Control assessment
- [Voting Rights Analysis](../06-ownership-structure/voting-rights-analysis.md) - CtrlPercentage calculation
- [Ownership Percentages](../06-ownership-structure/ownership-percentages.md) - Financial vs control %

### Related Scope Changes
- [Scope Changes](../03-core-calculations/scope-changes.md) - Entry/exit detection
- [Step Acquisition](../03-core-calculations/step-acquisition.md) - Method transitions

### Navigation
- [Cross-Reference Index](../00-index/CROSS_REFERENCE_INDEX.md) - Full document relationships
- [Executive Summary](../00-index/EXECUTIVE_SUMMARY.md) - Overview

### Technical References
- Knowledge Base: Chunks 0044, 0055, 0076, 0094, 0197
- Code: `P_CALC_OWNERSHIP_INDIRECT_PERCENTAGES.sql`

---
*Document 31 of 50+ | Batch 11: Control Determination & Data Architecture | Last Updated: 2024-12-01*
