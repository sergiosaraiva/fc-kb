# Hyperinflation Accounting: IAS 29 in Consolidation

## Document Metadata
- **Category**: Currency Translation
- **Theory Source**: IAS 29 - Financial Reporting in Hyperinflationary Economies
- **Implementation Files**:
  - `Sigma.Database/dbo/Tables/TS014C0.sql` - ConversionMethod column
  - `Sigma.Database/dbo/Tables/TS010S0.sql` - RateType2, FlagHistoricalRate2
  - `Sigma.Database/dbo/Stored Procedures/P_CONSO_BUNDLE_INTEGRATION_CURRENCY_TRANSLATION_CLOSING.sql`
  - `Sigma.Database/dbo/Stored Procedures/P_CONSO_BUNDLE_INTEGRATION_CURRENCY_TRANSLATION_HISTORICAL.sql`
- **Last Updated**: 2024-12-01
- **Completeness**: 40% (Framework exists; automated IAS 29 restatement not implemented)
- **Compliance Status**: PARTIAL - Temporal method configurable; full IAS 29 automation not available

## Executive Summary

IAS 29 "Financial Reporting in Hyperinflationary Economies" requires that financial statements of entities operating in hyperinflationary economies be restated in terms of the measuring unit current at the balance sheet date before translation. Prophix.Conso provides **partial support** through its dual ConversionMethod architecture and configurable rate types, but **does not automate the full IAS 29 restatement process**. Users must perform manual adjustments or use the User Elimination Framework for hyperinflationary subsidiary handling.

## Theoretical Framework

### IAS 29 Core Requirements

From IAS 29 standards:

> "The financial statements of an entity whose functional currency is the currency of a hyperinflationary economy shall be stated in terms of the measuring unit current at the balance sheet date."

### Hyperinflation Indicators (IAS 29.3)

An economy is considered hyperinflationary when:
1. The general population prefers to keep wealth in non-monetary assets or stable foreign currency
2. Monetary amounts are stated in terms of a stable foreign currency
3. Credit and lending prices compensate for expected inflation
4. Interest rates, wages, and prices are linked to a price index
5. **Cumulative inflation over three years approaches or exceeds 100%**

### Translation Process Under IAS 29

| Step | IAS 29 Requirement | Description |
|------|-------------------|-------------|
| 1 | **Restatement** | Restate historical cost statements using general price index |
| 2 | **Monetary vs Non-Monetary** | Classify items as monetary (not restated) or non-monetary (restated) |
| 3 | **Price Index Application** | Apply conversion factors based on acquisition dates |
| 4 | **Translation** | Translate restated statements at closing rate (IAS 21) |
| 5 | **P&L Treatment** | All gains/losses from restatement through P&L |

### Restatement Mechanics

```
Non-Monetary Items:
  Restated Amount = Historical Cost × (Closing Index / Acquisition Index)

Monetary Items:
  No restatement needed (already at current purchasing power)

Equity Components:
  Restated from initial recognition dates

Income/Expenses:
  Restated from transaction dates (or monthly averages)
```

### Example: Hyperinflation Restatement

```
Company in Hyperinflationary Economy:
  Fixed Assets acquired Year 1: 1,000 LC
  Acquisition Index (Year 1): 100
  Closing Index (Year 3): 250

Restatement:
  Restated Fixed Assets = 1,000 × (250 / 100) = 2,500 LC

Then translate to group currency:
  Group Amount = 2,500 LC × Closing Rate
```

## Current Implementation

### Dual ConversionMethod Architecture

Prophix.Conso supports two conversion method configurations per company:

```sql
-- TS014C0.sql
[ConversionMethod] TINYINT DEFAULT((1)),
CONSTRAINT [CK_TS014C0_CONVERSIONMETHOD] CHECK ([ConversionMethod]=(2) OR [ConversionMethod]=(1))
```

- **ConversionMethod = 1**: Standard (Current Rate Method)
- **ConversionMethod = 2**: Alternative (can be configured for Temporal Method)

### Rate Type Configuration

Each account has two sets of rate configurations:

```sql
-- TS010S0.sql
[RateType1]            CHAR(2) DEFAULT('CC'),  -- For ConversionMethod 1
[RateType2]            CHAR(2) DEFAULT('CC'),  -- For ConversionMethod 2
[FlagHistoricalRate1]  BIT DEFAULT((0)),
[FlagHistoricalRate2]  BIT DEFAULT((0)),
```

### Rate Type Codes

| Code | Description | Typical Use |
|------|-------------|-------------|
| CC | Closing Rate Current | Balance sheet items |
| AC | Average Rate Current | P&L items |
| MC | Monthly Cumulative | Progressive translation |
| CR | Closing Rate Reference | Prior period comparison |
| AR | Average Rate Reference | Prior period P&L |
| MR | Monthly Reference | Prior period monthly |
| NR | No Rate | No translation |

### Temporal Method Configuration (ConversionMethod 2)

For hyperinflationary entities, RateType2 can be configured:

| Account Type | RateType2 | FlagHistoricalRate2 | Effect |
|--------------|-----------|---------------------|--------|
| Cash/Receivables (Monetary) | CC | 0 | Closing rate, no adjustment |
| Inventory (Non-Monetary) | CC | 1 | Historical rate via flag |
| Fixed Assets (Non-Monetary) | CC | 1 | Historical rate via flag |
| Payables (Monetary) | CC | 0 | Closing rate |
| Equity | CC | 1 | Historical rate |
| Revenue/Expenses | AC | 0 | Average (approx. transaction date) |

### Historical Rate Processing

From `P_CONSO_BUNDLE_INTEGRATION_CURRENCY_TRANSLATION_HISTORICAL.sql`:

```sql
-- Accounts with FlagHistoricalRate create T075 adjustment journals
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

## Gap Analysis

### What IS Implemented

| Feature | Status | Implementation |
|---------|--------|----------------|
| Dual conversion methods | **Full** | ConversionMethod 1/2 per company |
| Account-level rate types | **Full** | RateType1/RateType2 per account |
| Historical rate flag | **Full** | FlagHistoricalRate1/2 |
| Temporal method config | **Partial** | Through RateType2 settings |
| T075 adjustment journals | **Full** | Historical rate corrections |

### What IS NOT Implemented

| Feature | Gap | Severity | Workaround |
|---------|-----|----------|------------|
| **Automatic IAS 29 Restatement** | Price index-based restatement before translation | 8 | Manual adjustment entries |
| **Price Index Table** | No storage for CPI/price indices | 7 | External calculation |
| **Acquisition Date Tracking** | No per-asset acquisition date for index lookup | 6 | User elimination framework |
| **Gain/Loss on Net Monetary Position** | Not calculated automatically | 7 | Manual journal entry |
| **Hyperinflation Flag** | No automatic detection | 5 | Set ConversionMethod = 2 manually |
| **Dual Currency Translation** | Restatement → then translation | 8 | Two-step manual process |

### Implementation Limitation Detail

**IAS 29 Full Compliance Requires**:

```
Step 1: Restatement (in local functional currency)
   - Monetary items: No change
   - Non-monetary items: Apply price index factor
   - P&L items: Restate from transaction date indices
   - Result: Restated local currency statements

Step 2: Translation (to group currency)
   - All amounts at closing rate (IAS 21.42)
   - No average rate for P&L (already restated)
   - CTA through OCI

Current System:
   - Supports Step 2 via ConversionMethod 2 + rate types
   - Does NOT automate Step 1 (price index restatement)
```

## Workaround Approach

### Manual Hyperinflation Processing

1. **External Restatement**:
   - Calculate restated amounts outside system
   - Apply price index factors to non-monetary items

2. **Data Entry**:
   - Enter restated amounts as local data (TD030B2/TD040B2)
   - OR use intercompany data entry with adjustment journals

3. **Configure ConversionMethod**:
   ```sql
   UPDATE TS014C0
   SET ConversionMethod = 2
   WHERE CompanyID = @HyperinflationaryCompanyID
   ```

4. **Configure Temporal Rates** (RateType2):
   - Monetary accounts: CC, FlagHistoricalRate2 = 0
   - Non-monetary accounts: CC, FlagHistoricalRate2 = 1

5. **User Elimination Framework**:
   - Create U-type elimination for gain/loss on net monetary position
   - Configure from monetary item analysis

### Example User Elimination for Net Monetary Gain/Loss

```sql
-- TS070S0 Header
INSERT INTO TS070S0 (ElimCode, ElimType, ElimText, ConsoMethodSelectionID, ...)
VALUES ('U050', 'U', 'Hyperinflation Gain/Loss', 4, ...)  -- Global only

-- TS071S0 Detail
INSERT INTO TS071S0 (EliminationHeaderID, FromType, FromAccountID, ToAccountID, ToSign, ...)
-- Credit Net Monetary Position account, Debit P&L gain/loss
```

## Comparison with IAS Requirements

| IAS 29 Requirement | Prophix.Conso Support | Gap |
|-------------------|----------------------|-----|
| Identify hyperinflationary economies | Manual identification | No auto-detection |
| Restate non-monetary items | Manual/external | No price index automation |
| Restate income/expenses | Manual/external | No transaction date indexing |
| Calculate monetary gain/loss | Manual/User Elim | No automatic calculation |
| Translate restated statements | ConversionMethod 2 | Supported via config |
| Present comparatives | Manual adjustment | Limited automation |

## Business Impact

### Current Capability
- Groups with hyperinflationary subsidiaries can achieve IAS 29 compliance
- Requires significant manual effort outside the system
- Final translation step supported through configuration

### Recommended Enhancement
- Add price index table (TS017R3 or similar)
- Add acquisition date tracking for non-monetary items
- Automate restatement calculation as pre-translation step
- Add net monetary position gain/loss calculation

## Appendix: Comprehensive Hyperinflation Accounting Examples

### Example 1: Temporal Method Configuration in Prophix.Conso

**Scenario**: Argentine subsidiary (ARS) needs to be consolidated using temporal method due to hyperinflation

**Step 1: Mark Company for Temporal Method**

```sql
-- Set ConversionMethod = 2 for the hyperinflationary subsidiary
UPDATE TS014C0
SET ConversionMethod = 2
WHERE ConsoID = @ConsoID
  AND CompanyCode = 'ARG_SUB';

-- Verify the change
SELECT CompanyCode, ConversionMethod, CurrCode
FROM TS014C0
WHERE ConsoID = @ConsoID
  AND CompanyCode = 'ARG_SUB';
-- Result: ARG_SUB, 2, ARS
```

**Step 2: Configure Account Rate Types (RateType2)**

| Account Type | Account Examples | RateType2 | FlagHistoricalRate2 | Rationale |
|--------------|------------------|-----------|---------------------|-----------|
| Cash & Equivalents | 1010 Cash | CC | 0 | Monetary - closing rate |
| Receivables | 1200 Trade Receivables | CC | 0 | Monetary - closing rate |
| Inventory | 1300 Inventory | CC | 1 | Non-monetary - historical |
| Fixed Assets | 1500 PP&E | CC | 1 | Non-monetary - historical |
| Payables | 2100 Trade Payables | CC | 0 | Monetary - closing rate |
| Borrowings | 2400 Long-term Debt | CC | 0 | Monetary - closing rate |
| Share Capital | 3010 Share Capital | CC | 1 | Non-monetary - historical |
| Retained Earnings | 3500 Retained Earnings | CC | 1 | Non-monetary - historical |
| Revenue | 4000 Sales Revenue | AC | 0 | Average (approx. transaction) |
| Cost of Sales | 5000 COGS | AC | 0 | Average rate |
| Operating Expenses | 6000 SG&A | AC | 0 | Average rate |

**Step 3: SQL Configuration**

```sql
-- Configure non-monetary accounts for temporal method
UPDATE TS010S0
SET RateType2 = 'CC',
    FlagHistoricalRate2 = 1  -- Use historical rate
WHERE ConsoID = @ConsoID
  AND AccountID IN (
    SELECT AccountID FROM TS010S0
    WHERE ConsoID = @ConsoID
      AND (AccountCode LIKE '13%'   -- Inventory
           OR AccountCode LIKE '15%' -- Fixed Assets
           OR AccountCode LIKE '30%' -- Equity
           OR AccountCode LIKE '35%') -- Retained Earnings
  );

-- Configure P&L accounts for average rate
UPDATE TS010S0
SET RateType2 = 'AC',
    FlagHistoricalRate2 = 0  -- Use average rate
WHERE ConsoID = @ConsoID
  AND AccountID IN (
    SELECT AccountID FROM TS010S0
    WHERE ConsoID = @ConsoID
      AND (AccountCode LIKE '4%'    -- Revenue
           OR AccountCode LIKE '5%'  -- Cost of Sales
           OR AccountCode LIKE '6%') -- Expenses
  );
```

### Example 2: Complete IAS 29 Workaround Process

**Scenario**: Full hyperinflation accounting for Venezuelan subsidiary

**Given Data (Local Currency - VES)**:

| Account | Historical Cost (VES) | Acquisition Date | Acquisition Index | Current Index (Dec 2024) |
|---------|----------------------|------------------|-------------------|-------------------------|
| Fixed Assets | 10,000 | Jan 2020 | 100 | 1,500 |
| Inventory | 5,000 | Oct 2024 | 1,200 | 1,500 |
| Share Capital | 8,000 | Jan 2020 | 100 | 1,500 |
| Retained Earnings | 4,000 | Cumulative | Various | 1,500 |

**Exchange Rates**:
- Closing rate (Dec 2024): 1 USD = 50 VES
- Average rate (2024): 1 USD = 35 VES

**Step 1: Calculate IAS 29 Restatement Factors**

```
Fixed Assets:
  Restatement Factor = Current Index / Acquisition Index
                     = 1,500 / 100 = 15.0
  Restated Amount = 10,000 × 15.0 = 150,000 VES

Inventory (FIFO - recent acquisition):
  Restatement Factor = 1,500 / 1,200 = 1.25
  Restated Amount = 5,000 × 1.25 = 6,250 VES

Share Capital:
  Restatement Factor = 1,500 / 100 = 15.0
  Restated Amount = 8,000 × 15.0 = 120,000 VES

Retained Earnings:
  Opening (restated): 4,000 × 12.0 (assumed avg factor) = 48,000 VES
  Plus: Current year profit (restated)
```

**Step 2: Calculate Net Monetary Position Gain/Loss**

```
Net Monetary Position Analysis:
                        Opening    Avg Position   Closing
Cash                     2,000       3,000         4,000
Receivables              3,000       4,000         5,000
Less: Payables          (6,000)     (7,000)       (8,000)
Less: Debt              (5,000)     (5,000)       (5,000)
-----------------------------------------------------------
Net Monetary Position   (6,000)     (5,000)       (4,000)

Purchasing Power Gain/Loss:
  Opening NMP restated to closing: (6,000) × (1,500/1,000) = (9,000)
  Actual closing NMP: (4,000)
  Purchasing Power Gain: (4,000) - (9,000) = 5,000 VES gain

(In hyperinflation, holding net monetary liabilities = GAIN)
```

**Step 3: External Restatement Worksheet**

| Line | Description | Historical VES | Index Factor | Restated VES |
|------|-------------|----------------|--------------|--------------|
| 1 | Fixed Assets (gross) | 10,000 | 15.0 | 150,000 |
| 2 | Accum Depreciation | (2,000) | 15.0 | (30,000) |
| 3 | Fixed Assets (net) | 8,000 | | 120,000 |
| 4 | Inventory | 5,000 | 1.25 | 6,250 |
| 5 | Cash | 4,000 | 1.0 | 4,000 |
| 6 | Receivables | 5,000 | 1.0 | 5,000 |
| 7 | **Total Assets** | **22,000** | | **135,250** |
| 8 | Payables | 8,000 | 1.0 | 8,000 |
| 9 | Debt | 5,000 | 1.0 | 5,000 |
| 10 | **Total Liabilities** | **13,000** | | **13,000** |
| 11 | Share Capital | 8,000 | 15.0 | 120,000 |
| 12 | Retained Earnings | 1,000 | Balancing | 2,250 |
| 13 | **Total Equity** | **9,000** | | **122,250** |

**Step 4: Enter Restated Data in Prophix.Conso**

Option A: Enter restated amounts directly as local data
```sql
-- If entering restated amounts (150,000 VES for Fixed Assets)
-- Enter via standard data entry screens or import
-- System will then translate at closing rate
```

Option B: Enter historical amounts + adjustment journal
```sql
-- Enter historical: 10,000 VES
-- Create adjustment journal for restatement: +140,000 VES
```

**Step 5: Configure Translation and Run Consolidation**

```sql
-- 1. Ensure ConversionMethod = 2
-- 2. Run consolidation
-- 3. System translates at configured rates:

Translation Result (Restated VES → USD at closing rate 50):
  Fixed Assets: 120,000 VES / 50 = 2,400 USD
  Inventory: 6,250 VES / 50 = 125 USD
  Share Capital: 120,000 VES / 50 = 2,400 USD

-- Note: Under IAS 29, all items use closing rate AFTER restatement
```

**Step 6: Create User Elimination for Net Monetary Gain**

```sql
-- Header
INSERT INTO TS070S0 (ConsoID, ElimCode, ElimType, ElimText, Active,
                     ConsoMethodSelectionID, JournalTypeID, ...)
VALUES (@ConsoID, 'U051', 'U',
    'IAS 29 Net Monetary Gain - VEN Sub - 2024 - Gain 5,000 VES = 100 USD', 1,
    4, @JournalID, ...);  -- Global only

-- Detail Line
INSERT INTO TS071S0 (EliminationHeaderID, LineNr,
    FromType, FromAccountID, ToAccountID, ToSign, ...)
VALUES (@HeaderID, 1,
    1, @PlaceholderAccount, @NetMonetaryGainPL, 1, ...);
-- Manual amount: 100 USD (5,000 VES / 50)
```

### Example 3: Comparison - Normal vs Hyperinflationary Translation

**Same Company, Different Treatment**:

| Item | Historical VES | Normal Translation (Method 1) | Hyperinflation (Method 2 + Restatement) |
|------|---------------|------------------------------|----------------------------------------|
| | | Rate | USD | Restated VES | Rate | USD |
| Fixed Assets (net) | 8,000 | Closing 50 | 160 | 120,000 | Closing 50 | 2,400 |
| Inventory | 5,000 | Closing 50 | 100 | 6,250 | Closing 50 | 125 |
| Cash | 4,000 | Closing 50 | 80 | 4,000 | Closing 50 | 80 |
| **Total Assets** | **17,000** | | **340** | **130,250** | | **2,605** |
| Share Capital | 8,000 | Historical 10 | 800 | 120,000 | Closing 50 | 2,400 |
| Retained Earnings | 1,000 | Cumulative | 140 | 2,250 | Closing 50 | 45 |
| CTA | - | Balancing | (600) | - | Closing 50 | 160 |
| **Total Equity** | **9,000** | | **340** | **122,250** | | **2,605** |

**Key Differences**:
- Method 1: Historical rate on equity → CTA on translation
- Method 2 + IAS 29: Restatement preserves purchasing power → minimal CTA

### Configuration Checklist for Hyperinflationary Subsidiary

| Step | Action | SQL/Setting | Verify |
|------|--------|-------------|--------|
| 1 | Set ConversionMethod | TS014C0.ConversionMethod = 2 | Query company config |
| 2 | Configure monetary accounts | RateType2 = 'CC', FlagHistoricalRate2 = 0 | Check TS010S0 |
| 3 | Configure non-monetary accounts | RateType2 = 'CC', FlagHistoricalRate2 = 1 | Check TS010S0 |
| 4 | Configure P&L accounts | RateType2 = 'AC', FlagHistoricalRate2 = 0 | Check TS010S0 |
| 5 | Enter restated local data | Import or data entry | Review TD030B2/TD040B2 |
| 6 | Create net monetary gain/loss elimination | TS070S0/TS071S0 | Review user elims |
| 7 | Run consolidation | Standard process | Review translated amounts |
| 8 | Verify T075 adjustments | Check historical rate journals | Review TD045C2 |

### Countries Currently Classified as Hyperinflationary (Reference)

*As of 2024, based on IPTF and major accounting firms' guidance:*

| Country | Currency | Status | Notes |
|---------|----------|--------|-------|
| Argentina | ARS | Hyperinflationary | Since 2018 |
| Venezuela | VES | Hyperinflationary | Since 2009 |
| Zimbabwe | ZWL | Hyperinflationary | Multiple periods |
| Turkey | TRY | **Monitor** | Borderline 2022-2024 |
| Sudan | SDG | Hyperinflationary | Since 2021 |
| Lebanon | LBP | Hyperinflationary | Since 2020 |
| Iran | IRR | Hyperinflationary | Long-standing |
| Haiti | HTG | **Monitor** | Approaching threshold |

**Best Practice**: Review IPTF (International Practices Task Force) quarterly updates for current classifications.

## API Reference

### Primary API Handlers
| Handler | YAML File | Purpose | Status |
|---------|-----------|---------|--------|
| `Company_SaveCompany` | [api-company-endpoints.yaml](../11-agent-support/api-company-endpoints.yaml) | Set ConversionMethod = 2 for temporal | ✅ IMPLEMENTED |
| `Account_SaveAccount` | [api-account-endpoints.yaml](../11-agent-support/api-account-endpoints.yaml) | Configure RateType2, FlagHistoricalRate2 | ✅ IMPLEMENTED |
| `Consolidation_Execute` | [api-consolidation-endpoints.yaml](../11-agent-support/api-consolidation-endpoints.yaml) | Process temporal method translation | ✅ IMPLEMENTED |

### Supporting API Handlers
| Handler | YAML File | Purpose |
|---------|-----------|---------|
| `Elimination_SaveElimination` | [api-elimination-endpoints.yaml](../11-agent-support/api-elimination-endpoints.yaml) | Configure net monetary gain/loss workaround |
| `DataEntry_SaveData` | [api-data-entry-endpoints.yaml](../11-agent-support/api-data-entry-endpoints.yaml) | Enter restated local amounts |
| `ExchangeRate_SaveExchangeRate` | [api-exchange-rate-endpoints.yaml](../11-agent-support/api-exchange-rate-endpoints.yaml) | Update closing/average rates |

### API Workflow
```
Hyperinflation Accounting via API (Manual Workaround):

1. CONFIGURE COMPANY FOR TEMPORAL METHOD
   Company_SaveCompany → Set ConversionMethod = 2:
     - Hyperinflationary subsidiary uses Method 2
     - Triggers RateType2 settings

2. CONFIGURE ACCOUNT RATE TYPES
   Account_SaveAccount → For each account:
     Monetary (Cash, Receivables, Payables):
       - RateType2 = 'CC', FlagHistoricalRate2 = 0
     Non-monetary (Inventory, Fixed Assets, Equity):
       - RateType2 = 'CC', FlagHistoricalRate2 = 1
     P&L:
       - RateType2 = 'AC', FlagHistoricalRate2 = 0

3. ENTER RESTATED DATA (External IAS 29 Calculation)
   DataEntry_SaveData → Enter IAS 29 restated amounts:
     - Non-monetary items × (Closing Index / Acquisition Index)
     - Monetary items unchanged

4. CREATE NET MONETARY GAIN/LOSS ELIMINATION
   Elimination_SaveElimination → TS070S0/TS071S0:
     - U0XX elimination for purchasing power gain/loss
     - Manual amount from external calculation

5. RUN CONSOLIDATION
   Consolidation_Execute → Process temporal translation:
     - Monetary items at closing rate
     - Non-monetary items get T075 historical adjustment
```

### Implementation Status
| Feature | Status | Gap Reference |
|---------|--------|---------------|
| Dual ConversionMethod | ✅ IMPLEMENTED | Method 1/2 per company |
| RateType2 configuration | ✅ IMPLEMENTED | Account-level |
| FlagHistoricalRate2 | ✅ IMPLEMENTED | T075 adjustments |
| Automatic IAS 29 restatement | ❌ NOT_IMPLEMENTED | Severity 8 |
| Price index table | ❌ NOT_IMPLEMENTED | External calculation |
| Acquisition date tracking | ❌ NOT_IMPLEMENTED | Manual workaround |
| Net monetary gain/loss | ❌ NOT_IMPLEMENTED | User elimination |

### Related API Documentation
- [API Index](../11-agent-support/api-index.yaml) - Master handler catalog
- [Gap Analysis](../11-agent-support/gap-analysis-report.yaml) - **PARTIAL (40%)**

---

## Related Documentation

- [Translation Methods](translation-methods.md) - ConversionMethod 1/2 details
- [Exchange Rate Types](exchange-rate-types.md) - Rate type codes
- [Translation Adjustments (CTA)](translation-adjustments.md) - CTA handling
- [User-Defined Eliminations](../04-elimination-entries/user-eliminations.md) - Workaround framework

### Related Standards
- IAS 29 - Financial Reporting in Hyperinflationary Economies
- IAS 21 - The Effects of Changes in Foreign Exchange Rates
- IFRS 1 - First-time Adoption (hyperinflation considerations)

---
*Document 34 of 50+ | Batch 12: Advanced Translation & Elimination Templates | Last Updated: 2024-12-02 (Enhanced with comprehensive temporal method examples)*
*GAP STATUS: PARTIAL - Temporal method configurable; IAS 29 restatement manual*
