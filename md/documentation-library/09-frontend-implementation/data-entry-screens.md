# Data Entry Screens: Frontend Implementation

## Document Metadata
- **Category**: Frontend Implementation
- **Theory Source**: Implementation-specific (Knockout.js MVVM pattern)
- **Implementation Files**:
  - `Sigma.Mona.WebApplication/Screens/BundleStandardPeriod/` - Standard bundle entry
  - `Sigma.Mona.WebApplication/Screens/BundleMultiPeriod/` - Multi-period entry
  - `Sigma.Mona.WebApplication/Screens/BundleSpread/` - Spread entry
  - `Sigma.Mona.WebApplication/Screens/Adjustments/` - Adjustment entry
  - `Sigma.Mona.WebApplication/Screens/IntercoDataEntry/` - Intercompany entry
  - `Sigma.Database/dbo/Stored Procedures/P_VIEW_DATAENTRY_*.sql` - Data retrieval
- **Last Updated**: 2024-12-01
- **Completeness**: 95% (Full data entry architecture documented)
- **Compliance Status**: Frontend architecture reference

## Executive Summary

The data entry screens in Prophix.Conso provide interfaces for entering and managing financial data including local bundles, adjustments, intercompany transactions, and dimensional breakdowns. The implementation follows the project's standard **TypeScript/Knockout.js MVVM pattern** with grid-based data entry using DevExpress controls. Multiple entry modes support different data collection workflows.

## Architecture Overview

### Data Entry Screen Types

```
┌─────────────────────────────────────────────────────────────────┐
│                    Data Entry Screens                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌─────────────────────┐  ┌─────────────────────┐               │
│  │ BundleStandardPeriod │  │ BundleMultiPeriod   │               │
│  │ - Single period      │  │ - Multiple periods  │               │
│  │ - Grid-based entry   │  │ - Period comparison │               │
│  │ - Input form driven  │  │ - Trend analysis    │               │
│  └─────────────────────┘  └─────────────────────┘               │
│                                                                  │
│  ┌─────────────────────┐  ┌─────────────────────┐               │
│  │ Adjustments          │  │ IntercoDataEntry    │               │
│  │ - Journal entries    │  │ - Partner selection │               │
│  │ - Debit/Credit       │  │ - IC reconciliation │               │
│  │ - Approval workflow  │  │ - Netting preview   │               │
│  └─────────────────────┘  └─────────────────────┘               │
│                                                                  │
│  ┌─────────────────────┐  ┌─────────────────────┐               │
│  │ BundleSpread         │  │ DimensionalEntry    │               │
│  │ - SpreadJS control   │  │ - Dimension drill   │               │
│  │ - Excel-like UI      │  │ - Detail breakdown  │               │
│  │ - Formula support    │  │ - Hierarchical      │               │
│  └─────────────────────┘  └─────────────────────┘               │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Layer Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    BundleStandardPeriod.cshtml                   │
│   - Knockout.js bindings                                         │
│   - DevExpress grid controls                                     │
│   - Input form layout                                            │
└─────────────────────────────────────────────────────────────────┘
                              ▲
                              │ data-bind
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    BundleStandardPeriod.ts                       │
│   - Observable properties                                        │
│   - Cell change tracking                                         │
│   - Validation logic                                             │
│   - Service communication                                        │
└─────────────────────────────────────────────────────────────────┘
                              ▲
                              │ Message Broker
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    BundleStandardPeriodService.cs                │
│   - Message handlers                                             │
│   - Data retrieval/save                                          │
│   - Business validation                                          │
└─────────────────────────────────────────────────────────────────┘
                              ▲
                              │ Stored Procedure
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    P_VIEW_DATAENTRY_BUNDLE_*                     │
│   - Grid structure retrieval                                     │
│   - Amount data loading                                          │
│   - Input form configuration                                     │
└─────────────────────────────────────────────────────────────────┘
```

## BundleStandardPeriod Implementation

### TypeScript ViewModel

```typescript
// BundleStandardPeriod.ts

interface BundleStandardPeriodDataObservable {
    InputFormCode: KnockoutObservable<string>;
    InputFormName: KnockoutObservable<string>;
    CompanyID: KnockoutObservable<number>;
    CompanyCode: KnockoutObservable<string>;
    CompanyName: KnockoutObservable<string>;
    Option: KnockoutObservable<number>;        // Data view option
    OptionText: KnockoutObservable<string>;
    Locked: KnockoutObservable<boolean>;
    CurrCode: KnockoutObservable<string>;
    NbrDec: KnockoutObservable<string>;        // Decimal precision
    UnitsOf: KnockoutObservable<number>;       // Display units
    ClientSideCalculations: KnockoutObservable<string>;
    RowsResult: KnockoutObservableArray<IRowsResultObservable>;
    ColsResult: KnockoutObservableArray<any>;
    EntityVersion: KnockoutObservableArray<EntityVersion>;
}
```

### Row and Cell Interfaces

```typescript
interface IRowsResultObservable {
    AccountSum: KnockoutObservable<string>;
    Description: KnockoutObservable<string>;
    Formula: KnockoutObservable<string>;
    HasDimensions: KnockoutObservable<boolean>;
    HasFlows: KnockoutObservable<boolean>;
    HasIntercos: KnockoutObservable<boolean>;
    HasParticipations: KnockoutObservable<boolean>;
    HasPartners: KnockoutObservable<boolean>;
    HasUnexplainedFlow: KnockoutObservable<boolean>;
    HasUnexplainedIC: KnockoutObservable<boolean>;
    IdentLevel: KnockoutObservable<number>;
    IsBold: KnockoutObservable<boolean>;
    IsItalic: KnockoutObservable<boolean>;
    LineNr: KnockoutObservable<number>;
    LineType: KnockoutObservable<string>;
    Cells: KnockoutObservableArray<ICellsResultObservable>;
}

interface ICellsResultObservable {
    AccountID: KnockoutObservable<number>;
    Amount: KnockoutObservable<number>;
    OriginalAmount: KnockoutObservable<number>;
    BaseRecordKeyID: KnockoutObservable<number>;
    ColNr: KnockoutObservable<number>;
    Comment: KnockoutObservable<string>;
    OriginalComment: KnockoutObservable<string>;
    CommentEnabled: KnockoutObservable<boolean>;
    LineNr: KnockoutObservable<number>;
    ReadOnly: KnockoutObservable<boolean>;
    SignMultiplier: KnockoutObservable<number>;
}
```

### Data View Options

```typescript
// Options enum for data view modes
enum Options {
    Undefined = 0,
    LocalAmounts = 1,            // Raw imported data
    AdjustedBundles = 2,         // After local adjustments
    LocalAdjustments = 3,        // Adjustment entries only
    LocalPlusAdjustmentsN = 4,   // Current period total
    LocalPlusAdjustmentsN1 = 5,  // Prior period total
    Comments = 6                  // Comment view
}
```

## Backend Service Implementation

### BundleStandardPeriodService DTOs

```csharp
public class BundleStandardPeriodDTO
{
    public int InputFormID { get; set; }
    public string InputFormCode { get; set; }
    public string InputFormName { get; set; }
    public int CompanyID { get; set; }
    public string CompanyCode { get; set; }
    public string CompanyName { get; set; }
    public byte? Option { get; set; }
    public string OptionText { get; set; }
    public bool Locked { get; set; }
    public string CurrCode { get; set; }
    public byte? NbrDec { get; set; }
    public byte? UnitsOf { get; set; }
    public bool? ClientSideCalculations { get; set; }
    public string LabelAmountsPowerOf { get; set; }
    public List<RowsResultDTO> RowsResult { get; set; }
    public List<P_VIEW_DATAENTRY_BUNDLE_ACCOUNTResult2> ColsResult { get; set; }
    public EntityVersion[] EntityVersion { get; set; }
}

public class RowsResultDTO
{
    public string AccountSum { get; set; }
    public string Description { get; set; }
    public string Formula { get; internal set; }
    public bool? HasDimensions { get; set; }
    public bool? HasFlows { get; set; }
    public bool? HasIntercos { get; set; }
    public bool? HasParticipations { get; set; }
    public bool? HasPartners { get; set; }
    public short? IdentLevel { get; set; }
    public bool? IsBold { get; set; }
    public bool? IsItalic { get; set; }
    public bool? IsUnderlined { get; set; }
    public short? LineNr { get; set; }
    public char? LineType { get; set; }
    public List<CellsResultDTO> Cells { get; set; }
}

public class CellsResultDTO
{
    public int? AccountID { get; set; }
    public decimal? Amount { get; set; }
    public int? BaseRecordKeyID { get; set; }
    public short? ColNr { get; set; }
    public string Comment { get; set; }
    public short? LineNr { get; set; }
    public bool? ReadOnly { get; set; }
    public short? SignMultiplier { get; set; }
}
```

### Message Handlers

```csharp
// Service message handler constants
public static class BundleStandardPeriodHandlers
{
    public const string GetBundleData = "BundleStandardPeriod_GetBundleData";
    public const string SaveBundleData = "BundleStandardPeriod_SaveBundleData";
    public const string GetInputForms = "BundleStandardPeriod_GetInputForms";
    public const string GetCompanies = "BundleStandardPeriod_GetCompanies";
    public const string ExportToExcel = "BundleStandardPeriod_ExportToExcel";
    public const string ImportFromExcel = "BundleStandardPeriod_ImportFromExcel";
}
```

## Input Form Configuration

### SETUP_TS022* Tables

Input forms control data entry grid structure:

| Table | Purpose |
|-------|---------|
| SETUP_TS022S0 | Input form definitions |
| SETUP_TS022S1 | Form descriptions (multi-language) |
| SETUP_TS022S2 | Row definitions (accounts) |
| SETUP_TS022S3 | Column definitions |
| SETUP_TS022S4 | Cell-level configuration |

### Form Structure

```sql
-- Input form structure
SELECT
    InputFormID, InputFormCode, InputFormName,
    ShowFlows, ShowIntercos, ShowDimensions,
    DefaultOption, AllowImport, AllowExport
FROM SETUP_TS022S0
WHERE ConsoID = @ConsoID AND Active = 1
```

## Data Flow

### Get Bundle Data Request

```
1. User selects Company + Input Form
   │
   ▼
2. BundleStandardPeriod.ts calls service
   BundleStandardPeriodHandlers.GetBundleData
   { CompanyID, InputFormID, Option }
   │
   ▼
3. Service executes P_VIEW_DATAENTRY_BUNDLE_*
   - P_VIEW_DATAENTRY_BUNDLE_HEADER (grid structure)
   - P_VIEW_DATAENTRY_BUNDLE_ACCOUNT (row definitions)
   - P_VIEW_DATAENTRY_BUNDLE_DATA (amounts)
   │
   ▼
4. Response mapped to BundleStandardPeriodDTO
   │
   ▼
5. TypeScript maps to observables
   Knockout updates grid bindings
```

### Save Bundle Data Request

```
1. User edits cell values
   │
   ▼
2. Change tracking captures modified cells
   OriginalAmount vs Amount comparison
   │
   ▼
3. Save triggered
   BundleStandardPeriodHandlers.SaveBundleData
   { CompanyID, Changes: [{ AccountID, Amount, Comment }] }
   │
   ▼
4. Backend validation
   - Period not locked
   - Account is editable
   - Amount within range
   │
   ▼
5. Update TD030B2 (local bundles)
   OR Insert/Update based on existence
   │
   ▼
6. Update company status
   Status_Bundles = 1 (needs re-integration)
```

## Grid Features

### Totals Calculation

```typescript
interface TotalsDataObservable {
    CurrCode: KnockoutObservable<string>;
    NrDec: KnockoutObservable<number>;
    BalanceDebit: KnockoutObservable<number>;
    BalanceCredit: KnockoutObservable<number>;
    PLDebit: KnockoutObservable<number>;
    PLCredit: KnockoutObservable<number>;
    PLINC: KnockoutObservable<number>;     // P&L to Balance
    PLBAL: KnockoutObservable<number>;     // Balance sheet check
    ContingenciesDebit: KnockoutObservable<number>;
    ContingenciesCredit: KnockoutObservable<number>;
}
```

### Validation Indicators

| Indicator | Meaning | Visual |
|-----------|---------|--------|
| HasUnexplainedFlow | Flow breakdown incomplete | Warning icon |
| HasUnexplainedIC | IC breakdown incomplete | Warning icon |
| HasUnexplainedDim | Dimension breakdown incomplete | Warning icon |

### Cell Formatting

```typescript
// Cell styling based on properties
function getCellStyle(cell: ICellsResultObservable): string {
    if (cell.ReadOnly()) return 'cell-readonly';
    if (cell.Amount() !== cell.OriginalAmount()) return 'cell-modified';
    return 'cell-editable';
}
```

## Drill-Down Functionality

### Flow Breakdown

```
Bundle Amount (TD030B2)
        │
        ▼ HasFlows = true
Flow Detail (TD040B2)
├── Opening Balance
├── Increase
├── Decrease
├── Transfer
└── Closing Balance
```

### Intercompany Breakdown

```
IC Amount (TD030I2)
        │
        ▼ HasIntercos = true
Partner Detail
├── Partner A: 100,000
├── Partner B: 250,000
└── Partner C: 75,000
    ─────────────────
    Total: 425,000
```

### Dimensional Breakdown

```
Account Amount (TD030B2)
        │
        ▼ HasDimensions = true
Dimension Detail (TD050B2)
├── Segment A: 500,000
├── Segment B: 300,000
└── Segment C: 200,000
    ─────────────────
    Total: 1,000,000
```

## Excel Integration

### Export Functionality

```csharp
// Export to Excel using Syncfusion XlsIO
public byte[] ExportBundleToExcel(BundleStandardPeriodDTO data)
{
    using (var excelEngine = new ExcelEngine())
    {
        var workbook = excelEngine.Excel.Workbooks.Create(1);
        var sheet = workbook.Worksheets[0];

        // Write header
        sheet.Range["A1"].Text = data.CompanyCode;
        sheet.Range["B1"].Text = data.InputFormName;

        // Write grid data
        int row = 3;
        foreach (var rowData in data.RowsResult)
        {
            sheet.Range[row, 1].Text = rowData.AccountSum;
            sheet.Range[row, 2].Text = rowData.Description;
            // ... cell amounts
            row++;
        }

        return SaveToBytes(workbook);
    }
}
```

### Import Functionality

```csharp
// Import from Excel
public ImportResult ImportBundleFromExcel(Stream fileStream, int companyId)
{
    using (var excelEngine = new ExcelEngine())
    {
        var workbook = excelEngine.Excel.Workbooks.Open(fileStream);
        var sheet = workbook.Worksheets[0];

        var changes = new List<CellChange>();
        // Parse Excel and map to account IDs
        // Validate amounts
        // Return changes for save
    }
}
```

## Entity Locking

### Shared Lock Pattern

```csharp
using (var updateHelper = new EntityUpdateHelper(helper, LockingModes.Shared, db))
{
    // Lock company for data entry
    updateHelper.LockEntity(
        EntityTypes.Company,
        CompanyService.GetEntityKey(consoID, companyId));

    // Retrieve data
    var bundleData = GetBundleData(db, consoId, companyId, inputFormId);

    // Return with entity version
    bundleData.EntityVersion = updateHelper.GetEntityVersions();
}
```

## API Reference

### Frontend-to-API Handlers
| Screen | API Handler | Purpose |
|--------|-------------|---------|
| BundleStandardPeriod | DataEntry_GetData | Load grid data |
| BundleStandardPeriod | DataEntry_SaveData | Save changes |
| Adjustments | Adjustment_GetAdjustments | Load adjustments |
| IntercoDataEntry | IntercoData_GetData | Load IC data |

### Message Handler Mapping
```
Data Entry API Flow:

1. LOAD DATA
   BundleStandardPeriod.ts → BundleStandardPeriod_GetBundleData
   → P_VIEW_DATAENTRY_BUNDLE_* procedures

2. SAVE CHANGES
   BundleStandardPeriod.ts → BundleStandardPeriod_SaveBundleData
   → TD030B2/TD040B2 update
   → Status_Bundles = 1

3. DRILL-DOWN
   HasFlows → Flow detail popup
   HasIntercos → IC detail popup
   HasDimensions → Dimension detail popup
```

### Related API Documentation
- [API Index](../11-agent-support/api-index.yaml) - Master handler catalog
- [Data Import Services](../08-application-layer/data-import-services.md) - Bulk entry alternative

---

## Related Documentation

- [Ownership Screens](ownership-screens.md) - Similar frontend patterns
- [Consolidation Screens](consolidation-screens.md) - Related screen implementation
- [Data Import Services](../08-application-layer/data-import-services.md) - Bulk data entry
- [Data Tables Catalog](../07-database-implementation/data-tables-catalog.md) - Target tables

---
*Document 42 of 50+ | Batch 14: Consolidation Workflow & Reporting | Last Updated: 2024-12-01*
