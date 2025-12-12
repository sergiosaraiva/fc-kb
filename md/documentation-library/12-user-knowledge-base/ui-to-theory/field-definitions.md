# Field Definitions: UI Labels to Theory Concepts

## Overview

This document maps every significant field label in Prophix.Conso to its underlying consolidation theory concept. Use this when users ask "What does this field mean?" or when translating between UI terminology and theoretical concepts.

---

## Quick Reference by Screen

### Group > Companies

| Field Label | Theory Concept | Description | IFRS Reference |
|-------------|---------------|-------------|----------------|
| **Company Code** | Entity Identifier | Unique code for legal entity | - |
| **Company Name** | Entity Name | Legal or trading name | - |
| **Currency** | Functional Currency | Primary currency of operations | IAS 21.9 |
| **Country** | Jurisdiction | Legal registration country | - |
| **Consolidation Method** | Method of Consolidation | G/P/E/N classification | IFRS 10, IAS 28 |
| **Group Percentage** | Effective Ownership % | Indirect ownership through chain | IFRS 10.B86 |
| **Minority Percentage** | Non-Controlling Interest % | 100% minus Group % | IFRS 10.22 |
| **Group Control Percentage** | Effective Voting/Control % | Power to direct relevant activities | IFRS 10.10 |
| **Number of Decimals** | Reporting Precision | Decimal places for amounts | - |

### Group > Group Structure

| Field Label | Theory Concept | Description | IFRS Reference |
|-------------|---------------|-------------|----------------|
| **Financial Rights** | Ownership Interest | Economic interest (dividend/liquidation rights) | IFRS 10.B89 |
| **Voting Rights** | Voting Power | Decision-making power | IFRS 10.B34 |
| **Financial Rights Issued** | Total Shares Outstanding | Denominator for ownership % | - |
| **Voting Rights Issued** | Total Voting Shares | Denominator for control % | - |
| **Direct %** | Direct Holding | Parent's direct ownership in subsidiary | - |
| **Indirect %** | Indirect Holding | Ownership through intermediate entities | IFRS 10.B86 |

### Group > Exchange Rates

| Field Label | Theory Concept | Description | IFRS Reference |
|-------------|---------------|-------------|----------------|
| **Close (CC)** | Closing Rate | Spot rate at balance sheet date | IAS 21.8 |
| **Average (AC)** | Average Rate | Average rate for period (P&L items) | IAS 21.40 |
| **Month (MC)** | Monthly/Manual Rate | Override rate for specific needs | - |
| **Historical (HC)** | Historical Rate | Rate at transaction/acquisition date | IAS 21.39(b) |
| **Reference Currency** | Presentation Currency | Group reporting currency | IAS 21.8 |

### Group > Scope

| Field Label | Theory Concept | Description | IFRS Reference |
|-------------|---------------|-------------|----------------|
| **In Scope** | Consolidation Perimeter | Entities included in consolidation | IFRS 10.4 |
| **Entry Date** | Acquisition Date | Date control obtained | IFRS 3.8 |
| **Exit Date** | Disposal Date | Date control lost | IFRS 10.25 |
| **Method** | Consolidation Method | How entity is consolidated | IFRS 10/IAS 28 |

---

## Data Entry Fields

### Data Entry > Bundles

| Field Label | Theory Concept | Description | IFRS Reference |
|-------------|---------------|-------------|----------------|
| **Account** | Chart of Accounts | Group standardized account | - |
| **Opening Balance** | Prior Period Closing | Brought forward amount | - |
| **Movement** | Period Activity | Changes during period | - |
| **Closing Balance** | Period End Balance | Opening + Movement | - |
| **Local Currency** | Functional Currency Amount | Amount in entity's currency | IAS 21.9 |
| **Group Currency** | Presentation Currency Amount | Translated to group currency | IAS 21.8 |
| **Flow** | Cash Flow Classification | C (Cash) or NC (Non-Cash) | IAS 7 |

### Data Entry > Intercompany

| Field Label | Theory Concept | Description | IFRS Reference |
|-------------|---------------|-------------|----------------|
| **Partner Company** | Counterparty | Other group entity in IC transaction | - |
| **IC Account** | Intercompany Account | Account designated for IC | - |
| **IC Amount** | Intercompany Balance | Amount to be eliminated | IFRS 10.B86(c) |
| **Rule** | IC Elimination Rule | How IC is processed | - |

### Data Entry > Local Adjustments

| Field Label | Theory Concept | Description | IFRS Reference |
|-------------|---------------|-------------|----------------|
| **Adjustment Type** | Pre-Consolidation Adjustment | Local correction before consolidation | - |
| **Debit Account** | Dr Entry | Account being debited | - |
| **Credit Account** | Cr Entry | Account being credited | - |
| **Journal Code** | Adjustment Reference | Identifier for adjustment | - |

---

## Consolidation Fields

### Consolidation > Statusboard

| Field Label | Theory Concept | Description | IFRS Reference |
|-------------|---------------|-------------|----------------|
| **Bundle** | Local Data Status | ✓ = Local data changed, needs processing | - |
| **Adjustments** | Adjustment Status | ✓ = Adjustments changed, needs processing | - |
| **Conso** | Consolidation Status | ✓ = Either changed, needs full reprocessing | - |
| **Include Dimensions** | Dimensional Analysis | Include analytical dimensions in T-journals | - |

### Consolidation > Intercompany Matching

| Field Label | Theory Concept | Description | IFRS Reference |
|-------------|---------------|-------------|----------------|
| **Threshold** | Materiality Tolerance | Difference ignored below this amount | - |
| **Unmatched** | IC Difference | Transactions not reconciled | - |
| **Matched** | IC Reconciled | Transactions successfully matched | - |
| **Rule** | IC Elimination Rule | Determines elimination treatment | - |
| **Transfer Difference** | Reclassification | Move difference in/out of group | - |
| **Reclassify Difference** | Translation Reclassification | Reclassify P&L IC difference | - |
| **Book Difference** | Booking Adjustment | Book BS IC difference | - |

### Consolidation > Events

| Field Label | Theory Concept | Description | IFRS Reference |
|-------------|---------------|-------------|----------------|
| **Event Code** | Consolidation Event | Type of scope change or adjustment | IFRS 3, IFRS 10 |
| **Event Type** | Transaction Type | Acquisition, disposal, restructure | - |
| **Generate** | Create Journal | Produce elimination/adjustment entry | - |

### Consolidation > Eliminations

| Field Label | Theory Concept | Description | IFRS Reference |
|-------------|---------------|-------------|----------------|
| **S-Code** | System Elimination Code | Pre-defined elimination type (S001-S094) | - |
| **U-Code** | User Elimination Code | Custom elimination type (U###) | - |
| **Elimination Type** | Elimination Category | Participation, IC, Dividend, etc. | - |
| **Active** | Elimination Status | Whether elimination is enabled | - |

---

## Adjustment Fields

### Adjustments > Journal Entry

| Field Label | Theory Concept | Description | IFRS Reference |
|-------------|---------------|-------------|----------------|
| **Journal Type** | Adjustment Category | L=Local, G=Group, E=Elimination, R=Restatement | - |
| **Entry Number** | Journal Reference | Unique identifier for entry | - |
| **Company** | Entity | Company affected by adjustment | - |
| **Partner** | Counterparty | For IC adjustments, the other party | - |
| **Account** | GL Account | Account being adjusted | - |
| **Debit** | Dr Amount | Debit entry amount | - |
| **Credit** | Cr Amount | Credit entry amount | - |
| **Description** | Narrative | Explanation of adjustment | - |
| **Posted** | Status | Whether journal is posted | - |

### Journal Types Explained

| Code | Name | Theory Concept | Use Case |
|------|------|---------------|----------|
| **L** | Local Adjustment | Pre-consolidation correction | Align local GAAP to group GAAP |
| **G** | Group Adjustment | Consolidation adjustment | Fair value adjustments, policy alignment |
| **E** | Elimination | Elimination entry | IC eliminations, participation |
| **R** | Restatement | Prior period adjustment | Error correction, policy change |
| **T** | T-Journal | System-generated | Automatic consolidation entries |

---

## Configuration Fields

### Configuration > Accounts

| Field Label | Theory Concept | Description | IFRS Reference |
|-------------|---------------|-------------|----------------|
| **Account Code** | GL Account Number | Unique account identifier | - |
| **Account Name** | Account Description | Account label | - |
| **Account Type** | Classification | BS or P&L classification | IAS 1 |
| **Currency Rate** | Translation Rate Type | CC, AC, MC, or HC | IAS 21 |
| **IC Account** | Intercompany Flag | Designated for IC transactions | - |
| **Flow Type** | Cash Flow Classification | Cash or Non-Cash | IAS 7 |
| **Dimension** | Analytical Axis | Additional analysis dimension | - |

### Configuration > Eliminations

| Field Label | Theory Concept | Description | IFRS Reference |
|-------------|---------------|-------------|----------------|
| **Elimination Code** | S-code or U-code | Unique elimination identifier | - |
| **Description** | Elimination Name | What elimination does | - |
| **Journal Type** | Output Journal | Type of journal created | - |
| **Sequence** | Execution Order | Order of processing | - |
| **Active** | Enabled | Whether elimination runs | - |
| **Account Mapping** | Dr/Cr Accounts | Accounts affected by elimination | - |

---

## Report Fields

### Reports > Standard Reports

| Field Label | Theory Concept | Description | IFRS Reference |
|-------------|---------------|-------------|----------------|
| **Report Type** | Financial Statement | BS, P&L, Cash Flow, Equity | IAS 1 |
| **Company Selection** | Scope | Entities in report | - |
| **Period** | Reporting Date | Current and/or reference period | - |
| **Currency** | Presentation Currency | Currency for display | IAS 21.38 |
| **Comparison** | Comparative Information | Prior period comparison | IAS 1.38 |

### Reports > Consolidation Reports

| Field Label | Theory Concept | Description | IFRS Reference |
|-------------|---------------|-------------|----------------|
| **Elimination Detail** | Elimination Analysis | Breakdown of eliminations | - |
| **Adjustment Detail** | Adjustment Analysis | Breakdown of adjustments | - |
| **T-Journal** | Consolidation Journal | System-generated entries | - |
| **Company Contribution** | Subsidiary Analysis | Each entity's contribution | - |

---

## Period Fields

### Period Selection

| Field Label | Theory Concept | Description | IFRS Reference |
|-------------|---------------|-------------|----------------|
| **Current Period** | Reporting Period | Primary period for consolidation | - |
| **Reference Period** | Comparative Period | Prior period for comparison | IAS 1.38 |
| **Period Code** | Period Identifier | Format: YYYYMMCCCVVV | - |
| **Category** | Period Nature | ACT=Actual, BUD=Budget, FCT=Forecast | - |
| **Version** | Period Version | 000=Original, 001+=Revisions | - |
| **Locked** | Period Status | Red=Locked, Black=Open | - |

### Period Code Format

```
202312ACT001
│  │  │  │
│  │  │  └── Version (001)
│  │  └───── Category (ACT=Actual)
│  └──────── Month (12)
└─────────── Year (2023)
```

---

## Glossary Quick Reference

| UI Term | Theory Term | Definition |
|---------|-------------|------------|
| Bundle | Local Package | Subsidiary's financial data package |
| Conso | Consolidation | The consolidation process |
| IC | Intercompany | Between group entities |
| T-Journal | Consolidation Journal | System-generated elimination entries |
| S-Code | System Elimination | Pre-defined elimination (S001-S094) |
| U-Code | User Elimination | Custom elimination (U###) |
| Flow | Cash Flow Movement | Balance sheet movement classification |
| MI/NCI | Minority/Non-Controlling Interest | Ownership not held by parent |
| CTA | Currency Translation Adjustment | FX translation difference |
| PPA | Purchase Price Allocation | Fair value allocation on acquisition |

---

## Related Documentation

- [Screen Glossary](screen-glossary.md) - Screen-level explanations
- [Workflow-Theory Map](workflow-theory-map.md) - Process mapping
- [Theory vs Product Overview](../discrepancy-mapping/theory-vs-product-overview.md)
- [Help Index](../help-index.md) - User documentation

---

*Field Definitions | Version 1.0 | Last Updated: 2024-12-03*
