# Voting Rights Analysis: Control Percentage Calculation

## Document Metadata
- **Category**: Ownership Structure
- **Theory Source**: Knowledge base chunks: 0044, 0066, 0067, 0083, 0084, 0085
- **Implementation Files**:
  - `Sigma.Database/dbo/Tables/TS015S0.sql` - NbrVotingRights, CtrlPercentage
  - `Sigma.Database/dbo/Tables/TS014C0.sql` - NbrVotingRightsIssued, GroupCtrlPerc
  - `Sigma.Database/dbo/Stored Procedures/P_CALC_OWNERSHIP_DIRECT_PERCENTAGES.sql` - Direct control calculation
  - `Sigma.Database/dbo/Stored Procedures/P_CALC_OWNERSHIP_INDIRECT_PERCENTAGES.sql` - Indirect control calculation
- **Last Updated**: 2024-12-01
- **Completeness**: 90% (Voting rights tracked separately; potential voting rights not implemented)
- **Compliance Status**: IFRS 10 - Compliant for actual voting rights

## Executive Summary

Voting rights analysis determines the control percentage used for consolidation method determination. Unlike financial percentage (used for profit allocation), control percentage is based on voting power and determines whether an entity exercises control, joint control, or significant influence. Prophix.Conso implements **separate tracking of financial rights and voting rights** in TS015S0, allowing for different ownership and control percentages when share classes have different voting characteristics.

## Theoretical Framework

### IFRS 10 Control Concept

From Allen White's "Direct Consolidation" (Chunk 44):

> "We first need to know the control percentage owned by the group in each individual company, which is the basic information to determine the consolidation method."

### Control vs Financial Percentage

| Aspect | Control Percentage | Financial Percentage |
|--------|-------------------|---------------------|
| **Basis** | Voting rights | Financial/dividend rights |
| **Purpose** | Method determination | Profit/equity allocation |
| **IFRS Reference** | IFRS 10 (control) | Ownership interest |
| **Typical Divergence** | Dual-class shares | Preference shares |

### Voting Rights Types

1. **Actual Voting Rights**: Currently exercisable votes
2. **Potential Voting Rights**: Convertible instruments, options (IAS 28)
3. **De Facto Control**: <50% but control through dispersed ownership
4. **Contractual Control**: Board appointments, veto rights

### Control Assessment Framework

```
Control Percentage = Voting Rights Owned / Total Voting Rights Issued

Where:
- Voting Rights Owned = Direct + Indirect holdings
- Total Voting Rights = All issued shares with voting rights
- Treasury shares may be excluded from denominator
```

## Current Implementation

### Voting Rights Data Structure

**TS015S0 - Ownership Records**

```sql
CREATE TABLE [dbo].[TS015S0] (
    [ControlID]       INT IDENTITY NOT NULL,
    [ConsoID]         INT NOT NULL,
    [CompanyID]       INT NOT NULL,      -- Owner company
    [CompanyOwnedID]  INT NOT NULL,      -- Owned company
    [FinPercentage]   DECIMAL(9,6),      -- Financial % (derived)
    [CtrlPercentage]  DECIMAL(9,6),      -- Control/Voting % (derived)
    [NbrFinRights]    BIGINT NOT NULL,   -- Number of financial shares owned
    [NbrVotingRights] BIGINT NOT NULL    -- Number of voting rights owned
);
```

**TS014C0 - Company-Level Totals**

```sql
CREATE TABLE [dbo].[TS014C0] (
    -- ... other columns ...
    [GroupPerc]              DECIMAL(24,6),  -- Group financial %
    [MinorPerc]              DECIMAL(24,6),  -- Minority financial %
    [GroupCtrlPerc]          DECIMAL(24,6),  -- Group control %
    [NbrFinRightsIssued]     BIGINT,         -- Total financial shares issued
    [NbrVotingRightsIssued]  BIGINT,         -- Total voting rights issued
    -- ... other columns ...
);
```

### Direct Percentage Calculation

`P_CALC_OWNERSHIP_DIRECT_PERCENTAGES.sql`:

```sql
-- Calculate control percentage from voting rights
UPDATE TS015S0
SET CtrlPercentage =
    CASE
        WHEN b.NbrVotingRightsIssued = 0 THEN 0
        ELSE CAST(a.NbrVotingRights AS FLOAT) /
             CAST(b.NbrVotingRightsIssued AS FLOAT) * 100
    END
FROM TS015S0 a
INNER JOIN TS014C0 b
    ON b.ConsoID = a.ConsoID AND b.CompanyID = a.CompanyOwnedID
WHERE a.ConsoID = @ConsoID;

-- Calculate financial percentage from financial rights
UPDATE TS015S0
SET FinPercentage =
    CASE
        WHEN b.NbrFinRightsIssued = 0 THEN 0
        ELSE CAST(a.NbrFinRights AS FLOAT) /
             CAST(b.NbrFinRightsIssued AS FLOAT) * 100
    END
FROM TS015S0 a
INNER JOIN TS014C0 b
    ON b.ConsoID = a.ConsoID AND b.CompanyID = a.CompanyOwnedID
WHERE a.ConsoID = @ConsoID;
```

### Indirect Control Calculation

`P_CALC_OWNERSHIP_INDIRECT_PERCENTAGES.sql` calculates indirect control through subsidiaries:

```sql
-- Control percentage propagation through group
-- Uses iterative approach for control chain

WHILE @CounterI <= @MaxLoop
BEGIN
    UPDATE #GroupControl
    SET OldCtrl = NewCtrl

    UPDATE #GroupControl
    SET NewCtrl = SumTS015.CtrlSubTotal
    FROM #GroupControl a
    JOIN (
        SELECT a.CompanyOwnedID,
               SUM(CAST(a.NbrVotingRights AS FLOAT) /
                   CAST(b.NbrVotingRightsIssued AS FLOAT) * 100) AS CtrlSubTotal
        FROM #OwnerShip a
        INNER JOIN #Companies b ON (b.CompanyID = a.CompanyOwnedID)
        WHERE a.CompanyID IN (
            -- Only count control through controlled entities
            SELECT CompanyID FROM #GroupControl WHERE NewCtrl > 50
        )
        GROUP BY a.CompanyOwnedID
    ) SumTS015 ON SumTS015.CompanyOwnedID = a.CompanyID

    -- Exit when no changes
    IF (SELECT COUNT(*) FROM #GroupControl WHERE OldCtrl <> NewCtrl) = 0
        SET @CounterI = @MaxLoop + 1

    SET @CounterI = @CounterI + 1
END
```

### Control vs Financial Divergence Example

```
Company B Share Structure:
- Class A: 1,000 shares, 10 votes each = 10,000 votes
- Class B: 4,000 shares, 1 vote each = 4,000 votes
- Total: 5,000 shares, 14,000 votes

Parent owns:
- 500 Class A shares (5,000 votes)
- 500 Class B shares (500 votes)
- Total: 1,000 shares (5,500 votes)

TS015S0 Record:
  NbrFinRights = 1,000
  NbrVotingRights = 5,500

TS014C0:
  NbrFinRightsIssued = 5,000
  NbrVotingRightsIssued = 14,000

Calculated Percentages:
  FinPercentage = 1,000 / 5,000 = 20%
  CtrlPercentage = 5,500 / 14,000 = 39.3%

Consolidation Method:
  Based on 39.3% control = Equity Method (E)
  Financial allocation = 20%
```

## Control Calculation Scenarios

### Scenario 1: Equal Voting and Financial Rights

```
Standard shares: 1 share = 1 vote = 1 financial right

Parent owns 60%:
  NbrFinRights = 60
  NbrVotingRights = 60
  NbrFinRightsIssued = 100
  NbrVotingRightsIssued = 100

Result:
  FinPercentage = 60%
  CtrlPercentage = 60%
  ConsoMethod = 'G' (Global Integration)
```

### Scenario 2: Non-Voting Preference Shares

```
Company has:
- 100 ordinary shares (voting)
- 100 preference shares (non-voting, dividend priority)

Parent owns:
- 60 ordinary shares
- 40 preference shares

TS015S0:
  NbrFinRights = 100 (60+40)
  NbrVotingRights = 60

TS014C0:
  NbrFinRightsIssued = 200
  NbrVotingRightsIssued = 100

Result:
  FinPercentage = 100/200 = 50%
  CtrlPercentage = 60/100 = 60%
  ConsoMethod = 'G' (based on 60% control)
```

### Scenario 3: Indirect Control Chain

```
P owns 80% of A (control)
A owns 40% of B (significant influence only)

Group control in B:
- Through A: 80% × 40% = 32% (but A doesn't control B)
- Actually: 0% effective control (A only has influence)

Result:
  B's ConsoMethod determined by its OWN control % (40%)
  B = Equity Method (E)
```

## Validation and Constraints

### TS014C0 Constraints

```sql
-- Voting rights must be positive for consolidated companies
CONSTRAINT [CK_TS014C0_NBRVOTINGRIGHTSISSUED]
CHECK ([ConsolidatedCompany]=(0) OR ISNULL([NbrVotingRightsIssued],(0))>=(1))

-- Financial rights must be positive for consolidated companies
CONSTRAINT [CK_TS014C0_NBRFINRIGHTSISSUED]
CHECK ([ConsolidatedCompany]=(0) OR ISNULL([NbrFinRightsIssued],(0))>=(1))
```

### Ownership Validation

```sql
-- From P_CALC_OWNERSHIP_INDIRECT_PERCENTAGES:
-- Check that owned shares don't exceed issued shares
IF EXISTS (
    SELECT 1
    FROM TS015S0 a
    INNER JOIN TS014C0 b
        ON b.ConsoID = a.ConsoID AND b.CompanyID = a.CompanyOwnedID
    WHERE a.ConsoID = @ConsoID
      AND a.NbrVotingRights > b.NbrVotingRightsIssued
)
BEGIN
    -- Error: Shares owned exceed shares issued
    SET @errorinfo = dbo.AddError0('SHARES_EXCEED_ISSUED', @errorinfo)
END
```

## Gap Analysis

### Implemented Features

| Feature | Implementation | Status |
|---------|----------------|--------|
| Separate voting/financial tracking | TS015S0 columns | **Full** |
| Direct control calculation | P_CALC_OWNERSHIP_DIRECT_PERCENTAGES | **Full** |
| Indirect control propagation | P_CALC_OWNERSHIP_INDIRECT_PERCENTAGES | **Full** |
| Control-based method determination | Threshold rules | **Full** |
| Circular control handling | Matrix algebra | **Full** |

### Not Implemented

| Feature | Gap | Severity |
|---------|-----|----------|
| Potential voting rights | IAS 28 consideration | 6 |
| De facto control assessment | IFRS 10.B42 | 7 |
| Veto rights tracking | Protective vs substantive | 5 |
| Board representation | Contractual control | 5 |

### Potential Voting Rights Gap

IFRS 10 and IAS 28 require consideration of:
- Convertible instruments
- Share options/warrants
- Contingent rights

**Current Limitation**: System only tracks actual voting rights, not potential.

## API Reference

### Primary API Handlers
| Handler | YAML File | Purpose | Status |
|---------|-----------|---------|--------|
| `Ownership_GetOwnerships` | [api-ownership-endpoints.yaml](../11-agent-support/api-ownership-endpoints.yaml) | Get NbrVotingRights, CtrlPercentage | ✅ IMPLEMENTED |
| `Ownership_SaveOwnership` | [api-ownership-endpoints.yaml](../11-agent-support/api-ownership-endpoints.yaml) | Update voting rights | ✅ IMPLEMENTED |
| `Ownership_CalculatePercentages` | [api-ownership-endpoints.yaml](../11-agent-support/api-ownership-endpoints.yaml) | Calculate CtrlPercentage | ✅ IMPLEMENTED |

### Supporting API Handlers
| Handler | YAML File | Purpose |
|---------|-----------|---------|
| `Company_GetCompanies` | [api-company-endpoints.yaml](../11-agent-support/api-company-endpoints.yaml) | Get NbrVotingRightsIssued, GroupCtrlPerc |
| `Company_SaveCompany` | [api-company-endpoints.yaml](../11-agent-support/api-company-endpoints.yaml) | Update total voting rights issued |

### Voting Rights Data Flow
```
Voting Rights Analysis via API:

1. COMPANY SETUP
   Company_SaveCompany → TS014C0:
     - NbrVotingRightsIssued (total voting rights)
     - NbrFinRightsIssued (total financial rights)

2. OWNERSHIP ENTRY
   Ownership_SaveOwnership → TS015S0:
     - NbrVotingRights (voting rights held)
     - NbrFinRights (financial rights held)

3. DIRECT PERCENTAGE CALCULATION
   Ownership_CalculatePercentages → P_CALC_OWNERSHIP_DIRECT_PERCENTAGES:
     - CtrlPercentage = NbrVotingRights / NbrVotingRightsIssued * 100
     - FinPercentage = NbrFinRights / NbrFinRightsIssued * 100

4. INDIRECT CONTROL CALCULATION
   → P_CALC_OWNERSHIP_INDIRECT_PERCENTAGES:
     - Iterative propagation through controlled entities
     - GroupCtrlPerc stored in TS014C0
```

### Implementation Status
| Feature | Status | Notes |
|---------|--------|-------|
| Separate voting/financial tracking | ✅ IMPLEMENTED | TS015S0 columns |
| Direct control calculation | ✅ IMPLEMENTED | P_CALC_OWNERSHIP_DIRECT_PERCENTAGES |
| Indirect control propagation | ✅ IMPLEMENTED | Iterative algorithm |
| Potential voting rights | ❌ NOT_IMPLEMENTED | IAS 28 gap |
| De facto control | ❌ NOT_IMPLEMENTED | IFRS 10.B42 gap |

### Related API Documentation
- [API Index](../11-agent-support/api-index.yaml) - Master handler catalog
- [Gap Analysis](../11-agent-support/gap-analysis-report.yaml) - **IMPLEMENTED (90%)**

---

## Related Documentation

- [Ownership Percentages](ownership-percentages.md) - Financial percentage details
- [Control vs Ownership](control-vs-ownership.md) - Control assessment principles
- [Direct and Indirect Holdings](direct-indirect-holdings.md) - Ownership chains
- [Consolidation Method Determination](../02-consolidation-methods/consolidation-method-determination.md) - Method selection
- [Preference Shares](../03-core-calculations/preference-shares.md) - Multi-class considerations

### Related Knowledge Chunks
- Chunk 0044: Control and financial percentages
- Chunk 0066: Percentage calculation principles
- Chunk 0067: Group percentage determination
- Chunk 0083-0085: Treasury shares and voting
- Chunk 0084: Control assessment factors

---
*Document 32 of 50+ | Batch 11: Control Determination & Data Architecture | Last Updated: 2024-12-01*
