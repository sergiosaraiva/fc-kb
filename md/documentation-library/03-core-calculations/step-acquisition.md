# Step Acquisition: Successive Purchase Accounting

## Document Metadata
- **Category**: Core Calculations
- **Theory Source**: Knowledge base chunks: 0006, 0197, 0428, 0471, 1060
- **Implementation Files**:
  - `Sigma.Database/dbo/Tables/TS014C0.sql` - ConsoMethod tracking, FlagEnteringScope
  - `Sigma.Database/dbo/Tables/TS011C0.sql` - VarConsoMeth_XX special flows
  - `Sigma.Database/dbo/Stored Procedures/P_CONSO_ELIM_CHANGE_METHOD.sql` - **S072 elimination** (method change flow reclassification)
  - `Sigma.Database/dbo/Stored Procedures/P_CONSO_ELIM_USER.sql` - Method change selection (IDs 15-18)
  - `Sigma.Database/dbo/Stored Procedures/P_CALC_OWNERSHIP_INDIRECT_PERCENTAGES.sql` - Percentage recalculation
- **Last Updated**: 2024-12-01 (Enhanced with S072 elimination details)
- **Completeness**: 50% (Method change flows + S072 flow reclassification documented; goodwill remeasurement not automated)
- **Compliance Status**: IFRS 3 - Business Combinations (Partial)

## Executive Summary

Step acquisition (successive purchase, piecemeal acquisition) occurs when control is achieved through multiple transactions over time, transitioning from non-controlling investment to controlling interest. IFRS 3 requires that upon achieving control, the previously held equity interest be remeasured at acquisition-date fair value, with any resulting gain/loss recognized in profit or loss. Prophix.Conso provides **partial support**: method change flows (VarConsoMeth_EG, VarConsoMeth_PG) exist to capture the impact, and company selection methods can target method-changing companies. However, the **automatic goodwill calculation** and **fair value remeasurement** at the step-up date require **manual configuration**.

## Theoretical Framework

### Concept Definition

Step acquisition accounting addresses the transition from:
- **Equity Method (E)** → **Global Integration (G)**: Gaining control over previously associated company
- **Proportional (P)** → **Global (G)**: JV becomes subsidiary
- **Non-consolidated (N)** → **Global (G)**: Investment becomes controlling

### IFRS 3 Requirements

When control is obtained in stages:

1. **Remeasure Previously Held Interest**
   - Fair value at acquisition date
   - Recognize gain/loss in P&L

2. **Calculate Goodwill**
   - Consideration transferred (new purchase)
   - Plus: Fair value of previously held interest
   - Plus: Non-controlling interest (at FV or proportionate share)
   - Less: Net identifiable assets acquired

3. **Discontinue Equity Method**
   - Stop one-line consolidation
   - Begin full consolidation of assets/liabilities

### Step Acquisition Formula

```
Goodwill = (Cash paid for additional shares)
         + (Fair value of previously held equity interest)
         + (NCI at fair value or proportionate net assets)
         - (Fair value of identifiable net assets)

Gain/Loss on Step-up = Fair value of old interest - Book value of old interest
```

### Example Scenario (from Chunk 428)

```
Year 1: P owns 80% of A, A owns 60% of B
        P's indirect control of B = 80% × 60% = 48%

Year 2: P acquires additional 10% of A (now 90%)
        P's indirect control of B = 90% × 60% = 54%

Step Acquisition Impact:
- Minority interests in A reduced from 20% to 10%
- P's indirect control of B increases by 6%
- Potential goodwill on additional A acquisition
- May trigger step acquisition accounting
```

### Method Change Scenarios

| From | To | Scenario | Key Accounting |
|------|-----|----------|----------------|
| E (20-50%) | G (>50%) | Gain control of associate | Remeasure + new goodwill |
| P (50% joint) | G (>50%) | JV becomes subsidiary | Remeasure + new goodwill |
| N (<20%) | G (>50%) | Investment to control | Standard acquisition |
| G (>50%) | E (20-50%) | Lose control, retain influence | Deconsolidation + fair value |

## Current Implementation

### Method Change Detection

**TS014C0 - ConsoMethod Tracking**

```sql
-- Consolidation method values
CONSTRAINT [CK_TS014C0_CONSOMETHOD]
CHECK ([ConsoMethod]='P' OR [ConsoMethod]='G' OR [ConsoMethod]='N'
    OR [ConsoMethod]='E' OR [ConsoMethod]='S' OR [ConsoMethod]='T' OR [ConsoMethod]='X')
```

The system compares ConsoMethod between current and reference period to detect changes.

### Special Flows for Method Changes

From `TS011C1` (special flow codes), six directional method change flows exist:

| SpecFlowCode | Description | Transition |
|--------------|-------------|------------|
| VarConsoMeth_GE | Variation G→E | Lose control, retain significant influence |
| VarConsoMeth_EG | Variation E→G | **Step acquisition** - gain control |
| VarConsoMeth_PE | Variation P→E | JV loses joint control |
| VarConsoMeth_EP | Variation E→P | Associate gains joint control |
| VarConsoMeth_PG | Variation P→G | **Step acquisition** - JV to subsidiary |
| VarConsoMeth_GP | Variation G→P | Lose exclusive, retain joint control |

### S072 Elimination - Method Change Flow Reclassification

**P_CONSO_ELIM_CHANGE_METHOD.sql** handles flow reclassification when consolidation method changes:

```sql
-- S072 Elimination: Reclassification of opening flows on method change
-- Supported transitions (from procedure header):

-- Not Conso → Conso
--   N → E  |
--   N → P  | => @PreviousPeriodAdjFlowID → @VarPercIntegFlowID
--   N → G  |

-- Change Method
--   E → P  | => @PreviousPeriodAdjFlowID → @VarPercIntegFlowID
--   E → G  |

--   P → G  | => @PreviousPeriodAdjFlowID → @VarPercIntegFlowID * %i
--   P → E  |

--   G → E  | => @PreviousPeriodAdjFlowID → @VarPercIntegFlowID * -1
--   G → P  | => @PreviousPeriodAdjFlowID → @VarPercIntegFlowID * -1 * %i
```

**Important**: This procedure handles **flow reclassification only**. It does NOT:
- Recalculate goodwill at step acquisition date
- Perform fair value remeasurement of previously held interest
- Generate gain/loss on step-up

*Verified in Gap Deep Verification Iteration 2 (2024-12-01)*

### Company Selection for Method Changes

`P_CONSO_ELIM_USER.sql` provides selection methods targeting method-changing companies:

```sql
-- Selection IDs for scope changes (from TS070S1)
-- 8 = FlagEnteringScope = 1 (entering companies)
-- 9 = FlagLeavingScope = 1 (leaving companies)

-- Additional selection IDs:
-- 15 = All entering companies
-- 16 = All leaving companies
-- 17 = All entering partners
-- 18 = All leaving partners
```

### Percentage Recalculation

`P_CALC_OWNERSHIP_INDIRECT_PERCENTAGES.sql` recalculates percentages when ownership changes:

```sql
-- Consolidation method is updated based on new control percentage
If @UpdateConsoMethod = 1
Begin
    Update #Companies
        Set ConsoMethod =
            Case
                When ( GroupCtrlPerc > @ConsoMethP OR CompanyID = @ParentID ) then 'G'
                When ( GroupCtrlPerc = @ConsoMethP AND CompanyID <> @ParentID )  then 'P'
                When ( GroupCtrlPerc >= @ConsoMethN AND  GroupCtrlPerc < @ConsoMethP ) then 'E'
                When ( GroupCtrlPerc < @ConsoMethN ) then 'N'
                Else 'N'
            End
End
```

**Thresholds**:
- `@ConsoMethP = 50` (50% = Proportional boundary)
- `@ConsoMethN = 20` (20% = Not consolidated boundary)

## Gap Analysis

### Gap Status: CONFIRMED - NOT_IMPLEMENTED (Severity 8)

**What's Missing**:

1. **Automatic Goodwill Recalculation on Step-Up**
   - System doesn't automatically recalculate goodwill when method changes E→G or P→G
   - User must manually calculate and enter via user elimination

2. **Fair Value Remeasurement**
   - No mechanism to capture fair value of previously held interest
   - No automatic gain/loss calculation on step-up

3. **Historical Cost Tracking**
   - Book value of prior investment not separately tracked
   - Comparison to fair value requires manual lookup

4. **Step Acquisition Date Tracking**
   - No specific field for the date control was achieved
   - Only period-level method changes detected

5. **Partial Period P&L Allocation**
   - When control gained mid-period, P&L should be prorated
   - No automatic cut-off mechanism

6. **NCI Fair Value Option**
   - IFRS allows NCI at fair value or proportionate share
   - No systematic choice mechanism

### What IS Available

| Capability | Implementation | Status |
|------------|----------------|--------|
| Method change detection | Period comparison of ConsoMethod | **Available** |
| Method change flows | VarConsoMeth_XX special flows | **Available** |
| Target method-changing companies | Selection IDs 15-18 | **Available** |
| Percentage recalculation | P_CALC_OWNERSHIP_INDIRECT_PERCENTAGES | **Available** |
| User elimination framework | TS070S0/TS071S0 for manual adjustments | **Available** |

## Manual Workaround

### Step Acquisition Process

**Step 1: Update Ownership Data**

```sql
-- Update shares owned in TS015S0
UPDATE TS015S0
SET NbrFinRights = @NewSharesOwned,
    FinPercentage = @NewFinPercentage,
    NbrVotingRights = @NewVotesOwned,
    CtrlPercentage = @NewCtrlPercentage
WHERE ConsoID = @ConsoID
  AND CompanyID = @ParentID
  AND CompanyOwnedID = @AcquiredCompanyID;
```

**Step 2: Recalculate Percentages**

```sql
EXEC [dbo].[P_CALC_OWNERSHIP_INDIRECT_PERCENTAGES]
    @ConsoID = @ConsoID,
    @CustomerID = @CustomerID,
    @ParentID = @ParentID,
    @UpdateConsoMethod = 1,  -- Allow method to change
    @UseSessionTable = 0,
    @Debug = 0;
```

**Step 3: Manual Goodwill Calculation**

Calculate externally:
```
New Goodwill = Consideration (all tranches)
             + FV of previously held interest
             + NCI (at chosen measurement basis)
             - FV of net identifiable assets
```

**Step 4: Create User Elimination for Step-Up Adjustment**

```sql
-- Header
INSERT INTO TS070S0 (ConsoID, ElimCode, ElimType, ElimText, Active,
                     ConsoMethodSelectionID, JournalTypeID, ...)
VALUES (@ConsoID, 'U020', 'U', 'Step Acquisition - E to G', 1,
        15, @JournalID, ...);  -- SelectionID 15 = Entering companies

-- Line 1: Recognize gain on remeasurement
INSERT INTO TS071S0 (EliminationHeaderID, LineNr,
    FromType, FromAccountID, FromPeriod,
    ToAccountID, ToSign, Percentage)
VALUES (@HeaderID, 1,
    1, @EquityInvestmentAccount, 'C',  -- Old equity method balance
    @GainOnStepUpAccount, 1, 1);       -- Credit P&L

-- Line 2: Record new goodwill
INSERT INTO TS071S0 (...)
VALUES (@HeaderID, 2,
    1, @GoodwillSourceAccount, 'C',
    @GoodwillAccount, 1, 1);
```

**Step 5: Run Consolidation**

The VarConsoMeth_EG flow will automatically capture method change impact in equity reconciliation.

## Recommended Implementation

### Phase 1: Step Acquisition Event Type

```sql
-- Add to TS080S0 (Event Types)
INSERT INTO TS080S0 (EventTypeCode, EventTypeDescription)
VALUES ('STEP_ACQ', 'Step Acquisition - Control Achieved');

-- Add fields to track
ALTER TABLE TS014C0 ADD
    StepAcquisitionDate DATE NULL,
    PriorMethodBookValue DECIMAL(28,6) NULL,
    AcquisitionFairValue DECIMAL(28,6) NULL;
```

### Phase 2: Automatic Goodwill Procedure

```sql
CREATE PROCEDURE P_CONSO_STEP_ACQUISITION
    @ConsoID INT,
    @CompanyID INT,  -- Company that changed method
    @PriorMethod CHAR(1),  -- E or P
    @NewMethod CHAR(1),    -- G
    @FairValueOfOldInterest DECIMAL(28,6),
    @ConsiderationPaid DECIMAL(28,6),
    @NCIMethod CHAR(1)  -- 'F' = Fair Value, 'P' = Proportionate
AS
BEGIN
    -- Calculate goodwill
    -- Record remeasurement gain/loss
    -- Create elimination entries
END
```

### Phase 3: UI Enhancement

Add step acquisition wizard:
1. Select company that achieved control
2. Enter fair value of prior interest
3. Enter consideration for additional shares
4. Select NCI measurement method
5. System calculates goodwill and gain/loss

## Appendix: Comprehensive Step Acquisition Examples

### Example 1: Equity Method to Global Integration (E → G)

**Scenario**: Parent P acquires control of Associate A through a second purchase

**Timeline**:
```
Year 1 (Initial Investment):
  P acquires 30% of A for 900
  A's net assets: 2,000
  A consolidated using Equity Method (E)

Year 3 (Step Acquisition):
  P acquires additional 35% of A for 1,400
  P now owns 65% → changes to Global Integration (G)
  A's net assets at step-up: 2,800
  Fair value of A's net assets: 3,200
  Fair value of P's original 30%: 1,100
```

**Step 1: Determine Book Value of Original 30% Interest**

```
Original cost:                                    900
Add: Share of A's profits (Years 1-3):
     30% × (2,800 - 2,000) = 30% × 800 =         240
Less: Dividends received:                        (80)
                                               ------
Equity method carrying value at step-up:       1,060
```

**Step 2: Calculate Gain/Loss on Remeasurement**

```
Fair value of original 30% interest:           1,100
Less: Book value (equity method):             (1,060)
                                               ------
Gain on remeasurement (P&L):                      40
```

**Step 3: Calculate Goodwill at Step Acquisition Date**

```
Consideration transferred:
  - Cash for additional 35%:                   1,400
  - Fair value of previously held 30%:         1,100
                                               ------
  Total consideration:                         2,500

Plus: NCI at fair value (35% × FV of A):
  35% × 3,200 =                                1,120
                                               ------
Total:                                         3,620

Less: Fair value of net identifiable assets:  (3,200)
                                               ------
Goodwill on step acquisition:                    420
```

**Step 4: Summary of Accounting Entries**

| Entry | Debit | Credit | Amount |
|-------|-------|--------|--------|
| Remeasure old interest | Investment in A | | 40 |
| | | Gain on step-up (P&L) | 40 |
| Record new goodwill | Goodwill | | 420 |
| | | Various (goodwill calculation) | 420 |
| Recognize NCI | | NCI (equity) | 1,120 |

**Step 5: Implementation in Prophix.Conso**

```sql
-- Step 5a: Update ownership data
UPDATE TS015S0
SET FinPercentage = 65.00,
    CtrlPercentage = 65.00,
    NbrFinRights = @NewTotalShares
WHERE ConsoID = @ConsoID
  AND CompanyID = @ParentID
  AND CompanyOwnedID = @CompanyAID;

-- Step 5b: Run percentage recalculation (method will change E→G)
EXEC [dbo].[P_CALC_OWNERSHIP_INDIRECT_PERCENTAGES]
    @ConsoID = @ConsoID,
    @CustomerID = @CustomerID,
    @ParentID = @ParentID,
    @UpdateConsoMethod = 1;

-- Step 5c: Create user elimination for remeasurement gain
INSERT INTO TS070S0 (ConsoID, ElimCode, ElimType, ElimText, Active,
                     ConsoMethodSelectionID, JournalTypeID, ...)
VALUES (@ConsoID, 'U021', 'U',
    'Step Acq - A - E→G - Remeasure gain 40 - IFRS 3.42', 1, 15, @JournalID, ...);

-- Step 5d: Elimination detail - gain on remeasurement
INSERT INTO TS071S0 (EliminationHeaderID, LineNr,
    FromType, FromAccountID, ToAccountID, ToSign, ...)
VALUES (@HeaderID, 1,
    1, @EquityMethodInvestment, @GainOnStepUpPL, 1, ...);
-- Manual amount: 40

-- Step 5e: Create user elimination for goodwill
INSERT INTO TS070S0 (ConsoID, ElimCode, ElimType, ElimText, Active, ...)
VALUES (@ConsoID, 'U022', 'U',
    'Step Acq - A - Goodwill 420 - Ref: STEP-2024-001', 1, ...);

INSERT INTO TS071S0 (EliminationHeaderID, LineNr,
    FromType, FromAccountID, ToAccountID, ToSign, ...)
VALUES (@HeaderID, 1,
    1, @PlaceholderAccount, @GoodwillAccount, 1, ...);
-- Manual amount: 420
```

**Step 6: Verify with S072 Flow Reclassification**

The system automatically runs S072 elimination which reclassifies opening flows:
```
VarConsoMeth_EG flow captures:
  - Prior equity method reserves moving to full consolidation
  - Transition impact on equity reconciliation
```

### Example 2: Proportional to Global Integration (P → G)

**Scenario**: P increases stake in Joint Venture B from 50% to 75%

**Before**:
```
P owns 50% of B (Proportional Method - P)
B's net assets: 4,000
B consolidated at 50% = 2,000 integrated
```

**After Step Acquisition**:
```
P acquires additional 25% for 1,200
P now owns 75% → Global Integration (G)
Fair value of B's net assets: 4,400
Fair value of P's original 50%: 2,300
```

**Step 1: Book Value of Original 50%**

```
Under proportional method, P consolidated 50% of B's net assets:
  50% × 4,000 = 2,000

But for step acquisition, we need the investment value:
Original cost + share of post-acquisition profits
Assume: Original cost 1,800 + profits 200 = 2,000
```

**Step 2: Gain on Remeasurement**

```
Fair value of original 50%:                    2,300
Less: Book value:                             (2,000)
                                               ------
Gain on remeasurement (P&L):                     300
```

**Step 3: Goodwill Calculation**

```
Consideration:
  - Cash for additional 25%:                   1,200
  - FV of previously held 50%:                 2,300
  Total:                                       3,500

Plus: NCI (25% × 4,400):                       1,100
                                               ------
Total:                                         4,600

Less: FV of net assets:                       (4,400)
                                               ------
Goodwill:                                        200
```

**Step 4: Key Differences from E→G**

| Aspect | E→G | P→G |
|--------|-----|-----|
| Prior consolidation | One-line equity pickup | 50% line-by-line |
| Flow reclassification | Full opening to VarConsoMeth_EG | 50% delta via VarConsoMeth_PG |
| S072 multiplier | ×1 | ×%i (integration percentage) |

### Example 3: Multi-Tier Step Acquisition

**Scenario**: P gains control of B indirectly through increased ownership in A

**Structure Before**:
```
P owns 70% of A (G)
A owns 45% of B (E - equity method at A level)
P's indirect % in B = 70% × 45% = 31.5%
B consolidated via A's equity method
```

**Change**: A acquires additional 15% of B

**Structure After**:
```
P owns 70% of A (G)
A owns 60% of B (G - now full consolidation at A level)
P's indirect % in B = 70% × 60% = 42%
B now fully consolidated through A
```

**Key Accounting Points**:

1. **At A's Level**:
   - A recognizes step acquisition accounting
   - A calculates goodwill on B
   - A records gain/loss on remeasurement of original 45%

2. **At Group Level**:
   - P consolidates A which now consolidates B
   - Minority interest in B = (1 - 42%) = 58%
   - Goodwill on B flows through A's consolidation

3. **System Behavior**:
   ```sql
   -- B's method changes E→G at A's perspective
   -- S072 runs for A→B relationship
   -- VarConsoMeth_EG flow captures transition

   -- P_CALC_OWNERSHIP_INDIRECT_PERCENTAGES recalculates:
   -- P's indirect % in B changes from 31.5% to 42%
   ```

### Step Acquisition Checklist

| Step | Action | System Support | Manual Required |
|------|--------|----------------|-----------------|
| 1 | Identify method change trigger | Auto-detected | - |
| 2 | Determine step-up date | Period-level only | Exact date |
| 3 | Calculate book value of old interest | - | Yes |
| 4 | Determine fair value of old interest | - | Yes |
| 5 | Calculate remeasurement gain/loss | - | Yes |
| 6 | Determine FV of net identifiable assets | - | Yes |
| 7 | Calculate goodwill | - | Yes |
| 8 | Determine NCI measurement basis | - | Yes |
| 9 | Update ownership percentages | P_CALC_OWNERSHIP_INDIRECT_PERCENTAGES | - |
| 10 | Create remeasurement elimination | User elimination framework | Entry |
| 11 | Create goodwill elimination | User elimination framework | Entry |
| 12 | Verify flow reclassification | S072 automatic | Review |

### Decision Tree: Step Acquisition Scenarios

```
                    ┌─────────────────────────────────┐
                    │   Ownership % Increased?         │
                    └─────────────────────────────────┘
                                   │
                    ┌──────────────┴──────────────┐
                    │                             │
               Yes (crossing                  No (within
               control threshold)             same method)
                    │                             │
                    ▼                             ▼
          ┌─────────────────┐           ┌─────────────────┐
          │ STEP ACQUISITION │           │ EQUITY          │
          │ ACCOUNTING       │           │ TRANSACTION     │
          └─────────────────┘           │ (within equity) │
                    │                   └─────────────────┘
        ┌───────────┴───────────┐
        │                       │
   From E or P              From N
        │                       │
        ▼                       ▼
┌──────────────────┐    ┌──────────────────┐
│ Remeasure prior  │    │ Standard         │
│ interest at FV   │    │ acquisition      │
│ Gain/loss to P&L │    │ accounting       │
└──────────────────┘    └──────────────────┘
        │                       │
        └───────────┬───────────┘
                    │
                    ▼
          ┌─────────────────┐
          │ Calculate       │
          │ Goodwill        │
          │ (Total FV basis)│
          └─────────────────┘
```

### Common Pitfalls and Solutions

| Pitfall | Issue | Solution |
|---------|-------|----------|
| Wrong book value | Using cost instead of equity-adjusted value | Track cumulative equity pickups |
| Missing FV adjustments | Not adjusting net assets to FV | Perform full PPA at step-up |
| Incorrect NCI | Using proportionate when FV chosen | Document NCI policy choice |
| Flow timing | Mixing pre/post step-up flows | Use period-specific eliminations |
| Goodwill double-count | Adding old goodwill to new | Replace, don't add |

## API Reference

### Primary API Handlers
| Handler | YAML File | Purpose | Status |
|---------|-----------|---------|--------|
| `Consolidation_Execute` | [api-consolidation-endpoints.yaml](../11-agent-support/api-consolidation-endpoints.yaml) | Execute S072 method change | ✅ IMPLEMENTED |
| `Ownership_SaveOwnership` | [api-ownership-endpoints.yaml](../11-agent-support/api-ownership-endpoints.yaml) | Update ownership percentages | ✅ IMPLEMENTED |
| `LaunchCalculateIndirectPercentagesJob` | [api-ownership-endpoints.yaml](../11-agent-support/api-ownership-endpoints.yaml) | Recalculate after ownership change | ✅ IMPLEMENTED |

### Supporting API Handlers
| Handler | YAML File | Purpose |
|---------|-----------|---------|
| `Journal_SaveJournal` | [api-adjustment-endpoints.yaml](../11-agent-support/api-adjustment-endpoints.yaml) | Book manual goodwill adjustment |
| `Report_ExecuteReport` | [api-reports-endpoints.yaml](../11-agent-support/api-reports-endpoints.yaml) | Generate goodwill report |
| `Company_GetCompanies` | [api-company-endpoints.yaml](../11-agent-support/api-company-endpoints.yaml) | Get companies with method changes |

### API Workflow
```
1. Ownership_SaveOwnership → Update shares (trigger method change)
2. LaunchCalculateIndirectPercentagesJob → Recalculate percentages
   → ConsoMethod auto-updates based on thresholds
3. Journal_SaveJournal → Book remeasurement gain/loss (manual)
4. Journal_SaveJournal → Book new goodwill (manual)
5. Consolidation_Execute → S072 reclassifies opening flows
6. Report_ExecuteReport (GoodwillReport) → Verify goodwill
```

### Implementation Status
| Feature | Status | Gap Reference |
|---------|--------|---------------|
| Method change detection | ✅ IMPLEMENTED | - |
| S072 flow reclassification | ✅ IMPLEMENTED | P_CONSO_ELIM_CHANGE_METHOD |
| VarConsoMeth_XX flows | ✅ IMPLEMENTED | TS011C1 |
| Automatic goodwill recalc | ❌ NOT_IMPLEMENTED | Severity 8, IFRS 3 |
| FV remeasurement | ❌ NOT_IMPLEMENTED | Severity 8, IFRS 3 |

### Related API Documentation
- [API Index](../11-agent-support/api-index.yaml) - Master handler catalog
- [Gap Analysis](../11-agent-support/gap-analysis-report.yaml) - **PARTIAL (50%)** - Framework exists, manual calculation required

---

## See Also

### Related Core Calculations
- [Goodwill Calculation](goodwill-calculation.md) - Standard goodwill methodology
- [Scope Changes](scope-changes.md) - Entry/exit detection
- [Deconsolidation](deconsolidation.md) - Reverse scenario (lose control)
- [Flow Management](flow-management.md) - VarConsoMeth_XX flows

### Related Consolidation Methods
- [Equity Method](../02-consolidation-methods/equity-method.md) - Pre-control accounting (E→G)
- [Proportional Method](../02-consolidation-methods/proportional-method.md) - JV transitions (P→G)
- [Method Determination](../02-consolidation-methods/consolidation-method-determination.md) - Threshold assignment

### Related Eliminations
- [User Eliminations](../04-elimination-entries/user-eliminations.md) - Manual goodwill entries
- [Participation Eliminations](../04-elimination-entries/participation-eliminations.md) - Investment elimination

### Technical References
- Knowledge Base: Chunks 0197, 0428, 0471, 1060
- Code: `P_CONSO_ELIM_CHANGE_METHOD.sql` (S072)

### Navigation
- [Cross-Reference Index](../00-index/CROSS_REFERENCE_INDEX.md) - Full document relationships
- [Missing Features](../10-gap-analysis/missing-features.md) - Gap status

---
*Document 27 of 50+ | Batch 9: High Priority Gap Analysis | Last Updated: 2024-12-02 (Enhanced with comprehensive step-up examples)*
*GAP STATUS: CONFIRMED - PARTIAL (Severity 8) - Framework exists, manual calculation required*
