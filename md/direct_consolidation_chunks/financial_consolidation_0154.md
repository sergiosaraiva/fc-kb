# Chunk 154: Consolidation Implications:

## Context

This section explains minority interest calculations. Discusses relationships between entities: P.

## Content

## Consolidation Implications:
- Complex indirect percentage calculations
- Multiple elimination entries required
- Cross-participation affects minority interests


This again is easy to calculate in Excel by using the following syntax for each cell of the output matrix

\[
= I N D E X (M M U L T (A: B; C: D); L I N E; C O L)
\]

where "A:B" is the range of the matrix D, "C:D" is the range of the inverse matrix we just calculated and "LINE" and "COL" are the line and the column number of the corresponding cell of the final matrix.

Of course, we are interested only in the first line of that matrix which gives the indirect percentages from P in all other subsidiaries. For instance, we see indeed that P owns indirectly  60%  in B.

This algorithm works for any structure of any size. Crossed participations or cycle of participations (A -> B -> C -> A) are also accepted. The only restriction is that a subsidiary cannot own shares of the parent company. If so, that link must be ignored.


## Related Topics

- Minority interests calculation
- Elimination entries

---
*Chunk 154 | Consolidation Implications:*