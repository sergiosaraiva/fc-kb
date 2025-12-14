# Reporting Services: Application Layer Architecture

## Document Metadata
- **Category**: Application Layer
- **Theory Source**: Implementation-specific (Financial reporting architecture)
- **Implementation Files**:
  - `Sigma.Database/dbo/Stored Procedures/P_REPORT_*.sql` - 179+ report procedures
  - `Sigma.Mona.WebApplication/Screens/Report*/` - Report screen components
  - `Sigma.Mona.WebApplication/UserControls/Reports/` - Report definitions
  - `Sigma.Database/dbo/Views/V_REPORT_*.sql` - Report views
- **Last Updated**: 2024-12-01
- **Completeness**: 100% (Comprehensive reporting architecture)
- **Compliance Status**: Architecture reference document

## Executive Summary

The Prophix.Conso reporting services provide a comprehensive framework for generating financial reports, analysis outputs, and data extracts. With 179+ stored procedures supporting 200+ report types, the system covers standard financial statements, cross-tabulation analysis, audit trails, and custom reports. Reports are generated via DevExpress controls with multi-language support and flexible parameterization.

## Reporting Architecture Overview

### Report Processing Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                    User Report Request                           │
│  - Report selection via menu                                     │
│  - Parameter configuration (period, company, format)             │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Report Controller                             │
│  - Validate parameters                                           │
│  - Check access rights                                           │
│  - Route to appropriate service                                  │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    P_REPORT_* Procedures                         │
│  - Execute report logic                                          │
│  - Query consolidated data (TD035C2, TD045C2)                   │
│  - Apply translations via GetMessageValue()                      │
│  - Return structured result sets                                 │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    DevExpress Report Viewer                      │
│  - Render report grid/chart                                      │
│  - Export to Excel, PDF, CSV                                     │
│  - Print functionality                                           │
└─────────────────────────────────────────────────────────────────┘
```

## Report Procedure Catalog

### Report Categories

| Category | Procedure Count | Examples | Business Purpose |
|----------|-----------------|----------|------------------|
| **Standard Reports** | ~40 | P_REPORT_ACCOUNT, P_REPORT_COMPANY | Core financial data |
| **Cross-Tabulation** | ~60 | P_REPORT_CROSS_* | Multi-dimensional analysis |
| **General Ledger** | ~15 | P_REPORT_GENERAL_LEDGER* | Transaction detail |
| **Custom Reports** | ~25 | P_REPORT_CUSTOM_REPORT_* | User-defined reports |
| **Audit Reports** | ~20 | P_REPORT_CROSS_AUDIT_* | Compliance & reconciliation |
| **Elimination Reports** | ~10 | P_REPORT_ELIMINATIONS* | Consolidation transparency |
| **Analysis Reports** | ~30 | P_REPORT_*_ANALYSIS* | Variance & trend analysis |

### Standard Report Procedures

#### P_REPORT_CONSOLIDATION_SUMMARY

**Purpose**: Master consolidated financial statement

```sql
CREATE PROCEDURE [dbo].[P_REPORT_CONSOLIDATION_SUMMARY]
    @CustomerID int,
    @ConsoID int,
    @DataLanguageLCID int,
    @AccountSummationID int,
    @CompanyFilterMode smallint,       -- 0=All, 1=Selected
    @CompanyFilterIDs nvarchar(max),   -- Comma-separated
    @IncludeJournalTypes nvarchar(max), -- Journal filter
    @GroupByCompany bit = 0,
    @ShowVariance bit = 0
```

**Output Columns**:
- AccountCode, AccountName
- OpeningBalance, Movement, ClosingBalance
- CurrentPeriod, ReferencePeriod, Variance

#### P_REPORT_GOODWILL

**Purpose**: Goodwill calculation and movement analysis

**Key Data Sources**:
- TS014C0 (Company acquisition data)
- TD035C2 (Consolidated equity)
- TS015S0 (Ownership percentages)

#### P_REPORT_ELIMINATIONS

**Purpose**: Detailed elimination entry report

**Shows**:
- Journal entries by elimination type
- Debit/Credit amounts
- Partner company details
- Elimination codes and descriptions

### Cross-Tabulation Reports (P_REPORT_CROSS_*)

#### Report Structure Pattern

All cross-tab reports follow consistent parameter pattern:

```sql
CREATE PROCEDURE [dbo].[P_REPORT_CROSS_*]
    @CustomerID int,
    @ConsoID int,
    @DataLanguageLCID int,
    -- Row dimension
    @RowSummationID int,           -- Account/Flow summation
    @RowDetailLevel tinyint,       -- 0=Summary, 1=Detail
    -- Column dimension
    @ColDimension tinyint,         -- 1=Company, 2=Currency, 3=Period
    @ColFilterIDs nvarchar(max),
    -- Data selection
    @JournalTypeFilter nvarchar(50),
    @ShowIntercompany bit,
    @ShowMinority bit
```

#### Key Cross-Tab Reports

| Procedure | Row Axis | Column Axis | Purpose |
|-----------|----------|-------------|---------|
| P_REPORT_CROSS_ACCOUNT_ACCOUNTSFLOWS | Accounts | Flows | Account movement analysis |
| P_REPORT_CROSS_ACCOUNT_CONSOLIDATEDACCOUNTS | Accounts | Companies | Company contribution |
| P_REPORT_CROSS_BUNDLE_INTERCOMPANIES | IC Accounts | Partners | IC reconciliation |
| P_REPORT_CROSS_GROUP_COMPANIES | Companies | Attributes | Group structure |
| P_REPORT_CROSS_AUDIT_BYCOMPANY | Companies | Journals | Audit by company |

### Header/Detail Pattern

Most reports use header + detail procedure pairs:

```sql
-- Header: Report metadata and parameters
P_REPORT_CONSOLIDATION_SUMMARY_HEADER
    @CustomerID, @ConsoID, @DataLanguageLCID
    -- Returns: Report title, period info, parameters

-- Detail: Actual report data
P_REPORT_CONSOLIDATION_SUMMARY
    @CustomerID, @ConsoID, @DataLanguageLCID, ...
    -- Returns: Report rows with amounts
```

## Report Service Layer

### Message Handler Pattern

```csharp
// ReportService.cs - Message handler pattern
internal static void GetReportData(SessionController helper,
    Message requestMessage, Message responseMessage)
{
    using var db = DAOFactory.CreateDataContext();

    // Access control
    helper.EnsureAccessRight(db, UserActions.Report_View);

    // Parameter extraction
    var consoId = helper.WorkingConsoID;
    var reportType = requestMessage.GetInt("ReportType");
    var parameters = ExtractReportParameters(requestMessage);

    // Execute report procedure
    var results = db.P_REPORT_CONSOLIDATION_SUMMARY(
        helper.UserCustomerID,
        consoId,
        helper.DataLanguageLCID,
        parameters.AccountSummationID,
        parameters.CompanyFilterMode,
        parameters.CompanyFilterIDs,
        parameters.JournalTypeFilter,
        parameters.GroupByCompany,
        parameters.ShowVariance
    );

    // Return structured data
    responseMessage["scf_items"] = results.ToList();
}
```

### Report DTOs

```csharp
public class ReportRowDTO
{
    public string AccountCode { get; set; }
    public string AccountName { get; set; }
    public int IndentLevel { get; set; }
    public bool IsBold { get; set; }
    public decimal? Amount { get; set; }
    public decimal? VarianceAmount { get; set; }
    public decimal? VariancePercent { get; set; }
}

public class ReportHeaderDTO
{
    public string ReportTitle { get; set; }
    public string PeriodDescription { get; set; }
    public string CompanyFilter { get; set; }
    public DateTime GeneratedDate { get; set; }
}
```

## Multi-Language Support

### Translation Integration

```sql
-- Report procedures use GetMessageValue() for translations
SELECT
    AccountCode,
    dbo.GetMessageValue(AccountDescriptionID, @DataLanguageLCID) AS AccountName,
    Amount
FROM TD035C2
INNER JOIN TS010S0 ON ...
```

### Language Parameter Flow

```
User Language Setting (UI)
        │
        ▼
@DataLanguageLCID (Parameter)
        │
        ▼
GetMessageValue() (Translation lookup)
        │
        ▼
T_TRANSLATION (Translation table)
        │
        ▼
Localized Report Output
```

## Report Export Functionality

### Supported Formats

| Format | Export Method | Use Case |
|--------|---------------|----------|
| Excel (XLSX) | Syncfusion XlsIO | Data analysis |
| PDF | DevExpress PDF | Official documents |
| CSV | Direct export | Data integration |
| HTML | Report viewer | Web display |

### Export Service Pattern

```csharp
public class ReportExportService
{
    public byte[] ExportToExcel(ReportData data, ExportOptions options)
    {
        using (var excelEngine = new ExcelEngine())
        {
            var workbook = excelEngine.Excel.Workbooks.Create(1);
            var sheet = workbook.Worksheets[0];

            // Header row
            WriteReportHeader(sheet, data.Header);

            // Data rows
            WriteReportData(sheet, data.Rows);

            // Formatting
            ApplyReportFormatting(sheet, options);

            return SaveToStream(workbook);
        }
    }
}
```

## Custom Report Framework

### SETUP_TS018* Tables

Custom reports defined in setup tables:

| Table | Purpose |
|-------|---------|
| SETUP_TS018S0 | Custom report definitions |
| SETUP_TS018S1 | Report descriptions (multi-language) |
| SETUP_TS018S2 | Report column definitions |
| SETUP_TS018S3 | Column detail configuration |
| SETUP_TS018C1 | Consolidation difference reports |
| SETUP_TS018C2 | Minority interest reports |

### Custom Report Types

| Report Type | P_REPORT_CUSTOM_REPORT_* | Purpose |
|-------------|--------------------------|---------|
| Flow | P_REPORT_CUSTOM_REPORT_DEFINITION_FLOW | Cash flow statements |
| Dimension | P_REPORT_CUSTOM_REPORT_DEFINITION_DIMENSION | Dimensional analysis |
| Cashflow | P_REPORT_CUSTOM_REPORT_DEFINITION_CASHFLOW | Cash flow specific |
| Contribution | P_REPORT_CUSTOM_REPORT_DEFINITION_*_CONTRIBUTION | Company contribution |

## Report Views

### Supporting Views

```sql
-- V_REPORT_ACCOUNTSUMMATION
-- Flattened account summation hierarchy for reporting
CREATE VIEW [dbo].[V_REPORT_ACCOUNTSUMMATION] AS
SELECT
    ConsoID, AccountSummationID,
    AccountCode, AccountName,
    ParentSummationID, IndentLevel,
    SortOrder, IsTotal
FROM TS010G0
```

### Key Report Views

| View | Purpose | Used By |
|------|---------|---------|
| V_REPORT_ACCOUNTSUMMATION | Account hierarchy | Most reports |
| V_JOURNALTYPE | Journal type lookup | Elimination reports |
| V_COMPANYLIST | Company selection | Company filters |

## Performance Optimization

### Query Optimization Patterns

```sql
-- Index hints for large datasets
SELECT ...
FROM TD035C2 WITH (INDEX(IX_TD035C2))
WHERE ConsoID = @ConsoID

-- OPTION RECOMPILE for variable parameters
SELECT ... WHERE CompanyID IN (...)
OPTION (RECOMPILE)
```

### Caching Strategy

| Cache Level | Implementation | TTL |
|-------------|----------------|-----|
| Report definitions | Application cache | Session |
| Translation values | Memory cache | 15 min |
| Exchange rates | Request scope | Request |

## API Reference

### Primary API Handlers
| Handler | YAML File | Purpose | Status |
|---------|-----------|---------|--------|
| `Report_ExecuteReport` | [api-reports-endpoints.yaml](../11-agent-support/api-reports-endpoints.yaml) | Execute P_REPORT_* procedures | ✅ IMPLEMENTED |
| `Report_GetReportDefinitions` | [api-reports-endpoints.yaml](../11-agent-support/api-reports-endpoints.yaml) | Get SETUP_TS018* config | ✅ IMPLEMENTED |
| `Report_ExportReport` | [api-reports-endpoints.yaml](../11-agent-support/api-reports-endpoints.yaml) | Export to Excel/PDF | ✅ IMPLEMENTED |

### Report Category Handlers
| Category | Handler Pattern | Procedure Pattern |
|----------|-----------------|-------------------|
| Standard | Report_ConsolidationSummary | P_REPORT_CONSOLIDATION_SUMMARY |
| Cross-Tab | Report_CrossAccount* | P_REPORT_CROSS_* |
| Audit | Report_Audit* | P_REPORT_CROSS_AUDIT_* |
| Custom | Report_CustomReport* | P_REPORT_CUSTOM_REPORT_* |

### API Workflow
```
Report Generation via API:

1. REPORT SELECTION
   Report_GetReportDefinitions → Available reports

2. PARAMETER CONFIGURATION
   Report_GetParameters → Report parameters
   → ConsoID, CompanyFilter, JournalFilter, etc.

3. EXECUTION
   Report_ExecuteReport → P_REPORT_*
   → Returns structured result sets

4. EXPORT
   Report_ExportReport → Excel/PDF/CSV
```

### Related API Documentation
- [API Index](../11-agent-support/api-index.yaml) - Master handler catalog
- [Gap Analysis](../11-agent-support/gap-analysis-report.yaml) - **FULLY IMPLEMENTED (100%)**

---

## Related Documentation

- [Consolidation Workflow](../03-core-calculations/consolidation-workflow.md) - Data source processing
- [Data Tables Catalog](../07-database-implementation/data-tables-catalog.md) - Report data sources
- [Stored Procedures Catalog](../07-database-implementation/stored-procedures-catalog.md) - Procedure reference
- [Consolidation Screens](../09-frontend-implementation/consolidation-screens.md) - Report UI

---
*Document 41 of 50+ | Batch 14: Consolidation Workflow & Reporting | Last Updated: 2024-12-01*
