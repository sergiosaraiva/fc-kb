# Intercompany Transaction Eliminations

## Document Metadata
- **Category**: Elimination Entries
- **Theory Source**: Knowledge base chunks: 0278, 0890, 0027, 0050
- **Implementation Files**:
  - `Sigma.Database/dbo/Stored Procedures/P_CONSO_ELIM.sql`
  - `Sigma.Database/dbo/Stored Procedures/P_CONSO_ELIM_INTERCOMPANY_NETTING.sql`
  - `Sigma.Database/dbo/Stored Procedures/P_CONSO_ELIM_INTERCOMPANY_NETTING_FULL.sql`
  - `Sigma.Database/dbo/Stored Procedures/P_UPDATE_INTERCO.sql`
  - `Sigma.Database/dbo/Stored Procedures/P_REPORT_INTERCO_RECONCILIATION.sql`
- **Last Updated**: 2024-12-01
- **Completeness**: 95% (comprehensive elimination system)
- **Compliance Status**: IFRS 10 compliant - Elimination requirements

## Executive Summary

Intercompany transaction elimination is a **fundamental requirement** of consolidated financial statements. When companies within a group transact with each other (sales, purchases, loans, dividends), these transactions must be eliminated to prevent double-counting and to present the group as a single economic entity.

Prophix.Conso provides a **comprehensive elimination engine** through `P_CONSO_ELIM` that orchestrates multiple specialized elimination procedures, including intercompany netting, participation eliminations, equity eliminations, and minority interest allocations.

## Theoretical Framework

### Concept Definition
From Allen White's "Direct Consolidation":

> Intercompany transactions between group companies must be eliminated because they represent internal movements that would otherwise be double-counted. The consolidated financial statements should present the group as if it were a single company transacting only with third parties.

### Key Principles

1. **Full Elimination**: All intercompany balances and transactions must be eliminated
2. **Matching Required**: Counterparty entries must match (or differences must be reconciled)
3. **Unrealized Profit Elimination**: Profits on intercompany sales not yet realized externally must be eliminated
4. **Deferred vs Reserve Approach**: Group policy choice for handling unrealized profits
5. **Materiality Thresholds**: Practical limits for reconciliation differences

### Types of Intercompany Eliminations

```
1. Balance Sheet Eliminations:
   - Intercompany receivables/payables
   - Intercompany loans
   - Investment in subsidiaries vs subsidiary equity

2. Income Statement Eliminations:
   - Intercompany sales/purchases
   - Intercompany service charges
   - Intercompany interest income/expense
   - Intercompany dividends

3. Unrealized Profit Eliminations:
   - Inventory profit margins
   - Fixed asset transfer gains
   - Deferred income recognition
```

### Elimination Approaches (from Chunk 0278)

**Approach 1: Market Conditions (No Elimination)**
- Transaction at arm's length → may keep profit
- Risk: Distorts consolidated results

**Approach 2: Deferred Income/Expense Method**
- Eliminate profit in seller's books
- Reduce asset value in buyer's books
- Use deferred accounts (reversed on external sale)

**Approach 3: Reserves Method**
- Similar to Approach 2 but uses equity reserves
- Attention needed for different ownership percentages

## Current Implementation

### Database Layer

#### Master Elimination Procedure

`P_CONSO_ELIM` orchestrates all elimination types:

```sql
CREATE procedure [dbo].[P_CONSO_ELIM]
    @UserID int,
    @ConsoID int,
    @CompanyIDs varchar(max),
    @ExecuteDimensions bit,
    @Debug bit = 0,
    @errorinfo xml output

-- Orchestrates the following elimination procedures:
-- 1. P_CONSO_ELIM_PROPORTIONAL    - Proportional method eliminations
-- 2. P_CONSO_ELIM_EQUITYMETHOD    - Equity method eliminations
-- 3. P_CONSO_ELIM_NOTCONSOLIDATED - Non-consolidated company eliminations
-- 4. P_CONSO_ELIM_INTERCOMPANY    - Intercompany transaction eliminations
-- 5. P_CONSO_ELIM_EQUITYCAPITAL   - Equity/capital eliminations
-- 6. P_CONSO_ELIM_PARTICIPATIONS1 - Participation eliminations (owner)
-- 7. P_CONSO_ELIM_PARTICIPATIONS2 - Participation eliminations (owned)
-- 8. P_CONSO_ELIM_MINORITYINTEREST - Minority interest allocation
```

#### Elimination Code System

The system uses codes in `TS070S0` to define elimination rules:

| Code | Type | Description | Selection |
|------|------|-------------|-----------|
| S001 | S | Currency Translation | All Companies |
| S077 | S | Not Consolidated Elimination | N companies |
| S079 | S | Proportional Eliminations | P companies |
| S081 | S | Equity Eliminations | E companies |
| S083 | S | Intercompany Elimination | G,P companies |
| S085 | S | Minority Interest | Global companies |
| S087 | S | Shareholders Funds Eliminations | G,P,E companies |
| S089 | S | Participation Elim (Owner) | G,P,E companies |
| S090 | S | Participation Elim (Owned) | G,P,E companies |

#### Intercompany Netting

`P_CONSO_ELIM_INTERCOMPANY_NETTING` handles the matching and elimination:

```sql
-- Key elimination logic:
-- 1. Identify intercompany account pairs
-- 2. Match receivables against payables
-- 3. Calculate differences
-- 4. Post elimination journal entries
-- 5. Track unreconciled amounts
```

### Deletion Rules (from P_CONSO_ELIM)

The system follows specific rules for journal deletion:

1. **Inactive Eliminations**: Delete all journal entries (unless type used by active elimination)
2. **S090/S094 Eliminations**: Delete journals for companies without ownership relationships
3. **Other Eliminations**: Delete journals for selected companies only
4. **Non-Consolidated**: Always delete journals for ConsolidatedCompany = 0

### Application Layer

Eliminations are triggered via `ConsolidationIntegrationJob`:

```csharp
public enum StoredProcedures : byte
{
    Elims = 0x8,  // Triggers P_CONSO_ELIM
    All = (LinkedCategories | Bundles | Adjustments | Elims)
}

private const string StoredProcedureNameElims = "dbo.P_CONSO_ELIM";
```

### Frontend Layer

**Intercompany Data Entry:**
- Enter intercompany balances by counterparty
- Match transactions before consolidation
- Review differences and adjust

**Intercompany Reports:**
- `P_REPORT_INTERCO_RECONCILIATION` - Reconciliation report
- `P_REPORT_INTERCO_VALIDATION` - Validation report
- `P_VIEW_ICVIEWER` - Interactive IC viewer

## Theory vs Practice Analysis

| Aspect | Theory (Allen White) | Implementation (Prophix.Conso) | Variance |
|--------|---------------------|--------------------------------|----------|
| Full Elimination | Required | Complete implementation | **None** - Aligned |
| Matching | Required | IC reconciliation tools | **Enhanced** |
| Unrealized Profit | Two approaches | Configurable per group | **Aligned** |
| Materiality | Recommended | Configurable thresholds | **Enhanced** |
| Multi-Method Support | Implicit | G,P,E,N differentiation | **Enhanced** |
| Journal Management | Not specified | Sophisticated deletion rules | **Additional** |
| Dimension Support | Not covered | Full dimension elimination | **Additional** |

## Gap Analysis

### Missing Elements
- [ ] **None identified** - Intercompany elimination is comprehensive

### Divergent Implementation
- **Journal Deletion Logic**: More sophisticated than basic theory (handles inactive/active scenarios)
- **Method-Specific Eliminations**: Theory treats generically; implementation has specific procedures per method

### Additional Features (Beyond Theory)
- ✅ **Intercompany Viewer**: Interactive IC balance viewer
- ✅ **Reconciliation Reports**: Detailed matching analysis
- ✅ **Validation Reports**: Pre-consolidation IC checks
- ✅ **Dimension-Level Elimination**: Break down by dimensions
- ✅ **Configurable Thresholds**: Materiality settings per group
- ✅ **Multi-Method Handling**: Different procedures for G/P/E/N
- ✅ **Netting Options**: Full netting vs partial

## Business Impact

### Current Capabilities
- Full intercompany elimination across all methods
- Sophisticated reconciliation and matching tools
- Audit trail through dedicated journal types
- Configurable materiality thresholds
- Support for complex multi-company structures

### Operational Considerations
- **Data Quality**: IC balances must be entered accurately
- **Reconciliation**: Differences should be resolved before consolidation
- **Thresholds**: Define appropriate materiality limits
- **Timing**: Ensure both parties report same amounts

## Best Practices (from Chunk 0890)

1. **Define Thresholds**: Set materiality limits for IC differences
   - Balance sheet threshold
   - P&L threshold
   - Year-end may require zero tolerance

2. **Group Procedures**: Document elimination policies
   - Gain on asset disposal method (Deferred vs Reserve)
   - Get auditor approval
   - Use single language for communication

3. **Incremental Documentation**: Build procedures file over time
   - Add new procedures as situations arise
   - Review and approve with auditors

## Recommendations

1. **Pre-Validation**: Implement mandatory IC reconciliation check before consolidation
2. **Threshold Alerts**: Add warnings when IC differences exceed thresholds
3. **Automated Matching**: Consider AI-assisted matching for high-volume IC
4. **Historical Tracking**: Enhanced view of IC elimination history

## API Reference

### Primary API Handlers
| Handler | YAML File | Purpose | Status |
|---------|-----------|---------|--------|
| `Consolidation_Execute` | [api-consolidation-endpoints.yaml](../11-agent-support/api-consolidation-endpoints.yaml) | Trigger P_CONSO_ELIM (master eliminator) | ✅ IMPLEMENTED |
| `IntercoDataEntry_GetData` | [api-interco-endpoints.yaml](../11-agent-support/api-interco-endpoints.yaml) | Get intercompany balances | ✅ IMPLEMENTED |
| `IntercoDataEntry_SaveData` | [api-interco-endpoints.yaml](../11-agent-support/api-interco-endpoints.yaml) | Enter IC transaction amounts | ✅ IMPLEMENTED |

### Supporting API Handlers
| Handler | YAML File | Purpose |
|---------|-----------|---------|
| `IntercoMatching_GetMatchingStatus` | [api-interco-endpoints.yaml](../11-agent-support/api-interco-endpoints.yaml) | Verify IC transaction matching |
| `Report_ExecuteReport` | [api-reports-endpoints.yaml](../11-agent-support/api-reports-endpoints.yaml) | P_REPORT_INTERCO_RECONCILIATION |
| `Elimination_GetEliminations` | [api-elimination-endpoints.yaml](../11-agent-support/api-elimination-endpoints.yaml) | Get IC elimination details |

### Elimination Code Reference
| Code | Procedure | Purpose |
|------|-----------|---------|
| S077 | P_CONSO_ELIM_NOTCONSOLIDATED | Non-consolidated eliminations |
| S079 | P_CONSO_ELIM_PROPORTIONAL | Proportional method eliminations |
| S081 | P_CONSO_ELIM_EQUITYMETHOD | Equity method eliminations |
| S083 | P_CONSO_ELIM_INTERCOMPANY | Intercompany netting |
| S085 | P_CONSO_ELIM_MINORITYINTEREST | Minority interest allocation |

### API Workflow
```
Intercompany Elimination via API:

1. DATA ENTRY
   IntercoDataEntry_SaveData → Enter IC balances:
     - Receivables/Payables by counterparty
     - Sales/Purchases by counterparty
     - Loans/Borrowings by counterparty

2. MATCHING VERIFICATION
   IntercoMatching_GetMatchingStatus → Check reconciliation:
     - Identify differences
     - Review threshold compliance

3. ELIMINATION EXECUTION
   Consolidation_Execute → P_CONSO_ELIM orchestrates:
     - P_CONSO_ELIM_INTERCOMPANY_NETTING
     - P_CONSO_ELIM_INTERCOMPANY_NETTING_FULL
     - Method-specific eliminations (S077, S079, S081, S083)

4. VALIDATION
   Report_ExecuteReport (IC Reconciliation) → Verify:
     - Matching status
     - Residual differences
     - Elimination completeness
```

### Implementation Status
| Feature | Status | Notes |
|---------|--------|-------|
| IC balance elimination | ✅ IMPLEMENTED | P_CONSO_ELIM_INTERCOMPANY_NETTING |
| IC netting (full) | ✅ IMPLEMENTED | P_CONSO_ELIM_INTERCOMPANY_NETTING_FULL |
| Multi-method support | ✅ IMPLEMENTED | G/P/E/N differentiation |
| Reconciliation reports | ✅ IMPLEMENTED | P_REPORT_INTERCO_RECONCILIATION |
| Dimension-level elimination | ✅ IMPLEMENTED | Extended elimination support |

### Related API Documentation
- [API Index](../11-agent-support/api-index.yaml) - Master handler catalog
- [Gap Analysis](../11-agent-support/gap-analysis-report.yaml) - **FULLY IMPLEMENTED (95%)**

---

## Related Documentation
- See also: [Global Integration](../02-consolidation-methods/global-integration.md)
- See also: [Minority Interest](../03-core-calculations/minority-interest.md)
- Knowledge Base: Chunks 0278, 0890
- Code: `P_CONSO_ELIM.sql:1-80`

## Appendix: Elimination Journal Flow

```
Consolidation Run
      │
      ▼
P_CONSO_ELIM (Master)
      │
      ├──► P_CONSO_ELIM_PROPORTIONAL
      │
      ├──► P_CONSO_ELIM_EQUITYMETHOD
      │
      ├──► P_CONSO_ELIM_NOTCONSOLIDATED
      │
      ├──► P_CONSO_ELIM_INTERCOMPANY ◄── Intercompany netting
      │
      ├──► P_CONSO_ELIM_EQUITYCAPITAL
      │
      ├──► P_CONSO_ELIM_PARTICIPATIONS1 (Owner)
      │
      ├──► P_CONSO_ELIM_PARTICIPATIONS2 (Owned)
      │
      └──► P_CONSO_ELIM_MINORITYINTEREST
```

---
*Document 5 of 50+ | Batch 2: Core Calculations | Last Updated: 2024-12-01*