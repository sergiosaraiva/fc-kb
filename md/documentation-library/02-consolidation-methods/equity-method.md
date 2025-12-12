# Equity Method (Significant Influence)

## Document Metadata
- **Category**: Consolidation Method
- **Theory Source**: Knowledge base chunks: 0042, 0048, 0076, 0055, 0073, 0081
- **Implementation Files**:
  - `Sigma.Database/dbo/Stored Procedures/P_CONSO_ELIM_EQUITYMETHOD.sql`
  - `Sigma.Database/InitializationScript.sql` (TS070S1 - ConsoMethodSelection 'E')
  - `Sigma.Database/dbo/Stored Procedures/P_CONSO_ELIM.sql`
- **Last Updated**: 2024-12-01
- **Completeness**: 95% (comprehensive implementation)
- **Compliance Status**: IAS 28 compliant - Investments in Associates

## Executive Summary

The Equity Method is used when an investor has **significant influence** over an investee but not control. Typically, this applies when ownership is between **20% and 50%** of voting rights. Under this method, the investment is initially recorded at cost and subsequently adjusted for the investor's share of the investee's profits or losses.

Prophix.Conso implements the Equity Method as consolidation method code 'E', with dedicated elimination procedures (`P_CONSO_ELIM_EQUITYMETHOD`) that handle the single-line presentation of associates in the consolidated financial statements.

## Theoretical Framework

### Concept Definition
From Allen White's "Direct Consolidation":

> We speak of **significant influence** when a parent company, directly and/or indirectly, holds investments in the capital of another company, forming together a percentage of detention between a commonly accepted range of **20% and 50%**. In this case, it is common to refer to the company as an **associated company** instead of a subsidiary.

### Key Principles

1. **Significant Influence Threshold**: 20-50% ownership presumed to indicate significant influence
2. **Single-Line Consolidation**: Only investment balance and share of profit shown (not line-by-line)
3. **Equity Pickup**: Investment adjusted for share of associate's profits/losses
4. **No Full Consolidation**: Assets, liabilities, income, expenses NOT consolidated line-by-line
5. **Elimination of Unrelated Accounts**: 100% of A/L eliminated except for equity portion

### Ownership Thresholds (from Chunk 0048)

```
┌──────────────────────────────────────────────────────────────┐
│                    OWNERSHIP THRESHOLDS                       │
├──────────────────────────────────────────────────────────────┤
│  > 50%     │  Control              → Global Integration      │
│  20-50%    │  Significant Influence → Equity Method          │
│  < 20%     │  Financial Investment  → Cost Method            │
└──────────────────────────────────────────────────────────────┘
```

### Formula/Algorithm

```
Equity Method Accounting:

Initial Recognition:
  Investment = Cost of Acquisition

Subsequent Measurement:
  Investment = Cost + Share of Profits - Dividends Received

Share of Profit:
  Equity Pickup = Ownership % × Associate Net Income

Balance Sheet Presentation:
  Single line: "Investment in Associates" = Adjusted Investment Value

P&L Presentation:
  Single line: "Share of Profit from Associates" = Equity Pickup

Elimination Logic (from Chunk 0042):
  - Eliminate 100% of all A/L accounts (associate not consolidated)
  - Except: Equity eliminated for % NOT belonging to group
```

### Example (from Chunk 0076)

```
Company A owns:
  - 80% of Company B (Global Integration)
  - 8% direct in Company C

Company B owns:
  - 15% in Company C

Company A's effective holding in C:
  Direct: 8%
  Indirect via B: 80% × 15% = 12%
  Total: 8% + 12% = 20% → borderline significant influence

Result: C consolidated using Equity Method
```

## Current Implementation

### Database Layer

#### Consolidation Method Code

The system uses code 'E' for Equity Method in `TS070S1`:

```sql
-- From InitializationScript.sql
INSERT [TS070S1] VALUES (6, 6, N'ConsolidationMethod_EquityOnly', 0, N'E', N'E', ...);

-- Method Selection Codes:
-- 'G' = Global Integration
-- 'P' = Proportional Integration
-- 'E' = Equity Method ← This method
-- 'N' = Not Consolidated
```

#### Equity Method Elimination Procedure

`P_CONSO_ELIM_EQUITYMETHOD` handles the specific elimination:

```sql
CREATE procedure [dbo].[P_CONSO_ELIM_EQUITYMETHOD]
    @Login nvarchar(256),
    @SessionID int,
    @ConsoID int,
    @RefConsoID int,
    @PreviousPeriodAdjFlowID int,
    @ConsoCurrCode nvarchar(3),
    @ParentCompanyID int,
    @JournalTypeS001ID int,
    @UNEXPVarFlowID int,
    @NETVarFlowID int,
    @ExecuteDimensions bit,
    @Debug bit,
    @errorinfo xml output
as begin
    -- Key accounts for equity method
    declare @EquityValAccountID int     -- Investment in Associate
    declare @EquityProfitAccountID int  -- Share of Profit
    declare @EquityLossAccountID int    -- Share of Loss
    declare @PLINCAccountID int         -- P&L Impact account

    -- Process Step 1: Get S081 elimination record
    -- Process Step 2: Eliminate all A/L except equity portion
    -- Process Step 3: Record equity pickup
end
```

#### Elimination Code S081

The system uses code S081 for equity method eliminations:

```sql
-- From TS070S0
ElimCode = 'S081'
ElimText = 'Equity eliminations'
ProcedureName = 'P_CONSO_ELIM_EQUITYMETHOD'
ConsoMethodSelectionID = 6  -- Equity Only
```

### Integration in Elimination Flow

`P_CONSO_ELIM` orchestrates the equity method as part of the full elimination process:

```sql
-- Within P_CONSO_ELIM
-- Step 2: Equity Method Eliminations
EXEC P_CONSO_ELIM_EQUITYMETHOD
    @Login, @SessionID, @ConsoID, @RefConsoID, ...
```

### Application Layer

The equity method is selected in company configuration:

```csharp
// ConsolidationIntegrationJob.cs triggers P_CONSO_ELIM
// which includes P_CONSO_ELIM_EQUITYMETHOD for 'E' companies
```

### Frontend Layer

- **Company Setup**: Select 'E' as consolidation method
- **Ownership Data Entry**: Record ownership percentage (20-50%)
- **Consolidation Reports**: View equity pickup in consolidated statements

## Theory vs Practice Analysis

| Aspect | Theory (Allen White) | Implementation (Prophix.Conso) | Variance |
|--------|---------------------|--------------------------------|----------|
| Threshold | 20-50% | Configurable per company | **Flexible** |
| Method Code | "Equity Method" | Code 'E' | Naming only |
| Single-Line | Investment + Share of Profit | Full implementation | **None** - Aligned |
| Elimination | 100% except equity | Procedure S081 | **None** - Aligned |
| Profit/Loss | Single share | Separate accounts | **Enhanced** |
| Period Changes | Track movement | Reference period comparison | **Enhanced** |
| Dimensions | Not covered | Full dimension support | **Additional** |

## Gap Analysis

### Missing Elements
- [ ] **IFRS 11 Joint Venture Distinction**: Theory combines JV and Associates; IFRS 11 may require different handling (noted in missing-features.md)

### Divergent Implementation
- **Separate Profit/Loss Accounts**: Theory uses single "share of profit"; implementation separates profit and loss accounts for more granular reporting

### Additional Features (Beyond Theory)
- ✅ **Reference Period Tracking**: Compare equity pickup between periods
- ✅ **Dimension-Level Calculation**: Break down by dimensions
- ✅ **Configurable Thresholds**: Can override 20-50% if justified
- ✅ **Journal Integration**: Dedicated journal type (S081)
- ✅ **Rounding Control**: Period-specific decimal precision

## Business Impact

### Current Capabilities
- Full IAS 28 compliant equity method
- Support for complex indirect ownership calculations
- Audit trail through dedicated journal types
- Period-over-period movement analysis

### Operational Considerations
- Ensure ownership percentages are accurate (especially indirect)
- Review equity pickup calculations for reasonableness
- Monitor significant influence indicators beyond just percentage

## Recommendations

1. **IFRS 11 Review**: Verify joint venture treatment aligns with current standards
2. **Influence Indicators**: Add checklist for significant influence beyond ownership %
3. **Impairment Monitoring**: Add alert when associate has persistent losses
4. **Visualization**: Show indirect ownership path in ownership structure

## API Reference

### Primary API Handlers
| Handler | YAML File | Purpose | Status |
|---------|-----------|---------|--------|
| `Consolidation_Execute` | [api-consolidation-endpoints.yaml](../11-agent-support/api-consolidation-endpoints.yaml) | Execute consolidation (includes S081 for method E) | ✅ IMPLEMENTED |
| `Ownership_GetOwnership` | [api-ownership-endpoints.yaml](../11-agent-support/api-ownership-endpoints.yaml) | Get ownership 20-50% for equity method | ✅ IMPLEMENTED |
| `Company_SaveCompany` | [api-company-endpoints.yaml](../11-agent-support/api-company-endpoints.yaml) | Set ConsoMethod='E' | ✅ IMPLEMENTED |

### Supporting API Handlers
| Handler | YAML File | Purpose |
|---------|-----------|---------|
| `Event_GetEvents` | [api-event-endpoints.yaml](../11-agent-support/api-event-endpoints.yaml) | Get equity method events |
| `Elimination_GetEliminations` | [api-elimination-endpoints.yaml](../11-agent-support/api-elimination-endpoints.yaml) | Get S081 equity eliminations |
| `Report_ExecuteReport` | [api-reports-endpoints.yaml](../11-agent-support/api-reports-endpoints.yaml) | Generate equity method reports |

### API Workflow
```
1. Company_SaveCompany (ConsoMethod='E') → Set equity method
2. Ownership_SaveOwnership → Record 20-50% ownership
3. Consolidation_Execute → S081 equity eliminations
4. Report_ExecuteReport → Investment in Associates line
```

### Related API Documentation
- [API Index](../11-agent-support/api-index.yaml) - Master handler catalog
- [Gap Analysis](../11-agent-support/gap-analysis-report.yaml) - Theory alignment: **IAS 28 compliant**

---

## See Also

### Related Consolidation Methods
- [Global Integration](global-integration.md) - >50% control (full consolidation)
- [Proportional Method](proportional-method.md) - 50% joint control
- [Method Determination](consolidation-method-determination.md) - Threshold-based assignment

### Related Calculations & Eliminations
- [Step Acquisition](../03-core-calculations/step-acquisition.md) - E→G method transitions
- [Dividend Eliminations](../04-elimination-entries/dividend-eliminations.md) - DivReceivedEquity treatment
- [Intercompany Transactions](../04-elimination-entries/intercompany-transactions.md) - IC eliminations

### Related Ownership
- [Control vs Ownership](../06-ownership-structure/control-vs-ownership.md) - Influence determination
- [Voting Rights Analysis](../06-ownership-structure/voting-rights-analysis.md) - Control percentage

### Navigation
- [Cross-Reference Index](../00-index/CROSS_REFERENCE_INDEX.md) - Full document relationships
- [Executive Summary](../00-index/EXECUTIVE_SUMMARY.md) - Overview

### Technical References
- Knowledge Base: Chunks 0042, 0048, 0076
- Code: `P_CONSO_ELIM_EQUITYMETHOD.sql:25-60`

## Appendix: Equity Method vs Global Integration Comparison

| Feature | Global Integration (G) | Equity Method (E) |
|---------|----------------------|-------------------|
| Ownership | >50% | 20-50% |
| Assets/Liabilities | Line-by-line 100% | Single line (Investment) |
| Income/Expenses | Line-by-line 100% | Single line (Share of profit) |
| Minority Interest | Calculated | N/A |
| Intercompany Elimination | Required | Limited (only with group) |
| Full Consolidation | Yes | No |
| Presentation | All accounts | Two accounts only |

---
*Document 6 of 50+ | Batch 2: Core Calculations | Last Updated: 2024-12-01*