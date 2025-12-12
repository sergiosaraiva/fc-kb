# Chunk 115: Key Points:

## Context

This section contains financial statement data.

## Content

## Key Points:
- Both subsidiaries cross-own each other
- Creates interdependency in valuations
- Affects dividend flow calculations


The control percentage in company C1 is  100%  because the remaining  20%  owned by C2 can be taken into account, C2 obviously being controlled by the group at  60% .

If we keep in mind the basic principle to be applied for the financial percentage of company C1, we just have to inventory all paths starting at P and arriving in C1, multiply the percentages along each path and then add them together.

At a first glance, we would say there are two paths, namely P -> C1 giving 80% and P -> C2 -> C1 giving 60% * 20% = 12%, and we would say the indirect financial percentage is 92%. That's not correct!

Here is the correct answer with (nearly) all the paths.

We first identify an infinite set of paths starting from  P  and ending at C1


| Path 1 | P - C1 | 80% |
| :--- | :--- | ---: |
| Path 2 | P - C1 - C2 - C1 | 4.8% |
| Path 3 | P - C1 - C2 - C1 - C2 - C1 | 0.288% |
| Path 4 | P - ... | ... |
|   |   | 85.088% |


but there is also a second set of paths, different from the first one, starting from  P  and ending in  C1  via  C2 , giving


| Path 1 | P - C2 - C1 | 12% |
| :--- | :--- | ---: |
| Path 2 | P - C2 - C1 - C2 - C1 | 0.72% |
| Path 3 | P - C2 - C1 - C2 - C1 - C2 - C1 | 0.043% |
| Path 4 | P - ... | ... |
|   |  | 12.763% |


The indirect financial percentage is then  97.851%  instead of the  92%  calculated above.

The difference is important and the following question arises: "What if we forget some paths?". The answer is quite clear: the group financial percentage is lower then what it is expected to be and the difference with regard to  100%  is given to the  3^{rd}  Parties. So, that means that the Group part in Equity and in profit is less and not correct.

Of course, as soon as the mistake has been identified, a correction must be applied. Speaking about financial percentage, this mistake has an impact on the consolidated reserves of the concerned company. If the difference is material, a comment will be added to the notes of the consolidated accounts.


## Related Topics

- Dividend elimination

---
*Chunk 115 | Key Points:*