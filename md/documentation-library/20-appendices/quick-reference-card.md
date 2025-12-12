# Quick Reference Card

## Document Metadata
- **Document Type**: Quick Reference
- **Purpose**: One-page reference for daily consolidation operations
- **Last Updated**: 2024-12-02
- **Version**: 1.1 (Final)

---

## Elimination Codes (S001-S085)

### System Eliminations

| Code | Name | Description | When Used |
|------|------|-------------|-----------|
| **S001** | Opening Balance | Carry forward prior closing | Every period |
| **S010** | Equity Capital | Eliminate subsidiary equity | Global (G) entities |
| **S020** | Dividends | IC dividend elimination | When dividends declared |
| **S030** | IC Netting | Receivables/payables netting | IC transactions exist |
| **S040** | Equity Method | One-line consolidation | Equity (E) entities |
| **S050** | Participation 0 | Investment vs equity - Step 0 | Global (G) entities |
| **S051** | Participation 1 | Investment vs equity - Step 1 | Global (G) entities |
| **S052** | Participation 2 | Investment vs equity - Step 2 | Global (G) entities |
| **S053** | Participation 3 | Investment vs equity - Step 3 | Global (G) entities |
| **S054** | Participation 4 | Investment vs equity - Step 4 | Global (G) entities |
| **S060** | Proportional | Proportional integration adj | Proportional (P) entities |
| **S072** | Method Change | Flow reclassification | Method transitions |
| **S085** | Minority Interest | NCI recognition | Global (G) with MI% > 0 |

### User Eliminations

| Code | Usage |
|------|-------|
| **U001-U099** | Standard recurring adjustments |
| **U100-U199** | Project-specific adjustments |
| **U200+** | One-time/special adjustments |

---

## Consolidation Methods

| Code | Method | Ownership | Control | Use Case |
|------|--------|-----------|---------|----------|
| **G** | Global Integration | Any | >50% | Subsidiaries |
| **E** | Equity Method | 20-50% | Significant influence | Associates |
| **P** | Proportional | 50% | Joint control | Joint ventures |
| **N** | Not Consolidated | <20% | None | Investments |
| **S** | Scope | Variable | Variable | Temporary status |
| **T** | Transferred | N/A | N/A | Intra-group transfer |
| **X** | Excluded | N/A | N/A | Explicitly excluded |

---

## Key Stored Procedures

### Consolidation Workflow
```sql
-- Main consolidation orchestrator
EXEC P_CONSO_CALCULATE_BUNDLE_INTEGRATION @ConsoID, @PeriodID, @SessionID

-- Ownership calculation
EXEC P_CALC_OWNERSHIP_DIRECT_PERCENTAGES @ConsoID, @PeriodID
EXEC P_CALC_OWNERSHIP_INDIRECT_PERCENTAGES @ConsoID, @PeriodID
```

### Elimination Execution
```sql
-- Run all eliminations
EXEC P_CONSO_ELIM @ConsoID, @PeriodID, @SessionID

-- Specific eliminations
EXEC P_CONSO_ELIM_DIVIDEND @ConsoID, @PeriodID, @SessionID
EXEC P_CONSO_ELIM_MINORITYINTEREST @ConsoID, @PeriodID, @SessionID
EXEC P_CONSO_ELIM_USER @ConsoID, @PeriodID, @SessionID
```

### Reporting
```sql
-- Goodwill report
EXEC P_REPORT_GOODWILL @ConsoID, @PeriodID, @CompanyID

-- Equity reconciliation
EXEC P_REPORT_CONSOLIDATED_EQUITY @ConsoID, @PeriodID

-- Ownership view
EXEC P_VIEW_OWNERSHIP @ConsoID, @PeriodID, @CompanyID
```

---

## Common Diagnostic Queries

### Check Consolidation Status
```sql
SELECT CompanyID, CompanyName, ConsoMethod, ConsoStatus,
       GroupFinPerc, GroupCtrlPerc, MinorityPerc
FROM TS014C0
WHERE ConsoID = @ConsoID AND PeriodID = @PeriodID
ORDER BY CompanyID;
```

### View Ownership Links
```sql
SELECT CompanyID, CompanyOwnedID, FinPercentage, CtrlPercentage
FROM TS015S0
WHERE ConsoID = @ConsoID AND PeriodID = @PeriodID
ORDER BY CompanyID, CompanyOwnedID;
```

### Check Elimination Journals
```sql
SELECT JournalTypeCode, CompanyID, AccountID, FlowCode,
       SUM(AmountLocal) AS LocalAmt, SUM(AmountGroup) AS GroupAmt
FROM TD045C2
WHERE ConsoID = @ConsoID AND PeriodID = @PeriodID
GROUP BY JournalTypeCode, CompanyID, AccountID, FlowCode
ORDER BY JournalTypeCode, CompanyID;
```

### Find Unbalanced Journals
```sql
SELECT JournalTypeCode, CompanyID,
       SUM(CASE WHEN AmountGroup > 0 THEN AmountGroup ELSE 0 END) AS Debits,
       SUM(CASE WHEN AmountGroup < 0 THEN AmountGroup ELSE 0 END) AS Credits,
       SUM(AmountGroup) AS Balance
FROM TD045C2
WHERE ConsoID = @ConsoID AND PeriodID = @PeriodID
GROUP BY JournalTypeCode, CompanyID
HAVING ABS(SUM(AmountGroup)) > 0.01;
```

### Check Exchange Rates
```sql
SELECT CurrCode, RateType, Rate
FROM TS017R0
WHERE ConsoID = @ConsoID AND PeriodID = @PeriodID
ORDER BY CurrCode, RateType;
```

### Find Missing Exchange Rates
```sql
SELECT DISTINCT c.CurrCode, 'Missing Rate' AS Issue
FROM TS014C0 c
LEFT JOIN TS017R0 r ON r.ConsoID = c.ConsoID
    AND r.PeriodID = c.PeriodID AND r.CurrCode = c.CurrCode
WHERE c.ConsoID = @ConsoID AND c.PeriodID = @PeriodID
  AND c.ConsoMethod IN ('G','E','P')
  AND r.CurrCode IS NULL;
```

### Circular Ownership Detection
```sql
SELECT a.CompanyID, a.CompanyOwnedID, b.CompanyOwnedID AS CircularTo
FROM TS015S0 a
INNER JOIN TS015S0 b ON a.CompanyOwnedID = b.CompanyID
WHERE a.ConsoID = @ConsoID AND b.ConsoID = @ConsoID
  AND a.PeriodID = @PeriodID AND b.PeriodID = @PeriodID
  AND b.CompanyOwnedID = a.CompanyID;
```

---

## POV (Point of View) Dimensions

### Core Dimensions

| Dimension | Table Column | Description |
|-----------|--------------|-------------|
| **ConsoID** | All tables | Multi-tenant isolation key |
| **PeriodID** | Most tables | Fiscal period (YYYYMM format) |
| **CompanyID** | TS014C0, TD* | Legal entity identifier |
| **AccountID** | TS010S0, TD* | Chart of accounts |
| **FlowCode** | TS011C0, TD* | Movement type |
| **PartnerID** | TD040B2 | Intercompany partner |

### Period Format
```
202412 = December 2024
202501 = January 2025
Format: YYYYMM (6 digits)
```

### Special Flows

| Flow | Description | Use |
|------|-------------|-----|
| **OPEN** | Opening balance | B/S start |
| **CLOSE** | Closing balance | B/S end |
| **NET** | Net movement | CLOSE - OPEN |
| **MVTC** | Current movements | P&L activity |
| **TRANSADJ** | Translation adjustment | CTA posting |
| **VarConsoMeth_EG** | Method change E→G | Step acquisition |
| **VarConsoMeth_GE** | Method change G→E | Deconsolidation |

---

## Key Tables Quick Reference

### Setup Tables (TS*)

| Table | Purpose | Key Columns |
|-------|---------|-------------|
| **TS014C0** | Company master | ConsoMethod, GroupFinPerc, GroupCtrlPerc |
| **TS015S0** | Ownership links | CompanyID, CompanyOwnedID, FinPercentage |
| **TS010S0** | Account master | AccountID, RateType, FlagInterCompany |
| **TS011C0** | Flow definitions | FlowCode, FlowType |
| **TS017R0** | Exchange rates | CurrCode, RateType, Rate |
| **TS020S0** | Journal types | JournalTypeCode, Description |
| **TS070S0** | User elim headers | ElimCode, Description |
| **TS071S0** | User elim details | ElimCode, LineNo, AccountID |

### Data Tables (TD*)

| Table | Purpose | Key Columns |
|-------|---------|-------------|
| **TD030B2** | Local data (bundles) | CompanyID, AccountID, AmountLocal |
| **TD035C2** | Consolidated data | CompanyID, AccountID, AmountGroup |
| **TD040B2** | Intercompany data | CompanyID, PartnerID, AmountLocal |
| **TD045C2** | Elimination journals | JournalTypeCode, AmountGroup |

---

## Rate Types

| Code | Name | Usage |
|------|------|-------|
| **CC** | Closing Current | B/S monetary items |
| **AC** | Average Current | P&L items |
| **MC** | Monthly Cumulative | Progressive P&L |
| **CR** | Closing Reference | Prior period B/S |
| **AR** | Average Reference | Prior period P&L |
| **NR** | No Rate | Same currency |

---

## Common Flags

### Company Flags (TS014C0)

| Flag | Values | Meaning |
|------|--------|---------|
| **FlagParent** | 0/1 | Is parent company |
| **FlagEnteringScope** | 0/1 | Entering consolidation |
| **FlagLeavingScope** | 0/1 | Leaving consolidation |
| **ConsoStatus** | 0/1 | 0=Not run, 1=Calculated |

### Account Flags (TS010S0)

| Flag | Values | Meaning |
|------|--------|---------|
| **FlagInterCompany** | 0/1 | IC account type |
| **FlagEquity** | 0/1 | Equity account |
| **FlagPL** | 0/1 | P&L account |
| **FlagHistoricalRate1** | 0/1 | Use historical rate |

---

## Troubleshooting Checklist

### Before Consolidation
- [ ] Exchange rates loaded for all currencies
- [ ] Ownership percentages sum correctly
- [ ] All bundles imported and validated
- [ ] Prior period closed and carried forward

### After Consolidation
- [ ] No unbalanced elimination journals
- [ ] Minority interest calculated for all G entities
- [ ] CTA posted for foreign subsidiaries
- [ ] Intercompany balances eliminated to zero

### Common Issues Quick Fix

| Issue | First Check | Solution |
|-------|-------------|----------|
| MI not calculating | GroupFinPerc < 100? | Verify ownership chain |
| CTA unexpected | Historical rate flags? | Check FlagHistoricalRate |
| IC not eliminating | PartnerID set? | Verify TD040B2 data |
| Ownership wrong | Circular ownership? | Run P_CALC_OWNERSHIP_INDIRECT |

---

## Quick Links

- [Troubleshooting Guide](../17-troubleshooting/common-issues.md)
- [Glossary](glossary.md)
- [Stored Procedures Catalog](../07-database-implementation/stored-procedures-catalog.md)
- [Data Tables Catalog](../07-database-implementation/data-tables-catalog.md)
- [Journal Types](../07-database-implementation/journal-types.md)
- [Cross-Reference Index](../00-index/CROSS_REFERENCE_INDEX.md)

---

*Quick Reference Card v1.1 | Financial Consolidation Documentation Library | 2024-12-02*
