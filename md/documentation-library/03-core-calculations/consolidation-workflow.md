# Consolidation Workflow: End-to-End Process Architecture

## Document Metadata
- **Category**: Core Calculations
- **Theory Source**: Implementation-specific (Direct consolidation orchestration)
- **Implementation Files**:
  - `Sigma.Database/dbo/Stored Procedures/P_CONSO_CALCULATE_BUNDLE_INTEGRATION.sql` - Master orchestrator
  - `Sigma.Database/dbo/Stored Procedures/P_CONSO_BUNDLE_INTEGRATION_*.sql` - Phase procedures
  - `Sigma.Database/dbo/Stored Procedures/P_CONSO_ELIM.sql` - Elimination orchestrator
  - `Sigma.Database/dbo/Stored Procedures/P_CONSO_HELPER_*.sql` - Helper procedures
  - `Sigma.Mona.WebApplication/Screens/ConsolidationIntegration/` - UI components
- **Last Updated**: 2024-12-01
- **Completeness**: 100% (Comprehensive workflow documentation)
- **Compliance Status**: Architecture reference document

## Executive Summary

The consolidation workflow in Prophix.Conso transforms local subsidiary financial data into consolidated group financial statements through a five-phase orchestrated process. The master procedure `P_CONSO_CALCULATE_BUNDLE_INTEGRATION` coordinates validation, currency translation, adjustment integration, elimination processing, and status updates in a single atomic transaction.

## Workflow Architecture Overview

### End-to-End Process Flow

```
User/Scheduler Trigger
        │
        ▼
┌─────────────────────────────────────────────────────────────────┐
│              P_CONSO_CALCULATE_BUNDLE_INTEGRATION                │
│                    (Master Orchestrator)                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Phase 1: VALIDATION & PREPARATION                               │
│  ├── P_CONSO_CHECK_LOCKED (Period lock validation)              │
│  ├── P_CONSO_HELPER_FILL_COMPANY_TABLE (Company scope)          │
│  └── P_CONSO_HELPER_FILL_EXCHANGERATE (Rate preparation)        │
│                                                                  │
│  Phase 2: CURRENCY TRANSLATION                                   │
│  ├── P_CONSO_BUNDLE_INTEGRATION_CURRENCY_TRANSLATION_CLOSING    │
│  ├── P_CONSO_BUNDLE_INTEGRATION_CURRENCY_TRANSLATION_FLOWS      │
│  └── P_CONSO_BUNDLE_INTEGRATION_CURRENCY_TRANSLATION_HISTORICAL │
│                                                                  │
│  Phase 3: ADJUSTMENT INTEGRATION                                 │
│  ├── P_CONSO_BUNDLE_INTEGRATION_ADJUSTMENTS                     │
│  └── P_CONSO_BUNDLE_INTEGRATION_ADJUSTMENTS_FLOWS               │
│                                                                  │
│  Phase 4: ELIMINATION PROCESSING                                 │
│  └── P_CONSO_ELIM (Elimination orchestrator)                    │
│      ├── P_CONSO_ELIM_INTERCOMPANY_NETTING                      │
│      ├── P_CONSO_ELIM_PARTICIPATIONS0-4                         │
│      ├── P_CONSO_ELIM_MINORITYINTEREST                          │
│      ├── P_CONSO_ELIM_EQUITYMETHOD                              │
│      ├── P_CONSO_ELIM_PROPORTIONAL                              │
│      ├── P_CONSO_ELIM_DIVIDEND                                  │
│      └── P_CONSO_ELIM_USER                                      │
│                                                                  │
│  Phase 5: FINALIZATION                                           │
│  ├── Status flag updates (TS014C0)                              │
│  └── Audit logging (TL010S0)                                    │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
        │
        ▼
  Consolidated Data (TD035C2, TD045C2, TD055C2)
```

## Phase 1: Validation and Preparation

### Pre-Consolidation Checks

**Period Lock Validation**:
```sql
-- P_CONSO_CHECK_LOCKED
-- Ensures consolidation period is not locked
IF EXISTS (SELECT 1 FROM TS005S0 WHERE ConsoID = @ConsoID AND IsLocked = 1)
    RAISERROR ('Period is locked', 16, 1)
```

**Company Status Verification**:
- All in-scope companies have `Status_Bundles = 1`
- Consolidation method properly configured (G/P/E/N)
- Ownership percentages defined in TS015S0
- Parent company identified in TS014C0

### Temporary Table Preparation

| Table | Procedure | Purpose |
|-------|-----------|---------|
| TMP_CONSO_COMPANYID | P_CONSO_HELPER_FILL_COMPANY_TABLE | Companies to process with ownership % |
| TMP_CONSO_EXCHANGERATE | P_CONSO_HELPER_FILL_EXCHANGERATE | Pre-loaded exchange rates |
| #AllCompanies | Dynamic | Shared company context for eliminations |

### Exchange Rate Availability

```sql
-- P_CONSO_HELPER_FILL_EXCHANGERATE
INSERT INTO TMP_CONSO_EXCHANGERATE (
    SessionID, FromCurrCode,
    ClosingRateCur, AverageRateCur, AverageMonthCur,
    ClosingRateRef, AverageRateRef, AverageMonthRef
)
SELECT @SessionID, CurrCode,
    -- Current period rates
    ClosingRate, AverageRate, AverageMonthRate,
    -- Reference period rates
    RefClosingRate, RefAverageRate, RefAverageMonthRate
FROM TS017R0
WHERE ConsoID = @ConsoID
```

**Rate Types**:
- **CC**: Closing rate - Current period
- **CR**: Closing rate - Reference period
- **AC**: Average rate - Current period
- **AR**: Average rate - Reference period
- **MC**: Monthly average - Current period
- **MR**: Monthly average - Reference period

## Phase 2: Currency Translation

### Translation Process Overview

Converts local amounts (TD030B2) to consolidation currency (TD035C2):

```
Local Currency Amounts    →    Exchange Rates    →    Consolidated Amounts
     TD030B2              TMP_CONSO_EXCHANGERATE         TD035C2/TD045C2
```

### Three Translation Procedures

| Procedure | Applies To | Rate Used |
|-----------|-----------|-----------|
| P_CONSO_BUNDLE_INTEGRATION_CURRENCY_TRANSLATION_CLOSING | Balance sheet accounts | Closing rate |
| P_CONSO_BUNDLE_INTEGRATION_CURRENCY_TRANSLATION_FLOWS | Income statement flows | Average rate |
| P_CONSO_BUNDLE_INTEGRATION_CURRENCY_TRANSLATION_HISTORICAL | Equity items | Historical rate |

### Translation Formula

```sql
-- Closing amount translation
INSERT INTO TD035C2 (ConsoID, CompanyID, AccountID, Amount, CurrCode)
SELECT
    @ConsoID,
    TD030B2.CompanyID,
    TD030B2.AccountID,
    TD030B2.Amount * TMP_CONSO_EXCHANGERATE.ClosingRateCur,
    @ConsoCurrCode
FROM TD030B2
INNER JOIN TMP_CONSO_EXCHANGERATE ON ...
WHERE TD030B2.ConsoID = @ConsoID
```

### CTA Calculation

Currency Translation Adjustment automatically calculated:
```
CTA = Closing Rate Amount - Historical Rate Amount
```

Posted to special account configured in T_CONFIG (`CTAACC`).

## Phase 3: Adjustment Integration

### Local Adjustments Processing

```
TD030E0 (Adjustment Headers)
        │
        ▼
TD030E2 (Adjustment Details)
        │
        ▼
P_CONSO_BUNDLE_INTEGRATION_ADJUSTMENTS
        │
        ▼
TD035C2 (Consolidated Closing)
TD045C2 (Consolidated Flows)
```

### Adjustment Types Processed

| JournalType | Description | Processing |
|-------------|-------------|------------|
| LA | Local Adjustments | Company-level corrections |
| TA | Tax Adjustments | Tax-related adjustments |
| UA | User Adjustments | Manual adjustments |

## Phase 4: Elimination Processing

### P_CONSO_ELIM: Elimination Orchestrator

```sql
-- Elimination execution sequence
EXEC P_CONSO_ELIM_INTERCOMPANY_NETTING     -- IC balance netting
EXEC P_CONSO_ELIM_PARTICIPATIONS0          -- Investment cost elimination
EXEC P_CONSO_ELIM_PARTICIPATIONS1          -- Equity capital elimination
EXEC P_CONSO_ELIM_PARTICIPATIONS2          -- Acquisition differences
EXEC P_CONSO_ELIM_PARTICIPATIONS3          -- Goodwill handling
EXEC P_CONSO_ELIM_PARTICIPATIONS4          -- Reserves transfer
EXEC P_CONSO_ELIM_MINORITYINTEREST         -- NCI calculation
EXEC P_CONSO_ELIM_EQUITYMETHOD             -- Equity method companies
EXEC P_CONSO_ELIM_PROPORTIONAL             -- Proportional integration
EXEC P_CONSO_ELIM_DIVIDEND                 -- IC dividend elimination
EXEC P_CONSO_ELIM_USER                     -- User-defined eliminations
```

### Elimination Output

All eliminations write to consolidated tables with journal tracking:
- **TD035C2**: Consolidated closing amounts
- **TD045C2**: Consolidated flow amounts
- **TD055C2**: Consolidated dimensional amounts

## Phase 5: Finalization

### Status Flag Updates

```sql
-- Update company status after successful consolidation
UPDATE TS014C0
SET Status_ClosingAmounts = 0,  -- Processed
    Status_Flows = 0,           -- Processed
    Status_Adjustments = 0      -- Processed
WHERE ConsoID = @ConsoID
AND CompanyID IN (SELECT CompanyID FROM TMP_CONSO_COMPANYID WHERE SessionID = @SessionID)
```

### Status Flag Meanings

| Flag | Value 0 | Value 1 |
|------|---------|---------|
| Status_Bundles | Integrated | Needs integration |
| Status_ClosingAmounts | Consolidated | Needs consolidation |
| Status_Flows | Consolidated | Needs consolidation |
| Status_Adjustments | Processed | Needs processing |

### Audit Trail

Session logged to TL010S0:
- SessionID (unique identifier)
- UserID (who ran consolidation)
- StartTime / EndTime
- CompanyCount processed
- ErrorCount

## Trigger Mechanisms

### User-Initiated Consolidation

Via Consolidation Integration screen:
```typescript
// ConsolidationIntegration.ts
export const handlerLaunchConsolidationJob = "ConsolidationIntegration_LaunchJob";

// Parameters
{
    ConsoID: selectedConsoID,
    CompanyIDs: selectedCompanies,  // null = all
    ExecuteDimensions: true,
    Debug: false
}
```

### Scheduled Consolidation

Via Hangfire job scheduler:
```csharp
// ConsolidationIntegrationJob.cs
public class ConsolidationIntegrationJob : IJob
{
    public async Task Execute(JobExecutionContext context)
    {
        // Calls P_CONSO_CALCULATE_BUNDLE_INTEGRATION
    }
}
```

### Prerequisites for Consolidation

| Prerequisite | Validation | Error if Missing |
|--------------|------------|------------------|
| Period not locked | TS005S0.IsLocked = 0 | "Period is locked" |
| Bundle data ready | Status_Bundles = 1 | "Bundle data not ready" |
| Exchange rates defined | TS017R0 has rates | "Missing exchange rates" |
| Ownership configured | TS015S0 populated | "Ownership not defined" |
| Parent company set | TS014C0.IsParentCompany | "No parent company" |

## Transaction Management

### Atomic Processing

```sql
-- P_CONSO_CALCULATE_BUNDLE_INTEGRATION
BEGIN TRANSACTION

    -- Phase 1: Validation
    -- Phase 2: Currency Translation
    -- Phase 3: Adjustment Integration
    -- Phase 4: Elimination Processing
    -- Phase 5: Finalization

    IF @@ERROR = 0
        COMMIT TRANSACTION
    ELSE
        ROLLBACK TRANSACTION
```

### Lock Acquisition

```sql
-- Optional: Acquire exclusive lock during processing
IF @LockDuringProcess = 1
    EXEC P_SYS_LOCK_CONSO @ConsoID, @LockedByGuid, 'EXCLUSIVE'
```

## Performance Considerations

### Optimization Patterns

| Pattern | Implementation | Benefit |
|---------|----------------|---------|
| Rate pre-loading | TMP_CONSO_EXCHANGERATE | Avoids repeated lookups |
| Company scope filtering | TMP_CONSO_COMPANYID | Reduces processing scope |
| Batch processing | SET-based operations | Minimizes round trips |
| Session isolation | SessionID-based temp tables | Multi-user concurrency |

### Typical Execution Times

| Company Count | Expected Duration |
|---------------|-------------------|
| 10-50 | 30 seconds - 2 minutes |
| 50-200 | 2-10 minutes |
| 200+ | 10-30 minutes |

## API Reference

### Primary API Handlers
| Handler | YAML File | Purpose | Status |
|---------|-----------|---------|--------|
| `Consolidation_Execute` | [api-consolidation-endpoints.yaml](../11-agent-support/api-consolidation-endpoints.yaml) | Trigger P_CONSO_CALCULATE_BUNDLE_INTEGRATION | ✅ IMPLEMENTED |
| `Consolidation_GetStatus` | [api-consolidation-endpoints.yaml](../11-agent-support/api-consolidation-endpoints.yaml) | Check consolidation status | ✅ IMPLEMENTED |
| `Job_GetJobStatus` | [api-job-monitoring-endpoints.yaml](../11-agent-support/api-job-monitoring-endpoints.yaml) | Monitor consolidation job | ✅ IMPLEMENTED |

### Supporting API Handlers
| Handler | YAML File | Purpose |
|---------|-----------|---------|
| `Company_GetCompanies` | [api-company-endpoints.yaml](../11-agent-support/api-company-endpoints.yaml) | Get companies for consolidation scope |
| `Event_GetEvents` | [api-event-endpoints.yaml](../11-agent-support/api-event-endpoints.yaml) | Get consolidation events |
| `ExchangeRate_GetExchangeRates` | [api-currency-endpoints.yaml](../11-agent-support/api-currency-endpoints.yaml) | Verify exchange rates |
| `Elimination_GetEliminations` | [api-elimination-endpoints.yaml](../11-agent-support/api-elimination-endpoints.yaml) | Get posted eliminations |

### API Workflow
```
Consolidation Execution via API:

1. PRE-VALIDATION
   Company_GetCompanies → Verify scope
   ExchangeRate_GetExchangeRates → Verify rates
   Consolidation_GetStatus → Check not locked

2. EXECUTION
   Consolidation_Execute → Triggers P_CONSO_CALCULATE_BUNDLE_INTEGRATION:
     Phase 1: P_CONSO_CHECK_LOCKED, P_CONSO_HELPER_FILL_*
     Phase 2: P_CONSO_BUNDLE_INTEGRATION_CURRENCY_TRANSLATION_*
     Phase 3: P_CONSO_BUNDLE_INTEGRATION_ADJUSTMENTS*
     Phase 4: P_CONSO_ELIM (all elimination procedures)
     Phase 5: Status updates

3. MONITORING
   Job_GetJobStatus → Monitor progress

4. RESULTS
   Elimination_GetEliminations → View posted eliminations
   Report_ExecuteReport → Generate consolidated reports
```

### Related API Documentation
- [API Index](../11-agent-support/api-index.yaml) - Master handler catalog (242 handlers)
- [API Workflow Diagrams](../11-agent-support/api-workflow-diagrams.yaml) - 9 Mermaid workflow diagrams
- [Gap Analysis](../11-agent-support/gap-analysis-report.yaml) - **FULLY IMPLEMENTED (100%)**

---

## Related Documentation

- [Global Integration Method](../02-consolidation-methods/global-integration.md) - Integration theory
- [Elimination Execution Engine](../08-application-layer/elimination-execution-engine.md) - P_CONSO_ELIM details
- [Currency Translation Methods](../05-currency-translation/translation-methods.md) - Translation theory
- [Consolidation Services](../08-application-layer/consolidation-services.md) - Application layer
- [Consolidation Screens](../09-frontend-implementation/consolidation-screens.md) - UI implementation

### Navigation
- [Cross-Reference Index](../00-index/CROSS_REFERENCE_INDEX.md) - Find related documents
- [Quick Reference Card](../20-appendices/quick-reference-card.md) - Codes and queries
- [Troubleshooting Guide](../17-troubleshooting/common-issues.md) - Issue resolution
- [Glossary](../20-appendices/glossary.md) - Term definitions

---
*Document 40 of 50+ | Batch 14: Consolidation Workflow & Reporting | Last Updated: 2024-12-01*
