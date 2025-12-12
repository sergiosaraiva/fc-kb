# Exchange Rate Types in Currency Translation

## Document Metadata
- **Category**: Currency Translation
- **Theory Source**: Knowledge base chunks: 0231, 0232, 0233, 0234, 0235, 0236, 0237, 0238, 0242, 0243, 0244
- **Implementation Files**:
  - `Sigma.Database/dbo/Tables/TS017R0.sql` (Exchange rate master table)
  - `Sigma.Database/dbo/Tables/TMP_CONSO_EXCHANGERATE.sql` (Session exchange rate cache)
  - `Sigma.Database/dbo/Stored Procedures/P_CONSO_HELPER_FILL_EXCHANGERATE.sql`
  - `Sigma.Database/dbo/Stored Procedures/P_CONSO_BUNDLE_INTEGRATION_CURRENCY_TRANSLATION_CLOSING.sql`
  - `Sigma.Database/dbo/Stored Procedures/P_CONSO_BUNDLE_INTEGRATION_CURRENCY_TRANSLATION_FLOWS.sql`
  - `Sigma.Database/dbo/Stored Procedures/P_UPDATE_CURRENCY_RATE.sql`
- **Last Updated**: 2024-12-01
- **Completeness**: 95% (All core rate types implemented)
- **Compliance Status**: IAS 21 - The Effects of Changes in Foreign Exchange Rates

## Executive Summary

Exchange rate types define how foreign currency amounts are converted to the consolidation (group) currency. Prophix.Conso implements three primary rate types (Closing, Average, Monthly Average) with variants for current and reference period handling. The implementation fully supports IAS 21 requirements for balance sheet translation at closing rates and P&L translation at average rates.

## Theoretical Framework

### Concept Definition

From Allen White's "Direct Consolidation" (Chunk 232):

> "Groups often have subsidiaries in foreign countries, meaning that the individual accounts of these subsidiaries are then booked in foreign currency... The statutory accounts of subsidiaries must then be translated into the currency of the parent company which is also called the consolidation currency."

### Key Principles

1. **Closing Rate (CC/CR)**: Applied to balance sheet accounts; represents the exchange rate at period end
2. **Average Rate (AC/AR)**: Applied to P&L accounts; represents the average rate over the period (typically arithmetic mean of monthly closing rates)
3. **Monthly Average Rate (MC/MR)**: Progressive accumulation rate for cumulative translation accuracy
4. **Historical Rate**: Applied to equity accounts to maintain consistency in consolidated reserves
5. **No Rate (NR)**: Pass-through for amounts already in consolidation currency

### Rate Type Codes in Prophix.Conso

| Code | Full Name | Description | Application |
|------|-----------|-------------|-------------|
| NR | No Rate | No conversion applied | Same-currency companies |
| CC | Closing Rate Current | Period-end rate for current period | Balance sheet accounts |
| AC | Average Rate Current | Average rate for current period | P&L accounts |
| MC | Monthly Average Current | Progressive monthly average | Cumulative P&L items |
| CR | Closing Rate Reference | Period-end rate for reference period | Opening balance sheet |
| AR | Average Rate Reference | Average rate for reference period | Reference P&L items |
| MR | Monthly Average Reference | Progressive rate from reference | Reference cumulative items |

### Formula/Algorithm

**Balance Sheet Translation** (Chunk 233):
> "A balance sheet is a picture taken at the end of the consolidation period. It seems normal to use the currency rate corresponding to that date to translate all amounts."

**P&L Translation** (Chunk 234):
> "A much more realistic approach consists in using an average rate over the twelve months of the year. Usually, this average rate is the arithmetic mean of the twelve monthly closing rates of the period."

**Translation Formula**:
```
Translated Amount = Local Amount × Exchange Rate

Where Exchange Rate depends on rate type:
- CC/CR: Closing Rate
- AC/AR: Average Rate
- MC/MR: Monthly Average Rate
- NR: 1.0 (no conversion)
```

### Example

From Chunk 236 - Year 1 Translation:
```
Local Currency (CUR):
- Assets: 5,000 CUR
- Capital: 3,500 CUR
- Profit: 300 CUR

Rates:
- Closing Rate: 1 CUR = 2 EUR
- Average Rate: 1 CUR = 2.1 EUR

Translated (EUR):
- Assets: 5,000 × 2 = 10,000 EUR (closing rate)
- Capital: 3,500 × 2 = 7,000 EUR (closing rate)
- Profit: 300 × 2.1 = 630 EUR (average rate)
```

## Current Implementation

### Database Layer

#### Exchange Rate Master Table (TS017R0)

```sql
CREATE TABLE [dbo].[TS017R0] (
    [CurrencyRateID]    INT             IDENTITY (1, 1) NOT NULL,
    [ConsoID]           INT             NOT NULL,
    [CurrCode]          NVARCHAR (3)    NOT NULL,
    [ReferenceCurrCode] NVARCHAR (3)    NOT NULL,
    [ClosingRate]       DECIMAL (28, 12) DEFAULT ((0)) NOT NULL,
    [AverageRate]       DECIMAL (28, 12) DEFAULT ((0)) NOT NULL,
    [AverageMonth]      DECIMAL (28, 12) DEFAULT ((0)) NOT NULL,
    -- Audit fields: CreatedBy, CreatedDate, ModifiedBy, ModifiedDate
    CONSTRAINT [CK_TS017R0_AverageMonth] CHECK ([AverageMonth]>=(0)),
    CONSTRAINT [CK_TS017R0_AverageRate] CHECK ([AverageRate]>=(0)),
    CONSTRAINT [CK_TS017R0_ClosingRate] CHECK ([ClosingRate]>=(0))
);
```

**Key Fields**:
- `ClosingRate`: End-of-period exchange rate (DECIMAL 28,12 for precision)
- `AverageRate`: Period average rate (arithmetic mean)
- `AverageMonth`: Monthly progressive average for cumulative calculations

#### Session Exchange Rate Cache (TMP_CONSO_EXCHANGERATE)

```sql
CREATE TABLE [dbo].[TMP_CONSO_EXCHANGERATE] (
    [SessionID]              INT             NOT NULL,
    [FromCurrCode]           NVARCHAR (3)    NOT NULL,
    [ClosingRateCur]         DECIMAL (28,12) NOT NULL,  -- Current period closing
    [AverageRateCur]         DECIMAL (28,12) NOT NULL,  -- Current period average
    [AverageMonthCur]        DECIMAL (28,12) NOT NULL,  -- Current monthly average
    [ClosingRateRef]         DECIMAL (28,12) NOT NULL,  -- Reference period closing
    [AverageRateRef]         DECIMAL (28,12) NOT NULL,  -- Reference period average
    [AverageMonthRef]        DECIMAL (28,12) NOT NULL   -- Reference monthly average
);
```

**Purpose**: Caches calculated exchange rates per consolidation session for performance. Populated by `P_CONSO_HELPER_FILL_EXCHANGERATE`.

### Rate Application Logic

From `P_CONSO_BUNDLE_INTEGRATION_CURRENCY_TRANSLATION_CLOSING.sql` (lines 590-622):

```sql
update dbo.TMP_TD035C2
set CurrCode = @ConsoCurrCode,
    Amount =
    case
        -- No Rate (NR): No conversion
        when (b.ConversionMethod = 1 and d.RateType1 = 'NR') or
             (b.ConversionMethod = 2 and d.RateType2 = 'NR') then Amount

        -- Average Rate Current (AC)
        when (b.ConversionMethod = 1 and d.RateType1 = 'AC') or
             (b.ConversionMethod = 2 and d.RateType2 = 'AC') then Amount * c.AverageRateCur

        -- Closing Rate Current (CC)
        when (b.ConversionMethod = 1 and d.RateType1 = 'CC') or
             (b.ConversionMethod = 2 and d.RateType2 = 'CC') then Amount * c.ClosingRateCur

        -- Monthly Average Current (MC) - Progressive calculation
        when (b.ConversionMethod = 1 and d.RateType1 = 'MC') or
             (b.ConversionMethod = 2 and d.RateType2 = 'MC') then
            (Amount - isnull(AmountPreviousMonthLC, 0)) * c.AverageMonthCur
            + isnull(AmountPreviousMonthGC, 0)

        -- Reference period rates (AR, CR, MR)
        when (b.ConversionMethod = 1 and d.RateType1 = 'AR') or
             (b.ConversionMethod = 2 and d.RateType2 = 'AR') then Amount * c.AverageRateRef
        when (b.ConversionMethod = 1 and d.RateType1 = 'CR') or
             (b.ConversionMethod = 2 and d.RateType2 = 'CR') then Amount * c.ClosingRateRef
        when (b.ConversionMethod = 1 and d.RateType1 = 'MR') or
             (b.ConversionMethod = 2 and d.RateType2 = 'MR') then
            (Amount - isnull(AmountPreviousMonthLC, 0)) * c.AverageMonthRef
            + isnull(AmountPreviousMonthGC, 0)
        else 0
    end
```

### Account-Level Rate Configuration

The rate type is configured per account in `TS010S0` (Chart of Accounts):
- `RateType1`: Rate type for conversion method 1
- `RateType2`: Rate type for conversion method 2
- `ConversionMethod`: Determines which rate type field to use (company-level setting)

### Application Layer

**Exchange Rate Helper** (`P_CONSO_HELPER_FILL_EXCHANGERATE.sql`):
```sql
-- Populates session exchange rate cache using UDF_CURRENCY_CALCULATE_RATES
insert into dbo.TMP_CONSO_EXCHANGERATE
    (SessionID, FromCurrCode, ClosingRateCur, AverageRateCur, AverageMonthCur,
     ClosingRateRef, AverageRateRef, AverageMonthRef)
select @SessionID, FromCurrCode, ClosingRateCur, AverageRateCur, AverageMonthCur,
       ClosingRateRef, AverageRateRef, AverageMonthRef
from dbo.UDF_CURRENCY_CALCULATE_RATES(@ConsoID, @ConsoCurrCode, @RefConsoID, 2, 1)
```

### Frontend Layer

**Exchange Rate Management Screens**:
- `Sigma.Mona.WebApplication/Screens/ImportExchangeRates/` - Import rates from external sources
- `Sigma.Mona.WebApplication/Screens/Reports/ReportPartialCurrencies.ts` - Currency reporting

## Theory vs Practice Analysis

| Aspect | Theory (Allen White) | Prophix.Conso Implementation | Alignment |
|--------|---------------------|------------------------------|-----------|
| Closing Rate | Period-end rate for B/S | `ClosingRate` field, CC/CR codes | Full |
| Average Rate | Arithmetic mean of monthly rates | `AverageRate` field, AC/AR codes | Full |
| Monthly Progressive | Cumulative translation | `AverageMonth`, MC/MR codes | Full |
| Historical Rates | Per-transaction tracking | Managed via Translation Adjustments | Indirect |
| Precision | Not specified | DECIMAL(28,12) - 12 decimal places | Exceeds |
| Reference Period | Opening balance translation | *Ref suffix rate codes (CR, AR, MR) | Full |

## Gap Analysis

### Missing Elements

1. **Historical Rate Per Transaction**: Theory suggests tracking individual transaction rates; implementation uses Translation Adjustment flows instead (valid alternative approach per Chunk 244)

### Divergent Implementation

1. **Historical Rate Management**: Rather than storing historical rates per equity transaction, Prophix.Conso manages translation differences through adjustment journals (T075 journals)

### Additional Features (Beyond Theory)

1. **Dual Conversion Methods**: Support for two parallel conversion methods per company (ConversionMethod 1 vs 2)
2. **Session-Based Rate Caching**: Performance optimization not mentioned in theory
3. **Monthly Average Variant**: MC/MR rates for progressive cumulative translation
4. **28-Digit Precision**: DECIMAL(28,12) exceeds typical consolidation requirements

## Business Impact

1. **Multi-Currency Consolidation**: Enables groups with subsidiaries in different currency zones
2. **IAS 21 Compliance**: Implementation meets international reporting standards
3. **Audit Trail**: Rate changes trigger status updates via `TR_TS017R0` trigger
4. **Precision**: 12 decimal places prevent rounding errors in large-value translations

## Recommendations

1. **Consider Historical Rate Tracking Enhancement**: For complex equity transactions with multiple acquisition tranches, explicit historical rate storage could improve auditability
2. **Rate Source Integration**: Consider API integration with market data providers for automatic rate updates
3. **Rate Validation Rules**: Add business rules to flag significant rate changes (potential data entry errors)

## API Reference

### Primary API Handlers
| Handler | YAML File | Purpose | Status |
|---------|-----------|---------|--------|
| `ExchangeRate_GetExchangeRates` | [api-exchange-rate-endpoints.yaml](../11-agent-support/api-exchange-rate-endpoints.yaml) | Get rates from TS017R0 | ✅ IMPLEMENTED |
| `ExchangeRate_SaveExchangeRate` | [api-exchange-rate-endpoints.yaml](../11-agent-support/api-exchange-rate-endpoints.yaml) | Update exchange rates | ✅ IMPLEMENTED |
| `ImportExchangeRates_Execute` | [api-import-endpoints.yaml](../11-agent-support/api-import-endpoints.yaml) | Import rates from external sources | ✅ IMPLEMENTED |

### Supporting API Handlers
| Handler | YAML File | Purpose |
|---------|-----------|---------|
| `Currency_GetCurrencies` | [api-currency-endpoints.yaml](../11-agent-support/api-currency-endpoints.yaml) | Get currency code list |
| `Consolidation_Execute` | [api-consolidation-endpoints.yaml](../11-agent-support/api-consolidation-endpoints.yaml) | Trigger rate application |

### Rate Type Reference
| Code | Field in TS017R0 | API Field | Purpose |
|------|------------------|-----------|---------|
| CC | ClosingRate | closingRateCur | Period-end rate (B/S) |
| AC | AverageRate | averageRateCur | Period average (P&L) |
| MC | AverageMonth | averageMonthCur | Monthly progressive |
| CR | ClosingRate | closingRateRef | Reference closing |
| AR | AverageRate | averageRateRef | Reference average |
| MR | AverageMonth | averageMonthRef | Reference monthly |
| NR | N/A | (rate = 1.0) | No conversion |

### API Workflow
```
Exchange Rate Management via API:

1. RATE ENTRY
   ExchangeRate_SaveExchangeRate → TS017R0:
     - CurrCode (source currency)
     - ReferenceCurrCode (target currency)
     - ClosingRate (DECIMAL 28,12)
     - AverageRate (DECIMAL 28,12)
     - AverageMonth (DECIMAL 28,12)

2. BULK IMPORT
   ImportExchangeRates_Execute → Import from:
     - Excel files
     - External rate providers
     - Manual entry screens

3. RATE CACHING
   Consolidation_Execute → P_CONSO_HELPER_FILL_EXCHANGERATE:
     - Populates TMP_CONSO_EXCHANGERATE per session
     - Calculates all rate variants (CC/AC/MC/CR/AR/MR)

4. RATE APPLICATION
   P_CONSO_BUNDLE_INTEGRATION_CURRENCY_TRANSLATION_*:
     - Amount × Rate based on RateType
```

### Related API Documentation
- [API Index](../11-agent-support/api-index.yaml) - Master handler catalog
- [Gap Analysis](../11-agent-support/gap-analysis-report.yaml) - **FULLY IMPLEMENTED (95%)**

---

## Related Documentation

- [Translation Methods](translation-methods.md) - Temporal vs Current Rate methods
- [Translation Adjustments (CTA)](translation-adjustments.md) - Cumulative Translation Adjustment handling
- [Stored Procedures Catalog](../07-database-implementation/stored-procedures-catalog.md) - P_CONSO_* procedure details
- [Consolidation Services](../08-application-layer/consolidation-services.md) - ConsolidationIntegrationJob architecture

### Related Knowledge Chunks
- Chunk 0231: Introduction to Currency Translation
- Chunk 0232: Currency Translation Principles
- Chunk 0233: Balance Sheet Translation
- Chunk 0234: P&L Translation
- Chunk 0235: Notes/Flows Translation
- Chunk 0236-0238: Translation Examples Year 1 & 2
- Chunk 0242: Currency Translation of Flows
- Chunk 0243-0244: Historical Rate Management

### Navigation
- [Cross-Reference Index](../00-index/CROSS_REFERENCE_INDEX.md) - Find related documents
- [Quick Reference Card](../20-appendices/quick-reference-card.md) - Rate type codes
- [Troubleshooting Guide](../17-troubleshooting/common-issues.md) - Currency issues
- [Glossary](../20-appendices/glossary.md) - Term definitions

---
*Document 10 of 50+ | Batch 4: Currency & Translation | Last Updated: 2024-12-01*
