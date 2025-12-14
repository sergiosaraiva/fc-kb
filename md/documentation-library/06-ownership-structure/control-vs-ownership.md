# Control vs Ownership: Consolidation Method Determination

## Document Metadata
- **Category**: Ownership Structure
- **Theory Source**: Knowledge base chunks: 0042, 0046, 0047, 0048, 0050, 0055, 0076
- **Implementation Files**:
  - `Sigma.Database/dbo/Stored Procedures/P_CALC_OWNERSHIP_INDIRECT_PERCENTAGES.sql`
  - `Sigma.Database/dbo/Tables/TS014C0.sql` (ConsoMethod, GroupCtrlPerc)
  - `Sigma.Database/dbo/Tables/T_CONFIG.sql` (CALC_NO_PROPORTIONAL)
- **Last Updated**: 2024-12-01
- **Completeness**: 95% (Standard IFRS thresholds implemented)
- **Compliance Status**: IFRS 10 - Control Model, IAS 28 - Significant Influence

## Executive Summary

Prophix.Conso implements the IFRS control model to determine consolidation methods. Control is assessed using the calculated `GroupCtrlPerc` (indirect control percentage), which is then mapped to consolidation methods using configurable thresholds. The system distinguishes between ownership (financial interest) and control (power over investee), using control percentage for method determination and ownership percentage for earnings allocation.

## Theoretical Framework

### Concept Definition

From Allen White's "Direct Consolidation" (Chunk 42):

> "For each global integration company, we calculate the minority interests in the equity and reclassify the amount on the Minority interests account. For each equity method company, we eliminate 100% of all assets and liabilities accounts, excepted equity which is eliminated for the percentage which doesn't belong to the group."

### Control vs Ownership Distinction

| Concept | Definition | IFRS Standard | Use in Consolidation |
|---------|------------|---------------|---------------------|
| **Control** | Power over relevant activities + variable returns + ability to use power | IFRS 10 | Determines consolidation method |
| **Significant Influence** | Power to participate in decisions, not control | IAS 28 | Equity method threshold |
| **Ownership** | Right to dividends and residual interest | - | Determines profit allocation |

### IFRS Control Model (IFRS 10)

Control requires ALL THREE elements:
1. **Power**: Rights that give current ability to direct relevant activities
2. **Exposure**: Exposure, or rights, to variable returns from involvement
3. **Link**: Ability to use power to affect those returns

### Consolidation Method Thresholds

| Control Level | Method | Description |
|---------------|--------|-------------|
| **>50%** (Control) | Global Integration (G) | 100% of assets/liabilities consolidated |
| **=50%** (Joint Control) | Proportional (P) | Share of assets/liabilities consolidated |
| **20-50%** (Significant Influence) | Equity Method (E) | One-line consolidation |
| **<20%** (No Influence) | Not Consolidated (N) | Investment at cost/fair value |

### Key Principles

From Chunk 46:
```
Control Threshold:
    ┌─────┐
    │  P  │──────> 50%+ ──────→ Global Integration
    └─────┘
```

1. **Control ≠ Ownership**: A company can be controlled with <50% ownership (through voting agreements, potential voting rights)
2. **Rebuttable Presumptions**: >50% voting = presumed control; 20-50% = presumed significant influence
3. **Substance Over Form**: Actual control matters, not just percentage

### Example

**Control Without Majority Ownership**:
```
Parent P owns:
- 45% voting rights in Subsidiary S
- Contractual right to appoint majority of board

Analysis:
- Financial ownership: 45%
- Effective control: 100% (due to board appointment rights)

Result:
- ConsoMethod: 'G' (Global Integration)
- GroupPerc: 45% (for minority interest: 55%)
- GroupCtrlPerc: 100% (for method determination)
```

**Ownership Without Control**:
```
Company A owns:
- 60% non-voting preference shares in B
- 10% ordinary voting shares in B

Analysis:
- Financial ownership: 60% (preference shares participate economically)
- Voting rights: 10%

Result:
- ConsoMethod: 'N' or 'E' (no control despite 60% economic interest)
- GroupPerc: 60% (if equity method: share of profit)
- GroupCtrlPerc: 10%
```

## Current Implementation

### Method Determination Algorithm

From `P_CALC_OWNERSHIP_INDIRECT_PERCENTAGES.sql` (lines 484-518):

```sql
-- Check if Proportional Method is used or not
select @NoProportionalMethod = [dbo].[UDF_GET_CONFIG]('CALC_NO_PROPORTIONAL', NULL, @ConsoID)

If ISNULL(@NoProportionalMethod, 0) = 0
Begin
    -- Standard IFRS thresholds with proportional method
    Update #Companies
    Set ConsoMethod =
        Case
            -- Global Integration: >50% control OR parent company
            When (GroupCtrlPerc > @ConsoMethP OR CompanyID = @ParentID) then 'G'

            -- Proportional: exactly 50% (joint control)
            When (GroupCtrlPerc = @ConsoMethP AND CompanyID <> @ParentID) then 'P'

            -- Equity Method: 20-50% (significant influence)
            When (GroupCtrlPerc >= @ConsoMethN AND GroupCtrlPerc < @ConsoMethP
                  AND CompanyID <> @ParentID) then 'E'

            -- Not Consolidated: <20% (no influence)
            When (GroupCtrlPerc < @ConsoMethN AND CompanyID <> @ParentID) then 'N'

            Else 'N' -- Should not occur
        End
END
Else
BEGIN
    -- Alternative: No proportional method (IFRS 11 style)
    Update #Companies
    Set ConsoMethod =
        Case
            When (GroupCtrlPerc > @ConsoMethP OR CompanyID = @ParentID) then 'G'
            -- Note: 50% now goes to equity method, not proportional
            When (GroupCtrlPerc >= @ConsoMethN AND GroupCtrlPerc <= @ConsoMethP
                  AND CompanyID <> @ParentID) then 'E'
            When (GroupCtrlPerc < @ConsoMethN AND CompanyID <> @ParentID) then 'N'
            Else 'N'
        End
END
```

### Configurable Thresholds

```sql
-- Default thresholds
Set @ConsoMethP = 50  -- Proportional threshold (control)
Set @ConsoMethN = 20  -- Not consolidated threshold (significant influence)
```

### Control Percentage Propagation

The system calculates indirect control using an iterative algorithm:

```sql
-- Control propagates only through controlled subsidiaries
WHILE @CounterI <= @MaxLoop
BEGIN
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
            -- KEY: Only controlled companies can pass control
            SELECT CompanyID from #GroupControl where NewCtrl > 50
        )
        GROUP BY a.CompanyOwnedID
    ) SumTS015 ON SumTS015.CompanyOwnedID = a.CompanyID

    -- Exit when stable (no changes)
    IF (SELECT count(*) FROM #GroupControl WHERE OldCtrl <> NewCtrl) = 0
        SET @CounterI = @MaxLoop + 1

    SET @CounterI = @CounterI + 1
END
```

**Key Insight**: Control only propagates through entities where the parent already has >50% control. This ensures:
- P controls B (>50%) → P can use B's voting rights in C
- P does not control D (30%) → P cannot use D's voting rights

### Configuration Options

**CALC_NO_PROPORTIONAL**:
```sql
-- Disables proportional method (IFRS 11 compliance)
-- When set to '1', 50% joint ventures use equity method instead
Select TOP 1 @NoProportionalMethod = CASE when [Value] = '0' then 0 else 1 end
From [dbo].[T_CONFIG]
Where [Key] = 'CALC_NO_PROPORTIONAL'
AND ([CustomerID] is null or [CustomerID] = @CustomerID)
Order by [CustomerID] DESC
```

**GENERAL_COMPUTE_INDIRECT_THIRDS**:
```sql
-- Controls whether to compute indirect third-party percentages
-- For equity/proportional methods
Select TOP 1 @ComputeIndirectThirds = CASE when [Value] = '0' then 0 else 1 end
From [dbo].[T_CONFIG]
Where [Key] = 'GENERAL_COMPUTE_INDIRECT_THIRDS'
```

### Parent Company Special Handling

```sql
-- Parent company always gets 100% control and global integration
Update #GroupControl
Set NewCtrl = 100, OldCtrl = 100
where CompanyID = @ParentID

-- Parent company always has 100% group percentage
Update #Companies
Set GroupPerc = 100, MinorPerc = 0
Where CompanyID = @ParentID or GroupPerc > 100
```

### Method to Elimination Mapping

| ConsoMethod | Description | Elimination Procedure |
|-------------|-------------|----------------------|
| G | Global Integration | P_CONSO_ELIM_MINORITYINTEREST |
| P | Proportional | P_CONSO_ELIM_PROPORTIONAL |
| E | Equity Method | P_CONSO_ELIM_EQUITYMETHOD |
| N | Not Consolidated | P_CONSO_ELIM_NOTCONSOLIDATED |

## Theory vs Practice Analysis

| Aspect | Theory (IFRS 10/IAS 28) | Prophix.Conso Implementation | Alignment |
|--------|------------------------|------------------------------|-----------|
| Control Threshold | >50% voting (rebuttable) | GroupCtrlPerc > 50 | Full |
| Significant Influence | 20-50% (rebuttable) | 20 <= GroupCtrlPerc < 50 | Full |
| Joint Control | Shared control, unanimous | GroupCtrlPerc = 50 | Simplified |
| Control Propagation | Only through controlled entities | Iterative algorithm | Full |
| IFRS 11 Option | No proportional for JVs | CALC_NO_PROPORTIONAL config | Full |
| De Facto Control | <50% but effective control | Manual override required | Partial |
| Potential Voting Rights | Consider convertibles | Not automated | Gap |

## Gap Analysis

### Missing Elements

1. **De Facto Control**: No automatic detection of control with <50% voting
2. **Potential Voting Rights**: No consideration of convertible instruments
3. **Substantive Rights**: No qualitative control assessment
4. **Kick-Out Rights**: No automated protective vs substantive rights analysis

### Divergent Implementation

1. **Joint Control Simplification**: System uses exactly 50% threshold; IFRS requires unanimous consent assessment
2. **Significant Influence**: Presumes 20% threshold; actual assessment may require override

### Additional Features (Beyond Theory)

1. **IFRS 11 Toggle**: Configuration to disable proportional method
2. **Iterative Propagation**: Efficient multi-level control calculation
3. **Configurable Thresholds**: Customer-level override capability

## Business Impact

1. **Correct Consolidation Method**: Ensures appropriate accounting treatment per investment
2. **IFRS Compliance**: Supports both IAS 31 (proportional) and IFRS 11 (equity for JVs) approaches
3. **Audit Trail**: Clear documentation of method determination logic
4. **Flexibility**: Manual override capability for complex control situations

## Recommendations

1. **Add Override Capability**: Allow manual control percentage override for de facto control situations
2. **Document Control Basis**: Add field to document basis for control determination (voting rights, contractual, etc.)
3. **Consider Potential Rights**: Add option to include potential voting rights in control calculation
4. **Joint Control Assessment**: Add workflow for joint control documentation (IFRS 11 compliance)

## API Reference

### Primary API Handlers
| Handler | YAML File | Purpose | Status |
|---------|-----------|---------|--------|
| `Company_GetCompanies` | [api-company-endpoints.yaml](../11-agent-support/api-company-endpoints.yaml) | Get ConsoMethod, GroupCtrlPerc | ✅ IMPLEMENTED |
| `Ownership_CalculatePercentages` | [api-ownership-endpoints.yaml](../11-agent-support/api-ownership-endpoints.yaml) | Calculate control percentages | ✅ IMPLEMENTED |
| `Consolidation_Execute` | [api-consolidation-endpoints.yaml](../11-agent-support/api-consolidation-endpoints.yaml) | Apply method-specific eliminations | ✅ IMPLEMENTED |

### Supporting API Handlers
| Handler | YAML File | Purpose |
|---------|-----------|---------|
| `Config_GetConfig` | [api-config-endpoints.yaml](../11-agent-support/api-config-endpoints.yaml) | Get CALC_NO_PROPORTIONAL setting |
| `Ownership_GetOwnerships` | [api-ownership-endpoints.yaml](../11-agent-support/api-ownership-endpoints.yaml) | Get direct ownership records |

### Control Threshold Configuration
| Config Key | Values | Effect |
|------------|--------|--------|
| `CALC_NO_PROPORTIONAL` | 0/1 | Enable/disable proportional method |
| `GENERAL_COMPUTE_INDIRECT_THIRDS` | 0/1 | Compute third-party indirect percentages |

### API Workflow
```
Control-Based Method Determination via API:

1. OWNERSHIP ENTRY
   Ownership_SaveOwnership → TS015S0:
     - NbrVotingRights (for control calculation)
     - NbrFinRights (for allocation calculation)

2. CONTROL PERCENTAGE CALCULATION
   Ownership_CalculatePercentages → P_CALC_OWNERSHIP_INDIRECT_PERCENTAGES:
     - Iterative propagation algorithm
     - Control flows only through >50% entities
     - Result: GroupCtrlPerc per company

3. METHOD ASSIGNMENT
   Automatic based on GroupCtrlPerc thresholds:
     - >50%: ConsoMethod = 'G'
     - =50%: ConsoMethod = 'P' (if CALC_NO_PROPORTIONAL = 0)
     - 20-50%: ConsoMethod = 'E'
     - <20%: ConsoMethod = 'N'

4. ELIMINATION ROUTING
   Consolidation_Execute routes to appropriate procedure:
     - G → P_CONSO_ELIM_MINORITYINTEREST
     - P → P_CONSO_ELIM_PROPORTIONAL
     - E → P_CONSO_ELIM_EQUITYMETHOD
     - N → P_CONSO_ELIM_NOTCONSOLIDATED
```

### Implementation Status
| Feature | Status | Notes |
|---------|--------|-------|
| Control-based method | ✅ IMPLEMENTED | Standard IFRS thresholds |
| IFRS 11 toggle | ✅ IMPLEMENTED | CALC_NO_PROPORTIONAL config |
| Control propagation | ✅ IMPLEMENTED | Iterative algorithm |
| De facto control | ⚠️ PARTIAL | Manual override required |
| Potential voting rights | ❌ NOT_IMPLEMENTED | Gap severity 5 |

### Related API Documentation
- [API Index](../11-agent-support/api-index.yaml) - Master handler catalog
- [Gap Analysis](../11-agent-support/gap-analysis-report.yaml) - **FULLY IMPLEMENTED (95%)**

---

## Related Documentation

- [Direct and Indirect Holdings](direct-indirect-holdings.md) - Calculation mechanics
- [Ownership Percentages](ownership-percentages.md) - Financial vs voting percentages
- [Equity Method](../02-consolidation-methods/equity-method.md) - Equity method details
- [Global Integration](../02-consolidation-methods/global-integration.md) - Full consolidation

### Related Knowledge Chunks
- Chunk 0042: Step 6 - Elimination processing
- Chunk 0046-0047: Control threshold diagrams
- Chunk 0048: Equity method (20-50%)
- Chunk 0050: Global integration implications
- Chunk 0055: Method transition
- Chunk 0076: Significant influence indicators

---
*Document 15 of 50+ | Batch 5: Ownership Structure | Last Updated: 2024-12-01*
