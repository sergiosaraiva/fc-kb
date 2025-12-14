# Deconsolidation: Disposal and Exit Accounting

## Document Metadata
- **Category**: Core Calculations
- **Theory Source**: Knowledge base chunks: 0198, 0339-0343, 1322-1324
- **Implementation Files**:
  - `Sigma.Database/dbo/Tables/TS014C0.sql` - FlagExistingScope, FlagDiscontinuing, AvailableForSale
  - `Sigma.Database/dbo/Tables/TS070S1.sql` - FlagLeavingScope, selection method configuration
  - `Sigma.Database/dbo/Stored Procedures/P_CONSO_ELIM_USER.sql` - FlagLeaving company selection
  - `Sigma.Database/dbo/Stored Procedures/P_CONSO_EVENT_GENERIC.sql` - Leaving scope event processing
  - `Sigma.Database/dbo/Stored Procedures/P_CONSO_LINKED_CATEGORY.sql` - Leaving company data copy
- **Last Updated**: 2024-12-01
- **Completeness**: 70% (Framework available; disposal adjustments require manual configuration)
- **Compliance Status**: IFRS 10 - Loss of Control, IAS 27 - Separate Financial Statements

## Executive Summary

Deconsolidation occurs when a subsidiary leaves the consolidation scope, typically through disposal of controlling interest, liquidation, or loss of control. Prophix.Conso supports deconsolidation through scope change flags (`FlagExistingScope`, `FlagLeavingScope`) and selection methods that allow specific eliminations and events to target leaving companies. Disposal gain/loss calculations and release of accumulated reserves (goodwill, CTA) require manual configuration through user-defined eliminations or group adjustments.

## Theoretical Framework

### Concept Definition

From Allen White's "Direct Consolidation" (Chunk 339):

> "A company A is consolidated since a number of years and, one day the group decides to sell the company to 3rd Parties. Such situation leads to a certain number of remarks, amongst which... the gain or loss on disposal should be calculated as the difference between the selling price and the percentage owned in company A equity."

### Types of Deconsolidation

| Type | Description | Accounting Impact |
|------|-------------|-------------------|
| **Full Disposal** | 100% sale to third parties | Complete exit, gain/loss recognition |
| **Partial Disposal (Loss of Control)** | Sale reducing control <50% | Exit + equity method investment |
| **Internal Disposal** | Sale within group | No group impact, only MI adjustment |
| **Liquidation** | Company wound up | Release all reserves to P&L |
| **Deconsolidation** | Administrative exit | Method change to 'N' |

### Key Principles (from Chunks 339, 198)

1. **Statutory vs Consolidated Gain**: Disposal gain differs between statutory (book value) and consolidated (equity value) view
2. **Equity Value Calculation**: `Equity Value = Financial % × Equity of Subsidiary`
3. **Goodwill Release**: Proportionate goodwill must be written off through P&L
4. **CTA Recycling**: Accumulated translation reserves must be released on disposal
5. **Partial Year Results**: Include P&L only up to disposal date

### Value Concepts (Chunk 198)

```
Equity Value of A = Investment in A + Consolidated Reserves of A

Where:
- Investment in A = Historical acquisition cost (statutory value)
- Consolidated Reserves = Financial % × Equity - Investment
```

**Disposal Gain/Loss Calculation**:
```
Statutory View:
  Gain = Selling Price - Statutory Book Value (historical cost)

Consolidation View:
  Gain = Selling Price - Equity Value
       = Selling Price - (Financial % × Net Equity)

Adjustment Needed = Statutory Gain - Consolidated Gain
```

### Disposal Accounting Flow

```
Company Exits Scope:
┌─────────────────────────────────────────────────────────────┐
│  1. Determine disposal date                                  │
│  2. Calculate statutory gain/loss (in parent books)          │
│  3. Calculate consolidated gain/loss (equity value basis)    │
│  4. Book adjustment: Statutory → Consolidated gain           │
│  5. Reverse accumulated goodwill to P&L                      │
│  6. Release accumulated CTA to P&L                           │
│  7. Release consolidated reserves                            │
│  8. Include P&L results up to disposal date only            │
│  9. Remove company from consolidation scope                  │
└─────────────────────────────────────────────────────────────┘
```

### Detailed Example (from Chunks 340-343)

**Scenario**: P owns 80% of A, sells 20% to third parties for 500

**Before Disposal (Year 1)**:
```
Company A Equity:
- Capital:           1,000
- Reserves:            500
- Revaluation:         200
- Profit Y1:           100
- Total:             1,800

Goodwill in P:          400

Consolidated Position:
- Consolidated Reserves = 80% × 1,800 - (1,200 - 400) = 640
- Minority Interests = 20% × 1,800 = 360
```

**Disposal Analysis (Year 2)**:
```
Statutory View:
- Selling Price:        500
- Book Value (20%):     300  (20/80 × 1,200)
- Statutory Gain:       200

Consolidation View:
- Equity at disposal = 1,000 + 600 + 200 + 50 = 1,850
- 20% Equity Value = 370
- Gain before goodwill = 500 - 370 = 130
- Goodwill release = 20/80 × 400 = 100
- Consolidated Gain = 130 - 100 = 30

Adjustment Required:
- Dr. Gain on Disposal    170
- Cr. Consolidated Reserves    170
  (Reduces statutory gain 200 to consolidated gain 30)
```

## Current Implementation

### Database Schema

#### TS014C0 - Company Scope Flags

```sql
CREATE TABLE [dbo].[TS014C0] (
    ...
    [FlagEnteringScope]  BIT  DEFAULT ((0)) NOT NULL,  -- Entering this period
    [FlagExistingScope]  BIT  DEFAULT ((0)) NOT NULL,  -- Existed in prior period
    [FlagDiscontinuing]  BIT  NOT NULL,                -- Marked for discontinuation
    [AvailableForSale]   BIT  DEFAULT ((0)) NOT NULL,  -- IFRS 5 classification
    ...
);
```

#### TS070S1 - Selection Methods with Leaving Flag

```sql
CREATE TABLE [dbo].[TS070S1] (
    [ConsoMethodSelectionID] INT  IDENTITY (1, 1) NOT NULL,
    [SelectionID]            TINYINT        NOT NULL,
    [SelectionText]          NVARCHAR (50)  NOT NULL,
    [Parent]                 BIT            NOT NULL,
    [SelectionCode]          CHAR (1)       NULL,
    [AvailableForSale]       BIT            NULL,
    [FlagDiscontinuing]      BIT            NULL,
    [FlagEnteringScope]      BIT            DEFAULT ((0)) NOT NULL,
    [FlagLeavingScope]       BIT            DEFAULT ((0)) NOT NULL
);
```

### Leaving Company Detection

From `P_CONSO_ELIM_USER.sql` (company selection):

```sql
create table #Companies (
    pk int identity primary key,
    ...
    CurCompanyID int,          -- Current period (NULL if leaving)
    RefCompanyID int,          -- Reference period (exists if leaving)
    ...
    FlagEntering bit,          -- Company entering scope
    FlagLeaving bit            -- Company leaving scope
)

-- Leaving: In reference period but NOT in current period
-- FlagLeaving = 1 when RefCompanyID IS NOT NULL AND CurCompanyID IS NULL
```

### Selection Methods for Leaving Companies

| SelectionID | Code | Description | Use Case |
|-------------|------|-------------|----------|
| 9 | J | Leaving companies only | Disposal adjustments |
| 16 | - | All leaving (ConsoMethodSelectionID) | Comprehensive exit processing |
| 18 | - | All leaving partners | Partner-specific leaving |

From `P_CONSO_ELIM_USER.sql` (lines 336-339):

```sql
else if @ConsoMethodSelectionID = 16  -- All leaving
begin
    delete from #Companies where not (FlagLeaving = 1)
end
```

### Event Processing for Leaving Companies

From `P_CONSO_EVENT_GENERIC.sql` (lines 275, 329):

```sql
-- Get leaving scope flag from selection configuration
, @IsLeaving = FlagLeavingScope
From dbo.TS070S1
Where SelectionCode = ISNULL(@SelectionMethod, 'A')

-- Filter companies based on leaving scope
( @IsLeaving = 0 or b.FlagExistingScope = @IsLeaving or @SelectionMethod = 'P' )
```

### Data Copy for Leaving Companies

From `P_CONSO_LINKED_CATEGORY.sql` (lines 922-925):

```sql
-- For companies leaving the scope, look also in the reference period
Update a
Set a.IsUsed = 1
From @CompanyMappings a
-- Additional logic to include leaving company data
```

### User Elimination Configuration for Disposal

Disposal adjustments must be configured manually using the user elimination framework:

**Step 1: Define Special Accounts**
```sql
-- Required accounts for disposal processing:
- Financial Investment account
- Gain/Loss on Disposal account
- Consolidated Reserves account
- Goodwill account
- CTA Reserve account
```

**Step 2: Create Disposal Elimination Header**
```sql
INSERT INTO TS070S0 (ConsoID, ElimCode, JournalText,
                     ConsoMethodSelectionID, Active, ...)
VALUES (@ConsoID, 'U002', 'Disposal Adjustment - Leaving Companies',
        16, 1, ...)  -- ConsoMethodSelectionID 16 = All leaving
```

**Step 3: Define Disposal Adjustment Lines**
```sql
-- Line 1: Reverse statutory gain (adjust to consolidated basis)
INSERT INTO TS071S0 (EliminationHeaderID, LineNr,
    FromType, FromAccountID, FromPeriod,
    ToAccountID, ToSign, Percentage)
VALUES (@HeaderID, 1,
    1, @GainOnDisposal_AccountID, 'C',  -- Closing, Current Period
    @GainOnDisposal_AccountID, -1, 1)   -- Reverse 100%

-- Line 2: Release consolidated reserves
-- (Additional lines for goodwill, CTA, etc.)
```

## Theory vs Practice Analysis

| Aspect | Theory (IFRS 10/IAS 27) | Prophix.Conso Implementation | Alignment |
|--------|------------------------|------------------------------|-----------|
| Exit Detection | Required | FlagLeavingScope, period comparison | Full |
| Selection Methods | Implied | SelectionID 9, 16, 18 for leaving | Full |
| Disposal Gain Calculation | Required | Manual via user eliminations | Partial |
| Goodwill Release | Required | Manual adjustment | Partial |
| CTA Recycling | Required | Manual adjustment | Partial |
| Partial Year P&L | Required | Manual configuration | Partial |
| Statutory vs Conso Gain | Required | User elimination framework | Full |

## Gap Analysis

### Missing Elements

1. **Automatic Disposal Gain Calculation**: No built-in procedure to calculate statutory vs consolidated gain
2. **Automatic Goodwill Release**: No auto-write-off of proportionate goodwill
3. **Automatic CTA Recycling**: No auto-release of translation reserves
4. **Disposal Date Tracking**: No explicit field for disposal date
5. **Step-Down Automation**: Losing control (G→E transition) not automated

### Divergent Implementation

1. **Manual Configuration Required**: Theory assumes systematic processing; implementation requires setup
2. **No Standard Disposal Template**: Each group must configure disposal eliminations
3. **Event-Based vs Flag-Based**: Theory uses events; implementation uses scope flags

### Additional Features (Beyond Theory)

1. **Flexible Selection Methods**: Target specific leaving company types
2. **Partner Leaving Support**: Handle partner companies exiting scope
3. **Available for Sale Integration**: IFRS 5 classification support
4. **Reference Period Tracking**: Full comparison with prior period state

## Business Impact

### Current Capabilities

1. **Exit Detection**: Automatic via period comparison
2. **Selective Processing**: Apply eliminations to leaving companies only
3. **Custom Events**: Configurable disposal events via TS080S0/TS080C1
4. **Partner Handling**: Track partner company scope changes

### Operational Considerations

1. **Pre-Disposal Review**: Verify company marked as leaving before consolidation run
2. **Manual Adjustments**: Calculate and enter disposal gain adjustment
3. **Goodwill Tracking**: Maintain records of goodwill per subsidiary for release
4. **CTA Documentation**: Track accumulated translation reserves for recycling
5. **Partial Year Cut-Off**: Configure P&L inclusion period manually

## Recommendations

1. **Add Disposal Date Field**: New column for exact date of control transfer
2. **Auto Gain Calculation**: Build procedure to compare statutory vs equity value
3. **Goodwill Release Module**: Automate write-off based on ownership change
4. **CTA Auto-Recycling**: Automatic release of translation reserves on exit
5. **Standard Disposal Template**: Pre-configured elimination rules for common scenarios

## Practical Implementation Example

### Full Disposal Scenario

**Situation**: P sells 100% of subsidiary S on September 30

**Configuration**:
```
Current Period TS014C0:
- S's row removed or ConsoMethod = 'N'

Reference Period TS014C0:
- S's row exists with ConsoMethod = 'G'

System Detection:
- FlagLeaving = 1 (in reference, not in current)
```

**Required Manual Adjustments**:
```
1. Calculate Disposal Gain Adjustment:
   Statutory gain (in P's books)        XXX
   Less: Equity value basis gain       (YYY)
   Adjustment required                  ZZZ

2. Release Goodwill:
   Dr. P&L (Goodwill write-off)         AAA
   Cr. Goodwill                         AAA

3. Release CTA:
   Dr. CTA Reserve                      BBB
   Cr. P&L (CTA recycling)              BBB

4. Adjust Consolidated Reserves:
   Dr. Gain on Disposal                 ZZZ
   Cr. Consolidated Reserves            ZZZ
```

### Partial Disposal (Control Retained)

**Situation**: P sells 20% of S, retaining 60% (control maintained)

**Configuration**:
```
TS014C0:
- S remains with ConsoMethod = 'G'
- GroupPerc changes from 80% to 60%
- MinorPerc changes from 20% to 40%
- FlagEnteringScope = 0
- FlagExistingScope = 1 (existed before)
```

**Required Adjustments** (as per Chunk 343):
```
1. Proportionate Goodwill Release:
   20/80 × Original Goodwill = Amount to P&L

2. Disposal Gain Adjustment:
   Statutory gain vs Consolidated gain (equity basis)

3. Minority Interest Increase:
   Recalculate MI at new 40% level
```

## API Reference

### Primary API Handlers
| Handler | YAML File | Purpose | Status |
|---------|-----------|---------|--------|
| `Company_GetCompanies` | [api-company-endpoints.yaml](../11-agent-support/api-company-endpoints.yaml) | Get leaving companies via period comparison | ✅ IMPLEMENTED |
| `Consolidation_Execute` | [api-consolidation-endpoints.yaml](../11-agent-support/api-consolidation-endpoints.yaml) | Process disposal eliminations | ✅ IMPLEMENTED |
| `Journal_SaveJournal` | [api-adjustment-endpoints.yaml](../11-agent-support/api-adjustment-endpoints.yaml) | Book disposal gain/loss manually | ✅ IMPLEMENTED |

### Supporting API Handlers
| Handler | YAML File | Purpose |
|---------|-----------|---------|
| `Event_GetEvents` | [api-event-endpoints.yaml](../11-agent-support/api-event-endpoints.yaml) | Get leaving scope events |
| `Report_ExecuteReport` | [api-reports-endpoints.yaml](../11-agent-support/api-reports-endpoints.yaml) | Generate disposal analysis reports |

### API Workflow
```
1. Company_GetCompanies → Detect leaving companies:
   - RefCompanyID NOT NULL AND CurCompanyID NULL = Leaving
   - SelectionID 9, 16, 18 for leaving companies
2. Journal_SaveJournal → Book disposal adjustments (manual):
   - Disposal gain/loss adjustment
   - Goodwill release
   - CTA recycling
3. Consolidation_Execute → Process leaving company eliminations
4. Report_ExecuteReport → Verify disposal impact
```

### Implementation Status
| Feature | Status | Gap Reference |
|---------|--------|---------------|
| Exit detection | ✅ IMPLEMENTED | FlagLeavingScope |
| Selection methods | ✅ IMPLEMENTED | IDs 9, 16, 18 |
| Disposal gain calculation | ❌ NOT_IMPLEMENTED | Manual via Journal |
| Goodwill auto-release | ❌ NOT_IMPLEMENTED | Manual |
| CTA auto-recycling | ❌ NOT_IMPLEMENTED | Manual |

### Related API Documentation
- [API Index](../11-agent-support/api-index.yaml) - Master handler catalog
- [Gap Analysis](../11-agent-support/gap-analysis-report.yaml) - **PARTIAL (70%)**

---

## Related Documentation

- [Scope Changes](scope-changes.md) - Entry/exit detection mechanisms
- [Goodwill Calculation](goodwill-calculation.md) - Original goodwill setup
- [Translation Adjustments](../05-currency-translation/translation-adjustments.md) - CTA accumulation
- [Participation Eliminations](../04-elimination-entries/participation-eliminations.md) - Investment accounting
- [Control vs Ownership](../06-ownership-structure/control-vs-ownership.md) - Method changes

### Related Knowledge Chunks
- Chunk 0198: Company value from consolidation viewpoint
- Chunk 0339: Disposal situation overview
- Chunk 0340-0343: Detailed disposal example with calculations
- Chunk 1322: In/Out consolidation scope topics
- Chunk 1323: Group restructuring (deconsolidation, liquidation)
- Chunk 1324: Special disposal situations

---
*Document 21 of 50+ | Batch 7: Standard Progression | Last Updated: 2024-12-01*
