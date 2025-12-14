# Data Import Services: Application Layer Architecture

## Document Metadata
- **Category**: Application Layer
- **Theory Source**: Implementation-specific (Data integration architecture)
- **Implementation Files**:
  - `Sigma.Database/dbo/Stored Procedures/P_SYS_IMPORT*.sql` - 64+ import procedures
  - `Sigma.Mona/Data/` - Data context and entities
  - `Sigma.Mona.WebApplication/Screens/Import/` - Import UI components
  - `Sigma.Database/dbo/Tables/TMP_IMPORT*.sql` - Import staging tables
- **Last Updated**: 2024-12-01
- **Completeness**: 100% (Comprehensive import architecture documentation)
- **Compliance Status**: Implementation reference document

## Executive Summary

The Prophix.Conso Data Import Services provide a comprehensive framework for importing consolidation data from external sources. The architecture follows a three-phase pattern: **Mapping** (validation and transformation), **Staging** (temporary table processing), and **Processing** (permanent data insertion). With 64+ stored procedures covering 15+ data types, the import system supports both manual file uploads and automated hub integrations.

## Architecture Overview

### Import Data Flow

```
External Data Source
        │
        ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Phase 1: MAPPINGS                             │
│   P_SYS_IMPORT{Entity}_MAPPINGS                                 │
│   - Parse incoming data (CSV, Excel, XML)                       │
│   - Validate structure and format                               │
│   - Map external codes to internal IDs                          │
│   - Insert to TMP_IMPORT{Entity}_MAPPINGS                       │
└─────────────────────────────────────────────────────────────────┘
        │
        ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Phase 2: VALIDATION                           │
│   TMP_IMPORT{Entity}_MAPPINGS                                   │
│   - DoImport flag per row (true/false)                          │
│   - ErrorCode for validation failures                           │
│   - User review and correction                                  │
└─────────────────────────────────────────────────────────────────┘
        │
        ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Phase 3: PROCESS                              │
│   P_SYS_IMPORT{Entity}_PROCESS                                  │
│   - Insert validated rows to permanent tables                   │
│   - Apply business rules                                        │
│   - Update status flags                                         │
│   - Clean up staging tables                                     │
└─────────────────────────────────────────────────────────────────┘
        │
        ▼
    Permanent Data Tables (TD*, TS*)
```

## Import Procedure Catalog

### Core Data Import Procedures

| Entity | Mappings SP | Process SP | Target Tables |
|--------|-------------|------------|---------------|
| **Data** | P_SYS_IMPORTDATA_MAPPINGS | P_SYS_IMPORTDATA_PROCESS | TD030B2, TD040B2, TD050B2 |
| **Adjustments** | P_SYS_IMPORTADJUSTMENTS_MAPPINGS | P_SYS_IMPORTADJUSTMENTS_PROCESS | TD030E0, TD030E2 |
| **Companies** | P_SYS_IMPORTCOMPANIES_MAPPINGS | P_SYS_IMPORTCOMPANIES_PROCESS | TS014C0 |
| **Ownership** | P_SYS_IMPORTOWNERSHIP_MAPPINGS | P_SYS_IMPORTOWNERSHIP_PROCESS | TS015S0 |
| **Accounts** | P_SYS_IMPORTACCOUNTS_MAPPINGS | P_SYS_IMPORTACCOUNTS_PROCESS | TS010S0 |
| **Flows** | P_SYS_IMPORTFLOWS_MAPPINGS | P_SYS_IMPORTFLOWS_PROCESS | TS011S0 |
| **Exchange Rates** | P_SYS_IMPORTEXCHANGERATE_MAPPINGS | P_SYS_IMPORTEXCHANGERATE_PROCESS | TS017R0 |
| **Bundle** | P_SYS_IMPORTBUNDLE_MAPPINGS | P_SYS_IMPORTBUNDLE_PROCESS | TD030B2, adjustments |
| **Dimensions** | P_SYS_IMPORTDIMENSIONDETAILS_MAPPINGS | P_SYS_IMPORTDIMENSIONDETAILS_PROCESS | TS050G2 |
| **Translations** | P_SYS_IMPORTTRANSLATIONS_MAPPINGS | P_SYS_IMPORTTRANSLATIONS_PROCESS | T_TRANSLATION |

### Supporting Procedures

| Procedure | Purpose |
|-----------|---------|
| P_SYS_IMPORTDATA_ERROR_INSERT | Log import errors |
| P_SYS_IMPORTDATA_EXECUTE_RULES | Apply import transformation rules |
| P_SYS_IMPORTDATA_INSERT | Insert individual data records |
| P_SYS_IMPORTDATA_TO_HUB | Export data to hub system |
| P_SYS_IMPORTSTRUCTURE_INSERT | Insert structure elements |

## Staging Tables

### TMP_IMPORTDATA_MAPPINGS Structure

```sql
CREATE TABLE [dbo].[TMP_IMPORTDATA_MAPPINGS] (
    [pk]                    INT IDENTITY PRIMARY KEY,
    [SessionID]             INT NOT NULL,

    -- Source identification
    [SourceRowNumber]       INT,
    [SourceCompanyCode]     NVARCHAR(20),
    [SourceAccountCode]     NVARCHAR(20),
    [SourceFlowCode]        NVARCHAR(20),
    [SourcePartnerCode]     NVARCHAR(20),

    -- Mapped internal IDs
    [CompanyID]             INT,
    [AccountID]             INT,
    [FlowID]                INT,
    [PartnerCompanyID]      INT,

    -- Amount and processing
    [Amount]                DECIMAL(28,6),
    [MappingFactor]         DECIMAL(10,6) DEFAULT 1,

    -- Validation
    [DoImport]              BIT DEFAULT 1,
    [ErrorCode]             NVARCHAR(50),
    [ErrorMessage]          NVARCHAR(500)
);
```

### Session-Based Isolation

All import operations use `SessionID` for multi-user isolation:

```sql
-- Create unique session for import operation
DECLARE @SessionID INT = NEWID()

-- All operations filtered by session
INSERT INTO TMP_IMPORTDATA_MAPPINGS (SessionID, ...)
SELECT @SessionID, ... FROM ParsedData

-- Processing only handles this session
EXEC P_SYS_IMPORTDATA_PROCESS @SessionID = @SessionID

-- Cleanup after processing
DELETE FROM TMP_IMPORTDATA_MAPPINGS WHERE SessionID = @SessionID
```

## P_SYS_IMPORTDATA_PROCESS Details

### Key Processing Logic

From `P_SYS_IMPORTDATA_PROCESS.sql`:

```sql
-- Phase 1: Validate session data
SELECT @ValidRowCount = COUNT(*)
FROM TMP_IMPORTDATA_MAPPINGS
WHERE SessionID = @SessionID AND DoImport = 1

-- Phase 2: Apply mapping factors
UPDATE TMP_IMPORTDATA_MAPPINGS
SET Amount = Amount * ISNULL(MappingFactor, 1)
WHERE SessionID = @SessionID

-- Phase 3: Insert to permanent tables
INSERT INTO TD030B2 (ConsoID, CompanyID, AccountID, Amount, ...)
SELECT @ConsoID, CompanyID, AccountID, Amount, ...
FROM TMP_IMPORTDATA_MAPPINGS
WHERE SessionID = @SessionID AND DoImport = 1

-- Phase 4: Update company status
UPDATE TS014C0
SET Status_Bundles = 1,
    Status_Adjustments = 1
WHERE CompanyID IN (SELECT DISTINCT CompanyID FROM TMP_IMPORTDATA_MAPPINGS WHERE SessionID = @SessionID)
```

### Import Options

| Option | Description | Effect |
|--------|-------------|--------|
| ReplaceImportedAccounts | Clear existing data for imported accounts | Delete before insert |
| ReplaceImportedTypes | Clear by journal type | Selective replacement |
| ReplaceImportedGroups | Clear by account group | Group-level replacement |
| SumIntercos | Aggregate IC transactions | Consolidate IC amounts |
| REMOVE_SESSION_AFTER_IMPORT | Auto-cleanup staging | Performance optimization |

### Error Handling Pattern

```sql
-- Error insertion during mapping phase
EXEC P_SYS_IMPORTDATA_ERROR_INSERT
    @SessionID = @SessionID,
    @RowNumber = @CurrentRow,
    @ErrorCode = 'INVALID_COMPANY',
    @ErrorMessage = 'Company code not found: ' + @CompanyCode

-- Mark row as invalid
UPDATE TMP_IMPORTDATA_MAPPINGS
SET DoImport = 0,
    ErrorCode = 'INVALID_COMPANY'
WHERE SessionID = @SessionID AND pk = @pk
```

## Hub Integration

### Data Exchange with External Systems

```
┌─────────────────┐          ┌─────────────────┐
│  External Hub   │  ◄────►  │  Prophix.Conso  │
│  (Prophix 365)  │          │                 │
└─────────────────┘          └─────────────────┘
         │                           │
         ▼                           ▼
T_HUB_DATA_IN               T_HUB_DATA_OUT
T_HUB_ADJUSTMENTS_IN        T_HUB_ADJUSTMENTS_OUT
T_HUB_STARTJOB              T_HUB_DATA_OUT_JOBS
```

### Hub Import Procedures

| Procedure | Direction | Purpose |
|-----------|-----------|---------|
| P_SYS_IMPORTDATA_DETAILS_FROM_HUB | Inbound | Pull data from hub |
| P_SYS_IMPORTDATA_TO_HUB | Outbound | Push data to hub |
| P_SYS_IMPORTDATA_TO_HUB_STARTJOB | Outbound | Initiate hub job |
| P_SYS_IMPORTADJUSTMENTS_DETAILS_FROM_HUB | Inbound | Pull adjustments |
| P_SYS_IMPORTADJUSTMENTS_TO_HUB_STARTJOB | Outbound | Push adjustments |

## Import Job Management

### Job Integration

Import operations integrate with the job system:

```sql
-- From P_SYS_IMPORTDATA_PROCESS header
@JobID int,
@LockedByGuid uniqueidentifier,
@Login nvarchar(256)

-- Lock acquisition
EXEC @result = P_SYS_LOCK_CONSO
    @ConsoID = @ConsoID,
    @LockedByGuid = @LockedByGuid,
    @LockMode = 'EXCLUSIVE'

-- Transaction management
BEGIN TRANSACTION
    -- Import processing
    IF @@ERROR = 0
        COMMIT TRANSACTION
    ELSE
        ROLLBACK TRANSACTION
```

### Locking Strategy

1. **Exclusive lock** on consolidation during import
2. **Session isolation** for concurrent imports
3. **Transaction rollback** on error

## Performance Considerations

### Large Volume Imports

From procedure comments (P_SYS_IMPORTDATA_PROCESS):

```sql
-- Added OPTION(RECOMPILE) for performance reasons
-- if there are a lot of records in TMP_IMPORTDATA_DETAILS/MAPPING

SELECT ... FROM TMP_IMPORTDATA_MAPPINGS
WHERE SessionID = @SessionID
OPTION (RECOMPILE)

-- Option to update statistics at the end of this procedure
IF @UpdateStatistics = 1
    UPDATE STATISTICS TMP_IMPORTDATA_MAPPINGS
```

### Best Practices

| Practice | Benefit |
|----------|---------|
| Batch processing | Memory efficiency |
| Session cleanup | Table growth control |
| Index hints | Execution plan stability |
| Statistics update | Query optimizer accuracy |

## Application Layer Integration

### C# Service Pattern

```csharp
// Import service workflow
public async Task<ImportResult> ImportDataAsync(ImportRequest request)
{
    using var db = DAOFactory.CreateDataContext();
    var sessionId = GenerateSessionId();

    try
    {
        // Phase 1: Parse and map
        await db.P_SYS_IMPORTDATA_MAPPINGSAsync(
            sessionId, request.Data, request.ConsoId);

        // Phase 2: Validate
        var errors = await GetMappingErrorsAsync(sessionId);
        if (errors.Any()) return new ImportResult { Errors = errors };

        // Phase 3: Process
        await db.P_SYS_IMPORTDATA_PROCESSAsync(
            sessionId, request.ConsoId, request.JobId);

        return new ImportResult { Success = true };
    }
    finally
    {
        // Cleanup
        await CleanupSessionAsync(sessionId);
    }
}
```

## API Reference

### Primary API Handlers
| Handler | YAML File | Purpose | Status |
|---------|-----------|---------|--------|
| `Import_Execute` | [api-import-endpoints.yaml](../11-agent-support/api-import-endpoints.yaml) | Trigger P_SYS_IMPORT*_PROCESS | ✅ IMPLEMENTED |
| `Import_GetMappings` | [api-import-endpoints.yaml](../11-agent-support/api-import-endpoints.yaml) | Get TMP_IMPORT*_MAPPINGS | ✅ IMPLEMENTED |
| `Import_ValidateMappings` | [api-import-endpoints.yaml](../11-agent-support/api-import-endpoints.yaml) | Validation before process | ✅ IMPLEMENTED |

### Import Entity Types via API
| Entity | Handler Suffix | Target Table |
|--------|----------------|--------------|
| Data | ImportData_* | TD030B2, TD040B2 |
| Adjustments | ImportAdjustments_* | TD030E0, TD030E2 |
| Companies | ImportCompanies_* | TS014C0 |
| Ownership | ImportOwnership_* | TS015S0 |
| ExchangeRate | ImportExchangeRate_* | TS017R0 |

### API Workflow
```
Data Import via API:

1. UPLOAD & PARSE
   Import_Upload → File parsing
   Import_CreateMappings → P_SYS_IMPORT*_MAPPINGS

2. VALIDATION
   Import_ValidateMappings → Review DoImport flags
   Import_GetErrors → Get validation errors

3. PROCESS
   Import_Execute → P_SYS_IMPORT*_PROCESS
   → Target tables updated
   → Status flags set
```

### Related API Documentation
- [API Index](../11-agent-support/api-index.yaml) - Master handler catalog
- [Gap Analysis](../11-agent-support/gap-analysis-report.yaml) - **FULLY IMPLEMENTED (100%)**

---

## Related Documentation

- [Consolidation Services](consolidation-services.md) - Application layer overview
- [Data Tables Catalog](../07-database-implementation/data-tables-catalog.md) - Target table reference
- [Stored Procedures Catalog](../07-database-implementation/stored-procedures-catalog.md) - SP reference
- [Journal Types](../07-database-implementation/journal-types.md) - Import journal handling

---
*Document 37 of 50+ | Batch 13: Application Services & Frontend Implementation | Last Updated: 2024-12-01*
