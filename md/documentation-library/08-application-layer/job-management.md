# Job Management: Background Processing Architecture

## Document Metadata
- **Category**: Application Layer
- **Theory Source**: Implementation-specific (Hangfire job processing)
- **Implementation Files**:
  - `Sigma.Mona.Jobs/Job.cs` - Base job class
  - `Sigma.Mona.Jobs/JobResult.cs` - Job result handling
  - `Sigma.Mona.Jobs/JobSchedule.cs` - Scheduling configuration
  - `Sigma.Mona.Jobs/Database/*.cs` - Database operation jobs (40+ files)
  - `Sigma.Mona.Jobs/ImportExport/*.cs` - Import/export jobs
  - `Sigma.Mona.Jobs/Utils/*.cs` - Utility jobs
  - `Sigma.Mona.WebApplication/Screens/JobSchedule/` - Job scheduling UI
- **Last Updated**: 2024-12-01
- **Completeness**: 100% (Full job architecture documented)
- **Compliance Status**: Application architecture reference

## Executive Summary

Prophix.Conso uses Hangfire for background job processing, enabling long-running operations like consolidation, imports, exports, and maintenance tasks to execute asynchronously. The job system includes 50+ specialized job classes organized by category, with support for progress reporting, cancellation, logging, and both LINQ-to-SQL and Entity Framework data access.

## Job Architecture Overview

### Job Categories

```
┌─────────────────────────────────────────────────────────────────┐
│                    Job Architecture                              │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  DATABASE JOBS (Sigma.Mona.Jobs/Database/)                      │
│  ├── ConsolidationIntegrationJob - Full consolidation           │
│  ├── CalculateIndirectPercentagesJob - Ownership calculation    │
│  ├── ConsoActionJob - Consolidation actions                     │
│  ├── BackupJob / RestoreJob - Database maintenance              │
│  ├── DeleteConsoJob / DeleteCustomerJob - Data cleanup          │
│  ├── CopyConsoJob / CopyStructureJob / CopySubGroupJob          │
│  ├── CustomProcedureJob - Custom SP execution                   │
│  ├── ProcessManagementJob - Workflow processing                 │
│  └── WorkflowJob - Workflow execution                           │
│                                                                  │
│  IMPORT/EXPORT JOBS                                              │
│  ├── ImportDataJob / ExportDataJob - Data transfer              │
│  ├── ImportAdjustmentsJob / ExportAdjustmentsJob                │
│  ├── ImportExRateJob / ExportExRateJob - Exchange rates         │
│  ├── ImportStructureJob / ExportStructureJob                    │
│  ├── ImportTranslationJob / ExportTranslationJob                │
│  ├── ImportBundleJob - Bundle data import                       │
│  ├── GenericImportJob / GenericExportJob                        │
│  └── ExportCubeJob / ExportReportingSolutionsJob                │
│                                                                  │
│  UTILITY JOBS (Sigma.Mona.Jobs/Utils/)                          │
│  ├── CleanupJob - System cleanup                                │
│  ├── ClosePeriodJob - Period closing                            │
│  ├── IndexRebuildJob - Index maintenance                        │
│  ├── RunCommandLineJob - Command execution                      │
│  ├── RunSqlCommandJob - SQL execution                           │
│  └── RunStoredProcedureJob - SP execution                       │
│                                                                  │
│  REPORTING JOBS                                                  │
│  └── ValidationReportJob - Report validation                    │
│                                                                  │
│  OTHER JOBS                                                      │
│  ├── EmailJob - Email notifications                             │
│  ├── DIStudioJob - Data integration                             │
│  ├── FlexSheetJob - SpreadJS operations                         │
│  ├── WebServiceJob - External service calls                     │
│  └── SystemLogsJob - Log management                             │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

## Base Job Class

### Job.cs Implementation

```csharp
namespace Sigma.Mona.Jobs
{
    public abstract class Job
    {
        // Connection and context management
        public string MonaConnectionString => Config.MonaConnectionString;
        public Data.MonaDataContext MonaDataContext { get { return GetMonaDataContext(); } }
        public EF.MonaDbContext DbContext { get { return dbContext ??= new EF.MonaDbContext(...); } }

        // Job identification
        public int JobID;
        public Business.SessionController SessionController = null;
        public Common.Utility.LogHelper LogHelper { get; }

        // Cancellation support
        public System.Threading.CancellationToken HFCancellationtoken;

        // Core methods
        public virtual JobResult Execute(JobParams jobVars) { throw new NotImplementedException(); }
        public virtual Task<JobResult> ExecuteAsync(JobParams jobVars) { return Task.FromResult(Execute(jobVars)); }
        public abstract bool Abort();

        // Progress reporting
        public void ProgressChanged(TranslatableString tstr)
        {
            LogHelper.AddUserMessage(tstr);
        }

        // Resource cleanup
        public virtual void DisposeResources()
        {
            if (monaDataContext != null) monaDataContext.Dispose();
            if (dbContext != null) dbContext.Dispose();
        }

        // Cancellation check helper
        internal void CheckHFCancellationToken(CancellationToken token)
        {
            if (token != null)
            {
                try { token.ThrowIfCancellationRequested(); }
                catch (OperationCanceledException)
                {
                    Abort();
                    throw;
                }
            }
        }
    }
}
```

### Key Features

| Feature | Implementation |
|---------|----------------|
| Dual Data Access | Both LINQ-to-SQL and EF contexts |
| Progress Reporting | Via LogHelper.AddUserMessage |
| Cancellation | HFCancellationtoken integration |
| Resource Management | DisposeResources() cleanup |
| Translation Support | TranslationPrefix for messages |

## ConsolidationIntegrationJob Deep Dive

### Stored Procedure Orchestration

```csharp
public enum StoredProcedures : byte
{
    Undefined        = 0x0,
    LinkedCategories = 0x1,  // P_CONSO_LINKED_CATEGORY
    Bundles          = 0x2,  // P_CONSO_CALCULATE_BUNDLE_INTEGRATION
    Adjustments      = 0x4,  // P_CONSO_CALCULATE_ADJUSTMENTS_INTEGRATION
    Elims            = 0x8,  // P_CONSO_ELIM
    All              = (LinkedCategories | Bundles | Adjustments | Elims)
}
```

### Execution Flow

```
1. Parameter Validation
   │
   ├── screenStructureID
   ├── StoredProceduresToExecute (flags)
   ├── ExecuteDimensions
   ├── ConsoIDs or ConsoCodes
   └── CompanyIDs or CompanyCodes (optional)
   │
   ▼
2. Conso Query & Validation
   │
   ├── Filter by CustomerID
   ├── Filter by locked status
   └── Order by ConsoCode
   │
   ▼
3. For Each Consolidation:
   │
   ├── Create log checkpoint
   ├── Log process start
   │
   ├── Execute Procedures:
   │   ├── LinkedCategories (if selected)
   │   ├── Run Advanced Formulas
   │   ├── Bundles (if selected)
   │   ├── Adjustments (if selected)
   │   └── Eliminations (if selected)
   │
   └── Log process end
   │
   ▼
4. Return JobResult
```

### Stored Procedure Execution

```csharp
private ErrorInfo RunStoredProcedure(LogHelper logHelper, ..., StoredProcedures procedure, ...)
{
    using (var command = new SqlCommand(storedProcedureName, connection))
    {
        command.CommandType = CommandType.StoredProcedure;
        command.CommandTimeout = Common.Config.ScriptsCommandTimeoutSeconds;

        // Parameters
        command.Parameters.Add(new SqlParameter("@UserID", UserID ?? DBNull.Value));
        command.Parameters.Add(new SqlParameter("@ConsoID", consoID));
        command.Parameters.Add(new SqlParameter("@CompanyIDs", companyIDs));
        command.Parameters.Add(new SqlParameter("@ExecuteDimensions", executeDimensions));
        command.Parameters.Add(new SqlParameter("@Debug", Config.ScriptsDebugFlag));

        // Error output
        var xmlErrorInfo = command.Parameters.Add(
            new SqlParameter("@errorinfo", SqlDbType.Xml, -1));
        xmlErrorInfo.Direction = ParameterDirection.Output;

        // Cancellation-aware execution
        AbortAction = () => { command.Cancel(); return true; };
        command.ExecuteNonQuery();
        CheckHFCancellationToken(HFCancellationtoken);

        // Parse error output
        if (xmlErrorInfo.Value != DBNull.Value)
        {
            var errorInfo = ErrorInfo.Parse((string)xmlErrorInfo.Value);
            if (errorInfo.HasErrors) return errorInfo;
        }
        return null;
    }
}
```

## Job Parameters Pattern

### JobParams Usage

```csharp
// Parameter constants
public const string JobParameterConsoIDs = "ConsoIDs";
public const string JobParameterCompanyIDs = "CompanyIDs";
public const string JobParameterStoredProceduresToExecute = "StoredProceduresToExecute";
public const string JobParameterExecuteDimensions = "ExecuteDimensions";

// Retrieval in Execute()
var consoIDs = (int[])jobVars.Get(JobParameterConsoIDs);
var companyIDs = (int[])jobVars.Get(JobParameterCompanyIDs);
var procedures = (StoredProcedures)jobVars.Get(JobParameterStoredProceduresToExecute);
```

## Job Result Handling

### JobResult Structure

```csharp
public class JobResult
{
    public bool Success { get; set; }
    public object ResultParams { get; set; }
    public ErrorInfo ErrorInfo { get; set; }

    public JobResult(bool success = false, object resultParams = null, ErrorInfo errorInfo = null)
    {
        Success = success;
        ResultParams = resultParams;
        ErrorInfo = errorInfo;
    }
}
```

### Return Patterns

```csharp
// Success
return new JobResult { Success = true };

// Failure with error info
return new JobResult(success: false, resultParams: null, errorInfo: errorInfo);

// Failure using LogHelper
if (logHelper.HasErrors)
    return null;  // JobExecute uses logHelper as result
```

## Job Catalog

### Database Jobs

| Job Class | Purpose |
|-----------|---------|
| ConsolidationIntegrationJob | Full consolidation process |
| CalculateIndirectPercentagesJob | Ownership recalculation |
| ConsoActionJob | Individual consolidation actions |
| BackupJob | Database backup |
| RestoreJob | Database restore |
| DeleteConsoJob | Consolidation deletion |
| DeleteCustomerJob | Customer deletion |
| CopyConsoJob | Copy consolidation |
| CopyStructureJob | Copy structure |
| CopySubGroupJob | Copy sub-group |
| CustomProcedureJob | Custom stored procedure |
| ProcessManagementJob | Process management |
| WorkflowJob | Workflow execution |
| SystemLogsJob | System log management |

### Import/Export Jobs

| Job Class | Purpose |
|-----------|---------|
| ImportDataJob | Import data files |
| ExportDataJob | Export data files |
| ImportAdjustmentsJob | Import adjustments |
| ExportAdjustmentsJob | Export adjustments |
| ImportExRateJob | Import exchange rates |
| ExportExRateJob | Export exchange rates |
| ImportStructureJob | Import structures |
| ExportStructureJob | Export structures |
| ImportTranslationJob | Import translations |
| ExportTranslationJob | Export translations |
| ImportBundleJob | Import bundle data |
| GenericImportJob | Generic import handler |
| GenericExportJob | Generic export handler |
| ExportCubeJob | OLAP cube export |
| ExportReportingSolutionsJob | Reporting export |

### Utility Jobs

| Job Class | Purpose |
|-----------|---------|
| CleanupJob | System cleanup tasks |
| ClosePeriodJob | Period closing |
| IndexRebuildJob | Index maintenance |
| RunCommandLineJob | Execute command line |
| RunSqlCommandJob | Execute SQL commands |
| RunStoredProcedureJob | Execute stored procedure |

## Logging and Progress

### System Log Integration

```csharp
// Log entry creation
var logEntry = Data.LogModification.NewLogEntry(
    customerID: CustomerID,
    logGroup: Data.ModificationsLog.LogGroups.Consolidation,
    messageKey: logStartMessageKey,
    consoID: conso.ConsoID,
    userID: UserID,
    screenStructureID: screenStructureID,
    logHelper: logHelper);

// Log message key patterns
logStartMessageKey = Data.ModificationsLog.Message.LogKeyConsoStatusboardStart;
logEndMessageKey = Data.ModificationsLog.Message.LogKeyConsoStatusboardEnd;
```

### Progress Messages

```csharp
// Translation key-based progress
private const string ProgressMessageKeyBundles = "ConsolidationIntegrationProgressBundles";
private const string ProgressMessageKeyAdjustments = "ConsolidationIntegrationProgressAdjustments";
private const string ProgressMessageKeyElims = "ConsolidationIntegrationProgressEliminations";

// With batch progress
logHelper.AddUserMessageTranslated(progressMessageKey, progressString, consoCode);
// Example: "Conso 3/5 '202312ACT001': Converting and integrating bundles"
```

## Job Scheduling (Frontend)

### JobSchedule Screen

```
Sigma.Mona.WebApplication/Screens/JobSchedule/
├── JobScheduleController.cs
├── JobScheduleService.cs
└── JobScheduleTypes/
    ├── ConsolidationJob.cs
    ├── ImportAdjustmentsJob.cs
    ├── ExportHubAdjustmentsJob.cs
    └── ... (job-specific configuration UI)
```

### Scheduling Configuration

Jobs can be scheduled via:
- Immediate execution (UI trigger)
- Recurring schedules (Hangfire recurring jobs)
- Event-triggered (workflow completion)

## Advanced Formulas Integration

### Pre-Consolidation Formulas

```csharp
Action runAdvancedFormulas = () =>
{
    Business.AdvancedFormula.ExecutionManager.LaunchAdvancedFormulas(
        SessionController.SessionInstance,
        dataContext,
        EF.Entities.AdvancedFormulaGroup.Types.BeforeConsolidation,
        screenID,
        consoCode,
        companyCodes,
        logHelper: logHelper);
};

// Execute after LinkedCategories or before any SP
if ((storedProceduresToExecute & StoredProcedures.LinkedCategories) == 0)
    runAdvancedFormulas();  // Before any SP
else
    // After LinkedCategories execution
```

## Error Handling

### Error Flow Pattern

```csharp
try
{
    errorInfo = RunConsoOnSinglePeriod(...);
}
catch (Exception ex)
{
    if (ex.Message == ExecutionManager.MissingCompanies)
    {
        skippedConsos.Add(conso.ConsoCode);
        continue;  // Skip this conso, continue with others
    }
    else
    {
        logHelper.AddExceptionToErrors(ex);
    }
}

// Check for errors after execution
if (logHelper.HasErrors || errorInfo != null)
{
    if (errorInfo != null)
        return new JobResult(success: false, resultParams: null, errorInfo: errorInfo);
    else
        return null;  // LogHelper contains errors
}
```

### Lock Handling

```csharp
// Check for locked consolidations
var queryConsos = dc.Consos.Where(v => v.CustomerID == CustomerID && !v.Locked);

// Lock error message
if (consos.Length != consoCount)
{
    var consoDetail = allConsos.Where(v => consoIDs.Contains(v.ConsoID))
        .Select(v => new { v.LockedByLogin, v.LockedDate }).FirstOrDefault();

    throw new DataException(key: TrK.ConsoLockedWidthOutReason, parameters: new[] {
        consoDetail.LockedByLogin,
        consoDetail.LockedDate?.ToString("MMM dd yyyy hh:mmtt")
    });
}
```

## API Reference

### Primary API Handlers
| Handler | YAML File | Purpose | Status |
|---------|-----------|---------|--------|
| `Job_Execute` | [api-job-endpoints.yaml](../11-agent-support/api-job-endpoints.yaml) | Queue Hangfire job | ✅ IMPLEMENTED |
| `Job_GetStatus` | [api-job-endpoints.yaml](../11-agent-support/api-job-endpoints.yaml) | Get job progress | ✅ IMPLEMENTED |
| `Job_Cancel` | [api-job-endpoints.yaml](../11-agent-support/api-job-endpoints.yaml) | Cancel running job | ✅ IMPLEMENTED |

### Job Type Handlers
| Job Type | Handler | Job Class |
|----------|---------|-----------|
| Consolidation | Consolidation_Execute | ConsolidationIntegrationJob |
| Import | Import_Execute | ImportDataJob |
| Export | Export_Execute | ExportDataJob |
| Ownership | Ownership_Calculate | CalculateIndirectPercentagesJob |

### API Workflow
```
Job Execution via API:

1. JOB TRIGGER
   Job_Execute → Hangfire.Enqueue():
     - JobType: ConsolidationIntegration, Import, etc.
     - Parameters: Job-specific params

2. PROGRESS MONITORING
   Job_GetStatus → Job state + progress messages
   → Running, Succeeded, Failed, Cancelled

3. CANCELLATION
   Job_Cancel → HFCancellationToken triggered
   → Job.Abort() called
```

### Related API Documentation
- [API Index](../11-agent-support/api-index.yaml) - Master handler catalog
- [Gap Analysis](../11-agent-support/gap-analysis-report.yaml) - **FULLY IMPLEMENTED (100%)**

---

## Related Documentation

- [Consolidation Workflow](../03-core-calculations/consolidation-workflow.md) - Orchestration details
- [Data Import Services](data-import-services.md) - Import job patterns
- [Consolidation Services](consolidation-services.md) - Service layer integration
- [Elimination Execution Engine](elimination-execution-engine.md) - P_CONSO_ELIM processing

---
*Document 47 of 50+ | Batch 16: System Mechanics & Adjustment Processing | Last Updated: 2024-12-01*
