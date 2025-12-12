# Application Layer

Documentation for C# services and message handlers.

## Documents

| Document | Description |
|----------|-------------|
| [consolidation-services.md](consolidation-services.md) | Service architecture overview |
| [elimination-execution-engine.md](elimination-execution-engine.md) | P_CONSO_ELIM execution flow |
| [data-import-services.md](data-import-services.md) | 64+ P_SYS_IMPORT procedures |
| [reporting-services.md](reporting-services.md) | 179+ P_REPORT_* procedures |
| [job-management.md](job-management.md) | 50+ Hangfire background jobs |

## Architecture

```
MessagesBroker (Handlers)
    │
    ▼
Sigma.Mona (Services)
    │
    ▼
Entity Framework / LINQ to SQL
    │
    ▼
SQL Server (Stored Procedures)
```

## Key Patterns

- **Message Handlers**: Process frontend requests via MessagesBroker
- **Service Classes**: Business logic in Sigma.Mona/Screens/
- **Stored Procedures**: Database operations via P_CONSO_*, P_CALC_*, P_REPORT_*
- **Background Jobs**: Long-running operations via Hangfire

## Related Documentation

- [Database Implementation](../07-database-implementation/) - Stored procedures
- [Frontend Implementation](../09-frontend-implementation/) - UI integration

---

*Folder: 08-application-layer | Last Updated: 2025-12-04*
