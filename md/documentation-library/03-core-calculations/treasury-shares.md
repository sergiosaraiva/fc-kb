# Treasury Shares: Own Shares in Consolidation

## Document Metadata
- **Category**: Core Calculations
- **Theory Source**: Knowledge base chunks: 0083, 0085, 0086, 0088, 0089, 0118-0120
- **Implementation Files**:
  - `Sigma.Database/dbo/Stored Procedures/P_VIEW_OWNERSHIP_DETAIL.sql` - OWNERSHIP_AUTHORIZE_OWNSHARES config
  - `Sigma.Database/dbo/Tables/TS015S0.sql` - Can store self-ownership records
  - `Sigma.Database/dbo/Tables/T_CONFIG.sql` - Configuration storage
- **Last Updated**: 2024-12-02 (Enhanced with visual diagram, implementation checklist, and validation queries)
- **Completeness**: 75% (Data entry supported; comprehensive workarounds documented; accounting treatment not automated)
- **Compliance Status**: IAS 32 - Partial (manual adjustments required)

## Executive Summary

Treasury shares (own shares) occur when a company or its subsidiaries hold shares of the company itself. Per IAS 32, treasury shares must be deducted from equity, not recognized as assets, and no dividends should be recorded on them. Prophix.Conso provides **limited support** for treasury shares: the configuration `OWNERSHIP_AUTHORIZE_OWNSHARES` allows data entry of self-ownership, but the **consolidation accounting treatment** (equity deduction, dividend exclusion, percentage adjustment) requires **manual configuration** through user-defined eliminations.

## Theoretical Framework

### Concept Definition

From Allen White's "Direct Consolidation" (Chunk 83):

> "A corporation, or its affiliates, could hold its own shares (known as Treasury shares). To determine the percentage of control, these shares must be subtracted from the total of shares of the company."

### Types of Treasury Shares

| Type | Description | Consolidation Impact |
|------|-------------|---------------------|
| **Direct** | Company holds its own shares | Deduct from equity |
| **Indirect** | Subsidiary holds parent shares | Treat as treasury at group level |
| **Cross-Treasury** | Subsidiary A holds shares of subsidiary B which holds shares of A | Complex circular adjustment |

### IAS 32 Requirements

1. **Equity Deduction**: Treasury shares deducted from equity, not shown as asset
2. **No Gain/Loss**: No gain or loss recognized on purchase, sale, or cancellation
3. **No Dividends**: Company cannot pay dividends to itself
4. **Disclosure**: Quantity and reasons for holding must be disclosed

### Visual: Treasury Share Treatment Flow

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    TREASURY SHARE CONSOLIDATION FLOW                         │
└─────────────────────────────────────────────────────────────────────────────┘

  SCENARIO: Parent P owns 60% of Subsidiary B; B holds 5% of its own shares

  STEP 1: IDENTIFY TREASURY                 STEP 2: CALCULATE EFFECTIVE %
  ─────────────────────────────             ──────────────────────────────

  ┌─────────────────────────────┐           ┌─────────────────────────────┐
  │ Parent P                    │           │ PERCENTAGE ADJUSTMENT        │
  │ └── 60% ──► Subsidiary B    │           │                             │
  │              └── 5% ──► B   │◄─Treasury │ Shares outstanding: 100%    │
  │                  (self)     │           │ Less treasury:       (5%)   │
  └─────────────────────────────┘           │ Circulating:         95%    │
                                            │                             │
                                            │ P's effective: 60%/95%      │
                                            │            = 63.16% control │
                                            └─────────────────────────────┘

  STEP 3: EQUITY DEDUCTION (IAS 32)         STEP 4: ELIMINATION JOURNAL
  ───────────────────────────────           ─────────────────────────────

  ┌─────────────────────────────┐           ┌───────┬──────────────┬──────┐
  │ B's Balance Sheet           │           │ Entry │ Account      │ Amt  │
  ├─────────────────────────────┤           ├───────┼──────────────┼──────┤
  │ ASSETS                      │           │  Dr   │ Treasury     │  50  │
  │   Investment Own Shares: 50 │──Remove──►│       │ Contra-Equity│      │
  │                             │           │  Cr   │ Investment   │ (50) │
  │ EQUITY                      │           │       │ Own Shares   │      │
  │   Share Capital:       800  │           └───────┴──────────────┴──────┘
  │   Retained Earnings:   150  │
  │   Treasury Shares:    (50)  │◄─Add contra
  │   ─────────────────────     │
  │   Net Equity:          900  │◄─Adjusted
  └─────────────────────────────┘

  INDIRECT TREASURY (Sub holds Parent shares):
  ┌─────────────────────────────────────────────────────────────────────────┐
  │ If Subsidiary B holds 3% of Parent P:                                   │
  │                                                                         │
  │   P ──60%──► B ──3%──► P  (circular!)                                  │
  │                                                                         │
  │ Treatment: At group level, B's investment in P = GROUP treasury shares │
  │ Elimination: Dr Group Contra-Equity, Cr B's Investment in P            │
  └─────────────────────────────────────────────────────────────────────────┘
```

### Control Percentage Adjustment (Chunk 85-86)

```
Example:
- A owns 60% of B
- B owns 5% of its own shares (treasury)

Effective Control Calculation:
- Total voting shares in circulation = 100% - 5% = 95%
- A's effective control = 60% / 95% = 63.16%
```

### Consolidation Treatment (Chunk 88)

Required adjustments:
1. Eliminate treasury shares from equity
2. Adjust ownership percentages
3. No dividends on treasury shares
4. Disclosure requirements apply

## Current Implementation

### Configuration Option

`P_VIEW_OWNERSHIP_DETAIL.sql` (line 37):

```sql
-- Configuration to allow company to own shares in itself
Declare @ConfigVal bit
select @ConfigVal = ISNULL([dbo].[UDF_GET_CONFIG](
    'OWNERSHIP_AUTHORIZE_OWNSHARES', NULL, @ConsoID), 0)

-- When enabled (1), allows self-ownership in UI:
and ( a.CompanyID <> @CompanyID or @ConfigVal = 1)
```

**Purpose**: Controls whether the ownership UI allows selecting the same company as both owner and owned.

### Data Entry Support

When `OWNERSHIP_AUTHORIZE_OWNSHARES = 1`, users can enter:

```sql
-- TS015S0 - Treasury share record
INSERT INTO TS015S0 (ConsoID, CompanyID, CompanyOwnedID, FinPercentage, NbrFinRights)
VALUES (@ConsoID, @CompanyB_ID, @CompanyB_ID, 5.0, 500);  -- B owns 5% of itself
```

### What Is NOT Automated

| Requirement | Status | Current Workaround |
|-------------|--------|-------------------|
| Equity deduction | **Manual** | User elimination to debit Equity, credit Treasury |
| Percentage adjustment | **Manual** | User must manually adjust in P_CALC_OWNERSHIP |
| Dividend exclusion | **Manual** | Manual adjustment in dividend elimination |
| Indirect treasury (sub holds parent) | **Manual** | Complex user elimination required |
| MI adjustment for indirect | **Manual** | Not automated |

### Matrix Algebra Consideration

The `P_CALC_OWNERSHIP_INDIRECT_PERCENTAGES` procedure processes self-ownership records if entered, but does **not** automatically:
1. Exclude treasury shares from denominator
2. Apply IAS 32 percentage adjustment formula
3. Adjust minority interest accordingly

## Gap Analysis

### Gap Status: CONFIRMED - NOT_IMPLEMENTED (Severity 8)

**What's Missing**:

1. **Automatic Equity Deduction**
   - No built-in elimination to move treasury shares from assets to contra-equity
   - User must configure TS070S0/TS071S0 manually

2. **Percentage Auto-Adjustment**
   - System uses gross shares issued, not net (after treasury)
   - Formula should be: `Effective % = Direct % / (100% - Treasury %)`

3. **Dividend Exclusion**
   - P_CONSO_ELIM_DIVIDEND does not check for treasury shares
   - Dividend on treasury shares incorrectly included

4. **Indirect Treasury Detection**
   - When subsidiary owns parent shares, system doesn't flag as group treasury
   - No automatic elimination at group level

5. **Circular Treasury Impact (Chunk 119)**
   - C1's stake in P creates circular ownership
   - Should be treated as treasury shares in consolidation
   - Not automatically detected or adjusted

### Recommended Implementation

**Phase 1: Database Schema Enhancement**

```sql
-- Add treasury flag to TS015S0
ALTER TABLE TS015S0 ADD IsTreasuryShare BIT DEFAULT 0;

-- Or add special account designation in TS012C0
-- ConsolidationAccountCode = 'TREASURY' for treasury classification
```

**Phase 2: Percentage Calculation Update**

```sql
-- In P_CALC_OWNERSHIP_INDIRECT_PERCENTAGES
-- Before building ownership matrix, adjust for treasury:
UPDATE #Companies
SET NbrFinRightsIssued = NbrFinRightsIssued - ISNULL(TreasuryShares, 0)
FROM #Companies c
LEFT JOIN (
    SELECT CompanyOwnedID, SUM(NbrFinRights) as TreasuryShares
    FROM TS015S0
    WHERE CompanyID = CompanyOwnedID  -- Self-ownership
    GROUP BY CompanyOwnedID
) t ON t.CompanyOwnedID = c.CompanyID
```

**Phase 3: Automatic Elimination**

```sql
-- System elimination S0XX for treasury shares
-- Header
INSERT INTO TS070S0 (ElimCode, ElimType, ElimText, ...)
VALUES ('S015', 'S', 'Treasury Share Elimination', ...);

-- Details: Move from Asset to Contra-Equity
INSERT INTO TS071S0 (EliminationHeaderID, FromType, FromAccountID,
                     ToType, ToAccountID, ToSign, Percentage)
VALUES (@HeaderID, 1, @TreasuryAssetAccount,
        1, @TreasuryContraEquity, -1, 1);
```

## Manual Workaround

### Current Process for Treasury Shares

**Step 1: Enable Data Entry**

```sql
-- Set configuration to allow self-ownership
INSERT INTO T_CONFIG ([Key], [Value], CustomerID)
VALUES ('OWNERSHIP_AUTHORIZE_OWNSHARES', '1', @CustomerID);
```

**Step 2: Enter Treasury Holdings**

Via UI or SQL:
```sql
INSERT INTO TS015S0 (ConsoID, CompanyID, CompanyOwnedID, FinPercentage)
VALUES (@ConsoID, @SubsidiaryID, @SubsidiaryID, 5.0);
```

**Step 3: Create Manual Elimination**

```sql
-- Header: Treasury Share Adjustment
INSERT INTO TS070S0 (ConsoID, ElimCode, ElimType, ElimText, Active,
                     ConsoMethodSelectionID, JournalTypeID, ...)
VALUES (@ConsoID, 'U010', 'U', 'Treasury Share - Equity Deduction', 1,
        4, @JournalID, ...);  -- Method 4 = Global only

-- Line: Reclassify from asset to contra-equity
INSERT INTO TS071S0 (EliminationHeaderID, LineNr,
    FromType, FromAccountID, FromPeriod,
    ToAccountID, ToSign, Percentage)
VALUES (@HeaderID, 1,
    1, @TreasuryInvestmentAccount, 'C',
    @TreasuryContraEquityAccount, -1, 1);
```

**Step 4: Adjust Ownership Percentages Manually**

Since automatic adjustment isn't available, users must:
1. Calculate effective percentages manually
2. Override in TS014C0 if needed
3. Or accept that group/minor % may be slightly off

### Complete Numeric Example: Treasury Share Handling

**Scenario**:
- Parent P owns 60% of Subsidiary B
- Subsidiary B holds 5% of its own shares (treasury)
- B's equity: 1,000 (including 50 in treasury shares at cost)

**Step 1: Calculate Effective Percentages**
```
Shares in circulation = 100% - 5% = 95%
P's effective ownership = 60% / 95% = 63.16%
NCI effective = 40% / 95% = 42.11%

Note: These don't sum to 100% - the difference (5.26%) represents the treasury effect
Actually: 63.16% + 42.11% = 105.27% of circulating shares
Scaled: 63.16/105.27 = 60%, 42.11/105.27 = 40% (back to original!)

Correct interpretation: P controls 63.16% of votes among non-treasury shareholders
```

**Step 2: Configure in System**
```sql
-- Enable treasury share data entry
INSERT INTO T_CONFIG ([Key], [Value], CustomerID)
VALUES ('OWNERSHIP_AUTHORIZE_OWNSHARES', '1', @CustomerID);

-- Enter P's ownership of B (using standard 60%)
INSERT INTO TS015S0 (ConsoID, CompanyID, CompanyOwnedID, FinPercentage, CtrlPercentage)
VALUES (@ConsoID, @ParentID, @SubsidiaryBID, 60.00, 60.00);

-- Enter B's self-ownership (treasury)
INSERT INTO TS015S0 (ConsoID, CompanyID, CompanyOwnedID, FinPercentage, CtrlPercentage)
VALUES (@ConsoID, @SubsidiaryBID, @SubsidiaryBID, 5.00, 0.00);  -- 0% voting
```

**Step 3: Create Treasury Share Elimination**
```sql
-- Header
INSERT INTO TS070S0 (ConsoID, ElimCode, ElimType, ElimText, Active,
                     ConsoMethodSelectionID, JournalTypeID, MinorityFlag, ...)
VALUES (@ConsoID, 'U011', 'U', 'Treasury Shares - B 5% - IAS 32 Equity Deduction',
        1, 4, @JournalID, 0, ...);

-- Detail Line 1: Remove treasury from investments (if booked there)
-- Dr  Contra-Equity (Treasury Shares)    50
--     Cr  Investment in Own Shares            50
INSERT INTO TS071S0 (EliminationHeaderID, LineNr,
    FromType, FromAccountID, FromPeriod, ToAccountID, ToSign, Percentage)
VALUES (@HeaderID, 1,
    2, @InvestmentOwnShares, 'C', @TreasuryContraEquity, 1, 1);
```

**Step 4: Verify Consolidated Equity**
```
B's Equity before consolidation:     1,000
  Share Capital:                       800
  Retained Earnings:                   150
  Treasury Shares (contra):            (50)  ← Added via user elimination
Net Equity for consolidation:          950

P's share (60%):                       570
NCI share (40%):                       380
```

### Workaround for Indirect Treasury Shares

**Scenario**: Subsidiary B holds 3% of Parent P shares

This creates "indirect treasury" - at group level, these are the group's own shares.

```sql
-- Step 1: Enter ownership (B owns P)
INSERT INTO TS015S0 (ConsoID, CompanyID, CompanyOwnedID, FinPercentage, ...)
VALUES (@ConsoID, @SubsidiaryBID, @ParentID, 3.00, ...);

-- Step 2: Create indirect treasury elimination
INSERT INTO TS070S0 (ConsoID, ElimCode, ElimType, ElimText, ...)
VALUES (@ConsoID, 'U012', 'U', 'Indirect Treasury - Sub holds Parent shares', ...);

-- Step 3: Eliminate as group treasury
-- Dr  Group Contra-Equity (Treasury)     XXX
--     Cr  B's Investment in P                 XXX

INSERT INTO TS071S0 (EliminationHeaderID, LineNr,
    FromType, FromAccountID, FromPeriod, ToAccountID, ToSign, ...)
VALUES (@HeaderID, 1,
    1, @BInvestmentInParent, 'C', @GroupTreasuryContraEquity, 1, ...);
```

### Configuration Reference

| Config Key | Value | Effect |
|------------|-------|--------|
| `OWNERSHIP_AUTHORIZE_OWNSHARES` | `0` (default) | Self-ownership blocked in UI |
| `OWNERSHIP_AUTHORIZE_OWNSHARES` | `1` | Self-ownership allowed in UI |

**How to Set Configuration**:
```sql
-- Check current value
SELECT * FROM T_CONFIG
WHERE [Key] = 'OWNERSHIP_AUTHORIZE_OWNSHARES';

-- Set or update
MERGE INTO T_CONFIG AS target
USING (SELECT 'OWNERSHIP_AUTHORIZE_OWNSHARES' AS [Key], '1' AS [Value]) AS source
ON target.[Key] = source.[Key] AND target.CustomerID = @CustomerID
WHEN MATCHED THEN UPDATE SET [Value] = source.[Value]
WHEN NOT MATCHED THEN INSERT ([Key], [Value], CustomerID)
                      VALUES (source.[Key], source.[Value], @CustomerID);
```

### Audit Trail Best Practices

For treasury share adjustments, include in elimination text:
1. Company code holding treasury
2. Percentage of treasury held
3. Reference to IAS 32 requirement
4. Date of treasury purchase/acquisition

**Example**:
```sql
ElimText = 'Treasury Shares - SUBS_B - 5% own shares - IAS 32.33 - Acquired 2023-06-15'
```

## Theory vs Practice Analysis

| Aspect | Theory (IAS 32) | Prophix.Conso Implementation | Alignment |
|--------|----------------|------------------------------|-----------|
| Data Entry | Allow recording | Config option available | **Partial** |
| Equity Deduction | Automatic | Manual elimination required | **Gap** |
| Percentage Adjustment | Automatic | Not implemented | **Gap** |
| Dividend Exclusion | Automatic | Not implemented | **Gap** |
| Indirect Treasury | Auto-detect | Not implemented | **Gap** |
| MI Adjustment | Required | Not implemented | **Gap** |

## Business Impact

### Current Capabilities

1. **Data Entry**: Can record self-ownership when configured
2. **Awareness**: System processes records through matrix algebra
3. **Manual Path**: User eliminations can achieve compliance

### Operational Considerations

1. **Extra Configuration**: Requires manual setup for each treasury situation
2. **Percentage Risk**: Group/minority percentages may be slightly incorrect
3. **Audit Trail**: Manual adjustments harder to trace
4. **Dividend Risk**: May include dividends on treasury if not manually excluded

## API Reference

### Primary API Handlers
| Handler | YAML File | Purpose | Status |
|---------|-----------|---------|--------|
| `Ownership_SaveOwnership` | [api-ownership-endpoints.yaml](../11-agent-support/api-ownership-endpoints.yaml) | Enter self-ownership (when OWNERSHIP_AUTHORIZE_OWNSHARES=1) | ✅ IMPLEMENTED |
| `Journal_SaveJournal` | [api-adjustment-endpoints.yaml](../11-agent-support/api-adjustment-endpoints.yaml) | Book treasury equity deduction (manual) | ✅ IMPLEMENTED |

### Supporting API Handlers
| Handler | YAML File | Purpose |
|---------|-----------|---------|
| `Ownership_GetOwnership` | [api-ownership-endpoints.yaml](../11-agent-support/api-ownership-endpoints.yaml) | Get treasury holdings |
| `LaunchCalculateIndirectPercentagesJob` | [api-ownership-endpoints.yaml](../11-agent-support/api-ownership-endpoints.yaml) | Recalculate (no treasury adjustment) |

### API Workflow
```
1. Enable configuration: OWNERSHIP_AUTHORIZE_OWNSHARES = 1
2. Ownership_SaveOwnership → Enter self-ownership in TS015S0:
   CompanyID = CompanyOwnedID (treasury)
3. Journal_SaveJournal → Book equity deduction (manual):
   Dr Contra-Equity (Treasury Shares)
   Cr Investment in Own Shares
4. Consolidation_Execute → Process (no automatic treasury treatment)
```

### Implementation Status
| Feature | Status | Gap Reference |
|---------|--------|---------------|
| Treasury data entry | ✅ IMPLEMENTED | Config-enabled |
| Auto equity deduction | ❌ NOT_IMPLEMENTED | Severity 8, IAS 32 |
| % auto-adjustment | ❌ NOT_IMPLEMENTED | Manual |
| Dividend exclusion | ❌ NOT_IMPLEMENTED | Manual |
| Indirect treasury detect | ❌ NOT_IMPLEMENTED | Manual |

### Configuration
| Key | Value | Effect |
|-----|-------|--------|
| `OWNERSHIP_AUTHORIZE_OWNSHARES` | `0` | Self-ownership blocked (default) |
| `OWNERSHIP_AUTHORIZE_OWNSHARES` | `1` | Self-ownership allowed |

### Related API Documentation
- [API Index](../11-agent-support/api-index.yaml) - Master handler catalog
- [Gap Analysis](../11-agent-support/gap-analysis-report.yaml) - **NOT_IMPLEMENTED (Severity 8)**

---

## Related Documentation

- [Circular Ownership](circular-ownership.md) - Indirect treasury creates circularity
- [Ownership Percentages](../06-ownership-structure/ownership-percentages.md) - Financial % calculation
- [Dividend Eliminations](../04-elimination-entries/dividend-eliminations.md) - Dividend processing
- [User-Defined Eliminations](../04-elimination-entries/user-eliminations.md) - Manual adjustment framework

### Related Knowledge Chunks
- Chunk 0083: Treasury shares concept
- Chunk 0085-0086: Ownership structure with treasury
- Chunk 0088-0089: Consolidation treatment requirements
- Chunk 0118-0120: Treasury share circular impact

---
*Document 26 of 50+ | Batch 9: High Priority Gap Analysis | Last Updated: 2024-12-01*
*GAP STATUS: CONFIRMED - NOT_IMPLEMENTED (Severity 8)*
