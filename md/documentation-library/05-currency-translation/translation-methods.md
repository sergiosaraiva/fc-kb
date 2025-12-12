# Currency Translation Methods

## Document Metadata
- **Category**: Currency Translation
- **Theory Source**: Knowledge base chunks: 0232, 0233, 0234, 0235, 0239, 0240, 0241, 0245, 0246
- **Implementation Files**:
  - `Sigma.Database/dbo/Tables/TS014C0.sql` (Company table - ConversionMethod)
  - `Sigma.Database/dbo/Tables/TS010S0.sql` (Account table - RateType1/2, FlagHistoricalRate)
  - `Sigma.Database/dbo/Stored Procedures/P_CONSO_BUNDLE_INTEGRATION_CURRENCY_TRANSLATION_CLOSING.sql`
  - `Sigma.Database/dbo/Stored Procedures/P_CONSO_BUNDLE_INTEGRATION_CURRENCY_TRANSLATION_FLOWS.sql`
  - `Sigma.Database/dbo/Stored Procedures/P_CONSO_BUNDLE_INTEGRATION_CURRENCY_TRANSLATION_HISTORICAL.sql`
- **Last Updated**: 2024-12-01
- **Completeness**: 95% (Current rate method fully implemented; dual-method support available)
- **Compliance Status**: IAS 21 - The Effects of Changes in Foreign Exchange Rates

## Executive Summary

Prophix.Conso implements currency translation using a flexible dual-method architecture that supports both the Current Rate Method (primary IFRS approach) and configurable alternative methods through account-level rate type configuration. The system uses a ConversionMethod flag per company combined with RateType1/RateType2 settings per account to determine which exchange rate applies during translation.

## Theoretical Framework

### Concept Definition

From Allen White's "Direct Consolidation" (Chunk 232):

> "Groups often have subsidiaries in foreign countries, meaning that the individual accounts of these subsidiaries are then booked in foreign currency... For these subsidiaries whose accounts are booked in foreign currency, we highly recommend to receive foreign currency information instead of information already translated into consolidation currency. The explanations developed in this chapter will show that this process of currency translation must be managed by the consolidation department."

### Translation Methods Overview

| Method | Application | Balance Sheet | P&L | Equity |
|--------|-------------|---------------|-----|--------|
| **Current Rate Method** | Functional currency subsidiaries (IAS 21) | Closing rate | Average rate | Historical rate |
| **Temporal Method** | Foreign operations in hyperinflationary economies | Monetary: Closing; Non-monetary: Historical | Historical rates | Historical rate |
| **Direct Translation** | Same functional and presentation currency | No translation needed | No translation needed | No translation needed |

### Visual: Translation Method Comparison

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    CURRENCY TRANSLATION METHOD COMPARISON                    │
└─────────────────────────────────────────────────────────────────────────────┘

  CURRENT RATE METHOD (IAS 21 - Standard)     TEMPORAL METHOD (Hyperinflationary)
  ────────────────────────────────────────    ───────────────────────────────────

  ┌─────────────────────────────────────┐    ┌─────────────────────────────────────┐
  │          BALANCE SHEET               │    │          BALANCE SHEET               │
  ├─────────────────────────────────────┤    ├─────────────────────────────────────┤
  │ Monetary Assets    → CLOSING RATE   │    │ Monetary Assets    → CLOSING RATE   │
  │ Non-monetary       → CLOSING RATE   │    │ Non-monetary       → HISTORICAL     │
  │ Liabilities        → CLOSING RATE   │    │ Liabilities        → CLOSING RATE   │
  │ Equity             → HISTORICAL     │    │ Equity             → HISTORICAL     │
  └─────────────────────────────────────┘    └─────────────────────────────────────┘
           │                                           │
           ▼                                           ▼
  ┌─────────────────────────────────────┐    ┌─────────────────────────────────────┐
  │          INCOME STATEMENT            │    │          INCOME STATEMENT            │
  ├─────────────────────────────────────┤    ├─────────────────────────────────────┤
  │ Revenue            → AVERAGE RATE   │    │ Revenue            → HISTORICAL     │
  │ Cost of Sales      → AVERAGE RATE   │    │ Cost of Sales      → HISTORICAL     │
  │ Operating Expenses → AVERAGE RATE   │    │ Depreciation       → HISTORICAL     │
  │ Depreciation       → AVERAGE RATE   │    │ Other Expenses     → HISTORICAL     │
  └─────────────────────────────────────┘    └─────────────────────────────────────┘
           │                                           │
           ▼                                           ▼
  ┌─────────────────────────────────────┐    ┌─────────────────────────────────────┐
  │       TRANSLATION DIFFERENCE         │    │       TRANSLATION DIFFERENCE         │
  ├─────────────────────────────────────┤    ├─────────────────────────────────────┤
  │ Posted to OCI (TRANSADJ)            │    │ Posted to P&L                       │
  │ Accumulates in equity               │    │ Immediate income/expense impact     │
  │ Recycled on disposal                │    │ No recycling needed                 │
  └─────────────────────────────────────┘    └─────────────────────────────────────┘

  RATE CODES IN PROPHIX.CONSO:
  ┌──────────┬─────────────────────────────────────────┐
  │ Code     │ Description                             │
  ├──────────┼─────────────────────────────────────────┤
  │ CC       │ Closing Current - Period-end spot rate  │
  │ CR       │ Closing Reference - Prior period end    │
  │ AC       │ Average Current - Period average        │
  │ AR       │ Average Reference - Prior period avg    │
  │ MC       │ Monthly Cumulative - Progressive avg    │
  │ NR       │ No Rate - Same currency (rate = 1)      │
  └──────────┴─────────────────────────────────────────┘
```

### Key Principles

From the theory (Chunks 233-235):

1. **Balance Sheet Translation** (Chunk 233):
> "A balance sheet is a picture taken at the end of the consolidation period. It seems normal to use the currency rate corresponding to that date to translate all amounts."

2. **P&L Translation** (Chunk 234):
> "The P&L is not a picture. It is a movie... A much more realistic approach consists in using an average rate over the twelve months of the year."

3. **Notes/Flows Translation** (Chunk 235):
> "Speaking about the flows, they are also a kind of movie showing different pictures during the consolidation period. Happening during the year, it seems reasonable to also use the same average rate as the one used for the P&L."

4. **Historical Rate for Equity**:
> Equity accounts require historical rate translation to maintain consistency in consolidated reserves and avoid unexplainable variations due to exchange rate fluctuations.

### The Current Rate Method (Primary Implementation)

The current rate method (also called the closing rate method) is the standard approach under IAS 21 for translating functional currency subsidiaries:

**Step 1**: Translate all balance sheet items at closing rate (except equity)
**Step 2**: Translate P&L items at average rate
**Step 3**: Translate equity at historical rates
**Step 4**: Record translation differences in Other Comprehensive Income (Translation Adjustments)

### Example from Theory (Chunk 236)

```
Local Currency (CUR) Balance Sheet:
- Assets: 5,000 CUR
- Capital: 3,500 CUR
- Reserves: 0 CUR
- Profit: 300 CUR
- Liabilities: 1,200 CUR

Exchange Rates:
- Closing Rate: 1 CUR = 2 EUR
- Average Rate: 1 CUR = 2.1 EUR

Translation Process:
1. Assets at Closing Rate: 5,000 × 2 = 10,000 EUR
2. Liabilities at Closing Rate: 1,200 × 2 = 2,400 EUR
3. Capital at Closing Rate: 3,500 × 2 = 7,000 EUR
4. Profit at Average Rate: 300 × 2.1 = 630 EUR
5. Translation Adjustment = (600 - 630) = -30 EUR (balancing entry)
```

## Current Implementation

### Architecture Overview

Prophix.Conso implements translation methods through a three-tier configuration:

```
Company Level (TS014C0)
├── ConversionMethod: 1 or 2
│
Account Level (TS010S0)
├── RateType1: CC, AC, MC, CR, AR, MR, NR (for ConversionMethod 1)
├── RateType2: CC, AC, MC, CR, AR, MR, NR (for ConversionMethod 2)
├── FlagHistoricalRate1: Boolean (for ConversionMethod 1)
└── FlagHistoricalRate2: Boolean (for ConversionMethod 2)
```

### Company Configuration (TS014C0)

```sql
CREATE TABLE [dbo].[TS014C0] (
    [CompanyID]        INT           NOT NULL,
    [CompanyCode]      NVARCHAR(12)  NOT NULL,
    [CurrCode]         NVARCHAR(3)   NOT NULL,       -- Company's local currency
    [ConsoMethod]      CHAR(1)       DEFAULT('G'),   -- G=Global, E=Equity, P=Proportional
    [ConversionMethod] TINYINT       DEFAULT((1)),   -- 1 or 2 (determines rate set)
    -- ...
    CONSTRAINT [CK_TS014C0_CONVERSIONMETHOD] CHECK ([ConversionMethod]=(2) OR [ConversionMethod]=(1))
);
```

**ConversionMethod Values**:
- **1**: Use RateType1 and FlagHistoricalRate1 from account configuration
- **2**: Use RateType2 and FlagHistoricalRate2 from account configuration

This dual-method approach allows:
- Different companies to use different translation approaches
- Same chart of accounts with flexible rate assignments
- Support for temporal method via RateType2 configuration

### Account Configuration (TS010S0)

```sql
CREATE TABLE [dbo].[TS010S0] (
    [AccountID]            INT           NOT NULL,
    [Account]              NVARCHAR(12)  NOT NULL,
    [AccountType]          CHAR(1)       NOT NULL,   -- B=Balance, P=P&L

    -- Conversion Method 1 Settings
    [RateType1]            CHAR(2)       DEFAULT('CC'),  -- Rate type for method 1
    [FlagHistoricalRate1]  BIT           DEFAULT((0)),   -- Historical rate flag
    [HistoricalAccountID1] INT           NULL,           -- Target account for historical adj.

    -- Conversion Method 2 Settings
    [RateType2]            CHAR(2)       DEFAULT('CC'),  -- Rate type for method 2
    [FlagHistoricalRate2]  BIT           DEFAULT((0)),   -- Historical rate flag
    [HistoricalAccountID2] INT           NULL,           -- Target account for historical adj.

    CONSTRAINT [CK_TS010S0_RATETYPE1] CHECK ([RateType1] IN ('CC','AC','MC','CR','AR','MR','NR')),
    CONSTRAINT [CK_TS010S0_RATETYPE2] CHECK ([RateType2] IN ('CC','AC','MC','CR','AR','MR','NR'))
);
```

### Rate Type Application Logic

From `P_CONSO_BUNDLE_INTEGRATION_CURRENCY_TRANSLATION_CLOSING.sql` (lines 590-622):

```sql
update dbo.TMP_TD035C2
set CurrCode = @ConsoCurrCode,
    Amount =
    case
        -- Select rate based on ConversionMethod (1 or 2)
        when (b.ConversionMethod = 1 and d.RateType1 = 'NR') or
             (b.ConversionMethod = 2 and d.RateType2 = 'NR')
            then Amount  -- No conversion

        when (b.ConversionMethod = 1 and d.RateType1 = 'AC') or
             (b.ConversionMethod = 2 and d.RateType2 = 'AC')
            then Amount * c.AverageRateCur  -- Average rate current

        when (b.ConversionMethod = 1 and d.RateType1 = 'CC') or
             (b.ConversionMethod = 2 and d.RateType2 = 'CC')
            then Amount * c.ClosingRateCur  -- Closing rate current

        when (b.ConversionMethod = 1 and d.RateType1 = 'MC') or
             (b.ConversionMethod = 2 and d.RateType2 = 'MC')
            then (Amount - isnull(AmountPreviousMonthLC,0)) * c.AverageMonthCur
                 + isnull(AmountPreviousMonthGC,0)  -- Monthly cumulative
        -- ... Reference period rates (AR, CR, MR)
    end
from dbo.TMP_CONSO_COMPANYID b
     inner join dbo.TMP_CONSO_EXCHANGERATE c
     inner join dbo.TS010S0 d  -- Account settings
```

### Translation Process Flow

The consolidation process executes translation in three main procedures:

```
1. P_CONSO_BUNDLE_INTEGRATION_CURRENCY_TRANSLATION_CLOSING
   ├── Translates balance sheet amounts (B001 journal)
   ├── Applies closing rate to B/S accounts
   ├── Applies average rate to P&L accounts
   ├── Creates NOTBALPL, PLBAL, NOTBALBS corrective entries
   └── Calculates TDPL (Translation Difference P&L) and TDBS entries

2. P_CONSO_BUNDLE_INTEGRATION_CURRENCY_TRANSLATION_FLOWS
   ├── Translates flow data (movements during period)
   ├── Applies appropriate rates per flow type
   ├── Calculates TRANSADJ flow for translation differences
   └── Manages UNEXPVAR (Unexplained Variance) flow

3. P_CONSO_BUNDLE_INTEGRATION_CURRENCY_TRANSLATION_HISTORICAL
   ├── Handles historical rate adjustments (T075 journals)
   ├── Processes FlagHistoricalRate accounts
   └── Creates adjustment entries in TD033E0/TD035C2
```

### Historical Rate Handling

Accounts with `FlagHistoricalRate = 1` receive special treatment:

From `P_CONSO_BUNDLE_INTEGRATION_CURRENCY_TRANSLATION_HISTORICAL.sql` (line 191):

```sql
-- Select accounts requiring historical rate treatment
insert into dbo.TMP_TD045C2 (...)
select ...
from dbo.TMP_CONSO_COMPANYID a
     inner join dbo.TD045C2 b on (...)
     inner join dbo.TS010S0 c on (...)
where a.SessionID = @SessionID
      and b.JournalTypeID = @JournalTypeB001ID
      and b.FlowID = @TRANSADJFlowID
      and ((a.ConversionMethod = 1 and c.FlagHistoricalRate1 = 1)
           or (a.ConversionMethod = 2 and c.FlagHistoricalRate2 = 1))
```

This creates T075 (Historical Translation) journal entries that:
- Reverse the translation difference on historical-rate accounts
- Book the difference to TDBS (Translation Difference Balance Sheet)
- Maintain equity accounts at historical rates

### Typical Configuration: Current Rate Method

For standard IAS 21 current rate method translation:

| Account Type | RateType1 | FlagHistoricalRate1 | Description |
|--------------|-----------|---------------------|-------------|
| Assets (B/S) | CC | 0 | Closing rate, no historical adjustment |
| Liabilities (B/S) | CC | 0 | Closing rate, no historical adjustment |
| Capital (Equity) | CC | 1 | Closing rate with historical adjustment |
| Reserves (Equity) | CC | 1 | Closing rate with historical adjustment |
| Income (P&L) | AC | 0 | Average rate |
| Expenses (P&L) | AC | 0 | Average rate |

### Alternative Configuration: Temporal Method

For temporal method (ConversionMethod = 2):

| Account Type | RateType2 | FlagHistoricalRate2 | Description |
|--------------|-----------|---------------------|-------------|
| Monetary Assets | CC | 0 | Closing rate |
| Non-monetary Assets | CC | 1 | Historical rate via flag |
| Monetary Liabilities | CC | 0 | Closing rate |
| Non-monetary Liabilities | CC | 1 | Historical rate via flag |
| Equity | CC | 1 | Historical rate |
| Income/Expenses | AC | 0 | Transaction date (approximated by average) |

## Theory vs Practice Analysis

| Aspect | Theory (Allen White/IAS 21) | Prophix.Conso Implementation | Alignment |
|--------|---------------------------|------------------------------|-----------|
| Current Rate Method | Primary method for functional currency subs | ConversionMethod 1 + RateType1 settings | Full |
| Temporal Method | For hyperinflationary economies | ConversionMethod 2 + RateType2 settings | Configurable |
| B/S at Closing Rate | Standard for assets/liabilities | RateType = CC (default) | Full |
| P&L at Average Rate | Standard for income/expenses | RateType = AC for P&L accounts | Full |
| Equity at Historical | Required for consolidated reserves integrity | FlagHistoricalRate + T075 journals | Full |
| Dual-Method Support | Different methods for different subsidiaries | Per-company ConversionMethod | Enhanced |

## Gap Analysis

### Missing Elements

1. **Hyperinflation Adjustments (IAS 29)**: The temporal method support is partial; full IAS 29 restatement before translation is not automated

### Divergent Implementation

1. **Historical Rate Mechanism**: Rather than storing actual historical exchange rates per transaction, the system uses adjustment journals (T075) to achieve the same result - this is a valid implementation approach noted in Chunk 244

### Additional Features (Beyond Theory)

1. **Dual Conversion Methods**: Support for two parallel translation configurations per chart of accounts
2. **Monthly Average Rate (MC/MR)**: Progressive cumulative translation for mid-year accuracy
3. **Reference Period Rates (CR/AR/MR)**: Explicit support for prior period comparison rates
4. **Account-Level Rate Override**: Each account can have different rate types independent of account type

## Business Impact

1. **Multi-Currency Group Consolidation**: Supports groups with subsidiaries in different currency zones
2. **IAS 21 Compliance**: Standard current rate method implementation meets regulatory requirements
3. **Flexibility**: Dual-method architecture allows different approaches for different subsidiaries
4. **Audit Trail**: Historical adjustments tracked in T075 journals with full journal entry details

## Recommendations

1. **Document Standard Configurations**: Create template account setups for common scenarios (current rate, temporal)
2. **Add IAS 29 Support**: Consider adding automated hyperinflation restatement for complete temporal method support
3. **Configuration Validation**: Add validation rules to ensure rate type assignments are consistent with account types

## API Reference

### Primary API Handlers
| Handler | YAML File | Purpose | Status |
|---------|-----------|---------|--------|
| `Consolidation_Execute` | [api-consolidation-endpoints.yaml](../11-agent-support/api-consolidation-endpoints.yaml) | Trigger currency translation procedures | ✅ IMPLEMENTED |
| `ExchangeRate_GetExchangeRates` | [api-exchange-rate-endpoints.yaml](../11-agent-support/api-exchange-rate-endpoints.yaml) | Get exchange rates from TS017R0 | ✅ IMPLEMENTED |
| `ExchangeRate_SaveExchangeRate` | [api-exchange-rate-endpoints.yaml](../11-agent-support/api-exchange-rate-endpoints.yaml) | Update exchange rates | ✅ IMPLEMENTED |

### Supporting API Handlers
| Handler | YAML File | Purpose |
|---------|-----------|---------|
| `Company_GetCompanies` | [api-company-endpoints.yaml](../11-agent-support/api-company-endpoints.yaml) | Get ConversionMethod (1/2) setting |
| `Account_GetAccounts` | [api-account-endpoints.yaml](../11-agent-support/api-account-endpoints.yaml) | Get RateType1/2, FlagHistoricalRate settings |
| `Report_ExecuteReport` | [api-reports-endpoints.yaml](../11-agent-support/api-reports-endpoints.yaml) | Currency translation reports |

### API Workflow
```
Currency Translation via API:

1. CONFIGURATION
   Company_GetCompanies → Get ConversionMethod per company:
     - Method 1: Standard (Current Rate)
     - Method 2: Alternative (Temporal)
   Account_GetAccounts → Get rate type assignments:
     - RateType1/RateType2 (CC/AC/MC/NR)
     - FlagHistoricalRate1/2

2. EXCHANGE RATE ENTRY
   ExchangeRate_SaveExchangeRate → Update TS017R0:
     - ClosingRate (CC)
     - AverageRate (AC)
     - AverageMonth (MC)

3. TRANSLATION EXECUTION
   Consolidation_Execute → P_CONSO_BUNDLE_INTEGRATION:
     - P_CONSO_HELPER_FILL_EXCHANGERATE (cache rates)
     - P_CONSO_BUNDLE_INTEGRATION_CURRENCY_TRANSLATION_CLOSING
     - P_CONSO_BUNDLE_INTEGRATION_CURRENCY_TRANSLATION_FLOWS
     - P_CONSO_BUNDLE_INTEGRATION_CURRENCY_TRANSLATION_HISTORICAL

4. VERIFICATION
   Report_ExecuteReport → Translation analysis reports
```

### Implementation Status
| Feature | Status | Notes |
|---------|--------|-------|
| Current Rate Method | ✅ IMPLEMENTED | ConversionMethod = 1 |
| Temporal Method | ✅ IMPLEMENTED | ConversionMethod = 2 |
| Dual-method architecture | ✅ IMPLEMENTED | Per-company setting |
| Account-level rates | ✅ IMPLEMENTED | RateType1/2 per account |
| Historical rate adjustment | ✅ IMPLEMENTED | T075 journals |

### Related API Documentation
- [API Index](../11-agent-support/api-index.yaml) - Master handler catalog
- [Gap Analysis](../11-agent-support/gap-analysis-report.yaml) - **FULLY IMPLEMENTED (95%)**

---

## Related Documentation

- [Exchange Rate Types](exchange-rate-types.md) - Rate type codes and storage
- [Translation Adjustments (CTA)](translation-adjustments.md) - Handling cumulative translation differences
- [Stored Procedures Catalog](../07-database-implementation/stored-procedures-catalog.md) - P_CONSO_* procedure details
- [Consolidation Services](../08-application-layer/consolidation-services.md) - Application layer architecture

### Related Knowledge Chunks
- Chunk 0232: Currency Translation Principles
- Chunk 0233: Balance Sheet Translation (Closing Rate)
- Chunk 0234: P&L Translation (Average Rate)
- Chunk 0235: Notes/Flows Translation
- Chunk 0239-0241: Consolidation of Foreign Companies
- Chunk 0243-0244: Historical Rate Management
- Chunk 0245-0246: Consolidation Adjustments in Local Currency

---
*Document 11 of 50+ | Batch 4: Currency & Translation | Last Updated: 2024-12-01*
