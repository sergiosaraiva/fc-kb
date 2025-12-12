# Index Strategy: Database Performance Patterns

## Document Metadata
- **Category**: Database Implementation
- **Theory Source**: Implementation-specific (SQL Server optimization patterns)
- **Implementation Files**:
  - `Sigma.Database/dbo/Tables/TD*.sql` - Data tables with indexes
  - `Sigma.Database/dbo/Tables/TS*.sql` - Setup tables with indexes
  - `Sigma.Database/dbo/Tables/TMP_*.sql` - Temporary tables with indexes
- **Last Updated**: 2024-12-01
- **Completeness**: 100% (Comprehensive index pattern documentation)
- **Compliance Status**: Database architecture reference

## Executive Summary

Prophix.Conso employs a consistent indexing strategy across 93+ database tables to optimize consolidation performance while maintaining multi-tenant data isolation. The strategy prioritizes **ConsoID-first indexing** for tenant isolation, **FILLFACTOR 80** for update-heavy tables, and **composite business keys** for uniqueness enforcement. This document catalogs the indexing patterns, naming conventions, and optimization rationale.

## Core Indexing Principles

### Multi-Tenant Isolation Pattern

All indexes lead with `ConsoID` to ensure query plans leverage tenant partitioning:

```sql
-- Standard pattern: ConsoID as first column
PRIMARY KEY CLUSTERED ([ConsoID] ASC, [EntityID] ASC)

-- Business key uniqueness
UNIQUE NONCLUSTERED ([ConsoID] ASC, [CompanyCode] ASC)
```

### FILLFACTOR Strategy

Standard FILLFACTOR = 80 across all tables:

```sql
WITH (FILLFACTOR = 80)
```

**Rationale**:
- 20% free space accommodates row updates without page splits
- Consolidation data frequently updated during processing
- Balance between read performance and update overhead

## Index Pattern Catalog

### Pattern 1: Setup Tables (TS*) - Configuration Data

**Characteristics**: Relatively static, small row counts, frequent lookups

```sql
-- Example: TS014C0 (Companies)
CREATE TABLE [dbo].[TS014C0] (
    [CompanyID] INT IDENTITY NOT NULL,
    [ConsoID] INT NOT NULL,
    [CompanyCode] NVARCHAR(8) NOT NULL,

    -- Primary key: ConsoID + Identity
    CONSTRAINT [PK_TS014C0] PRIMARY KEY CLUSTERED
        ([ConsoID] ASC, [CompanyID] ASC) WITH (FILLFACTOR = 80),

    -- Business key uniqueness
    CONSTRAINT [IX_TS014C0] UNIQUE NONCLUSTERED
        ([ConsoID] ASC, [CompanyCode] ASC) WITH (FILLFACTOR = 80)
);
```

**Index Structure**:
| Index | Type | Columns | Purpose |
|-------|------|---------|---------|
| PK_TS014C0 | Clustered | ConsoID, CompanyID | Row storage, FK target |
| IX_TS014C0 | Unique NC | ConsoID, CompanyCode | Code lookups |

### Pattern 2: Ownership Tables (TS015S0) - Relationship Data

**Characteristics**: Many-to-many relationships, frequent joins

```sql
-- Example: TS015S0 (Ownership Links)
CREATE TABLE [dbo].[TS015S0] (
    [ControlID] INT IDENTITY NOT NULL,
    [ConsoID] INT NOT NULL,
    [CompanyID] INT NOT NULL,        -- Shareholder
    [CompanyOwnedID] INT NOT NULL,   -- Company owned

    -- Primary key
    CONSTRAINT [PK_TS015S0] PRIMARY KEY CLUSTERED
        ([ConsoID] ASC, [ControlID] ASC) WITH (FILLFACTOR = 80),

    -- Business key uniqueness
    CONSTRAINT [IX_TS015S0_2] UNIQUE NONCLUSTERED
        ([ConsoID] ASC, [CompanyID] ASC, [CompanyOwnedID] ASC)
);

-- Supporting indexes for lookups
CREATE NONCLUSTERED INDEX [IX_TS015S0]
    ON [dbo].[TS015S0]([ConsoID] ASC, [CompanyID] ASC)
    WITH (FILLFACTOR = 80);

CREATE NONCLUSTERED INDEX [IX_TS015S0_1]
    ON [dbo].[TS015S0]([CompanyOwnedID] ASC)
    WITH (FILLFACTOR = 80);
```

**Index Structure**:
| Index | Type | Columns | Purpose |
|-------|------|---------|---------|
| PK_TS015S0 | Clustered | ConsoID, ControlID | Row storage |
| IX_TS015S0_2 | Unique NC | ConsoID, CompanyID, CompanyOwnedID | Prevent duplicates |
| IX_TS015S0 | NC | ConsoID, CompanyID | Find what company owns |
| IX_TS015S0_1 | NC | CompanyOwnedID | Find who owns company |

### Pattern 3: Local Data Tables (TD030B2, TD040B2) - Transaction Data

**Characteristics**: High volume, batch inserts/updates, complex lookups

```sql
-- Example: TD030B2 (Local Adjusted Bundles)
CREATE TABLE [dbo].[TD030B2] (
    [LocalAdjustedBundleID] INT IDENTITY NOT NULL,
    [ConsoID] INT NOT NULL,
    [CompanyID] INT NOT NULL,
    [AccountID] INT NOT NULL,
    [CurrCode] NVARCHAR(3) NOT NULL,
    [Amount] DECIMAL(24, 6) NOT NULL,

    -- Primary key: NONCLUSTERED for identity
    CONSTRAINT [PK_TD030B2] PRIMARY KEY NONCLUSTERED
        ([ConsoID] ASC, [LocalAdjustedBundleID] ASC) WITH (FILLFACTOR = 80)
);

-- Clustered: Business key for range queries
CREATE UNIQUE CLUSTERED INDEX [IX_TD030B2]
    ON [dbo].[TD030B2]([ConsoID] ASC, [CompanyID] ASC, [CurrCode] ASC, [AccountID] ASC)
    WITH (FILLFACTOR = 80);

-- Supporting: Account-based lookups
CREATE NONCLUSTERED INDEX [IX_TD030B2_ACCOUNTID]
    ON [dbo].[TD030B2]([ConsoID] ASC, [AccountID] ASC)
    WITH (FILLFACTOR = 80);
```

**Key Design Decision**: Clustered index on business key, not identity:
- Range queries by Company/Currency/Account common
- Identity access via NONCLUSTERED PK for FK relationships
- Optimizes bulk consolidation operations

### Pattern 4: Consolidated Data Tables (TD035C2, TD045C2)

**Characteristics**: Write-heavy during consolidation, complex read patterns for reports

```sql
-- Example: TD045C2 (Consolidated Flows)
CREATE TABLE [dbo].[TD045C2] (
    [ConsolidatedFlowsID] BIGINT IDENTITY NOT NULL,
    [ConsoID] INT NOT NULL,
    [CompanyID] INT NOT NULL,
    [JournalTypeID] INT NOT NULL,
    [JournalEntry] BIGINT NOT NULL,
    [AccountID] INT NOT NULL,
    [FlowID] INT NOT NULL,
    [CurrCode] NVARCHAR(3) NOT NULL,
    [Amount] DECIMAL(24, 6) NOT NULL,

    -- Primary key
    CONSTRAINT [PK_TD045C2] PRIMARY KEY CLUSTERED
        ([ConsoID] ASC, [ConsolidatedFlowsID] ASC) WITH (FILLFACTOR = 80),

    -- Uniqueness constraint (10-column composite)
    CONSTRAINT [IX_TD045C2] UNIQUE NONCLUSTERED
        ([ConsoID], [CurrCode], [CompanyID], [JournalTypeID],
         [JournalEntry], [JournalSequence], [AccountID],
         [PartnerCompanyID], [TransactionCurrCode], [FlowID])
);

-- Journal-based lookups
CREATE NONCLUSTERED INDEX [IX_TD045C2_1]
    ON [dbo].[TD045C2]([ConsoID], [JournalTypeID], [JournalEntry], [CurrCode]);

-- Covering index for aggregations
CREATE NONCLUSTERED INDEX [IX_TD045C2_2]
    ON [dbo].[TD045C2]([ConsoID], [CompanyID], [CurrCode])
    INCLUDE([JournalTypeID], [AccountID], [FlowID], [Amount]);
```

**Advanced Pattern**: Covering index with INCLUDE columns:
- Key columns for filtering: ConsoID, CompanyID, CurrCode
- INCLUDE columns avoid key lookups for aggregations
- Critical for report performance

### Pattern 5: Intercompany Tables (TD030I2, TD040I2)

**Characteristics**: Partner relationships, elimination processing

```sql
-- Example: TD040I2 (IC Flow Data)
CREATE TABLE [dbo].[TD040I2] (
    [LocalAdjustedBundleIntercoID] INT IDENTITY NOT NULL,
    [ConsoID] INT NOT NULL,
    [CompanyID] INT NOT NULL,
    [PartnerCompanyID] INT NOT NULL,
    [AccountID] INT NOT NULL,
    [FlowID] INT NOT NULL,

    -- Primary key
    CONSTRAINT [PK_TD040I2] PRIMARY KEY CLUSTERED
        ([ConsoID] ASC, [LocalAdjustedBundleIntercoID] ASC)
        WITH (FILLFACTOR = 80),

    -- Full business key uniqueness
    CONSTRAINT [IX_TD040I2] UNIQUE NONCLUSTERED
        ([ConsoID], [CompanyID], [CurrCode], [FlowID],
         [AccountID], [PartnerCompanyID], [TransactionCurrCode])
        WITH (FILLFACTOR = 80)
);
```

### Pattern 6: Dimensional Tables (TD050B2)

**Characteristics**: Parent-child relationship, dimensional breakdowns

```sql
-- Example: TD050B2 (Dimensional Bundles)
CREATE TABLE [dbo].[TD050B2] (
    [LocalAdjustedBundleDimID] BIGINT IDENTITY NOT NULL,
    [ConsoID] INT NOT NULL,
    [LocalAdjustedBundleID] INT NOT NULL,  -- FK to TD030B2
    [DimensionGroupID] INT NOT NULL,
    [Dim1DetailID] INT NOT NULL,
    [Dim2DetailID] INT NULL,
    [Dim3DetailID] INT NULL,

    -- Primary key
    CONSTRAINT [PK_TD050B2] PRIMARY KEY CLUSTERED
        ([ConsoID] ASC, [LocalAdjustedBundleDimID] ASC)
        WITH (FILLFACTOR = 80),

    -- Prevent duplicate dimension combinations
    CONSTRAINT [IX_TD050B2_1] UNIQUE NONCLUSTERED
        ([ConsoID], [LocalAdjustedBundleID], [DimensionGroupID],
         [Dim1DetailID], [Dim2DetailID], [Dim3DetailID])
        WITH (FILLFACTOR = 80)
);
```

### Pattern 7: Temporary/Staging Tables (TMP_*)

**Characteristics**: Session isolation, bulk operations, automatic cleanup

```sql
-- Example: TMP_CONSO_EXCHANGERATE
CREATE TABLE [dbo].[TMP_CONSO_EXCHANGERATE] (
    [TmpConsoExchangeRateID] INT IDENTITY NOT NULL,
    [SessionID] INT NOT NULL,  -- Session isolation key
    [FromCurrCode] NVARCHAR(3) NOT NULL,
    [ClosingRateCur] DECIMAL(28,12) NOT NULL,

    -- Session-first clustering
    CONSTRAINT [PK_TMP_CONSO_EXCHANGERATE] PRIMARY KEY CLUSTERED
        ([SessionID] ASC, [FromCurrCode] ASC) WITH (FILLFACTOR = 80),

    -- Cascade delete for cleanup
    CONSTRAINT [FK_TMP_CONSO_EXCHANGERATE_TL010S0]
        FOREIGN KEY ([SessionID])
        REFERENCES [dbo].[TL010S0] ([SessionID])
        ON DELETE CASCADE
);
```

**Session Pattern Benefits**:
- Multi-user concurrent consolidation support
- Automatic cleanup via cascade delete
- Session-scoped query optimization

### Pattern 8: Import Staging Tables (TMP_IMPORT*)

**Characteristics**: Bulk data loading, validation processing

```sql
-- Example: TMP_IMPORTDATA_DETAILS
CREATE TABLE [dbo].[TMP_IMPORTDATA_DETAILS] (
    [TmpImportDataDetailsID] INT IDENTITY NOT NULL,
    [SessionID] INT NOT NULL,
    [RowNumber] INT NOT NULL,

    -- NONCLUSTERED PK for identity access
    CONSTRAINT [PK_TMP_TS027S0_DETAILS] PRIMARY KEY NONCLUSTERED
        ([TmpImportDataDetailsID] ASC)
);

-- Session-based processing
CREATE NONCLUSTERED INDEX [IX_TMP_IMPORTDATA_DETAILS]
    ON [dbo].[TMP_IMPORTDATA_DETAILS]([SessionID] ASC);
```

## Index Naming Conventions

| Pattern | Convention | Example |
|---------|------------|---------|
| Primary Key | PK_{TableName} | PK_TS014C0 |
| Unique Constraint | IX_{TableName} | IX_TS014C0 |
| Secondary Unique | IX_{TableName}_N | IX_TS015S0_2 |
| Non-unique Index | IX_{TableName}_N | IX_TD045C2_1 |
| Descriptive Index | IX_{Table}_{Column} | IX_TD030B2_ACCOUNTID |

## Performance Optimization Patterns

### Query Patterns Optimized

| Query Type | Index Strategy | Example Table |
|------------|----------------|---------------|
| Tenant isolation | ConsoID-first | All tables |
| Code lookups | Unique NC on Code | TS014C0 |
| Range by company | Clustered on CompanyID | TD030B2 |
| Journal retrieval | NC on JournalTypeID | TD045C2 |
| Aggregation | Covering with INCLUDE | TD045C2_2 |
| Dimension drill | Composite dimension key | TD050B2 |

### Consolidation Process Optimization

```
1. Bundle Integration
   └── TD030B2: IX_TD030B2 (CompanyID, CurrCode, AccountID)

2. Flow Calculation
   └── TD040B2: IX_TD040B2 (CompanyID, CurrCode, FlowID, AccountID)

3. Elimination Processing
   └── TD030I2/TD040I2: Partner-based lookups

4. Consolidated Output
   └── TD035C2/TD045C2: Covering indexes for reports
```

## Maintenance Considerations

### Index Rebuild Recommendation

| Table Category | Rebuild Frequency | Fragmentation Threshold |
|----------------|-------------------|------------------------|
| TD* (Data) | Weekly | > 30% |
| TS* (Setup) | Monthly | > 30% |
| TMP_* | After major operations | > 50% |

### Statistics Update Pattern

```sql
-- From P_SYS_IMPORTDATA_PROCESS
IF @UpdateStatistics = 1
    UPDATE STATISTICS TMP_IMPORTDATA_MAPPINGS
```

## API Reference

### Index Impact on API Performance
| API Handler | Critical Indexes | Query Pattern |
|-------------|------------------|---------------|
| Company_GetCompanies | IX_TS014C0 | ConsoID + CompanyCode |
| DataEntry_GetData | IX_TD030B2 | ConsoID + CompanyID + AccountID |
| Consolidation_Execute | IX_TD035C2, IX_TD045C2 | ConsoID + JournalTypeID |
| Report_Execute | IX_TD035C2_2 (covering) | ConsoID + CompanyID + CurrCode |

### ConsoID-First Pattern
All API operations benefit from ConsoID-first indexing for multi-tenant isolation:
```
Query Plan: ConsoID filter → Index seek → Partition elimination
```

### Related API Documentation
- [API Index](../11-agent-support/api-index.yaml) - Master handler catalog
- Performance optimization impacts all handlers

---

## Related Documentation

- [Data Tables Catalog](data-tables-catalog.md) - Complete table reference
- [Stored Procedures Catalog](stored-procedures-catalog.md) - Query patterns
- [Data Import Services](../08-application-layer/data-import-services.md) - Import staging
- [Elimination Execution Engine](../08-application-layer/elimination-execution-engine.md) - Processing queries

---
*Document 39 of 50+ | Batch 13: Application Services & Frontend Implementation | Last Updated: 2024-12-01*
