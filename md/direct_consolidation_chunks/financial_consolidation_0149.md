# Chunk 149: Consolidation Challenges:

## Context

This section explains minority interest calculations. Shows detailed calculations. Discusses relationships between entities: B.

## Content

## Consolidation Challenges:
- Circular holdings require iterative calculation
- Treasury shares in C affect ownership
- Multiple elimination entries required
- Complex minority interest computation


The answer we want to get through the algorithm is  86% = 80% + 60% * 10%  for A,  60%  for B and  56.4% = 80% * 40% + 60% * 10% * 40% + 60% * 20% + 10%  for C.

We first build a matrix with direct percentages between companies. Let's call D that matrix.


| P | A | B | C |
| ---: | ---: | ---: | ---: |
|   |  |  |  |
| 0 | 0.8 | 0.6 | 0.1 |
| 0 | 0 | 0 | 0.4 |
| 0 | 0.1 | 0 | 0.2 |
| 0 | 0 | 0 | 0 |


For instance, company B owns  20% = 0.2  in company C.

We then define the unit matrix called  \mathbf{I}  with 1 on the diagonal and 0 in all the other cells


| 1 | 0 | 0 | 0 |
| ---: | ---: | ---: | ---: |
| 0 | 1 | 0 | 0 |
| 0 | 0 | 1 | 0 |
| 0 | 0 | 0 | 1 |


and calculate  \mathbb{I} - \mathbb{D}  in order to get


| 1 | -0.8 | -0.6 | -0.1 |
| ---: | ---: | ---: | ---: |
| 0 | 1 | 0 | -0.4 |
| 0 | -0.1 | 1 | -0.2 |
| 0 | 0 | 0 | 1 |


Now, this matrix has to be inverted. It is a function provided by Microsoft Excel ©. We get INV(I - D)


| 1 | 0.86 | 0.6 | 0.56 |
| ---: | ---: | ---: | ---: |
| 0 | 1 | 0 | 0.4 |
| 0 | 0.1 | 1 | 0.24 |
| 0 | 0 | 0 | 1 |


Using the Excel syntax, each cell of this matrix is defined as follows

\[
= I N D E X (I N V E R S E (A: B); L I N E, C O L)
\]

where "A:B" is the range defining the matrix to be inverted. "LINE" is the line number and "COL" is the column number of the cell in the output matrix.

Finally, we calculate the product of both matrices  D  and  \(INV(I - D)\)  which gives the expected result.


<!-- Source: 6212f37511427f2d626aa0dfe6c8fc523495418f51eb7e42c129c05f5d686361.jpg -->
<!-- Type: table -->
<!-- Confidence: high -->
<!-- Converted: 2024-11-28T16:49:00 -->
<!-- Context: Ownership matrix with cross-participations -->
<!-- Section: Ownership percentage matrix -->


## Related Topics

- Minority interests calculation
- Elimination entries

---
*Chunk 149 | Consolidation Challenges:*