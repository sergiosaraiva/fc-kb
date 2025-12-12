# Ownership Percentages: Financial, Voting, and Control

## Document Metadata
- **Category**: Ownership Structure
- **Theory Source**: Knowledge base chunks: 0027, 0050, 0066, 0067, 0083, 0084, 0085, 0087
- **Implementation Files**:
  - `Sigma.Database/dbo/Tables/TS014C0.sql` (Company - GroupPerc, MinorPerc, GroupCtrlPerc)
  - `Sigma.Database/dbo/Tables/TS015S0.sql` (Ownership - FinPercentage, CtrlPercentage)
  - `Sigma.Database/dbo/Stored Procedures/P_CALC_OWNERSHIP_DIRECT_PERCENTAGES.sql`
  - `Sigma.Database/dbo/Stored Procedures/P_CALC_OWNERSHIP_INDIRECT_PERCENTAGES.sql`
- **Last Updated**: 2024-12-01
- **Completeness**: 95% (Financial and voting rights fully implemented)
- **Compliance Status**: IFRS 10 - Different Types of Ownership Rights

## Executive Summary

Prophix.Conso distinguishes between two fundamental types of ownership rights: Financial Rights (economic interest in dividends and net assets) and Voting Rights (control over entity decisions). These are tracked separately at both the direct (TS015S0) and indirect (TS014C0) levels, enabling proper consolidation method determination and minority interest calculation even when financial and voting percentages differ.

## Theoretical Framework

### Concept Definition

From Allen White's "Direct Consolidation" (Chunk 83):

> "To determine the percentage of control, these shares must be subtracted from the total of shares of the company."

### Types of Ownership Percentages

| Type | Description | Used For |
|------|-------------|----------|
| **Financial Percentage** | Economic interest (dividends, net assets) | Minority interest calculation |
| **Voting/Control Percentage** | Voting power over decisions | Consolidation method determination |
| **Group Percentage** | Indirect financial ownership from parent | Earnings allocation |
| **Minority Percentage** | Non-controlling interest | External stakeholder share |

### Key Principles

1. **Financial ≠ Voting**: A company can have different financial and voting rights
2. **Control Determines Method**: Voting percentage determines consolidation method (G/P/E/N)
3. **Financial Determines Allocation**: Financial percentage determines profit/equity split
4. **Indirect Calculation**: Both types must be calculated through ownership chains

### Scenarios Where Financial ≠ Voting

1. **Preference Shares**: Non-voting shares with enhanced dividend rights
2. **Dual-Class Shares**: Different voting weights per share class
3. **Treasury Shares** (Chunk 83-85): Company holds own shares (excluded from voting)
4. **Voting Agreements**: Contractual arrangements affecting control
5. **Convertible Securities**: Potential voting rights

### Example

**Treasury Shares Scenario** (Chunks 83-85):
```
Company A owns 60% of Company B
Company B owns 5% of its own shares (treasury)

Calculation:
- Available voting rights: 100% - 5% = 95%
- A's effective control: 60% / 95% = 63.16% (control)
- A's financial interest: 60% (unchanged for dividends)

Result:
- CtrlPercentage: 63.16% (A controls B)
- FinPercentage: 60% (A's economic interest)
```

**Dual-Class Shares**:
```
Company A has:
- 1,000 Class A shares (10 votes each)
- 9,000 Class B shares (1 vote each)

Shareholder X owns:
- 500 Class A shares
- 2,000 Class B shares

Financial Interest: 2,500 / 10,000 = 25%
Voting Power: (500×10 + 2,000×1) / (1,000×10 + 9,000×1) = 7,000 / 19,000 = 36.84%
```

## Current Implementation

### Database Schema

#### Direct Ownership (TS015S0)

```sql
CREATE TABLE [dbo].[TS015S0] (
    [ControlID]       INT            IDENTITY NOT NULL,
    [ConsoID]         INT            NOT NULL,
    [CompanyID]       INT            NOT NULL,      -- Shareholder
    [CompanyOwnedID]  INT            NOT NULL,      -- Owned company

    -- Financial Rights (economic interest)
    [FinPercentage]   DECIMAL(9,6)   DEFAULT((0)),  -- Calculated %
    [NbrFinRights]    BIGINT         DEFAULT((0)),  -- Number of rights held

    -- Voting Rights (control)
    [CtrlPercentage]  DECIMAL(9,6)   DEFAULT((0)),  -- Calculated %
    [NbrVotingRights] BIGINT         DEFAULT((0)),  -- Number of votes held
);
```

#### Company Structure (TS014C0)

```sql
CREATE TABLE [dbo].[TS014C0] (
    [CompanyID]              INT            NOT NULL,
    [ConsoID]                INT            NOT NULL,

    -- Issued Rights (denominator for percentage calculations)
    [NbrFinRightsIssued]     BIGINT         DEFAULT((0)),  -- Total financial rights
    [NbrVotingRightsIssued]  BIGINT         DEFAULT((0)),  -- Total voting rights

    -- Calculated Indirect Percentages
    [GroupPerc]              DECIMAL(9,6)   DEFAULT((0)),  -- Indirect financial %
    [MinorPerc]              DECIMAL(9,6)   DEFAULT((0)),  -- Third-party %
    [GroupCtrlPerc]          DECIMAL(9,6)   DEFAULT((0)),  -- Indirect control %

    -- Derived Consolidation Method
    [ConsoMethod]            CHAR(1)        DEFAULT('G'),  -- G/P/E/N
);
```

### Percentage Calculation Logic

#### Direct Percentage Calculation

From `P_CALC_OWNERSHIP_DIRECT_PERCENTAGES.sql`:

```sql
-- Financial Percentage
if @NbrFinRightsIssued = 0
    set @FinPercentage = null  -- Cannot divide by zero
else if (@NbrFinRights / @NbrFinRightsIssued >= 10)
begin
    set @FinPercentage = 0     -- Overflow protection
    select @errorinfo = dbo.AddWarning2('INVALID_FIN_PERCENTAGE', @CompanyName, @CompanyOwnedName, @errorinfo)
end
else
    set @FinPercentage = 100 * (cast(@NbrFinRights as float) / @NbrFinRightsIssued)

-- Control Percentage (same logic, different fields)
if @NbrVotingRightsIssued = 0
    set @CtrlPercentage = null
else if (@NbrVotingRights / @NbrVotingRightsIssued >= 10)
begin
    set @CtrlPercentage = 0
    select @errorinfo = dbo.AddWarning2('INVALID_CTRL_PERCENTAGE', @CompanyName, @CompanyOwnedName, @errorinfo)
end
else
    set @CtrlPercentage = 100 * (cast(@NbrVotingRights as float) / @NbrVotingRightsIssued)
```

#### Indirect Percentage Calculation

From `P_CALC_OWNERSHIP_INDIRECT_PERCENTAGES.sql`:

**Control Percentage Propagation**:
```sql
-- Control propagates only through controlled entities (>50%)
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
        SELECT CompanyID from #GroupControl where NewCtrl > 50
    )
    GROUP BY a.CompanyOwnedID
) SumTS015 ON SumTS015.CompanyOwnedID = a.CompanyID
```

**Financial Percentage (Matrix Method)**:
```sql
-- Uses FinPercentage in ownership matrix
Update #Matrices
Set val = c.FinPercentage / 100  -- Note: Uses FinPercentage, not CtrlPercentage
From #Matrices
    inner join #Companies a On (a.SortID = #Matrices.Row)
    inner join #Companies b On (b.SortID = #Matrices.Col)
    inner join #OwnerShip c on (c.CompanyID = a.CompanyID
                               and c.CompanyOwnedID = b.CompanyID)
```

### Validation Checks

```sql
-- Warn if financial percentage exceeds 100%
if @FinPercentage > 100
    select @errorinfo = dbo.AddWarning2('INVALID_FIN_PERCENTAGE',
                                        @CompanyName, @CompanyOwnedName, @errorinfo)

-- Warn if control percentage exceeds 100%
if @CtrlPercentage > 100
    select @errorinfo = dbo.AddWarning2('INVALID_CTRL_PERCENTAGE',
                                        @CompanyName, @CompanyOwnedName, @errorinfo)

-- Validate shares owned don't exceed shares issued
Select Top 1 @CompanyCodeWithError = 'Invalid Nbr of Shares owned in Company ' + b.CompanyCode
From #OwnerShip a
    Inner Join #Companies b on (b.CompanyID = a.CompanyOwnedID)
where b.NbrFinRightsIssued < a.NbrFinRights
   or b.NbrVotingRightsIssued < a.NbrVotingRights
```

### Usage in Consolidation

**Method Determination** (based on control percentage):
```sql
Update #Companies
Set ConsoMethod =
    Case
        When (GroupCtrlPerc > 50 OR CompanyID = @ParentID) then 'G'  -- Global Integration
        When (GroupCtrlPerc = 50) then 'P'                          -- Proportional
        When (GroupCtrlPerc >= 20 AND GroupCtrlPerc < 50) then 'E'  -- Equity Method
        When (GroupCtrlPerc < 20) then 'N'                          -- Not Consolidated
        Else 'N'
    End
```

**Minority Interest** (based on financial percentage):
```sql
-- For global integration: minority = 100% - group financial %
Update #Companies
Set MinorPerc = ROUND(100 - GroupPerc, 16)  -- Uses GroupPerc (financial), not GroupCtrlPerc
Where ConsoMethod in ('G', 'N')
      and CompanyID <> @ParentID
```

### Rights Tracking Approach

The system uses share counts rather than percentages as the primary input:

| Field | Table | Description |
|-------|-------|-------------|
| `NbrFinRights` | TS015S0 | Financial rights held by shareholder |
| `NbrVotingRights` | TS015S0 | Voting rights held by shareholder |
| `NbrFinRightsIssued` | TS014C0 | Total financial rights issued by company |
| `NbrVotingRightsIssued` | TS014C0 | Total voting rights issued by company |

**Benefits of Share-Count Approach**:
1. Handles complex capital structures (multiple share classes)
2. Enables recalculation when capital changes
3. Supports audit trail of share movements
4. Accommodates fractional ownership without precision loss

## Theory vs Practice Analysis

| Aspect | Theory (Allen White/IFRS 10) | Prophix.Conso Implementation | Alignment |
|--------|------------------------------|------------------------------|-----------|
| Financial vs Voting Separation | Required for complex structures | Separate FinPercentage/CtrlPercentage | Full |
| Control-Based Method | >50% voting = control | GroupCtrlPerc thresholds | Full |
| Financial-Based Allocation | Economic interest for NCI | GroupPerc for MinorPerc calculation | Full |
| Treasury Shares | Exclude from voting | Manual adjustment to NbrVotingRightsIssued | Partial |
| Preference Shares | Different rights per class | Supported via NbrFinRights ≠ NbrVotingRights | Full |
| Potential Voting Rights | Consider convertibles | Not automated | Gap |

## Gap Analysis

### Missing Elements

1. **Treasury Share Automation**: No automatic detection/exclusion of treasury shares from voting calculations
2. **Potential Voting Rights**: No consideration of convertible securities, options, warrants
3. **Preference Share Classification**: No explicit tracking of share class types

### Divergent Implementation

1. **Percentage Precision**: Direct percentages stored as DECIMAL(9,6), indirect as DECIMAL(9,6) - may cause precision loss

### Additional Features (Beyond Theory)

1. **Share-Count Based**: Primary input is share counts, not percentages
2. **Dual Method Support**: `CALC_NO_PROPORTIONAL` config to disable proportional method
3. **Validation Warnings**: Automatic detection of invalid percentage scenarios

## Business Impact

1. **Accurate Consolidation Method**: Separate voting percentage ensures correct method selection
2. **Fair NCI Calculation**: Financial percentage ensures fair profit/equity allocation
3. **Complex Structure Support**: Handles multi-class capital structures
4. **Audit Compliance**: Share-count tracking provides detailed audit trail

## Recommendations

1. **Add Treasury Share Detection**: Automatically identify and exclude treasury shares from voting calculations
2. **Implement Share Class Tracking**: Add share class dimension for detailed capital structure modeling
3. **Consider Potential Rights**: Add option to include/exclude potential voting rights per IFRS 10

## API Reference

### Primary API Handlers
| Handler | YAML File | Purpose | Status |
|---------|-----------|---------|--------|
| `Ownership_GetOwnerships` | [api-ownership-endpoints.yaml](../11-agent-support/api-ownership-endpoints.yaml) | Get FinPercentage, CtrlPercentage from TS015S0 | ✅ IMPLEMENTED |
| `Ownership_SaveOwnership` | [api-ownership-endpoints.yaml](../11-agent-support/api-ownership-endpoints.yaml) | Update NbrFinRights, NbrVotingRights | ✅ IMPLEMENTED |
| `Ownership_CalculatePercentages` | [api-ownership-endpoints.yaml](../11-agent-support/api-ownership-endpoints.yaml) | Execute P_CALC_OWNERSHIP_* procedures | ✅ IMPLEMENTED |

### Supporting API Handlers
| Handler | YAML File | Purpose |
|---------|-----------|---------|
| `Company_GetCompanies` | [api-company-endpoints.yaml](../11-agent-support/api-company-endpoints.yaml) | Get GroupPerc, MinorPerc, GroupCtrlPerc |
| `Company_SaveCompany` | [api-company-endpoints.yaml](../11-agent-support/api-company-endpoints.yaml) | Update NbrFinRightsIssued, NbrVotingRightsIssued |

### Percentage Type Reference
| Type | Source Table | Field | Purpose |
|------|--------------|-------|---------|
| Direct Financial % | TS015S0 | FinPercentage | Direct ownership share |
| Direct Control % | TS015S0 | CtrlPercentage | Direct voting power |
| Indirect Financial % | TS014C0 | GroupPerc | Group ownership through chain |
| Indirect Control % | TS014C0 | GroupCtrlPerc | Group voting power for method |
| Minority % | TS014C0 | MinorPerc | Non-controlling interest (100% - GroupPerc) |

### API Workflow
```
Ownership Percentage Management via API:

1. COMPANY CONFIGURATION
   Company_SaveCompany → TS014C0:
     - NbrFinRightsIssued (total financial shares)
     - NbrVotingRightsIssued (total voting rights)

2. OWNERSHIP ENTRY
   Ownership_SaveOwnership → TS015S0:
     - CompanyID, CompanyOwnedID (relationship)
     - NbrFinRights, NbrVotingRights (share counts)

3. PERCENTAGE CALCULATION
   Ownership_CalculatePercentages:
     - P_CALC_OWNERSHIP_DIRECT_PERCENTAGES:
       * FinPercentage = NbrFinRights / NbrFinRightsIssued × 100
       * CtrlPercentage = NbrVotingRights / NbrVotingRightsIssued × 100
     - P_CALC_OWNERSHIP_INDIRECT_PERCENTAGES:
       * Matrix-based calculation for GroupPerc
       * Control propagation for GroupCtrlPerc
       * MinorPerc = 100 - GroupPerc

4. CONSOLIDATION USE
   Consolidation_Execute uses:
     - GroupCtrlPerc → Consolidation method (G/P/E/N)
     - GroupPerc → Profit/equity allocation
     - MinorPerc → Minority interest calculation
```

### Implementation Status
| Feature | Status | Notes |
|---------|--------|-------|
| Financial percentage tracking | ✅ IMPLEMENTED | FinPercentage column |
| Voting percentage tracking | ✅ IMPLEMENTED | CtrlPercentage column |
| Share-count based input | ✅ IMPLEMENTED | NbrFinRights/NbrVotingRights |
| Indirect calculation | ✅ IMPLEMENTED | Matrix algebra |
| Treasury share automation | ❌ NOT_IMPLEMENTED | Manual adjustment required |

### Related API Documentation
- [API Index](../11-agent-support/api-index.yaml) - Master handler catalog
- [Gap Analysis](../11-agent-support/gap-analysis-report.yaml) - **FULLY IMPLEMENTED (95%)**

---

## Related Documentation

- [Direct and Indirect Holdings](direct-indirect-holdings.md) - Calculation mechanics
- [Control vs Ownership](control-vs-ownership.md) - Control determination rules
- [Minority Interest](../03-core-calculations/minority-interest.md) - NCI calculation

### Related Knowledge Chunks
- Chunk 0027: Percentage determination requirements
- Chunk 0066-0067: Minority interest percentages
- Chunk 0083-0085: Treasury shares and ownership structure

### Navigation
- [Cross-Reference Index](../00-index/CROSS_REFERENCE_INDEX.md) - Find related documents
- [Quick Reference Card](../20-appendices/quick-reference-card.md) - Ownership queries
- [Troubleshooting Guide](../17-troubleshooting/common-issues.md) - Ownership issues
- [Glossary](../20-appendices/glossary.md) - Term definitions

---
*Document 14 of 50+ | Batch 5: Ownership Structure | Last Updated: 2024-12-01*
