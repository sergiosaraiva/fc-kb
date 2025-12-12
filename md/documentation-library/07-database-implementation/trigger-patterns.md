# Trigger Patterns: Database Status Management Architecture

## Document Metadata
- **Category**: Database Implementation
- **Theory Source**: Implementation-specific (Status flag management)
- **Implementation Files**:
  - `Sigma.Database/dbo/Tables/TD030B2.sql` - TR_TD030B2 (Bundle trigger)
  - `Sigma.Database/dbo/Tables/TS014C0.sql` - TR_TS014C0 (Company trigger)
  - `Sigma.Database/dbo/Tables/TS015S0.sql` - TR_TS015S0 (Ownership trigger)
  - `Sigma.Database/dbo/Tables/TS017R0.sql` - TR_TS017R0 (Exchange rate trigger)
  - 32+ additional trigger-enabled tables
- **Last Updated**: 2024-12-01
- **Completeness**: 100% (Comprehensive trigger pattern documentation)
- **Compliance Status**: Database architecture reference

## Executive Summary

Prophix.Conso uses database triggers to maintain consolidation status flags, ensuring data consistency and signaling when reprocessing is needed. With 32+ trigger-enabled tables, the trigger architecture follows a consistent pattern: detect data changes, update related status flags in TS014C0, and support bypass mechanisms for bulk operations.

## Trigger Architecture Overview

### Purpose

Triggers serve three primary functions:
1. **Status Flag Management**: Mark affected companies as needing reprocessing
2. **Cascade Signaling**: Propagate change notifications across related entities
3. **Audit Support**: Enable change tracking without application overhead

### Trigger Categories

```
┌─────────────────────────────────────────────────────────────────┐
│                    Trigger Categories                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  DATA TRIGGERS (TD* tables)                                      │
│  ├── TR_TD030B2  - Local bundles                                │
│  ├── TR_TD030B1  - Raw bundles                                  │
│  ├── TR_TD040B2  - Flow amounts                                 │
│  ├── TR_TD030I2  - Intercompany closing                         │
│  ├── TR_TD040I2  - Intercompany flows                           │
│  ├── TR_TD050B2  - Dimensional amounts                          │
│  ├── TR_TD030E2  - Adjustment details                           │
│  └── TR_TD033E*  - Group adjustments                            │
│                                                                  │
│  SETUP TRIGGERS (TS* tables)                                     │
│  ├── TR_TS014C0  - Company configuration                        │
│  ├── TR_TS015S0  - Ownership links                              │
│  ├── TR_TS017R0  - Exchange rates                               │
│  ├── TR_TS010*   - Account structures                           │
│  ├── TR_TS011*   - Flow structures                              │
│  ├── TR_TS013I*  - Intercompany rules                           │
│  └── TR_TS070S0  - Elimination definitions                      │
│                                                                  │
│  HUB TRIGGERS (T_HUB_* tables)                                   │
│  ├── TR_T_HUB_DATA_*        - Hub data integration              │
│  └── TR_T_HUB_ADJUSTMENTS_* - Hub adjustments                   │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

## Standard Trigger Pattern

### Core Template

```sql
CREATE TRIGGER [dbo].[TR_{TableName}]
ON [dbo].[{TableName}]
AFTER INSERT, UPDATE, DELETE
AS BEGIN
    SET NOCOUNT ON

    -- Bypass check: Skip if bulk operation flag exists
    IF (OBJECT_ID('tempdb..#NO_CLEAR_CONSO_STATUS') IS NOT NULL) RETURN

    -- Update status flags for affected companies
    UPDATE dbo.TS014C0
    SET Status_Bundles = 1,
        Status_ClosingAmounts = 1,
        Status_Flows = 1
    FROM (
        SELECT DISTINCT ConsoID, CompanyID FROM inserted
        UNION
        SELECT DISTINCT ConsoID, CompanyID FROM deleted
    ) a
    WHERE dbo.TS014C0.ConsoID = a.ConsoID
      AND dbo.TS014C0.CompanyID = a.CompanyID
END
```

### Key Components

| Component | Purpose |
|-----------|---------|
| `SET NOCOUNT ON` | Prevent row count messages |
| `#NO_CLEAR_CONSO_STATUS` check | Enable bypass for bulk operations |
| `inserted` virtual table | Access new/updated rows |
| `deleted` virtual table | Access old/deleted rows |
| `UNION` | Combine affected companies |

## Status Flag System

### TS014C0 Status Flags

| Flag | Meaning (0) | Meaning (1) |
|------|-------------|-------------|
| Status_Bundles | Integrated | Needs integration |
| Status_ClosingAmounts | Consolidated | Needs consolidation |
| Status_Flows | Flows processed | Needs flow processing |
| Status_Adjustments | Adjustments applied | Needs adjustment processing |

### Flag Propagation Rules

| Source Table | Triggers Flags |
|--------------|----------------|
| TD030B2 (Bundles) | Bundles, ClosingAmounts, Flows |
| TD040B2 (Flows) | Bundles, ClosingAmounts, Flows |
| TD030I2 (IC Closing) | Bundles, ClosingAmounts, Flows |
| TD030E2 (Adjustments) | Adjustments |
| TS015S0 (Ownership) | Flows, ClosingAmounts |
| TS017R0 (Rates) | ClosingAmounts, Flows |

## Trigger Examples

### TR_TD030B2 - Bundle Data Trigger

```sql
-- From TD030B2.sql
CREATE TRIGGER [dbo].[TR_TD030B2]
ON [dbo].[TD030B2]
AFTER INSERT, UPDATE, DELETE
AS BEGIN
    SET NOCOUNT ON

    IF (OBJECT_ID('tempdb..#NO_CLEAR_CONSO_STATUS') IS NOT NULL) RETURN

    UPDATE dbo.TS014C0
    SET Status_Bundles = 1,
        Status_ClosingAmounts = 1,
        Status_Flows = 1
    FROM (
        SELECT DISTINCT ConsoID, CompanyID FROM inserted
        UNION
        SELECT DISTINCT ConsoID, CompanyID FROM deleted
    ) a
    WHERE dbo.TS014C0.ConsoID = a.ConsoID
      AND dbo.TS014C0.CompanyID = a.CompanyID
END
```

### TR_TS014C0 - Company Configuration Trigger

```sql
-- From TS014C0.sql - Conditional trigger with change detection
CREATE TRIGGER [dbo].[TR_TS014C0]
ON dbo.TS014C0
AFTER INSERT, UPDATE
AS BEGIN
    SET NOCOUNT ON

    IF (OBJECT_ID('tempdb..#NO_CLEAR_CONSO_STATUS') IS NOT NULL) RETURN

    -- Only fire on specific column changes
    UPDATE dbo.TS014C0
    SET Status_Bundles = 1,
        Status_Adjustments = 1,
        Status_Flows = 1,
        Status_ClosingAmounts = 1
    FROM inserted a
         LEFT OUTER JOIN deleted b
           ON b.ConsoID = a.ConsoID AND b.CompanyID = a.CompanyID
    WHERE dbo.TS014C0.ConsoID = a.ConsoID
      AND dbo.TS014C0.CompanyID = a.CompanyID
      AND (
          (a.ConsoMethod <> b.ConsoMethod)
          OR (a.CurrCode <> b.CurrCode)
          OR (ISNULL(a.GroupPerc, 0) <> ISNULL(b.GroupPerc, 0))
          OR (ISNULL(a.MinorPerc, 0) <> ISNULL(b.MinorPerc, 0))
          OR (ISNULL(a.GroupCtrlPerc, 0) <> ISNULL(b.GroupCtrlPerc, 0))
          OR (ISNULL(a.NbrFinRightsIssued, 0) <> ISNULL(b.NbrFinRightsIssued, 0))
          OR (ISNULL(a.NbrVotingRightsIssued, 0) <> ISNULL(b.NbrVotingRightsIssued, 0))
          OR (a.ConsolidatingCompany <> b.ConsolidatingCompany)
          OR (a.AvailableForSale <> b.AvailableForSale)
          OR (a.ConsolidatedCompany <> b.ConsolidatedCompany)
          OR (a.CalculateDeferredTax <> b.CalculateDeferredTax)
          OR (ISNULL(a.DeferredTaxRate, 0) <> ISNULL(b.DeferredTaxRate, 0))
          OR (a.ConversionMethod <> b.ConversionMethod)
      )
END
```

### TR_TS015S0 - Ownership Trigger

```sql
-- From TS015S0.sql - Multi-company impact
CREATE TRIGGER [dbo].[TR_TS015S0]
ON [dbo].[TS015S0]
AFTER INSERT, UPDATE, DELETE
AS BEGIN
    SET NOCOUNT ON

    IF (OBJECT_ID('tempdb..#NO_CLEAR_CONSO_STATUS') IS NOT NULL) RETURN

    -- Affects both owner AND owned company
    UPDATE dbo.TS014C0
    SET Status_Flows = 1,
        Status_ClosingAmounts = 1
    FROM (
        SELECT DISTINCT ConsoID, CompanyID FROM inserted
        UNION
        SELECT DISTINCT ConsoID, CompanyOwnedID AS CompanyID FROM inserted
        UNION
        SELECT DISTINCT ConsoID, CompanyID FROM deleted
        UNION
        SELECT DISTINCT ConsoID, CompanyOwnedID AS CompanyID FROM deleted
    ) a
    WHERE dbo.TS014C0.ConsoID = a.ConsoID
      AND dbo.TS014C0.CompanyID = a.CompanyID
END
```

## Bypass Mechanism

### #NO_CLEAR_CONSO_STATUS Pattern

For bulk operations, create a temp table to bypass triggers:

```sql
-- Bulk operation with trigger bypass
CREATE TABLE #NO_CLEAR_CONSO_STATUS (dummy int)

-- Perform bulk inserts/updates
INSERT INTO TD030B2 (ConsoID, CompanyID, AccountID, Amount, ...)
SELECT ... FROM source_data

-- Clean up
DROP TABLE #NO_CLEAR_CONSO_STATUS

-- Manually set status flags at the end
UPDATE TS014C0
SET Status_Bundles = 1
WHERE ConsoID = @ConsoID
```

### Use Cases for Bypass

| Scenario | Reason |
|----------|--------|
| Import operations | Bulk data loading |
| Consolidation processing | Status managed by procedure |
| Period copy operations | Mass data transfer |
| Data migration | One-time operations |

## Dimensional Table Triggers

### TD050B2 - Dimensional Bundle Trigger

```sql
-- From TD050B2.sql - Joins to parent table for CompanyID
CREATE TRIGGER [dbo].[TR_TD050B2]
ON [dbo].[TD050B2]
AFTER INSERT, UPDATE, DELETE
AS BEGIN
    SET NOCOUNT ON

    IF (OBJECT_ID('tempdb..#NO_CLEAR_CONSO_STATUS') IS NOT NULL) RETURN

    UPDATE dbo.TS014C0
    SET Status_Bundles = 1,
        Status_ClosingAmounts = 1,
        Status_Flows = 1
    FROM (
        -- Join to TD030B2 to get CompanyID
        SELECT DISTINCT a.ConsoID, b.CompanyID
        FROM inserted a
        INNER JOIN dbo.TD030B2 b
          ON b.ConsoID = a.ConsoID
         AND b.LocalAdjustedBundleID = a.LocalAdjustedBundleID
        UNION
        SELECT DISTINCT a.ConsoID, b.CompanyID
        FROM deleted a
        INNER JOIN dbo.TD030B2 b
          ON b.ConsoID = a.ConsoID
         AND b.LocalAdjustedBundleID = a.LocalAdjustedBundleID
    ) a
    WHERE dbo.TS014C0.ConsoID = a.ConsoID
      AND dbo.TS014C0.CompanyID = a.CompanyID
END
```

## Trigger Catalog

### Data Tables (TD*)

| Trigger | Table | Flags Updated |
|---------|-------|---------------|
| TR_TD030B1 | TD030B1 | Bundles, ClosingAmounts, Flows |
| TR_TD030B2 | TD030B2 | Bundles, ClosingAmounts, Flows |
| TR_TD040B2 | TD040B2 | Bundles, ClosingAmounts, Flows |
| TR_TD030I2 | TD030I2 | Bundles, ClosingAmounts, Flows |
| TR_TD040I2 | TD040I2 | Bundles, ClosingAmounts, Flows |
| TR_TD050B2 | TD050B2 | Bundles, ClosingAmounts, Flows |
| TR_TD050I2 | TD050I2 | Bundles, ClosingAmounts, Flows |
| TR_TD030E2 | TD030E2 | Adjustments |
| TR_TD033E0 | TD033E0 | Adjustments |
| TR_TD033E2 | TD033E2 | Adjustments |
| TR_TD043E2 | TD043E2 | Adjustments |
| TR_TD053E2 | TD053E2 | Adjustments |

### Setup Tables (TS*)

| Trigger | Table | Flags Updated |
|---------|-------|---------------|
| TR_TS010C0 | TS010C0 | Account summation dirty |
| TR_TS010G2 | TS010G2 | Account summation dirty |
| TR_TS010G3 | TS010G3 | Account summation dirty |
| TR_TS010S0 | TS010S0 | Account changes |
| TR_TS011C0 | TS011C0 | Flow summation dirty |
| TR_TS011G2 | TS011G2 | Flow summation dirty |
| TR_TS011G3 | TS011G3 | Flow summation dirty |
| TR_TS011S0 | TS011S0 | Flow changes |
| TR_TS013I0 | TS013I0 | IC rule changes |
| TR_TS013I1 | TS013I1 | IC rule changes |
| TR_TS013I2 | TS013I2 | IC rule changes |
| TR_TS014C0 | TS014C0 | Company config changes |
| TR_TS015S0 | TS015S0 | Flows, ClosingAmounts |
| TR_TS017R0 | TS017R0 | ClosingAmounts, Flows |
| TR_TS070S0 | TS070S0 | Elimination changes |

## Best Practices

### Do's

- Always include bypass check
- Use UNION to handle both inserted and deleted
- Set NOCOUNT ON for performance
- Join to parent tables for dimensional data
- Handle NULL values with ISNULL()

### Don'ts

- Don't perform heavy calculations in triggers
- Don't call external resources
- Don't use cursors in triggers
- Don't modify other tables besides TS014C0

## API Reference

### Status Flag Integration
| Trigger | Tables Affected | API Impact |
|---------|-----------------|------------|
| TR_TD030B2 | TS014C0 Status_Bundles | Consolidation_Execute required |
| TR_TS014C0 | TS014C0 Status_* | Company_SaveCompany triggers |
| TR_TS015S0 | TS014C0 Status_Flows | Ownership_SaveOwnership triggers |
| TR_TS017R0 | TS014C0 Status_ClosingAmounts | ExchangeRate_Save triggers |

### Trigger Bypass via API
```
Import Operations (bypass triggers):
  Import_Execute → P_SYS_IMPORT*:
    - Creates #NO_CLEAR_CONSO_STATUS temp table
    - Triggers skip processing
    - Manual status update at end
```

### Related API Documentation
- [API Index](../11-agent-support/api-index.yaml) - Master handler catalog
- Status flag management via Company_GetCompanies/SaveCompany

---

## Related Documentation

- [Data Tables Catalog](data-tables-catalog.md) - Table reference
- [Index Strategy](index-strategy.md) - Performance optimization
- [Consolidation Workflow](../03-core-calculations/consolidation-workflow.md) - Status flag consumption
- [Data Import Services](../08-application-layer/data-import-services.md) - Bypass usage

---
*Document 45 of 50+ | Batch 15: Advanced Eliminations & Database Patterns | Last Updated: 2024-12-01*
