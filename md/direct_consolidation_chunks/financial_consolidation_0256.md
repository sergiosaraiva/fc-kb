# Chunk 256: The situation

## Context

This section addresses foreign currency translation. Contains formula: corresponding to a transaction rate of 1 CUR = 1.4 EUR at that time..

## Content

### The situation

Company A (EUR) sends an invoice of 1000 to company B (CUR) booked for an amount of 778 CUR, corresponding to a transaction rate of 1 CUR = 1.4 EUR at that time.

At the end of the year, we suppose the invoice is not paid yet and the situation in both company accounts is the following


| A (EUR) |  |  |  |
| --- | ---: | --- | ---: |
| Receivables/B | 1,000 | Result | 1,000 |
| Result | 1,000 | Sales/B | 1,000 |



| B (CUR) |  |
| --- | --- |
|   | Result (714) |
|   | Payables/A 714 |
| Purchases/A 714 |   |
| Result (714) |   |


At the end of the year, closing rate is 1 CUR = 1.5 EUR and average rate is 1 CUR = 1.7 EUR, giving the following translated accounts for B


| A (EUR) |  |  |  |
| --- | ---: | --- | ---: |
| Receivables/B | 1,000 | Result | 1,000 |
| Result | 1,000 | Sales/B | 1,000 |



| B (EUR) |  |
| --- | --- |
|   | Result (1,214) |
|   | Trans. Adj. 143 |
|   | Payables/A 1,071 |
| Purchases/A 1,214 |   |
| Result (1,214) |   |


where we can see a double intercompany difference arising because of the currency conversion, one in the balance sheet for 71 and another in the P&L for 214.


## Related Topics

- Currency translation

---
*Chunk 256 | The situation*