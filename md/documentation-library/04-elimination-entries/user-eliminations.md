# User-Defined Eliminations Framework

## Document Metadata
- **Category**: Elimination Entries
- **Theory Source**: Implementation-specific (configurable elimination engine)
- **Implementation Files**:
  - `Sigma.Database/dbo/Tables/TS070S0.sql` - Elimination header definitions
  - `Sigma.Database/dbo/Tables/TS071S0.sql` - Elimination line details
  - `Sigma.Database/dbo/Tables/TS070S1.sql` - Company selection methods
  - `Sigma.Database/dbo/Stored Procedures/P_CONSO_ELIM_USER.sql` - User elimination processing
  - `Sigma.Database/dbo/Stored Procedures/P_CONSO_ELIM_USER_PROCESS.sql` - Elimination execution
- **Last Updated**: 2024-12-01
- **Completeness**: 100% (Full configurable elimination framework)
- **Compliance Status**: Flexible framework supporting custom IFRS/GAAP adjustments

## Executive Summary

The User-Defined Eliminations Framework in Prophix.Conso provides a powerful, configurable engine for creating custom consolidation adjustments. Unlike system eliminations (S0XX codes executed by dedicated stored procedures), user eliminations (U-type) are defined through configuration tables (TS070S0/TS071S0) and executed by the generic `P_CONSO_ELIM_USER` procedure. This framework supports complex scenarios like profit-in-stock eliminations, deferred tax adjustments, and custom intercompany processing.

## Framework Architecture

### Two-Tier Configuration

```
┌─────────────────────────────────────────────────────────────┐
│                    TS070S0 - Header                          │
│   Defines: What, When, Where, Who                           │
│   - ElimCode (U001, U002, etc.)                             │
│   - Company selection method                                 │
│   - Journal assignment                                       │
│   - Active/Inactive status                                   │
│   - Behaviour flags                                          │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    TS071S0 - Details                         │
│   Defines: How (source → target mapping)                    │
│   - Source: Account, Flow, Partner, Period                  │
│   - Target: Account, Flow, Sign, Percentage                 │
│   - Data types: Closing, IC, Dimensional                    │
└─────────────────────────────────────────────────────────────┘
```

## Database Schema

### TS070S0 - Elimination Header

```sql
CREATE TABLE [dbo].[TS070S0] (
    [EliminationHeaderID]     INT            IDENTITY NOT NULL,
    [ConsoID]                 INT            NOT NULL,
    [ElimCode]                NVARCHAR (4)   NOT NULL,   -- e.g., 'U001'
    [ElimType]                CHAR (1)       NOT NULL,   -- 'S'=System, 'U'=User
    [ElimText]                NVARCHAR (25)  NOT NULL,   -- Short description
    [Active]                  BIT            NOT NULL,   -- Enable/disable
    [ElimLevel]               TINYINT        NOT NULL,   -- Processing order
    [JournalSummationID]      INT            NULL,
    [JournalTypeID]           INT            NOT NULL,   -- Target journal
    [JournalText]             NVARCHAR(MAX)  NOT NULL,   -- Long description
    [ConsoMethodSelectionID]  INT            NOT NULL,   -- Company filter
    [Behaviour]               TINYINT        NOT NULL,   -- 0-4
    [MinorityFlag]            BIT            NOT NULL,   -- Include MI data
    [AssociatedJournalTypeID] INT            NULL,       -- Linked T-journal
    [ProcedureName]           VARCHAR (50)   NULL,       -- Custom SP (optional)
    [PostingCompanyType]      CHAR (1)       DEFAULT 'C',-- C=Company, P=Partner
    [PostingCompanyID]        INT            NULL
);
```

### ElimType Values

| Code | Type | Description |
|------|------|-------------|
| **S** | System | Built-in eliminations (S001-S099) |
| **U** | User | User-defined custom eliminations |

### Behaviour Options

| Code | Description | Use Case |
|------|-------------|----------|
| 0 | Standard | Normal elimination processing |
| 1 | Reference period only | Prior period adjustments |
| 2 | Current period only | Current year entries |
| 3 | Both periods | Full period processing |
| 4 | Variation | Period-over-period change |

### TS071S0 - Elimination Line Details

```sql
CREATE TABLE [dbo].[TS071S0] (
    [EliminationDetailID]        INT      IDENTITY NOT NULL,
    [ConsoID]                    INT      NOT NULL,
    [EliminationHeaderID]        INT      NOT NULL,
    [LineNr]                     SMALLINT NOT NULL,

    -- Source Definition
    [FromType]                   TINYINT  NOT NULL,      -- Data source type
    [FromAccountID]              INT      NULL,          -- Specific account
    [FromConsolidationAccountID] INT      NULL,          -- Special account
    [FromAccountSummationID]     INT      NULL,          -- Account group
    [FromPeriod]                 CHAR (1) NOT NULL,      -- C=Current, R=Reference
    [FromFlowID]                 INT      NULL,          -- Specific flow
    [FromConsolidationFlowID]    INT      NULL,          -- Special flow
    [FromFlowSummationID]        INT      NULL,          -- Flow group
    [FromPartnerCompanyID]       INT      NULL,          -- IC partner
    [FromPartnerMethod]          CHAR (1) NULL,          -- G/P/E/N
    [FromDimensionGroupID]       INT      NULL,
    [FromCheck]                  SMALLINT NULL,          -- Sign validation

    -- Target Definition
    [ToType]                     TINYINT  NOT NULL,      -- Target type
    [ToAccountID]                INT      NULL,
    [ToConsolidationAccountID]   INT      NULL,
    [ToSign]                     SMALLINT NOT NULL,      -- 1 or -1
    [ToFlowID]                   INT      NULL,
    [ToConsolidationFlowID]      INT      NULL,
    [ToPartnerCompanyType]       CHAR (1) NULL,          -- P=Partner, C=Company
    [ToPartnerCompanyID]         INT      NULL,
    [ToDimensionGroupID]         INT      NULL,

    -- Percentage Application
    [Percentage]                 TINYINT  NOT NULL,
    [PercentageCustomAccountID]  INT      NULL
);
```

### FromType / ToType Values

| Code | Name | Description | Data Table |
|------|------|-------------|------------|
| 1 | Closing | Closing amounts | TD035C2 (TD030B2 local) |
| 2 | Closing Flow | Flow-level closing | TD045C2 (TD040B2 local) |
| 3 | Closing Dimension | Dimensional closing | TD055C2 (TD050B2 local) |
| 4 | Interco | Intercompany amounts | TD035I2 (TD030I2 local) |
| 5 | Interco Flow | IC flow-level | TD045I2 (TD040I2 local) |
| 6 | Interco Dimension | IC dimensional | TD055I2 (TD050I2 local) |

### Same-as-Source Modifiers

ToType can be modified to carry source attributes:

| Modifier | Added Value | Effect |
|----------|-------------|--------|
| Account SaS | +10 | Target uses source account |
| Flow SaS | +30 | Target uses source flow |
| Account & Flow SaS | +40 | Both carried over |
| Dimension SaS | +60 | Dimension carried over |
| Account & Dimension SaS | +70 | Account + dimension |

**Examples**:
- ToType = 11: Closing with same account as source
- ToType = 32: Closing Flow with same flow as source
- ToType = 41: Closing with same account and flow

### Percentage Options

```sql
-- From extended properties on TS071S0.Percentage:
1 = 100%
2 = 0%

-- Current Period Percentages (TP)
3 = Group Financial Company % TP
4 = Minority Financial Company % TP
5 = Group + Minority Financial Company % TP

6 = Group Financial PartnerCompany % TP
7 = Minority Financial PartnerCompany % TP
8 = Group + Minority Financial PartnerCompany % TP

-- Last Period Percentages (LP)
9 = Group Financial Company % LP
10 = Minority Financial Company % LP
11 = Group + Minority Financial Company % LP

12 = Group Financial PartnerCompany % LP
13 = Minority Financial PartnerCompany % LP
14 = Group + Minority Financial PartnerCompany % LP
```

### FromPeriod Values

| Code | Description |
|------|-------------|
| C | Current period data |
| R | Reference (prior) period data |

### FromCheck - Sign Validation

| Value | Description |
|-------|-------------|
| NULL | No validation |
| 1 | Process only if Amount >= 0 |
| -1 | Process only if Amount < 0 |

## Company Selection Methods

### TS070S1 - Selection Method Configuration

```sql
CREATE TABLE [dbo].[TS070S1] (
    [ConsoMethodSelectionID] INT           IDENTITY NOT NULL,
    [SelectionID]            TINYINT       NOT NULL,
    [SelectionText]          NVARCHAR (50) NOT NULL,
    [Parent]                 BIT           NOT NULL,
    [SelectionCode]          CHAR (1)      NULL,
    [AvailableForSale]       BIT           NULL,
    [FlagDiscontinuing]      BIT           NULL,
    [FlagEnteringScope]      BIT           DEFAULT 0,
    [FlagLeavingScope]       BIT           DEFAULT 0
);
```

### Standard Selection Methods

| ID | Code | Description | Filter |
|----|------|-------------|--------|
| 1 | A | All companies | None |
| 2 | - | Parent only | IsParent = 1 |
| 3 | - | All except parent | IsParent = 0 |
| 4 | G | Global integration | ConsoMethod = 'G' |
| 5 | P | Proportional | ConsoMethod = 'P' |
| 6 | E | Equity method | ConsoMethod = 'E' |
| 7 | N | Not consolidated | ConsoMethod = 'N' |
| 8 | J | Entering companies | FlagEnteringScope = 1 |
| 9 | L | Leaving companies | FlagLeavingScope = 1 |
| 10 | - | Available for sale | AvailableForSale = 1 |
| 11 | - | All except parent and N | Consolidated, not parent |

### Additional Selection IDs (from P_CONSO_ELIM_USER)

| ID | Description |
|----|-------------|
| 15 | All entering companies |
| 16 | All leaving companies |
| 17 | All entering partners |
| 18 | All leaving partners |

## Elimination Processing

### P_CONSO_ELIM_USER Execution Flow

```sql
CREATE PROCEDURE [dbo].[P_CONSO_ELIM_USER]
    @CurConsoID int,
    @RefConsoID int,
    @UserID int,
    @CurCompanyIDs varchar(max),
    @EliminationHeaderID int,
    @SessionID int,
    @errorinfo xml output

-- Processing Steps:
-- 1. Load elimination configuration from TS070S0/TS071S0
-- 2. Build #Companies temp table with scope flags
-- 3. Apply company selection filter
-- 4. For each elimination line:
--    a. Read source amounts based on FromType, FromPeriod
--    b. Apply percentage calculation
--    c. Apply sign (ToSign)
--    d. Post to target account/flow
-- 5. Write results to TMP_TD0XXC2 tables
```

### Company Processing Table

```sql
CREATE TABLE #Companies (
    pk int identity primary key,
    CompanyCurrCode nvarchar(3),
    CurCompanyID int,
    RefCompanyID int,
    CurCompanyGroupPerc decimal(24,6),
    CurCompanyMinorPerc decimal(24,6),
    RefCompanyGroupPerc decimal(24,6),
    RefCompanyMinorPerc decimal(24,6),
    ConsoMethod char(1),
    IsParentCompany bit,
    AvailableForSale bit,
    FlagDiscontinuing bit,
    FlagEntering bit,       -- Entering scope flag
    FlagLeaving bit,        -- Leaving scope flag
    CurCompanyTaxRate decimal(24,6),
    RefCompanyTaxRate decimal(24,6)
);
```

## Configuration Examples

### Example 1: Profit-in-Stock Elimination

**Header (TS070S0)**:
```sql
INSERT INTO TS070S0 (ConsoID, ElimCode, ElimType, ElimText, Active,
                     ConsoMethodSelectionID, Behaviour, MinorityFlag, ...)
VALUES (@ConsoID, 'U001', 'U', 'Stock Margin Elim', 1,
        4, 0, 0, ...)  -- ConsoMethodSelectionID=4 (Global only)
```

**Lines (TS071S0)**:
```sql
-- Line 1: Read intercompany sales
INSERT INTO TS071S0 (EliminationHeaderID, LineNr, FromType, FromAccountID,
                     FromPeriod, ToType, ToAccountID, ToSign, Percentage)
VALUES (@HeaderID, 1,
        4, @IC_Sales_AccountID,  -- FromType=4 (Interco)
        'C',                      -- Current period
        1, @StockMargin_AccountID, -1, 1)  -- ToType=1, Reverse, 100%

-- Line 2: Credit reserves
INSERT INTO TS071S0 (...)
VALUES (@HeaderID, 2,
        4, @IC_Sales_AccountID,
        'C',
        1, @Reserves_AccountID, 1, 1)  -- Credit
```

### Example 2: Deferred Tax Adjustment

```sql
-- Header
INSERT INTO TS070S0 (..., ElimCode, ConsoMethodSelectionID, ...)
VALUES (..., 'U002', 11, ...)  -- All except parent and N

-- Detail: Apply tax rate
INSERT INTO TS071S0 (..., Percentage, ...)
VALUES (..., 1, ...)  -- 100%
-- Or use custom account for rate lookup:
VALUES (..., @TaxRateAccountID, ...)
```

### Example 3: Entering Company Goodwill

```sql
-- Header targeting entering companies only
INSERT INTO TS070S0 (..., ConsoMethodSelectionID, ...)
VALUES (..., 8, ...)  -- SelectionID 8 = Entering

-- Detail lines for goodwill calculation
INSERT INTO TS071S0 (...)
VALUES (...)
```

## Processing Integration

### Elimination Execution Sequence

User eliminations are executed as part of the consolidation elimination phase:

```sql
-- From P_CONSO_ELIM.sql
-- Loop through all active eliminations
CURSOR CR_ELIM FOR
    SELECT EliminationHeaderID, ElimCode, ElimType, Active,
           ProcedureName, JournalTypeID, JournalType, JournalCategory
    FROM TS070S0
    WHERE ConsoID = @ConsoID
      AND Active = 1
    ORDER BY ElimLevel, ElimCode

-- For U-type eliminations:
IF @ElimType = 'U' AND @ProcedureName IS NULL
    EXEC dbo.P_CONSO_ELIM_USER @CurConsoID, @RefConsoID, @UserID,
                                @CurCompanyIDs, @EliminationHeaderID, ...
```

## Business Impact

### Current Capabilities

1. **Fully Configurable**: No code changes needed for new eliminations
2. **Complex Scenarios**: Multi-line, multi-account, multi-flow support
3. **Period Awareness**: Current vs reference period handling
4. **Percentage Flexibility**: Multiple percentage application options
5. **Scope Filtering**: Target specific company types
6. **Dimensional Support**: Handle dimensional data eliminations

### Use Cases

| Scenario | Configuration Approach |
|----------|----------------------|
| Stock margins | IC amounts → Reserves |
| Deferred tax | Tax base × Rate |
| Goodwill allocation | Participation → Asset accounts |
| Management adjustments | Manual entries at group level |
| Method change effects | Period-specific adjustments |
| Intercompany pricing | IC amounts at percentage |

### Operational Considerations

1. **Configuration Testing**: Test new eliminations in sandbox
2. **Line Sequencing**: Order lines logically (LineNr)
3. **Sign Conventions**: Verify ToSign for correct impact
4. **Percentage Selection**: Choose appropriate percentage type
5. **Period Selection**: Match FromPeriod to business logic

## See Also

### Related Eliminations
- [Elimination Templates](elimination-templates.md) - Configuration patterns
- [Profit-in-Stock Eliminations](profit-in-stock-eliminations.md) - Stock margin use case
- [Participation Eliminations](participation-eliminations.md) - System elimination example
- [Dividend Eliminations](dividend-eliminations.md) - Dividend entries

### Related Gap Workarounds
- [Treasury Shares](../03-core-calculations/treasury-shares.md) - GAP workaround
- [Step Acquisition](../03-core-calculations/step-acquisition.md) - GAP workaround
- [Preference Shares](../03-core-calculations/preference-shares.md) - GAP workaround
- [Impairment Testing](../03-core-calculations/impairment-testing.md) - GAP workaround
- [Hyperinflation Accounting](../05-currency-translation/hyperinflation-accounting.md) - GAP workaround

### Related Database
- [Journal Types](../07-database-implementation/journal-types.md) - Journal assignment
- [Data Tables Catalog](../07-database-implementation/data-tables-catalog.md) - TS070S0/TS071S0 tables

### Navigation
- [Cross-Reference Index](../00-index/CROSS_REFERENCE_INDEX.md) - Full document relationships
- [Executive Summary](../00-index/EXECUTIVE_SUMMARY.md) - Overview

## API Reference

### Primary API Handlers
| Handler | YAML File | Purpose | Status |
|---------|-----------|---------|--------|
| `Consolidation_Execute` | [api-consolidation-endpoints.yaml](../11-agent-support/api-consolidation-endpoints.yaml) | Trigger P_CONSO_ELIM_USER processing | ✅ IMPLEMENTED |
| `Elimination_GetEliminations` | [api-elimination-endpoints.yaml](../11-agent-support/api-elimination-endpoints.yaml) | Get user elimination configuration | ✅ IMPLEMENTED |
| `Elimination_SaveElimination` | [api-elimination-endpoints.yaml](../11-agent-support/api-elimination-endpoints.yaml) | Create/update elimination rules | ✅ IMPLEMENTED |

### Supporting API Handlers
| Handler | YAML File | Purpose |
|---------|-----------|---------|
| `JournalType_GetJournalTypes` | [api-journal-endpoints.yaml](../11-agent-support/api-journal-endpoints.yaml) | Get target journal options |
| `Account_GetAccounts` | [api-account-endpoints.yaml](../11-agent-support/api-account-endpoints.yaml) | Get account options for FromAccountID/ToAccountID |
| `Flow_GetFlows` | [api-flow-endpoints.yaml](../11-agent-support/api-flow-endpoints.yaml) | Get flow options for FromFlowID/ToFlowID |

### API Workflow
```
User Elimination Configuration via API:

1. DEFINE ELIMINATION HEADER
   Elimination_SaveElimination → Insert TS070S0:
     - ElimCode (U001, U002, etc.)
     - ElimType = 'U' (User)
     - ConsoMethodSelectionID (company filter)
     - Behaviour (0-4 period mode)
     - JournalTypeID (target journal)

2. DEFINE ELIMINATION LINES
   Elimination_SaveElimination → Insert TS071S0:
     - FromType (1-6: Closing/Flow/Dimension/IC variants)
     - FromAccountID, FromPeriod (C/R)
     - ToType (1-76 with SaS modifiers)
     - ToAccountID, ToSign, Percentage

3. EXECUTION
   Consolidation_Execute → P_CONSO_ELIM → P_CONSO_ELIM_USER:
     - Load configuration from TS070S0/TS071S0
     - Build #Companies with scope flags
     - Process each line: Read source → Apply % → Post target

4. VERIFICATION
   Elimination_GetEliminations → Review posted entries
```

### Configuration Reference Tables
| Table | Purpose | Key Columns |
|-------|---------|-------------|
| TS070S0 | Elimination headers | ElimCode, ElimType, Behaviour, ConsoMethodSelectionID |
| TS071S0 | Elimination details | FromType, FromAccountID, ToType, ToAccountID, Percentage |
| TS070S1 | Company selection methods | SelectionID, SelectionCode (A/G/P/E/N/J/L) |

### Related API Documentation
- [API Index](../11-agent-support/api-index.yaml) - Master handler catalog
- [Gap Analysis](../11-agent-support/gap-analysis-report.yaml) - **FULLY IMPLEMENTED (100%)**

---
*Document 24 of 50+ | Batch 8: Core System Mechanics | Last Updated: 2024-12-01*
