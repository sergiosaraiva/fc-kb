# Elimination Entries

Documentation for consolidation elimination entries (T-Journals).

## Documents

| Document | Description | S-Codes |
|----------|-------------|---------|
| [participation-eliminations.md](participation-eliminations.md) | Investment elimination | S050-S054 |
| [dividend-eliminations.md](dividend-eliminations.md) | Intercompany dividend processing | S020 |
| [dividend-calculation-logic.md](dividend-calculation-logic.md) | 4-line journal pattern detail | S020 |
| [intercompany-transactions.md](intercompany-transactions.md) | IC netting eliminations | S030 |
| [user-eliminations.md](user-eliminations.md) | TS070S0/TS071S0 framework | U### |
| [profit-in-stock-eliminations.md](profit-in-stock-eliminations.md) | Stock margin eliminations | - |
| [elimination-templates.md](elimination-templates.md) | Configuration patterns | - |

## Key Concepts

- **S-Codes**: System-generated elimination type identifiers (S001-S085)
- **U-Codes**: User-defined elimination codes (U###)
- **T-Journal**: Consolidation journal entry record
- **Execution Order**: S-code numerical sequence determines processing order

## Related Documentation

- [Journal Types](../07-database-implementation/journal-types.md) - Complete S-code reference
- [User Eliminations](user-eliminations.md) - Manual workaround framework
- [Core Calculations](../03-core-calculations/) - Calculation logic

---

*Folder: 04-elimination-entries | Last Updated: 2025-12-04*
