# Journal Types: Categories and Posting Classification

## Document Metadata
- **Category**: Database Implementation
- **Theory Source**: Implementation-specific (consolidation workflow)
- **Implementation Files**:
  - `Sigma.Database/dbo/Tables/TS020S0.sql` - Journal type definitions
  - `Sigma.Database/dbo/Tables/TS020S1.sql` - Journal descriptions
  - `Sigma.Database/dbo/Tables/TS020G0.sql` - Journal summation groups
  - `Sigma.Database/dbo/Tables/TS020G1.sql` - Summation descriptions
  - `Sigma.Database/dbo/Tables/TS020G2.sql` - Journal-to-summation mapping
  - `Sigma.Database/dbo/Views/V_JOURNALTYPE.sql` - Journal type view
- **Last Updated**: 2024-12-01
- **Completeness**: 100% (Full journal type framework)
- **Compliance Status**: Implementation framework for adjustment tracking

## Executive Summary

Journal types in Prophix.Conso classify and organize consolidation entries by their source and purpose. The system uses a two-level classification: **JournalType** (B/E/L/T/M) identifies the nature of the entry, while **JournalCategory** (3-character code) provides specific sub-classification. Journal summations group related journal types for reporting purposes (BUNDLE, MANUAL, EVENT, TECH, CONSO).

## Journal Type Classification

### Primary Journal Types

| JournalType | Code | Description | Origin |
|-------------|------|-------------|--------|
| **B** | Bundle | Statutory account data | Data entry/import |
| **E** | Elimination | Automatic eliminations | Consolidation process |
| **L** | Local adjustment | Local company adjustments | Manual entry |
| **T** | Technical | System-generated technical entries | Consolidation engine |
| **M** | Manual | Manual consolidation adjustments | Group adjustments |

### Journal Type Constraint

```sql
CONSTRAINT [CK_TS020S0_JOURNALTYPE]
CHECK ([JournalType]='L' OR [JournalType]='T' OR [JournalType]='E' OR [JournalType]='M' OR [JournalType]='B')
```

### Journal Category Examples

| Type | Category | Description |
|------|----------|-------------|
| B | 001 | Bundle accounts (statutory data) |
| E | 020 | Dividend elimination (S020) |
| E | 079 | Proportional elimination (S079) |
| E | 089 | Participation eliminations |
| T | 001 | Currency translation adjustments |
| M | 001 | Group adjustments |
| L | 001 | Local untaxed reserves |

## Database Schema

### TS020S0 - Journal Type Definitions

```sql
CREATE TABLE [dbo].[TS020S0] (
    [JournalTypeID]           INT          IDENTITY NOT NULL,
    [JournalType]             CHAR (1)     NOT NULL,      -- B, E, L, T, M
    [JournalCategory]         NVARCHAR (3) NOT NULL,      -- e.g., '001', '020', '079'
    [ConsoID]                 INT          NOT NULL,
    [AssociatedJournalTypeID] INT          NULL,          -- Link to related journal
    [JournalDescriptionID]    INT          NOT NULL,
    [AvailableForEndUser]     BIT          DEFAULT 0      -- Visible in UI
);
```

**Key Relationships**:
- Each journal type belongs to a consolidation (ConsoID)
- AssociatedJournalTypeID links related journals (e.g., E-journal to T-journal)
- JournalDescriptionID provides multilingual description

### TS020S1 - Journal Descriptions

```sql
CREATE TABLE [dbo].[TS020S1] (
    [JournalDescriptionID] INT IDENTITY NOT NULL,
    [ConsoID]              INT NOT NULL,
    [Description]          XML NULL  -- Multilingual XML format
);

-- Description format:
-- <messages><message lcid="2057">Bundle accounts</message></messages>
```

### V_JOURNALTYPE - Journal Type View

```sql
CREATE VIEW [dbo].[V_JOURNALTYPE] AS
SELECT
    a.JournalTypeID,
    a.JournalType,
    a.JournalCategory,
    a.ConsoID,
    CASE WHEN a.AssociatedJournalTypeID IS NULL
         THEN a.JournalTypeID
         ELSE a.AssociatedJournalTypeID
    END AS AssociatedJournalTypeID,
    a.JournalDescriptionID,
    b.[Description] AS JournalDescription,
    CASE WHEN a.AssociatedJournalTypeID IS NULL
         THEN a.JournalType
         ELSE c.JournalType
    END AS AssociatedJournalType,
    -- ... (additional associated fields)
    a.AvailableForEndUser
FROM dbo.TS020S0 a
    INNER JOIN dbo.TS020S1 b ON (...)
    LEFT OUTER JOIN dbo.TS020S0 c ON (...)
```

## Journal Summations

### TS020G0 - Journal Summation Groups

```sql
CREATE TABLE [dbo].[TS020G0] (
    [JournalSummationID]            INT           IDENTITY NOT NULL,
    [JournalSummationCode]          NVARCHAR (12) NOT NULL,
    [ConsoID]                       INT           NOT NULL,
    [JournalSummationDescriptionID] INT           NOT NULL,
    [IsHardcoded]                   BIT           DEFAULT 0,  -- System summation
    [FlagEventsOnly]                BIT           NOT NULL    -- Events only filter
);
```

### Standard Journal Summations

| Code | Description | Purpose |
|------|-------------|---------|
| **BUNDLE** | Bundle | Statutory data entries |
| **MANUAL** | Manual | User-entered adjustments |
| **EVENT** | Event | Event-driven entries |
| **TECH** | Tech | Technical/system entries |
| **CONSO** | Conso | Consolidation adjustments |

### TS020G2 - Journal-to-Summation Mapping

```sql
CREATE TABLE [dbo].[TS020G2] (
    [JournalJournalSummationID] INT IDENTITY NOT NULL,
    [ConsoID]                   INT NOT NULL,
    [JournalTypeID]             INT NOT NULL,
    [JournalSummationID]        INT NOT NULL
);

-- Links journal types to summation groups
-- One journal can belong to multiple summations
```

## Journal Type Usage in Eliminations

### Elimination Code to Journal Mapping

Each elimination code (S0XX) creates entries in specific journals:

| ElimCode | JournalType | JournalCategory | Description |
|----------|-------------|-----------------|-------------|
| S001 | B | 001 | Bundle opening |
| S020 | E | 020 | Dividend elimination |
| S079 | E | 079 | Proportional elimination |
| S089-S094 | E | 089-094 | Participation eliminations |
| CTA | T | 001 | Translation adjustments |

### Journal Selection in Eliminations

From `P_CONSO_ELIM_DIVIDEND.sql`:
```sql
-- Find bundle journal for opening data
SELECT @JournalTypeB001ID = JournalTypeID
FROM TS020S0
WHERE ConsoID = @ConsoID
  AND JournalType = 'B'
  AND JournalCategory = '001'

-- Find elimination journal for dividends
SELECT @JournalTypeS020ID = JournalTypeID
FROM TS020S0
WHERE ConsoID = @ConsoID
  AND JournalType = 'E'
  AND JournalCategory = '020'
```

### Technical Journal Hierarchy

For POV (Point of View) multi-level structures:
```sql
-- Build T-journal hierarchy
-- T0XX → T1XX → T2XX → T3XX (levels)
SELECT Cast(a.Item as int) as [Level],
       'T' + Cast(a.Item as nvarchar(1)) + RIGHT(@JournalCategory,2) as JournalCode
-- Maps level-specific technical journals
```

## Data Table Journal References

### TD035C2 - Closing Amounts

```sql
-- Contains JournalTypeID to track entry source
INSERT INTO dbo.TD035C2 (
    SessionID,
    CompanyID,
    JournalTypeID,      -- Links to TS020S0
    JournalEntry,       -- Entry sequence number
    AccountID,
    Amount,
    ...
)
```

### TD045C2 - Flow Amounts

```sql
-- Flow-level data includes journal type
INSERT INTO dbo.TD045C2 (
    SessionID,
    CompanyID,
    JournalTypeID,
    JournalEntry,
    AccountID,
    FlowID,             -- Links to TS011S0
    Amount,
    ...
)
```

## Journal Entry Numbering

### Entry Sequencing

- JournalEntry: Sequential number within journal type
- Unique within: ConsoID + CompanyID + JournalTypeID
- Used for audit trail and reversal tracking

### Entry Creation in Eliminations

```sql
-- Get next journal entry number
SELECT @JournalEntry = ISNULL(MAX(JournalEntry), 0) + 1
FROM dbo.TD035C2
WHERE ConsoID = @ConsoID
  AND CompanyID = @CompanyID
  AND JournalTypeID = @JournalTypeID

-- Insert new elimination entry
INSERT INTO dbo.TD035C2 (JournalTypeID, JournalEntry, ...)
VALUES (@JournalTypeS020ID, @JournalEntry, ...)
```

## Journal Filtering and Selection

### By Journal Type

```sql
-- Select only elimination journals
WHERE a.JournalType = 'E'

-- Select all non-bundle journals
WHERE a.JournalType <> 'B'

-- Select manual adjustments
WHERE a.JournalType IN ('L', 'M')
```

### By Summation

```sql
-- Get all journals in BUNDLE summation
SELECT j.JournalTypeID
FROM dbo.TS020S0 j
    INNER JOIN dbo.TS020G2 jg ON j.JournalTypeID = jg.JournalTypeID
    INNER JOIN dbo.TS020G0 g ON jg.JournalSummationID = g.JournalSummationID
WHERE g.JournalSummationCode = 'BUNDLE'
  AND j.ConsoID = @ConsoID
```

## Standard Journal Categories by Type

### Bundle Journals (B)

| Category | Description |
|----------|-------------|
| 001 | Bundle accounts |

### Elimination Journals (E)

| Category | Description | ElimCode |
|----------|-------------|----------|
| 020 | Dividend elimination | S020 |
| 079 | Proportional elimination | S079 |
| 089 | Participations (owner) | S089 |
| 090 | Participations (owned) | S090 |
| 091 | Shareholders funds | S091 |
| 092 | Third parties (owner) | S092 |
| 093 | Third parties (owned) | S093 |
| 094 | Intercompany eliminations | S094 |

### Technical Journals (T)

| Category | Description |
|----------|-------------|
| 001 | Currency translation |
| 0XX | Level-specific CTA |

### Manual Journals (M)

| Category | Description |
|----------|-------------|
| 001 | Group adjustments |
| 002+ | Custom adjustments |

### Local Journals (L)

| Category | Description |
|----------|-------------|
| 001 | Untaxed reserves |
| 002+ | Local adjustments |

## Business Impact

### Current Capabilities

1. **Complete Classification**: All entries tracked by type and category
2. **Audit Trail**: Journal entry numbering for traceability
3. **Flexible Grouping**: Summations for reporting
4. **Associated Journals**: Linked E→T journals for flow-through

### Operational Considerations

1. **Journal Setup**: Configure during consolidation template creation
2. **Category Naming**: Follow consistent category numbering
3. **Summation Assignment**: Map journals to appropriate summations
4. **End User Visibility**: Control AvailableForEndUser flag

## API Reference

### Primary API Handlers
| Handler | YAML File | Purpose | Status |
|---------|-----------|---------|--------|
| `JournalType_GetJournalTypes` | [api-journal-endpoints.yaml](../11-agent-support/api-journal-endpoints.yaml) | Get TS020S0 definitions | ✅ IMPLEMENTED |
| `JournalType_SaveJournalType` | [api-journal-endpoints.yaml](../11-agent-support/api-journal-endpoints.yaml) | Update journal types | ✅ IMPLEMENTED |
| `Consolidation_Execute` | [api-consolidation-endpoints.yaml](../11-agent-support/api-consolidation-endpoints.yaml) | Create journals (B/E/T) | ✅ IMPLEMENTED |

### Journal Type Code Reference
| Type | Category | API Filter | Description |
|------|----------|------------|-------------|
| B | 001 | journalType='B' | Bundle accounts |
| E | 020-094 | journalType='E' | Elimination journals |
| T | 001-0XX | journalType='T' | Technical/CTA journals |
| M | 001+ | journalType='M' | Manual group adjustments |
| L | 001+ | journalType='L' | Local adjustments |

### Related API Documentation
- [API Index](../11-agent-support/api-index.yaml) - Master handler catalog
- [Gap Analysis](../11-agent-support/gap-analysis-report.yaml) - **FULLY IMPLEMENTED (100%)**

---

## Related Documentation

- [Stored Procedures Catalog](stored-procedures-catalog.md) - Elimination procedures
- [Flow Management](../03-core-calculations/flow-management.md) - Flow integration
- [Consolidation Services](../08-application-layer/consolidation-services.md) - Service layer

### Navigation
- [Cross-Reference Index](../00-index/CROSS_REFERENCE_INDEX.md) - Find related documents
- [Quick Reference Card](../20-appendices/quick-reference-card.md) - Elimination code reference
- [Troubleshooting Guide](../17-troubleshooting/common-issues.md) - Issue resolution
- [Glossary](../20-appendices/glossary.md) - Term definitions

---
*Document 23 of 50+ | Batch 8: Core System Mechanics | Last Updated: 2024-12-01*
