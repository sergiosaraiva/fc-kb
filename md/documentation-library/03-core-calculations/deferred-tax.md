# Deferred Tax: Automatic Tax Effect Calculations

## Document Metadata
- **Category**: Core Calculations
- **Theory Source**: IAS 12 - Income Taxes (Deferred tax on consolidation adjustments)
- **Implementation Files**:
  - `Sigma.Database/dbo/Stored Procedures/P_UPDATE_GROUPADJUSTMENT_JOURNAL_DETAIL_DEFERRED_TAX.sql` - Tax calculation
  - `Sigma.Database/dbo/Stored Procedures/P_UPDATE_GROUPADJUSTMENT_JOURNAL_DETAIL_VALIDATE.sql` - Validation
  - `Sigma.Database/dbo/Tables/TS014C0.sql` - Company DeferredTaxRate, CalculateDeferredTax
  - `Sigma.Database/dbo/Tables/TS010C0.sql` - Special accounts (DefTaxAccount*)
  - `Sigma.Database/dbo/Tables/TS011C0.sql` - Special flows (DefTaxFlow*)
- **Last Updated**: 2024-12-01
- **Completeness**: 95% (Full deferred tax automation documented)
- **Compliance Status**: IAS 12 - Income Taxes

## Executive Summary

Prophix.Conso provides automatic deferred tax calculation on group adjustment journal entries. When configured, the system calculates the tax effect of P&L adjustments and creates balancing deferred tax asset/liability entries. The feature requires specific special accounts and flows to be configured, and uses the company-level DeferredTaxRate setting.

## Deferred Tax Architecture

### Processing Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                    Deferred Tax Calculation                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  1. Adjustment Journal Entry Created                             │
│     │                                                            │
│     ▼                                                            │
│  2. User Enables "Calculate Deferred Tax"                       │
│     │                                                            │
│     ▼                                                            │
│  3. System Validates Configuration                               │
│     ├── Special accounts defined?                               │
│     └── Special flows defined?                                  │
│     │                                                            │
│     ▼                                                            │
│  4. Calculate P&L Impact                                         │
│     Sum of amounts where AccountType = 'P'                      │
│     (excluding PLINC account)                                   │
│     │                                                            │
│     ▼                                                            │
│  5. Apply Tax Rate                                               │
│     DeferredTaxImpact = P&L Impact × (DeferredTaxRate/100)      │
│     │                                                            │
│     ▼                                                            │
│  6. Determine Accounts Based on Sign                            │
│     If positive: BS=DT, PL=CT                                   │
│     If negative: BS=CT, PL=DT                                   │
│     │                                                            │
│     ▼                                                            │
│  7. Create Two Journal Lines                                    │
│     Dr. Deferred Tax Asset/Liability (BS)                       │
│     Cr. Deferred Tax Expense/Benefit (P&L)                      │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

## Configuration Requirements

### Company-Level Settings (TS014C0)

```sql
-- From TS014C0
CalculateDeferredTax bit        -- Enable/disable per company
DeferredTaxRate decimal(9,6)    -- Tax rate percentage (e.g., 25.00)
```

### Required Special Accounts

| Special Account Code | Description | Usage |
|---------------------|-------------|-------|
| PLINC | P&L Income | Excluded from tax base calculation |
| PLBAL | P&L to Balance | Balance sheet linkage |
| DefTaxAccountBSDT | Deferred Tax Asset (BS) | Debit entry for positive impact |
| DefTaxAccountBSCT | Deferred Tax Liability (BS) | Debit entry for negative impact |
| DefTaxAccountPLDT | Deferred Tax Expense (P&L) | Credit for positive impact |
| DefTaxAccountPLCT | Deferred Tax Benefit (P&L) | Credit for negative impact |

### Required Special Flows

| Special Flow Code | Description | Usage |
|------------------|-------------|-------|
| DefTaxFlowDT | Deferred Tax Debit Flow | For positive tax impacts |
| DefTaxFlowCT | Deferred Tax Credit Flow | For negative tax impacts |

### Configuration Validation

```sql
-- Check special accounts exist
select @UnsetSpecAcounts = case when @UnsetSpecAcounts = ''
    then scod.SpecAccountCode
    else @UnsetSpecAcounts + ', ' + scod.SpecAccountCode end
from dbo.TS010C1 scod
left join dbo.TS010C0 sacc on sacc.ConsoID = @ConsoID
    and scod.SpecAccountCode = sacc.SpecAccountCode
where scod.SpecAccountCode in (
    'PLINC','PLBAL',
    'DefTaxAccountBSDT','DefTaxAccountPLCT',
    'DefTaxAccountBSCT','DefTaxAccountPLDT'
)
and sacc.AccountID is null

if len(@UnsetSpecAcounts) > 0
    select @errorinfo = dbo.AddError1('AdjustmentsGroupTaxSpecAcctInvalid',
        @UnsetSpecAcounts, @errorinfo)
```

## P_UPDATE_GROUPADJUSTMENT_JOURNAL_DETAIL_DEFERRED_TAX

### Parameters

```sql
CREATE procedure [dbo].[P_UPDATE_GROUPADJUSTMENT_JOURNAL_DETAIL_DEFERRED_TAX]
    @ConsoID int,                    -- Required
    @UserID int,                     -- Required
    @GroupAdjustmentsHeaderID int,   -- Required
    @DeferredTaxRate decimal(24,6),  -- Tax rate percentage
    @errorinfo xml output
```

### Calculation Logic

```sql
-- Step 1: Get existing journal lines
create table #result (
    pk int identity,
    ConsoID int,
    GroupAdjustmentsAccountDetailsID int,
    GroupAdjustmentsHeaderID int,
    Sequence int,
    AccountID int,
    Account nvarchar(12),
    AccountType char(1),
    Amount decimal(24,6),
    ...
)

exec dbo.P_VIEW_GROUPADJUSTMENT_JOURNAL_DETAIL
    @ConsoID = @ConsoID,
    @GroupAdjustmentsHeaderID = @GroupAdjustmentsHeaderID

-- Step 2: Calculate P&L impact (excluding PLINC)
select @DeferredTaxImpact = isnull(sum(Amount) * (@DeferredTaxRate/100), 0)
from #result
where AccountType = 'P'
  and AccountID <> @PlincAccountID

-- Step 3: Check if impact is zero
if @DeferredTaxImpact = 0
begin
    select @errorinfo = dbo.AddWarning0('AdjustmentsGroupTaxIsZero', @errorinfo)
    goto EXIT_PROCEDURE
end

-- Step 4: Determine accounts based on sign
Set @BSAccountCode = Case when @DeferredTaxImpact > 0
    then @BSAccountCodeDT
    else @BSAccountCodeCT end

Set @PLAccountCode = Case when @DeferredTaxImpact > 0
    then @PLAccountCodeCT
    else @PLAccountCodeDT end
```

### Journal Entry Creation

```sql
-- Create debit entry (Balance Sheet - Deferred Tax Asset/Liability)
exec dbo.P_UPDATE_GROUPADJUSTMENT_JOURNAL_DETAIL
    @ConsoID = @ConsoID,
    @GroupAdjustmentsAccountDetailsID = -1,  -- New line
    @GroupAdjustmentsHeaderID = @GroupAdjustmentsHeaderID,
    @Sequence = 2147483641,  -- MAX_INT - places at end
    @Account = @BSAccountCode,
    @Flow = @FlowCode,
    @Debit = @DeferredTaxImpact,
    @Credit = null,
    @UserID = @UserID,
    @errorinfo = @errorinfo OUTPUT

-- Create credit entry (P&L - Deferred Tax Expense/Benefit)
exec dbo.P_UPDATE_GROUPADJUSTMENT_JOURNAL_DETAIL
    @ConsoID = @ConsoID,
    @GroupAdjustmentsAccountDetailsID = -1,  -- New line
    @GroupAdjustmentsHeaderID = @GroupAdjustmentsHeaderID,
    @Sequence = 2147483640,  -- MAX_INT - 1
    @Account = @PLAccountCode,
    @Debit = null,
    @Credit = @DeferredTaxImpact,
    @UserID = @UserID,
    @errorinfo = @errorinfo output
```

## Frontend Integration

### AdjustmentsJournalEdit Interface

```typescript
interface AdjustmentsJournalitemObservable {
    // Deferred tax settings
    DeferredTaxRate: KnockoutObservable<number>;
    DeferredTaxRateChecked: KnockoutObservable<boolean>;
    // ...
}
```

### User Workflow

1. Create/Edit adjustment journal entry
2. Enter P&L adjustment lines
3. Check "Calculate Deferred Tax" checkbox
4. System calculates and adds deferred tax lines
5. Save complete journal with tax entries

## Account Selection Logic

### Sign-Based Account Determination

| Tax Impact | BS Account | P&L Account | Flow |
|------------|------------|-------------|------|
| Positive (expense increases) | DefTaxAccountBSDT (Asset) | DefTaxAccountPLCT (Benefit) | DefTaxFlowDT |
| Negative (expense decreases) | DefTaxAccountBSCT (Liability) | DefTaxAccountPLDT (Expense) | DefTaxFlowCT |

### Example Scenario

```
Original Adjustment:
  Dr. Depreciation Expense (P&L)    100,000
  Cr. Accumulated Depreciation      100,000

Deferred Tax Calculation (Rate = 25%):
  Tax Impact = 100,000 × 25% = 25,000 (positive)

Deferred Tax Entry:
  Dr. Deferred Tax Asset (BS)       25,000
  Cr. Deferred Tax Benefit (P&L)    25,000

Combined Effect:
  - P&L expense increased by 100,000
  - Tax benefit reduces net expense by 25,000
  - Net P&L impact = 75,000
  - Deferred Tax Asset created
```

## Error Handling

### Validation Errors

| Error Code | Message | Cause |
|------------|---------|-------|
| AdjustmentsGroupTaxSpecAcctInvalid | Special accounts not configured | Missing DefTaxAccount* |
| AdjustmentsGroupTaxSpecFlowtInvalid | Special flows not configured | Missing DefTaxFlow* |
| AdjustmentsGroupTaxIsZero | No tax impact calculated | No P&L adjustments |

### Warning Handling

```sql
-- Zero impact warning (not error)
if @DeferredTaxImpact = 0
begin
    select @errorinfo = dbo.AddWarning0('AdjustmentsGroupTaxIsZero', @errorinfo)
    goto EXIT_PROCEDURE
end
```

## Company Configuration View

### V_COMPANY Integration

```sql
-- From V_COMPANY
SELECT
    CompanyID,
    CompanyCode,
    CompanyName,
    CalculateDeferredTax,    -- Flag for automatic calculation
    DeferredTaxRate,         -- Rate to apply
    ...
FROM TS014C0
```

## Limitations and Notes

### Current Limitations

1. **Group Adjustments Only**: Deferred tax calculation only applies to group (TD033E0) adjustments, not local (TD030E0) adjustments
2. **Manual Rate Entry**: Tax rate must be set per journal or inherited from company settings
3. **No Temporary Difference Tracking**: System calculates immediate tax effect, not full deferred tax lifecycle

### Implementation Notes

- Deferred tax lines are placed at end of journal (Sequence = MAX_INT)
- PLINC account is excluded from tax base to avoid circular calculation
- Both debit and credit flows are configured for sign flexibility

## API Reference

### Primary API Handlers
| Handler | YAML File | Purpose | Status |
|---------|-----------|---------|--------|
| `GroupAdjustment_SaveJournalDetail` | [api-adjustment-endpoints.yaml](../11-agent-support/api-adjustment-endpoints.yaml) | Trigger P_UPDATE_GROUPADJUSTMENT_JOURNAL_DETAIL_DEFERRED_TAX | ✅ IMPLEMENTED |
| `GroupAdjustment_GetJournalDetail` | [api-adjustment-endpoints.yaml](../11-agent-support/api-adjustment-endpoints.yaml) | Get journal with deferred tax lines | ✅ IMPLEMENTED |

### Supporting API Handlers
| Handler | YAML File | Purpose |
|---------|-----------|---------|
| `Company_GetCompanies` | [api-company-endpoints.yaml](../11-agent-support/api-company-endpoints.yaml) | Get DeferredTaxRate setting |
| `Account_GetAccounts` | [api-account-endpoints.yaml](../11-agent-support/api-account-endpoints.yaml) | Get special DefTaxAccount* accounts |

### API Workflow
```
Deferred Tax Automatic Calculation:

1. GroupAdjustment_GetJournalDetail → Open adjustment journal
2. User enters P&L adjustment lines
3. User checks "Calculate Deferred Tax"
4. GroupAdjustment_SaveJournalDetail → Triggers:
   - P_UPDATE_GROUPADJUSTMENT_JOURNAL_DETAIL_VALIDATE
   - P_UPDATE_GROUPADJUSTMENT_JOURNAL_DETAIL_DEFERRED_TAX
   - Creates deferred tax lines automatically
5. GroupAdjustment_GetJournalDetail → Verify tax entries
```

### Configuration Requirements
| Special Account | Purpose |
|-----------------|---------|
| DefTaxAccountBSDT | Deferred Tax Asset (BS) |
| DefTaxAccountBSCT | Deferred Tax Liability (BS) |
| DefTaxAccountPLDT | Deferred Tax Expense (P&L) |
| DefTaxAccountPLCT | Deferred Tax Benefit (P&L) |

### Related API Documentation
- [API Index](../11-agent-support/api-index.yaml) - Master handler catalog
- [Gap Analysis](../11-agent-support/gap-analysis-report.yaml) - **FULLY IMPLEMENTED (95%)**

---

## Related Documentation

- [Adjustment Screens](../09-frontend-implementation/adjustment-screens.md) - Frontend integration
- [User Eliminations](../04-elimination-entries/user-eliminations.md) - Elimination adjustments
- [Journal Types](../07-database-implementation/journal-types.md) - Journal classification
- [Flow Management](flow-management.md) - Special flow handling

### Navigation
- [Cross-Reference Index](../00-index/CROSS_REFERENCE_INDEX.md) - Find related documents
- [Quick Reference Card](../20-appendices/quick-reference-card.md) - Codes and queries
- [Troubleshooting Guide](../17-troubleshooting/common-issues.md) - Issue resolution
- [Glossary](../20-appendices/glossary.md) - Term definitions

---
*Document 49 of 50+ | Batch 17: Final Documentation | Last Updated: 2024-12-01*
