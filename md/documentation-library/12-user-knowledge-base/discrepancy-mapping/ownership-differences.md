# Ownership Differences: Theory vs Product

## Overview

This document details how Prophix.Conso calculates ownership percentages and determines consolidation methods compared to Allen White's "Direct Consolidation" and IFRS 10/IAS 28 requirements. Understanding these differences is essential for proper group structure configuration and audit validation.

---

## Executive Summary

| Aspect | Theory (IFRS 10/Allen White) | Product (Prophix.Conso) |
|--------|------------------------------|------------------------|
| **Control Test** | Qualitative + Quantitative | Primarily quantitative (>50% = control) |
| **Input Method** | Percentage-based | Share count-based (more precise) |
| **Circular Ownership** | Iterative mathematical solution | Matrix-based propagation algorithm |
| **Potential Voting Rights** | Must be considered if substantive | Not automatically considered |
| **De Facto Control** | Control < 50% possible | Manual override required |

---

## 1. Consolidation Method Determination

### Theory (IFRS 10)

Control assessment requires evaluation of:

1. **Power over the investee** - Ability to direct relevant activities
2. **Exposure to variable returns** - Rights to variable returns from involvement
3. **Link between power and returns** - Ability to use power to affect returns

This is a **qualitative assessment** that considers:
- Voting rights (actual and potential)
- Contractual arrangements
- Board composition
- De facto control scenarios
- Principal vs agent relationships

**IFRS 10 Method Determination**:

| Situation | Method | Standard |
|-----------|--------|----------|
| Control (power + returns + link) | Full Consolidation | IFRS 10 |
| Joint Control | Proportional/Equity | IFRS 11 |
| Significant Influence | Equity Method | IAS 28 |
| No significant influence | Fair Value | IFRS 9 |

### Product Implementation

Prophix.Conso uses a **quantitative percentage-based** approach:

```sql
Update #Companies
Set ConsoMethod =
    Case
        When (GroupCtrlPerc > 50 OR CompanyID = @ParentID) then 'G'  -- Global
        When (GroupCtrlPerc = 50) then 'P'                          -- Proportional
        When (GroupCtrlPerc >= 20 AND GroupCtrlPerc < 50) then 'E'  -- Equity
        When (GroupCtrlPerc < 20) then 'N'                          -- Not Consolidated
        Else 'N'
    End
```

| Control % | Method | Code |
|-----------|--------|------|
| > 50% | Global Integration | G |
| = 50% | Proportional | P |
| 20-50% | Equity Method | E |
| < 20% | Not Consolidated | N |

### Key Differences

| Aspect | Theory | Product | Gap |
|--------|--------|---------|-----|
| **De Facto Control** | Control possible < 50% | Not automatic | Manual override required |
| **Joint Arrangements** | IFRS 11 classification | Simplified P method | May need manual adjustment |
| **Substantive Rights** | Must assess substance | Not evaluated | Document in procedures |
| **Potential Voting Rights** | Consider if substantive | Not included | Manual percentage adjustment |

**Workaround**: Use manual method override in Group > Group Structure to set consolidation method when theoretical analysis differs from percentage calculation.

---

## 2. Percentage Calculation Methods

### Theory Approach

Two key percentages:
1. **Ownership %** (Financial): Economic interest in dividends and net assets
2. **Voting %** (Control): Power to direct relevant activities

These may differ due to:
- Non-voting shares
- Preference shares
- Multi-class share structures
- Voting agreements
- Potential voting rights

### Product Implementation

Prophix.Conso maintains **two separate percentage chains**:

| Table | Field | Purpose |
|-------|-------|---------|
| **TS015S0** | `NbrFinRights` | Number of financial rights (shares) |
| **TS015S0** | `NbrVotingRights` | Number of voting rights |
| **TS014C0** | `GroupPerc` | Indirect financial ownership % |
| **TS014C0** | `GroupCtrlPerc` | Indirect control/voting % |
| **TS014C0** | `MinorPerc` | Non-controlling interest % |

**Share-Based Input** (more precise than percentage):

```sql
-- Financial percentage calculation
FinPercentage = (NbrFinRights / NbrFinRightsIssued) * 100

-- Control percentage calculation
CtrlPercentage = (NbrVotingRights / NbrVotingRightsIssued) * 100
```

### Indirect Ownership Calculation

**Direct Holdings** (TS015S0):
```
Parent -> Sub A: 80% financial, 80% voting
Parent -> Sub B: 60% financial, 60% voting
Sub A -> Sub C: 70% financial, 70% voting
```

**Indirect Holdings** (calculated):
```
Parent -> Sub C (indirect): 80% × 70% = 56% effective
```

### Key Differences

| Aspect | Theory | Product | Notes |
|--------|--------|---------|-------|
| **Input Precision** | Often percentage-based | Share count-based | Product more precise |
| **Fractional Ownership** | May round | Full precision (16 decimals) | Product advantage |
| **Multi-Class Shares** | Complex treatment | Separate rights tracking | Basic support |
| **Treasury Shares** | Deduct from calculation | Manual deduction needed | Gap |

---

## 3. Circular Ownership Handling

### Theory Approach

Circular ownership (Company A owns B, B owns C, C owns A) requires:

1. **Iterative mathematical solution**
2. **Matrix algebra approach**
3. **Convergence calculation**

Example:
```
Parent owns 80% of Sub A
Sub A owns 60% of Sub B
Sub B owns 10% of Sub A (circular)
```

Theoretical solution requires solving simultaneous equations.

### Product Implementation

Prophix.Conso uses a **matrix-based propagation algorithm**:

```sql
-- P_CALC_OWNERSHIP_INDIRECT_PERCENTAGES.sql
-- Control propagates only through entities controlled >50%

UPDATE #GroupControl
Set NewCtrl = SumTS015.CtrlSubTotal
FROM #GroupControl a
JOIN (
    SELECT a.CompanyOwnedID,
           sum(cast(a.NbrVotingRights as float) /
               cast(b.NbrVotingRightsIssued as float) * 100) as CtrlSubTotal
    FROM #OwnerShip a
        Inner Join #Companies b on (b.CompanyID = a.CompanyOwnedID)
    WHERE a.CompanyID IN (
        SELECT CompanyID from #GroupControl where NewCtrl > 50
    )
    GROUP BY a.CompanyOwnedID
) SumTS015 ON SumTS015.CompanyOwnedID = a.CompanyID
```

**Key Logic**:
- Control only propagates through entities where control > 50%
- Prevents infinite loops in circular structures
- Iterates until percentages stabilize

### Key Differences

| Aspect | Theory | Product | Impact |
|--------|--------|---------|--------|
| **Algorithm** | Mathematical iteration | Matrix propagation | Usually equivalent results |
| **Convergence** | May not converge | Always converges | Product more stable |
| **Complex Circles** | Full mathematical solution | Simplified propagation | May differ for complex structures |
| **Validation** | Manual verification | Automated | Document verification |

**Recommendation**: For complex circular ownership structures, manually verify calculated percentages against theoretical calculation.

---

## 4. Minority Interest (NCI) Calculation

### Theory (IFRS 10)

Non-controlling interest at acquisition:
- Option A: NCI at fair value (full goodwill method)
- Option B: NCI at proportionate share of net assets

Subsequent measurement:
- Share of profit/loss
- Share of OCI
- Dividends received

### Product Implementation

Minority interest calculated as:

```sql
Update #Companies
Set MinorPerc = ROUND(100 - GroupPerc, 16)
Where ConsoMethod in ('G', 'N')
      and CompanyID <> @ParentID
```

**Simple formula**: `MI% = 100% - Group%`

Applied only to:
- Globally consolidated companies (G)
- Non-consolidated companies (N)
- Excludes parent company

### Key Differences

| Aspect | Theory | Product | Gap |
|--------|--------|---------|-----|
| **Initial Recognition** | Fair value OR proportionate | Proportionate only | No full goodwill option |
| **Fair Value Option** | Election available | Not supported | Manual adjustment needed |
| **NCI Goodwill** | If fair value option | Not calculated | Manual entry if needed |
| **Subsequent Changes** | Complex tracking | Simplified | May need manual adjustments |

---

## 5. Special Ownership Scenarios

### Reciprocal Holdings

**Theory**: Complex mathematical treatment, may affect control determination

**Product**: Supported through circular ownership algorithm, but may need validation

### Treasury Shares

**Theory**: Deducted from issued shares for percentage calculation

**Product**: Manual adjustment required - not automatically detected

**Workaround**:
1. Adjust `NbrFinRightsIssued` to exclude treasury shares
2. Or manually adjust percentages

### Preference Shares

**Theory**: Complex treatment depending on characteristics (cumulative, participating, convertible)

**Product**: Limited support - tracked as separate rights but limited automatic treatment

**Workaround**: Manual classification and adjustment for preference share characteristics

### Step Acquisitions

**Theory**: Remeasure previous interest at fair value on gaining control

**Product**: S094 (Participation Type 4) provides basic handling

**Gap**: Full fair value remeasurement requires manual adjustment

---

## 6. User Interface: Group Structure Screen

**Navigation**: Group > Group Structure

### Key Fields

| Field | Description | Theory Mapping |
|-------|-------------|----------------|
| **Financial Rights** | Number of shares for economic interest | Ownership percentage |
| **Voting Rights** | Number of shares for control | Control percentage |
| **Group %** | Calculated indirect financial ownership | Effective ownership |
| **Minority %** | Calculated NCI percentage | Non-controlling interest |
| **Method** | G/P/E/N | Consolidation method |

### Tabs

| Tab | Purpose |
|-----|---------|
| **Shareholders** | Who owns this company (shares held BY others) |
| **Participations** | What this company owns (shares held IN others) |

### Manual Override

Users can override calculated method:
1. Select company
2. Change Method field
3. Save

**Document override rationale** for audit trail.

---

## 7. Practical Implications

### For Consultants

1. **During Implementation**:
   - Verify percentage calculations match client expectations
   - Document any manual overrides with rationale
   - Configure multi-tier structures carefully
   - Test circular ownership scenarios

2. **Training Users**:
   - Explain share count vs percentage input
   - Train on manual method overrides
   - Document treasury share handling procedures

### For Auditors

1. **Verification Points**:
   - Recalculate key percentages manually
   - Verify method determination is appropriate
   - Check for undocumented overrides
   - Validate NCI calculations

2. **Common Issues**:
   - Treasury shares not deducted
   - De facto control not recognized
   - Preference shares incorrectly treated
   - Circular ownership calculation errors

### For Consolidators

1. **Data Entry**:
   - Enter share counts, not percentages (more precise)
   - Update when share structures change
   - Document treasury share adjustments

2. **Validation**:
   - Review percentage summary reports
   - Verify method assignments
   - Check NCI allocations

---

## 8. Frequently Asked Questions

**Q: Why doesn't my control percentage match my manual calculation?**
A: Check for circular ownership effects, treasury shares, and rounding. The product uses 16-decimal precision.

**Q: Can I have control with less than 50%?**
A: Yes, but you must manually override the consolidation method. Document the de facto control rationale.

**Q: How do I handle treasury shares?**
A: Reduce the `NbrFinRightsIssued` and `NbrVotingRightsIssued` fields by treasury share count.

**Q: Why is my NCI different from expected?**
A: The product uses proportionate share method only. For full goodwill method, add manual adjustment.

**Q: How do I handle potential voting rights?**
A: Manually adjust voting rights count if potential rights are substantive and exercisable.

---

## Related Documentation

- [Theory vs Product Overview](theory-vs-product-overview.md)
- [Elimination Differences](elimination-differences.md)
- [Help: Input Consolidation Scope](../help-content/0306-input-the-consolidation-scope.md)
- [Technical: Circular Ownership](../../03-core-calculations/circular-ownership.md)
- [Technical: Minority Interest](../../03-core-calculations/minority-interest.md)

---

*Ownership Differences | Version 1.0 | Last Updated: 2024-12-03*
