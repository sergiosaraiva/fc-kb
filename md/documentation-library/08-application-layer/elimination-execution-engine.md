# Elimination Execution Engine: P_CONSO_ELIM Architecture

## Document Metadata
- **Category**: Application Layer
- **Theory Source**: Implementation-specific (Consolidation execution orchestration)
- **Implementation Files**:
  - `Sigma.Database/dbo/Stored Procedures/P_CONSO_ELIM.sql` - Main orchestrator (905 lines)
  - `Sigma.Database/dbo/Stored Procedures/P_CONSO_ELIM_*.sql` - 22 elimination procedures
  - `Sigma.Database/dbo/Tables/TS070S0.sql` - Elimination configuration
  - `Sigma.Database/dbo/Tables/TS020S0.sql` - Journal type definitions
- **Last Updated**: 2024-12-01
- **Completeness**: 100% (Full documentation of execution engine)
- **Compliance Status**: Implementation architecture document

## Executive Summary

The Elimination Execution Engine (`P_CONSO_ELIM`) is the central orchestrator for all consolidation eliminations in Prophix.Conso. It coordinates the execution of 22+ specialized elimination procedures (S-type) and user-defined eliminations (U-type) in a configurable sequence. The engine handles company selection, journal management, session control, and result aggregation into temporary tables for subsequent posting to permanent consolidated data tables.

## Architecture Overview

### Component Hierarchy

```
┌─────────────────────────────────────────────────────────────────────┐
│                    CONSOLIDATION WORKFLOW                           │
│   (Initiated by UI or scheduled job)                               │
└─────────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    P_CONSO_ELIM                                      │
│                    (Main Orchestrator)                               │
│   - Session management                                               │
│   - Company list preparation                                         │
│   - Elimination sequence control                                     │
│   - Journal deletion/creation                                        │
│   - Result aggregation                                               │
└─────────────────────────────────────────────────────────────────────┘
            │                       │                        │
            ▼                       ▼                        ▼
┌────────────────────┐  ┌────────────────────┐  ┌────────────────────┐
│  System Elims (S)  │  │  User Elims (U)    │  │ Dimension Elims    │
│  22+ procedures    │  │  P_CONSO_ELIM_USER │  │ P_CONSO_DIM_*      │
└────────────────────┘  └────────────────────┘  └────────────────────┘
            │                       │                        │
            └───────────────────────┴────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    TMP_TD0XXC2 Tables                                │
│   (Session-based temporary results)                                 │
└─────────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    TD035C2, TD045C2, TD055C2                        │
│   (Permanent consolidated data)                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### System Elimination Procedures (S-Type)

| Procedure | ElimCode | Description | Journal |
|-----------|----------|-------------|---------|
| `P_CONSO_ELIM_INTERCOMPANY` | S001 | Intercompany netting | TC |
| `P_CONSO_ELIM_INTERCOMPANY_100PC` | S002 | 100% IC elimination | TC |
| `P_CONSO_ELIM_INTERCOMPANY_NE` | S003 | Non-equity IC | TC |
| `P_CONSO_ELIM_INTERCOMPANY_NETTING` | S004 | IC netting full | TC |
| `P_CONSO_ELIM_INTERCOMPANY_NETTING_FULL` | S005 | Complete netting | TC |
| `P_CONSO_ELIM_PARTICIPATIONS0` | S010 | Participation elim phase 0 | TE |
| `P_CONSO_ELIM_PARTICIPATIONS1` | S011 | Participation elim phase 1 | TE |
| `P_CONSO_ELIM_PARTICIPATIONS2` | S012 | Participation elim phase 2 | TE |
| `P_CONSO_ELIM_PARTICIPATIONS3` | S013 | Participation elim phase 3 | TE |
| `P_CONSO_ELIM_PARTICIPATIONS4` | S014 | Participation elim phase 4 | TE |
| `P_CONSO_ELIM_EQUITYCAPITAL` | S020 | Equity capital elimination | TE |
| `P_CONSO_ELIM_EQUITYMETHOD` | S030 | Equity method processing | TM |
| `P_CONSO_ELIM_PROPORTIONAL` | S040 | Proportional method | TP |
| `P_CONSO_ELIM_DIVIDEND` | S050 | Dividend eliminations | TD |
| `P_CONSO_ELIM_MINORITYINTEREST` | S060 | Minority interest calc | TI |
| `P_CONSO_ELIM_CHANGE_METHOD` | S070 | Method change handling | TX |
| `P_CONSO_ELIM_NOTCONSOLIDATED` | S080 | Non-consolidated exclusion | TN |
| `P_CONSO_ELIM_EPU` | S090 | EPU processing | TU |
| `P_CONSO_ELIM_EPU_REVERSE` | S094 | EPU reversal | TU |
| `P_CONSO_ELIM_USER` | - | User-defined framework | User-defined |
| `P_CONSO_ELIM_USER_PROCESS` | - | User elim execution | User-defined |
| `P_CONSO_ELIM_USER_FROM_DATA` | - | Data-driven user elim | User-defined |

## P_CONSO_ELIM Detailed Flow

### Input Parameters

```sql
CREATE PROCEDURE [dbo].[P_CONSO_ELIM]
    @UserID           INT,              -- Executing user
    @ConsoID          INT,              -- Current consolidation ID
    @CompanyIDs       VARCHAR(MAX) = NULL,  -- Company filter (null = all)
    @ExecuteDimensions BIT = 0,         -- Process dimensional data
    @Debug            BIT = 0,          -- Debug mode
    @errorinfo        XML OUTPUT        -- Error/warning collection
```

### Execution Phases

#### Phase 1: Initialization (Lines 1-150)

```sql
-- Create session-scoped temp tables
CREATE TABLE #AllCompanies (
    pk                      INT IDENTITY PRIMARY KEY,
    CompanyID               INT,
    CompanyCode             NVARCHAR(12),
    ConsoMethod             CHAR(1),
    ConsolidatedCompany     BIT,
    GroupPerc               DECIMAL(20,6),
    MinorPerc               DECIMAL(20,6),
    JournalEntry            INT,
    IncludedInCompanySelection BIT,
    RefCompanyID            INT,
    RefConsoMethod          CHAR(1),
    RefGroupPerc            DECIMAL(20,6),
    RefMinorPerc            DECIMAL(20,6),
    AlternateEntry          INT,
    SortOrder               INT
);

CREATE TABLE #JournalsToDelete (
    JournalTypeID           INT,
    CompanyID               INT,
    JournalEntry            INT
);

-- Get reference consolidation ID for period comparison
SELECT @RefConsoID = RefConsoID
FROM dbo.TS096S0
WHERE ConsoID = @ConsoID;

-- Get special flow IDs
SELECT @UNEXPVarFlowID = dbo.UDF_GET_SPECIAL_FLOW(@ConsoID, 'UNEXPVAR');
SELECT @NETVarFlowID = dbo.UDF_GET_SPECIAL_FLOW(@ConsoID, 'NETVAR');
SELECT @PreviousPeriodAdjFlowID = dbo.UDF_GET_SPECIAL_FLOW(@ConsoID, 'PREVIOUSPERIODADJ');
```

#### Phase 2: Company List Preparation (Lines 406-456)

```sql
-- Get all companies in consolidation scope
INSERT INTO #AllCompanies (CompanyID, CompanyCode, ConsoMethod, ...)
SELECT  a.CompanyID,
        a.CompanyCode,
        a.ConsoMethod,
        a.ConsolidatedCompany,
        a.GroupPerc,
        a.MinorPerc,
        b.JournalEntry,
        CASE WHEN @CompanyIDs IS NULL THEN 1 ELSE 0 END,
        0,      -- RefCompanyID
        'N',    -- RefConsoMethod
        0,      -- RefGroupPerc
        0,      -- RefMinorPerc
        ROW_NUMBER() OVER (ORDER BY a.CompanyCode),
        ROW_NUMBER() OVER (ORDER BY a.CompanyCode)
FROM    dbo.TS014C0 a WITH(NOLOCK)
        INNER JOIN dbo.T_JOURNAL_ENTRY_MAP b WITH(NOLOCK)
            ON (b.ConsoID = @ConsoID AND b.CompanyID = a.CompanyID
                AND b.CompanyOwnedID IS NULL)
WHERE   a.ConsoID = @ConsoID
        AND a.ConsolidatedCompany = 1;

-- Get reference period percentages for scope change detection
UPDATE a
SET RefCompanyID = b.CompanyID,
    RefConsoMethod = ISNULL(b.ConsoMethod, 'N'),
    RefGroupPerc = ISNULL(b.GroupPerc, 0),
    RefMinorPerc = ISNULL(b.MinorPerc, 0)
FROM #AllCompanies a
INNER JOIN dbo.TS014C0 b WITH(NOLOCK)
    ON b.CompanyCode = a.CompanyCode AND b.ConsoID = @RefConsoID;
```

#### Phase 3: Validation (Lines 489-512)

```sql
-- Check bundle integration status
SELECT @BundlesNotDoneCount = COUNT(CompanyID)
FROM dbo.TS014C0 WITH(NOLOCK)
WHERE ConsoID = @ConsoID
  AND Status_Bundles = 1
  AND ConsolidatedCompany = 1;

IF @BundlesNotDoneCount > 0
    SET @errorinfo = dbo.AddWarning0('P_CONSO_ELIM_BUNDLE_INTEGRATION_FIRST', @errorinfo);

-- Check adjustments status
SELECT @AdjustmentsNotDoneCount = COUNT(CompanyID)
FROM dbo.TS014C0 WITH(NOLOCK)
WHERE ConsoID = @ConsoID
  AND Status_Adjustments = 1
  AND ConsolidatedCompany = 1;

IF @AdjustmentsNotDoneCount > 0
    SET @errorinfo = dbo.AddWarning0('P_CONSO_ELIM_ADJ_INTEGRATION_FIRST', @errorinfo);
```

#### Phase 4: Elimination Cursor Loop (Lines 572-782)

```sql
-- Create cursor over active eliminations
DECLARE CR_ELIM CURSOR STATIC FOR
    SELECT  a.EliminationHeaderID,
            a.ElimCode,
            a.ElimType,
            a.Active,
            a.ProcedureName,
            a.JournalTypeID,
            b.JournalType,
            b.JournalCategory
    FROM    dbo.TS070S0 a WITH(NOLOCK)
            INNER JOIN dbo.TS020S0 b WITH(NOLOCK)
                ON (b.ConsoID = a.ConsoID AND b.JournalTypeID = a.JournalTypeID)
    WHERE   a.ConsoID = @ConsoID
            AND a.ElimCode <> 'S001'  -- S001 handled separately
            AND a.Active = 1
    ORDER BY a.ElimLevel, a.ElimCode;

OPEN CR_ELIM;

-- Process each elimination
WHILE (@@FETCH_STATUS = 0)
BEGIN
    IF @ElimType = 'S' AND @ProcedureName IS NOT NULL
    BEGIN
        -- System elimination: Dynamic execution
        SET @SQL = 'exec dbo.' + @ProcedureName +
            ' @Login, @SessionID, @ConsoID, @RefConsoID, ' +
            '@PreviousPeriodAdjFlowID, @ConsoCurrCode, @ParentCompanyID, ' +
            '@JournalTypeS001ID, @UNEXPVarFlowID, @NETVarFlowID, ' +
            '@ExecuteDimensions, @Debug, @errorinfo output';

        EXEC sp_executesql @SQL, @SQLParams, ...;
    END
    ELSE IF @ElimType = 'U'
    BEGIN
        -- User elimination: Call generic processor
        EXEC [dbo].[P_CONSO_ELIM_USER]
            @CurConsoID = @ConsoID,
            @RefConsoID = @RefConsoID,
            @UserID = @UserID,
            @CurCompanyIDs = @CompanyIDs,
            @EliminationHeaderID = @EliminationHeaderID,
            @SessionID = @SessionID,
            @JournalTypeS001ID = @JournalTypeS001ID,
            @errorinfo = @errorinfo OUTPUT,
            @Debug = @Debug;
    END

    FETCH NEXT FROM CR_ELIM INTO ...;
END;

CLOSE CR_ELIM;
DEALLOCATE CR_ELIM;
```

#### Phase 5: Journal Cleanup (Lines 831-950)

```sql
-- Prepare deletion lists
INSERT INTO @TD035C2ToDelete (_ConsolidatedAmountID)
SELECT  a.ConsolidatedAmountID
FROM    dbo.TD035C2 a WITH(NOLOCK)
        INNER JOIN #JournalsToDelete b
            ON (b.JournalTypeID = a.JournalTypeID
                AND (b.CompanyID IS NULL OR b.CompanyID = a.CompanyID)
                AND (b.JournalEntry IS NULL OR b.JournalEntry = a.JournalEntry))
WHERE   a.ConsoID = @ConsoID;

-- Delete old elimination journals
DELETE FROM dbo.TD055C2 WHERE ConsoID = @ConsoID
    AND ConsolidatedAmountID IN (SELECT _ConsolidatedAmountID FROM @TD035C2ToDelete);

DELETE FROM dbo.TD045C2 WHERE ConsoID = @ConsoID
    AND ConsolidatedFlowsID IN (SELECT _ConsolidatedFlowsID FROM @TD045C2ToDelete);

DELETE FROM dbo.TD035C2 WHERE ConsoID = @ConsoID
    AND ConsolidatedAmountID IN (SELECT _ConsolidatedAmountID FROM @TD035C2ToDelete);
```

#### Phase 6: Result Posting (Lines 950-end)

```sql
-- Insert new elimination results from temp tables
INSERT INTO dbo.TD035C2 (ConsoID, CompanyID, JournalTypeID, JournalEntry, ...)
SELECT  @ConsoID, CompanyID, JournalTypeID, JournalEntry, ...
FROM    dbo.TMP_TD035C2
WHERE   SessionID = @SessionID;

INSERT INTO dbo.TD045C2 (ConsoID, CompanyID, JournalTypeID, JournalEntry, FlowID, ...)
SELECT  @ConsoID, CompanyID, JournalTypeID, JournalEntry, FlowID, ...
FROM    dbo.TMP_TD045C2
WHERE   SessionID = @SessionID;

-- Clean up temp tables
DELETE FROM dbo.TMP_TD035C2 WHERE SessionID = @SessionID;
DELETE FROM dbo.TMP_TD045C2 WHERE SessionID = @SessionID;
```

## Standard Elimination Procedure Interface

All S-type procedures follow a standard interface:

```sql
CREATE PROCEDURE [dbo].[P_CONSO_ELIM_XXXXX]
    @Login                  NVARCHAR(256),
    @SessionID              INT,
    @ConsoID                INT,
    @RefConsoID             INT,
    @PreviousPeriodAdjFlowID INT,
    @ConsoCurrCode          NVARCHAR(3),
    @ParentCompanyID        INT,
    @JournalTypeS001ID      INT,
    @UNEXPVarFlowID         INT,
    @NETVarFlowID           INT,
    @ExecuteDimensions      BIT,
    @Debug                  BIT,
    @errorinfo              XML OUTPUT
AS
BEGIN
    -- Common initialization
    -- Company selection based on ConsoMethod
    -- Source data retrieval
    -- Elimination calculation
    -- Result writing to TMP_TD0XXC2
END
```

## Journal Type Management

### Journal Categories

| Type | Category | Description |
|------|----------|-------------|
| T | C | Technical - Intercompany |
| T | E | Technical - Equity/Participation |
| T | I | Technical - Minority Interest |
| T | M | Technical - Equity Method |
| T | P | Technical - Proportional |
| T | D | Technical - Dividends |
| T | X | Technical - Method Change |
| T | U | Technical - User Defined |

### Duplicate Journal Detection

```sql
-- Check if journal type is used by multiple eliminations
SELECT  @JournalInUse = CASE
            WHEN SUM(CASE WHEN EliminationHeaderID <> @EliminationHeaderID
                          THEN 1 ELSE 0 END) > 0
            THEN 1 ELSE 0 END,
        @JournalInUseInSystem = CASE
            WHEN SUM(CASE WHEN EliminationHeaderID <> @EliminationHeaderID
                          AND ElimType = 'S' THEN 1 ELSE 0 END) > 0
            THEN 1 ELSE 0 END,
        @IsFirstOfDuplicatedJournal = CASE
            WHEN MIN(EliminationHeaderID) = @EliminationHeaderID
            THEN 1 ELSE 0 END
FROM dbo.TS070S0 WITH(NOLOCK)
WHERE ConsoID = @ConsoID
  AND JournalTypeID = @JournalTypeID
  AND Active = 1;

-- Warning if duplicate (but continue)
IF @JournalInUse = 1 AND @IsFirstOfDuplicatedJournal = 1
    SET @errorinfo = dbo.AddWarning1('P_CONSO_ELIM_MULTIPLE_JOURNAL',
                                     @JournalType + @JournalCategory, @errorinfo);

-- Skip if another system elimination uses same journal
IF @JournalInUseInSystem = 1
    GOTO FetchNextFromCursor;
```

## Temporary Tables Architecture

### Session-Based Isolation

```sql
-- Each elimination session uses unique SessionID
-- Results written to TMP_ tables with SessionID

CREATE TABLE [dbo].[TMP_TD035C2] (
    SessionID           INT NOT NULL,
    ConsoID             INT NOT NULL,
    CompanyID           INT NOT NULL,
    JournalTypeID       INT NOT NULL,
    JournalEntry        INT NOT NULL,
    AccountID           INT NOT NULL,
    Amount              DECIMAL(28,6),
    ...
);

CREATE TABLE [dbo].[TMP_TD045C2] (
    SessionID           INT NOT NULL,
    ConsoID             INT NOT NULL,
    CompanyID           INT NOT NULL,
    JournalTypeID       INT NOT NULL,
    JournalEntry        INT NOT NULL,
    FlowID              INT NOT NULL,
    AccountID           INT NOT NULL,
    Amount              DECIMAL(28,6),
    PartnerCompanyID    INT,
    ...
);
```

## Debug Mode

When `@Debug = 1`:

```sql
-- Performance tracking
IF @Debug = 1
    EXEC dbo.P_SYS_DEBUG_PRINT @ProcedureName, @StartTime, @LastTime OUTPUT;

-- Balance validation
IF @Debug = 1
BEGIN
    IF EXISTS (
        SELECT JournalType, JournalCategory, JournalEntry, SUM(Amount)
        FROM dbo.TMP_TD035C2 a WITH(NOLOCK)
             INNER JOIN dbo.TS020S0 b ON (b.JournalTypeID = a.JournalTypeID)
             INNER JOIN dbo.TS010S0 c ON (c.AccountID = a.AccountID
                                          AND c.AccountType IN ('B', 'P', 'C'))
        WHERE a.SessionID = @SessionID
        GROUP BY JournalType, JournalCategory, JournalEntry
        HAVING SUM(Amount) <> 0
    )
    BEGIN
        EXEC dbo.P_SYS_DEBUG_PRINT 'T journals not in balance - TD035C2',
                                   @StartTime, @LastTime OUTPUT;
    END
END
```

## Error Handling

### Error Collection Pattern

```sql
-- Errors are accumulated in XML output
SET @errorinfo = dbo.AddError1('ELIMINATION_S001_NOT_FOUND',
                               'Intercompany elimination (general)', @errorinfo);

SET @errorinfo = dbo.AddError2('PROCEDURE_NOT_FOUND',
                               @ElimCode, @ProcedureName, @errorinfo);

SET @errorinfo = dbo.AddWarning0('ParentCompanyIsEmpty', @errorinfo);

-- Check for errors before continuing
IF dbo.HasError(@errorinfo) = 1
    GOTO CleanupAndEnd;

IF dbo.HasWarning(@errorinfo) = 1 OR dbo.HasError(@errorinfo) = 1
    GOTO CleanupAndEnd;
```

## API Reference

### Primary API Handlers
| Handler | YAML File | Purpose | Status |
|---------|-----------|---------|--------|
| `Consolidation_Execute` | [api-consolidation-endpoints.yaml](../11-agent-support/api-consolidation-endpoints.yaml) | Trigger P_CONSO_ELIM | ✅ IMPLEMENTED |
| `Elimination_GetEliminations` | [api-elimination-endpoints.yaml](../11-agent-support/api-elimination-endpoints.yaml) | Get TS070S0 configuration | ✅ IMPLEMENTED |

### Elimination Procedure-to-API Mapping
| Procedure | ElimCode | Triggered By |
|-----------|----------|--------------|
| P_CONSO_ELIM | Orchestrator | Consolidation_Execute |
| P_CONSO_ELIM_DIVIDEND | S020 | P_CONSO_ELIM cursor |
| P_CONSO_ELIM_EQUITYMETHOD | S081 | P_CONSO_ELIM cursor |
| P_CONSO_ELIM_MINORITYINTEREST | S085 | P_CONSO_ELIM cursor |
| P_CONSO_ELIM_USER | U-type | P_CONSO_ELIM cursor |

### Related API Documentation
- [API Index](../11-agent-support/api-index.yaml) - Master handler catalog
- [Gap Analysis](../11-agent-support/gap-analysis-report.yaml) - **FULLY IMPLEMENTED (100%)**

---

## Related Documentation

- [User-Defined Eliminations](../04-elimination-entries/user-eliminations.md) - TS070S0/TS071S0 configuration
- [Intercompany Transactions](../04-elimination-entries/intercompany-transactions.md) - S001-S005
- [Participation Eliminations](../04-elimination-entries/participation-eliminations.md) - S010-S014
- [Journal Types](../07-database-implementation/journal-types.md) - Journal classification
- [Consolidation Services](consolidation-services.md) - Application layer integration

### Navigation
- [Cross-Reference Index](../00-index/CROSS_REFERENCE_INDEX.md) - Find related documents
- [Quick Reference Card](../20-appendices/quick-reference-card.md) - Elimination codes
- [Troubleshooting Guide](../17-troubleshooting/common-issues.md) - Elimination issues
- [Glossary](../20-appendices/glossary.md) - Term definitions

---
*Document 30 of 50+ | Batch 10: Execution Layer | Last Updated: 2024-12-01*
*Implementation Reference - P_CONSO_ELIM.sql (905 lines)*
