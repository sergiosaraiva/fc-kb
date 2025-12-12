# Profit-in-Stock (Unrealized Profit) Eliminations

## Document Metadata
- **Category**: Elimination Entries
- **Theory Source**: Knowledge base chunks: 0269, 0284-0288, 0357, 0921
- **Implementation Files**:
  - `Sigma.Database/dbo/Stored Procedures/P_CONSO_ELIM_USER.sql` - Custom elimination engine
  - `Sigma.Database/dbo/Tables/TS070S0.sql` - Elimination headers (including custom)
  - `Sigma.Database/dbo/Tables/TS071S0.sql` - Elimination line details
  - `Sigma.Database/dbo/Stored Procedures/P_CONSO_ELIM_USER_PROCESS.sql` - User elimination processing
- **Last Updated**: 2024-12-01
- **Completeness**: 70% (Framework available; requires manual configuration)
- **Compliance Status**: IAS 2, IFRS 15 - Inventory and Revenue Recognition

## Executive Summary

Profit-in-stock eliminations (also called stock margins or unrealized profit in inventory) remove internal group profits that remain embedded in ending inventory. When Company A sells goods to Company B at a markup, and B still holds those goods at period-end, the group profit must be eliminated to prevent overstating both inventory and retained earnings. Prophix.Conso provides this capability through its **user-defined elimination framework** (`P_CONSO_ELIM_USER`) rather than a dedicated built-in procedure, requiring manual configuration of elimination rules.

## Theoretical Framework

### Concept Definition

From Allen White's "Direct Consolidation" (Chunk 284):

> "In most of the industrial groups, some companies are dedicated to supply on the market and make products and some other companies are dedicated to sell these products. In such situation, the normal practice for the industrial companies is to sell the products to the commercial companies, including a benefit called stocks margin."

### Why Eliminate Profit-in-Stock?

```
Manufacturing Company A sells to Sales Company B:
- Cost to A: 300
- Sale price to B: 350
- A's profit: 50 (internal group profit)

If B still holds stock at year-end:
- B's inventory shows: 350
- A's P&L shows profit: 50
- Group perspective: Profit not yet realized externally

Without Elimination:
- Group overstates inventory by: 50
- Group overstates profit by: 50

With Elimination:
- Reduce sales/profit: -50
- Reduce inventory: -50
- Or: Increase reserves: +50 (Approach 3)
```

### Key Principles (from Chunks 284-288)

1. **Timing Recognition**: Profit is only realized when goods are sold externally
2. **Period Carry-Forward**: Adjustments must be carried forward and reversed when stock sold
3. **Two-Company Approach**: Each adjustment is booked in balance within each company
4. **Method Consistency**: Choose between Deferred (Approach 2) or Reserves (Approach 3) method

### Three Approaches to Profit Elimination

**Approach 1: No Elimination (Market Conditions)**
- If transaction at arm's length, keep profit
- Risk: Distorts consolidated results
- Generally not recommended

**Approach 2: Deferred Income/Expense Method**
```
Seller (A):
  Dr. Sales/B           350
  Cr. Deferred Income    50
  Cr. Cost of Sales     300

Buyer (B):
  Dr. Deferred Expense   50
  Cr. Stocks             50
```
- Use deferred accounts
- Reverse on external sale
- Clean audit trail

**Approach 3: Reserves Method** (from Chunk 285)
```
Seller (A):
  Dr. Sales/B            50
  Cr. Reserves           50
  Dr. Result            -50 (P&L impact)

Buyer (B):
  No adjustment to B's books
  (Stock value kept at 350)
```
- Uses equity reserves
- Attention needed for different ownership percentages
- Simpler but less transparent

### Year-Over-Year Handling (Chunks 285-288)

**Year 1 Entry**:
```
Stock margin: 50
- Eliminate profit in A: (50)
- Adjust reserves: +50 (Approach 3)
Impact on group result: (50)
```

**Year 2 Entry**:
```
Old stock sold, new margin: 60

Step 1: Carry forward Year 1
- Historical adjustment affects reserves

Step 2: Reverse Year 1 (stock sold)
- Improve profit by 50

Step 3: New margin elimination
- Eliminate new margin: (60)

Net Year 2 impact: 50 - 60 = (10)
```

### Multi-Year Pattern (from Chunk 288)

| Period | Company A | Company B | Net Impact |
|--------|-----------|-----------|------------|
| Year 1 | (50) | 0 | (50) |
| Year 2 | (60) | +50 | (10) |
| Year 3+ | Similar pattern | Reversal | Minimal net |

> "After Year 1, and forever, if the stocks margins are relatively similar each year, the impact on the profit cannot be significant."

## Current Implementation

### Implementation Approach

Prophix.Conso does **not** have a dedicated S-code elimination (like S020 for dividends or S089 for participations) for profit-in-stock. Instead, it provides:

1. **User-Defined Elimination Framework** - Configurable rules
2. **Group Adjustment Journals** - Manual entry capability
3. **Custom Events** - Automated processing of user-defined rules

### Elimination Configuration Tables

#### TS070S0 - Elimination Headers

```sql
CREATE TABLE [dbo].[TS070S0] (
    [EliminationHeaderID]    INT          IDENTITY NOT NULL,
    [ConsoID]                INT          NOT NULL,
    [ElimCode]               NVARCHAR(4)  NOT NULL,  -- e.g., 'U001' for user-defined
    [JournalTypeID]          INT          NOT NULL,
    [JournalText]            NVARCHAR(MAX) NULL,
    [Behaviour]              TINYINT      NOT NULL,
    [MinorityFlag]           BIT          NOT NULL,
    [ConsoMethodSelectionID] INT          NOT NULL,
    [Active]                 BIT          NOT NULL
);
```

#### TS071S0 - Elimination Line Details

```sql
CREATE TABLE [dbo].[TS071S0] (
    [EliminationDetailID]    INT      IDENTITY NOT NULL,
    [EliminationHeaderID]    INT      NOT NULL,
    [LineNr]                 SMALLINT NOT NULL,
    [FromType]               TINYINT  NOT NULL,    -- 1=Closing, 4=Interco
    [FromAccountID]          INT      NULL,        -- Source account
    [FromPeriod]             CHAR(1)  NOT NULL,    -- C=Current, R=Reference
    [ToAccountID]            INT      NULL,        -- Target account
    [ToSign]                 SMALLINT NOT NULL,    -- 1 or -1
    [Percentage]             TINYINT  NOT NULL     -- % to apply
);

-- Percentage options:
-- 1 = 100%
-- 3 = Group Financial Company % (This Period)
-- 4 = Minority Financial Company % (This Period)
-- 5 = Group + Minority Financial Company % (This Period)
```

### User Elimination Processing

From `P_CONSO_ELIM_USER.sql` (lines 55-150):

```sql
CREATE procedure [dbo].[P_CONSO_ELIM_USER]
    @CurConsoID int,
    @RefConsoID int,
    @UserID int,
    @CurCompanyIDs varchar(max),
    @EliminationHeaderID int,    -- Configured elimination rule
    @SessionID int,
    @errorinfo xml output

-- Process:
-- 1. Load elimination configuration from TS070S0/TS071S0
-- 2. Select companies based on ConsoMethodSelectionID
-- 3. For each elimination line:
--    a. Read source amounts (FromAccountID, FromPeriod)
--    b. Apply percentage and sign
--    c. Post to target account (ToAccountID)
-- 4. Create journal entries
```

### Company Selection Methods

The user elimination supports various selection methods:

| SelectionID | Description |
|-------------|-------------|
| 1 | All companies |
| 2 | Parent only |
| 3 | All except parent |
| 4 | Global integration (G) |
| 5 | Proportional (P) |
| 6 | Equity method (E) |
| 7 | Not consolidated (N) |
| 8 | Entering companies |
| 9 | Leaving companies |
| 10 | Available for sale |
| 11 | All except parent and N |

### Configuring a Stock Margin Elimination

**Step 1: Define Accounts**
```sql
-- Required special accounts:
- Stocks account (inventory)
- Deferred Income account (if Approach 2)
- Reserves account (if Approach 3)
- Intercompany Sales account (with PartnerType)
- Intercompany Purchases account (with PartnerType)
```

**Step 2: Create Elimination Header**
```sql
INSERT INTO TS070S0 (ConsoID, ElimCode, JournalText, Active, ...)
VALUES (@ConsoID, 'U001', 'Stock Margin Elimination', 1, ...)
```

**Step 3: Define Elimination Lines**
```sql
-- Line 1: Reduce intercompany sales
INSERT INTO TS071S0 (EliminationHeaderID, LineNr,
    FromType, FromAccountID, FromPeriod,
    ToAccountID, ToSign, Percentage)
VALUES (@HeaderID, 1,
    4, @IC_Sales_AccountID, 'C',  -- Interco, Current Period
    @IC_Sales_AccountID, -1, 1)   -- Reduce by 100%

-- Line 2: Adjust reserves (Approach 3)
INSERT INTO TS071S0 (...)
VALUES (@HeaderID, 2,
    4, @IC_Sales_AccountID, 'C',
    @Reserves_AccountID, 1, 1)    -- Credit reserves
```

### Group Adjustment Journals

For complex scenarios, manual group adjustments can be entered through:

```sql
-- P_UPDATE_GROUPADJUSTMENT_JOURNAL
-- Allows direct entry of consolidation adjustments
-- Supports:
- Closing amounts (TD035C2)
- Flow amounts (TD045C2)
- Dimension amounts (TD055C2)
```

### Reference Period Support

The system tracks both current and reference periods:

```sql
create table #Companies (
    CurCompanyID int,           -- Current period company
    RefCompanyID int,           -- Reference period company
    CurCompanyGroupPerc decimal, -- Current financial %
    RefCompanyGroupPerc decimal  -- Reference financial %
)
```

This enables:
- Year-over-year carry forward
- Reversal calculations
- Percentage change handling

## Theory vs Practice Analysis

| Aspect | Theory (Allen White) | Prophix.Conso Implementation | Alignment |
|--------|---------------------|------------------------------|-----------|
| Stock Margin Elimination | Required | Via user eliminations | Partial |
| Approach 2 (Deferred) | Recommended | Configurable | Full |
| Approach 3 (Reserves) | Alternative | Configurable | Full |
| Year-over-Year Handling | Required | Manual configuration | Partial |
| Automatic Detection | Implied | Not available | Gap |
| Two-Company Balance | Required | Supported | Full |
| Percentage Application | By ownership | Configurable | Full |

## Gap Analysis

### Missing Elements

1. **No Dedicated S-Code**: Unlike dividends (S020) or participations (S089), no built-in "S0XX" code for stock margins
2. **No Automatic Detection**: Cannot auto-identify intercompany inventory
3. **No Margin Rate Tracking**: No built-in margin percentage tracking per partner
4. **No Inventory Audit Trail**: Missing historical stock margin tracking

### Divergent Implementation

1. **Manual Configuration Required**: Theory assumes automatic; implementation requires setup
2. **No Standard Template**: Each group must configure from scratch
3. **Period Carry-Forward**: Must be manually configured vs automatic in theory

### Additional Features (Beyond Theory)

1. **Flexible Percentage Options**: Multiple percentage application methods
2. **Dimension Support**: Can eliminate at dimensional level
3. **Partner Method Filtering**: Filter by consolidation method (G/P/E/N)
4. **Entering/Leaving Handling**: Special treatment for scope changes

## Business Impact

### Current Capabilities

1. **Framework Available**: Full user elimination infrastructure
2. **Configurable Rules**: Define custom elimination logic
3. **Percentage Flexibility**: Apply at various ownership levels
4. **Period Awareness**: Current vs reference period handling

### Limitations

1. **Setup Complexity**: Requires technical configuration knowledge
2. **Manual Maintenance**: Year-over-year adjustments need attention
3. **No Auto-Audit**: Cannot automatically audit inventory margins
4. **Error Risk**: Misconfiguration can cause incorrect eliminations

### Recommendations for Implementation

1. **Define Standard Template**: Create reusable elimination configuration
2. **Document Margin Rates**: Track margin rates per intercompany relationship
3. **Year-End Checklist**: Establish review process for stock eliminations
4. **Validation Reports**: Build custom reports to verify eliminations

## Methodology Principles (from Chunk 357)

Key principles for booking stock margin eliminations:

1. **Balanced Entries**: Each adjustment consists of debits and credits in balance
2. **Single Company**: Each adjustment fully booked within one company
3. **No Cross-Company Booking**: Don't debit one company and credit another
4. **Local Currency**: Book foreign company adjustments in local currency
5. **Professional Documentation**: Maintain audit trail for complex adjustments

## Practical Implementation Example

### Scenario: Manufacturing Group

**Setup**:
- Company A (manufacturer) sells to Company B (distributor)
- Margin rate: 15%
- B holds 1,000,000 inventory from A at year-end

**Year 1 Elimination**:
```
Elimination amount: 1,000,000 × 15% = 150,000

Company A entries (in A's books):
Dr. Sales to B              150,000
Cr. Consolidated Reserves   150,000

P&L Impact: (150,000)
```

**Year 2 Elimination** (assuming 800,000 inventory at 16% margin):
```
New elimination: 800,000 × 16% = 128,000
Reversal of Y1: 150,000

Company A:
Dr. Consolidated Reserves   150,000  (reverse Y1)
Cr. Result                  150,000

Dr. Sales to B              128,000  (new Y2)
Cr. Consolidated Reserves   128,000

Net P&L Impact: +150,000 - 128,000 = +22,000
```

## API Reference

### Primary API Handlers
| Handler | YAML File | Purpose | Status |
|---------|-----------|---------|--------|
| `Consolidation_Execute` | [api-consolidation-endpoints.yaml](../11-agent-support/api-consolidation-endpoints.yaml) | Trigger P_CONSO_ELIM_USER for stock margin | ✅ IMPLEMENTED |
| `Elimination_SaveElimination` | [api-elimination-endpoints.yaml](../11-agent-support/api-elimination-endpoints.yaml) | Configure stock margin elimination rules | ✅ IMPLEMENTED |
| `IntercoDataEntry_SaveData` | [api-interco-endpoints.yaml](../11-agent-support/api-interco-endpoints.yaml) | Enter IC inventory margins | ✅ IMPLEMENTED |

### Supporting API Handlers
| Handler | YAML File | Purpose |
|---------|-----------|---------|
| `IntercoDataEntry_GetData` | [api-interco-endpoints.yaml](../11-agent-support/api-interco-endpoints.yaml) | Get IC inventory data |
| `GroupAdjustment_SaveJournalDetail` | [api-adjustment-endpoints.yaml](../11-agent-support/api-adjustment-endpoints.yaml) | Manual margin adjustment entry |

### API Workflow
```
Profit-in-Stock Elimination via API (Manual Configuration Required):

1. MARGIN DATA ENTRY
   IntercoDataEntry_SaveData → Enter IC inventory margins:
     - Intercompany sales amounts
     - Margin percentages (external calculation)

2. CONFIGURE ELIMINATION (One-Time Setup)
   Elimination_SaveElimination → TS070S0 Header:
     - ElimCode = 'U0XX' (user-defined)
     - Behaviour = 3 (both periods - carry forward)
     - ConsoMethodSelectionID = 4 (Global only)

   Elimination_SaveElimination → TS071S0 Lines:
     - Line 1: IC Sales → Stock Margin (reverse)
     - Line 2: IC Sales → Reserves (credit)
     - Line 3: IC Sales (Ref) → Reverse prior margin

3. EXECUTION
   Consolidation_Execute → P_CONSO_ELIM → P_CONSO_ELIM_USER:
     - Process per configured rules
     - Apply Approach 2 (Deferred) or Approach 3 (Reserves)

4. VERIFICATION
   Elimination_GetEliminations → Verify entries
```

### Implementation Status
| Feature | Status | Gap Reference |
|---------|--------|---------------|
| User elimination framework | ✅ IMPLEMENTED | TS070S0/TS071S0 |
| Manual margin configuration | ✅ IMPLEMENTED | P_CONSO_ELIM_USER |
| Period carry-forward | ✅ IMPLEMENTED | Behaviour = 3 |
| Automatic margin detection | ❌ NOT_IMPLEMENTED | Severity 7 |
| Margin rate tracking | ❌ NOT_IMPLEMENTED | External calculation |
| Inventory audit trail | ❌ NOT_IMPLEMENTED | Manual tracking |

### Related API Documentation
- [API Index](../11-agent-support/api-index.yaml) - Master handler catalog
- [Gap Analysis](../11-agent-support/gap-analysis-report.yaml) - **PARTIAL (70%)**

---

## Related Documentation

- [Intercompany Transactions](intercompany-transactions.md) - General IC eliminations
- [Participation Eliminations](participation-eliminations.md) - Investment eliminations
- [Dividend Eliminations](dividend-eliminations.md) - IC dividend handling
- [Missing Features](../10-gap-analysis/missing-features.md) - Implementation gaps

### Related Knowledge Chunks
- Chunk 0269: Methodology for consolidation adjustments
- Chunk 0284-0288: Stock margins elimination examples
- Chunk 0357: Methodology principles for balanced entries
- Chunk 0921: Future automation of stock margin eliminations

---
*Document 18 of 50+ | Batch 6: Elimination Entries | Last Updated: 2024-12-01*
