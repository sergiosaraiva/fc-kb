# Direct and Indirect Holdings in Group Structures

## Document Metadata
- **Category**: Ownership Structure
- **Theory Source**: Knowledge base chunks: 0027, 0050, 0066, 0067, 0070, 0083, 0087
- **Implementation Files**:
  - `Sigma.Database/dbo/Tables/TS014C0.sql` (Company structure with percentages)
  - `Sigma.Database/dbo/Tables/TS015S0.sql` (Direct ownership relationships)
  - `Sigma.Database/dbo/Stored Procedures/P_CALC_OWNERSHIP_DIRECT_PERCENTAGES.sql`
  - `Sigma.Database/dbo/Stored Procedures/P_CALC_OWNERSHIP_INDIRECT_PERCENTAGES.sql`
  - `Sigma.Database/dbo/Stored Procedures/P_VIEW_OWNERSHIP.sql`
  - `Sigma.Database/dbo/Stored Procedures/P_VIEW_OWNERSHIP_DETAIL.sql`
- **Last Updated**: 2024-12-01
- **Completeness**: 95% (Full matrix-based indirect calculation implemented)
- **Compliance Status**: IFRS 10 - Control Assessment

## Executive Summary

Prophix.Conso implements a sophisticated matrix-based algorithm for calculating both direct and indirect ownership percentages. Direct holdings are stored in TS015S0 (ownership table) and calculated via `P_CALC_OWNERSHIP_DIRECT_PERCENTAGES`. Indirect holdings are computed using Gauss elimination matrix inversion in `P_CALC_OWNERSHIP_INDIRECT_PERCENTAGES`, which handles multi-level ownership chains and cross-holdings (excluding circular ownership).

## Theoretical Framework

### Concept Definition

From Allen White's "Direct Consolidation" (Chunk 27):

> "Each ownership relationship requires percentage determination. Different consolidation methods may apply (global, proportional, equity). Eliminations needed between group companies. Minority interests calculation at each level."

### Direct Holdings

**Direct holding** represents the immediate ownership relationship between two entities:
- Parent A owns 75% of Subsidiary B = Direct holding of 75%
- This is stored at the relationship level (who owns whom)

### Indirect Holdings

**Indirect holding** represents ownership through intermediate entities:
- If Parent A owns 75% of B, and B owns 80% of C
- A's indirect holding in C = 75% × 80% = 60%

### Key Principles

1. **Financial Interest (FinPercentage)**: Right to dividends and net assets
2. **Voting Rights (CtrlPercentage)**: Power over investee decisions
3. **Group Percentage (GroupPerc)**: Cumulative indirect ownership from parent perspective
4. **Minority Percentage (MinorPerc)**: Portion not owned by the group (100% - GroupPerc for global integration)

### Formula/Algorithm

**Direct Percentage Calculation**:
```
FinPercentage = (NbrFinRights / NbrFinRightsIssued) × 100
CtrlPercentage = (NbrVotingRights / NbrVotingRightsIssued) × 100
```

**Indirect Percentage Calculation** (Matrix Method):
```
Let A = Ownership Matrix (row i owns col j)
Let I = Identity Matrix
Let X = I - A

Group Percentages = B × X^(-1)

Where:
- X^(-1) is calculated via Gauss elimination
- B = Selection vector (1 in parent position, 0 elsewhere)
```

### Example

**Simple Chain (Chunk 66-67)**:
```
Parent P owns 75% of B
B owns 90% of C

Direct Holdings:
- P → B: 75%
- B → C: 90%

Indirect Holdings:
- P → C: 75% × 90% = 67.5%

Minority Interests:
- In B: 25% (100% - 75%)
- In C: 32.5% (100% - 67.5%)
```

**Multi-Level Structure**:
```
        ┌──────┐
        │  P   │ (Parent)
        └──┬───┘
           │ 75%
           ▼
        ┌──────┐
        │  B   │
        └──┬───┘
           │ 90%
           ▼
        ┌──────┐
        │  C   │
        └──────┘

Group percentages:
- P: 100% (always)
- B: 75%
- C: 67.5%

Minority percentages:
- P: 0%
- B: 25%
- C: 32.5%
```

## Current Implementation

### Database Layer

#### Company Structure Table (TS014C0)

```sql
CREATE TABLE [dbo].[TS014C0] (
    [CompanyID]            INT            NOT NULL,
    [ConsoID]              INT            NOT NULL,
    [CompanyCode]          NVARCHAR(12)   NOT NULL,
    [ConsoMethod]          CHAR(1)        DEFAULT('G'),  -- G=Global, P=Proportional, E=Equity, N=Not consolidated
    [GroupPerc]            DECIMAL(9,6)   DEFAULT((0)),  -- Indirect financial percentage
    [MinorPerc]            DECIMAL(9,6)   DEFAULT((0)),  -- Third-party percentage
    [GroupCtrlPerc]        DECIMAL(9,6)   DEFAULT((0)),  -- Indirect control percentage
    [NbrFinRightsIssued]   BIGINT         DEFAULT((0)),  -- Total shares issued
    [NbrVotingRightsIssued] BIGINT        DEFAULT((0)),  -- Total voting rights issued
    [ConsolidatedCompany]  BIT            DEFAULT((1)),  -- Include in consolidation
    -- ... additional fields
);
```

**Key Fields**:
- `GroupPerc`: Calculated indirect ownership from parent (result of matrix calculation)
- `MinorPerc`: Minority interest percentage (100% - GroupPerc for global integration)
- `GroupCtrlPerc`: Calculated indirect control percentage (for method determination)
- `ConsoMethod`: Consolidation method derived from GroupCtrlPerc thresholds

#### Ownership Relationships Table (TS015S0)

```sql
CREATE TABLE [dbo].[TS015S0] (
    [ControlID]       INT            IDENTITY NOT NULL,
    [ConsoID]         INT            NOT NULL,
    [CompanyID]       INT            NOT NULL,      -- Owner (shareholder)
    [CompanyOwnedID]  INT            NOT NULL,      -- Owned company
    [FinPercentage]   DECIMAL(9,6)   DEFAULT((0)),  -- Direct financial %
    [CtrlPercentage]  DECIMAL(9,6)   DEFAULT((0)),  -- Direct voting/control %
    [NbrFinRights]    BIGINT         DEFAULT((0)),  -- Number of financial rights
    [NbrVotingRights] BIGINT         DEFAULT((0)),  -- Number of voting rights
);
```

**Purpose**: Stores the direct ownership links between companies. Each row represents one ownership relationship (shareholder → company).

### Direct Percentage Calculation

From `P_CALC_OWNERSHIP_DIRECT_PERCENTAGES.sql`:

```sql
-- Calculate direct percentages from share counts
if @NbrFinRightsIssued = 0
    set @FinPercentage = null  -- Can't divide by zero
else if (@NbrFinRights / @NbrFinRightsIssued >= 10)
begin
    set @FinPercentage = 0     -- Exceeds maximum allowed
    select @errorinfo = dbo.AddWarning2('INVALID_FIN_PERCENTAGE', ...)
end
else
    set @FinPercentage = 100 * (cast(@NbrFinRights as float) / @NbrFinRightsIssued)

-- Same logic for control percentage
if @NbrVotingRightsIssued = 0
    set @CtrlPercentage = null
else
    set @CtrlPercentage = 100 * (cast(@NbrVotingRights as float) / @NbrVotingRightsIssued)

-- Update ownership record
update dbo.TS015S0
set    FinPercentage = @FinPercentage,
       CtrlPercentage = @CtrlPercentage
where  ConsoID = @ConsoID and ControlID = @ControlID
```

### Indirect Percentage Calculation (Matrix Algorithm)

From `P_CALC_OWNERSHIP_INDIRECT_PERCENTAGES.sql`:

**Step 1: Build Ownership Matrix**
```sql
-- Create matrix A where A[i,j] = ownership percentage of company i in company j
Insert into #Matrices
Select 1 As MatrixNo,
       b.SortID as Row,      -- Owner company
       c.SortID as Col,      -- Owned company
       0 as val
From #Companies b cross join #Companies c

-- Fill matrix with direct ownership percentages
Update #Matrices
Set val = c.FinPercentage / 100
From #Matrices
    inner join #Companies a On (a.SortID = #Matrices.Row)
    inner join #Companies b On (b.SortID = #Matrices.Col)
    inner join #OwnerShip c on (c.CompanyID = a.CompanyID
                               and c.CompanyOwnedID = b.CompanyID)
```

**Step 2: Add Third Parties Row**
```sql
-- Calculate third-party ownership as (1 - sum of internal ownership)
Update #Matrices
Set val = b.val
From #Matrices
    Inner Join (
        Select 1 as MatrixNo,
               @MaxSortID + 1 as Row,  -- Third parties row
               b.Col as Col,
               1 - sum(b.val) as val   -- Remainder goes to third parties
        From #Matrices b
        Where MatrixNo = 1 and b.Col <> 1 and b.Col <> (@MaxSortID + 1)
        Group By b.Col
    ) b On (b.MatrixNo = #Matrices.MatrixNo
           and b.Row = #Matrices.Row
           and b.Col = #Matrices.Col)
```

**Step 3: Matrix Inversion via Gauss Elimination**
```sql
-- Build X = I - A (Identity minus ownership matrix)
Insert into #Matrices
Select 3 as MatrixNr,
       [Row], [Col],
       Case when [Row] = [Col] then 1-ISNULL(val, 0)
            else ISNULL(val, 0)*-1
       end as val
From #Matrices where MatrixNo = 1

-- Gauss elimination to find X^(-1)
-- Uses augmented matrix [X | I] and row operations
-- After completion, right side contains X^(-1)
```

**Step 4: Calculate Group Percentages**
```sql
-- Multiply selection vector B by inverse matrix
-- B = [1, 0, 0, ...] (1 in parent position)
-- Result gives group percentage for each company

INSERT INTO #Matrices
SELECT 6 As MatrixNo, A.Row, B.Col, SUM(A.val * B.val) AS val
FROM #Matrices A JOIN #Matrices B
ON A.MatrixNo = 5      -- Selection matrix B
AND B.MatrixNo = 4     -- Inverse matrix X^(-1)
AND A.Col = B.Row
WHERE A.Row = 1        -- Parent row
GROUP BY A.Row, B.Col

-- Update companies with calculated percentages
Update #Companies
Set GroupPerc = ROUND(b.val * 100, 16)
From #Companies
    inner join #Matrices b
        ON (b.MatrixNo = 6 and b.Row = 1 and b.Col = #Companies.SortID)
Where #Companies.SortID <> 1  -- Exclude parent
```

### Consolidation Method Determination

```sql
-- Method thresholds (configurable)
Set @ConsoMethP = 50  -- Proportional threshold
Set @ConsoMethN = 20  -- Not consolidated threshold

-- Determine method from control percentage
Update #Companies
Set ConsoMethod =
    Case
        When (GroupCtrlPerc > @ConsoMethP OR CompanyID = @ParentID) then 'G'  -- Global
        When (GroupCtrlPerc = @ConsoMethP AND CompanyID <> @ParentID) then 'P' -- Proportional
        When (GroupCtrlPerc >= @ConsoMethN AND GroupCtrlPerc < @ConsoMethP) then 'E' -- Equity
        When (GroupCtrlPerc < @ConsoMethN) then 'N'  -- Not consolidated
        Else 'N'
    End
```

### Control Percentage Propagation

The control percentage calculation uses iterative propagation:

```sql
-- Loop through ownership until no more changes
WHILE @CounterI <= @MaxLoop
BEGIN
    UPDATE #GroupControl
    Set OldCtrl = NewCtrl

    UPDATE #GroupControl
    Set NewCtrl = SumTS015.CtrlSubTotal
    FROM #GroupControl a
    JOIN (
        SELECT a.CompanyOwnedID,
               sum(cast(a.NbrVotingRights as float) /
                   cast(b.NbrVotingRightsIssued as float) * 100) as CtrlSubTotal
        FROM #OwnerShip a
            Inner Join #Companies b on (b.CompanyID = a.CompanyOwnedID)
        WHERE a.CompanyID IN (
            SELECT CompanyID from #GroupControl where NewCtrl > 50  -- Only controlled companies
        )
        GROUP BY a.CompanyOwnedID
    ) SumTS015 ON SumTS015.CompanyOwnedID = a.CompanyID

    -- Exit when no changes detected
    IF (SELECT count(*) FROM #GroupControl WHERE OldCtrl <> NewCtrl) = 0
        SET @CounterI = @MaxLoop + 1

    SET @CounterI = @CounterI + 1
END
```

### Minority Interest Calculation

**For Global Integration (G)**:
```sql
Update #Companies
Set MinorPerc = ROUND(100 - GroupPerc, 16)
Where ConsoMethod in ('G', 'N')
      and CompanyID <> @ParentID
```

**For Equity/Proportional Methods**:
The system uses a separate Phase 2 calculation that builds a modified ownership matrix for third-party perspective calculations.

## Theory vs Practice Analysis

| Aspect | Theory (Allen White) | Prophix.Conso Implementation | Alignment |
|--------|---------------------|------------------------------|-----------|
| Direct Holdings | Share-based ownership | TS015S0 with NbrFinRights/NbrVotingRights | Full |
| Indirect Holdings | Multiplicative chain | Matrix inversion (Gauss elimination) | Full |
| Multi-Level Chains | Sequential multiplication | Single matrix operation | Enhanced |
| Control Determination | >50% voting = control | Iterative propagation algorithm | Full |
| Method Thresholds | Standard IFRS ranges | Configurable (50%/20% defaults) | Full |
| Cross-Holdings | Complex scenarios | Matrix handles non-circular cross-holdings | Partial |

## Gap Analysis

### Missing Elements

1. **Circular Ownership**: The matrix algorithm cannot handle circular ownership (A owns B owns C owns A) - results in matrix singularity
2. **Treasury Shares**: No automatic exclusion of treasury shares from voting rights calculation (must be manually adjusted)

### Divergent Implementation

1. **Precision**: Implementation uses DECIMAL(28,16) during calculation, rounded to DECIMAL(9,6) for storage - may cause minor precision loss in complex structures

### Additional Features (Beyond Theory)

1. **Matrix-Based Calculation**: Single-step calculation for all indirect percentages (more efficient than iterative chain multiplication)
2. **Session-Based Results**: `@UseSessionTable` parameter allows writing to temporary table for what-if analysis
3. **Configurable Thresholds**: `CALC_NO_PROPORTIONAL` and `GENERAL_COMPUTE_INDIRECT_THIRDS` configuration keys
4. **Validation Checks**: Automatic detection of companies without shareholders, invalid share counts

## Business Impact

1. **Accurate Consolidation**: Correct ownership percentages ensure proper consolidation method selection
2. **Minority Interest**: Accurate calculation of non-controlling interests
3. **Audit Compliance**: Complete ownership chain documentation for auditors
4. **What-If Analysis**: Session-based calculation supports scenario planning

## Recommendations

1. **Implement Circular Ownership Detection**: Add validation to detect circular ownership before calculation, with user warning
2. **Treasury Share Automation**: Consider automatic exclusion of treasury shares from voting rights calculation
3. **Calculation History**: Store historical ownership percentage calculations for audit trail

## API Reference

### Primary API Handlers
| Handler | YAML File | Purpose | Status |
|---------|-----------|---------|--------|
| `Ownership_GetOwnerships` | [api-ownership-endpoints.yaml](../11-agent-support/api-ownership-endpoints.yaml) | Get direct ownership from TS015S0 | ✅ IMPLEMENTED |
| `Ownership_SaveOwnership` | [api-ownership-endpoints.yaml](../11-agent-support/api-ownership-endpoints.yaml) | Update ownership relationships | ✅ IMPLEMENTED |
| `Ownership_CalculatePercentages` | [api-ownership-endpoints.yaml](../11-agent-support/api-ownership-endpoints.yaml) | Trigger P_CALC_OWNERSHIP_* procedures | ✅ IMPLEMENTED |

### Supporting API Handlers
| Handler | YAML File | Purpose |
|---------|-----------|---------|
| `Company_GetCompanies` | [api-company-endpoints.yaml](../11-agent-support/api-company-endpoints.yaml) | Get GroupPerc, MinorPerc, GroupCtrlPerc |
| `Consolidation_Execute` | [api-consolidation-endpoints.yaml](../11-agent-support/api-consolidation-endpoints.yaml) | Run full consolidation with ownership calc |
| `Report_ExecuteReport` | [api-reports-endpoints.yaml](../11-agent-support/api-reports-endpoints.yaml) | P_VIEW_OWNERSHIP, P_VIEW_OWNERSHIP_DETAIL |

### API Workflow
```
Ownership Calculation via API:

1. DIRECT OWNERSHIP ENTRY
   Ownership_SaveOwnership → TS015S0:
     - CompanyID (shareholder)
     - CompanyOwnedID (owned company)
     - NbrFinRights (financial shares)
     - NbrVotingRights (voting rights)

2. PERCENTAGE CALCULATION
   Ownership_CalculatePercentages:
     - P_CALC_OWNERSHIP_DIRECT_PERCENTAGES (FinPercentage, CtrlPercentage)
     - P_CALC_OWNERSHIP_INDIRECT_PERCENTAGES (GroupPerc, MinorPerc, GroupCtrlPerc)
     - Matrix inversion via Gauss elimination

3. CONSOLIDATION METHOD DETERMINATION
   Automatic based on GroupCtrlPerc:
     - >50%: G (Global Integration)
     - =50%: P (Proportional)
     - 20-50%: E (Equity Method)
     - <20%: N (Not Consolidated)

4. REPORTING
   Report_ExecuteReport → P_VIEW_OWNERSHIP:
     - Ownership structure visualization
     - Direct/indirect percentage breakdown
```

### Implementation Status
| Feature | Status | Notes |
|---------|--------|-------|
| Direct percentage calculation | ✅ IMPLEMENTED | P_CALC_OWNERSHIP_DIRECT_PERCENTAGES |
| Matrix-based indirect calculation | ✅ IMPLEMENTED | Gauss elimination |
| Multi-level chain support | ✅ IMPLEMENTED | Unlimited depth |
| Cross-holdings | ✅ IMPLEMENTED | Non-circular only |
| Circular ownership | ⚠️ PARTIAL | Results in matrix singularity |

### Related API Documentation
- [API Index](../11-agent-support/api-index.yaml) - Master handler catalog
- [Gap Analysis](../11-agent-support/gap-analysis-report.yaml) - **FULLY IMPLEMENTED (95%)**

---

## Related Documentation

- [Ownership Percentages](ownership-percentages.md) - Financial vs voting percentages
- [Control vs Ownership](control-vs-ownership.md) - Control determination rules
- [Minority Interest](../03-core-calculations/minority-interest.md) - NCI calculation

### Related Knowledge Chunks
- Chunk 0027: Consolidation Considerations (percentage determination)
- Chunk 0050: Consolidation Implications (full line-by-line consolidation)
- Chunk 0066-0067: Minority Interest Examples
- Chunk 0070: Equal Three-Way Joint Ownership
- Chunk 0083: Treasury Shares

---
*Document 13 of 50+ | Batch 5: Ownership Structure | Last Updated: 2024-12-01*
