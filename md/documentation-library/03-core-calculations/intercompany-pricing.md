# Intercompany Pricing: Transfer Pricing and Stock Margins in Consolidation

## Document Metadata
- **Category**: Core Calculations
- **Theory Source**: Knowledge base chunks: 0284, 0285, 0286, 0287, 0288, 0357, 0921
- **Implementation Files**:
  - `Sigma.Database/dbo/Tables/TS070S0.sql` - User elimination configuration
  - `Sigma.Database/dbo/Tables/TS071S0.sql` - Elimination detail mapping
  - `Sigma.Database/dbo/Stored Procedures/P_CONSO_ELIM_USER.sql` - User elimination execution
  - `Sigma.Database/dbo/Tables/TD030I2.sql` - Intercompany closing amounts
  - `Sigma.Database/dbo/Tables/TD040I2.sql` - Intercompany flow amounts
- **Last Updated**: 2024-12-01
- **Completeness**: 70% (Framework exists; automatic margin detection not implemented)
- **Compliance Status**: PARTIAL - Manual configuration required for stock margin eliminations

## Executive Summary

Intercompany pricing (transfer pricing) and stock margin elimination address the accounting treatment of unrealized profits arising from intercompany transactions. When one group company sells inventory to another at a markup, the profit is "unrealized" from the group perspective until the inventory is sold to external parties. Prophix.Conso provides a **configurable framework** for stock margin eliminations through the User Elimination system (TS070S0/TS071S0), but **does not automatically detect or calculate** intercompany margins.

## Theoretical Framework

### The Stock Margin Problem

From Allen White's "Direct Consolidation" (Chunk 284):

> "In most of the industrial groups, some companies are dedicated to supply on the market and make products and some other companies are dedicated to sell these products. In such situation, the normal practice for the industrial companies is to sell the products to the commercial companies, including a benefit called stocks margin."

### Transaction Flow

```
Company A (Manufacturer)              Company B (Distributor)
┌─────────────────────────┐          ┌─────────────────────────┐
│ Cost of Goods: 300      │          │ Purchased from A: 350   │
│ Sold to B: 350          │  ──────► │ Inventory Value: 350    │
│ Margin: 50              │          │ Sold to Market: ?       │
└─────────────────────────┘          └─────────────────────────┘

                                     Margin still in B's inventory
```

### Group Perspective

- **Statutory View**: A has profit of 50, B has inventory of 350
- **Group View**: Combined inventory should be at group cost (300)
- **Unrealized Profit**: 50 must be eliminated until sold externally

### Year-over-Year Dynamics (Chunks 285-288)

**Year 1 - Initial Elimination**:
```
Statutory:                    Consolidated:
A: Sales to B = 350          Eliminate IC Sales: (50)
A: Profit = 50               Reduce Inventory: (50)
B: Inventory = 350           Credit Reserves: 50
                             Net Profit Impact: (50)
```

**Year 2 - Carry Forward and New Margin**:
```
New Transaction:
A: Sales to B = 460 (cost 400, margin 60)

Prior Year Stock Sold:
B sold Year 1 inventory to market

Consolidation Adjustments:
1. Reverse prior year: +50 to profit (stocks sold)
2. Eliminate current year: (60) new margin
Net Impact: (10) = (60) + 50
```

### Key Insight (Chunk 288)

> "After Year 1, and forever, if the stocks margins are relatively similar each year, the impact on the profit cannot be significant (-10 in our case study). That's why we recommend simulating figures before taking such decision."

## Current Implementation

### User Elimination Framework

Stock margin eliminations in Prophix.Conso are configured through the User Elimination system:

```sql
-- Header: TS070S0
CREATE TABLE [dbo].[TS070S0] (
    [EliminationHeaderID]     INT            IDENTITY NOT NULL,
    [ConsoID]                 INT            NOT NULL,
    [ElimCode]                NVARCHAR (4)   NOT NULL,   -- e.g., 'U020'
    [ElimType]                CHAR (1)       NOT NULL,   -- 'U' = User
    [ElimText]                NVARCHAR (25)  NOT NULL,
    [Active]                  BIT            NOT NULL,
    [Behaviour]               TINYINT        NOT NULL,   -- 3 for both periods
    [JournalTypeID]           INT            NOT NULL,
    [ConsoMethodSelectionID]  INT            NOT NULL,   -- Company selection
    [MinorityFlag]            BIT            NOT NULL
);

-- Detail: TS071S0
CREATE TABLE [dbo].[TS071S0] (
    [EliminationDetailID]     INT            IDENTITY NOT NULL,
    [EliminationHeaderID]     INT            NOT NULL,
    [LineNr]                  SMALLINT       NOT NULL,
    [FromType]                TINYINT        NOT NULL,   -- 4/5 = Intercompany
    [FromAccountID]           INT            NULL,
    [FromPeriod]              CHAR (1)       NOT NULL,   -- C/R
    [ToType]                  TINYINT        NOT NULL,
    [ToAccountID]             INT            NULL,
    [ToSign]                  SMALLINT       NOT NULL,
    [Percentage]              TINYINT        NOT NULL
);
```

### Data Sources for Stock Margins

| Table | Purpose | Key Columns |
|-------|---------|-------------|
| TD030I2 | IC closing amounts | CompanyID, PartnerCompanyID, AccountID, Amount |
| TD040I2 | IC flow amounts | FlowID, PartnerCompanyID, Amount |
| TD030B2 | Local closing amounts | Inventory accounts |

### FromType Values for IC Data

| Code | Description | Use Case |
|------|-------------|----------|
| 4 | Intercompany Closing | IC receivables/payables |
| 5 | Intercompany Flow | IC sales/purchases with flows |
| 6 | Intercompany Dimensional | Dimensional IC data |

## Configuration Pattern: Stock Margin Elimination

### Step 1: Create Elimination Header

```sql
INSERT INTO TS070S0 (
    ConsoID, ElimCode, ElimType, ElimText, Active, ElimLevel,
    JournalTypeID, ConsoMethodSelectionID, Behaviour, MinorityFlag,
    JournalText
)
VALUES (
    @ConsoID,
    'U020',                    -- Unique code
    'U',                       -- User type
    'Stock Margin',            -- Short name
    1,                         -- Active
    20,                        -- Processing order
    @JournalTypeID,            -- Target journal (e.g., TU type)
    4,                         -- Global integration companies
    3,                         -- Both periods separately
    0,                         -- No MI processing
    'Elimination of unrealized profit in intercompany inventory'
);
```

### Step 2: Configure Elimination Lines

**Line 1: Current Period - Eliminate Sales**
```sql
INSERT INTO TS071S0 (
    ConsoID, EliminationHeaderID, LineNr,
    FromType, FromAccountID, FromPeriod, FromPartnerMethod,
    ToType, ToAccountID, ToSign, Percentage
)
VALUES (
    @ConsoID, @HeaderID, 1,
    5,                         -- IC Flow data
    @IC_Sales_AccountID,       -- IC Sales account
    'C',                       -- Current period
    'G',                       -- Global partners only
    2,                         -- Closing Flow target
    @StockMargin_AccountID,    -- Stock margin elimination account
    -1,                        -- Reverse sign
    1                          -- 100%
);
```

**Line 2: Current Period - Credit Reserves**
```sql
INSERT INTO TS071S0 (...)
VALUES (
    @ConsoID, @HeaderID, 2,
    5, @IC_Sales_AccountID, 'C', 'G',
    2, @Reserves_AccountID, 1, 1  -- Credit reserves
);
```

**Line 3: Reference Period - Reverse Prior Margin**
```sql
INSERT INTO TS071S0 (...)
VALUES (
    @ConsoID, @HeaderID, 3,
    5, @IC_Sales_AccountID, 'R', 'G',  -- Reference period
    2, @StockMargin_AccountID, 1, 1    -- Opposite to reverse carry-forward
);
```

**Line 4: Reference Period - Debit Reserves**
```sql
INSERT INTO TS071S0 (...)
VALUES (
    @ConsoID, @HeaderID, 4,
    5, @IC_Sales_AccountID, 'R', 'G',
    2, @Reserves_AccountID, -1, 1
);
```

### Processing Flow

```
P_CONSO_ELIM (Orchestrator)
        │
        ▼
P_CONSO_ELIM_USER (User Elimination Processor)
        │
        ├── Read TS070S0 header for U020
        ├── Apply ConsoMethodSelectionID filter (Global companies)
        │
        ├── Process Behaviour = 3 (Both periods)
        │   ├── Reference Period Lines (3, 4)
        │   │   └── Reverse prior year margin
        │   └── Current Period Lines (1, 2)
        │       └── Eliminate current year margin
        │
        └── Write to TMP_TD035C2, TMP_TD045C2
                │
                ▼
        Post to TD035C2, TD045C2 (Consolidated data)
```

## Gap Analysis

### Implemented Features

| Feature | Status | Notes |
|---------|--------|-------|
| User elimination framework | **Full** | TS070S0/TS071S0 configuration |
| IC data source types | **Full** | FromType 4, 5, 6 |
| Period handling | **Full** | Behaviour = 3 for carry-forward |
| Partner filtering | **Full** | FromPartnerMethod option |
| Percentage application | **Full** | Fixed and ownership-based |

### Not Implemented

| Feature | Gap | Severity | Workaround |
|---------|-----|----------|------------|
| **Automatic Margin Detection** | No inventory audit to identify IC stock | 8 | Manual identification |
| **Margin Percentage Calculation** | No auto-calculation of markup % | 7 | Manual data entry |
| **Stock Age Tracking** | No FIFO/LIFO/Average tracking | 6 | External calculation |
| **Partial Sale Recognition** | If only part of IC stock sold | 6 | Proportional adjustment |
| **Deferred Tax on Margin** | Tax effect of elimination | 5 | Separate elimination |

### Manual Process Required

```
1. Inventory Audit
   └── Identify IC purchases still in stock

2. Margin Calculation
   └── Calculate markup = IC Price - Group Cost

3. Data Entry
   └── Enter margin amount via IC data or user elimination

4. Run Consolidation
   └── P_CONSO_ELIM processes configured eliminations
```

## Accounting Approaches

### Approach 1: P&L Reversal (Theory)

From Chunk 285:
```
Eliminate via P&L:
  Dr. Sales (IC)           50
    Cr. Result (Profit)    50
```

### Approach 2: Reserves Impact (Direct Consolidation)

The recommended approach in Direct Consolidation:
```
Current Year:
  Dr. Reserves             50
    Cr. Inventory          50

Result Impact via Reserves
```

### Approach 3: Deferred Account (Common Practice)

```
Current Year Entry:
  Dr. Deferred Stock Margin    50
    Cr. Inventory              50

P&L Entry:
  Dr. Profit (or Sales)        50
    Cr. Deferred Stock Margin  50
```

## Reporting Considerations

### Audit Trail

User eliminations create journal entries with:
- JournalTypeID linking to journal type (e.g., TU for user)
- JournalEntry number for tracking
- Full amount breakdown in TD035C2/TD045C2

### Variance Analysis

Period-over-period impact:
```
Year 1 Impact: (50) = Full new margin
Year 2 Impact: (10) = New margin (60) - Prior reversed (50)
Year 3 Impact: Variable based on inventory turnover
```

### Report Integration

Stock margin eliminations flow to standard reports:
- Consolidation Summary (P_REPORT_CONSOLIDATION_SUMMARY)
- Elimination Report (P_REPORT_ELIMINATIONS)
- Cross Report (P_REPORT_CROSS_REPORT_MODULAR)

## API Reference

### Primary API Handlers
| Handler | YAML File | Purpose | Status |
|---------|-----------|---------|--------|
| `IntercoDataEntry_GetData` | [api-interco-endpoints.yaml](../11-agent-support/api-interco-endpoints.yaml) | Get intercompany transaction data | ✅ IMPLEMENTED |
| `IntercoDataEntry_SaveData` | [api-interco-endpoints.yaml](../11-agent-support/api-interco-endpoints.yaml) | Save intercompany amounts | ✅ IMPLEMENTED |
| `Consolidation_Execute` | [api-consolidation-endpoints.yaml](../11-agent-support/api-consolidation-endpoints.yaml) | Process stock margin eliminations | ✅ IMPLEMENTED |

### Supporting API Handlers
| Handler | YAML File | Purpose |
|---------|-----------|---------|
| `Elimination_GetEliminations` | [api-elimination-endpoints.yaml](../11-agent-support/api-elimination-endpoints.yaml) | Get stock margin user eliminations |
| `IntercoMatching_GetMatchingStatus` | [api-interco-endpoints.yaml](../11-agent-support/api-interco-endpoints.yaml) | Verify IC transaction matching |

### API Workflow
```
Stock Margin Elimination via API:

1. IntercoDataEntry_GetData → Get IC sales/purchases
2. EXTERNAL: Calculate stock margin amounts
3. IntercoDataEntry_SaveData → Enter margin amounts
4. Configure user elimination (TS070S0/TS071S0):
   - FromType = 5 (IC Flow data)
   - Behaviour = 3 (Both periods)
5. Consolidation_Execute → P_CONSO_ELIM_USER processes:
   - Current period: Eliminate new margin
   - Reference period: Reverse prior margin
6. Elimination_GetEliminations → Verify entries
```

### Implementation Status
| Feature | Status | Gap Reference |
|---------|--------|---------------|
| User elimination framework | ✅ IMPLEMENTED | TS070S0/TS071S0 |
| IC data source types | ✅ IMPLEMENTED | FromType 4, 5, 6 |
| Period carry-forward | ✅ IMPLEMENTED | Behaviour = 3 |
| Automatic margin detection | ❌ NOT_IMPLEMENTED | Manual |
| Margin % calculation | ❌ NOT_IMPLEMENTED | External |

### Related API Documentation
- [API Index](../11-agent-support/api-index.yaml) - Master handler catalog
- [Gap Analysis](../11-agent-support/gap-analysis-report.yaml) - **PARTIAL (70%)**

---

## Related Documentation

- [Profit-in-Stock Eliminations](../04-elimination-entries/profit-in-stock-eliminations.md) - Detailed patterns
- [User-Defined Eliminations](../04-elimination-entries/user-eliminations.md) - Framework reference
- [Elimination Templates](../04-elimination-entries/elimination-templates.md) - Configuration patterns
- [Intercompany Transactions](../04-elimination-entries/intercompany-transactions.md) - IC elimination basics
- [Flow Management](flow-management.md) - Special flows for variances

### Related Knowledge Chunks
- Chunk 0284: Stock margin situation overview
- Chunk 0285: Year 1 adjustments
- Chunk 0286-0287: Year 2 adjustments
- Chunk 0288: Multi-year impact analysis
- Chunk 0357: Inventory elimination principles
- Chunk 0921: Complex elimination scenarios

---
*Document 36 of 50+ | Batch 12: Advanced Translation & Elimination Templates | Last Updated: 2024-12-01*
