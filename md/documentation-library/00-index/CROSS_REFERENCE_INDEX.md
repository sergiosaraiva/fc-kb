# Cross-Reference Index

## Document Metadata
- **Document Type**: Navigation Index
- **Purpose**: Bidirectional navigation between related documents
- **Total Documents Indexed**: 52
- **Last Updated**: 2025-12-04
- **Version**: 2.0 (Post-Quality Improvement)

---

## Quick Navigation

| I'm Working On... | Start Here | Then See |
|-------------------|------------|----------|
| New consolidation setup | [Global Integration](../02-consolidation-methods/global-integration.md) | [Method Determination](../02-consolidation-methods/consolidation-method-determination.md) |
| Ownership structure | [Ownership Percentages](../06-ownership-structure/ownership-percentages.md) | [Multi-tier Holdings](../06-ownership-structure/multi-tier-holdings.md) |
| Eliminations | [User Eliminations](../04-elimination-entries/user-eliminations.md) | [Elimination Templates](../04-elimination-entries/elimination-templates.md) |
| Currency issues | [Exchange Rate Types](../05-currency-translation/exchange-rate-types.md) | [Translation Adjustments](../05-currency-translation/translation-adjustments.md) |
| Database queries | [Stored Procedures Catalog](../07-database-implementation/stored-procedures-catalog.md) | [Data Tables Catalog](../07-database-implementation/data-tables-catalog.md) |
| Known limitations | [Missing Features](../10-gap-analysis/missing-features.md) | Individual gap documents |
| **Troubleshooting** | [Common Issues](../17-troubleshooting/common-issues.md) | Diagnostic queries |
| **Look up terms** | [Glossary](../20-appendices/glossary.md) | Alphabetical index |
| **Quick reference** | [Quick Reference Card](../20-appendices/quick-reference-card.md) | Codes, queries, tables |

---

## Cross-Reference by Topic

### Consolidation Methods

| Document | Related Documents | Key Connections |
|----------|-------------------|-----------------|
| [Global Integration](../02-consolidation-methods/global-integration.md) | [Minority Interest](../03-core-calculations/minority-interest.md), [Participation Eliminations](../04-elimination-entries/participation-eliminations.md), [Method Determination](../02-consolidation-methods/consolidation-method-determination.md) | >50% control triggers full consolidation with NCI |
| [Equity Method](../02-consolidation-methods/equity-method.md) | [Step Acquisition](../03-core-calculations/step-acquisition.md), [Dividend Eliminations](../04-elimination-entries/dividend-eliminations.md), [Control vs Ownership](../06-ownership-structure/control-vs-ownership.md) | 20-50% significant influence, one-line consolidation |
| [Proportional Method](../02-consolidation-methods/proportional-method.md) | [Step Acquisition](../03-core-calculations/step-acquisition.md), [Intercompany Transactions](../04-elimination-entries/intercompany-transactions.md), [Control vs Ownership](../06-ownership-structure/control-vs-ownership.md) | Joint control, IFRS 11 considerations |
| [Method Determination](../02-consolidation-methods/consolidation-method-determination.md) | [Voting Rights Analysis](../06-ownership-structure/voting-rights-analysis.md), [Control vs Ownership](../06-ownership-structure/control-vs-ownership.md), [Scope Changes](../03-core-calculations/scope-changes.md) | Threshold-based automatic assignment |

### Core Calculations

| Document | Related Documents | Key Connections |
|----------|-------------------|-----------------|
| [Goodwill Calculation](../03-core-calculations/goodwill-calculation.md) | [Participation Eliminations](../04-elimination-entries/participation-eliminations.md), [Step Acquisition](../03-core-calculations/step-acquisition.md), [Impairment Testing](../03-core-calculations/impairment-testing.md), [Deconsolidation](../03-core-calculations/deconsolidation.md) | Acquisition accounting, NCI options |
| [Minority Interest](../03-core-calculations/minority-interest.md) | [Global Integration](../02-consolidation-methods/global-integration.md), [Multi-tier Holdings](../06-ownership-structure/multi-tier-holdings.md), [Participation Eliminations](../04-elimination-entries/participation-eliminations.md), [Equity Reconciliation](../03-core-calculations/equity-reconciliation.md) | NCI allocation across tiers |
| [Circular Ownership](../03-core-calculations/circular-ownership.md) | [Multi-tier Holdings](../06-ownership-structure/multi-tier-holdings.md), [Ownership Percentages](../06-ownership-structure/ownership-percentages.md), [Treasury Shares](../03-core-calculations/treasury-shares.md) | Matrix algebra via Gauss elimination |
| [Flow Management](../03-core-calculations/flow-management.md) | [Equity Reconciliation](../03-core-calculations/equity-reconciliation.md), [Journal Types](../07-database-implementation/journal-types.md), [Scope Changes](../03-core-calculations/scope-changes.md), [Step Acquisition](../03-core-calculations/step-acquisition.md) | Special flows, movement analysis |
| [Treasury Shares](../03-core-calculations/treasury-shares.md) | [Circular Ownership](../03-core-calculations/circular-ownership.md), [Ownership Percentages](../06-ownership-structure/ownership-percentages.md), [User Eliminations](../04-elimination-entries/user-eliminations.md), [Missing Features](../10-gap-analysis/missing-features.md) | GAP - Manual workaround |
| [Step Acquisition](../03-core-calculations/step-acquisition.md) | [Goodwill Calculation](../03-core-calculations/goodwill-calculation.md), [Equity Method](../02-consolidation-methods/equity-method.md), [Proportional Method](../02-consolidation-methods/proportional-method.md), [Flow Management](../03-core-calculations/flow-management.md), [Missing Features](../10-gap-analysis/missing-features.md) | Method transitions E→G, P→G |
| [Preference Shares](../03-core-calculations/preference-shares.md) | [Ownership Percentages](../06-ownership-structure/ownership-percentages.md), [Minority Interest](../03-core-calculations/minority-interest.md), [User Eliminations](../04-elimination-entries/user-eliminations.md), [Missing Features](../10-gap-analysis/missing-features.md) | GAP - Virtual entity workaround |
| [Impairment Testing](../03-core-calculations/impairment-testing.md) | [Goodwill Calculation](../03-core-calculations/goodwill-calculation.md), [User Eliminations](../04-elimination-entries/user-eliminations.md), [Missing Features](../10-gap-analysis/missing-features.md) | GAP - External calculation |
| [Scope Changes](../03-core-calculations/scope-changes.md) | [Deconsolidation](../03-core-calculations/deconsolidation.md), [Step Acquisition](../03-core-calculations/step-acquisition.md), [Flow Management](../03-core-calculations/flow-management.md), [Method Determination](../02-consolidation-methods/consolidation-method-determination.md) | Entry/exit detection |
| [Deconsolidation](../03-core-calculations/deconsolidation.md) | [Scope Changes](../03-core-calculations/scope-changes.md), [Goodwill Calculation](../03-core-calculations/goodwill-calculation.md), [Translation Adjustments](../05-currency-translation/translation-adjustments.md), [User Eliminations](../04-elimination-entries/user-eliminations.md) | Disposal accounting, CTA recycling |
| [Consolidation Workflow](../03-core-calculations/consolidation-workflow.md) | [Elimination Execution Engine](../08-application-layer/elimination-execution-engine.md), [Consolidation Services](../08-application-layer/consolidation-services.md), [Job Management](../08-application-layer/job-management.md) | 5-phase orchestration |
| [Equity Reconciliation](../03-core-calculations/equity-reconciliation.md) | [Flow Management](../03-core-calculations/flow-management.md), [Minority Interest](../03-core-calculations/minority-interest.md), [Journal Types](../07-database-implementation/journal-types.md), [Reporting Services](../08-application-layer/reporting-services.md) | Movement analysis by journal |
| [Deferred Tax](../03-core-calculations/deferred-tax.md) | [Elimination Templates](../04-elimination-entries/elimination-templates.md), [User Eliminations](../04-elimination-entries/user-eliminations.md), [Intercompany Pricing](../03-core-calculations/intercompany-pricing.md) | Automatic IAS 12 calculation |
| [Intercompany Pricing](../03-core-calculations/intercompany-pricing.md) | [Profit-in-Stock Eliminations](../04-elimination-entries/profit-in-stock-eliminations.md), [Intercompany Transactions](../04-elimination-entries/intercompany-transactions.md), [Deferred Tax](../03-core-calculations/deferred-tax.md) | Transfer pricing, stock margins |

### Elimination Entries

| Document | Related Documents | Key Connections |
|----------|-------------------|-----------------|
| [Participation Eliminations](../04-elimination-entries/participation-eliminations.md) | [Goodwill Calculation](../03-core-calculations/goodwill-calculation.md), [Global Integration](../02-consolidation-methods/global-integration.md), [Minority Interest](../03-core-calculations/minority-interest.md), [Elimination Execution Engine](../08-application-layer/elimination-execution-engine.md) | S050-S054 investment elimination |
| [Dividend Eliminations](../04-elimination-entries/dividend-eliminations.md) | [Dividend Calculation Logic](../04-elimination-entries/dividend-calculation-logic.md), [Equity Method](../02-consolidation-methods/equity-method.md), [Intercompany Transactions](../04-elimination-entries/intercompany-transactions.md) | S020 four-line journal |
| [Dividend Calculation Logic](../04-elimination-entries/dividend-calculation-logic.md) | [Dividend Eliminations](../04-elimination-entries/dividend-eliminations.md), [Journal Types](../07-database-implementation/journal-types.md), [Elimination Execution Engine](../08-application-layer/elimination-execution-engine.md) | FinPercentage-based calculation |
| [Intercompany Transactions](../04-elimination-entries/intercompany-transactions.md) | [Profit-in-Stock Eliminations](../04-elimination-entries/profit-in-stock-eliminations.md), [Intercompany Pricing](../03-core-calculations/intercompany-pricing.md), [User Eliminations](../04-elimination-entries/user-eliminations.md) | S030 netting elimination |
| [User Eliminations](../04-elimination-entries/user-eliminations.md) | [Elimination Templates](../04-elimination-entries/elimination-templates.md), [All Gap Documents](../10-gap-analysis/missing-features.md), [Adjustment Screens](../09-frontend-implementation/adjustment-screens.md) | TS070S0/TS071S0 framework |
| [Profit-in-Stock Eliminations](../04-elimination-entries/profit-in-stock-eliminations.md) | [Intercompany Transactions](../04-elimination-entries/intercompany-transactions.md), [Intercompany Pricing](../03-core-calculations/intercompany-pricing.md), [User Eliminations](../04-elimination-entries/user-eliminations.md) | Unrealized profit removal |
| [Elimination Templates](../04-elimination-entries/elimination-templates.md) | [User Eliminations](../04-elimination-entries/user-eliminations.md), [Journal Types](../07-database-implementation/journal-types.md), [Deferred Tax](../03-core-calculations/deferred-tax.md) | Configuration patterns |

### Currency Translation

| Document | Related Documents | Key Connections |
|----------|-------------------|-----------------|
| [Exchange Rate Types](../05-currency-translation/exchange-rate-types.md) | [Translation Methods](../05-currency-translation/translation-methods.md), [Hyperinflation Accounting](../05-currency-translation/hyperinflation-accounting.md), [Data Tables Catalog](../07-database-implementation/data-tables-catalog.md) | CC, AC, MC rate codes |
| [Translation Methods](../05-currency-translation/translation-methods.md) | [Exchange Rate Types](../05-currency-translation/exchange-rate-types.md), [Translation Adjustments](../05-currency-translation/translation-adjustments.md), [Hyperinflation Accounting](../05-currency-translation/hyperinflation-accounting.md) | Current vs temporal method |
| [Translation Adjustments](../05-currency-translation/translation-adjustments.md) | [Translation Methods](../05-currency-translation/translation-methods.md), [Deconsolidation](../03-core-calculations/deconsolidation.md), [Equity Reconciliation](../03-core-calculations/equity-reconciliation.md), [Flow Management](../03-core-calculations/flow-management.md) | CTA calculation and recycling |
| [Hyperinflation Accounting](../05-currency-translation/hyperinflation-accounting.md) | [Translation Methods](../05-currency-translation/translation-methods.md), [Exchange Rate Types](../05-currency-translation/exchange-rate-types.md), [User Eliminations](../04-elimination-entries/user-eliminations.md), [Missing Features](../10-gap-analysis/missing-features.md) | IAS 29, temporal method config |

### Ownership Structure

| Document | Related Documents | Key Connections |
|----------|-------------------|-----------------|
| [Direct-Indirect Holdings](../06-ownership-structure/direct-indirect-holdings.md) | [Multi-tier Holdings](../06-ownership-structure/multi-tier-holdings.md), [Ownership Percentages](../06-ownership-structure/ownership-percentages.md), [Circular Ownership](../03-core-calculations/circular-ownership.md) | Holding chain calculation |
| [Ownership Percentages](../06-ownership-structure/ownership-percentages.md) | [Direct-Indirect Holdings](../06-ownership-structure/direct-indirect-holdings.md), [Voting Rights Analysis](../06-ownership-structure/voting-rights-analysis.md), [Control vs Ownership](../06-ownership-structure/control-vs-ownership.md), [Treasury Shares](../03-core-calculations/treasury-shares.md) | Financial vs voting vs control |
| [Control vs Ownership](../06-ownership-structure/control-vs-ownership.md) | [Method Determination](../02-consolidation-methods/consolidation-method-determination.md), [Voting Rights Analysis](../06-ownership-structure/voting-rights-analysis.md), [Missing Features](../10-gap-analysis/missing-features.md) | De facto control considerations |
| [Voting Rights Analysis](../06-ownership-structure/voting-rights-analysis.md) | [Control vs Ownership](../06-ownership-structure/control-vs-ownership.md), [Ownership Percentages](../06-ownership-structure/ownership-percentages.md), [Method Determination](../02-consolidation-methods/consolidation-method-determination.md) | CtrlPercentage calculation |
| [Multi-tier Holdings](../06-ownership-structure/multi-tier-holdings.md) | [Direct-Indirect Holdings](../06-ownership-structure/direct-indirect-holdings.md), [Circular Ownership](../03-core-calculations/circular-ownership.md), [Minority Interest](../03-core-calculations/minority-interest.md), [Ownership Screens](../09-frontend-implementation/ownership-screens.md) | Matrix algebra G = D + G×D |

### Database Implementation

| Document | Related Documents | Key Connections |
|----------|-------------------|-----------------|
| [Stored Procedures Catalog](../07-database-implementation/stored-procedures-catalog.md) | [Elimination Execution Engine](../08-application-layer/elimination-execution-engine.md), [Data Tables Catalog](../07-database-implementation/data-tables-catalog.md), [Consolidation Workflow](../03-core-calculations/consolidation-workflow.md) | 65+ P_CONSO_* procedures |
| [Data Tables Catalog](../07-database-implementation/data-tables-catalog.md) | [Stored Procedures Catalog](../07-database-implementation/stored-procedures-catalog.md), [Temp Table Patterns](../07-database-implementation/temp-table-patterns.md), [Index Strategy](../07-database-implementation/index-strategy.md) | 93 consolidation tables |
| [Journal Types](../07-database-implementation/journal-types.md) | [Elimination Execution Engine](../08-application-layer/elimination-execution-engine.md), [User Eliminations](../04-elimination-entries/user-eliminations.md), [Equity Reconciliation](../03-core-calculations/equity-reconciliation.md) | S001-S085 codes |
| [Index Strategy](../07-database-implementation/index-strategy.md) | [Data Tables Catalog](../07-database-implementation/data-tables-catalog.md), [Temp Table Patterns](../07-database-implementation/temp-table-patterns.md) | ConsoID-first indexing |
| [Trigger Patterns](../07-database-implementation/trigger-patterns.md) | [Data Tables Catalog](../07-database-implementation/data-tables-catalog.md), [Consolidation Workflow](../03-core-calculations/consolidation-workflow.md) | Status management, bypass pattern |
| [Temp Table Patterns](../07-database-implementation/temp-table-patterns.md) | [Data Tables Catalog](../07-database-implementation/data-tables-catalog.md), [Index Strategy](../07-database-implementation/index-strategy.md), [Stored Procedures Catalog](../07-database-implementation/stored-procedures-catalog.md) | 80+ TMP_* tables |

### Application Layer

| Document | Related Documents | Key Connections |
|----------|-------------------|-----------------|
| [Consolidation Services](../08-application-layer/consolidation-services.md) | [Consolidation Workflow](../03-core-calculations/consolidation-workflow.md), [Job Management](../08-application-layer/job-management.md), [Consolidation Screens](../09-frontend-implementation/consolidation-screens.md) | Service layer architecture |
| [Elimination Execution Engine](../08-application-layer/elimination-execution-engine.md) | [Stored Procedures Catalog](../07-database-implementation/stored-procedures-catalog.md), [Journal Types](../07-database-implementation/journal-types.md), [All Elimination Docs](../04-elimination-entries/) | P_CONSO_ELIM orchestration |
| [Data Import Services](../08-application-layer/data-import-services.md) | [Data Entry Screens](../09-frontend-implementation/data-entry-screens.md), [Stored Procedures Catalog](../07-database-implementation/stored-procedures-catalog.md) | 64+ P_SYS_IMPORT procedures |
| [Reporting Services](../08-application-layer/reporting-services.md) | [Equity Reconciliation](../03-core-calculations/equity-reconciliation.md), [Stored Procedures Catalog](../07-database-implementation/stored-procedures-catalog.md) | 179+ P_REPORT_* procedures |
| [Job Management](../08-application-layer/job-management.md) | [Consolidation Services](../08-application-layer/consolidation-services.md), [Consolidation Workflow](../03-core-calculations/consolidation-workflow.md) | 50+ Hangfire job classes |

### Frontend Implementation

| Document | Related Documents | Key Connections |
|----------|-------------------|-----------------|
| [Consolidation Screens](../09-frontend-implementation/consolidation-screens.md) | [Consolidation Services](../08-application-layer/consolidation-services.md), [Consolidation Workflow](../03-core-calculations/consolidation-workflow.md) | TypeScript/Knockout.js MVVM |
| [Ownership Screens](../09-frontend-implementation/ownership-screens.md) | [Multi-tier Holdings](../06-ownership-structure/multi-tier-holdings.md), [Ownership Percentages](../06-ownership-structure/ownership-percentages.md) | Financial vs voting display |
| [Data Entry Screens](../09-frontend-implementation/data-entry-screens.md) | [Data Import Services](../08-application-layer/data-import-services.md), [Consolidation Screens](../09-frontend-implementation/consolidation-screens.md) | Bundle entry, Excel integration |
| [Adjustment Screens](../09-frontend-implementation/adjustment-screens.md) | [User Eliminations](../04-elimination-entries/user-eliminations.md), [Elimination Templates](../04-elimination-entries/elimination-templates.md) | Debit/credit entry, approval |

---

## Cross-Reference by Stored Procedure

| Procedure | Primary Document | Related Documents |
|-----------|------------------|-------------------|
| P_CONSO_CALCULATE_BUNDLE_INTEGRATION | [Consolidation Workflow](../03-core-calculations/consolidation-workflow.md) | [Consolidation Services](../08-application-layer/consolidation-services.md), [Global Integration](../02-consolidation-methods/global-integration.md) |
| P_CONSO_ELIM | [Elimination Execution Engine](../08-application-layer/elimination-execution-engine.md) | [Stored Procedures Catalog](../07-database-implementation/stored-procedures-catalog.md), [Journal Types](../07-database-implementation/journal-types.md) |
| P_CONSO_ELIM_PARTICIPATIONS0-4 | [Participation Eliminations](../04-elimination-entries/participation-eliminations.md) | [Goodwill Calculation](../03-core-calculations/goodwill-calculation.md), [Elimination Execution Engine](../08-application-layer/elimination-execution-engine.md) |
| P_CONSO_ELIM_DIVIDEND | [Dividend Eliminations](../04-elimination-entries/dividend-eliminations.md) | [Dividend Calculation Logic](../04-elimination-entries/dividend-calculation-logic.md) |
| P_CONSO_ELIM_MINORITYINTEREST | [Minority Interest](../03-core-calculations/minority-interest.md) | [Global Integration](../02-consolidation-methods/global-integration.md), [Multi-tier Holdings](../06-ownership-structure/multi-tier-holdings.md) |
| P_CONSO_ELIM_EQUITYMETHOD | [Equity Method](../02-consolidation-methods/equity-method.md) | [Dividend Eliminations](../04-elimination-entries/dividend-eliminations.md) |
| P_CONSO_ELIM_PROPORTIONAL | [Proportional Method](../02-consolidation-methods/proportional-method.md) | [Intercompany Transactions](../04-elimination-entries/intercompany-transactions.md) |
| P_CONSO_ELIM_USER | [User Eliminations](../04-elimination-entries/user-eliminations.md) | [Elimination Templates](../04-elimination-entries/elimination-templates.md), [All Gap Documents](../10-gap-analysis/missing-features.md) |
| P_CONSO_ELIM_CHANGE_METHOD | [Step Acquisition](../03-core-calculations/step-acquisition.md) | [Scope Changes](../03-core-calculations/scope-changes.md), [Flow Management](../03-core-calculations/flow-management.md) |
| P_CONSO_ELIM_INTERCOMPANY_NETTING | [Intercompany Transactions](../04-elimination-entries/intercompany-transactions.md) | [Profit-in-Stock Eliminations](../04-elimination-entries/profit-in-stock-eliminations.md) |
| P_CALC_OWNERSHIP_INDIRECT_PERCENTAGES | [Multi-tier Holdings](../06-ownership-structure/multi-tier-holdings.md) | [Circular Ownership](../03-core-calculations/circular-ownership.md), [Ownership Percentages](../06-ownership-structure/ownership-percentages.md) |
| P_CALC_OWNERSHIP_DIRECT_PERCENTAGES | [Ownership Percentages](../06-ownership-structure/ownership-percentages.md) | [Direct-Indirect Holdings](../06-ownership-structure/direct-indirect-holdings.md) |
| P_VIEW_OWNERSHIP | [Ownership Screens](../09-frontend-implementation/ownership-screens.md) | [Multi-tier Holdings](../06-ownership-structure/multi-tier-holdings.md) |
| P_REPORT_GOODWILL | [Goodwill Calculation](../03-core-calculations/goodwill-calculation.md) | [Reporting Services](../08-application-layer/reporting-services.md) |
| P_REPORT_CONSOLIDATED_EQUITY | [Equity Reconciliation](../03-core-calculations/equity-reconciliation.md) | [Reporting Services](../08-application-layer/reporting-services.md) |

---

## Cross-Reference by Database Table

| Table | Primary Document | Related Documents |
|-------|------------------|-------------------|
| TS014C0 | [Data Tables Catalog](../07-database-implementation/data-tables-catalog.md) | [Method Determination](../02-consolidation-methods/consolidation-method-determination.md), [Scope Changes](../03-core-calculations/scope-changes.md) |
| TS015S0 | [Ownership Percentages](../06-ownership-structure/ownership-percentages.md) | [Multi-tier Holdings](../06-ownership-structure/multi-tier-holdings.md), [Direct-Indirect Holdings](../06-ownership-structure/direct-indirect-holdings.md) |
| TS070S0 | [User Eliminations](../04-elimination-entries/user-eliminations.md) | [Elimination Templates](../04-elimination-entries/elimination-templates.md) |
| TS071S0 | [User Eliminations](../04-elimination-entries/user-eliminations.md) | [Elimination Templates](../04-elimination-entries/elimination-templates.md) |
| TS011C0 | [Flow Management](../03-core-calculations/flow-management.md) | [Journal Types](../07-database-implementation/journal-types.md) |
| TS011C1 | [Flow Management](../03-core-calculations/flow-management.md) | [Step Acquisition](../03-core-calculations/step-acquisition.md) |
| TS020S0 | [Journal Types](../07-database-implementation/journal-types.md) | [Elimination Execution Engine](../08-application-layer/elimination-execution-engine.md) |
| TS017R0 | [Exchange Rate Types](../05-currency-translation/exchange-rate-types.md) | [Translation Methods](../05-currency-translation/translation-methods.md) |
| TD035C2 | [Data Tables Catalog](../07-database-implementation/data-tables-catalog.md) | [Consolidation Workflow](../03-core-calculations/consolidation-workflow.md) |
| TD045C2 | [Data Tables Catalog](../07-database-implementation/data-tables-catalog.md) | [Journal Types](../07-database-implementation/journal-types.md), [Elimination Execution Engine](../08-application-layer/elimination-execution-engine.md) |
| TS010S0 | [Data Tables Catalog](../07-database-implementation/data-tables-catalog.md) | [Exchange Rate Types](../05-currency-translation/exchange-rate-types.md), [Hyperinflation Accounting](../05-currency-translation/hyperinflation-accounting.md) |

---

## Cross-Reference by Elimination Code

| Code | Description | Primary Document | Related Documents |
|------|-------------|------------------|-------------------|
| S001 | Opening Balance | [Journal Types](../07-database-implementation/journal-types.md) | [Consolidation Workflow](../03-core-calculations/consolidation-workflow.md) |
| S010 | Equity Capital | [Participation Eliminations](../04-elimination-entries/participation-eliminations.md) | [Goodwill Calculation](../03-core-calculations/goodwill-calculation.md) |
| S020 | Dividends | [Dividend Eliminations](../04-elimination-entries/dividend-eliminations.md) | [Dividend Calculation Logic](../04-elimination-entries/dividend-calculation-logic.md) |
| S030 | Intercompany Netting | [Intercompany Transactions](../04-elimination-entries/intercompany-transactions.md) | [Profit-in-Stock Eliminations](../04-elimination-entries/profit-in-stock-eliminations.md) |
| S040 | Equity Method | [Equity Method](../02-consolidation-methods/equity-method.md) | [Dividend Eliminations](../04-elimination-entries/dividend-eliminations.md) |
| S050-54 | Participations | [Participation Eliminations](../04-elimination-entries/participation-eliminations.md) | [Goodwill Calculation](../03-core-calculations/goodwill-calculation.md), [Minority Interest](../03-core-calculations/minority-interest.md) |
| S060 | Proportional | [Proportional Method](../02-consolidation-methods/proportional-method.md) | [Intercompany Transactions](../04-elimination-entries/intercompany-transactions.md) |
| S072 | Method Change | [Step Acquisition](../03-core-calculations/step-acquisition.md) | [Scope Changes](../03-core-calculations/scope-changes.md), [Flow Management](../03-core-calculations/flow-management.md) |
| S085 | Minority Interest | [Minority Interest](../03-core-calculations/minority-interest.md) | [Global Integration](../02-consolidation-methods/global-integration.md) |
| U### | User-Defined | [User Eliminations](../04-elimination-entries/user-eliminations.md) | [Elimination Templates](../04-elimination-entries/elimination-templates.md), [All Gap Documents](../10-gap-analysis/missing-features.md) |

---

## Cross-Reference by IFRS Standard

| Standard | Primary Document | Related Documents |
|----------|------------------|-------------------|
| IFRS 3 (Business Combinations) | [Goodwill Calculation](../03-core-calculations/goodwill-calculation.md) | [Step Acquisition](../03-core-calculations/step-acquisition.md), [Participation Eliminations](../04-elimination-entries/participation-eliminations.md) |
| IFRS 10 (Consolidated FS) | [Global Integration](../02-consolidation-methods/global-integration.md) | [Minority Interest](../03-core-calculations/minority-interest.md), [Control vs Ownership](../06-ownership-structure/control-vs-ownership.md) |
| IFRS 11 (Joint Arrangements) | [Proportional Method](../02-consolidation-methods/proportional-method.md) | [Method Determination](../02-consolidation-methods/consolidation-method-determination.md) |
| IAS 12 (Income Taxes) | [Deferred Tax](../03-core-calculations/deferred-tax.md) | [Elimination Templates](../04-elimination-entries/elimination-templates.md), [Intercompany Pricing](../03-core-calculations/intercompany-pricing.md) |
| IAS 21 (Currency) | [Translation Methods](../05-currency-translation/translation-methods.md) | [Exchange Rate Types](../05-currency-translation/exchange-rate-types.md), [Translation Adjustments](../05-currency-translation/translation-adjustments.md) |
| IAS 27 (Separate FS) | [Equity Method](../02-consolidation-methods/equity-method.md) | [Dividend Eliminations](../04-elimination-entries/dividend-eliminations.md) |
| IAS 28 (Associates) | [Equity Method](../02-consolidation-methods/equity-method.md) | [Control vs Ownership](../06-ownership-structure/control-vs-ownership.md), [Voting Rights Analysis](../06-ownership-structure/voting-rights-analysis.md) |
| IAS 29 (Hyperinflation) | [Hyperinflation Accounting](../05-currency-translation/hyperinflation-accounting.md) | [Translation Methods](../05-currency-translation/translation-methods.md), [Missing Features](../10-gap-analysis/missing-features.md) |
| IAS 36 (Impairment) | [Impairment Testing](../03-core-calculations/impairment-testing.md) | [Goodwill Calculation](../03-core-calculations/goodwill-calculation.md), [Missing Features](../10-gap-analysis/missing-features.md) |

---

## Gap Document Cross-References

| Gap | Primary Document | Workaround Document | Related System Documents |
|-----|------------------|---------------------|--------------------------|
| Treasury Shares | [Treasury Shares](../03-core-calculations/treasury-shares.md) | [User Eliminations](../04-elimination-entries/user-eliminations.md) | [Circular Ownership](../03-core-calculations/circular-ownership.md), [Ownership Percentages](../06-ownership-structure/ownership-percentages.md) |
| Step Acquisition | [Step Acquisition](../03-core-calculations/step-acquisition.md) | [User Eliminations](../04-elimination-entries/user-eliminations.md), [Flow Management](../03-core-calculations/flow-management.md) | [Goodwill Calculation](../03-core-calculations/goodwill-calculation.md), [Equity Method](../02-consolidation-methods/equity-method.md) |
| Preference Shares | [Preference Shares](../03-core-calculations/preference-shares.md) | [User Eliminations](../04-elimination-entries/user-eliminations.md) | [Ownership Percentages](../06-ownership-structure/ownership-percentages.md), [Minority Interest](../03-core-calculations/minority-interest.md) |
| Impairment Testing | [Impairment Testing](../03-core-calculations/impairment-testing.md) | [User Eliminations](../04-elimination-entries/user-eliminations.md) | [Goodwill Calculation](../03-core-calculations/goodwill-calculation.md) |
| IAS 29 Automation | [Hyperinflation Accounting](../05-currency-translation/hyperinflation-accounting.md) | [User Eliminations](../04-elimination-entries/user-eliminations.md) | [Translation Methods](../05-currency-translation/translation-methods.md), [Exchange Rate Types](../05-currency-translation/exchange-rate-types.md) |

---

## Document Dependency Graph

```
                              ┌─────────────────────────────┐
                              │     Executive Summary       │
                              │    (EXECUTIVE_SUMMARY.md)   │
                              └─────────────┬───────────────┘
                                            │
         ┌──────────────────────────────────┼──────────────────────────────────┐
         │                                  │                                  │
         ▼                                  ▼                                  ▼
┌─────────────────┐              ┌─────────────────┐              ┌─────────────────┐
│ Consolidation   │              │ Core            │              │ Gap Analysis    │
│ Methods (4)     │              │ Calculations    │              │ (1)             │
│                 │              │ (13)            │              │                 │
│ • Global        │◄────────────►│ • Goodwill      │◄────────────►│ • Missing       │
│ • Equity        │              │ • Minority      │              │   Features      │
│ • Proportional  │              │ • Circular      │              │                 │
│ • Determination │              │ • Flow Mgmt     │              └────────┬────────┘
└────────┬────────┘              │ • Step Acq      │                       │
         │                       │ • Treasury      │                       │
         │                       │ • Preference    │                       │
         │                       │ • Impairment    │                       │
         │                       └────────┬────────┘                       │
         │                                │                                │
         └────────────────┬───────────────┴───────────────┬────────────────┘
                          │                               │
                          ▼                               ▼
               ┌─────────────────┐              ┌─────────────────┐
               │ Elimination     │              │ Ownership       │
               │ Entries (6)     │              │ Structure (5)   │
               │                 │              │                 │
               │ • Participation │◄────────────►│ • Direct/Ind    │
               │ • Dividend      │              │ • Percentages   │
               │ • Intercompany  │              │ • Control       │
               │ • User Elim     │              │ • Voting        │
               │ • Templates     │              │ • Multi-tier    │
               └────────┬────────┘              └────────┬────────┘
                        │                                │
         ┌──────────────┴────────────────────────────────┘
         │
         ▼
┌─────────────────┐              ┌─────────────────┐              ┌─────────────────┐
│ Currency        │              │ Database        │              │ Application     │
│ Translation (4) │              │ Implementation  │              │ Layer (5)       │
│                 │              │ (6)             │              │                 │
│ • Exchange Rate │◄────────────►│ • Procedures    │◄────────────►│ • Services      │
│ • Methods       │              │ • Tables        │              │ • Elim Engine   │
│ • CTA           │              │ • Journal Types │              │ • Import        │
│ • Hyperinflation│              │ • Index/Trigger │              │ • Reporting     │
└─────────────────┘              │ • Temp Tables   │              │ • Jobs          │
                                 └────────┬────────┘              └────────┬────────┘
                                          │                                │
                                          └────────────────┬───────────────┘
                                                           │
                                                           ▼
                                                ┌─────────────────┐
                                                │ Frontend        │
                                                │ Implementation  │
                                                │ (4)             │
                                                │                 │
                                                │ • Consolidation │
                                                │ • Ownership     │
                                                │ • Data Entry    │
                                                │ • Adjustments   │
                                                └─────────────────┘
```

---

## API Reference Cross-Reference

### API Documentation Files (11-agent-support/)

| YAML File | Handlers | Primary Theory Documents |
|-----------|----------|-------------------------|
| [api-consolidation-endpoints.yaml](../11-agent-support/api-consolidation-endpoints.yaml) | 12 | [Global Integration](../02-consolidation-methods/global-integration.md), [Consolidation Workflow](../03-core-calculations/consolidation-workflow.md) |
| [api-ownership-endpoints.yaml](../11-agent-support/api-ownership-endpoints.yaml) | 3 | [Ownership Percentages](../06-ownership-structure/ownership-percentages.md), [Circular Ownership](../03-core-calculations/circular-ownership.md), [Multi-tier Holdings](../06-ownership-structure/multi-tier-holdings.md) |
| [api-elimination-endpoints.yaml](../11-agent-support/api-elimination-endpoints.yaml) | 18 | [Participation Eliminations](../04-elimination-entries/participation-eliminations.md), [Intercompany Transactions](../04-elimination-entries/intercompany-transactions.md) |
| [api-event-endpoints.yaml](../11-agent-support/api-event-endpoints.yaml) | 7 | [Consolidation Workflow](../03-core-calculations/consolidation-workflow.md), [Elimination Templates](../04-elimination-entries/elimination-templates.md) |
| [api-company-endpoints.yaml](../11-agent-support/api-company-endpoints.yaml) | 8 | [Method Determination](../02-consolidation-methods/consolidation-method-determination.md) |
| [api-account-endpoints.yaml](../11-agent-support/api-account-endpoints.yaml) | 20 | [Participation Eliminations](../04-elimination-entries/participation-eliminations.md), [User Eliminations](../04-elimination-entries/user-eliminations.md) |
| [api-currency-endpoints.yaml](../11-agent-support/api-currency-endpoints.yaml) | 12 | [Exchange Rate Types](../05-currency-translation/exchange-rate-types.md), [Translation Methods](../05-currency-translation/translation-methods.md) |
| [api-data-entry-endpoints.yaml](../11-agent-support/api-data-entry-endpoints.yaml) | 27 | [Data Entry Screens](../09-frontend-implementation/data-entry-screens.md) |
| [api-adjustment-endpoints.yaml](../11-agent-support/api-adjustment-endpoints.yaml) | 20 | [User Eliminations](../04-elimination-entries/user-eliminations.md), [Adjustment Screens](../09-frontend-implementation/adjustment-screens.md) |
| [api-interco-endpoints.yaml](../11-agent-support/api-interco-endpoints.yaml) | 17 | [Intercompany Transactions](../04-elimination-entries/intercompany-transactions.md), [Intercompany Pricing](../03-core-calculations/intercompany-pricing.md) |
| [api-reports-endpoints.yaml](../11-agent-support/api-reports-endpoints.yaml) | 24 | [Reporting Services](../08-application-layer/reporting-services.md), [Equity Reconciliation](../03-core-calculations/equity-reconciliation.md) |
| [api-job-monitoring-endpoints.yaml](../11-agent-support/api-job-monitoring-endpoints.yaml) | 4 | [Job Management](../08-application-layer/job-management.md), [Consolidation Workflow](../03-core-calculations/consolidation-workflow.md) |
| [api-validation-rule-endpoints.yaml](../11-agent-support/api-validation-rule-endpoints.yaml) | 6 | [Consolidation Workflow](../03-core-calculations/consolidation-workflow.md) |
| [api-import-data-endpoints.yaml](../11-agent-support/api-import-data-endpoints.yaml) | 12 | [Data Import Services](../08-application-layer/data-import-services.md) |
| [api-export-data-endpoints.yaml](../11-agent-support/api-export-data-endpoints.yaml) | 3 | [Reporting Services](../08-application-layer/reporting-services.md) |

### Key API Handlers by Theory Concept

| Theory Concept | Primary Handler | Supporting Handlers | Status |
|---------------|-----------------|---------------------|--------|
| Global Integration | `Consolidation_Execute` | `Company_GetCompanies`, `Event_GetEvents` | ✅ IMPLEMENTED |
| Equity Method | `Consolidation_Execute` (S081) | `Ownership_GetOwnership` | ✅ IMPLEMENTED |
| Proportional Method | `Consolidation_Execute` (S079) | `Ownership_GetOwnership` | ✅ IMPLEMENTED |
| Method Determination | `LaunchCalculateIndirectPercentagesJob` | `Ownership_SaveOwnership` | ✅ IMPLEMENTED |
| Circular Ownership | `LaunchCalculateIndirectPercentagesJob` | `Ownership_GetOwnership` | ✅ IMPLEMENTED |
| Minority Interest | `Consolidation_Execute` (S085) | `Report_ExecuteReport` | ✅ IMPLEMENTED |
| Goodwill Calculation | `Report_ExecuteReport` | `Journal_SaveJournal` | ⚠️ PARTIAL |
| Participation Eliminations | `Elimination_GetEliminations` | `Consolidation_Execute` | ✅ IMPLEMENTED |
| Dividend Eliminations | `Consolidation_Execute` (S020) | `Elimination_GetEliminations` | ✅ IMPLEMENTED |
| Intercompany Transactions | `IntercoDataEntry_GetData` | `IntercoMatching_GetMatchingStatus` | ✅ IMPLEMENTED |
| Currency Translation | `ExchangeRate_GetExchangeRates` | `ImportExchangeRates_Import` | ✅ IMPLEMENTED |
| Step Acquisition | Manual via `Journal_SaveJournal` | - | ❌ NOT_IMPLEMENTED |
| Treasury Shares | Manual via `Ownership_SaveOwnership` | - | ❌ NOT_IMPLEMENTED |
| Impairment Testing | External + `Journal_SaveJournal` | - | ❌ NOT_IMPLEMENTED |

### API Master Reference Documents

| Document | Purpose | Location |
|----------|---------|----------|
| [api-index.yaml](../11-agent-support/api-index.yaml) | Master catalog of 242 handlers | 11-agent-support/ |
| [api-workflow-diagrams.yaml](../11-agent-support/api-workflow-diagrams.yaml) | 9 Mermaid workflow diagrams | 11-agent-support/ |
| [api-error-handling.yaml](../11-agent-support/api-error-handling.yaml) | Error patterns & recovery | 11-agent-support/ |
| [api-validation-report.yaml](../11-agent-support/api-validation-report.yaml) | Handler verification (76% coverage) | 11-agent-support/ |
| [gap-analysis-report.yaml](../11-agent-support/gap-analysis-report.yaml) | Theory-to-implementation mapping (87%) | 11-agent-support/ |

---

## How to Use This Index

### Finding Related Content
1. **By Topic**: Use the topic tables to find all documents related to a specific area
2. **By Procedure**: Look up a stored procedure to find its documentation
3. **By Table**: Find which documents reference a specific database table
4. **By Standard**: Navigate from IFRS/IAS standards to implementation docs

### Following Dependencies
1. Start with the primary document for your topic
2. Check the "Related Documents" column for supporting information
3. Use the dependency graph to understand document relationships

### Gap Research
1. Start with [Missing Features](../10-gap-analysis/missing-features.md)
2. Navigate to the specific gap document
3. Check the workaround document for solutions

---

*Cross-Reference Index v2.0 (Post-Quality Improvement) | Financial Consolidation Documentation Library | 52 Documents | 2025-12-04*
