# Elimination Templates: Configuration Patterns and Best Practices

## Document Metadata
- **Category**: Elimination Entries
- **Theory Source**: Implementation-specific (Prophix.Conso elimination engine)
- **Implementation Files**:
  - `Sigma.Database/dbo/Tables/TS070S0.sql` - Elimination header definitions
  - `Sigma.Database/dbo/Tables/TS071S0.sql` - Elimination line details
  - `Sigma.Database/dbo/Tables/TS070S1.sql` - Company selection methods
  - `Sigma.Database/dbo/Stored Procedures/P_CONSO_ELIM_USER.sql` - User elimination execution
  - `Sigma.Database/dbo/Stored Procedures/P_CONSO_ELIM.sql` - Main elimination orchestrator
- **Last Updated**: 2024-12-01
- **Completeness**: 100% (Comprehensive template patterns)
- **Compliance Status**: Configuration reference document

## Executive Summary

Elimination templates in Prophix.Conso provide reusable patterns for configuring consolidation adjustments through the TS070S0/TS071S0 table structure. This document catalogs common template patterns, configuration best practices, and ready-to-use examples for typical consolidation scenarios. Templates reduce implementation time and ensure consistency across similar elimination requirements.

## Template Architecture Overview

### Two-Table Structure

```
┌─────────────────────────────────────────────────────────────────┐
│                    TS070S0 - HEADER                              │
│  "What elimination to run, when, and for which companies"       │
├─────────────────────────────────────────────────────────────────┤
│  ElimCode       │ Unique identifier (U001, U002, etc.)          │
│  ElimType       │ S=System, U=User                               │
│  ElimLevel      │ Processing order (1-99)                        │
│  Active         │ Enable/disable switch                          │
│  JournalTypeID  │ Target journal for postings                    │
│  ConsoMethodSelectionID │ Company filter                         │
│  Behaviour      │ Period processing mode (0-4)                   │
│  MinorityFlag   │ Include minority interest data                 │
│  PostingCompanyType │ Where to post: C=Company, P=Partner        │
└─────────────────────────────────────────────────────────────────┘
                              │
                              │ 1:N
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    TS071S0 - DETAILS                             │
│  "How to calculate and where to post the amounts"               │
├─────────────────────────────────────────────────────────────────┤
│  LineNr         │ Line sequence                                  │
│  FromType       │ Source data type (1-6)                         │
│  FromAccount*   │ Source account reference                       │
│  FromPeriod     │ C=Current, R=Reference                         │
│  FromFlow*      │ Source flow reference                          │
│  FromPartner*   │ IC partner filter                              │
│  FromCheck      │ Sign validation (NULL, 1, -1)                  │
│  ToType         │ Target data type (1-76)                        │
│  ToAccount*     │ Target account reference                       │
│  ToSign         │ 1=Same sign, -1=Reverse                        │
│  ToFlow*        │ Target flow reference                          │
│  Percentage     │ Amount multiplier (1-14)                       │
└─────────────────────────────────────────────────────────────────┘
```

## Reference Tables

### FromType / ToType Base Values

| Code | Name | Description | Source Table |
|------|------|-------------|--------------|
| 1 | Closing | Closing amounts | TD030B2 → TD035C2 |
| 2 | Closing Flow | Flow-level amounts | TD040B2 → TD045C2 |
| 3 | Closing Dimension | Dimensional amounts | TD050B2 → TD055C2 |
| 4 | Interco | Intercompany closing | TD030I2 |
| 5 | Interco Flow | IC flow-level | TD040I2 |
| 6 | Interco Dimension | IC dimensional | TD050I2 |

### ToType Modifiers (Same-as-Source)

| Modifier | Effect | ToType Example |
|----------|--------|----------------|
| +10 | Same account as source | 11, 14, 15 |
| +30 | Same flow as source | 32, 34, 35 |
| +40 | Same account & flow | 41, 42, 44 |
| +60 | Same dimension | 61, 63, 66 |
| +70 | Same account & dimension | 71, 73, 76 |

### Percentage Options

| Code | Description | Use Case |
|------|-------------|----------|
| 1 | 100% | Full amount |
| 2 | 0% | No posting (validation only) |
| 3 | Group % (Company, Current) | Standard group allocation |
| 4 | Minority % (Company, Current) | NCI allocation |
| 5 | Group + Minority % (Current) | Full percentage |
| 6-8 | Partner-based (Current) | IC adjustments |
| 9-14 | Reference period variants | Prior period percentages |

### Behaviour Options

| Code | Name | When Processed | Use Case |
|------|------|----------------|----------|
| 0 | Standard | Both periods | Normal eliminations |
| 1 | Reference Only | Prior period | Historical adjustments |
| 2 | Current Only | Current period | New period entries |
| 3 | Both Separate | Both, separately | Period comparison |
| 4 | Variation | Difference | Movement analysis |

### Company Selection Methods (TS070S1)

| ID | Code | Description | Filter |
|----|------|-------------|--------|
| 1 | A | All companies | None |
| 2 | - | Parent only | IsParent = 1 |
| 3 | - | All except parent | IsParent = 0 |
| 4 | G | Global integration | ConsoMethod = 'G' |
| 5 | P | Proportional | ConsoMethod = 'P' |
| 6 | E | Equity method | ConsoMethod = 'E' |
| 7 | N | Not consolidated | ConsoMethod = 'N' |
| 8 | J | Entering scope | FlagEnteringScope = 1 |
| 9 | L | Leaving scope | FlagLeavingScope = 1 |
| 10 | - | Available for sale | AvailableForSale = 1 |
| 11 | - | Consolidated, not parent | IsParent = 0, ConsoMethod IN (G,P,E) |

## Template Patterns

### Pattern 1: Basic Intercompany Elimination (100%)

**Use Case**: Eliminate intercompany balances at 100%

```sql
-- Header
INSERT INTO TS070S0 (ConsoID, ElimCode, ElimType, ElimText, Active, ElimLevel,
    JournalTypeID, ConsoMethodSelectionID, Behaviour, MinorityFlag, JournalText)
VALUES (@ConsoID, 'U010', 'U', 'IC Balance Elim', 1, 10,
    @JournalTypeID, 4, 0, 0, 'Intercompany balance elimination - 100%');

-- Detail Line 1: Debit IC Receivable → Credit IC Receivable (reverse)
INSERT INTO TS071S0 (ConsoID, EliminationHeaderID, LineNr,
    FromType, FromAccountID, FromPeriod,
    ToType, ToAccountID, ToSign, Percentage)
VALUES (@ConsoID, @HeaderID, 1,
    4, @IC_Receivable_AccountID, 'C',  -- FromType 4 = Interco
    1, @IC_Receivable_AccountID, -1, 1);  -- Reverse, 100%

-- Detail Line 2: Credit IC Payable → Debit IC Payable (reverse)
INSERT INTO TS071S0 (...)
VALUES (@ConsoID, @HeaderID, 2,
    4, @IC_Payable_AccountID, 'C',
    1, @IC_Payable_AccountID, -1, 1);
```

### Pattern 2: Profit-in-Stock Elimination with Carry Forward

**Use Case**: Eliminate unrealized margin on intercompany inventory

```sql
-- Header
INSERT INTO TS070S0 (ConsoID, ElimCode, ElimType, ElimText, Active, ElimLevel,
    JournalTypeID, ConsoMethodSelectionID, Behaviour, MinorityFlag, JournalText)
VALUES (@ConsoID, 'U020', 'U', 'Stock Margin', 1, 20,
    @JournalTypeID, 4, 3, 0, 'Unrealized profit in stock elimination');
    -- Behaviour 3 = Both periods separately

-- Line 1: Current period - Reverse sales
INSERT INTO TS071S0 (ConsoID, EliminationHeaderID, LineNr,
    FromType, FromAccountID, FromPeriod, FromPartnerMethod,
    ToType, ToConsolidationAccountID, ToSign, Percentage)
VALUES (@ConsoID, @HeaderID, 1,
    5, @IC_Sales_AccountID, 'C', 'G',  -- IC Flow, Global partners
    2, @Stock_Margin_FlowID, -1, 1);

-- Line 2: Current period - Credit reserves
INSERT INTO TS071S0 (...)
VALUES (@ConsoID, @HeaderID, 2,
    5, @IC_Sales_AccountID, 'C', 'G',
    2, @Reserves_ConsoAccountID, 1, 1);

-- Line 3: Reference period - Reverse prior margin (carry forward)
INSERT INTO TS071S0 (...)
VALUES (@ConsoID, @HeaderID, 3,
    5, @IC_Sales_AccountID, 'R', 'G',  -- Reference period
    2, @Stock_Margin_FlowID, 1, 1);  -- Opposite sign to reverse
```

### Pattern 3: Group Percentage Allocation

**Use Case**: Allocate amounts based on ownership percentage

```sql
-- Header
INSERT INTO TS070S0 (ConsoID, ElimCode, ElimType, ElimText, Active, ElimLevel,
    JournalTypeID, ConsoMethodSelectionID, Behaviour, MinorityFlag, JournalText)
VALUES (@ConsoID, 'U030', 'U', 'Ownership Alloc', 1, 30,
    @JournalTypeID, 11, 0, 1, 'Allocate at group percentage');
    -- ConsoMethodSelectionID 11 = All except parent and N
    -- MinorityFlag 1 = Include MI

-- Line 1: Group portion
INSERT INTO TS071S0 (ConsoID, EliminationHeaderID, LineNr,
    FromType, FromAccountID, FromPeriod,
    ToType, ToAccountID, ToSign, Percentage)
VALUES (@ConsoID, @HeaderID, 1,
    1, @Source_AccountID, 'C',
    1, @Group_Target_AccountID, 1, 3);  -- Percentage 3 = Group % current

-- Line 2: Minority portion
INSERT INTO TS071S0 (...)
VALUES (@ConsoID, @HeaderID, 2,
    1, @Source_AccountID, 'C',
    1, @Minority_Target_AccountID, 1, 4);  -- Percentage 4 = Minority % current
```

### Pattern 4: Same-as-Source Account Mapping

**Use Case**: Post to same account as source (account-by-account elimination)

```sql
-- Header
INSERT INTO TS070S0 (...)
VALUES (@ConsoID, 'U040', 'U', 'SaS Elim', 1, 40,
    @JournalTypeID, 4, 0, 0, 'Same-as-source account elimination');

-- Line: Use ToType 11 (Closing + Same Account)
INSERT INTO TS071S0 (ConsoID, EliminationHeaderID, LineNr,
    FromType, FromAccountSummationID, FromPeriod,  -- Account group
    ToType, ToSign, Percentage)
VALUES (@ConsoID, @HeaderID, 1,
    1, @IC_AccountGroup_SummationID, 'C',
    11, -1, 1);  -- ToType 11 = target uses source account
```

### Pattern 5: Entering Company Adjustment

**Use Case**: Special treatment for companies entering consolidation scope

```sql
-- Header
INSERT INTO TS070S0 (ConsoID, ElimCode, ElimType, ElimText, Active, ElimLevel,
    JournalTypeID, ConsoMethodSelectionID, Behaviour, MinorityFlag, JournalText)
VALUES (@ConsoID, 'U050', 'U', 'Entry Adjust', 1, 50,
    @JournalTypeID, 8, 2, 0, 'First consolidation adjustment');
    -- ConsoMethodSelectionID 8 = Entering companies
    -- Behaviour 2 = Current period only

-- Lines for opening balance adjustments...
INSERT INTO TS071S0 (...)
VALUES (@ConsoID, @HeaderID, 1,
    1, @Opening_Reserves_AccountID, 'C',
    1, @Group_Reserves_AccountID, -1, 3);
```

### Pattern 6: Sign-Conditional Processing

**Use Case**: Process only positive or negative amounts

```sql
-- Header
INSERT INTO TS070S0 (...)
VALUES (@ConsoID, 'U060', 'U', 'Positive Only', 1, 60,
    @JournalTypeID, 4, 0, 0, 'Process positive amounts only');

-- Line with FromCheck = 1 (positive amounts only)
INSERT INTO TS071S0 (ConsoID, EliminationHeaderID, LineNr,
    FromType, FromAccountID, FromPeriod, FromCheck,
    ToType, ToAccountID, ToSign, Percentage)
VALUES (@ConsoID, @HeaderID, 1,
    1, @Source_AccountID, 'C', 1,  -- FromCheck 1 = >= 0 only
    1, @Target_AccountID, 1, 1);

-- Separate line for negative amounts (FromCheck = -1)
INSERT INTO TS071S0 (...)
VALUES (@ConsoID, @HeaderID, 2,
    1, @Source_AccountID, 'C', -1,  -- FromCheck -1 = < 0 only
    1, @Alternative_Target_AccountID, 1, 1);
```

### Pattern 7: Partner-Based IC Elimination

**Use Case**: Eliminate IC based on partner company selection

```sql
-- Header
INSERT INTO TS070S0 (...)
VALUES (@ConsoID, 'U070', 'U', 'Partner IC Elim', 1, 70,
    @JournalTypeID, 4, 0, 0, 'Partner-based IC elimination');

-- Line: Source from specific partner
INSERT INTO TS071S0 (ConsoID, EliminationHeaderID, LineNr,
    FromType, FromAccountID, FromPeriod, FromPartnerCompanyID,
    ToType, ToAccountID, ToSign, ToPartnerCompanyType, Percentage)
VALUES (@ConsoID, @HeaderID, 1,
    5, @IC_AccountID, 'C', @PartnerCompanyID,  -- Specific partner
    5, @IC_AccountID, -1, 'P', 6);  -- ToPartnerCompanyType 'P', Partner %
```

### Pattern 8: Dimensional Elimination

**Use Case**: Process eliminations at dimensional level

```sql
-- Header
INSERT INTO TS070S0 (...)
VALUES (@ConsoID, 'U080', 'U', 'Dim Elim', 1, 80,
    @JournalTypeID, 4, 0, 0, 'Dimensional elimination');

-- Line: Dimensional source and target
INSERT INTO TS071S0 (ConsoID, EliminationHeaderID, LineNr,
    FromType, FromAccountID, FromPeriod, FromDimensionGroupID,
    ToType, ToAccountID, ToSign, ToDimensionGroupID, Percentage)
VALUES (@ConsoID, @HeaderID, 1,
    3, @AccountID, 'C', @DimGroupID,  -- FromType 3 = Dimensional
    63, @TargetAccountID, -1, NULL, 1);  -- ToType 63 = Dim + Same Dim
```

## Configuration Best Practices

### Naming Conventions

| Component | Convention | Example |
|-----------|------------|---------|
| ElimCode | U + 3 digits | U001, U050, U100 |
| ElimText | Short, descriptive | "Stock Margin", "IC Netting" |
| JournalText | Detailed explanation | "Eliminate unrealized profit on intercompany inventory transfers" |

### ElimLevel Guidelines

| Range | Category | Examples |
|-------|----------|----------|
| 1-19 | Pre-processing | Data validation, setup adjustments |
| 20-39 | IC eliminations | Netting, balance eliminations |
| 40-59 | Margin eliminations | Stock margins, service margins |
| 60-79 | Equity adjustments | Participation, capital eliminations |
| 80-99 | Post-processing | Reclassifications, final adjustments |

### Sequence Considerations

1. **Process independent eliminations first** (lower ElimLevel)
2. **Dependent eliminations after** their prerequisites
3. **Same ElimLevel**: Process in ElimCode order
4. **Reference period before current** when using Behaviour = 3

### Testing Checklist

- [ ] Verify company selection matches intended scope
- [ ] Test with sample data in non-production environment
- [ ] Validate journal balances (debits = credits)
- [ ] Check period handling (current vs reference)
- [ ] Verify percentage calculations
- [ ] Test sign conventions (ToSign)
- [ ] Review Same-as-Source behavior
- [ ] Validate dimensional mapping if applicable

## API Reference

### Primary API Handlers
| Handler | YAML File | Purpose | Status |
|---------|-----------|---------|--------|
| `Elimination_GetEliminations` | [api-elimination-endpoints.yaml](../11-agent-support/api-elimination-endpoints.yaml) | Get elimination template configurations | ✅ IMPLEMENTED |
| `Elimination_SaveElimination` | [api-elimination-endpoints.yaml](../11-agent-support/api-elimination-endpoints.yaml) | Save/update elimination templates | ✅ IMPLEMENTED |
| `Consolidation_Execute` | [api-consolidation-endpoints.yaml](../11-agent-support/api-consolidation-endpoints.yaml) | Execute configured eliminations | ✅ IMPLEMENTED |

### Supporting API Handlers
| Handler | YAML File | Purpose |
|---------|-----------|---------|
| `JournalType_GetJournalTypes` | [api-journal-endpoints.yaml](../11-agent-support/api-journal-endpoints.yaml) | Get target journal types |
| `Account_GetAccounts` | [api-account-endpoints.yaml](../11-agent-support/api-account-endpoints.yaml) | Get account options |
| `Flow_GetFlows` | [api-flow-endpoints.yaml](../11-agent-support/api-flow-endpoints.yaml) | Get flow options |
| `ConsolidationAccount_GetAccounts` | [api-account-endpoints.yaml](../11-agent-support/api-account-endpoints.yaml) | Get special accounts (SaS targets) |

### Template Configuration via API
```
Creating Elimination Template via API:

STEP 1: Create Header (TS070S0)
Elimination_SaveElimination:
  - ElimCode: 'U0XX'
  - ElimType: 'U'
  - ElimLevel: 10-99 (processing order)
  - Behaviour: 0-4 (period mode)
  - ConsoMethodSelectionID: 1-11 (company filter)
  - JournalTypeID: Target journal

STEP 2: Add Detail Lines (TS071S0)
Elimination_SaveElimination:
  - LineNr: Sequence number
  - FromType: 1-6 (data source)
  - FromAccountID/FromConsolidationAccountID
  - FromPeriod: 'C' or 'R'
  - ToType: 1-76 (with SaS modifiers)
  - ToAccountID/ToConsolidationAccountID
  - ToSign: 1 or -1
  - Percentage: 1-14 (calculation method)

STEP 3: Test Execution
Consolidation_Execute → Verify template processing
```

### Template Patterns Reference
| Pattern | ElimLevel | Behaviour | Use Case |
|---------|-----------|-----------|----------|
| IC Balance | 10-19 | 0 | Standard IC netting |
| Stock Margin | 20-39 | 3 | Carry-forward eliminations |
| Ownership Alloc | 40-59 | 0 | Percentage-based split |
| Entering Adjust | 60-79 | 2 | First consolidation entries |
| Sign-Conditional | 80-99 | 0 | Positive/negative routing |

### Related API Documentation
- [API Index](../11-agent-support/api-index.yaml) - Master handler catalog
- [Gap Analysis](../11-agent-support/gap-analysis-report.yaml) - **FULLY IMPLEMENTED (100%)**

---

## Related Documentation

- [User-Defined Eliminations](user-eliminations.md) - Framework reference
- [Profit-in-Stock Eliminations](profit-in-stock-eliminations.md) - Stock margin patterns
- [Intercompany Transactions](intercompany-transactions.md) - IC elimination patterns
- [Journal Types](../07-database-implementation/journal-types.md) - Journal configuration
- [Elimination Execution Engine](../08-application-layer/elimination-execution-engine.md) - Processing details

---
*Document 35 of 50+ | Batch 12: Advanced Translation & Elimination Templates | Last Updated: 2024-12-01*
