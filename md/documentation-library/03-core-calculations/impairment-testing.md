# Impairment Testing: Goodwill and Asset Impairment in Consolidation

## Document Metadata
- **Category**: Core Calculations
- **Theory Source**: Knowledge base chunks: 0041, 0731, IAS 36 requirements
- **Implementation Files**:
  - `Sigma.Database/dbo/Stored Procedures/P_REPORT_GOODWILL.sql` - Goodwill reporting (display only)
  - `Sigma.Database/dbo/Stored Procedures/P_REPORT_GOODWILL_HEADER.sql` - Goodwill header
  - `Sigma.Database/dbo/Tables/TS070S0.sql` - User elimination framework
  - `Sigma.Database/dbo/Tables/TS071S0.sql` - Elimination detail lines
- **Last Updated**: 2024-12-02 (Enhanced with visual diagram, implementation checklist, and validation queries)
- **Completeness**: 70% (Manual workaround fully documented with decision framework; no automated testing module)
- **Compliance Status**: IAS 36 - Minimal (requires full manual process)

## Executive Summary

Impairment testing under IAS 36 requires annual assessment of goodwill and indefinite-life intangible assets for potential value reduction. Allen White's "Direct Consolidation" (Chunks 41, 731) references goodwill depreciation and impairment as essential adjustments in consolidation. Prophix.Conso provides **goodwill reporting capability** but **no automated impairment testing module**. Users must calculate impairments externally and record adjustments through user-defined eliminations. There is no CGU (Cash Generating Unit) tracking, recoverable amount calculation, or systematic impairment workflow.

### Visual: Impairment Testing Process Flow

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    IMPAIRMENT TESTING WORKFLOW (IAS 36)                      │
└─────────────────────────────────────────────────────────────────────────────┘

  ANNUAL TESTING CYCLE:
  ┌─────────────────────────────────────────────────────────────────────────┐
  │                                                                         │
  │  ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐         │
  │  │ IDENTIFY │───►│ ALLOCATE │───►│  TEST    │───►│  RECORD  │         │
  │  │   CGUs   │    │ GOODWILL │    │RECOVERABLE│   │IMPAIRMENT│         │
  │  └──────────┘    └──────────┘    └──────────┘    └──────────┘         │
  │       │               │               │               │                │
  │       ▼               ▼               ▼               ▼                │
  │  Cash-Generating   Synergy-based   Higher of VIU   P&L expense        │
  │  Unit boundaries   allocation      and FVLCD       Reduce goodwill    │
  │                                                                         │
  └─────────────────────────────────────────────────────────────────────────┘

  IMPAIRMENT CALCULATION:
  ┌─────────────────────────────────────────────────────────────────────────┐
  │                                                                         │
  │  CARRYING AMOUNT          vs        RECOVERABLE AMOUNT                  │
  │  ─────────────────                  ──────────────────                  │
  │  ┌─────────────────────┐           ┌─────────────────────┐             │
  │  │ CGU Net Assets  800 │           │ VALUE IN USE (VIU)  │             │
  │  │ Allocated GW    200 │           │ = PV of future      │             │
  │  │ ─────────────────   │           │   cash flows        │             │
  │  │ TOTAL        1,000  │           │ = 950               │             │
  │  └─────────────────────┘           └─────────────────────┘             │
  │           │                                  │        │                 │
  │           │                                  │  OR    │                 │
  │           │                                  │        ▼                 │
  │           │                        ┌─────────────────────┐             │
  │           │                        │ FVLCD              │              │
  │           │                        │ = Market value     │              │
  │           │                        │   - disposal costs │              │
  │           │                        │ = 900              │              │
  │           │                        └─────────────────────┘             │
  │           │                                  │                          │
  │           │                          ┌──────┴──────┐                   │
  │           │                          │Higher = 950 │                   │
  │           ▼                          │(RECOVERABLE)│                   │
  │  ┌─────────────────────────────────┐└──────┬──────┘                   │
  │  │ IMPAIRMENT TEST:                        │                          │
  │  │                                         │                          │
  │  │  Carrying (1,000) > Recoverable (950)?  │                          │
  │  │  YES → Impairment = 50                  │                          │
  │  └─────────────────────────────────────────┘                          │
  │                                                                         │
  └─────────────────────────────────────────────────────────────────────────┘

  IMPAIRMENT WATERFALL (IAS 36.104):
  ┌─────────────────────────────────────────────────────────────────────────┐
  │                                                                         │
  │  Impairment Loss = 50                                                   │
  │                                                                         │
  │  STEP 1: Reduce Goodwill FIRST          STEP 2: Then Other Assets      │
  │  ────────────────────────────           ──────────────────────────      │
  │  ┌─────────────────────────┐           ┌─────────────────────────┐     │
  │  │ Goodwill: 200           │           │ (Only if impairment     │     │
  │  │ Less: Impairment (50)   │           │  exceeds goodwill)      │     │
  │  │ ───────────────────     │           │                         │     │
  │  │ Remaining: 150          │           │ Pro-rata to other       │     │
  │  └─────────────────────────┘           │ assets (not below       │     │
  │                                         │ individual FV)          │     │
  │  ⚠️ NEVER REVERSE GW IMPAIRMENT        └─────────────────────────┘     │
  │                                                                         │
  └─────────────────────────────────────────────────────────────────────────┘

  PROPHIX.CONSO WORKAROUND PROCESS:
  ┌─────────────────────────────────────────────────────────────────────────┐
  │                                                                         │
  │  STEP 1              STEP 2              STEP 3              STEP 4    │
  │  ───────             ───────             ───────             ───────   │
  │  ┌───────────┐       ┌───────────┐       ┌───────────┐       ┌───────┐ │
  │  │ External  │──────►│ Document  │──────►│ Create    │──────►│Verify │ │
  │  │ VIU/FVLCD │       │ Analysis  │       │User Elim  │       │Entry  │ │
  │  │ Calc      │       │ & Approve │       │TS070S0/71 │       │       │ │
  │  └───────────┘       └───────────┘       └───────────┘       └───────┘ │
  │                                                                         │
  │  ⚠️ NO CGU tables - track externally                                   │
  │  ⚠️ NO automated VIU - calculate in Excel                              │
  │  ⚠️ NO reversal prevention - manual discipline required                 │
  │                                                                         │
  │  ELIMINATION ENTRY:                                                     │
  │  ┌───────┬──────────────────────────┬─────────┬───────────────────────┐│
  │  │ Line  │ Account                  │ Dr/(Cr) │ Purpose               ││
  │  ├───────┼──────────────────────────┼─────────┼───────────────────────┤│
  │  │   1   │ Impairment Loss (P&L)    │  Dr 50  │ Recognize expense     ││
  │  │   2   │ Goodwill (B/S)           │ (Cr 50) │ Reduce asset          ││
  │  └───────┴──────────────────────────┴─────────┴───────────────────────┘│
  │                                                                         │
  └─────────────────────────────────────────────────────────────────────────┘
```

## Theoretical Framework

### IAS 36 Requirements

From Allen White's "Direct Consolidation" (Chunk 41):

> "We have to book a goodwill of 20 and, depending on the evaluation rules, to depreciate this goodwill or to book an impairment on this goodwill."

**Annual Testing Requirements**:
1. Goodwill - mandatory annual test (or when trigger events occur)
2. Indefinite-life intangibles - mandatory annual test
3. Other assets - test when impairment indicators present

### Impairment Calculation

```
Carrying Amount > Recoverable Amount = Impairment Loss

Where:
Recoverable Amount = Higher of:
  - Fair Value Less Costs of Disposal (FVLCD)
  - Value in Use (VIU)

Value in Use = Present Value of Future Cash Flows
```

### Cash Generating Units (CGU)

IAS 36 requires goodwill allocation to CGUs for impairment testing:

```
Group Structure:
├── Subsidiary A (Goodwill: 500)
│   ├── CGU Alpha (allocated: 300)
│   └── CGU Beta (allocated: 200)
└── Subsidiary B (Goodwill: 400)
    └── CGU Gamma (allocated: 400)

Impairment test performed at CGU level, not entity level.
```

### Goodwill Impairment Waterfall

```
CGU Carrying Amount:
  + Net Assets at carrying value
  + Allocated Goodwill
  = Total CGU Carrying Amount

If CGU Carrying > Recoverable Amount:
  1. First reduce goodwill to zero
  2. Then reduce other assets pro-rata (not below individual FV)
```

### Impairment Reversal

| Asset Type | Reversal Allowed |
|------------|-----------------|
| Goodwill | **Never** - IAS 36.124 |
| Other assets | Yes, if circumstances change |
| Prior period | No retroactive reversal |

## Current Implementation

### Goodwill Reporting Only

**P_REPORT_GOODWILL.sql** - Displays goodwill data but doesn't test for impairment:

```sql
-- Goodwill report structure
CREATE PROCEDURE [dbo].[P_REPORT_GOODWILL]
    @ConsoID INT,
    @CompanyID INT,
    @Debug BIT = 0
AS
BEGIN
    -- Returns goodwill amounts from consolidation data
    -- NO impairment calculation logic
    -- NO CGU structure
    -- NO value in use calculation

    SELECT
        CompanyID,
        CompanyCode,
        GoodwillAmount,
        ...
    FROM consolidation_data
    WHERE ConsoID = @ConsoID
END
```

### Manual Impairment Process

Users record impairments via user-defined eliminations:

```sql
-- Header: Goodwill Impairment
INSERT INTO TS070S0 (ConsoID, ElimCode, ElimType, ElimText, Active,
                     ConsoMethodSelectionID, JournalTypeID, ...)
VALUES (@ConsoID, 'U030', 'U', 'Goodwill Impairment', 1,
        4, @JournalID, ...);

-- Detail: Dr Impairment Loss, Cr Goodwill
INSERT INTO TS071S0 (EliminationHeaderID, LineNr,
    FromType, FromAccountID, FromPeriod,
    ToAccountID, ToSign, Percentage)
VALUES (@HeaderID, 1,
    1, @GoodwillAccount, 'C',
    @ImpairmentLossAccount, 1, 1);  -- Manual amount
```

### What's Available

| Capability | Implementation | Status |
|------------|----------------|--------|
| Goodwill display | P_REPORT_GOODWILL | **Available** |
| Manual impairment entry | User eliminations | **Available** |
| Impairment loss posting | Account framework | **Available** |
| Period tracking | Consolidation periods | **Available** |
| CGU definition | Not available | **Gap** |
| Automated testing | Not available | **Gap** |
| Value in Use calc | Not available | **Gap** |
| Recoverable amount | Not available | **Gap** |

## Gap Analysis

### Gap Status: CONFIRMED - NOT_IMPLEMENTED (Severity 8)

**What's Missing**:

1. **CGU Structure Definition**
   - No table for Cash Generating Unit definition
   - Cannot allocate goodwill to CGUs
   - No CGU hierarchy support

2. **Impairment Testing Module**
   - No annual testing workflow
   - No trigger event detection
   - No automated comparison of carrying vs recoverable

3. **Value in Use Calculation**
   - No cash flow projection storage
   - No discount rate configuration
   - No growth rate assumptions
   - No terminal value calculation

4. **Fair Value Less Costs of Disposal**
   - No market value tracking
   - No disposal cost estimation
   - No comparison logic

5. **Impairment Reversal Prevention**
   - System doesn't block goodwill impairment reversals
   - No audit trail for impairment decisions
   - Manual discipline required

6. **Reporting & Disclosure**
   - No standard impairment test documentation
   - No CGU allocation report
   - No sensitivity analysis

### Compliance Risk Assessment

| IAS 36 Requirement | Current Support | Risk Level |
|-------------------|-----------------|------------|
| Annual goodwill test | Manual only | **High** |
| CGU allocation | Not supported | **High** |
| VIU calculation | External | **Medium** |
| Reversal prohibition | Not enforced | **Medium** |
| Disclosure requirements | Manual | **Medium** |
| Audit trail | Limited | **Medium** |

## Manual Workaround

### Complete Manual Process

**Step 1: External Impairment Calculation**

Prepare externally in Excel/valuation tool:
- Identify CGUs
- Calculate Value in Use (DCF)
- Determine Fair Value Less Costs of Disposal
- Compare to carrying amount
- Calculate impairment loss

**Step 2: Document the Analysis**

Create supporting documentation:
- CGU identification rationale
- Key assumptions (discount rate, growth rate)
- Sensitivity analysis
- Management sign-off

**Step 3: Record in Prophix.Conso**

```sql
-- Create user elimination for impairment
INSERT INTO TS070S0 (ConsoID, ElimCode, ElimType, ElimText, Active,
                     ConsoMethodSelectionID, JournalTypeID, MinorityFlag, ...)
VALUES (@ConsoID, 'U031', 'U', 'GW Impairment - CGU Alpha', 1,
        4, @JournalID, 0, ...);

-- Line 1: Reduce Goodwill
INSERT INTO TS071S0 (EliminationHeaderID, LineNr,
    FromType, FromAccountID, FromPeriod,
    ToAccountID, ToSign, Percentage)
VALUES (@HeaderID, 1,
    2, @GoodwillAccount, 'C',      -- Flow level
    @AccumImpairmentAccount, -1, 1);  -- Credit

-- Line 2: Record P&L impact
INSERT INTO TS071S0 (...)
VALUES (@HeaderID, 2,
    1, @ImpairmentPlaceholder, 'C',
    @ImpairmentExpenseAccount, 1, 1);  -- Debit P&L
```

**Step 4: Verify MI Impact**

If goodwill relates to less-than-100% subsidiary:
- Consider whether impairment affects MI
- Create separate elimination if needed

**Step 5: Period Roll-Forward**

For subsequent periods:
- Carry forward accumulated impairment
- Do NOT reverse goodwill impairment
- Update carrying amount for CGU

### Tracking Template

| CGU | Goodwill Allocated | Carrying Amount | VIU | FVLCD | Recoverable | Impairment |
|-----|-------------------|-----------------|-----|-------|-------------|------------|
| Alpha | 300 | 450 | 400 | 380 | 400 | 50 |
| Beta | 200 | 350 | 380 | 360 | 380 | 0 |
| Gamma | 400 | 600 | 550 | 520 | 550 | 50 |

## Audit Documentation Best Practices

### Required Documentation Checklist

For each annual impairment test, maintain:

| Document | Purpose | Retention |
|----------|---------|-----------|
| CGU identification memo | Justifies CGU boundaries | Permanent |
| Goodwill allocation schedule | Shows allocation basis | Annual update |
| VIU calculation workbook | DCF model with assumptions | Annual |
| Key assumptions summary | Discount rate, growth rates | Annual |
| Sensitivity analysis | Impact of assumption changes | Annual |
| Management approval | Sign-off on results | Annual |
| Elimination entry support | Links to TS070S0/TS071S0 | Per entry |

### Audit Trail in Prophix.Conso

**Linking External Work to System Entries**:

```sql
-- Use JournalText field to create audit trail
INSERT INTO TS070S0 (ConsoID, ElimCode, ElimType, ElimText, ...)
VALUES (@ConsoID, 'U031', 'U',
    'GW Impairment - CGU Alpha - Ref: IMP-2024-001 - VIU 400K vs Carrying 450K',
    ...);

-- Include key details in elimination text:
-- 1. CGU name
-- 2. Reference number to external documentation
-- 3. Key comparison values
```

### Period-to-Period Roll-Forward

```
Year 1:
  Opening Goodwill: 1,000
  Impairment (CGU Alpha): (50)
  Impairment (CGU Gamma): (50)
  Closing Goodwill: 900

Year 2 (Copy Period):
  Opening Goodwill: 900  ← Copy forward closing
  New Test Results: ...
  ❌ NEVER reverse goodwill impairment
```

### Numeric Example: Complete Impairment Test

**Scenario**: Subsidiary acquired with goodwill of 500, now needs impairment testing.

**Step 1: Identify CGU and Allocate Goodwill**
```
Subsidiary X
├── CGU North: Allocated 200 (40% of synergies)
└── CGU South: Allocated 300 (60% of synergies)
```

**Step 2: Calculate Carrying Amounts**
```
CGU North:
  Net Assets at book value:     800
  Allocated Goodwill:           200
  Total Carrying Amount:      1,000

CGU South:
  Net Assets at book value:   1,200
  Allocated Goodwill:           300
  Total Carrying Amount:      1,500
```

**Step 3: Determine Recoverable Amounts**
```
CGU North:
  VIU (5-year DCF, 10% discount): 950
  FVLCD (market approach):        900
  Recoverable Amount:             950 (higher)
  Impairment: 1,000 - 950 =        50 ← Impairment required

CGU South:
  VIU (5-year DCF, 10% discount): 1,600
  FVLCD (market approach):        1,550
  Recoverable Amount:             1,600 (higher)
  Impairment: 1,500 - 1,600 =       0 ← No impairment
```

**Step 4: Record in Prophix.Conso**
```sql
-- Create user elimination for CGU North impairment
-- Header
INSERT INTO TS070S0 (ConsoID, ElimCode, ElimType, ElimText, Active, ...)
VALUES (@ConsoID, 'U032', 'U',
    'GW Impairment CGU North - IMP-2024-002 - Carrying 1,000 vs VIU 950', 1, ...);

-- Detail Line 1: Debit Impairment Loss (P&L)
-- Detail Line 2: Credit Goodwill (Balance Sheet)
-- Amount: 50
```

**Step 5: Verify Journal Entry**
```
Dr  Impairment Loss - Goodwill (P&L)     50
    Cr  Goodwill (BS)                         50
```

## Recommended Implementation

### Phase 1: CGU Definition Schema

```sql
-- Cash Generating Unit definition
CREATE TABLE TS085S0 (
    CGUID               INT IDENTITY PRIMARY KEY,
    ConsoID             INT NOT NULL,
    CGUCode             NVARCHAR(20) NOT NULL,
    CGUDescription      NVARCHAR(100),
    ParentCGUID         INT NULL,          -- Hierarchy support
    CompanyID           INT NULL,          -- Can link to company
    Active              BIT DEFAULT 1
);

-- Goodwill allocation to CGUs
CREATE TABLE TS085S1 (
    CGUGoodwillID       INT IDENTITY PRIMARY KEY,
    ConsoID             INT NOT NULL,
    CGUID               INT NOT NULL,
    GoodwillAccountID   INT NOT NULL,
    AllocatedAmount     DECIMAL(28,6),
    AllocationDate      DATE,
    AllocationBasis     NVARCHAR(200)      -- Documentation
);
```

### Phase 2: Impairment Test Record

```sql
-- Impairment test record
CREATE TABLE TS085S2 (
    ImpairmentTestID    INT IDENTITY PRIMARY KEY,
    ConsoID             INT NOT NULL,
    CGUID               INT NOT NULL,
    TestDate            DATE NOT NULL,
    CarryingAmount      DECIMAL(28,6),
    ValueInUse          DECIMAL(28,6),
    FairValueLCD        DECIMAL(28,6),
    RecoverableAmount   DECIMAL(28,6),
    ImpairmentRequired  DECIMAL(28,6),
    ImpairmentRecorded  DECIMAL(28,6),
    TestStatus          CHAR(1),           -- P=Pending, A=Approved, R=Rejected
    ApprovedByUserID    INT NULL,
    ApprovedDate        DATE NULL,
    Notes               NVARCHAR(MAX)
);

-- VIU Assumptions
CREATE TABLE TS085S3 (
    VIUAssumptionID     INT IDENTITY PRIMARY KEY,
    ImpairmentTestID    INT NOT NULL,
    AssumptionType      CHAR(1),           -- D=Discount, G=Growth, T=Terminal
    Year                INT,               -- 1-5 for projection period
    Value               DECIMAL(10,4),
    Notes               NVARCHAR(200)
);
```

### Phase 3: Automated Impairment Procedure

```sql
CREATE PROCEDURE P_CONSO_IMPAIRMENT_TEST
    @ConsoID INT,
    @CGUID INT,
    @TestDate DATE,
    @CarryingAmount DECIMAL(28,6),
    @ValueInUse DECIMAL(28,6),
    @FairValueLCD DECIMAL(28,6)
AS
BEGIN
    DECLARE @RecoverableAmount DECIMAL(28,6)
    DECLARE @ImpairmentRequired DECIMAL(28,6)

    -- Determine recoverable amount
    SET @RecoverableAmount =
        CASE WHEN @ValueInUse > @FairValueLCD
             THEN @ValueInUse
             ELSE @FairValueLCD END

    -- Calculate impairment
    SET @ImpairmentRequired =
        CASE WHEN @CarryingAmount > @RecoverableAmount
             THEN @CarryingAmount - @RecoverableAmount
             ELSE 0 END

    -- Record test
    INSERT INTO TS085S2 (...)
    VALUES (...)

    -- Generate user elimination if impairment required
    IF @ImpairmentRequired > 0
    BEGIN
        EXEC P_CONSO_CREATE_IMPAIRMENT_ELIMINATION
            @ConsoID = @ConsoID,
            @CGUID = @CGUID,
            @Amount = @ImpairmentRequired
    END
END
```

### Phase 4: UI Workflow

Impairment Testing screen:
1. Select CGU
2. Enter carrying amount (or auto-calculate from consolidation)
3. Input VIU assumptions or value
4. Input FVLCD or value
5. System calculates impairment
6. Approval workflow
7. Auto-create elimination entry
8. Generate test documentation report

## API Reference

### Primary API Handlers
| Handler | YAML File | Purpose | Status |
|---------|-----------|---------|--------|
| `Report_ExecuteReport` | [api-reports-endpoints.yaml](../11-agent-support/api-reports-endpoints.yaml) | Execute P_REPORT_GOODWILL (display only) | ✅ IMPLEMENTED |
| `Journal_SaveJournal` | [api-adjustment-endpoints.yaml](../11-agent-support/api-adjustment-endpoints.yaml) | Book impairment loss (manual) | ✅ IMPLEMENTED |

### Supporting API Handlers
| Handler | YAML File | Purpose |
|---------|-----------|---------|
| `Elimination_GetEliminations` | [api-elimination-endpoints.yaml](../11-agent-support/api-elimination-endpoints.yaml) | Get impairment eliminations |
| `Company_GetCompanies` | [api-company-endpoints.yaml](../11-agent-support/api-company-endpoints.yaml) | Get companies with goodwill |

### API Workflow
```
Impairment Testing via API (Manual Process):

1. Report_ExecuteReport (GoodwillReport) → Get current goodwill positions
2. EXTERNAL: Calculate VIU and FVLCD in Excel/valuation tool
3. EXTERNAL: Determine impairment amount
4. Journal_SaveJournal → Book impairment via user elimination:
   Dr  Impairment Loss (P&L)
   Cr  Goodwill (B/S)
5. Elimination_GetEliminations → Verify impairment recorded
```

### Implementation Status
| Feature | Status | Gap Reference |
|---------|--------|---------------|
| Goodwill display | ✅ IMPLEMENTED | P_REPORT_GOODWILL |
| Manual impairment entry | ✅ IMPLEMENTED | User eliminations |
| CGU definition | ❌ NOT_IMPLEMENTED | Severity 8, IAS 36 |
| Automated testing | ❌ NOT_IMPLEMENTED | Manual only |
| VIU calculation | ❌ NOT_IMPLEMENTED | External |
| Reversal prevention | ❌ NOT_IMPLEMENTED | Manual discipline |

### Related API Documentation
- [API Index](../11-agent-support/api-index.yaml) - Master handler catalog
- [Gap Analysis](../11-agent-support/gap-analysis-report.yaml) - **NOT_IMPLEMENTED (Severity 8)**

---

## Related Documentation

- [Goodwill Calculation](goodwill-calculation.md) - Initial goodwill recognition
- [Participation Eliminations](../04-elimination-entries/participation-eliminations.md) - Investment elimination
- [User-Defined Eliminations](../04-elimination-entries/user-eliminations.md) - Manual adjustments
- [Flow Management](flow-management.md) - Impairment flow tracking

### Related Knowledge Chunks
- Chunk 0041: Technical adjustments including impairment
- Chunk 0731: Goodwill transfer and impairment considerations
- IAS 36: Impairment of Assets (external reference)

---
*Document 29 of 50+ | Batch 10: Remaining Severity 8 Gaps | Last Updated: 2024-12-01*
*GAP STATUS: CONFIRMED - NOT_IMPLEMENTED (Severity 8) - Manual process only*
