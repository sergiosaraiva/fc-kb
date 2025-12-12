# Database Implementation

Documentation for database schema, stored procedures, and patterns.

## Documents

| Document | Description | Key Content |
|----------|-------------|-------------|
| [stored-procedures-catalog.md](stored-procedures-catalog.md) | 65+ P_CONSO_* procedures | Procedure reference |
| [data-tables-catalog.md](data-tables-catalog.md) | 93 consolidation tables | TS/TD table reference |
| [journal-types.md](journal-types.md) | S001-S085 elimination codes | S-code reference |
| [trigger-patterns.md](trigger-patterns.md) | 32+ consolidation triggers | Status flag patterns |
| [temp-table-patterns.md](temp-table-patterns.md) | 80+ TMP_* tables | Session tables |
| [index-strategy.md](index-strategy.md) | ConsoID-first indexing | Performance |

## Key Concepts

- **TS### Tables**: Setup/configuration tables (e.g., TS014C0 for companies)
- **TD### Tables**: Data/transaction tables (e.g., TD035C2 for consolidated amounts)
- **TMP_* Tables**: Temporary session tables for calculations
- **P_CONSO_* Procedures**: Core consolidation stored procedures
- **P_CALC_* Procedures**: Calculation procedures (ownership, etc.)
- **P_REPORT_* Procedures**: Report generation procedures

## Table Naming Convention

| Pattern | Type | Example |
|---------|------|---------|
| TS###S0 | Setup header | TS014S0 (company setup) |
| TS###C0 | Setup config | TS014C0 (company config) |
| TD###B2 | Bundle data | TD030B2 (local bundles) |
| TD###C2 | Consolidated | TD035C2 (consolidated amounts) |
| TMP_* | Temporary | TMP_CONSO_EXCHANGERATE |

## Related Documentation

- [Application Layer](../08-application-layer/) - Service integration
- [Core Calculations](../03-core-calculations/) - Business logic

---

*Folder: 07-database-implementation | Last Updated: 2025-12-04*
