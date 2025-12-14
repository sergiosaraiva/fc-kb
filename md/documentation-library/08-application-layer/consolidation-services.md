# Consolidation Services - Application Layer

## Document Metadata
- **Category**: Application Layer
- **Framework**: .NET Framework 4.8, C#
- **Architecture**: Message Broker Pattern, Background Jobs
- **Key Files**: `ConsolidationIntegrationJob.cs`, `MonaDbContext.Consolidation.cs`
- **Last Updated**: 2024-12-01
- **Completeness**: 95%

## Executive Summary

The application layer orchestrates consolidation operations through a **job-based architecture** using Hangfire for background processing. The primary entry point is `ConsolidationIntegrationJob`, which coordinates database stored procedure calls and manages the consolidation workflow.

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    Frontend (TypeScript)                     │
│         ConsolidationIntegration.ts, ConsoBatch.ts           │
└────────────────────────┬────────────────────────────────────┘
                         │ Message Broker
┌────────────────────────▼────────────────────────────────────┐
│                 Message Handlers (C#)                        │
│              ConsolidationService handlers                   │
└────────────────────────┬────────────────────────────────────┘
                         │ Job Queue
┌────────────────────────▼────────────────────────────────────┐
│              ConsolidationIntegrationJob                     │
│                   (Hangfire Job)                             │
└────────────────────────┬────────────────────────────────────┘
                         │ ADO.NET / Entity Framework
┌────────────────────────▼────────────────────────────────────┐
│                Database Layer (SQL Server)                   │
│                 P_CONSO_* Procedures                         │
└─────────────────────────────────────────────────────────────┘
```

## Key Components

### 1. ConsolidationIntegrationJob

**Location**: `Sigma.Mona.Jobs/Database/ConsolidationIntegrationJob.cs`

```csharp
public class ConsolidationIntegrationJob : Job
{
    // Stored procedure selection flags
    public enum StoredProcedures : byte
    {
        Undefined        = 0x0,
        LinkedCategories = 0x1,
        Bundles          = 0x2,   // P_CONSO_CALCULATE_BUNDLE_INTEGRATION
        Adjustments      = 0x4,   // P_CONSO_CALCULATE_ADJUSTMENTS_INTEGRATION
        Elims            = 0x8,   // P_CONSO_ELIM
        All              = (LinkedCategories | Bundles | Adjustments | Elims)
    }

    // Job parameters
    public const string JobParameterConsoIDs = "ConsoIDs";
    public const string JobParameterCompanyIDs = "CompanyIDs";
    public const string JobParameterStoredProceduresToExecute = "StoredProceduresToExecute";
    public const string JobParameterExecuteDimensions = "ExecuteDimensions";

    // Stored procedure constants
    private const string StoredProcedureNameBundles = "dbo.P_CONSO_CALCULATE_BUNDLE_INTEGRATION";
    private const string StoredProcedureNameAdjustments = "dbo.P_CONSO_CALCULATE_ADJUSTMENTS_INTEGRATION";
    private const string StoredProcedureNameElims = "dbo.P_CONSO_ELIM";
}
```

### 2. Job Execution Flow

```csharp
public override JobResult Execute(JobParams jobVars)
{
    // 1. Validate parameters
    var consoIDs = (int[])jobVars.Get(JobParameterConsoIDs);
    var procedures = (StoredProcedures)jobVars.Get(JobParameterStoredProceduresToExecute);

    // 2. Query consolidations (ordered by ConsoCode)
    var consos = dc.Consos
        .Where(v => !v.Locked)
        .OrderBy(v => v.ConsoCode)
        .ToArray();

    // 3. Process each consolidation
    foreach (var conso in consos)
    {
        // Execute Bundles integration
        if (procedures.HasFlag(StoredProcedures.Bundles))
            ExecuteStoredProcedure(StoredProcedureNameBundles, conso.ConsoID);

        // Execute Adjustments integration
        if (procedures.HasFlag(StoredProcedures.Adjustments))
            ExecuteStoredProcedure(StoredProcedureNameAdjustments, conso.ConsoID);

        // Execute Eliminations
        if (procedures.HasFlag(StoredProcedures.Elims))
            ExecuteStoredProcedure(StoredProcedureNameElims, conso.ConsoID);
    }
}
```

### 3. Entity Framework Integration

**Location**: `Sigma.Mona/EF/Procedures/Consolidation/`

```csharp
// MonaDbContext.Consolidation.cs
public partial class MonaDbContext
{
    // Consolidation entity mappings
    public DbSet<ConsolidationAccount> ConsolidationAccounts { get; set; }
    public DbSet<ConsolidationFlow> ConsolidationFlows { get; set; }

    // Stored procedure wrappers (if applicable)
}

// ConsolidationAccount.cs - EF Entity
public class ConsolidationAccount
{
    public int AccountID { get; set; }
    public int ConsoID { get; set; }
    // ... additional properties
}
```

## Job Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `ConsoIDs` | int[] | Yes* | Array of consolidation IDs to process |
| `ConsoCodes` | string[] | Yes* | Array of consolidation codes (alternative) |
| `CompanyIDs` | int[] | No | Filter to specific companies |
| `CompanyCodes` | string[] | No | Filter by company codes |
| `StoredProceduresToExecute` | StoredProcedures | Yes | Which procedures to run |
| `ExecuteDimensions` | bool | Yes | Include dimension processing |
| `ScreenStructureID` | int | No | Screen context |

*One of ConsoIDs or ConsoCodes required

## Error Handling

```csharp
// Lock checking
if (consos.Length != consoCount)
{
    var consoDetail = allConsos
        .Where(v => consoIDs.Contains(v.ConsoID))
        .Select(v => new { v.LockedByLogin, v.LockedDate })
        .FirstOrDefault();

    throw new DataException(
        key: TrK.ConsoLockedWidthOutReason,
        parameters: new[] { consoDetail.LockedByLogin, consoDetail.LockedDate }
    );
}
```

## Progress Tracking

```csharp
// Progress messages for UI
private const string ProgressMessageKeyBundles = "ConsolidationIntegrationProgressBundles";
private const string ProgressMessageKeyAdjustments = "ConsolidationIntegrationProgressAdjustments";
private const string ProgressMessageKeyElims = "ConsolidationIntegrationProgressEliminations";

// Batch progress
string progressString = $"{i+1}/{consos.Length}";
UpdateProgress(ProgressMessageKeyBundles, conso.ConsoID, conso.ConsoCode);
```

## Theory-to-Code Mapping

| Theoretical Concept | Application Layer Implementation |
|--------------------|----------------------------------|
| Global Integration | `StoredProcedures.Bundles` → `P_CONSO_CALCULATE_BUNDLE_INTEGRATION` |
| Eliminations | `StoredProcedures.Elims` → `P_CONSO_ELIM` |
| Currency Translation | Part of Bundles procedure chain |
| Adjustments | `StoredProcedures.Adjustments` → `P_CONSO_CALCULATE_ADJUSTMENTS_INTEGRATION` |

## Recommendations

1. **Async Enhancement**: Consider async/await for long-running consolidations
2. **Cancellation Support**: Add CancellationToken for user abort
3. **Detailed Logging**: Link log entries to theoretical concepts
4. **Performance Metrics**: Track procedure execution times

## API Reference

### Primary API Handlers
| Handler | YAML File | Purpose | Status |
|---------|-----------|---------|--------|
| `Consolidation_Execute` | [api-consolidation-endpoints.yaml](../11-agent-support/api-consolidation-endpoints.yaml) | Trigger ConsolidationIntegrationJob | ✅ IMPLEMENTED |
| `ConsolidationIntegration_GetStatus` | [api-consolidation-endpoints.yaml](../11-agent-support/api-consolidation-endpoints.yaml) | Check consolidation status | ✅ IMPLEMENTED |

### API Workflow
```
Consolidation via API:

1. TRIGGER CONSOLIDATION
   Consolidation_Execute → ConsolidationIntegrationJob:
     - ConsoIDs: Array of consolidation periods
     - CompanyIDs: Optional company filter
     - StoredProceduresToExecute: Bundles|Adjustments|Elims
     - ExecuteDimensions: Include dimensional processing

2. JOB EXECUTION
   ConsolidationIntegrationJob.Execute():
     - P_CONSO_CALCULATE_BUNDLE_INTEGRATION (Bundles)
     - P_CONSO_CALCULATE_ADJUSTMENTS_INTEGRATION (Adjustments)
     - P_CONSO_ELIM (Eliminations)

3. PROGRESS MONITORING
   Job_GetProgress → Job status and messages
```

### Related API Documentation
- [API Index](../11-agent-support/api-index.yaml) - Master handler catalog
- [Gap Analysis](../11-agent-support/gap-analysis-report.yaml) - **FULLY IMPLEMENTED (95%)**

---

## Related Documentation
- [Stored Procedures Catalog](../07-database-implementation/stored-procedures-catalog.md) - Database procedures
- [Global Integration](../02-consolidation-methods/global-integration.md) - Consolidation method
- [Consolidation Workflow](../03-core-calculations/consolidation-workflow.md) - 5-phase process
- [Elimination Execution Engine](elimination-execution-engine.md) - P_CONSO_ELIM details

### Navigation
- [Cross-Reference Index](../00-index/CROSS_REFERENCE_INDEX.md) - Find related documents
- [Quick Reference Card](../20-appendices/quick-reference-card.md) - Procedure signatures
- [Troubleshooting Guide](../17-troubleshooting/common-issues.md) - Issue resolution
- [Glossary](../20-appendices/glossary.md) - Term definitions

---
*Document 8 of 50+ | Batch 3: Implementation | Last Updated: 2024-12-01*