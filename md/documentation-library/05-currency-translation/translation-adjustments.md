# Translation Adjustments (CTA) in Currency Translation

## Document Metadata
- **Category**: Currency Translation
- **Theory Source**: Knowledge base chunks: 0236, 0237, 0238, 0240, 0241, 0243, 0244, 0245, 0246
- **Implementation Files**:
  - `Sigma.Database/dbo/Stored Procedures/P_CONSO_BUNDLE_INTEGRATION_CURRENCY_TRANSLATION_CLOSING.sql`
  - `Sigma.Database/dbo/Stored Procedures/P_CONSO_BUNDLE_INTEGRATION_CURRENCY_TRANSLATION_FLOWS.sql`
  - `Sigma.Database/dbo/Stored Procedures/P_CONSO_BUNDLE_INTEGRATION_CURRENCY_TRANSLATION_HISTORICAL.sql`
  - `Sigma.Database/dbo/Stored Procedures/P_REPORT_TRANSLATION_ADJUSTMENTS_ANALYSIS.sql`
- **Last Updated**: 2024-12-01
- **Completeness**: 95% (Full CTA calculation and reporting implemented)
- **Compliance Status**: IAS 21 - Other Comprehensive Income (OCI) presentation

## Executive Summary

Translation Adjustments (also known as Cumulative Translation Adjustment or CTA) represent the difference arising from translating foreign subsidiary accounts at different exchange rates for different account types. In Prophix.Conso, translation adjustments are managed through special accounts (TDBS, TDPL), special flows (TRANSADJ, UNEXPVAR), and journal types (T075, S001) to maintain balance sheet equilibrium after translation.

## Theoretical Framework

### Concept Definition

From Allen White's "Direct Consolidation" (Chunk 237):

> "By considering this column, we have to admit that a problem appears in the accounts because the profit in the P&L (630) is no longer the same as the profit in the equity (600). The correct value is the one corresponding to a translation at the average rate. That's the reason why we have to book in column (2) a consolidation adjustment transferring 30 (debit) from an account named 'Translation adjustments' to the profit (credit)."

### Origin of Translation Adjustments

Translation adjustments arise from the inconsistency created when:
1. **Balance sheet accounts** are translated at **closing rate** (period-end)
2. **P&L accounts** are translated at **average rate** (period average)
3. **Equity accounts** require **historical rates** (to maintain reserves integrity)

This creates a balancing discrepancy that must be recorded as a Translation Adjustment.

### Key Principles

From Chunk 238:

> "In consolidation, there is an important principle to consider. When we book an adjustment impacting the result one year, we must find this adjustment impacting the reserves next year. Moreover, if a consolidation adjustment impacts the reserves one year, we must find the same amount on the same reserves account next year."

From Chunk 240:

> "The consolidated reserves of A are 6104 = 80% * [7000 + 0 + 630] - 4000 and you can notice that the translation adjustments of (30) are not included in the formula. Indeed, we have made a special effort to 'clean' the reserves with the undesirable effect of currency rates."

### Formula/Algorithm

**Translation Adjustment Calculation**:
```
Translation Adjustment =
  Closing Rate Value (Assets - Liabilities)
  - Average Rate Value (Income - Expenses)
  - Historical Rate Value (Equity)
```

**Practical Formula from Year-Over-Year Analysis**:
```
Current Period CTA =
  (Current Closing Amount - Reference Closing Amount)
  - (Flow Amounts translated at flow rates)
  + Historical Rate Adjustments
```

### Detailed Example (Chunks 236-238)

**Year 1 Translation**:
```
Local Currency (CUR):
- Capital: 3,500 CUR
- Profit: 300 CUR
- Assets: 5,000 CUR
- Liabilities: 1,200 CUR

Rates:
- Closing Rate: 1 CUR = 2 EUR
- Average Rate: 1 CUR = 2.1 EUR

Translation Results:
- Assets at Closing: 5,000 x 2 = 10,000 EUR
- Liabilities at Closing: 1,200 x 2 = 2,400 EUR
- Capital at Closing: 3,500 x 2 = 7,000 EUR
- Profit at Closing: 300 x 2 = 600 EUR
- Profit at Average: 300 x 2.1 = 630 EUR

Translation Adjustment = 630 - 600 = 30 EUR (debit TDBS, credit Profit)
```

**Year 2 Translation (Chunk 237)**:
```
Year 2 Rates:
- Closing Rate: 1 CUR = 2.2 EUR
- Average Rate: 1 CUR = 2.5 EUR

Additional Adjustments Required:
1. Carry forward Year 1 adjustment to reserves: 30 EUR
2. Current year profit adjustment: 120 EUR
3. Reserves re-translation: 60 EUR
4. Capital re-translation: 700 EUR

Total Translation Adjustments: 610 EUR
```

## Current Implementation

### Special Accounts

| Code | Full Name | Purpose |
|------|-----------|---------|
| TDBS | Translation Difference Balance Sheet | Accumulates balance sheet translation differences |
| TDPL | Translation Difference P&L | Accumulates P&L translation differences |
| PLBAL | Profit/Loss Balance | Bridge account between P&L and Balance Sheet |

### Special Flows

| Code | Full Name | Purpose |
|------|-----------|---------|
| TRANSADJ | Translation Adjustment | Records flow-level translation differences |
| UNEXPVAR | Unexplained Variance | Captures residual translation differences |
| NETVAR | Net Variance | Used for FlowsType=2 accounts |
| PREVIOUSPERIODADJ | Previous Period Adjustment | Reference period reconciliation |

### Journal Types

| Code | Description | Usage |
|------|-------------|-------|
| B001 | Bundle Journal | Translated local bundle amounts |
| T075 | Translation Historical | Historical rate adjustment journals |
| S001 | System Translation | System-generated translation entries |

### Translation Process Overview

```
P_CONSO_BUNDLE_INTEGRATION_CURRENCY_TRANSLATION_CLOSING
│
├── Step 1: Translate B/S amounts at closing rate
├── Step 2: Translate P&L amounts at average rate
├── Step 3: Calculate NOTBALPL (P&L vs equity profit difference)
├── Step 4: Calculate PLBAL entries
├── Step 5: Calculate NOTBALBS (balance sheet equilibrium)
├── Step 6: Generate TDBS entries to maintain balance
└── Output: TD035C2, TD045C2 (translated amounts)

P_CONSO_BUNDLE_INTEGRATION_CURRENCY_TRANSLATION_FLOWS
│
├── Step 1: Copy local flows to temp table
├── Step 2: Convert flows at appropriate rates
├── Step 3: Calculate TRANSADJ flow differences
├── Step 4: Calculate UNEXPVAR for residual differences
└── Output: TD045C2 (translated flows with CTA)

P_CONSO_BUNDLE_INTEGRATION_CURRENCY_TRANSLATION_HISTORICAL
│
├── Step 1: Identify historical rate accounts
├── Step 2: Reverse closing rate translation
├── Step 3: Create T075 journal entries
├── Step 4: Book differences to TDBS
└── Output: TD033E0/E2, TD035C2, TD045C2 (historical adjustments)
```

### CTA Calculation Logic

From `P_CONSO_BUNDLE_INTEGRATION_CURRENCY_TRANSLATION_FLOWS.sql` (lines 580-700):

```sql
-- Translation difference calculation:
-- PLUS current conso closing amounts
-- MINUS reference conso closing amounts
-- MINUS current flows translated at flow rates
-- = Translation Adjustment (TRANSADJ or UNEXPVAR flow)

-- Step 1: Plus current period closing amounts (FlowsType = 1 or 2)
insert into dbo.TMP2_TD045C2 (...)
select @SessionID, a.CompanyID, b.JournalTypeID, a.JournalEntry,
       1 as JournalSequence, b.AccountID, b.PartnerCompanyID, b.CurrCode,
       @PREVIOUSPERIODADJFlowID, b.Amount, ...
from dbo.TMP_CONSO_COMPANYID a
     inner join dbo.TD035C2 b on (b.ConsoID = @ConsoID ...)
     inner join dbo.TS010S0 c on (c.FlowsType in (1,2) ...)

-- Step 2: Minus reference period closing amounts
insert into dbo.TMP2_TD045C2 (...)
select ... -1 * b.Amount, ...
from dbo.TMP_CONSO_COMPANYID a
     inner join dbo.TD035C2 b on (b.ConsoID = @RefConsoID ...)

-- Step 3: Minus current flows
insert into dbo.TMP2_TD045C2 (...)
select ... -1 * a.Amount, ...
from dbo.TMP_TD045C2 a
where a.JournalSequence in (1,2)

-- Step 4: Calculate translation difference
insert into dbo.TMP2_TD045C2 (...)
select @SessionID, a.CompanyID, @JournalTypeB001ID, b.JournalEntry,
       4 as JournalSequence, a.AccountID, a.PartnerCompanyID, @ConsoCurrCode,
       case
           when b.CurrCode <> @ConsoCurrCode then @TRANSADJFlowID
           when acc.FlowsType = 2 then @NETVARFlowID
           else @UNEXPVARFlowID
       end as FlowID,
       a.Amount, ...
from (select CompanyID, AccountID, PartnerCompanyID, sum(Amount) as Amount
      from dbo.TMP2_TD045C2 ...
      group by ... having sum(Amount) <> 0) a
```

### Historical Rate Adjustments

From `P_CONSO_BUNDLE_INTEGRATION_CURRENCY_TRANSLATION_HISTORICAL.sql` (lines 191-215):

```sql
-- Copy records from TD045C2 for historical rate accounts
-- Reverse the TRANSADJ amounts and rebook to TDBS

insert into dbo.TMP_TD045C2 (...)
select @SessionID, b.CompanyID, @ElimJournalTypeID, -- T075 journal
       a.JournalEntry,
       (1 + row_number() over (...)) as JournalSequence,
       b.AccountID, b.PartnerCompanyID, b.CurrCode,
       @TRANSADJFlowID,
       -1 * b.Amount,  -- Reverse the translation adjustment
       ...
from dbo.TMP_CONSO_COMPANYID a
     inner join dbo.TD045C2 b on (...)
     inner join dbo.TS010S0 c on (...)
where a.SessionID = @SessionID
      and b.JournalTypeID = @JournalTypeB001ID
      and b.FlowID = @TRANSADJFlowID
      and ((a.ConversionMethod = 1 and c.FlagHistoricalRate1 = 1)
           or (a.ConversionMethod = 2 and c.FlagHistoricalRate2 = 1))

-- Create offsetting entry on TDBS account
insert into dbo.TMP_TD045C2 (...)
select @SessionID, a.CompanyID, @ElimJournalTypeID, a.JournalEntry,
       1 as JournalSequence, @TDBSAccountID, null as PartnerCompanyID,
       @ConsoCurrCode, @TRANSADJFlowID,
       -1 * sum(a.Amount), ...
from dbo.TMP_TD045C2 a
where a.SessionID = @SessionID
group by a.CompanyID, a.JournalEntry
```

### Translation Adjustments Report

The `P_REPORT_TRANSLATION_ADJUSTMENTS_ANALYSIS.sql` provides comprehensive CTA analysis:

**Report Components**:
1. **Reference Period Local Amounts**: TD030B2 amounts at reference closing rate
2. **Current Period Local Amounts**: TD030B2 amounts at current closing rate
3. **Current Period Flows**: TD040B2 flows at flow rates
4. **Group Adjustment Data**: TD033E0/E2 adjustment journal amounts
5. **TDBS Reconciliation**: Amounts booked to Translation Difference account

**Report Output Fields**:
- ReferenceLocalAmount, ReferenceRate, ReferenceConsoAmount
- CurrentFlowAmount, FlowRate
- CurrentLocalAmount, CurrentRate, CurrentConsoAmount
- TranslationAdjustAmount
- TranslationInfo (1=Bundle, 2=Local Adj, 3=Conso Adj, 4=Minority Local, 5=Minority Conso)

### Group vs Minority Split

From Chunk 240:

> "The group part of the translation adjustments, 80% * (30) = (24) remains on a separate line in the consolidated equity. On the contrary, the calculation of minority interests will include these translation adjustments."

**Implementation**: The system tracks CTA separately for group and minority through:
- `MinorityFlag` column in TD035C2, TD045C2
- `TranslationInfo` levels in analysis report
- Separate Level2 groupings in P_REPORT_TRANSLATION_ADJUSTMENTS_ANALYSIS

## Theory vs Practice Analysis

| Aspect | Theory (Allen White) | Prophix.Conso Implementation | Alignment |
|--------|---------------------|------------------------------|-----------|
| CTA Account | Translation Adjustments in equity | TDBS special account | Full |
| P&L Bridge | PLBAL concept | PLBAL, TDPL accounts | Full |
| Flow Tracking | TRANSADJ flow for CTA | TRANSADJ, UNEXPVAR, NETVAR flows | Enhanced |
| Historical Adjustment | Per-account historical tracking | T075 journal type + FlagHistoricalRate | Full |
| Group/Minority Split | Group % * CTA separate | MinorityFlag separation | Full |
| Year-Over-Year | Carry forward mechanism | Reference period comparison | Full |
| Reporting | CTA analysis requirement | P_REPORT_TRANSLATION_ADJUSTMENTS_ANALYSIS | Full |

## Gap Analysis

### Missing Elements

1. **OCI Classification Detail**: While CTA is calculated correctly, explicit IAS 21 OCI reclassification on disposal is manual

### Divergent Implementation

1. **Historical Rate Storage**: System uses adjustment journals (T075) rather than storing individual historical rates - this is a valid implementation approach per Chunk 244

### Additional Features (Beyond Theory)

1. **Monthly Average CTA**: Supports progressive MC/MR rate translation for monthly accuracy
2. **Flow-Level CTA**: TRANSADJ flow provides detailed flow-level translation tracking
3. **Multi-Level Analysis**: TranslationInfo categorization for audit drill-down
4. **Participation-Specific CTA**: Separate tracking for participation (PartnerType=2) accounts

## Business Impact

1. **IAS 21 Compliance**: Proper recognition of translation differences in equity (OCI)
2. **Audit Trail**: Complete flow-by-flow analysis of translation differences
3. **Reserves Integrity**: Consolidated reserves calculation excludes CTA per theory
4. **Minority Interest Accuracy**: Proper allocation of CTA between group and minority

## Recommendations

1. **Disposal Reclassification**: Consider automating OCI-to-P&L reclassification on subsidiary disposal
2. **CTA Rollforward Report**: Add period-over-period CTA movement analysis
3. **Currency-by-Currency Analysis**: Add reporting breakdown by source currency

## API Reference

### Primary API Handlers
| Handler | YAML File | Purpose | Status |
|---------|-----------|---------|--------|
| `Consolidation_Execute` | [api-consolidation-endpoints.yaml](../11-agent-support/api-consolidation-endpoints.yaml) | Trigger CTA calculation | ✅ IMPLEMENTED |
| `Report_ExecuteReport` | [api-reports-endpoints.yaml](../11-agent-support/api-reports-endpoints.yaml) | P_REPORT_TRANSLATION_ADJUSTMENTS_ANALYSIS | ✅ IMPLEMENTED |

### Supporting API Handlers
| Handler | YAML File | Purpose |
|---------|-----------|---------|
| `Account_GetAccounts` | [api-account-endpoints.yaml](../11-agent-support/api-account-endpoints.yaml) | Get TDBS, TDPL special accounts |
| `Flow_GetFlows` | [api-flow-endpoints.yaml](../11-agent-support/api-flow-endpoints.yaml) | Get TRANSADJ, UNEXPVAR, NETVAR flows |
| `Journal_GetJournals` | [api-journal-endpoints.yaml](../11-agent-support/api-journal-endpoints.yaml) | Get T075 historical adjustment journals |

### Special Account/Flow Reference
| Type | Code | API Field | Purpose |
|------|------|-----------|---------|
| Account | TDBS | tdbsAccountId | Translation Difference (B/S) |
| Account | TDPL | tdplAccountId | Translation Difference (P&L) |
| Account | PLBAL | plbalAccountId | P&L to Balance bridge |
| Flow | TRANSADJ | transadjFlowId | CTA flow |
| Flow | UNEXPVAR | unexpvarFlowId | Residual differences |
| Flow | NETVAR | netvarFlowId | Net variance (FlowsType=2) |
| Journal | T075 | journalTypeT075 | Historical rate adjustments |

### API Workflow
```
Translation Adjustment via API:

1. CTA CALCULATION
   Consolidation_Execute → P_CONSO_BUNDLE_INTEGRATION_*:
     - CLOSING: Creates NOTBALPL, PLBAL, NOTBALBS, TDBS entries
     - FLOWS: Creates TRANSADJ, UNEXPVAR flow entries
     - HISTORICAL: Creates T075 journals for FlagHistoricalRate accounts

2. CTA COMPONENTS
   Calculation: Closing Amount (CC) - Flows (AC) - Historical = CTA
     - Assets/Liabilities at closing rate
     - P&L at average rate
     - Equity at historical rate
     - Difference → TDBS/TRANSADJ

3. REPORTING
   Report_ExecuteReport → P_REPORT_TRANSLATION_ADJUSTMENTS_ANALYSIS:
     - Reference period comparison
     - Flow-level breakdown
     - Group vs minority split
     - TranslationInfo categorization

4. VERIFICATION
   Journal_GetJournals → Review T075 entries
   Flow_GetFlows → Verify TRANSADJ amounts
```

### Implementation Status
| Feature | Status | Notes |
|---------|--------|-------|
| TDBS/TDPL accounts | ✅ IMPLEMENTED | Special accounts |
| TRANSADJ flow | ✅ IMPLEMENTED | CTA flow tracking |
| Historical rate adjustment | ✅ IMPLEMENTED | T075 journals |
| Group/MI split | ✅ IMPLEMENTED | MinorityFlag column |
| CTA analysis report | ✅ IMPLEMENTED | P_REPORT_TRANSLATION_ADJUSTMENTS_ANALYSIS |

### Related API Documentation
- [API Index](../11-agent-support/api-index.yaml) - Master handler catalog
- [Gap Analysis](../11-agent-support/gap-analysis-report.yaml) - **FULLY IMPLEMENTED (95%)**

---

## Related Documentation

- [Exchange Rate Types](exchange-rate-types.md) - Rate type codes and storage
- [Translation Methods](translation-methods.md) - Current rate vs temporal method
- [Stored Procedures Catalog](../07-database-implementation/stored-procedures-catalog.md) - P_CONSO_* procedure details
- [Minority Interest](../03-core-calculations/minority-interest.md) - NCI calculation with CTA

### Related Knowledge Chunks
- Chunk 0236-0238: Currency Translation of Balance Sheet and P&L
- Chunk 0240-0241: Consolidation of Foreign Companies (Year 1 & 2)
- Chunk 0242: Currency Translation of Flows
- Chunk 0243-0244: Historical Rate Management
- Chunk 0245-0246: Consolidation Adjustments in Local Currency

### Navigation
- [Cross-Reference Index](../00-index/CROSS_REFERENCE_INDEX.md) - Find related documents
- [Quick Reference Card](../20-appendices/quick-reference-card.md) - Rate type codes
- [Troubleshooting Guide](../17-troubleshooting/common-issues.md) - CTA issues
- [Glossary](../20-appendices/glossary.md) - Term definitions

---
*Document 12 of 50+ | Batch 4: Currency & Translation | Last Updated: 2024-12-01*
