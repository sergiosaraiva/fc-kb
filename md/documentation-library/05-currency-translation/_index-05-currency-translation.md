# Currency Translation

Documentation for foreign currency translation (IAS 21).

## Documents

| Document | Description | IAS Standard |
|----------|-------------|--------------|
| [translation-methods.md](translation-methods.md) | Closing rate, temporal methods | IAS 21 |
| [exchange-rate-types.md](exchange-rate-types.md) | CC, AC, MC, HC rate types | IAS 21 |
| [translation-adjustments.md](translation-adjustments.md) | CTA (Cumulative Translation Adjustment) | IAS 21 |
| [hyperinflation-accounting.md](hyperinflation-accounting.md) | IAS 29 restatement | IAS 29 (60% GAP) |

## Key Concepts

- **CC (Closing Rate)**: End-of-period rate for balance sheet items
- **AC (Average Rate)**: Period-average rate for P&L items
- **MC (Monthly Rate)**: Month-specific rate for detailed translation
- **HC (Historical Rate)**: Original transaction rate for non-monetary items
- **CTA**: Cumulative Translation Adjustment in equity

## Rate Type Usage

| Item Type | Rate Type | Example |
|-----------|-----------|---------|
| Monetary assets/liabilities | CC | Cash, receivables, payables |
| P&L items | AC | Revenue, expenses |
| Equity | HC | Share capital, reserves at acquisition |
| Non-monetary items | HC/CC | Fixed assets, inventory |

## Related Documentation

- [Core Calculations](../03-core-calculations/) - Translation in calculations
- [Stored Procedures](../07-database-implementation/stored-procedures-catalog.md) - P_CONSO_*_CURRENCY_TRANSLATION

---

*Folder: 05-currency-translation | Last Updated: 2025-12-04*
