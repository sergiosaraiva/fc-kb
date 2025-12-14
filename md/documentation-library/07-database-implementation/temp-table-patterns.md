# Temp Table Patterns: TMP_* Table Architecture

## Document Metadata
- **Category**: Database Implementation
- **Theory Source**: Implementation-specific (Session-based temporary storage)
- **Implementation Files**:
  - `Sigma.Database/dbo/Tables/TMP_*.sql` - 80+ persistent temp tables
  - `Sigma.Database/dbo/Tables/TL010S0.sql` - Session management table
  - Various stored procedures using temp tables
- **Last Updated**: 2024-12-01
- **Completeness**: 100% (Full temp table architecture documented)
- **Compliance Status**: Database architecture reference

## Executive Summary

Prophix.Conso uses a sophisticated temporary table architecture with 80+ persistent "TMP_*" tables for session-isolated data processing. Unlike SQL Server's native temporary tables (#temp), these are permanent tables with SessionID-based isolation, enabling complex multi-step consolidation processing while maintaining data integrity across long-running operations.

## Temp Table Architecture Overview

### Design Philosophy

```
┌─────────────────────────────────────────────────────────────────┐
│                    TMP_* Table Architecture                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  WHY PERSISTENT TEMP TABLES?                                     │
│  ├── Session isolation via SessionID                            │
│  ├── Automatic cleanup via FK CASCADE DELETE                    │
│  ├── Cross-procedure data sharing                               │
│  ├── Debugging capability (data persists on error)              │
│  └── Complex multi-step processing support                      │
│                                                                  │
│  SESSION MANAGEMENT                                              │
│  ┌─────────────┐                                                │
│  │ TL010S0     │ ← Session master table                         │
│  │ (Sessions)  │                                                │
│  └──────┬──────┘                                                │
│         │ FK CASCADE DELETE                                      │
│         ├──────────────────────────────────────────────         │
│         ▼                                                        │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐             │
│  │TMP_TD035C2  │  │TMP_TD045C2  │  │TMP_CONSO_*  │  ...        │
│  └─────────────┘  └─────────────┘  └─────────────┘             │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Session Management (TL010S0)

```sql
-- Session master table
CREATE TABLE [dbo].[TL010S0] (
    [SessionID] INT IDENTITY(1,1) NOT NULL,
    [CustomerID] INT NOT NULL,
    [UserID] INT NULL,
    [CreationDate] DATETIME NOT NULL DEFAULT GETDATE(),
    [LastActivityDate] DATETIME NOT NULL DEFAULT GETDATE(),
    [SessionType] VARCHAR(50) NULL,
    CONSTRAINT [PK_TL010S0] PRIMARY KEY ([SessionID])
)

-- All TMP_* tables reference this with CASCADE DELETE
CONSTRAINT [FK_TMP_xxx_TL010S0] FOREIGN KEY ([SessionID])
    REFERENCES [dbo].[TL010S0] ([SessionID]) ON DELETE CASCADE
```

## TMP_* Table Categories

### Consolidation Processing Tables

| Table | Purpose |
|-------|---------|
| TMP_TD035C2 | Consolidated closing amounts staging |
| TMP_TD045C2 | Consolidated flow amounts staging |
| TMP_TD040B2 | Bundle flow staging |
| TMP_TD040I2 | Intercompany flow staging |
| TMP_TD055C2 | Dimensional consolidated amounts |
| TMP_TD033E0 | Group adjustment staging |
| TMP_CONSO_EXCHANGERATE | Exchange rate cache |
| TMP_CONSO_COMPANYID | Company list for processing |
| TMP_CONSO_MATCHING | IC matching results |
| TMP_CONSO_SPECIAL_DIMENSION_DETAILS | Dimension processing |
| TMP_TS015S0 | Ownership staging |
| TMP_SUBGROUP_PERCENTAGES | Sub-group ownership |

### Import Processing Tables

| Table Pattern | Purpose |
|---------------|---------|
| TMP_IMPORT{Entity}_DETAILS | Raw imported data |
| TMP_IMPORT{Entity}_MAPPINGS | Code-to-ID mappings |
| TMP_IMPORT{Entity}_ERRORS | Validation errors |

**Entity Types**: Data, Adjustments, ExchangeRate, Accounts, Companies, Flows, Ownership, Structure, Translations, Bundle, CustomReports, MappingTables, DimensionDetails, AddInfoData

### Export Processing Tables

| Table | Purpose |
|-------|---------|
| TMP_EXPORTDATA | Data export staging |
| TMP_EXPORTDATA_DETAILS | Export detail records |
| TMP_EXPORTADJUSTMENTS | Adjustment export |
| TMP_EXPORTEXCHANGERATE | Exchange rate export |
| TMP_EXPORTSTRUCTURE | Structure export |
| TMP_EXPORTTRANSLATION | Translation export |

### Validation and Reporting Tables

| Table | Purpose |
|-------|---------|
| TMP_VALIDATION_REPORT_RULE | Validation rule results |
| TMP_VALIDATION_REPORT_RULE_DETAIL | Validation details |
| TMP_EVENT_GENERIC | Event processing |
| TMP_BULK_IMPORT_* | Bulk import processing |

## TMP_TD035C2 Deep Dive

### Table Structure

```sql
CREATE TABLE [dbo].[TMP_TD035C2] (
    [TmpConsolidatedAmountID] BIGINT IDENTITY(1,1) NOT NULL,
    [SessionID] INT NOT NULL,              -- Session isolation
    [CompanyID] INT NOT NULL,
    [JournalTypeID] INT NOT NULL,
    [JournalEntry] BIGINT NOT NULL,
    [JournalSequence] INT NOT NULL,
    [AccountID] INT NOT NULL,
    [PartnerCompanyID] INT NULL,
    [CurrCode] NVARCHAR(3) NOT NULL,
    [Amount] DECIMAL(24,6) NOT NULL,
    [FlowAmount] DECIMAL(24,6) NULL,
    [TransactionCurrCode] NVARCHAR(3) NULL,
    [TransactionAmount] DECIMAL(24,6) NULL,
    [ConvertedAmount] DECIMAL(24,6) NULL,
    [ConvertedFlow] DECIMAL(24,6) NULL,
    [FlowDifference] DECIMAL(24,6) NULL,
    [RateType] CHAR(2) NULL,
    [FlowID] INT NULL,
    [TransRate] DECIMAL(28,12) NULL,
    [MinorityFlag] BIT NULL,
    [ReferencePK] INT NULL,
    [ConsoID] INT NULL,
    [FlowsType] TINYINT NULL,
    [OriginalCurrCode] NVARCHAR(3) NULL,
    [Step] SMALLINT NULL,                  -- Processing step tracking
    [AmountPreviousMonthLC] DECIMAL(24,6) NULL,
    [AmountPreviousMonthGC] DECIMAL(24,6) NULL,

    CONSTRAINT [PK_TMP_TD035C2] PRIMARY KEY NONCLUSTERED
        ([TmpConsolidatedAmountID]) WITH (FILLFACTOR = 80),
    CONSTRAINT [FK_TMP_TD035C2_TL010S0] FOREIGN KEY ([SessionID])
        REFERENCES [dbo].[TL010S0] ([SessionID]) ON DELETE CASCADE
);

-- Clustered index for efficient step-based processing
CREATE CLUSTERED INDEX [IX_TMP_TD035C2_2]
    ON [dbo].[TMP_TD035C2]([SessionID] ASC, [Step] ASC);
```

### Usage in Consolidation

```sql
-- Step-based processing pattern
-- Step 1: Load raw data
INSERT INTO TMP_TD035C2 (SessionID, Step, ...)
SELECT @SessionID, 1, ...
FROM TD030B2

-- Step 2: Currency translation
UPDATE TMP_TD035C2
SET ConvertedAmount = Amount * @ExchangeRate,
    Step = 2
WHERE SessionID = @SessionID AND Step = 1

-- Step 3: Apply eliminations
INSERT INTO TMP_TD035C2 (SessionID, Step, ...)
SELECT @SessionID, 3, ...
FROM elimination_calculation

-- Final: Move to permanent storage
INSERT INTO TD035C2
SELECT ... FROM TMP_TD035C2
WHERE SessionID = @SessionID
```

## TMP_CONSO_EXCHANGERATE Pattern

### Table Structure

```sql
CREATE TABLE [dbo].[TMP_CONSO_EXCHANGERATE] (
    [TmpConsoExchangeRateID] INT IDENTITY(1,1) NOT NULL,
    [SessionID] INT NOT NULL,
    [FromCurrCode] NVARCHAR(3) NOT NULL,
    [ClosingRateCur] DECIMAL(28,12) NOT NULL,
    [AverageRateCur] DECIMAL(28,12) NOT NULL,
    [AverageMonthCur] DECIMAL(28,12) NOT NULL,
    [ClosingRateRef] DECIMAL(28,12) NOT NULL,
    [AverageRateRef] DECIMAL(28,12) NOT NULL,
    [AverageMonthRef] DECIMAL(28,12) NOT NULL,

    CONSTRAINT [PK_TMP_CONSO_EXCHANGERATE] PRIMARY KEY CLUSTERED
        ([SessionID] ASC, [FromCurrCode] ASC) WITH (FILLFACTOR = 80),
    CONSTRAINT [FK_TMP_CONSO_EXCHANGERATE_TL010S0] FOREIGN KEY ([SessionID])
        REFERENCES [dbo].[TL010S0] ([SessionID]) ON DELETE CASCADE
);
```

### Usage Pattern

```sql
-- Cache exchange rates for session
exec dbo.P_CONSO_HELPER_FILL_EXCHANGERATE
    @ConsoID = @ConsoID,
    @SessionID = @SessionID

-- Use cached rates during processing
SELECT
    a.Amount,
    a.Amount * r.ClosingRateCur as ConvertedAmount
FROM TMP_TD035C2 a
JOIN TMP_CONSO_EXCHANGERATE r
    ON r.SessionID = a.SessionID
    AND r.FromCurrCode = a.CurrCode
```

## Import Three-Phase Pattern

### Phase 1: Details Table (Raw Data)

```sql
-- Example: TMP_IMPORTDATA_DETAILS
CREATE TABLE TMP_IMPORTDATA_DETAILS (
    SessionID INT,
    RowNr INT,
    ConsoCode NVARCHAR(12),
    CompanyCode NVARCHAR(12),
    AccountCode NVARCHAR(12),
    Amount DECIMAL(24,6),
    ...
)
```

### Phase 2: Mappings Table (Code Resolution)

```sql
-- Example: TMP_IMPORTDATA_MAPPINGS
CREATE TABLE TMP_IMPORTDATA_MAPPINGS (
    SessionID INT,
    RowNr INT,
    ConsoID INT,         -- Resolved from ConsoCode
    CompanyID INT,       -- Resolved from CompanyCode
    AccountID INT,       -- Resolved from AccountCode
    ValidationStatus BIT
)
```

### Phase 3: Errors Table (Validation Results)

```sql
-- Example: TMP_IMPORTDATA_ERRORS
CREATE TABLE TMP_IMPORTDATA_ERRORS (
    SessionID INT,
    RowNr INT,
    ErrorCode NVARCHAR(50),
    ErrorMessage NVARCHAR(MAX),
    FieldName NVARCHAR(50)
)
```

## Index Strategy for TMP_* Tables

### Primary Key Pattern

```sql
-- Non-clustered PK on identity column
CONSTRAINT [PK_TMP_xxx] PRIMARY KEY NONCLUSTERED
    ([TmpIdentityID]) WITH (FILLFACTOR = 80)
```

### Clustered Index Pattern

```sql
-- Clustered on SessionID + processing key
CREATE CLUSTERED INDEX [IX_TMP_xxx]
    ON [dbo].[TMP_xxx]([SessionID] ASC, [ProcessingKey] ASC)
```

### Rationale

- **Non-clustered PK**: Allows flexibility in clustered index choice
- **SessionID-first clustering**: Efficient session-based data access
- **FILLFACTOR 80**: Accommodates frequent inserts/updates

## Session Lifecycle

### Session Creation

```sql
-- Create new session
INSERT INTO TL010S0 (CustomerID, UserID, SessionType)
VALUES (@CustomerID, @UserID, 'CONSOLIDATION')

SET @SessionID = SCOPE_IDENTITY()
```

### Session Cleanup

```sql
-- Option 1: Explicit deletion (cascades to all TMP_* tables)
DELETE FROM TL010S0 WHERE SessionID = @SessionID

-- Option 2: Age-based cleanup job
DELETE FROM TL010S0
WHERE LastActivityDate < DATEADD(HOUR, -24, GETDATE())
```

### Automatic Cascade

```sql
-- When session is deleted, all related TMP_* data is automatically removed
-- due to FK ON DELETE CASCADE
```

## TMP_* Table Catalog

### Consolidation (11 tables)

| Table | Records |
|-------|---------|
| TMP_TD035C2 | Closing amounts |
| TMP_TD035C2_JOURNALSEQUENCE | Journal sequencing |
| TMP_TD045C2 | Flow amounts |
| TMP_TD040B2 | Bundle flows |
| TMP_TD040I2 | IC flows |
| TMP_TD055C2 | Dimensional amounts |
| TMP_TD033E0 | Group adjustments |
| TMP_CONSO_EXCHANGERATE | Exchange rates |
| TMP_CONSO_COMPANYID | Company processing |
| TMP_CONSO_MATCHING | IC matching |
| TMP_CONSO_SPECIAL_DIMENSION_DETAILS | Dimensions |

### Import (55+ tables)

- TMP_IMPORTDATA_* (4 tables)
- TMP_IMPORTADJUSTMENTS_* (4 tables)
- TMP_IMPORTEXCHANGERATE_* (4 tables)
- TMP_IMPORTACCOUNTS_* (3 tables)
- TMP_IMPORTACCOUNTSTRUCTURES_* (3 tables)
- TMP_IMPORTCOMPANIES_* (3 tables)
- TMP_IMPORTFLOWS_* (3 tables)
- TMP_IMPORTOWNERSHIP_* (3 tables)
- TMP_IMPORTDIMENSIONDETAILS_* (3 tables)
- TMP_IMPORTCUSTOMREPORTS_* (9 tables)
- TMP_IMPORTMAPPINGTABLES_* (3 tables)
- TMP_IMPORTTRANSLATIONS_* (3 tables)
- TMP_IMPORTBUNDLE_* (6 tables)
- TMP_BULK_IMPORT_* (3 tables)

### Export (6 tables)

| Table | Purpose |
|-------|---------|
| TMP_EXPORTDATA | Data staging |
| TMP_EXPORTDATA_DETAILS | Data details |
| TMP_EXPORTADJUSTMENTS | Adjustments |
| TMP_EXPORTEXCHANGERATE | Exchange rates |
| TMP_EXPORTSTRUCTURE | Structures |
| TMP_EXPORTTRANSLATION | Translations |

### Other (8 tables)

| Table | Purpose |
|-------|---------|
| TMP_TS015S0 | Ownership staging |
| TMP_SUBGROUP_PERCENTAGES | Sub-group calcs |
| TMP_EVENT_GENERIC | Event processing |
| TMP_VALIDATION_REPORT_RULE | Validation results |
| TMP_VALIDATION_REPORT_RULE_DETAIL | Validation details |
| TMP_IMPORTRULES_DIMENSION | Dimension rules |
| TMP_IMPORTSTRUCTURE | Structure import |
| TMP_IMPORTSUMACCOUNTS | Sum account import |

## Best Practices

### Do's

- Always use SessionID for data isolation
- Include Step column for multi-phase processing
- Use clustered index on SessionID + key columns
- Clean up sessions after processing completes
- Use FK CASCADE DELETE for automatic cleanup

### Don'ts

- Don't share data across sessions without explicit design
- Don't leave orphaned sessions (implement cleanup job)
- Don't use TMP_* tables for long-term storage
- Don't bypass session isolation for "performance"

## API Reference

### Session Management via API
| Operation | Handler | TMP_* Tables Used |
|-----------|---------|-------------------|
| Consolidation | Consolidation_Execute | TMP_TD035C2, TMP_TD045C2, TMP_CONSO_* |
| Import | Import_Execute | TMP_IMPORT*_DETAILS, TMP_IMPORT*_MAPPINGS |
| Export | Export_Execute | TMP_EXPORT* |
| Ownership Calc | Ownership_Calculate | TMP_TS015S0, TMP_SUBGROUP_* |

### Session Lifecycle via API
```
API Session Management:

1. Session Creation:
   API Handler → Insert TL010S0 → Get SessionID

2. Processing:
   SessionID → TMP_* tables (isolated)
   FK to TL010S0 ensures isolation

3. Cleanup:
   Delete TL010S0 → CASCADE DELETE TMP_* data
   OR: Explicit cleanup after processing
```

### Related API Documentation
- [API Index](../11-agent-support/api-index.yaml) - Master handler catalog
- Session-scoped operations via all processing handlers

---

## Related Documentation

- [Index Strategy](index-strategy.md) - Indexing patterns
- [Data Tables Catalog](data-tables-catalog.md) - Permanent tables
- [Data Import Services](../08-application-layer/data-import-services.md) - Import processing
- [Consolidation Workflow](../03-core-calculations/consolidation-workflow.md) - Processing flow

---
*Document 50 of 50+ | Batch 17: Final Documentation | MILESTONE: 50 Documents Complete | Last Updated: 2024-12-01*
