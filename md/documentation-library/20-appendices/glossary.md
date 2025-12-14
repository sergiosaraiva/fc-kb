# Glossary of Terms

## Document Metadata
- **Document Type**: Reference Glossary
- **Purpose**: Standardize terminology across documentation
- **Total Terms**: 75+
- **Categories**: 10
- **Last Updated**: 2024-12-02
- **Version**: 1.0

---

## Quick Navigation

| Category | Jump To |
|----------|---------|
| [Consolidation Methods](#1-consolidation-methods) | G, E, P, N methods |
| [Ownership & Percentages](#2-ownership--percentages) | Financial %, Control %, Group % |
| [Elimination Types](#3-elimination-types) | S-codes, U-codes |
| [Currency Translation](#4-currency-translation) | Rate types, CTA |
| [Ownership Structures](#5-ownership-structures) | Multi-tier, Circular |
| [Accounting Concepts](#6-accounting-concepts) | Goodwill, NCI, Fair value |
| [Database Objects](#7-database-objects) | Tables, procedures |
| [Flow Codes](#8-flow-codes) | Special flows |
| [IFRS Standards](#9-ifrs-standards) | Applicable standards |
| [System Terminology](#10-system-terminology) | POV, Bundle, Period |

---

## 1. Consolidation Methods

| Term | Definition | Code | System Reference |
|------|------------|------|------------------|
| **Global Integration** | Full consolidation method for subsidiaries under control (>50%). 100% of assets/liabilities consolidated with NCI recognized separately. | G | TS014C0.ConsoMethod = 'G' |
| **Equity Method** | One-line consolidation for associates with significant influence (20-50%). Investment adjusted for share of profits/losses. | E | TS014C0.ConsoMethod = 'E' |
| **Proportional Integration** | Share-based consolidation for joint ventures (50% joint control). Include proportionate share of each line item. | P | TS014C0.ConsoMethod = 'P' |
| **Not Consolidated** | Entities below significance threshold (<20%) held at cost or fair value. | N | TS014C0.ConsoMethod = 'N' |
| **Scope Entity** | Placeholder for entities temporarily in/out of scope. | S | TS014C0.ConsoMethod = 'S' |
| **Transferred Entity** | Entity transferred within group during period. | T | TS014C0.ConsoMethod = 'T' |
| **Excluded Entity** | Explicitly excluded from consolidation. | X | TS014C0.ConsoMethod = 'X' |

**Related Documentation**: [Global Integration](../02-consolidation-methods/global-integration.md), [Equity Method](../02-consolidation-methods/equity-method.md), [Proportional Method](../02-consolidation-methods/proportional-method.md)

---

## 2. Ownership & Percentages

| Term | Definition | Calculation | System Reference |
|------|------------|-------------|------------------|
| **Financial Percentage (FinPerc)** | Share of economic benefits (dividends, profits). Based on capital shares owned. | Shares owned / Total shares | TS015S0.FinPercentage |
| **Control Percentage (CtrlPerc)** | Share of voting rights/decision power. May differ from financial % due to preference shares. | Voting rights / Total votes | TS015S0.CtrlPercentage |
| **Direct Percentage** | Ownership held directly by immediate parent without intermediate entities. | Direct shares / Total shares | TS014C0.DirectFinPerc |
| **Indirect Percentage** | Ownership held through intermediate subsidiaries in the ownership chain. | Sum of path products | Calculated by P_CALC_OWNERSHIP_INDIRECT_PERCENTAGES |
| **Group Percentage** | Total effective ownership by the group (direct + indirect). | Direct % + Indirect % | TS014C0.GroupFinPerc |
| **Integration Percentage** | Percentage used for proportional integration calculations. | Usually = FinPerc for P method | TS014C0.IntegPerc |
| **Minority Percentage** | Portion owned by third parties outside the group. | 100% - Group % | Calculated |

**Related Documentation**: [Ownership Percentages](../06-ownership-structure/ownership-percentages.md), [Direct-Indirect Holdings](../06-ownership-structure/direct-indirect-holdings.md)

---

## 3. Elimination Types

### System Eliminations (S-codes)

| Code | Term | Description | Procedure |
|------|------|-------------|-----------|
| **S001** | Opening Balance | Carry forward prior period closing to current opening | P_CONSO_ELIM_OPENING_BALANCE |
| **S010** | Equity Capital | Elimination of subsidiary equity against parent investment | P_CONSO_ELIM_EQUITYCAPITAL |
| **S020** | Dividend Elimination | Eliminate intercompany dividends (4-line journal) | P_CONSO_ELIM_DIVIDEND |
| **S030** | Intercompany Netting | Eliminate IC receivables/payables and revenue/expense | P_CONSO_ELIM_INTERCOMPANY_NETTING |
| **S040** | Equity Method Adjustment | One-line consolidation adjustments for associates | P_CONSO_ELIM_EQUITYMETHOD |
| **S050-S054** | Participation Eliminations | Investment elimination against subsidiary equity (5 steps) | P_CONSO_ELIM_PARTICIPATIONS0-4 |
| **S060** | Proportional Adjustment | Adjustments for proportional integration | P_CONSO_ELIM_PROPORTIONAL |
| **S072** | Method Change | Flow reclassification when consolidation method changes | P_CONSO_ELIM_CHANGE_METHOD |
| **S085** | Minority Interest | Recognition of non-controlling interest in equity and P&L | P_CONSO_ELIM_MINORITYINTEREST |

### User Eliminations (U-codes)

| Code | Term | Description |
|------|------|-------------|
| **U###** | User-Defined Elimination | Custom elimination configured via TS070S0/TS071S0 |
| **U001-U099** | Standard User Elims | Typically used for recurring adjustments |
| **U100+** | Special User Elims | Project-specific or one-time adjustments |

**Related Documentation**: [Journal Types](../07-database-implementation/journal-types.md), [User Eliminations](../04-elimination-entries/user-eliminations.md)

---

## 4. Currency Translation

### Rate Types

| Code | Term | Description | Typical Use |
|------|------|-------------|-------------|
| **CC** | Closing Rate Current | Exchange rate at balance sheet date for current period | B/S monetary items |
| **AC** | Average Rate Current | Average exchange rate for current period | P&L items |
| **MC** | Monthly Cumulative | Cumulative monthly rate for progressive translation | P&L monthly buildup |
| **CR** | Closing Rate Reference | Closing rate from prior/reference period | Prior period comparison |
| **AR** | Average Rate Reference | Average rate from prior/reference period | Prior period P&L |
| **MR** | Monthly Reference | Monthly rate from prior period | Prior monthly comparison |
| **NR** | No Rate | No translation applied | Same-currency entities |

### Translation Concepts

| Term | Definition | System Reference |
|------|------------|------------------|
| **CTA** | Cumulative Translation Adjustment. Equity reserve capturing FX differences from translating foreign subsidiaries. | TRANSADJ flow |
| **TRANSADJ** | Special flow code for translation adjustment entries. | TS011C1.SpecFlowCode |
| **Historical Rate** | Rate at original transaction/acquisition date, used for non-monetary items and equity. | FlagHistoricalRate1/2 |
| **Closing Rate Method** | Translate all B/S at closing, P&L at average, with CTA in equity. | ConversionMethod = 1 |
| **Temporal Method** | Translate monetary items at closing, non-monetary at historical rates. | ConversionMethod = 2 |
| **Functional Currency** | Primary currency of entity's economic environment. | TS014C0.CurrCode |
| **Group Currency** | Presentation currency of consolidated statements. | TS000S0 configuration |
| **T075** | Journal type for historical rate adjustment entries. | TS020S0.JournalTypeCode |

**Related Documentation**: [Exchange Rate Types](../05-currency-translation/exchange-rate-types.md), [Translation Methods](../05-currency-translation/translation-methods.md), [Translation Adjustments](../05-currency-translation/translation-adjustments.md)

---

## 5. Ownership Structures

| Term | Definition | Example |
|------|------------|---------|
| **Multi-tier Holdings** | Ownership through multiple intermediate entities. P→A→B means P owns A which owns B. | P (80%) → A (60%) → B gives P 48% indirect in B |
| **Direct Holdings** | Immediate parent-subsidiary ownership without intermediaries. | P directly owns 80% of A |
| **Indirect Holdings** | Ownership through intermediate subsidiaries. | P owns B through A |
| **Circular Ownership** | Cross-shareholdings creating ownership loops (A owns B, B owns A). Requires matrix algebra to solve. | A (20%) → B (15%) → A |
| **Cross-Holdings** | Reciprocal shareholdings between group entities. | Subsidiary owns shares in parent |
| **Treasury Shares** | Company's own shares held by itself or subsidiaries. Reduces effective outstanding shares. | A holds 10% of A's shares |
| **Parent Company** | Ultimate controlling entity at top of ownership chain. | TS014C0.FlagParent = 1 |
| **Subsidiary** | Entity controlled by parent (>50% voting rights). | ConsoMethod = 'G' |
| **Associate** | Entity with significant influence but not control (20-50%). | ConsoMethod = 'E' |
| **Joint Venture** | Entity with shared control (50% joint control). | ConsoMethod = 'P' |

**Related Documentation**: [Multi-tier Holdings](../06-ownership-structure/multi-tier-holdings.md), [Circular Ownership](../03-core-calculations/circular-ownership.md)

---

## 6. Accounting Concepts

### Goodwill & Acquisition

| Term | Definition | Calculation |
|------|------------|-------------|
| **Goodwill** | Excess of consideration paid over fair value of net identifiable assets acquired. | Consideration + NCI - FV Net Assets |
| **Bargain Purchase** | Negative goodwill when consideration is less than FV of net assets (IFRS 3.34). | Recognized in P&L immediately |
| **Consideration Transferred** | Cash, shares, or other assets given to acquire subsidiary. | Purchase price |
| **Fair Value Adjustment** | Revaluation of subsidiary assets/liabilities to FV at acquisition date. | FV - Book Value |
| **Purchase Price Allocation (PPA)** | Process of allocating consideration to identifiable assets and liabilities. | Required by IFRS 3 |
| **Acquisition Date** | Date when control is obtained over the subsidiary. | Used for goodwill calculation |

### Non-Controlling Interest (NCI)

| Term | Definition | Also Known As |
|------|------------|---------------|
| **NCI** | Non-Controlling Interest. Equity in subsidiary not attributable to parent. | Minority Interest (MI) |
| **Minority Interest** | Legacy term for NCI. Portion owned by third parties. | NCI (current term) |
| **NCI at Fair Value** | IFRS 3 option to measure NCI at FV (full goodwill method). | Option A |
| **NCI at Proportionate Share** | IFRS 3 option to measure NCI at share of net assets (partial goodwill). | Option B |

### Other Concepts

| Term | Definition |
|------|------------|
| **Control** | Power to govern financial and operating policies. Typically >50% voting rights. |
| **Significant Influence** | Power to participate in decisions without control. Typically 20-50%. |
| **Joint Control** | Contractually agreed sharing of control. Requires unanimous consent. |
| **De Facto Control** | Control without majority ownership due to dispersed shareholders. |
| **Potential Voting Rights** | Options, warrants, convertibles that could provide voting rights if exercised. |
| **Impairment** | Reduction in recoverable amount below carrying value. |
| **CGU** | Cash Generating Unit. Smallest group of assets generating independent cash flows. |
| **VIU** | Value in Use. Present value of future cash flows from an asset. |

**Related Documentation**: [Goodwill Calculation](../03-core-calculations/goodwill-calculation.md), [Minority Interest](../03-core-calculations/minority-interest.md)

---

## 7. Database Objects

### Key Tables

| Table | Description | Category |
|-------|-------------|----------|
| **TS014C0** | Company master with calculated percentages and consolidation method | Setup |
| **TS015S0** | Direct ownership links between companies | Setup |
| **TS010S0** | Account master with rate types and special account flags | Setup |
| **TS011C0** | Flow definitions for movement analysis | Setup |
| **TS011C1** | Special flow codes (VarConsoMeth, TRANSADJ, etc.) | Setup |
| **TS017R0** | Exchange rates by currency, period, and rate type | Setup |
| **TS020S0** | Journal type definitions (S-codes, U-codes) | Setup |
| **TS070S0** | User elimination headers | Setup |
| **TS071S0** | User elimination detail lines | Setup |
| **TD030B2** | Local data input (bundles) | Data |
| **TD040B2** | Intercompany data input | Data |
| **TD035C2** | Consolidated data (main fact table) | Data |
| **TD045C2** | Elimination journals | Data |
| **TMP_*** | Temporary tables for session processing | Temp |

### Key Procedures

| Procedure | Description |
|-----------|-------------|
| **P_CONSO_CALCULATE_BUNDLE_INTEGRATION** | Main consolidation orchestrator |
| **P_CALC_OWNERSHIP_INDIRECT_PERCENTAGES** | Calculate group percentages via matrix algebra |
| **P_CONSO_ELIM** | Elimination execution engine |
| **P_CONSO_ELIM_USER** | User-defined elimination processor |
| **P_REPORT_*** | Report generation procedures (179+) |
| **P_SYS_IMPORT_*** | Data import procedures (64+) |

**Related Documentation**: [Stored Procedures Catalog](../07-database-implementation/stored-procedures-catalog.md), [Data Tables Catalog](../07-database-implementation/data-tables-catalog.md)

---

## 8. Flow Codes

### Standard Flows

| Flow | Description |
|------|-------------|
| **OPEN** | Opening balance |
| **CLOSE** | Closing balance |
| **NET** | Net movement (CLOSE - OPEN) |
| **MVTC** | Current period movements |

### Special Flows

| Flow Code | Description | Use Case |
|-----------|-------------|----------|
| **TRANSADJ** | Translation adjustment | CTA calculation |
| **VarPercInteg** | Variation in integration percentage | Ownership changes |
| **VarConsoMeth_EG** | Method change E→G | Step acquisition |
| **VarConsoMeth_GE** | Method change G→E | Deconsolidation |
| **VarConsoMeth_PG** | Method change P→G | JV to subsidiary |
| **VarConsoMeth_GP** | Method change G→P | Lose exclusive control |
| **VarConsoMeth_EP** | Method change E→P | Associate gains JC |
| **VarConsoMeth_PE** | Method change P→E | JV loses JC |
| **UnexpVar** | Unexplained variance | Data quality flag |

**Related Documentation**: [Flow Management](../03-core-calculations/flow-management.md)

---

## 9. IFRS Standards

| Standard | Title | Relevance |
|----------|-------|-----------|
| **IFRS 3** | Business Combinations | Goodwill calculation, acquisition accounting |
| **IFRS 10** | Consolidated Financial Statements | Control definition, full consolidation |
| **IFRS 11** | Joint Arrangements | Joint ventures vs joint operations |
| **IFRS 12** | Disclosure of Interests | Required disclosures |
| **IAS 12** | Income Taxes | Deferred tax on consolidation adjustments |
| **IAS 21** | Effects of Changes in Foreign Exchange Rates | Currency translation |
| **IAS 27** | Separate Financial Statements | Parent-only statements |
| **IAS 28** | Investments in Associates and Joint Ventures | Equity method |
| **IAS 29** | Financial Reporting in Hyperinflationary Economies | Hyperinflation accounting |
| **IAS 36** | Impairment of Assets | Goodwill impairment testing |

**Related Documentation**: [Cross-Reference Index - IFRS Standards](../00-index/CROSS_REFERENCE_INDEX.md#cross-reference-by-ifrs-standard)

---

## 10. System Terminology

### Core Concepts

| Term | Definition |
|------|------------|
| **POV** | Point of View. Context for viewing data (ConsoID, Period, Company). |
| **ConsoID** | Consolidation identifier. Primary key for multi-tenant data isolation. |
| **Bundle** | Data package for a company/period. Unit of data entry. |
| **Period** | Fiscal period identifier (e.g., 202412 for December 2024). |
| **SessionID** | Temporary session identifier for processing isolation. |

### Processing Terms

| Term | Definition |
|------|------------|
| **Integration** | Process of combining company data with eliminations. |
| **Translation** | Currency conversion from local to group currency. |
| **Elimination** | Adjustments to remove intercompany items and recognize ownership. |
| **Validation** | Data quality checks before/after processing. |
| **Rollup** | Aggregation of subsidiary data to parent level. |

### Status & Flags

| Term | Definition | Values |
|------|------------|--------|
| **ConsoStatus** | Consolidation calculation status | 0=Not run, 1=Calculated |
| **FlagLocked** | Period lock status | 0=Open, 1=Locked |
| **FlagParent** | Indicates parent company | 0=No, 1=Yes |
| **FlagEnteringScope** | Company entering consolidation scope | 0=No, 1=Yes |
| **FlagLeavingScope** | Company leaving consolidation scope | 0=No, 1=Yes |
| **FlagInterCompany** | Account is intercompany type | 0=No, 1=Yes |
| **FlagEquity** | Account is equity type | 0=No, 1=Yes |
| **FlagPL** | Account is P&L type | 0=No, 1=Yes |

---

## Alphabetical Index

| Term | Section | Category |
|------|---------|----------|
| AC (Average Current) | [4](#4-currency-translation) | Currency |
| Acquisition Date | [6](#6-accounting-concepts) | Accounting |
| Associate | [5](#5-ownership-structures) | Structures |
| Bargain Purchase | [6](#6-accounting-concepts) | Accounting |
| Bundle | [10](#10-system-terminology) | System |
| CC (Closing Current) | [4](#4-currency-translation) | Currency |
| CGU | [6](#6-accounting-concepts) | Accounting |
| Circular Ownership | [5](#5-ownership-structures) | Structures |
| ConsoID | [10](#10-system-terminology) | System |
| Consideration Transferred | [6](#6-accounting-concepts) | Accounting |
| Control | [6](#6-accounting-concepts) | Accounting |
| Control Percentage | [2](#2-ownership--percentages) | Percentages |
| Cross-Holdings | [5](#5-ownership-structures) | Structures |
| CTA | [4](#4-currency-translation) | Currency |
| De Facto Control | [6](#6-accounting-concepts) | Accounting |
| Direct Holdings | [5](#5-ownership-structures) | Structures |
| Direct Percentage | [2](#2-ownership--percentages) | Percentages |
| Equity Method | [1](#1-consolidation-methods) | Methods |
| Fair Value Adjustment | [6](#6-accounting-concepts) | Accounting |
| Financial Percentage | [2](#2-ownership--percentages) | Percentages |
| Functional Currency | [4](#4-currency-translation) | Currency |
| Global Integration | [1](#1-consolidation-methods) | Methods |
| Goodwill | [6](#6-accounting-concepts) | Accounting |
| Group Currency | [4](#4-currency-translation) | Currency |
| Group Percentage | [2](#2-ownership--percentages) | Percentages |
| Historical Rate | [4](#4-currency-translation) | Currency |
| Impairment | [6](#6-accounting-concepts) | Accounting |
| Indirect Holdings | [5](#5-ownership-structures) | Structures |
| Indirect Percentage | [2](#2-ownership--percentages) | Percentages |
| Integration | [10](#10-system-terminology) | System |
| Integration Percentage | [2](#2-ownership--percentages) | Percentages |
| Joint Control | [6](#6-accounting-concepts) | Accounting |
| Joint Venture | [5](#5-ownership-structures) | Structures |
| Minority Interest | [6](#6-accounting-concepts) | Accounting |
| Minority Percentage | [2](#2-ownership--percentages) | Percentages |
| Multi-tier Holdings | [5](#5-ownership-structures) | Structures |
| NCI | [6](#6-accounting-concepts) | Accounting |
| Not Consolidated | [1](#1-consolidation-methods) | Methods |
| Parent Company | [5](#5-ownership-structures) | Structures |
| Period | [10](#10-system-terminology) | System |
| Potential Voting Rights | [6](#6-accounting-concepts) | Accounting |
| POV | [10](#10-system-terminology) | System |
| PPA | [6](#6-accounting-concepts) | Accounting |
| Proportional Integration | [1](#1-consolidation-methods) | Methods |
| S020 | [3](#3-elimination-types) | Eliminations |
| S085 | [3](#3-elimination-types) | Eliminations |
| SessionID | [10](#10-system-terminology) | System |
| Significant Influence | [6](#6-accounting-concepts) | Accounting |
| Subsidiary | [5](#5-ownership-structures) | Structures |
| Temporal Method | [4](#4-currency-translation) | Currency |
| TRANSADJ | [4](#4-currency-translation) | Currency |
| Treasury Shares | [5](#5-ownership-structures) | Structures |
| U### | [3](#3-elimination-types) | Eliminations |
| VarConsoMeth | [8](#8-flow-codes) | Flows |
| VIU | [6](#6-accounting-concepts) | Accounting |

---

## See Also

### Related Documentation
- [Cross-Reference Index](../00-index/CROSS_REFERENCE_INDEX.md) - Navigate by topic
- [Executive Summary](../00-index/EXECUTIVE_SUMMARY.md) - System overview
- [Troubleshooting Guide](../17-troubleshooting/common-issues.md) - Issue resolution

### Technical References
- [Stored Procedures Catalog](../07-database-implementation/stored-procedures-catalog.md)
- [Data Tables Catalog](../07-database-implementation/data-tables-catalog.md)
- [Journal Types](../07-database-implementation/journal-types.md)

---

*Glossary v1.1 (Final) | Financial Consolidation Documentation Library | 75+ Terms | 2024-12-02*
