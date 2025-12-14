# Screen Glossary: UI Screens to Theory Concepts

## Overview

This glossary maps every major screen in Prophix.Conso to its underlying consolidation theory concept. Use this when translating between what users see and what the system does.

---

## Navigation Menu Mapping

### Workflows Menu

| Screen | Navigation | Theory Concept | What It Does |
|--------|------------|----------------|--------------|
| **Workflow** | Workflows > Workflow | Close process management | Manage consolidation tasks and deadlines |
| **Dashboard** | Workflows > Dashboard | Status monitoring | View consolidation progress across companies |

**Theory Connection**: Consolidation is a controlled process with deadlines. The workflow ensures data quality through review/approval gates.

---

### Data Entry Menu

| Screen | Navigation | Theory Concept | What It Does |
|--------|------------|----------------|--------------|
| **Bundles** | Data Entry > Bundles | Local trial balance | Enter/view subsidiary financial data |
| **Spread Data Entry** | Data Entry > Spread | Account detail breakdown | Enter account sub-analysis |
| **Intercompany** | Data Entry > Intercompany | IC transactions | Record transactions with group companies |
| **Local Adjustments** | Data Entry > Local Adjustments | Pre-consolidation adjustments | Adjust local data before consolidation |
| **Validation Reports** | Data Entry > Validation | Data quality checks | Run validation rules on entered data |

**Theory Connection**: The "Bundle" is the consolidated data package from each subsidiary - their trial balance mapped to the group chart of accounts.

---

### Group Menu

| Screen | Navigation | Theory Concept | What It Does |
|--------|------------|----------------|--------------|
| **Companies** | Group > Companies | Legal entity register | Define subsidiaries and their attributes |
| **Group Structure** | Group > Group Structure | Ownership chain | Define who owns whom and percentages |
| **Exchange Rates** | Group > Exchange Rates | Currency translation rates | Enter CC, AC, MC, HC rates |
| **Scope** | Group > Scope | Consolidation perimeter | Define which entities consolidate |
| **Periods** | Group > Periods | Reporting periods | Manage consolidation periods |

**Theory Connection**: Group structure determines the consolidation method (G/P/E/N) and the minority interest calculation.

### Key Fields on Group Structure

| Field | Theory Term | Description |
|-------|-------------|-------------|
| Financial Rights | Ownership % | Economic interest in subsidiary |
| Voting Rights | Control % | Voting power for decisions |
| Group % | Consolidated % | Effective group ownership |
| Minority % | NCI % | Non-controlling interest |
| Method | Consolidation Method | G=Global, P=Proportional, E=Equity, N=Not consolidated |

---

### Automation Menu

| Screen | Navigation | Theory Concept | What It Does |
|--------|------------|----------------|--------------|
| **Jobs** | Automation > Jobs | Batch processing | Schedule and monitor consolidation jobs |
| **Estimates** | Automation > Estimates | Projection calculations | Compute estimated values |

**Theory Connection**: Large groups require automated batch processing to run consolidations efficiently.

---

### Adjustments Menu

| Screen | Navigation | Theory Concept | What It Does |
|--------|------------|----------------|--------------|
| **Journal Entry** | Adjustments > Journal Entry | Consolidation adjustments | Enter manual consolidation adjustments |
| **Journal List** | Adjustments > Journal List | Adjustment register | View/manage all adjustment journals |
| **Templates** | Adjustments > Templates | Recurring entries | Define reusable adjustment templates |

**Theory Connection**: Adjustments are IFRS-required entries not in local books - like goodwill amortization, fair value adjustments, or policy alignments.

### Journal Categories

| Category | Code | Theory Concept |
|----------|------|----------------|
| Local Adjustment | L | Pre-consolidation local corrections |
| Group Adjustment | G | Consolidation-level adjustments |
| Elimination | E | Intercompany elimination entries |
| Restatement | R | Prior period restatements |

---

### Consolidation Menu

| Screen | Navigation | Theory Concept | What It Does |
|--------|------------|----------------|--------------|
| **Statusboard** | Consolidation > Statusboard | Consolidation status | Monitor what needs (re)processing |
| **Integrate Bundles** | Consolidation > Integrate Bundles | Bundle aggregation | Roll up subsidiary data to group |
| **Integrate Adjustments** | Consolidation > Integrate Adjustments | Adjustment posting | Apply adjustments to consolidated data |
| **Eliminations** | Consolidation > Eliminations | Elimination processing | Run elimination calculations |
| **Intercompany Matching** | Consolidation > IC Matching | IC reconciliation | Match IC transactions between companies |
| **Events** | Consolidation > Events | Consolidation events | Process acquisitions, disposals, etc. |

**Theory Connection**: This is the core consolidation engine implementing "Direct Consolidation" methodology.

### Statusboard Columns Explained

| Column | Checkmark Means | Action Required |
|--------|-----------------|-----------------|
| Bundle | Local data changed | Run Integrate Bundles |
| Adj | Adjustments changed | Run Integrate Adjustments |
| Conso | Either changed | Run full consolidation |

---

### Reports Menu

| Screen | Navigation | Theory Concept | What It Does |
|--------|------------|----------------|--------------|
| **Standard Reports** | Reports > Standard | Statutory reports | Generate standard financial reports |
| **Consolidation Reports** | Reports > Consolidation | Elimination detail | View elimination and adjustment detail |
| **User Reports** | Reports > User Reports | Custom reporting | Run user-defined reports |
| **Analysis Reports** | Reports > Analysis | Pivot analysis | Interactive data analysis |
| **Document Repository** | Reports > Documents | File storage | Store and share documents |

**Theory Connection**: Consolidated financial statements are the output of the consolidation process - Balance Sheet, P&L, Cash Flow, Equity Movement.

---

### Transfers Menu

| Screen | Navigation | Theory Concept | What It Does |
|--------|------------|----------------|--------------|
| **Import Data** | Transfers > Import | Data loading | Import data from external sources |
| **Export Data** | Transfers > Export | Data extraction | Export data to files |
| **Exchange Rates** | Transfers > Exchange Rates | Rate import/export | Import rates from ECB, NBS, etc. |

**Theory Connection**: Consolidation systems must integrate with ERP, GL, and other source systems.

---

### Configuration Menu

| Screen | Navigation | Theory Concept | What It Does |
|--------|------------|----------------|--------------|
| **Accounts** | Configuration > Accounts | Chart of accounts | Define group account structure |
| **Flows** | Configuration > Flows | Cash flow definitions | Define flow types (C/NC) |
| **Dimensions** | Configuration > Dimensions | Analytical dimensions | Define additional analysis axes |
| **Elimination Rules** | Configuration > Eliminations | Elimination configuration | Configure S-codes and elimination logic |

**Theory Connection**: The chart of accounts and elimination rules are the foundation of the consolidation logic.

---

### Administration Menu

| Screen | Navigation | Theory Concept | What It Does |
|--------|------------|----------------|--------------|
| **Users** | Administration > Users | Access control | Manage user accounts |
| **Roles** | Administration > Roles | Permission management | Define what users can do |
| **Audit Log** | Administration > Audit | Audit trail | Track all system changes |

**Theory Connection**: Consolidation requires strong controls and audit trails for SOX/regulatory compliance.

---

## Screen-to-Theory Quick Lookup

### "I need to..." → Go to Screen

| Task | Screen | Navigation |
|------|--------|------------|
| Enter subsidiary data | Bundles | Data Entry > Bundles |
| Record intercompany transaction | Intercompany | Data Entry > Intercompany |
| Set currency rates | Exchange Rates | Group > Exchange Rates |
| Define ownership | Group Structure | Group > Group Structure |
| Check what needs processing | Statusboard | Consolidation > Statusboard |
| Run consolidation | Eliminations | Consolidation > Eliminations |
| Match IC transactions | IC Matching | Consolidation > IC Matching |
| Enter manual adjustment | Journal Entry | Adjustments > Journal Entry |
| Generate financial statements | Standard Reports | Reports > Standard |

---

*Screen Glossary | Version 1.0 | Last Updated: 2024-12-03*
