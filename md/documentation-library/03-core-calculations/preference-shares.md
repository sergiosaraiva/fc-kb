# Preference Shares: Multiple Share Classes in Consolidation

## Document Metadata
- **Category**: Core Calculations
- **Theory Source**: Knowledge base chunks: 0016, 0510, 0653, 1264
- **Implementation Files**:
  - `Sigma.Database/dbo/Tables/TS015S0.sql` - Ownership structure (NbrFinRights, NbrVotingRights)
  - `Sigma.Database/dbo/Tables/TS014C0.sql` - Company percentage storage
  - `Sigma.Database/dbo/Stored Procedures/P_CALC_OWNERSHIP_INDIRECT_PERCENTAGES.sql` - Single class calculation
- **Last Updated**: 2024-12-02 (Enhanced with visual diagram, implementation checklist, and validation queries)
- **Completeness**: 70% (Single share class only; comprehensive workarounds and decision framework documented)
- **Compliance Status**: IAS 32/IFRS 9 - Partial (manual adjustments required)

## Executive Summary

Preference shares (preferred stock, privileged shares) are equity instruments with preferential rights over ordinary shares, typically including cumulative dividends, liquidation preference, or conversion rights. Allen White's "Direct Consolidation" (Chunk 653) illustrates scenarios where companies have multiple share classes with different dividend entitlements. Prophix.Conso's current implementation supports **single share class percentages only** - there is no mechanism to track multiple share classes with different financial and voting characteristics within the same company.

### Visual: Preference Share Consolidation Decision Framework

```
┌─────────────────────────────────────────────────────────────────────────────┐
│               PREFERENCE SHARE CONSOLIDATION DECISION TREE                   │
└─────────────────────────────────────────────────────────────────────────────┘

  STEP 1: IDENTIFY SHARE CLASSES              STEP 2: DETERMINE ECONOMIC RIGHTS
  ───────────────────────────────             ─────────────────────────────────

  ┌─────────────────────────────┐             ┌─────────────────────────────────┐
  │ Company has multiple share  │             │ For each share class:           │
  │ classes?                    │             │ • Dividend priority order       │
  │                             │             │ • Cumulative or non-cumulative  │
  │   Ordinary ───────► Class 1 │             │ • Participating rights          │
  │   Preference A ───► Class 2 │             │ • Liquidation preference        │
  │   Preference B ───► Class 3 │             │ • Voting rights per share       │
  └─────────────────────────────┘             └─────────────────────────────────┘
           │                                              │
           ▼                                              ▼
  STEP 3: CALCULATE ECONOMIC %                STEP 4: SELECT WORKAROUND METHOD
  ────────────────────────────                ─────────────────────────────────

  ┌─────────────────────────────┐             ┌─────────────────────────────────┐
  │ Example: Dividends = 200    │             │   ┌─────────────────────┐       │
  │                             │             │   │ Simple scenario?    │       │
  │ Preference (5% cumul): 50   │             │   │ (1-2 classes, basic │       │
  │   Parent 40%:  20           │             │   │  cumulative pref)   │       │
  │   NCI 60%:     30           │             │   └──────────┬──────────┘       │
  │                             │             │         YES  │   NO             │
  │ Ordinary remaining: 150     │             │              ▼                  │
  │   Parent 70%: 105           │             │   ┌─────────────────────┐       │
  │   NCI 30%:     45           │             │   │ Method A:           │       │
  │                             │             │   │ Adjusted % in       │──►    │
  │ TOTAL Parent: 125 (62.5%)   │             │   │ TS015S0             │       │
  │ TOTAL NCI:     75 (37.5%)   │             │   └─────────────────────┘       │
  └─────────────────────────────┘             │              │ NO               │
                                              │              ▼                  │
                                              │   ┌─────────────────────┐       │
                                              │   │ Complex structure?  │       │
                                              │   │ Multiple classes,   │       │
                                              │   │ participating       │       │
                                              │   └──────────┬──────────┘       │
                                              │         YES  │   NO             │
                                              │              ▼                  │
                                              │   ┌─────────────────────┐       │
                                              │   │ Method B:           │       │
                                              │   │ Virtual Entity per  │──►    │
                                              │   │ Share Class         │       │
                                              │   └─────────────────────┘       │
                                              └─────────────────────────────────┘

  PROPHIX.CONSO LIMITATION:
  ┌─────────────────────────────────────────────────────────────────────────────┐
  │ ⚠️ TS015S0 stores SINGLE FinPercentage and CtrlPercentage per owner/owned  │
  │    - No ShareClassID column                                                 │
  │    - No DividendPriority field                                             │
  │    - Cannot track class-level ownership directly                            │
  │                                                                             │
  │ WORKAROUND OPTIONS:                                                         │
  │ ┌─────────────────┬────────────────────┬─────────────────────────────────┐ │
  │ │ Method          │ When to Use        │ System Configuration            │ │
  │ ├─────────────────┼────────────────────┼─────────────────────────────────┤ │
  │ │ A. Adjusted %   │ Simple cumulative  │ Calculate economic %, enter in  │ │
  │ │                 │ preference         │ FinPercentage field directly    │ │
  │ ├─────────────────┼────────────────────┼─────────────────────────────────┤ │
  │ │ B. Virtual      │ Complex, multi-    │ Create separate company codes   │ │
  │ │    Entity       │ class structures   │ for each share class            │ │
  │ ├─────────────────┼────────────────────┼─────────────────────────────────┤ │
  │ │ C. User Elim    │ Annual dividend    │ TS070S0/TS071S0 adjustment to   │ │
  │ │                 │ adjustments only   │ reallocate MI after std calc    │ │
  │ └─────────────────┴────────────────────┴─────────────────────────────────┘ │
  └─────────────────────────────────────────────────────────────────────────────┘
```

## Theoretical Framework

### Concept Definition

From Allen White's "Direct Consolidation" (Chunk 653):

> "Consider a company with two categories of shares:
> - Ordinary shares: 1,000 shares
> - Privileged shares: 1,000 shares with 5% cumulative dividend on capital
>
> The privileged shares receive priority dividend before ordinary shares participate."

### Types of Preference Shares

| Type | Description | Consolidation Impact |
|------|-------------|---------------------|
| **Cumulative Dividend** | Dividends accumulate if not paid | Affects distributable reserves allocation |
| **Participating** | Share in excess profits after preference dividend | Complex percentage calculation |
| **Convertible** | Can convert to ordinary shares | Potential voting rights consideration |
| **Redeemable** | Company can buy back at set price | May be classified as liability (IAS 32) |
| **Non-voting** | No voting rights attached | Different control vs financial percentage |

### Impact on Percentage Calculations

**Example from Chunk 653**:

```
Company Structure:
- 1,000 Ordinary shares
- 1,000 Privileged shares (5% cumulative dividend)

Ownership:
- Parent owns 600 ordinary + 400 privileged = 50% of total shares
- BUT economic entitlement differs based on profit distribution

Scenario: Total dividends = 100
- Privileged dividend first: 50 (5% of assumed 1,000 capital)
- Remaining for ordinary: 50
- Parent's share: (400/2000 × 50) + (600/1000 × 50) = 10 + 30 = 40 (not 50)
```

### IAS 32 Classification

Preference shares may be classified as:
1. **Equity**: Discretionary dividends, no redemption obligation
2. **Liability**: Mandatory redemption or cumulative dividends creating obligation
3. **Compound Instrument**: Convertible preference shares

Classification affects consolidation treatment - liabilities don't contribute to equity.

### Financial vs Voting Rights Divergence

```
Scenario: Dual-class shares
- Class A: 1 share = 10 votes (founder class)
- Class B: 1 share = 1 vote (ordinary)

Parent owns:
- 100% of Class A (1,000 shares, 10,000 votes)
- 20% of Class B (200 shares, 200 votes)
- Total shares: 1,200/6,000 = 20%
- Total votes: 10,200/11,000 = 93%

Control: 93% (G method)
Financial interest: 20%
```

## Current Implementation

### Single Share Class Model

**TS015S0 - Ownership Structure**

```sql
CREATE TABLE [dbo].[TS015S0] (
    [ConsoID]           INT NOT NULL,
    [CompanyID]         INT NOT NULL,      -- Owner
    [CompanyOwnedID]    INT NOT NULL,      -- Owned
    [FinPercentage]     DECIMAL(20,16),    -- Financial %
    [CtrlPercentage]    DECIMAL(20,16),    -- Control/Voting %
    [NbrFinRights]      BIGINT,            -- Total financial shares
    [NbrVotingRights]   BIGINT             -- Total voting shares
    -- NO ShareClassID field
    -- NO DividendPriority field
);
```

**Key Limitation**: Cannot store ownership by share class - only aggregate totals.

### Percentage Calculation Logic

`P_CALC_OWNERSHIP_INDIRECT_PERCENTAGES.sql`:

```sql
-- Percentage calculation assumes single class
Update #Companies
Set GroupPerc = ROUND(b.val * 100, 16)
From #Companies
    inner join #Matrices b
        ON (b.MatrixNo = 6 and b.Row = 1 and b.Col = #Companies.SortID)
Where #Companies.SortID <> 1

-- FinPercentage treated as uniform across all shares
-- No consideration for dividend preferences
```

### What's Available

| Capability | Implementation | Status |
|------------|----------------|--------|
| Single FinPercentage | TS015S0.FinPercentage | **Available** |
| Single CtrlPercentage | TS015S0.CtrlPercentage | **Available** |
| Vote count tracking | TS015S0.NbrVotingRights | **Available** |
| Share count tracking | TS015S0.NbrFinRights | **Available** |
| Multiple share classes | Not available | **Gap** |
| Dividend preferences | Not available | **Gap** |
| Economic entitlement calc | Not available | **Gap** |

## Gap Analysis

### Gap Status: CONFIRMED - NOT_IMPLEMENTED (Severity 8)

**What's Missing**:

1. **Share Class Tracking**
   - No table to store share class definitions
   - Cannot distinguish ordinary from preference shares
   - No class-level ownership records

2. **Dividend Priority Calculation**
   - System treats all shares equally for percentage
   - No mechanism for cumulative dividend preferences
   - Cannot allocate dividends by priority

3. **Economic Interest Calculation**
   - Financial percentage assumes pro-rata distribution
   - No adjustment for preference dividend entitlements
   - Minority interest calculation may be incorrect

4. **Liability Classification**
   - Redeemable preference shares should be classified as debt
   - No automatic reclassification mechanism
   - Manual user elimination required

5. **Conversion Rights Tracking**
   - Convertible preference shares not tracked
   - Potential voting rights not considered
   - No diluted ownership calculation

### Impact Assessment

| Scenario | Current Treatment | Correct Treatment | Risk |
|----------|-------------------|-------------------|------|
| Cumulative preference | Ignored | Allocate first | MI may be wrong |
| Non-voting preference | Same as ordinary | Exclude from control | Method may be wrong |
| Redeemable preference | Equity | Liability | B/S classification error |
| Participating preference | Pro-rata | Complex allocation | Profit split error |

## Manual Workaround

### Workaround 1: Adjusted Financial Percentage

Calculate economic entitlement manually and enter adjusted percentage:

```sql
-- Instead of:
-- FinPercentage = Shares owned / Total shares

-- Calculate:
-- FinPercentage = Economic entitlement / Total distributions

-- Example: Parent owns 600 ord + 400 pref out of 1000+1000
-- If 5% cumulative on pref capital = 50 priority
-- Economic % = (50% of pref dividend + 60% of remainder) / total

UPDATE TS015S0
SET FinPercentage = 55.0  -- Manually calculated economic %
WHERE ConsoID = @ConsoID
  AND CompanyID = @ParentID
  AND CompanyOwnedID = @SubsidiaryID;
```

### Workaround 2: User Elimination for Dividend Adjustment

```sql
-- Header: Preference Dividend Adjustment
INSERT INTO TS070S0 (ConsoID, ElimCode, ElimType, ElimText, Active,
                     ConsoMethodSelectionID, JournalTypeID, ...)
VALUES (@ConsoID, 'U025', 'U', 'Preference Dividend Adj', 1,
        4, @JournalID, ...);  -- Global only

-- Detail: Reallocate minority interest for preference dividend
INSERT INTO TS071S0 (EliminationHeaderID, LineNr,
    FromType, FromAccountID, FromPeriod,
    ToAccountID, ToSign, Percentage)
VALUES (@HeaderID, 1,
    1, @MinorityInterestReserves, 'C',
    @GroupReserves, 1, 1);  -- Transfer MI portion of preference dividend
```

### Workaround 3: Separate Entity for Share Class (Recommended)

Model each share class as a separate "virtual company" for complex scenarios:

```
Physical: Company B (1000 ord + 1000 pref)
Virtual:  Company B-ORD (ordinary class)
          Company B-PREF (preference class)

Parent owns:
- 60% of B-ORD
- 40% of B-PREF

Consolidate both virtual entities separately.
```

**Step-by-Step Implementation**:

**Step 1: Create Virtual Companies in TS014C0**
```sql
-- Original company
-- CompanyCode: 'SUBSB', CompanyName: 'Subsidiary B'

-- Create virtual ordinary class company
INSERT INTO TS014C0 (ConsoID, CompanyCode, CompanyName, ConsoMethod, ...)
VALUES (@ConsoID, 'SUBSB-ORD', 'Subsidiary B - Ordinary Shares', 'G', ...);

-- Create virtual preference class company
INSERT INTO TS014C0 (ConsoID, CompanyCode, CompanyName, ConsoMethod, ...)
VALUES (@ConsoID, 'SUBSB-PREF', 'Subsidiary B - Preference Shares', 'G', ...);
```

**Step 2: Configure Ownership Structure**
```sql
-- Parent owns 60% of ordinary class
INSERT INTO TS015S0 (ConsoID, CompanyID, CompanyOwnedID, FinPercentage, CtrlPercentage, ...)
VALUES (@ConsoID, @ParentID, @SubsBOrdID, 60.00, 100.00, ...);  -- 100% voting on ordinary

-- Parent owns 40% of preference class (no voting)
INSERT INTO TS015S0 (ConsoID, CompanyID, CompanyOwnedID, FinPercentage, CtrlPercentage, ...)
VALUES (@ConsoID, @ParentID, @SubsBPrefID, 40.00, 0.00, ...);  -- 0% voting on preference
```

**Step 3: Allocate Assets Appropriately**
```sql
-- Allocate equity capital proportionally to each class
-- SUBSB-ORD gets ordinary share capital
-- SUBSB-PREF gets preference share capital + any liquidation premium
```

**Step 4: Handle Dividend Eliminations**
```sql
-- Dividend from ordinary class entity
-- Elimination based on 60% ownership

-- Dividend from preference class entity
-- Elimination based on 40% ownership
-- Cumulative aspect handled by manual dividend timing
```

**Practical Example**:

| Entity | Capital | Ownership | Method | Dividend % |
|--------|---------|-----------|--------|------------|
| B-ORD | 500 | Parent 60% | G | 60% eliminated |
| B-PREF | 500 | Parent 40% | G | 40% eliminated |

**Advantages**:
- Full flexibility for different rights
- Standard consolidation mechanics work correctly
- Clear audit trail

**Limitations**:
- Creates extra entities in structure
- Requires careful balance sheet allocation
- Intercompany between virtual entities needs management

### Workaround 4: Combined User Elimination Approach

For simpler scenarios, use a single company with user elimination adjustments:

**Scenario**: Subsidiary B has 5% cumulative preference shares.

```sql
-- Step 1: Enter standard ownership (total shares basis)
-- FinPercentage = 50% (parent owns 50% of all shares)

-- Step 2: Create annual adjustment elimination
INSERT INTO TS070S0 (ConsoID, ElimCode, ElimType, ElimText, ...)
VALUES (@ConsoID, 'U026', 'U',
    'Preference Dividend Priority Adj - Cumulative 5% preference', ...);

-- Step 3: Detail line to reallocate
-- If preference holders get priority dividend of 25:
-- And parent holds 40% of preference shares:
-- Parent's extra share = 40% x 25 = 10 (beyond pro-rata)
-- This reduces MI allocation by 10

INSERT INTO TS071S0 (EliminationHeaderID, LineNr,
    FromType, FromAccountID, ToAccountID, ToSign, ...)
VALUES (@HeaderID, 1,
    1, @MinorityInterestReserves, @GroupReserves, 1, ...);
-- Amount: 10 (manual entry)
```

### Complete Numeric Example: Preference Share Consolidation

**Given**:
- Subsidiary B: 1,000 ordinary shares + 500 preference shares (10% cumulative)
- Parent owns: 700 ordinary (70%) + 200 preference (40%)
- Subsidiary B net income: 200
- Preference dividend entitlement: 50 (10% of 500 capital)

**Method 1: Adjusted Percentage Approach**

Calculate economic entitlement:
```
Total dividends available: 200
Preference first: 50
  - Parent's share: 40% × 50 = 20
  - NCI share: 60% × 50 = 30

Remaining for ordinary: 150
  - Parent's share: 70% × 150 = 105
  - NCI share: 30% × 150 = 45

Total Parent: 20 + 105 = 125 (62.5% economic)
Total NCI: 30 + 45 = 75 (37.5% economic)
```

Configure in system:
```sql
-- Enter economic percentage instead of share count percentage
UPDATE TS015S0
SET FinPercentage = 62.50
WHERE ConsoID = @ConsoID
  AND CompanyID = @ParentID
  AND CompanyOwnedID = @SubsidiaryBID;
```

**Method 2: Virtual Entity Approach**

Split into two entities:
```
SUBSB-ORD:  Net Assets = 1,500 (ordinary portion)
            Parent FinPercentage = 70%

SUBSB-PREF: Net Assets = 500 (preference portion)
            Parent FinPercentage = 40%
```

Result: Same economic outcome, cleaner audit trail.

## Recommended Implementation

### Phase 1: Share Class Schema

```sql
-- New table: Share class definitions
CREATE TABLE TS015S2 (
    ShareClassID        INT IDENTITY PRIMARY KEY,
    ConsoID             INT NOT NULL,
    CompanyID           INT NOT NULL,       -- Company with share classes
    ShareClassName      NVARCHAR(50),       -- 'Ordinary', 'Preference A', etc.
    TotalSharesIssued   BIGINT NOT NULL,
    VotesPerShare       INT DEFAULT 1,
    DividendPriority    INT DEFAULT 99,     -- Lower = higher priority
    DividendRate        DECIMAL(10,6),      -- Cumulative % if applicable
    IsParticipating     BIT DEFAULT 0,
    IsRedeemable        BIT DEFAULT 0,
    RedemptionDate      DATE NULL,
    IsConvertible       BIT DEFAULT 0,
    ConversionRatio     DECIMAL(10,4)
);

-- Extend TS015S0 for class-level ownership
ALTER TABLE TS015S0 ADD ShareClassID INT NULL;
-- FK to TS015S2.ShareClassID
```

### Phase 2: Dividend Allocation Procedure

```sql
CREATE PROCEDURE P_CALC_PREFERENCE_DIVIDEND_ALLOCATION
    @ConsoID INT,
    @TotalDividend DECIMAL(28,6),
    @CompanyID INT
AS
BEGIN
    -- 1. Calculate cumulative preference entitlement
    -- 2. Allocate remaining to participating/ordinary
    -- 3. Return economic percentage per owner
END
```

### Phase 3: Automatic Economic Percentage

Update `P_CALC_OWNERSHIP_INDIRECT_PERCENTAGES` to:
1. Detect multiple share classes
2. Calculate economic interest considering preferences
3. Store separate financial and economic percentages

## API Reference

### Primary API Handlers
| Handler | YAML File | Purpose | Status |
|---------|-----------|---------|--------|
| `Ownership_SaveOwnership` | [api-ownership-endpoints.yaml](../11-agent-support/api-ownership-endpoints.yaml) | Save ownership (single class only) | ✅ IMPLEMENTED |
| `Journal_SaveJournal` | [api-adjustment-endpoints.yaml](../11-agent-support/api-adjustment-endpoints.yaml) | Book preference dividend adjustments | ✅ IMPLEMENTED |

### Supporting API Handlers
| Handler | YAML File | Purpose |
|---------|-----------|---------|
| `Ownership_GetOwnership` | [api-ownership-endpoints.yaml](../11-agent-support/api-ownership-endpoints.yaml) | Get ownership percentages |
| `Company_GetCompanies` | [api-company-endpoints.yaml](../11-agent-support/api-company-endpoints.yaml) | Get companies (for virtual entity workaround) |

### API Workflow
```
Preference Share via Virtual Entity (Workaround):

1. Company_GetCompanies → Get subsidiary ID
2. Create virtual entities:
   - SUBSB-ORD (ordinary class)
   - SUBSB-PREF (preference class)
3. Ownership_SaveOwnership → Configure per-class ownership:
   - 70% of SUBSB-ORD
   - 40% of SUBSB-PREF
4. Consolidation_Execute → Process each class
5. Result: Correct economic split
```

### Implementation Status
| Feature | Status | Gap Reference |
|---------|--------|---------------|
| Single share class | ✅ IMPLEMENTED | TS015S0 |
| Multiple share classes | ❌ NOT_IMPLEMENTED | Severity 8 |
| Dividend priority | ❌ NOT_IMPLEMENTED | Manual workaround |
| Economic % calculation | ❌ NOT_IMPLEMENTED | Manual calculation |
| Virtual entity workaround | ✅ AVAILABLE | Documented |

### Related API Documentation
- [API Index](../11-agent-support/api-index.yaml) - Master handler catalog
- [Gap Analysis](../11-agent-support/gap-analysis-report.yaml) - **NOT_IMPLEMENTED (Severity 8)**

---

## Related Documentation

- [Ownership Percentages](../06-ownership-structure/ownership-percentages.md) - Financial vs control %
- [Dividend Eliminations](../04-elimination-entries/dividend-eliminations.md) - Dividend processing
- [Minority Interest](minority-interest.md) - NCI calculation
- [User-Defined Eliminations](../04-elimination-entries/user-eliminations.md) - Manual adjustments

### Related Knowledge Chunks
- Chunk 0653: Privileged shares with cumulative dividends
- Chunk 0016: Statutory vs reporting consolidation
- Chunk 0510: Key transactions
- Chunk 1264: Minority interest calculation scenarios

---
*Document 28 of 50+ | Batch 10: Remaining Severity 8 Gaps | Last Updated: 2024-12-01*
*GAP STATUS: CONFIRMED - NOT_IMPLEMENTED (Severity 8) - Single share class model only*
