# Currency Differences: Theory vs Product

## Overview

This document details how Prophix.Conso implements currency translation compared to IAS 21 and Allen White's "Direct Consolidation" framework. Understanding these differences is essential for multi-currency consolidations and audit validation of translation adjustments.

---

## Executive Summary

| Aspect | Theory (IAS 21 / Allen White) | Product (Prophix.Conso) |
|--------|------------------------------|------------------------|
| **Rate Types** | Many specific rates by account type | Four main types: CC, AC, MC, HC |
| **Translation Method** | Current rate or Temporal | Current rate method primary |
| **Functional Currency** | Detailed determination guidance | User-defined per company |
| **Hyperinflation** | Full IAS 29 restatement | Simplified adjustment approach |
| **Goodwill Translation** | Historical rate | Configurable |

---

## 1. Exchange Rate Types

### Theory (IAS 21)

IAS 21 prescribes specific rates for different balance sheet and income statement items:

| Item Type | Required Rate | Description |
|-----------|---------------|-------------|
| **Monetary Assets/Liabilities** | Closing Rate | Cash, receivables, payables |
| **Non-Monetary (Historical Cost)** | Historical Rate | Fixed assets at cost |
| **Non-Monetary (Fair Value)** | Rate at FV Date | Revalued assets |
| **Income/Expenses** | Average Rate | P&L items (approximation) |
| **Equity** | Historical Rates | Share capital, reserves |
| **Dividends** | Rate at Declaration | Dividend transactions |
| **Opening Balance** | Prior Period Closing | Brought forward |

### Product Implementation

Prophix.Conso uses **four main rate types**:

| Code | Name | Purpose |
|------|------|---------|
| **CC** | Closing Rate | End-of-period rate for monetary items |
| **AC** | Average Rate | Period average for income statement |
| **MC** | Manual Closing | Override rate for specific accounts |
| **HC** | Historical Rate | For equity and specific items |

**Storage**: Rates stored in `CurrencyRates` table per period:

```sql
CREATE TABLE CurrencyRates (
    ConsoID int,           -- Consolidation period
    CurrCode varchar(10),  -- Currency being translated
    ReferenceCurrCode varchar(10),  -- Target currency
    ClosingRate decimal,   -- CC
    AverageRate decimal,   -- AC
    AvgMonthRate decimal   -- MC (monthly average)
)
```

### Key Differences

| Aspect | Theory | Product | Gap |
|--------|--------|---------|-----|
| **Number of Rate Types** | Many per IAS 21 | Four main types | Some scenarios simplified |
| **Historical Per-Item** | Rate at transaction date | Single HC rate | May need manual tracking |
| **Fair Value Items** | Rate at FV measurement | Not automatic | Manual handling |
| **Dividend Rate** | Declaration date rate | Period rate | Approximation |

**Workaround**: Use MC (Manual Closing) rate for accounts requiring specific rates not covered by CC, AC, or HC.

---

## 2. Rate Assignment by Account

### Theory Approach

Each account should use the appropriate rate based on its nature:

```
Assets:
  Cash and Equivalents    → Closing Rate
  Receivables            → Closing Rate
  Inventory (at cost)    → Historical Rate
  Fixed Assets           → Historical Rate (cost basis)
  Intangibles            → Historical Rate

Liabilities:
  Payables               → Closing Rate
  Loans                  → Closing Rate
  Provisions             → Closing Rate

Equity:
  Share Capital          → Historical Rate
  Retained Earnings      → Historical (rolled forward)
  Other Reserves         → Various

Income Statement:
  All Items              → Average Rate (approximation)
```

### Product Implementation

**Account-Level Rate Configuration**:

Each account is assigned a rate type during setup:

**Navigation**: Configuration > Accounts

| Field | Description |
|-------|-------------|
| **Currency Rate** | CC, AC, MC, or HC |
| **Currency Rate Type** | Determines which rate applies |

**Common Configuration**:

| Account Category | Rate Type | Code |
|-----------------|-----------|------|
| Current Assets | Closing | CC |
| Fixed Assets | Historical | HC |
| Current Liabilities | Closing | CC |
| Long-term Liabilities | Closing | CC |
| Equity | Historical | HC |
| Revenue | Average | AC |
| Expenses | Average | AC |

### Key Differences

| Aspect | Theory | Product | Impact |
|--------|--------|---------|--------|
| **Granularity** | Per-transaction possible | Per-account | Less precise for mixed accounts |
| **Inventory** | Historical or NRV rate | Single rate | May need adjustment |
| **Revalued Assets** | FV date rate | HC or manual | Manual tracking needed |

---

## 3. Translation Methods

### Theory (IAS 21)

**Two main methods**:

1. **Current Rate Method** (most common):
   - All assets/liabilities at closing rate
   - Equity at historical rates
   - P&L at average rate
   - Translation difference to OCI

2. **Temporal Method** (for integrated operations):
   - Monetary items at closing rate
   - Non-monetary items at historical rates
   - P&L at average (or transaction date)
   - Translation difference to P&L

### Product Implementation

Prophix.Conso primarily implements the **Current Rate Method**:

```
Balance Sheet Translation:
  Assets/Liabilities × Closing Rate
  Equity × Historical Rate

Income Statement Translation:
  All Items × Average Rate

Translation Adjustment:
  Calculated as plug to balance
  Posted to designated reserve account
```

### Key Differences

| Aspect | Theory | Product | Gap |
|--------|--------|---------|-----|
| **Method Selection** | Current vs Temporal | Current rate primary | Limited temporal support |
| **Highly Integrated** | Temporal method | Manual adjustments | May need workaround |
| **Method per Entity** | Can vary | Consistent application | Configure carefully |

---

## 4. Translation Adjustment Calculation

### Theory Approach

Translation adjustment arises from:

1. **Opening net assets** translated at opening rate vs closing rate
2. **P&L items** translated at average rate vs closing rate
3. **Equity movements** at various rates

**Formula**:
```
Translation Adjustment =
  (Closing Net Assets × Closing Rate)
  - (Opening Net Assets × Opening Rate)
  - (P&L × Average Rate)
  - (Other Equity Movements × Transaction Rates)
```

### Product Implementation

**S075** - Translation Adjustment handling:

- Automatic calculation during consolidation
- Posted to designated translation reserve account
- Calculated as balancing figure

**Calculation Logic**:
```
For each foreign subsidiary:
  1. Translate all accounts at configured rates
  2. Calculate resulting imbalance
  3. Post difference to Translation Reserve
```

### Key Differences

| Aspect | Theory | Product | Notes |
|--------|--------|---------|-------|
| **Calculation Method** | Formula-based | Balancing figure | Usually equivalent |
| **Componentization** | May split by cause | Single amount | Less analytical detail |
| **NCI Share** | Separate NCI translation | Combined then split | Verify NCI allocation |

---

## 5. Hyperinflation (IAS 29)

### Theory Approach

For subsidiaries in hyperinflationary economies:

1. **Restate historical cost items** using general price index
2. **Apply restatement BEFORE translation**
3. **Translate restated amounts** at closing rate
4. **Recognize restatement gain/loss** in P&L

### Product Implementation

Prophix.Conso provides **simplified hyperinflation handling**:

- Manual restatement through adjustments
- No automatic price index application
- Translation after manual adjustments

### Key Differences

| Aspect | Theory | Product | Gap |
|--------|--------|---------|-----|
| **Price Index Application** | Automatic | Manual | Significant gap |
| **Restatement Calculation** | Per IAS 29 | User-determined | Manual process |
| **Gain/Loss Recognition** | Automatic | Manual journal | Requires user action |

**Workaround**:
1. Calculate restatement entries manually
2. Post adjustment journals (Adjustments > Journal Entry)
3. Document methodology for audit

---

## 6. Goodwill Translation

### Theory (IAS 21.47)

Goodwill arising on acquisition of foreign operation:
- Treat as **asset of foreign operation**
- Translate at **closing rate** each period
- Translation difference to **OCI**

### Product Implementation

Configurable approach:
- Can configure goodwill account to use CC (closing) or HC (historical)
- Default typically historical

### Key Differences

| Aspect | Theory | Product | Notes |
|--------|--------|---------|-------|
| **Default Treatment** | Closing rate | Configurable | Verify account setup |
| **Translation Difference** | To OCI | To translation reserve | Same effect |
| **Impairment** | Also translated | Manual process | Verify handling |

**Best Practice**: Configure goodwill accounts to use CC (closing) rate per IAS 21.

---

## 7. User Interface: Exchange Rates

**Navigation**: Group > Exchange Rates

### Rate Entry Screen

| Field | Description |
|-------|-------------|
| **Period Code** | Consolidation period |
| **Currency** | Currency being translated |
| **Close** | Closing rate (CC) |
| **Average** | Average rate (AC) |
| **Month** | Monthly/manual rate (MC) |

### Import Options

**Navigation**: Transfers > Exchange Rates > Import

| Source | Description |
|--------|-------------|
| **CSV** | Custom file format |
| **Excel** | Spreadsheet import |
| **ECB** | European Central Bank SDMX |
| **NBS** | National Bank of Slovakia SDMX |

### Reports

**Navigation**: Group > Exchange Rates > Reports tab

| Report | Content |
|--------|---------|
| **Standard** | All rates for period |
| **Reporting** | Rates vs reporting currency |
| **Statutory** | Rates by company |

---

## 8. Practical Implications

### For Consultants

1. **During Implementation**:
   - Map all accounts to appropriate rate types
   - Configure translation reserve account
   - Set up rate import automation if possible
   - Document hyperinflation procedures if applicable

2. **Training Users**:
   - Explain rate type meanings (CC, AC, MC, HC)
   - Train on rate entry/import
   - Document account-rate mapping rationale

### For Auditors

1. **Verification Points**:
   - Verify account-rate type mapping
   - Recalculate sample translations manually
   - Verify translation adjustment to OCI
   - Check goodwill translation treatment

2. **Common Issues**:
   - Incorrect rate type assignment
   - Missing rates causing zero translation
   - Goodwill using wrong rate
   - Hyperinflation not properly restated

### For Consolidators

1. **Period-End Tasks**:
   - Enter/import exchange rates
   - Verify rates for reasonableness
   - Review translation adjustment
   - Reconcile translation reserve

2. **Documentation**:
   - Source of exchange rates
   - Any manual rate adjustments
   - Hyperinflation calculations

---

## 9. Frequently Asked Questions

**Q: Why doesn't my translation adjustment match my manual calculation?**
A: Check account-rate type mappings. The product calculates translation as a balancing figure based on configured rates per account.

**Q: Can I use different rates for the same account type?**
A: Use the MC (Manual Closing) rate type for accounts requiring specific rates. Override at account level.

**Q: How do I handle temporal method for integrated operations?**
A: Manual configuration required. Set appropriate accounts to HC (historical) and manage translation differences through adjustment journals.

**Q: Where does the translation adjustment post?**
A: To the designated translation reserve account. Configure in account setup.

**Q: How do I import rates automatically?**
A: Use Transfers > Exchange Rates > Import with ECB or NBS SDMX feeds, or custom CSV/Excel files.

---

## Related Documentation

- [Theory vs Product Overview](theory-vs-product-overview.md)
- [Elimination Differences](elimination-differences.md)
- [Help: Input Currency Rates](../help-content/0303-input-the-currency-rates.md)
- [Technical: Translation Adjustments](../../05-currency-translation/translation-adjustments.md)
- [Technical: Hyperinflation](../../05-currency-translation/hyperinflation-accounting.md)

---

*Currency Differences | Version 1.0 | Last Updated: 2024-12-03*
