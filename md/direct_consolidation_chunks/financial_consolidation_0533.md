# Chunk 533: Unmatched intercompany amounts

## Context

This section covers elimination entries in consolidation.

## Content

### Unmatched intercompany amounts

In this situation we consider two companies, A and B, having Receivables and Payables intercompany amounts between them.

To make the explanation as clear as possible, we will limit our view to balance sheets consisting only of Receivables and Payables accounts.

Here are their statutory situations.


| Company A |  | variation |  |  |
| --- | ---: | --- | ---: | ---: |
| Pa. ables | - | 400 | 300 | 700 |



| Company B |  | Year 1 | Cash variation | Year 2 |
| :--- | :--- | ---: | :--- | ---: |
| Receivables | - | 1,000 | 200 | 1,200 |
| Payables | - | 900 | 200 | 1,100 |
|   | A | 100 |   | 100 |


The " - " sign means amounts with  {3}^{rd }  Parties.

In Year 1, Company A has intercompany Receivables with B for 100 and company B has the same amount on the Payables account. These positions are matched.

But in Year 2, the new intercompany amounts are unmatched for a difference of 50, 150 Receivables in A accounts and 100 Payables in B accounts.

To analyze the impact on the consolidated cash flow statement, we have to make some assumptions.

We first suppose the group has defined an intercompany materiality threshold

It specifies that all differences less or equal to 50 don't need to be adjusted and so here is what we get at consolidation level.


| Consolidation | Year 1 | Cash variation | Year 2 |
| :--- | ---: | ---: | ---: |
| Receivables | 1,300 | 450 | 1,750 |
| Link account | 0 | 50 | 50 |
| Payables | 1,300 | 500 | 1,800 |


We will find the difference on the Link account used during the elimination process (Part 2, Chapter 9).

The flow justifying the evolution of this account is the cash variation. If the Link account is considered as a pure technical account, it is possible that it has been ignored in the parameterization of the cash flow statement report of your consolidation software.

The impact is then very clear: the working capital shows  \(50 = (450)\)  as Receivables + 500 as Payables instead of zero. A technical error or 50 will be detected.

By considering all the accepted differences that could be generated depending on the number of intercompany combinations existing in the group, the net difference will be rather difficult to analyze.

The best option consists in reclassifying these differences

Indeed, we could transfer the 50 amount from the Link account to the consolidated Receivables account as shown here


| Consolidation | Year 1 | Cash variation | Transfer flow | Year 2 |
| :--- | ---: | ---: | :--- | ---: |
| Receivables | 1,300 | 450 | 50 | 1,750 |

## Related Topics

- Elimination entries

---
*Chunk 533 | Unmatched intercompany amounts*