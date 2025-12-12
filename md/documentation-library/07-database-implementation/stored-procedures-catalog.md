# Consolidation Stored Procedures Catalog

## Document Metadata
- **Category**: Database Implementation
- **Total Procedures**: 65 P_CONSO_* procedures
- **Database**: SQL Server 2022
- **Last Updated**: 2024-12-01
- **Completeness**: 100% cataloged

## Executive Summary

The Prophix.Conso database layer implements consolidation logic through **65 specialized stored procedures** prefixed with `P_CONSO_`. These procedures handle the complete consolidation lifecycle: bundle integration, currency translation, eliminations, intercompany matching, and consolidation events.

## Procedure Categories

### 1. Bundle Integration (8 procedures)

| Procedure | Purpose |
|-----------|---------|
| `P_CONSO_CALCULATE_BUNDLE_INTEGRATION` | **Master orchestrator** - coordinates full bundle integration |
| `P_CONSO_BUNDLE_INTEGRATION_CURRENCY_TRANSLATION_CLOSING` | Currency translation for closing balances |
| `P_CONSO_BUNDLE_INTEGRATION_CURRENCY_TRANSLATION_FLOWS` | Currency translation for flow items |
| `P_CONSO_BUNDLE_INTEGRATION_CURRENCY_TRANSLATION_HISTORICAL` | Historical rate translation |
| `P_CONSO_HELPER_FILL_COMPANY_TABLE` | Populate company selection temp table |
| `P_CONSO_HELPER_FILL_EXCHANGERATE` | Load exchange rates for translation |
| `P_CONSO_UPDATE_COMPANY_STATUS` | Update company consolidation status |
| `P_CONSO_LINKED_CATEGORY` | Process linked account categories |

### 2. Adjustments Integration (4 procedures)

| Procedure | Purpose |
|-----------|---------|
| `P_CONSO_CALCULATE_ADJUSTMENTS_INTEGRATION` | **Master** - orchestrates adjustment integration |
| `P_CONSO_ADJUSTMENTS_INTEGRATION_PREPARATION` | Prepare adjustment data |
| `P_CONSO_ADJUSTMENTS_INTEGRATION_IN_LOCAL_CURRENCY` | Process adjustments in local currency |
| `P_CONSO_ADJUSTMENTS_INTEGRATION_IN_CONSOLIDATION_CURRENCY` | Convert adjustments to conso currency |

### 3. Eliminations (22 procedures)

| Procedure | Purpose | Elim Code |
|-----------|---------|-----------|
| `P_CONSO_ELIM` | **Master orchestrator** - calls all elimination procedures | - |
| `P_CONSO_ELIM_PROPORTIONAL` | Proportional method eliminations | S079 |
| `P_CONSO_ELIM_EQUITYMETHOD` | Equity method eliminations | S081 |
| `P_CONSO_ELIM_NOTCONSOLIDATED` | Non-consolidated company eliminations | S077 |
| `P_CONSO_ELIM_INTERCOMPANY` | Intercompany transaction eliminations | S083 |
| `P_CONSO_ELIM_INTERCOMPANY_NETTING` | IC netting eliminations | - |
| `P_CONSO_ELIM_INTERCOMPANY_NETTING_FULL` | Full IC netting | - |
| `P_CONSO_ELIM_INTERCOMPANY_100PC` | 100% IC eliminations | - |
| `P_CONSO_ELIM_INTERCOMPANY_NE` | IC non-entity eliminations | - |
| `P_CONSO_ELIM_EQUITYCAPITAL` | Equity/capital eliminations | S087 |
| `P_CONSO_ELIM_PARTICIPATIONS0-4` | Participation eliminations (5 procedures) | S089/S090 |
| `P_CONSO_ELIM_MINORITYINTEREST` | Minority interest allocation | S085 |
| `P_CONSO_ELIM_DIVIDEND` | Dividend eliminations | - |
| `P_CONSO_ELIM_EPU` | Equity pickup | - |
| `P_CONSO_ELIM_EPU_REVERSE` | Reverse equity pickup | - |
| `P_CONSO_ELIM_USER` | User-defined eliminations | - |
| `P_CONSO_ELIM_USER_FROM_DATA` | Creates custom elimination data entries | - |
| `P_CONSO_ELIM_USER_PROCESS` | Processes custom elimination journal entries | - |
| `P_CONSO_ELIM_CHANGE_METHOD` | Method change processing | - |

### 4. Consolidation Events (12 procedures)

| Procedure | Purpose |
|-----------|---------|
| `P_CONSO_EVENT_GENERIC` | Generic event processing |
| `P_CONSO_EVENT_PREPARE` | Prepare event data |
| `P_CONSO_EVENT_PROCESS` | Execute event processing |
| `P_CONSO_EVENT_FROM_DATA` | Create event from data |
| `P_CONSO_EVENT_DIVIDENDS` | Process dividend events |
| `P_CONSO_EVENT_EQUITY_TO_GLOBAL` | Convert equity to global method |
| `P_CONSO_EVENT_RECLASS_IC` | Reclassify intercompany |
| `P_CONSO_EVENT_RECONCILE_IC` | Reconcile intercompany |
| `P_CONSO_EVENT_REVERSE_IC` | Reverse intercompany |
| `P_CONSO_EVENT_TRANSFER_IC` | Transfer intercompany |

### 5. Intercompany Matching (4 procedures)

| Procedure | Purpose |
|-----------|---------|
| `P_CONSO_MATCHING_PREPARE` | Prepare matching data |
| `P_CONSO_MATCHING_EXECUTE` | Execute matching rules |
| `P_CONSO_MATCHING_CORRECT` | Apply corrections |
| `P_CONSO_MATCHING_CORRECTION` | Process correction entries |

### 6. Dimension Processing (8 procedures)

| Procedure | Purpose |
|-----------|---------|
| `P_CONSO_DIM_BUNDLE_INTEGRATION_CURRENCY_TRANSLATION_CLOSING` | Dimension currency translation (closing) |
| `P_CONSO_DIM_BUNDLE_INTEGRATION_CURRENCY_TRANSLATION_HISTORICAL` | Dimension currency translation (historical) |
| `P_CONSO_DIM_ADJUSTMENTS_INTEGRATION` | Dimension adjustment integration |
| `P_CONSO_DIM_ELIM` | Dimension eliminations |
| `P_CONSO_DIM_ELIM_IC` | Dimension IC eliminations |
| `P_CONSO_DIM_HELPER_CORRECT_GROUPBUNDLES` | Correct dimension group bundles |
| `P_CONSO_DIM_HELPER_CORRECT_INPUT` | Ensure dimension data correctness before consolidation |
| `P_CONSO_DIM_HELPER_FILL_SPECIAL_DIMENSION_DETAILS` | Fill special dimension details |

### 7. Utility Procedures (10 procedures)

| Procedure | Purpose |
|-----------|---------|
| `P_CONSO_CHECK_LOCKED` | Check if conso is locked |
| `P_CONSO_CHECK_LOCKED_EXTENDED` | Extended lock check |
| `P_CONSO_UNLOCK` | Unlock consolidation |
| `P_CONSO_UNLOCK_BY_GUID` | Unlock by GUID |
| `P_CONSO_CLEAR_TABLES` | Clear consolidation tables |
| `P_CONSO_RECOMPUTE_SPECIFIC_FLOWS` | Recompute specific flows |
| `P_CONSO_RECOMPUTE_SPECIFIC_FLOWS_INTERCOS` | Recompute IC flows |
| `P_CONSO_UPDATE_JOURNAL_ENTRY_MAP` | Update journal mappings |

## Procedure Execution Flow

```
Consolidation Run
      │
      ├─► P_CONSO_CALCULATE_BUNDLE_INTEGRATION (Master)
      │   ├─► P_CONSO_HELPER_FILL_COMPANY_TABLE
      │   ├─► P_CONSO_HELPER_FILL_EXCHANGERATE
      │   ├─► P_CONSO_BUNDLE_INTEGRATION_CURRENCY_TRANSLATION_CLOSING
      │   ├─► P_CONSO_BUNDLE_INTEGRATION_CURRENCY_TRANSLATION_FLOWS
      │   └─► P_CONSO_BUNDLE_INTEGRATION_CURRENCY_TRANSLATION_HISTORICAL
      │
      ├─► P_CONSO_CALCULATE_ADJUSTMENTS_INTEGRATION
      │   ├─► P_CONSO_ADJUSTMENTS_INTEGRATION_PREPARATION
      │   ├─► P_CONSO_ADJUSTMENTS_INTEGRATION_IN_LOCAL_CURRENCY
      │   └─► P_CONSO_ADJUSTMENTS_INTEGRATION_IN_CONSOLIDATION_CURRENCY
      │
      └─► P_CONSO_ELIM (Master)
          ├─► P_CONSO_ELIM_PROPORTIONAL
          ├─► P_CONSO_ELIM_EQUITYMETHOD
          ├─► P_CONSO_ELIM_NOTCONSOLIDATED
          ├─► P_CONSO_ELIM_INTERCOMPANY
          ├─► P_CONSO_ELIM_EQUITYCAPITAL
          ├─► P_CONSO_ELIM_PARTICIPATIONS1-4
          └─► P_CONSO_ELIM_MINORITYINTEREST
```

## Key Tables Used

| Table | Purpose |
|-------|---------|
| `TS096S0` | Consolidation master data |
| `TS014C0` | Company consolidation status |
| `TS070S0` | Elimination headers |
| `TS070S1` | Consolidation method selections |
| `TD035C2` | Consolidated amounts |
| `TD045C2` | Consolidated flows |
| `TMP_TD033E0` | Temporary elimination data |

## Recommendations

1. **Performance Monitoring**: Add execution time logging for large consolidations
2. **Error Handling**: Standardize error output XML format
3. **Documentation**: Add inline comments referencing theory concepts

---

## See Also

### Related Documentation
- [Data Tables Catalog](data-tables-catalog.md) - Table structure reference
- [Journal Types](journal-types.md) - Elimination code definitions
- [Index Strategy](index-strategy.md) - Performance optimization
- [Trigger Patterns](trigger-patterns.md) - Automated data management
- [Temp Table Patterns](temp-table-patterns.md) - Session-based processing

### Consolidation Logic
- [Global Integration](../02-consolidation-methods/global-integration.md) - Full consolidation method
- [Elimination Execution Engine](../08-application-layer/elimination-execution-engine.md) - Application layer
- [Consolidation Workflow](../03-core-calculations/consolidation-workflow.md) - 5-phase process

### Navigation
- [Cross-Reference Index](../00-index/CROSS_REFERENCE_INDEX.md) - Find related documents
- [Quick Reference Card](../20-appendices/quick-reference-card.md) - Procedure signatures
- [Troubleshooting Guide](../17-troubleshooting/common-issues.md) - Issue resolution

---
*Document 7 of 50+ | Batch 3: Implementation | Last Updated: 2024-12-01*