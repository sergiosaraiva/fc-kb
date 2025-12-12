# Troubleshooting Guide: Common Issues and Solutions

## Document Metadata
- **Document Type**: Troubleshooting Reference
- **Purpose**: Self-service issue resolution for implementation teams
- **Categories**: Ownership, Eliminations, Currency, Data Entry, Performance
- **Last Updated**: 2024-12-02
- **Version**: 1.1 (Final)

---

## Quick Diagnostic Checklist

Before diving into specific issues, verify these common prerequisites:

| Check | How to Verify | Common Fix |
|-------|---------------|------------|
| Consolidation status | Check TD000S0.ConsoStatus | Re-run consolidation |
| Period lock status | Check TS001S0.FlagLocked | Unlock period for edits |
| Ownership data complete | Query TS015S0 for gaps | Add missing ownership links |
| Exchange rates loaded | Check TS017R0 for period | Import missing rates |
| Data imported | Check TD030B2/TD040B2 counts | Run data import |

---

## 1. Ownership Calculation Issues

### Issue 1.1: Circular Ownership Not Resolving

**Symptoms**:
- Consolidation hangs or times out during ownership calculation
- Error message: "Maximum iterations exceeded"
- Percentages show as NULL or 0

**Root Causes**:
1. Circular chain too complex (>10 companies in loop)
2. Missing ownership link creating incomplete circle
3. Ownership percentages sum to >100% for a company

**Diagnostic Query**:
```sql
-- Find circular ownership chains
SELECT a.CompanyID, a.CompanyOwnedID, a.FinPercentage, a.CtrlPercentage
FROM TS015S0 a
INNER JOIN TS015S0 b ON a.CompanyOwnedID = b.CompanyID
WHERE a.ConsoID = @ConsoID
  AND b.CompanyOwnedID = a.CompanyID
ORDER BY a.CompanyID;

-- Check for >100% total ownership
SELECT CompanyOwnedID, SUM(FinPercentage) as TotalOwnership
FROM TS015S0
WHERE ConsoID = @ConsoID
GROUP BY CompanyOwnedID
HAVING SUM(FinPercentage) > 100;
```

**Solutions**:

| Solution | When to Use | Steps |
|----------|-------------|-------|
| **Verify ownership data** | Data entry error suspected | Review TS015S0 entries for the circular chain |
| **Increase iteration limit** | Complex valid structure | Modify procedure parameter (advanced) |
| **Simplify structure** | Non-essential circularity | Remove redundant cross-holdings |

**Resolution Steps**:
1. Run diagnostic query to identify circular chains
2. Verify each ownership link is correct and complete
3. Check that percentages are accurate (not reversed)
4. If valid complex structure, monitor Gauss elimination convergence

**Related Documentation**: [Circular Ownership](../03-core-calculations/circular-ownership.md)

---

### Issue 1.2: Calculated Percentages Don't Match Expected

**Symptoms**:
- Group control percentage different from manual calculation
- Financial percentage differs from control percentage unexpectedly
- Minority interest allocation incorrect

**Root Causes**:
1. Direct vs indirect ownership path differences
2. Voting rights differ from financial rights
3. Treasury shares affecting effective ownership
4. Multi-path ownership not summing correctly

**Diagnostic Query**:
```sql
-- Compare direct vs calculated indirect percentages
SELECT
    c.CompanyCode,
    c.DirectFinPerc,
    c.GroupFinPerc,
    c.DirectCtrlPerc,
    c.GroupCtrlPerc,
    c.ConsoMethod
FROM TS014C0 c
WHERE c.ConsoID = @ConsoID
ORDER BY c.CompanyCode;

-- Check ownership paths
SELECT
    owner.CompanyCode AS Owner,
    owned.CompanyCode AS Owned,
    s.FinPercentage,
    s.CtrlPercentage
FROM TS015S0 s
INNER JOIN TS014C0 owner ON s.CompanyID = owner.CompanyID AND s.ConsoID = owner.ConsoID
INNER JOIN TS014C0 owned ON s.CompanyOwnedID = owned.CompanyID AND s.ConsoID = owned.ConsoID
WHERE s.ConsoID = @ConsoID
ORDER BY owner.CompanyCode, owned.CompanyCode;
```

**Solutions**:

| Scenario | Cause | Solution |
|----------|-------|----------|
| Direct % correct, Group % wrong | Missing indirect path | Add intermediate ownership links |
| Group % too high | Duplicate paths not normalized | Check for duplicate TS015S0 entries |
| Control % ≠ Financial % | Voting rights differ | Verify CtrlPercentage entries separately |
| Method wrong despite % | Threshold configuration | Check T_CONFIG for method thresholds |

**Calculation Verification**:
```
For multi-tier: P → A (80%) → B (60%)
  P's indirect in B = 80% × 60% = 48%

For multi-path: P → A (40%), P → B (30%), B → A (50%)
  P's direct in A = 40%
  P's indirect via B = 30% × 50% = 15%
  P's total in A = 40% + 15% = 55%
```

**Related Documentation**: [Multi-tier Holdings](../06-ownership-structure/multi-tier-holdings.md), [Ownership Percentages](../06-ownership-structure/ownership-percentages.md)

---

### Issue 1.3: Consolidation Method Assignment Incorrect

**Symptoms**:
- Company shown as Equity (E) when should be Global (G)
- Proportional (P) method applied unexpectedly
- Company excluded (N) when should be consolidated

**Root Causes**:
1. Control percentage below threshold
2. CONSO_NO_PROPORTIONAL configuration
3. Manual ConsoMethod override in TS014C0
4. Joint control not properly identified

**Diagnostic Query**:
```sql
-- Check method determination factors
SELECT
    c.CompanyCode,
    c.GroupCtrlPerc,
    c.ConsoMethod,
    CASE
        WHEN c.GroupCtrlPerc > 50 THEN 'G (Expected)'
        WHEN c.GroupCtrlPerc = 50 THEN 'P (Expected)'
        WHEN c.GroupCtrlPerc >= 20 THEN 'E (Expected)'
        ELSE 'N (Expected)'
    END AS ExpectedMethod
FROM TS014C0 c
WHERE c.ConsoID = @ConsoID
  AND c.ConsoMethod != CASE
        WHEN c.GroupCtrlPerc > 50 THEN 'G'
        WHEN c.GroupCtrlPerc = 50 THEN 'P'
        WHEN c.GroupCtrlPerc >= 20 THEN 'E'
        ELSE 'N'
    END;

-- Check proportional configuration
SELECT ConfigName, ConfigValue
FROM T_CONFIG
WHERE ConfigName = 'CONSO_NO_PROPORTIONAL';
```

**Solutions**:

| Mismatch | Cause | Solution |
|----------|-------|----------|
| E when should be G | Control <50% | Verify voting rights vs financial rights |
| N when should be E | Control <20% | Check if control threshold configured differently |
| No P method used | CONSO_NO_PROPORTIONAL = 1 | Disable if proportional needed |
| Manual override | Previous manual setting | Clear ConsoMethod and recalculate |

**Related Documentation**: [Method Determination](../02-consolidation-methods/consolidation-method-determination.md)

---

## 2. Elimination Issues

### Issue 2.1: Dividend Elimination Not Working

**Symptoms**:
- Intercompany dividends showing in consolidated P&L
- Dividend received not offset by dividend paid
- S020 elimination journal missing or incomplete

**Root Causes**:
1. Dividend accounts not configured in special accounts
2. Partner company not identified for IC matching
3. Ownership percentage not set for dividend calculation
4. Period mismatch between dividend declaration and receipt

**Diagnostic Query**:
```sql
-- Check dividend account configuration
SELECT * FROM TS012S1
WHERE ConsoID = @ConsoID
  AND SpecAccountCode IN ('DivReceived', 'DivPaid', 'DivReceivedEquity');

-- Check dividend elimination journal
SELECT
    j.JournalTypeCode,
    d.AccountCode,
    d.CompanyCode,
    d.PartnerCode,
    d.AmountLC,
    d.AmountGC
FROM TD045C2 d
INNER JOIN TS020S0 j ON d.JournalTypeID = j.JournalTypeID
WHERE d.ConsoID = @ConsoID
  AND j.JournalTypeCode = 'S020'
ORDER BY d.CompanyCode;

-- Find uneliminated dividends
SELECT
    c.CompanyCode,
    a.AccountCode,
    SUM(d.AmountGC) as TotalDividend
FROM TD035C2 d
INNER JOIN TS014C0 c ON d.CompanyID = c.CompanyID AND d.ConsoID = c.ConsoID
INNER JOIN TS010S0 a ON d.AccountID = a.AccountID AND d.ConsoID = a.ConsoID
WHERE d.ConsoID = @ConsoID
  AND a.AccountCode IN (SELECT AccountCode FROM TS012S1 WHERE SpecAccountCode = 'DivReceived')
GROUP BY c.CompanyCode, a.AccountCode
HAVING SUM(d.AmountGC) != 0;
```

**Solutions**:

| Issue | Diagnostic | Solution |
|-------|------------|----------|
| No S020 journal created | SpecAccount not configured | Configure DivReceived/DivPaid in TS012S1 |
| Partial elimination | FinPercentage incorrect | Verify ownership % in TS015S0 |
| Wrong partner matching | PartnerID not set | Set PartnerID on dividend data entries |
| Equity method dividend | Using wrong account | Use DivReceivedEquity for E method |

**4-Line Journal Pattern Verification**:
```
Expected S020 elimination structure:
  Line 1: Dr  DivReceived (receiving company)
  Line 2: Cr  DivPaid (paying company)
  Line 3: Dr  P&L Reserves adjustment
  Line 4: Cr  B/S Reserves adjustment

If any line missing, check account mapping in TS012S1
```

**Related Documentation**: [Dividend Eliminations](../04-elimination-entries/dividend-eliminations.md), [Dividend Calculation Logic](../04-elimination-entries/dividend-calculation-logic.md)

---

### Issue 2.2: Participation Elimination Out of Balance

**Symptoms**:
- S050-S054 journals not balancing
- Investment account not fully eliminated
- Goodwill calculation incorrect
- NCI calculation incorrect

**Root Causes**:
1. Investment account balance incorrect
2. Subsidiary equity accounts incomplete
3. Fair value adjustments missing
4. Acquisition date reserves incorrect

**Diagnostic Query**:
```sql
-- Check participation elimination balance
SELECT
    j.JournalTypeCode,
    SUM(CASE WHEN d.AmountGC > 0 THEN d.AmountGC ELSE 0 END) as Debits,
    SUM(CASE WHEN d.AmountGC < 0 THEN ABS(d.AmountGC) ELSE 0 END) as Credits,
    SUM(d.AmountGC) as NetBalance
FROM TD045C2 d
INNER JOIN TS020S0 j ON d.JournalTypeID = j.JournalTypeID
WHERE d.ConsoID = @ConsoID
  AND j.JournalTypeCode LIKE 'S05%'
GROUP BY j.JournalTypeCode;

-- Check investment vs equity
SELECT
    'Investment' as Type,
    c.CompanyCode as Investor,
    s.CompanyCode as Investee,
    d.AmountGC as Amount
FROM TD035C2 d
INNER JOIN TS014C0 c ON d.CompanyID = c.CompanyID
INNER JOIN TS010S0 a ON d.AccountID = a.AccountID
INNER JOIN TS012S1 sp ON a.AccountID = sp.AccountID AND sp.SpecAccountCode = 'ParticipationAccount'
LEFT JOIN TS014C0 s ON d.PartnerID = s.CompanyID
WHERE d.ConsoID = @ConsoID

UNION ALL

SELECT
    'Equity' as Type,
    '' as Investor,
    c.CompanyCode as Investee,
    SUM(d.AmountGC) as Amount
FROM TD035C2 d
INNER JOIN TS014C0 c ON d.CompanyID = c.CompanyID
INNER JOIN TS010S0 a ON d.AccountID = a.AccountID
WHERE d.ConsoID = @ConsoID
  AND a.FlagEquity = 1
GROUP BY c.CompanyCode;
```

**Solutions**:

| Imbalance | Likely Cause | Solution |
|-----------|--------------|----------|
| Investment > Equity × % | Goodwill exists | Verify goodwill calculation correct |
| Investment < Equity × % | Negative goodwill or error | Check for bargain purchase or data error |
| NCI incorrect | Ownership % wrong | Verify GroupFinPerc in TS014C0 |
| Multiple years differ | Opening balance issue | Check S001 opening balance carry-forward |

**Related Documentation**: [Participation Eliminations](../04-elimination-entries/participation-eliminations.md), [Goodwill Calculation](../03-core-calculations/goodwill-calculation.md)

---

### Issue 2.3: Intercompany Netting Not Complete

**Symptoms**:
- IC receivables/payables still showing in consolidated balance
- IC revenue/expense not eliminated
- S030 elimination partial or missing

**Root Causes**:
1. Partner company not specified on transactions
2. IC accounts not flagged for elimination
3. IC amounts don't match between partners
4. Currency translation differences on IC balances

**Diagnostic Query**:
```sql
-- Find unmatched intercompany balances
SELECT
    c1.CompanyCode as Company1,
    c2.CompanyCode as Company2,
    a.AccountCode,
    SUM(CASE WHEN d.CompanyID = c1.CompanyID THEN d.AmountGC ELSE 0 END) as Company1Amount,
    SUM(CASE WHEN d.CompanyID = c2.CompanyID THEN d.AmountGC ELSE 0 END) as Company2Amount,
    SUM(d.AmountGC) as Difference
FROM TD035C2 d
INNER JOIN TS014C0 c1 ON d.CompanyID = c1.CompanyID
INNER JOIN TS014C0 c2 ON d.PartnerID = c2.CompanyID
INNER JOIN TS010S0 a ON d.AccountID = a.AccountID
WHERE d.ConsoID = @ConsoID
  AND a.FlagInterCompany = 1
  AND d.PartnerID IS NOT NULL
GROUP BY c1.CompanyCode, c2.CompanyCode, a.AccountCode
HAVING SUM(d.AmountGC) != 0
ORDER BY ABS(SUM(d.AmountGC)) DESC;

-- Check IC account configuration
SELECT AccountCode, FlagInterCompany, ICAccountID
FROM TS010S0
WHERE ConsoID = @ConsoID
  AND FlagInterCompany = 1;
```

**Solutions**:

| Issue | Diagnostic | Solution |
|-------|------------|----------|
| No partner set | PartnerID is NULL | Add partner on IC transactions |
| Not flagged IC | FlagInterCompany = 0 | Configure account as intercompany |
| Amounts differ | FX translation | Add TRANSADJ flow for IC FX difference |
| Wrong IC pair | ICAccountID misconfigured | Verify IC account mapping |

**IC Matching Checklist**:
```
□ IC receivable has ICAccountID pointing to IC payable
□ IC payable has ICAccountID pointing to IC receivable
□ Both accounts have FlagInterCompany = 1
□ Transactions have PartnerID populated
□ Amounts match after currency translation
```

**Related Documentation**: [Intercompany Transactions](../04-elimination-entries/intercompany-transactions.md)

---

### Issue 2.4: User Elimination Not Executing

**Symptoms**:
- Custom U### elimination not appearing in results
- User elimination shows 0 amounts
- Selection criteria not matching expected companies

**Root Causes**:
1. Elimination header inactive (Active = 0)
2. Selection criteria not matching any companies
3. FromAccount has no balance in selected period
4. Percentage type not appropriate for data

**Diagnostic Query**:
```sql
-- Check user elimination configuration
SELECT
    h.ElimCode,
    h.ElimText,
    h.Active,
    h.ConsoMethodSelectionID,
    s.SelectionName,
    d.LineNr,
    d.FromType,
    fa.AccountCode as FromAccount,
    ta.AccountCode as ToAccount,
    d.ToSign,
    d.Percentage
FROM TS070S0 h
INNER JOIN TS070S1 s ON h.ConsoMethodSelectionID = s.SelectionID
LEFT JOIN TS071S0 d ON h.EliminationHeaderID = d.EliminationHeaderID
LEFT JOIN TS010S0 fa ON d.FromAccountID = fa.AccountID
LEFT JOIN TS010S0 ta ON d.ToAccountID = ta.AccountID
WHERE h.ConsoID = @ConsoID
  AND h.ElimCode = 'U###'  -- Replace with actual code
ORDER BY d.LineNr;

-- Check if selection matches companies
SELECT
    c.CompanyCode,
    c.ConsoMethod,
    c.FlagEnteringScope,
    c.FlagLeavingScope
FROM TS014C0 c
WHERE c.ConsoID = @ConsoID
  AND (
    -- Selection ID 1 = All companies
    1 = 1
    -- Add appropriate selection criteria
  );
```

**Solutions**:

| Issue | Diagnostic | Solution |
|-------|------------|----------|
| Active = 0 | Elimination disabled | Set Active = 1 in TS070S0 |
| Selection empty | Wrong ConsoMethodSelectionID | Change to appropriate selection |
| FromAccount no balance | Wrong account or period | Verify FromAccountID and FromPeriod |
| Percentage = 0 | Config error | Set appropriate percentage value |

**User Elimination Verification Steps**:
1. Check header is Active = 1
2. Verify ConsoMethodSelectionID matches target companies
3. Confirm FromAccountID has balance in FromPeriod
4. Test with manual amount (FromType = 0) first
5. Check JournalTypeID assignment

**Related Documentation**: [User Eliminations](../04-elimination-entries/user-eliminations.md), [Elimination Templates](../04-elimination-entries/elimination-templates.md)

---

## 3. Currency Translation Issues

### Issue 3.1: CTA (Cumulative Translation Adjustment) Unexpected Value

**Symptoms**:
- Large unexpected CTA balance
- CTA grows disproportionately each period
- CTA doesn't match manual calculation

**Root Causes**:
1. Incorrect rate type assigned to accounts
2. Historical rate not applied to equity accounts
3. Average rate used for B/S items
4. Opening balance translation difference

**Diagnostic Query**:
```sql
-- Check account rate type configuration
SELECT
    a.AccountCode,
    a.AccountText,
    a.RateType1,
    a.RateType2,
    a.FlagHistoricalRate1,
    a.FlagHistoricalRate2,
    a.FlagEquity,
    a.FlagPL
FROM TS010S0 a
WHERE a.ConsoID = @ConsoID
ORDER BY a.AccountCode;

-- Check exchange rates used
SELECT
    r.CurrCode,
    r.RateType,
    r.ExchangeRate,
    r.PeriodID
FROM TS017R0 r
WHERE r.ConsoID = @ConsoID
  AND r.PeriodID = @PeriodID
ORDER BY r.CurrCode, r.RateType;

-- Analyze CTA by company
SELECT
    c.CompanyCode,
    c.CurrCode,
    SUM(CASE WHEN f.FlowCode = 'TRANSADJ' THEN d.AmountGC ELSE 0 END) as CTA
FROM TD035C2 d
INNER JOIN TS014C0 c ON d.CompanyID = c.CompanyID
INNER JOIN TS011C0 f ON d.FlowID = f.FlowID
WHERE d.ConsoID = @ConsoID
  AND f.FlowCode = 'TRANSADJ'
GROUP BY c.CompanyCode, c.CurrCode
ORDER BY ABS(SUM(d.AmountGC)) DESC;
```

**Solutions**:

| CTA Issue | Likely Cause | Solution |
|-----------|--------------|----------|
| Too large | B/S items at average rate | Change RateType to CC (closing) |
| Keeps growing | Historical rates not used | Set FlagHistoricalRate1 = 1 for equity |
| Opening difference | Prior period not translated | Check S001 opening balance translation |
| Sign wrong | Positive/negative convention | Verify TRANSADJ account sign |

**Rate Type Guidance**:
```
Balance Sheet Items:
  - Monetary assets/liabilities: CC (Closing Current)
  - Non-monetary items: CC or Historical (depends on policy)
  - Equity items: Historical (FlagHistoricalRate1 = 1)

P&L Items:
  - Generally: AC (Average Current)
  - Or: MC (Monthly Cumulative) for progressive

CTA should capture:
  - Rate change effect on B/S items
  - Average vs closing difference on P&L
  - NOT equity at historical vs current
```

**Related Documentation**: [Translation Adjustments](../05-currency-translation/translation-adjustments.md), [Exchange Rate Types](../05-currency-translation/exchange-rate-types.md)

---

### Issue 3.2: Historical Rates Not Applied

**Symptoms**:
- Equity items translating at closing rate
- Share capital changing each period
- T075 adjustment journals missing

**Root Causes**:
1. FlagHistoricalRate not set on accounts
2. Historical rate not loaded in TS017R0
3. ConversionMethod not set correctly for company

**Diagnostic Query**:
```sql
-- Check historical rate configuration
SELECT
    a.AccountCode,
    a.FlagHistoricalRate1,
    a.FlagHistoricalRate2,
    a.FlagEquity
FROM TS010S0 a
WHERE a.ConsoID = @ConsoID
  AND a.FlagEquity = 1;

-- Check for T075 historical rate adjustments
SELECT
    j.JournalTypeCode,
    c.CompanyCode,
    a.AccountCode,
    d.AmountGC
FROM TD045C2 d
INNER JOIN TS020S0 j ON d.JournalTypeID = j.JournalTypeID
INNER JOIN TS014C0 c ON d.CompanyID = c.CompanyID
INNER JOIN TS010S0 a ON d.AccountID = a.AccountID
WHERE d.ConsoID = @ConsoID
  AND j.JournalTypeCode = 'T075'
ORDER BY c.CompanyCode, a.AccountCode;

-- Check company conversion method
SELECT CompanyCode, ConversionMethod, CurrCode
FROM TS014C0
WHERE ConsoID = @ConsoID
  AND CurrCode != @GroupCurrency;
```

**Solutions**:

| Issue | Solution |
|-------|----------|
| FlagHistoricalRate1 = 0 | Set to 1 for equity accounts |
| No T075 journals | Check P_CONSO_BUNDLE_INTEGRATION_CURRENCY_TRANSLATION_HISTORICAL |
| Wrong ConversionMethod | Set Method 1 or 2 as appropriate |

**Related Documentation**: [Translation Methods](../05-currency-translation/translation-methods.md), [Hyperinflation Accounting](../05-currency-translation/hyperinflation-accounting.md)

---

### Issue 3.3: Exchange Rates Missing or Incorrect

**Symptoms**:
- Error: "Exchange rate not found"
- Amounts translating as 0
- Local currency amounts correct, group currency wrong

**Diagnostic Query**:
```sql
-- Find missing exchange rates
SELECT DISTINCT
    c.CurrCode,
    @PeriodID as PeriodNeeded,
    'CC' as RateTypeNeeded
FROM TS014C0 c
WHERE c.ConsoID = @ConsoID
  AND c.CurrCode != @GroupCurrency
  AND NOT EXISTS (
    SELECT 1 FROM TS017R0 r
    WHERE r.ConsoID = @ConsoID
      AND r.CurrCode = c.CurrCode
      AND r.PeriodID = @PeriodID
      AND r.RateType = 'CC'
  );

-- Check rate values
SELECT
    CurrCode,
    RateType,
    ExchangeRate,
    PeriodID
FROM TS017R0
WHERE ConsoID = @ConsoID
  AND PeriodID = @PeriodID
ORDER BY CurrCode, RateType;
```

**Solutions**:

| Issue | Solution |
|-------|----------|
| Rate missing | Import rates for period via data entry |
| Rate = 0 | Correct rate value in TS017R0 |
| Rate inverted | Check if rate is Currency/Group or Group/Currency |
| Wrong period | Ensure rate exists for consolidation period |

**Required Rate Types**:
```
Minimum required per currency per period:
  - CC (Closing Current) - for B/S items
  - AC (Average Current) - for P&L items

Optional:
  - CR (Closing Reference) - for prior period comparison
  - AR (Average Reference) - for prior period P&L
  - MC (Monthly Cumulative) - for progressive translation
```

**Related Documentation**: [Exchange Rate Types](../05-currency-translation/exchange-rate-types.md)

---

## 4. Data Entry Issues

### Issue 4.1: Import Fails with Validation Errors

**Symptoms**:
- Import job fails with error messages
- Data partially imported
- Validation helper shows errors

**Common Validation Errors**:

| Error | Cause | Solution |
|-------|-------|----------|
| "Account not found" | AccountCode doesn't exist | Add account to TS010S0 or correct code |
| "Company not found" | CompanyCode doesn't exist | Add company to TS014C0 or correct code |
| "Period not found" | PeriodID invalid | Check TS001S0 for valid periods |
| "Invalid amount format" | Non-numeric data | Clean data before import |
| "Duplicate key" | Same record exists | Delete existing or use update mode |

**Diagnostic Query**:
```sql
-- Check import job status
SELECT
    JobID,
    JobStatus,
    ErrorMessage,
    StartTime,
    EndTime
FROM T_IMPORT_JOB
WHERE ConsoID = @ConsoID
ORDER BY StartTime DESC;

-- Find invalid account references
SELECT DISTINCT SourceAccountCode
FROM T_IMPORT_STAGING
WHERE ConsoID = @ConsoID
  AND SourceAccountCode NOT IN (
    SELECT AccountCode FROM TS010S0 WHERE ConsoID = @ConsoID
  );
```

**Pre-Import Checklist**:
```
□ All company codes exist in TS014C0
□ All account codes exist in TS010S0
□ Period is valid and unlocked
□ File format matches expected template
□ Amounts are numeric (no text)
□ Required fields are populated
```

**Related Documentation**: [Data Import Services](../08-application-layer/data-import-services.md), [Data Entry Screens](../09-frontend-implementation/data-entry-screens.md)

---

### Issue 4.2: Data Not Showing After Import

**Symptoms**:
- Import completed successfully
- No data visible in reports
- Data exists in staging but not in target

**Root Causes**:
1. Import to staging only (not processed)
2. Wrong period selected
3. Wrong company selected
4. Data in local currency only (no translation)

**Diagnostic Query**:
```sql
-- Check staging vs target data
SELECT
    'Staging' as Source,
    COUNT(*) as RecordCount
FROM T_IMPORT_STAGING
WHERE ConsoID = @ConsoID
  AND PeriodID = @PeriodID

UNION ALL

SELECT
    'Target TD030B2' as Source,
    COUNT(*) as RecordCount
FROM TD030B2
WHERE ConsoID = @ConsoID
  AND PeriodID = @PeriodID

UNION ALL

SELECT
    'Target TD040B2' as Source,
    COUNT(*) as RecordCount
FROM TD040B2
WHERE ConsoID = @ConsoID
  AND PeriodID = @PeriodID;

-- Check data by company
SELECT
    c.CompanyCode,
    COUNT(*) as RecordCount,
    SUM(d.AmountLC) as TotalLC
FROM TD030B2 d
INNER JOIN TS014C0 c ON d.CompanyID = c.CompanyID
WHERE d.ConsoID = @ConsoID
  AND d.PeriodID = @PeriodID
GROUP BY c.CompanyCode;
```

**Solutions**:

| Issue | Diagnostic | Solution |
|-------|------------|----------|
| In staging only | Check T_IMPORT_STAGING | Run import processing step |
| Wrong period | Check PeriodID in data | Re-import with correct period |
| No translation | AmountGC = 0 | Run consolidation to translate |
| Wrong company view | Check CompanyID filter | Select correct company in UI |

---

### Issue 4.3: Balance Sheet Doesn't Balance

**Symptoms**:
- Assets ≠ Liabilities + Equity
- Trial balance out of balance
- Validation shows balance error

**Root Causes**:
1. Incomplete data import
2. Rounding differences
3. Unclassified accounts
4. Translation timing differences

**Diagnostic Query**:
```sql
-- Check balance by account type
SELECT
    CASE
        WHEN a.AccountCode LIKE '1%' THEN 'Assets'
        WHEN a.AccountCode LIKE '2%' THEN 'Liabilities'
        WHEN a.AccountCode LIKE '3%' THEN 'Equity'
        WHEN a.AccountCode LIKE '4%' OR a.AccountCode LIKE '5%'
             OR a.AccountCode LIKE '6%' OR a.AccountCode LIKE '7%' THEN 'P&L'
        ELSE 'Other'
    END as AccountType,
    SUM(d.AmountGC) as TotalGC
FROM TD035C2 d
INNER JOIN TS010S0 a ON d.AccountID = a.AccountID
WHERE d.ConsoID = @ConsoID
  AND d.PeriodID = @PeriodID
GROUP BY
    CASE
        WHEN a.AccountCode LIKE '1%' THEN 'Assets'
        WHEN a.AccountCode LIKE '2%' THEN 'Liabilities'
        WHEN a.AccountCode LIKE '3%' THEN 'Equity'
        WHEN a.AccountCode LIKE '4%' OR a.AccountCode LIKE '5%'
             OR a.AccountCode LIKE '6%' OR a.AccountCode LIKE '7%' THEN 'P&L'
        ELSE 'Other'
    END;

-- Find unbalanced companies
SELECT
    c.CompanyCode,
    SUM(d.AmountGC) as NetBalance
FROM TD035C2 d
INNER JOIN TS014C0 c ON d.CompanyID = c.CompanyID
WHERE d.ConsoID = @ConsoID
  AND d.PeriodID = @PeriodID
GROUP BY c.CompanyCode
HAVING ABS(SUM(d.AmountGC)) > 0.01;
```

**Solutions**:

| Imbalance | Solution |
|-----------|----------|
| Small (< 1) | Rounding - accept or add adjustment |
| Large | Check for missing data or accounts |
| One company | Focus on that company's import |
| After translation | Check CTA account classification |

---

## 5. Performance Issues

### Issue 5.1: Consolidation Running Slowly

**Symptoms**:
- Consolidation takes hours instead of minutes
- Progress bar stuck on certain phase
- Timeout errors

**Root Causes**:
1. Large data volume
2. Missing indexes
3. Complex ownership structure
4. Too many elimination iterations

**Diagnostic Steps**:

```sql
-- Check data volume
SELECT
    'TD030B2' as TableName, COUNT(*) as Rows FROM TD030B2 WHERE ConsoID = @ConsoID
UNION ALL
SELECT 'TD040B2', COUNT(*) FROM TD040B2 WHERE ConsoID = @ConsoID
UNION ALL
SELECT 'TD035C2', COUNT(*) FROM TD035C2 WHERE ConsoID = @ConsoID
UNION ALL
SELECT 'TD045C2', COUNT(*) FROM TD045C2 WHERE ConsoID = @ConsoID;

-- Check company count
SELECT COUNT(*) as CompanyCount
FROM TS014C0
WHERE ConsoID = @ConsoID
  AND ConsoMethod IN ('G', 'P', 'E');

-- Check elimination count
SELECT
    j.JournalTypeCode,
    COUNT(*) as EntryCount
FROM TD045C2 d
INNER JOIN TS020S0 j ON d.JournalTypeID = j.JournalTypeID
WHERE d.ConsoID = @ConsoID
GROUP BY j.JournalTypeCode
ORDER BY COUNT(*) DESC;
```

**Performance Guidelines**:

| Metric | Acceptable | Slow | Very Slow |
|--------|------------|------|-----------|
| Companies | <100 | 100-500 | >500 |
| Data rows | <100K | 100K-1M | >1M |
| Eliminations | <10K | 10K-100K | >100K |
| Circular chains | <5 deep | 5-10 deep | >10 deep |

**Optimization Solutions**:

| Issue | Solution |
|-------|----------|
| Large data | Archive historical, use period-specific views |
| Missing indexes | Run index maintenance, check ConsoID-first indexes |
| Complex ownership | Simplify circular chains where possible |
| Many eliminations | Review user eliminations for efficiency |

**Related Documentation**: [Consolidation Workflow](../03-core-calculations/consolidation-workflow.md), [Index Strategy](../07-database-implementation/index-strategy.md)

---

### Issue 5.2: Timeout Errors During Processing

**Symptoms**:
- "Operation timed out" error
- Partial completion
- Job shows as failed

**Solutions**:

| Timeout Location | Solution |
|------------------|----------|
| Ownership calculation | Increase procedure timeout, check circular ownership |
| Currency translation | Process companies in batches |
| Eliminations | Review user elimination complexity |
| Data import | Split import into smaller files |

**Timeout Configuration**:
```sql
-- Check current timeout settings
SELECT ConfigName, ConfigValue
FROM T_CONFIG
WHERE ConfigName LIKE '%TIMEOUT%';

-- Extend timeout for specific operations (if permitted)
UPDATE T_CONFIG
SET ConfigValue = '600'  -- 10 minutes
WHERE ConfigName = 'CONSO_TIMEOUT_SECONDS';
```

---

### Issue 5.3: Memory Issues During Consolidation

**Symptoms**:
- "Out of memory" error
- Application crashes
- Server becomes unresponsive

**Root Causes**:
1. TMP_* tables growing too large
2. Session not cleaned up
3. Multiple concurrent consolidations
4. Large report generation

**Diagnostic Query**:
```sql
-- Check temp table sizes
SELECT
    t.name AS TableName,
    p.rows AS RowCount,
    SUM(a.total_pages) * 8 / 1024 AS SizeMB
FROM sys.tables t
INNER JOIN sys.partitions p ON t.object_id = p.object_id
INNER JOIN sys.allocation_units a ON p.partition_id = a.container_id
WHERE t.name LIKE 'TMP_%'
GROUP BY t.name, p.rows
ORDER BY SUM(a.total_pages) DESC;

-- Check active sessions
SELECT
    SessionID,
    UserID,
    CreateDate,
    LastActivityDate
FROM T_SESSION
WHERE CreateDate > DATEADD(hour, -24, GETDATE())
ORDER BY CreateDate DESC;
```

**Solutions**:

| Issue | Solution |
|-------|----------|
| TMP tables large | Clean up orphaned sessions |
| Many concurrent | Limit parallel consolidations |
| Memory leak | Restart application pool |
| Large reports | Use pagination or export |

**Related Documentation**: [Temp Table Patterns](../07-database-implementation/temp-table-patterns.md), [Job Management](../08-application-layer/job-management.md)

---

## Quick Reference: Error Message Lookup

| Error Message | Category | See Section |
|---------------|----------|-------------|
| "Circular ownership detected" | Ownership | 1.1 |
| "Exchange rate not found" | Currency | 3.3 |
| "Elimination out of balance" | Eliminations | 2.2 |
| "Account not found" | Data Entry | 4.1 |
| "Operation timed out" | Performance | 5.2 |
| "Maximum iterations exceeded" | Ownership | 1.1 |
| "Period is locked" | Data Entry | 4.1 |
| "Duplicate key violation" | Data Entry | 4.1 |
| "Translation adjustment required" | Currency | 3.1 |
| "Partner company not found" | Eliminations | 2.3 |

---

## See Also

### Related Documentation
- [Cross-Reference Index](../00-index/CROSS_REFERENCE_INDEX.md) - Find related documents
- [Executive Summary](../00-index/EXECUTIVE_SUMMARY.md) - System overview
- [Missing Features](../10-gap-analysis/missing-features.md) - Known limitations

### Technical References
- [Stored Procedures Catalog](../07-database-implementation/stored-procedures-catalog.md) - Procedure reference
- [Data Tables Catalog](../07-database-implementation/data-tables-catalog.md) - Table reference
- [Journal Types](../07-database-implementation/journal-types.md) - Elimination codes

### Support Resources
- [User Eliminations](../04-elimination-entries/user-eliminations.md) - Manual workarounds
- [Elimination Templates](../04-elimination-entries/elimination-templates.md) - Configuration patterns

---

*Troubleshooting Guide v1.0 | Financial Consolidation Documentation Library | 2024-12-02*
