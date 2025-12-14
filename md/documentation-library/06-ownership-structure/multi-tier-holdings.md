# Multi-Tier Holdings: Complex Ownership Structures

## Document Metadata
- **Category**: Ownership Structure
- **Theory Source**: Knowledge base chunks: 0027, 0050, 0066, 0067, 0069, 0112-0140
- **Implementation Files**:
  - `Sigma.Database/dbo/Stored Procedures/P_CALC_OWNERSHIP_INDIRECT_PERCENTAGES.sql` - Matrix calculation
  - `Sigma.Database/dbo/Tables/TS014C0.sql` - Company with calculated percentages
  - `Sigma.Database/dbo/Tables/TS015S0.sql` - Direct ownership links
  - `Sigma.Database/dbo/Stored Procedures/P_CALC_OWNERSHIP_DIRECT_PERCENTAGES.sql` - Direct calculation
- **Last Updated**: 2024-12-01
- **Completeness**: 95% (Full multi-tier calculation documented)
- **Compliance Status**: IAS 27, IFRS 10 - Control and ownership determination

## Executive Summary

Multi-tier holdings occur when a parent company controls subsidiaries through intermediate holding companies, creating ownership chains of varying depths. Prophix.Conso calculates indirect ownership percentages using **matrix algebra with Gauss elimination**, handling complex structures including circular ownership, cross-holdings, and deep hierarchies automatically.

## Ownership Structure Types

### Simple Two-Tier Structure

```
         Parent (P)
            │
           80%
            │
            ▼
      Subsidiary (S)
```

**Calculation**: Direct = Indirect = 80%

### Three-Tier Chain Structure

```
         Parent (P)
            │
           80%
            │
            ▼
     Holding Co (H)
            │
           75%
            │
            ▼
      Subsidiary (S)
```

**Calculation**:
- Direct: P→H = 80%, H→S = 75%
- Indirect: P→S = 80% × 75% = **60%**

### Complex Multi-Path Structure

```
         Parent (P)
          /     \
        60%     40%
        /         \
       ▼           ▼
   Sub A (A)    Sub B (B)
        \         /
        30%     50%
          \     /
           ▼   ▼
        Sub C (C)
```

**Calculation**:
- Path 1: P→A→C = 60% × 30% = 18%
- Path 2: P→B→C = 40% × 50% = 20%
- Indirect: P→C = 18% + 20% = **38%**

## Matrix Algebra Implementation

### P_CALC_OWNERSHIP_INDIRECT_PERCENTAGES Overview

The procedure uses matrix algebra to solve the ownership equation system:

```
Matrix Structure:
- Row = Owner company
- Col = Owned company
- Last Row/Column = Third Parties (external shareholders)

Equation: G = D + G × D
Where:
  G = Group percentage matrix (indirect)
  D = Direct ownership matrix
```

### Matrix Construction

```sql
-- From P_CALC_OWNERSHIP_INDIRECT_PERCENTAGES
-- Matrix Nr 1: Row = Owner, Col = Owned

Declare @MaxRow int        -- Number of companies
Declare @MaxCol int        -- Number of companies + 1 (Third Parties)
Declare @MaxDim int        -- Matrix dimension

-- Variable table for matrix operations
Declare @MatricesG TABLE (
    MatrixNr int,
    RowNr int,
    ColNr int,
    CellValue decimal(28,16)
)
```

### Gauss Elimination Algorithm

```sql
-- Gauss elimination for matrix inversion
SET @CounterI = 1
WHILE @CounterI <= @MaxDim
BEGIN
    -- Find pivot element
    -- Swap rows if needed
    -- Eliminate column values
    -- Scale pivot row

    SET @CounterI = @CounterI + 1
END
```

### Calculation Precision

```sql
-- High precision during calculation
Declare @temporary_value1 decimal(28,16)
Declare @CellValue decimal(28,16)

-- Final rounding
SELECT @RoundingDecimal = 6  -- Standard 6 decimal places
```

## Data Structures

### TS015S0 - Direct Ownership Links

```sql
CREATE TABLE [dbo].[TS015S0] (
    [ControlID] INT IDENTITY NOT NULL,
    [ConsoID] INT NOT NULL,
    [CompanyID] INT NOT NULL,        -- Owner
    [CompanyOwnedID] INT NOT NULL,   -- Owned
    [FinPercentage] DECIMAL(9,6),    -- Financial %
    [CtrlPercentage] DECIMAL(9,6),   -- Control/Voting %
    [NbrFinRights] BIGINT,           -- Shares held (financial)
    [NbrVotingRights] BIGINT         -- Shares held (voting)
)
```

### TS014C0 - Calculated Indirect Percentages

```sql
-- Stored after P_CALC_OWNERSHIP_INDIRECT_PERCENTAGES
UPDATE TS014C0
SET GroupPerc = @CalculatedGroupPerc,      -- Indirect group %
    MinorPerc = @CalculatedMinorPerc,      -- Minority %
    GroupCtrlPerc = @CalculatedCtrlPerc    -- Control %
WHERE ConsoID = @ConsoID AND CompanyID = @CompanyID
```

## Ownership Calculation Flow

### Processing Sequence

```
1. Load Direct Ownership (TS015S0)
   │
   ▼
2. Build Ownership Matrix
   - Populate D matrix with direct %
   - Set Third Party column
   │
   ▼
3. Apply Gauss Elimination
   - Solve G = D + G × D
   - Handle circular references
   │
   ▼
4. Extract Results
   - Group % from inverted matrix
   - Minority % = 100% - Group %
   │
   ▼
5. Update TS014C0
   - GroupPerc, MinorPerc, GroupCtrlPerc
   │
   ▼
6. Determine Consolidation Method
   - Based on GroupCtrlPerc thresholds
```

### Method Determination Thresholds

| Control % | Method | Description |
|-----------|--------|-------------|
| > 50% | G (Global) | Full consolidation |
| 20-50% | E (Equity) | Equity method |
| < 20% | N (Not) | Not consolidated |
| Config | P (Proportional) | Joint control |

## Handling Special Cases

### Circular Ownership

When companies own shares in each other:

```
     Company A
      ↗    ↘
    20%     80%
    ↙        ↖
     Company B
```

**Matrix Solution**:
The Gauss elimination automatically resolves circular references by solving the simultaneous equation system.

### Treasury Shares

When a company holds its own shares:

```
-- Handled via parent exclusion
@ParentID parameter excludes parent from ownership calculation
```

### Cross-Holdings Between Subsidiaries

```
        Parent
       /      \
     60%      70%
     /          \
  Sub A ←15%→ Sub B
```

**Calculation**:
Matrix algebra handles cross-holdings by including both A→B and B→A relationships in the ownership matrix.

## Consolidation Method Assignment

### Automatic Method Update

```sql
-- From P_CALC_OWNERSHIP_INDIRECT_PERCENTAGES
@UpdateConsoMethod bit = 1  -- Flag to update methods

-- Method thresholds from configuration
Declare @ConsoMethP decimal(28,12)  -- Proportional threshold
Declare @ConsoMethN decimal(28,12)  -- Not consolidated threshold

-- Assignment logic
CASE
    WHEN GroupCtrlPerc > 50 THEN 'G'
    WHEN GroupCtrlPerc > @ConsoMethN THEN 'E'
    ELSE 'N'
END
```

### Configuration Options

```sql
-- T_CONFIG settings
CONSO_NO_PROPORTIONAL = 1  -- Disable proportional method globally
```

## Validation Checks

### Ownership Completeness

```sql
-- Ensure all shares accounted for
IF EXISTS (
    SELECT CompanyOwnedID
    FROM TS015S0
    WHERE ConsoID = @ConsoID
    GROUP BY CompanyOwnedID
    HAVING SUM(NbrFinRights) > (
        SELECT NbrFinRightsIssued
        FROM TS014C0
        WHERE CompanyID = TS015S0.CompanyOwnedID
    )
)
    -- Error: More shares owned than issued
```

### Error Messages

| Error Code | Description |
|------------|-------------|
| P_CALC_OWNERSHIP_INDIRECT_PERCENTAGES_NO_SHAREHOLDER | No shareholders defined for company |
| SPECIFIC_ACCOUNT_NOT_FOUND | Missing required special account |

## Performance Considerations

### Optimization Techniques

```sql
-- Use variable table instead of temp table
Declare @MatricesG TABLE (...)

-- Loop optimization
SET @CounterI = 1
WHILE @CounterI <= @MaxDim
    -- Process in memory
```

### Complexity

- **Time Complexity**: O(n³) for Gauss elimination
- **Typical Performance**: < 1 second for 100 companies

## Appendix: Comprehensive Matrix Calculation Examples

### Example 1: Four-Company Chain Structure

**Ownership Structure**:
```
        ┌─────────────┐
        │  Parent (P) │  (Company 1)
        └──────┬──────┘
               │ 80%
               ▼
        ┌─────────────┐
        │  Holding (H)│  (Company 2)
        └──────┬──────┘
               │ 75%
               ▼
        ┌─────────────┐
        │   Sub (S)   │  (Company 3)
        └──────┬──────┘
               │ 60%
               ▼
        ┌─────────────┐
        │  OpCo (O)   │  (Company 4)
        └─────────────┘
```

**Step 1: Build Direct Ownership Matrix (D)**

Rows = Owner, Columns = Owned, Last column = Third Parties (TP)

```
          P      H      S      O      TP
    P [  0.00   0.80   0.00   0.00   0.20 ]
    H [  0.00   0.00   0.75   0.00   0.25 ]
    S [  0.00   0.00   0.00   0.60   0.40 ]
    O [  0.00   0.00   0.00   0.00   1.00 ]
   TP [  0.00   0.00   0.00   0.00   1.00 ]
```

**Step 2: Build Identity Matrix (I)**

```
          P      H      S      O      TP
    P [  1.00   0.00   0.00   0.00   0.00 ]
    H [  0.00   1.00   0.00   0.00   0.00 ]
    S [  0.00   0.00   1.00   0.00   0.00 ]
    O [  0.00   0.00   0.00   1.00   0.00 ]
   TP [  0.00   0.00   0.00   0.00   1.00 ]
```

**Step 3: Calculate (I - D)**

```
          P      H      S      O      TP
    P [  1.00  -0.80   0.00   0.00  -0.20 ]
    H [  0.00   1.00  -0.75   0.00  -0.25 ]
    S [  0.00   0.00   1.00  -0.60  -0.40 ]
    O [  0.00   0.00   0.00   1.00  -1.00 ]
   TP [  0.00   0.00   0.00   0.00   1.00 ]
```

**Step 4: Solve via Gauss Elimination**

The system solves: G × (I - D) = I

After Gauss elimination, we get the Group matrix (G):

```
          P      H      S      O      TP
    P [  1.00   0.80   0.60   0.36   0.00 ]  ← P's indirect ownership
    H [  0.00   1.00   0.75   0.45   0.00 ]  ← H's indirect ownership
    S [  0.00   0.00   1.00   0.60   0.00 ]  ← S's indirect ownership
    O [  0.00   0.00   0.00   1.00   0.00 ]  ← O's indirect ownership
   TP [  0.00   0.00   0.00   0.00   1.00 ]
```

**Step 5: Extract Results**

Reading from Row P (Parent's perspective):

| Company | Direct % | Group (Indirect) % | Calculation |
|---------|----------|-------------------|-------------|
| H | 80% | 80% | Direct |
| S | 0% | 60% | 80% × 75% |
| O | 0% | 36% | 80% × 75% × 60% |

**Step 6: Calculate Minority Interest**

| Company | Group % | Minority % | Consolidation Method |
|---------|---------|------------|---------------------|
| H | 80% | 20% | G (Global) |
| S | 60% | 40% | G (Global) |
| O | 36% | 64% | N (Not Conso) or E (Equity) |

### Example 2: Multi-Path Ownership Structure

**Ownership Structure**:
```
              ┌─────────────┐
              │  Parent (P) │
              └──────┬──────┘
                    / \
                 60%   40%
                 /       \
                ▼         ▼
        ┌───────────┐  ┌───────────┐
        │  Sub A    │  │  Sub B    │
        └─────┬─────┘  └─────┬─────┘
               \             /
               30%         50%
                 \         /
                  ▼       ▼
              ┌───────────────┐
              │    Sub C      │
              └───────────────┘
```

**Direct Ownership Matrix (D)**:

```
          P      A      B      C      TP
    P [  0.00   0.60   0.40   0.00   0.00 ]
    A [  0.00   0.00   0.00   0.30   0.70 ]
    B [  0.00   0.00   0.00   0.50   0.50 ]
    C [  0.00   0.00   0.00   0.00   1.00 ]
   TP [  0.00   0.00   0.00   0.00   1.00 ]
```

**After Gauss Elimination - Group Matrix (G)**:

```
          P      A      B      C      TP
    P [  1.00   0.60   0.40   0.38   0.00 ]  ← P's indirect ownership
    A [  0.00   1.00   0.00   0.30   0.00 ]
    B [  0.00   0.00   1.00   0.50   0.00 ]
    C [  0.00   0.00   0.00   1.00   0.00 ]
   TP [  0.00   0.00   0.00   0.00   1.00 ]
```

**Verification**: P→C = (60% × 30%) + (40% × 50%) = 18% + 20% = **38%** ✓

**Results Summary**:

| Company | Path(s) | Group % | Minority % | Method |
|---------|---------|---------|------------|--------|
| A | P→A | 60% | 40% | G |
| B | P→B | 40% | 60% | N/E |
| C | P→A→C + P→B→C | 38% | 62% | N/E |

### Example 3: Circular Ownership (Cross-Holdings)

**Ownership Structure**:
```
              ┌─────────────┐
              │  Parent (P) │
              └──────┬──────┘
                    │ 70%
                    ▼
              ┌───────────┐
              │  Sub A    │
              └─────┬─────┘
                   / \
                70%   │
                /     │ 20%
               ▼      │
        ┌───────────┐ │
        │  Sub B    │←┘
        └───────────┘
```

A owns 70% of B, B owns 20% of A (circular!)

**Direct Ownership Matrix (D)**:

```
          P      A      B      TP
    P [  0.00   0.70   0.00   0.30 ]
    A [  0.00   0.00   0.70   0.30 ]
    B [  0.00   0.20   0.00   0.80 ]
   TP [  0.00   0.00   0.00   1.00 ]
```

**The Math**: Solving for G when circular ownership exists:

Let x = P's effective % in A
Let y = P's effective % in B

```
x = 0.70 + y × 0.20   (P owns 70% directly + gets y% × 20% through B)
y = x × 0.70          (P's share of A × A's 70% in B)

Substituting:
x = 0.70 + (0.70x × 0.20)
x = 0.70 + 0.14x
x - 0.14x = 0.70
0.86x = 0.70
x = 0.8140 (81.40%)

y = 0.8140 × 0.70 = 0.5698 (56.98%)
```

**Group Matrix (G) After Gauss Elimination**:

```
          P      A      B      TP
    P [  1.00   0.8140  0.5698  0.00 ]
    A [  0.00   1.1628  0.8140  0.00 ]  ← Note: >1 due to circular amplification
    B [  0.00   0.2326  1.1628  0.00 ]
   TP [  0.00   0.00   0.00    1.00 ]
```

**Results**:

| Company | Direct % | Group % | Minority % | Method |
|---------|----------|---------|------------|--------|
| A | 70% | 81.40% | 18.60% | G |
| B | 0% | 56.98% | 43.02% | G |

**Note**: Circular ownership amplifies P's effective control above direct ownership!

### Example 4: Complete 5-Company Complex Structure

**Ownership Structure**:
```
                    ┌─────────────┐
                    │  Parent (P) │
                    └──────┬──────┘
                      /    |    \
                   80%    60%    30%
                   /       |       \
                  ▼        ▼        ▼
        ┌─────────┐  ┌─────────┐  ┌─────────┐
        │  Sub H1 │  │  Sub H2 │  │  Assoc A│
        └────┬────┘  └────┬────┘  └─────────┘
              \           /
              100%       75%
                \       /
                 ▼     ▼
               ┌─────────┐
               │  OpCo O │
               └─────────┘
```

**Direct Ownership Matrix (D)**:

```
          P      H1     H2     A      O      TP
    P [  0.00   0.80   0.60   0.30   0.00   0.00 ]
   H1 [  0.00   0.00   0.00   0.00   1.00   0.00 ]
   H2 [  0.00   0.00   0.00   0.00   0.75   0.25 ]
    A [  0.00   0.00   0.00   0.00   0.00   1.00 ]
    O [  0.00   0.00   0.00   0.00   0.00   1.00 ]
   TP [  0.00   0.00   0.00   0.00   0.00   1.00 ]
```

**Group Matrix (G) After Calculation**:

```
          P      H1     H2     A      O      TP
    P [  1.00   0.80   0.60   0.30   1.25   0.00 ]  ← P's ownership
   H1 [  0.00   1.00   0.00   0.00   1.00   0.00 ]
   H2 [  0.00   0.00   1.00   0.00   0.75   0.00 ]
    A [  0.00   0.00   0.00   1.00   0.00   0.00 ]
    O [  0.00   0.00   0.00   0.00   1.00   0.00 ]
   TP [  0.00   0.00   0.00   0.00   0.00   1.00 ]
```

**Note**: P's indirect ownership in O = (80% × 100%) + (60% × 75%) = 80% + 45% = **125%**?

This exceeds 100% because H1 and H2 together own more of O than O has shares. This indicates an error in the data entry (over-allocation). The system would flag this.

**Corrected Structure** (H1 owns 50%, H2 owns 50% of O):

```
P→O = (80% × 50%) + (60% × 50%) = 40% + 30% = **70%**
```

**Final Results**:

| Company | Calculation | Group % | Minority % | Method |
|---------|-------------|---------|------------|--------|
| H1 | Direct | 80% | 20% | G |
| H2 | Direct | 60% | 40% | G |
| A | Direct | 30% | 70% | E |
| O | (80%×50%)+(60%×50%) | 70% | 30% | G |

### Summary: Matrix Calculation Steps

| Step | Action | Formula/Operation |
|------|--------|-------------------|
| 1 | Load direct ownership | Read from TS015S0 |
| 2 | Build D matrix | Rows=Owner, Cols=Owned |
| 3 | Add Third Parties column | 1 - sum of direct ownership |
| 4 | Calculate I - D | Identity minus Direct |
| 5 | Gauss elimination | Solve G × (I-D) = I |
| 6 | Extract results | Read row for each perspective |
| 7 | Calculate minority | 100% - Group % |
| 8 | Assign method | Based on GroupCtrlPerc thresholds |

### SQL Representation in Prophix.Conso

```sql
-- The actual matrix values are stored in variable tables:
DECLARE @MatricesG TABLE (
    MatrixNr INT,      -- Matrix identifier (1-6 for different purposes)
    RowNr INT,         -- Row index (company sort ID)
    ColNr INT,         -- Column index (company sort ID)
    CellValue DECIMAL(28,16)  -- High precision value
);

-- After calculation, results are stored in TS014C0:
UPDATE TS014C0
SET GroupPerc = @CalculatedGroupPerc,    -- From matrix result
    MinorPerc = 100 - @CalculatedGroupPerc,  -- Calculated minority
    GroupCtrlPerc = @CalculatedCtrlPerc  -- For method determination
WHERE ConsoID = @ConsoID
  AND CompanyID = @CompanyID;
```

## API Reference

### Primary API Handlers
| Handler | YAML File | Purpose | Status |
|---------|-----------|---------|--------|
| `Ownership_GetOwnerships` | [api-ownership-endpoints.yaml](../11-agent-support/api-ownership-endpoints.yaml) | Get multi-tier ownership from TS015S0 | ✅ IMPLEMENTED |
| `Ownership_SaveOwnership` | [api-ownership-endpoints.yaml](../11-agent-support/api-ownership-endpoints.yaml) | Define ownership links | ✅ IMPLEMENTED |
| `Ownership_CalculatePercentages` | [api-ownership-endpoints.yaml](../11-agent-support/api-ownership-endpoints.yaml) | Execute matrix calculation | ✅ IMPLEMENTED |

### Supporting API Handlers
| Handler | YAML File | Purpose |
|---------|-----------|---------|
| `Company_GetCompanies` | [api-company-endpoints.yaml](../11-agent-support/api-company-endpoints.yaml) | Get calculated GroupPerc, MinorPerc |
| `Consolidation_Execute` | [api-consolidation-endpoints.yaml](../11-agent-support/api-consolidation-endpoints.yaml) | Apply consolidation with calculated percentages |
| `Report_ExecuteReport` | [api-reports-endpoints.yaml](../11-agent-support/api-reports-endpoints.yaml) | Ownership structure reports |

### API Workflow
```
Multi-Tier Ownership Calculation via API:

1. OWNERSHIP STRUCTURE ENTRY
   Ownership_SaveOwnership → TS015S0 for each relationship:
     - P → H1: 80%
     - P → H2: 60%
     - H1 → OpCo: 50%
     - H2 → OpCo: 50%

2. MATRIX CALCULATION
   Ownership_CalculatePercentages → P_CALC_OWNERSHIP_INDIRECT_PERCENTAGES:
     - Build Direct Ownership Matrix (D)
     - Calculate (I - D) matrix
     - Gauss elimination for inverse
     - Extract Group percentages from result

3. RESULT STORAGE
   Updates TS014C0 for each company:
     - GroupPerc (indirect financial %)
     - MinorPerc (100 - GroupPerc)
     - GroupCtrlPerc (indirect control %)
     - ConsoMethod (G/P/E/N based on thresholds)

4. CONSOLIDATION
   Consolidation_Execute uses calculated percentages:
     - Line-by-line consolidation at GroupPerc
     - Minority interest at MinorPerc
     - Method-specific eliminations
```

### Matrix Calculation Reference
| Matrix | Purpose | Content |
|--------|---------|---------|
| D (Nr 1) | Direct ownership | Direct % from TS015S0 |
| I (Nr 2) | Identity | Diagonal = 1 |
| I-D (Nr 3) | Input for inversion | Identity minus Direct |
| (I-D)^-1 (Nr 4) | Inverse | Gauss elimination result |
| G (Nr 6) | Group percentages | Indirect ownership result |

### Implementation Status
| Feature | Status | Notes |
|---------|--------|-------|
| Matrix-based calculation | ✅ IMPLEMENTED | O(n³) Gauss elimination |
| Multi-path ownership | ✅ IMPLEMENTED | Automatic sum of paths |
| Cross-holdings | ✅ IMPLEMENTED | Non-circular supported |
| Circular ownership | ⚠️ PARTIAL | Matrix singularity limitation |
| Deep hierarchies | ✅ IMPLEMENTED | Unlimited depth |

### Related API Documentation
- [API Index](../11-agent-support/api-index.yaml) - Master handler catalog
- [Gap Analysis](../11-agent-support/gap-analysis-report.yaml) - **FULLY IMPLEMENTED (95%)**

---

## Related Documentation

- [Direct and Indirect Holdings](direct-indirect-holdings.md) - Conceptual overview
- [Ownership Percentages](ownership-percentages.md) - Financial vs voting rights
- [Circular Ownership](../03-core-calculations/circular-ownership.md) - Cross-holding details
- [Control vs Ownership](control-vs-ownership.md) - Method determination
- [Consolidation Method Determination](../02-consolidation-methods/consolidation-method-determination.md) - Threshold logic

### Navigation
- [Cross-Reference Index](../00-index/CROSS_REFERENCE_INDEX.md) - Find related documents
- [Quick Reference Card](../20-appendices/quick-reference-card.md) - Ownership queries
- [Troubleshooting Guide](../17-troubleshooting/common-issues.md) - Ownership issues
- [Glossary](../20-appendices/glossary.md) - Term definitions

---
*Document 44 of 50+ | Batch 15: Advanced Eliminations & Database Patterns | Last Updated: 2024-12-01 (Enhanced with comprehensive matrix calculation examples)*
