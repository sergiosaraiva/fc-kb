# Troubleshooting

Documentation for common issues and resolution patterns.

## Documents

| Document | Description |
|----------|-------------|
| [common-issues.md](common-issues.md) | 15+ common issues with solutions |

## Issue Categories

### Data Issues
- Circular ownership calculation errors
- Missing ownership percentages
- Currency translation mismatches

### Elimination Issues
- Participation elimination failures
- Dividend calculation errors
- IC matching threshold problems

### Performance Issues
- Slow consolidation processing
- Memory issues with large groups
- Timeout during integration

## Quick Diagnosis

| Symptom | Likely Cause | Document Section |
|---------|--------------|------------------|
| Wrong group % | Circular ownership | [common-issues.md#circular](common-issues.md) |
| Missing NCI | Method determination | [common-issues.md#method](common-issues.md) |
| CTA imbalance | Rate type mismatch | [common-issues.md#currency](common-issues.md) |

## Related Documentation

- [Core Calculations](../03-core-calculations/) - Calculation logic
- [Database Implementation](../07-database-implementation/) - Procedure reference

---

*Folder: 17-troubleshooting | Last Updated: 2025-12-04*
