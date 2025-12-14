# Adjustment Screens: Frontend Implementation

## Document Metadata
- **Category**: Frontend Implementation
- **Theory Source**: Implementation-specific (Knockout.js MVVM pattern)
- **Implementation Files**:
  - `Sigma.Mona.WebApplication/Screens/AdjustmentsJournal/` - Journal list view
  - `Sigma.Mona.WebApplication/Screens/AdjustmentsJournalEdit/` - Journal entry/edit
  - `Sigma.Mona.WebApplication/Screens/AdjustmentsManagement/` - Adjustment management
  - `Sigma.Mona.WebApplication/Screens/ImportAdjustments/` - Adjustment import
  - `Sigma.Mona.WebApplication/Screens/ExportAdjustments/` - Adjustment export
- **Last Updated**: 2024-12-01
- **Completeness**: 95% (Full adjustment frontend documented)
- **Compliance Status**: Frontend architecture reference

## Executive Summary

The adjustment screens in Prophix.Conso provide interfaces for creating, editing, and managing manual consolidation adjustments. The implementation follows the standard TypeScript/Knockout.js MVVM pattern with debit/credit journal entry, partner company selection, flow assignment, dimensional breakdown, and approval workflow support.

## Screen Architecture Overview

### Adjustment Screen Types

```
┌─────────────────────────────────────────────────────────────────┐
│                    Adjustment Screens                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌─────────────────────────┐  ┌─────────────────────────┐       │
│  │ AdjustmentsJournal      │  │ AdjustmentsJournalEdit  │       │
│  │ - Journal listing       │  │ - Debit/Credit entry    │       │
│  │ - Filter by type        │  │ - Account selection     │       │
│  │ - Navigation to edit    │  │ - Partner assignment    │       │
│  │ - Approval status       │  │ - Flow selection        │       │
│  └─────────────────────────┘  └─────────────────────────┘       │
│                                                                  │
│  ┌─────────────────────────┐  ┌─────────────────────────┐       │
│  │ AdjustmentsManagement   │  │ ImportAdjustments       │       │
│  │ - Bulk operations       │  │ - File upload           │       │
│  │ - Approval workflow     │  │ - Mapping validation    │       │
│  │ - Copy/Delete           │  │ - Error handling        │       │
│  └─────────────────────────┘  └─────────────────────────┘       │
│                                                                  │
│  ┌─────────────────────────┐                                    │
│  │ ExportAdjustments       │                                    │
│  │ - Export to file        │                                    │
│  │ - Format selection      │                                    │
│  │ - Filter options        │                                    │
│  └─────────────────────────┘                                    │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Layer Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    AdjustmentsJournalEdit.cshtml                 │
│   - Knockout.js bindings                                         │
│   - DevExpress grid for journal lines                           │
│   - Account/Partner/Flow lookups                                │
└─────────────────────────────────────────────────────────────────┘
                              ▲
                              │ data-bind
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    AdjustmentsJournalEdit.ts                     │
│   - AdjustmentsJournalEditViewModel                             │
│   - Journal header observables                                   │
│   - Journal line collection                                      │
│   - Validation and save logic                                    │
└─────────────────────────────────────────────────────────────────┘
                              ▲
                              │ Message Broker
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    AdjustmentJournalEditServices.cs              │
│   - GetJournalData handler                                       │
│   - SaveJournalData handler                                      │
│   - Account/Partner lookup handlers                              │
└─────────────────────────────────────────────────────────────────┘
                              ▲
                              │ Stored Procedure / EF
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    TD030E0 / TD033E0                             │
│   - Local adjustment data                                        │
│   - Group adjustment data                                        │
└─────────────────────────────────────────────────────────────────┘
```

## AdjustmentsJournalEdit Implementation

### TypeScript Interfaces

```typescript
// Journal header observable
interface AdjustmentsJournalitemObservable {
    ID: KnockoutObservable<number>;
    ConsoID: KnockoutObservable<number>;
    JournalCode: KnockoutObservable<string>;
    JournalType: KnockoutObservable<string>;
    JournalCategory: KnockoutObservable<string>;
    JournalDescription: KnockoutObservable<string>;
    AssociatedJournalCode: KnockoutObservable<string>;
    AssociatedJournalType: KnockoutObservable<string>;
    AssociatedJournalCategory: KnockoutObservable<string>;
    AssociatedJournalDescription: KnockoutObservable<string>;
    JournalEntry: KnockoutObservable<string>;
    CompanyName: KnockoutObservable<string>;
    CompanyID: KnockoutObservable<number>;
    CompanyCode: KnockoutObservable<string>;
    JournalText: KnockoutObservable<string>;
    CurrCode: KnockoutObservable<string>;
    DeferredTaxRate: KnockoutObservable<number>;
    DeferredTaxRateChecked: KnockoutObservable<boolean>;
    MinorityFlag: KnockoutObservable<string>;
    CurrencyFlag: KnockoutObservable<string>;
    Behaviour: KnockoutObservable<number>;
    NbrDec: KnockoutObservable<number>;
    UnitsOf: KnockoutObservable<number>;
    ModificationUserLogin: KnockoutObservable<string>;
    CreationDate: KnockoutObservable<Date>;
    ModificationDate: KnockoutObservable<Date>;
    HeaderFileID: KnockoutObservable<number>;
    File: KnockoutObservable<IDownloadItem | undefined>;
    Approved: KnockoutObservable<boolean>;
    FlagCarriedOrCopied: KnockoutObservable<boolean>;
    CanModify: KnockoutObservable<boolean>;
    Rows: KnockoutObservableArray<AdjustmentsJournalEditObservable>;
    EntityVersion: KnockoutObservableArray<EntityVersion>;
    dirtyFlag: KnockoutComputed<boolean>;
}

// Journal line observable
interface AdjustmentsJournalEditObservable {
    ID: KnockoutObservable<number>;
    LineNr: KnockoutObservable<number>;
    Account: KnockoutObservable<string>;
    AccountType: KnockoutObservable<string>;
    AccountDescription: KnockoutObservable<string>;
    PartnerCode: KnockoutObservable<string>;
    PartnerName: KnockoutObservable<string>;
    Flow: KnockoutObservable<string>;
    FlowDescription: KnockoutObservable<string>;
    Debit: KnockoutObservable<number>;
    Credit: KnockoutObservable<number>;
    TransAmount: KnockoutObservable<number>;
    TransRate: KnockoutObservable<number>;
    TransCurrCode: KnockoutObservable<string>;
    Dim: KnockoutObservable<number>;
    HasDimension: KnockoutObservable<boolean>;
    DimensionURL: KnockoutObservable<string>;
    isSelected: KnockoutObservable<boolean>;
    NbrDec: KnockoutObservable<number>;
}
```

### ViewModel Initialization

```typescript
export var view: AdjustmentsJournalEditViewModel;

export function init(p: {
    CanModify: boolean;
    AddBlankURL: string;
    AdjustmentJournalID: number;
    AdjustmentsJournalEdit_UploaderOptions: any;
    AdjustmentType: string;
    AssociatedJournalsCodeDescriptionContext: string;
    CompanyCodeDescriptionContext: string;
    DDLBehavior: KeyValuePair<number, string>[];
    DDLCurrencies: KeyValuePair<string, string>[];
    DDLCurrencyFlag: KeyValuePair<string, string>[];
    DDLFileTypes: KeyValuePair<string, string>[];
    DDLListSort: KeyValuePair<string, string>[];
    DDLListThirds: KeyValuePair<number, string>[];
    IsEndUser: boolean;
    JournalsCodeDescriptionContext: string;
    NewAsCurrentURL: string;
    NextURL: string;
    PreviousURL: string;
    ReturnURL: string;
    SelectedConsoID: number;
    TemplateCopyType: string;
    TemplateID: number;
    LockJournal: boolean;
    ReportNr: number;
    Period: string;
    CanEdit: boolean;
    CompanyCode: string;
    JournalTypeCategory: string;
    CurrentPosition: number;
    TotalJournals: number;
}): void {
    view = new AdjustmentsJournalEditViewModel({
        ...p,
        actionsStartDisabled: true
    });
    ko.applyBindings(view, $(mona.pageContentSelector)[0]);
}
```

## Journal Entry Features

### Debit/Credit Entry

```
┌─────────────────────────────────────────────────────────────────┐
│                    Journal Entry Grid                            │
├──────┬───────────┬─────────┬────────┬─────────┬─────────┬──────┤
│ Line │ Account   │ Partner │ Flow   │ Debit   │ Credit  │ Dim  │
├──────┼───────────┼─────────┼────────┼─────────┼─────────┼──────┤
│ 1    │ 7000      │ SUB1    │ -      │ 100,000 │ -       │ -    │
│ 2    │ 3100      │ -       │ TPL    │ -       │ 100,000 │ -    │
├──────┴───────────┴─────────┴────────┴─────────┴─────────┴──────┤
│                         Totals: Debit = 100,000 | Credit = 100,000 │
│                         Balance: 0 (BALANCED)                    │
└─────────────────────────────────────────────────────────────────┘
```

### Validation Rules

| Rule | Description |
|------|-------------|
| Balance Check | Debit total must equal Credit total |
| Account Required | Each line must have an account |
| Amount Required | Each line needs Debit OR Credit |
| Partner Validation | Partner must exist if specified |
| Flow Validation | Flow must be valid for account |

### Behaviour Options

```typescript
// DDLBehavior dropdown values
DDLBehavior: KeyValuePair<number, string>[]

// Behaviour codes (from TS020S0)
// 1 = Current only
// 2 = Reference only
// 3 = Both current and reference
// 4 = Recurring
```

## Translation Support

### Translation Keys

```typescript
interface Translations extends mona.PageTranslations {
    Line: string;
    Account: string;
    Partner: string;
    Flow: string;
    AdjustmentJournalEdit_HistRate: string;
    TransAmount: string;
    Currency: string;
    Dim: string;
    CONFIRM_ACTION_WILL_SAVE: string;
    AdjustmentJournalEditViewAcct: string;
    CONFIRM_REFRESH: string;
    MultiplyDetailAtLeastOneRow: string;
    TableHeaderDebit: string;
    TableHeaderCredit: string;
    Actions: string;
    Yes: string;
    No: string;
    Ok: string;
    SigmaConsoFramework_ConfirmRemoveMessage: string;
    UndoChanges: string;
    Confirmation: string;
    Clean: string;
    Continue: string;
    Delete: string;
    CONFIRM_UNSAVED_CHANGES: string;
    NoFile: string;
    CONFIRM_DELETE_JOURNAL: string;
    Close: string;
    Amount: string;
    AccountCode: string;
}
```

## Journal Header Properties

### Currency and Display Settings

```typescript
// Currency configuration
CurrCode: KnockoutObservable<string>;        // Journal currency
CurrencyFlag: KnockoutObservable<string>;    // L=Local, G=Group, T=Transaction
NbrDec: KnockoutObservable<number>;          // Decimal precision
UnitsOf: KnockoutObservable<number>;         // Display units (1, 1000, 1000000)
```

### Special Features

```typescript
// Deferred tax automatic calculation
DeferredTaxRate: KnockoutObservable<number>;
DeferredTaxRateChecked: KnockoutObservable<boolean>;

// Minority flag for NCI impact
MinorityFlag: KnockoutObservable<string>;    // 0=Group, 1=Minority

// Associated journal (reversal pairs)
AssociatedJournalCode: KnockoutObservable<string>;
AssociatedJournalType: KnockoutObservable<string>;

// Approval workflow
Approved: KnockoutObservable<boolean>;
FlagCarriedOrCopied: KnockoutObservable<boolean>;
```

## Dirty Flag Pattern

### Change Tracking

```typescript
// Computed dirty flag on journal header
dirtyFlag: KnockoutComputed<boolean>;

// Implementation pattern
this.dirtyFlag = ko.computed(() => {
    // Check header changes
    if (this.JournalText() !== originalJournalText) return true;
    if (this.Behaviour() !== originalBehaviour) return true;

    // Check line changes
    for (const row of this.Rows()) {
        if (row.isModified()) return true;
    }

    return false;
});

// Usage for unsaved changes warning
if (view.dirtyFlag()) {
    const confirmed = await confirmDialog(translations.CONFIRM_UNSAVED_CHANGES);
    if (!confirmed) return;
}
```

## Dimensional Entry Support

### Dimension Drill-Down

```typescript
// Line-level dimension properties
HasDimension: KnockoutObservable<boolean>;
DimensionURL: KnockoutObservable<string>;
Dim: KnockoutObservable<number>;

// Navigation to dimension entry
function openDimensionEntry(row: AdjustmentsJournalEditObservable) {
    if (row.HasDimension()) {
        window.open(row.DimensionURL(), '_blank');
    }
}
```

### DimensionDataEntry Integration

```typescript
import * as dimensionModule from "../DimensionDataEntry/DimensionDataEntry";

// Dimension popup for adjustment line breakdown
```

## Service Communication

### Message Handlers

```typescript
// Service handler names
const Handlers = {
    GetJournalData: "AdjustmentsJournalEdit_GetData",
    SaveJournalData: "AdjustmentsJournalEdit_SaveData",
    DeleteJournal: "AdjustmentsJournalEdit_Delete",
    GetAccounts: "AdjustmentsJournalEdit_GetAccounts",
    GetPartners: "AdjustmentsJournalEdit_GetPartners",
    GetFlows: "AdjustmentsJournalEdit_GetFlows"
};
```

### Service Request Pattern

```typescript
// Load journal data
async function loadJournalData(journalId: number): Promise<void> {
    const response = await mona.callService({
        handler: Handlers.GetJournalData,
        data: { JournalID: journalId }
    });

    if (mona.checkResponseMessageErrors(response)) return;

    // Map to observables
    mapResponseToViewModel(response.data);
}

// Save journal data
async function saveJournalData(): Promise<boolean> {
    const journalData = serializeViewModel();

    const response = await mona.callService({
        handler: Handlers.SaveJournalData,
        data: journalData
    });

    return !mona.checkResponseMessageErrors(response);
}
```

## Adjustment Data Tables

### TD030E0 - Local Adjustments

```sql
-- Local company adjustments
CREATE TABLE TD030E0 (
    JournalHeaderID bigint,
    ConsoID int,
    CompanyID int,
    JournalTypeID int,
    JournalEntry bigint,
    JournalText nvarchar(max),
    CurrCode nvarchar(3),
    Behaviour tinyint,
    MinorityFlag bit,
    Approved bit,
    ...
)
```

### TD033E0 - Group Adjustments

```sql
-- Group level adjustments
CREATE TABLE TD033E0 (
    JournalHeaderID bigint,
    ConsoID int,
    JournalTypeID int,
    JournalEntry bigint,
    JournalText nvarchar(max),
    ...
)
```

## Import/Export Screens

### ImportAdjustments

```
Sigma.Mona.WebApplication/Screens/ImportAdjustments/
├── ImportAdjustments.cshtml
├── ImportAdjustments.ts
├── ImportAdjustmentsController.cs
├── ImportAdjustmentsService.cs
└── ImportAdjustmentsService.ts
```

### ExportAdjustments

```
Sigma.Mona.WebApplication/Screens/ExportAdjustments/
├── ExportAdjustments.cshtml
├── ExportAdjustments.ts
├── ExportAdjustmentsController.cs
└── ExportAdjustmentsService.cs
```

## Entity Locking

### Optimistic Concurrency

```typescript
// Entity version tracking
EntityVersion: KnockoutObservableArray<EntityVersion>;

// Check version before save
if (!validateEntityVersions(originalVersions, currentVersions)) {
    showError("Journal has been modified by another user");
    return false;
}
```

## Navigation Support

### Journal Navigation

```typescript
// Navigation URLs
NextURL: string;
PreviousURL: string;
ReturnURL: string;
NewAsCurrentURL: string;
AddBlankURL: string;

// Position tracking
CurrentPosition: number;
TotalJournals: number;
```

## Related Documentation

- [Data Entry Screens](data-entry-screens.md) - Similar MVVM patterns
- [Journal Types](../07-database-implementation/journal-types.md) - Journal classification
- [User Eliminations](../04-elimination-entries/user-eliminations.md) - Elimination adjustments
- [Job Management](../08-application-layer/job-management.md) - Import/Export jobs

---
*Document 48 of 50+ | Batch 16: System Mechanics & Adjustment Processing | Last Updated: 2024-12-01*
