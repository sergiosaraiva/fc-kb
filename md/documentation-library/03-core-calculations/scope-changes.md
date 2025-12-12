# Scope Changes: Entering and Leaving Companies

## Document Metadata
- **Category**: Core Calculations
- **Theory Source**: Knowledge base chunks: 0033-0035, 0044, 0269, 0328, 0339, 0355, 0400
- **Implementation Files**:
  - `Sigma.Database/dbo/Tables/TS014C0.sql` - FlagEnteringScope, FlagExistingScope columns
  - `Sigma.Database/dbo/Tables/TS070S1.sql` - Elimination selection methods
  - `Sigma.Database/dbo/Stored Procedures/P_CONSO_ELIM_USER.sql` - Entering/leaving selection
  - `Sigma.Database/dbo/Stored Procedures/P_CONSO_EVENT_GENERIC.sql` - Scope change events
  - `Sigma.Database/dbo/Stored Procedures/P_CALC_OWNERSHIP_INDIRECT_PERCENTAGES.sql` - % changes
- **Last Updated**: 2024-12-01
- **Completeness**: 85% (Core functionality; some automation needed)
- **Compliance Status**: IFRS 3 - Business Combinations, IFRS 10 - Consolidated Statements

## Executive Summary

Scope changes occur when companies enter or leave the consolidation perimeter. "Entering" companies are newly acquired or newly controlled subsidiaries that were not consolidated in the prior period. "Leaving" companies are disposed or deconsolidated subsidiaries that were consolidated in the prior period. Prophix.Conso tracks scope changes through flags (`FlagEnteringScope`, `FlagExistingScope`) and provides selection methods for applying specific eliminations and events to entering/leaving companies.

## Theoretical Framework

### Concept Definition

From Allen White's "Direct Consolidation" (Chunk 328):

> "When a new company is entering the consolidation scope after a shares acquisition, two questions need an answer: What is the equity at the date of acquisition? Can the difference between the acquisition price and the percentage of equity acquired be justified by some accounts to reevaluate or deevaluate?"

### Types of Scope Changes

| Type | Description | Accounting Impact |
|------|-------------|-------------------|
| **Entering - Acquisition** | New subsidiary acquired | Goodwill calculation, PPA |
| **Entering - Control Gained** | Existing associate → Subsidiary | Step acquisition |
| **Leaving - Disposal** | Subsidiary sold | Gain/loss recognition |
| **Leaving - Control Lost** | Subsidiary → Associate | Partial disposal |
| **Method Change** | G→P, P→E, E→N transitions | Reclassification entries |

### Key Principles

1. **Cut-off Date**: Determine exact date of control transfer
2. **Fair Value**: Measure assets/liabilities at acquisition date FV
3. **Partial Year**: Only include results from/until scope change date
4. **Goodwill**: Calculate on entry; write-off on exit
5. **CTA Recycling**: Release translation reserves on disposal

### Entry Accounting Flow

```
Company Enters Scope:
┌─────────────────────────────────────────────────────────┐
│  1. Determine acquisition date                           │
│  2. Calculate equity at acquisition date                 │
│  3. Perform Purchase Price Allocation (PPA)             │
│  4. Calculate goodwill/bargain purchase                  │
│  5. Include in consolidation from acquisition date       │
│  6. Pro-rate P&L if mid-year acquisition                │
└─────────────────────────────────────────────────────────┘
```

### Exit Accounting Flow

```
Company Leaves Scope:
┌─────────────────────────────────────────────────────────┐
│  1. Determine disposal date                              │
│  2. Calculate gain/loss on disposal                      │
│  3. Release accumulated goodwill                         │
│  4. Release accumulated CTA                              │
│  5. Release consolidated reserves                        │
│  6. Include results up to disposal date only            │
└─────────────────────────────────────────────────────────┘
```

## Current Implementation

### Database Schema

#### TS014C0 - Company Scope Flags

```sql
CREATE TABLE [dbo].[TS014C0] (
    ...
    [FlagEnteringScope]  BIT  CONSTRAINT [DefaultFlagEnteringValueConstraint_df] DEFAULT ((0)) NOT NULL,
    [FlagExistingScope]  BIT  CONSTRAINT [DefaultFlagExistingValueConstraint_df] DEFAULT ((0)) NOT NULL,
    [FlagDiscontinuing]  BIT  NOT NULL,
    [AvailableForSale]   BIT  CONSTRAINT [DF_TS014C0_AvailableForSale] DEFAULT ((0)) NOT NULL,
    ...
);
```

**Flag Meanings**:
| Flag | Value | Description |
|------|-------|-------------|
| FlagEnteringScope | 1 | Company newly entering consolidation |
| FlagExistingScope | 1 | Company existing in prior period |
| FlagDiscontinuing | 1 | Company marked for discontinuation |
| AvailableForSale | 1 | IFRS 5 - Held for sale classification |

### Selection Methods for Eliminations

From `TS070S1.sql` and user elimination procedures:

| SelectionID | Description | Use Case |
|-------------|-------------|----------|
| 1 | All companies | Standard eliminations |
| 2 | Parent only | Parent-specific adjustments |
| 3 | All except parent | Subsidiary eliminations |
| 4 | Global integration (G) | Full consolidation |
| 5 | Proportional (P) | Joint ventures |
| 6 | Equity method (E) | Associates |
| 7 | Not consolidated (N) | Cost method |
| **8** | **Entering companies** | **Acquisition adjustments** |
| **9** | **Leaving companies** | **Disposal adjustments** |
| 10 | Available for sale | IFRS 5 entities |
| 11 | All except parent and N | Operating entities |

### Entering/Leaving Selection Logic

From `P_CONSO_ELIM_USER.sql` (company selection):

```sql
create table #Companies (
    pk int identity primary key,
    CompanyCurrCode nvarchar(3),
    CurCompanyID int,
    RefCompanyID int,
    CurCompanyGroupPerc decimal (24,6),
    CurCompanyMinorPerc decimal (24,6),
    RefCompanyGroupPerc decimal (24, 6),
    RefCompanyMinorPerc decimal (24, 6),
    ConsoMethod char(1),
    IsParentCompany bit,
    AvailableForSale bit,
    FlagDiscontinuing bit,
    FlagEntering bit,       -- Company entering scope
    FlagLeaving bit         -- Company leaving scope
)
```

### Event Processing for Scope Changes

From `P_CONSO_EVENT_GENERIC.sql` (lines 70-77):

```sql
-- Handle Entering/Leaving as selection method
-- SelectionMethod = 8: Entering companies only
-- SelectionMethod = 9: Leaving companies only

-- Partners entering/leaving scope detection
-- Added logic for partners entering/leaving scope
```

### Reference vs Current Period Comparison

The system compares current period (CurConsoID) with reference period (RefConsoID) to detect scope changes:

```sql
-- Reference period columns track prior period state
RefCompanyID          -- Company ID in reference period (NULL if entering)
RefCompanyGroupPerc   -- Group % in reference period (0 if entering)
RefCompanyMinorPerc   -- Minor % in reference period

-- Current period columns track current state
CurCompanyID          -- Company ID in current period (NULL if leaving)
CurCompanyGroupPerc   -- Group % in current period
CurCompanyMinorPerc   -- Minor % in current period
```

**Detection Logic**:
```sql
-- Entering: In current period but NOT in reference period
FlagEntering = CASE WHEN RefCompanyID IS NULL AND CurCompanyID IS NOT NULL THEN 1 ELSE 0 END

-- Leaving: In reference period but NOT in current period
FlagLeaving = CASE WHEN RefCompanyID IS NOT NULL AND CurCompanyID IS NULL THEN 1 ELSE 0 END
```

### VarPercInteg Flow for Percentage Changes

When ownership percentages change (without full entry/exit), the system records the impact:

```sql
-- Percentage change impact recorded to VarPercInteg flow
select @VarPercIntegFlowID = dbo.UDF_GET_SPECIAL_FLOW(@ConsoID, 'VarPercInteg')

-- Calculate impact of percentage change on opening balances
ROUND(-1 * ISNULL(a.Amount, 0) *
      ((ISNULL(b.GroupPerc, 0) - ISNULL(b.RefGroupPerc, 0) +
        ISNULL(b.MinorPerc, 0) - ISNULL(b.RefMinorPerc, 0)) / 100),
      @RoundingDecimal) as Amount
```

### Custom Events for Scope Changes

The system supports custom events (TS080S0/TS080C1) that can be configured for scope changes:

```sql
-- Event header with entering/leaving selection
CREATE TABLE [dbo].[TS080S0] (
    [EventHeaderID]        INT          IDENTITY NOT NULL,
    [ConsoID]              INT          NOT NULL,
    [EventCode]            NVARCHAR(12) NOT NULL,
    [SelectionMethod]      CHAR(1)      NULL,  -- 8=Entering, 9=Leaving
    [PostingJournalTypeID] INT          NOT NULL,
    [Active]               BIT          NOT NULL,
    [ProcedureName]        VARCHAR(50)  NOT NULL
);
```

## Theory vs Practice Analysis

| Aspect | Theory (IFRS 3/10) | Prophix.Conso Implementation | Alignment |
|--------|-------------------|------------------------------|-----------|
| Entry Detection | Required | FlagEnteringScope | Full |
| Exit Detection | Required | Reference period comparison | Full |
| Selection Methods | Implied | 8=Entering, 9=Leaving | Full |
| Partial Year Results | Required | Manual configuration | Partial |
| Goodwill on Entry | Required | Via participation elims | Full |
| CTA Release on Exit | Required | Manual adjustment | Partial |
| Step Acquisition | Required | Not automated | Gap |

## Gap Analysis

### Missing Elements

1. **Automatic Partial Year**: No auto-calculation of pro-rated results
2. **Acquisition Date Tracking**: No explicit acquisition date field
3. **Step Acquisition Automation**: Gaining control events not fully automated
4. **CTA Auto-Recycling**: Translation reserve release requires manual entry

### Divergent Implementation

1. **Flag-Based vs Event-Based**: System uses flags; theory uses acquisition events
2. **Manual Configuration**: Many scope change entries require user configuration

### Additional Features (Beyond Theory)

1. **Selection Method Framework**: Flexible filtering for entering/leaving
2. **VarPercInteg Flow**: Explicit percentage change tracking
3. **AvailableForSale Flag**: IFRS 5 classification support

## Business Impact

### Current Capabilities

1. **Entry/Exit Detection**: Automatic via period comparison
2. **Selective Processing**: Apply eliminations to entering/leaving only
3. **Percentage Tracking**: Changes recorded to dedicated flow
4. **Custom Events**: Configurable acquisition/disposal events

### Operational Considerations

1. **Manual Review**: Verify scope changes before consolidation run
2. **Acquisition Date**: Document actual date for partial year calculation
3. **Goodwill Setup**: Configure goodwill for new acquisitions
4. **Disposal Entries**: Prepare gain/loss adjustments manually

## Recommendations

1. **Add Acquisition Date**: New field for exact control transfer date
2. **Auto Partial Year**: Calculate pro-rated results based on acquisition date
3. **Step Acquisition Module**: Automate gaining/losing control scenarios
4. **CTA Automation**: Auto-release translation reserves on disposal

## Practical Example

### Company Entry Scenario

**Situation**: P acquires 80% of S on July 1 (mid-year)

**Configuration**:
```
TS014C0:
- CompanyID: [S's ID]
- FlagEnteringScope: 1
- GroupPerc: 80
- ConsoMethod: 'G'
```

**Required Adjustments**:
1. Goodwill calculation (via S089-S094)
2. Pro-rate P&L to 6 months (manual or event)
3. Include B/S at 100% from July 1

### Company Exit Scenario

**Situation**: P sells 100% of S on September 30

**Configuration**:
```
Current Period: FlagEnteringScope = 0, ConsoMethod = 'N'
Reference Period: Had ConsoMethod = 'G'
System detects: FlagLeaving = 1
```

**Required Adjustments**:
1. Reverse goodwill (manual)
2. Calculate disposal gain/loss
3. Release consolidated reserves
4. Pro-rate P&L to 9 months

## API Reference

### Primary API Handlers
| Handler | YAML File | Purpose | Status |
|---------|-----------|---------|--------|
| `Company_GetCompanies` | [api-company-endpoints.yaml](../11-agent-support/api-company-endpoints.yaml) | Get companies with FlagEnteringScope/FlagExistingScope | ✅ IMPLEMENTED |
| `Consolidation_Execute` | [api-consolidation-endpoints.yaml](../11-agent-support/api-consolidation-endpoints.yaml) | Process scope change eliminations | ✅ IMPLEMENTED |
| `Event_GetEvents` | [api-event-endpoints.yaml](../11-agent-support/api-event-endpoints.yaml) | Get scope change events | ✅ IMPLEMENTED |

### Supporting API Handlers
| Handler | YAML File | Purpose |
|---------|-----------|---------|
| `Ownership_SaveOwnership` | [api-ownership-endpoints.yaml](../11-agent-support/api-ownership-endpoints.yaml) | Update ownership triggering scope change |
| `LaunchCalculateIndirectPercentagesJob` | [api-ownership-endpoints.yaml](../11-agent-support/api-ownership-endpoints.yaml) | Recalculate after scope change |

### API Workflow
```
1. Ownership_SaveOwnership → Add/remove company ownership
2. LaunchCalculateIndirectPercentagesJob → Detect scope changes:
   - FlagEnteringScope = 1 for new companies
   - FlagLeaving detected via period comparison
3. Event_GetEvents → Get scope change events (SelectionMethod 8/9)
4. Consolidation_Execute → Process:
   - Selection IDs 8, 15-17 for entering companies
   - Selection IDs 9, 16, 18 for leaving companies
```

### Implementation Status
| Feature | Status | Gap Reference |
|---------|--------|---------------|
| Entry detection | ✅ IMPLEMENTED | FlagEnteringScope |
| Exit detection | ✅ IMPLEMENTED | Period comparison |
| Selection methods | ✅ IMPLEMENTED | IDs 8, 9, 15-18 |
| Partial year P&L | ❌ NOT_IMPLEMENTED | Manual |
| Acquisition date tracking | ❌ NOT_IMPLEMENTED | Manual |

### Related API Documentation
- [API Index](../11-agent-support/api-index.yaml) - Master handler catalog
- [Gap Analysis](../11-agent-support/gap-analysis-report.yaml) - **PARTIAL (85%)**

---

## Related Documentation

- [Deconsolidation](deconsolidation.md) - Disposal accounting details
- [Participation Eliminations](../04-elimination-entries/participation-eliminations.md) - Investment handling
- [Goodwill Calculation](goodwill-calculation.md) - Acquisition goodwill
- [Control vs Ownership](../06-ownership-structure/control-vs-ownership.md) - Method changes

### Related Knowledge Chunks
- Chunk 0033-0035: Consolidation process overview
- Chunk 0044: Scope definition
- Chunk 0269: Methodology principles
- Chunk 0328: Acquisition entry scenario
- Chunk 0339-0344: Disposal scenarios
- Chunk 0400: Scope change impacts

---
*Document 20 of 50+ | Batch 7: Standard Progression | Last Updated: 2024-12-01*
