# Ownership Structure

Documentation for ownership percentages and control assessment.

## Documents

| Document | Description |
|----------|-------------|
| [direct-indirect-holdings.md](direct-indirect-holdings.md) | Ownership chain calculations |
| [ownership-percentages.md](ownership-percentages.md) | Financial vs voting percentages |
| [control-vs-ownership.md](control-vs-ownership.md) | Control assessment principles |
| [voting-rights-analysis.md](voting-rights-analysis.md) | IFRS 10 voting rights |
| [multi-tier-holdings.md](multi-tier-holdings.md) | Matrix algebra for indirect % |

## Key Concepts

- **Direct Holding**: Parent directly owns shares in subsidiary
- **Indirect Holding**: Ownership through intermediate entities
- **Financial %**: Economic interest (profit sharing)
- **Voting %**: Control interest (voting power)
- **Control %**: Effective control percentage for method determination

## Percentage Types

| Type | Calculation | Usage |
|------|-------------|-------|
| Financial % | Sum of direct + indirect economic interests | NCI allocation |
| Voting % | Voting power considering special arrangements | Method determination |
| Group % | Parent's total economic interest | Elimination calculations |
| Minority % | 100% - Group % | NCI calculations |

## Related Documentation

- [Consolidation Methods](../02-consolidation-methods/) - Method determination
- [Core Calculations](../03-core-calculations/) - Circular ownership, multi-tier
- [Stored Procedures](../07-database-implementation/stored-procedures-catalog.md) - P_CALC_OWNERSHIP_*

---

*Folder: 06-ownership-structure | Last Updated: 2025-12-04*
