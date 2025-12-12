# Chunk 244: 6.5 How to manage historical rates on the equity accounts?

## Context

This section addresses foreign currency translation. Contains formula: closing rate value of capital is  150 = 100^{*}1.5  instead of historical rate  160 = 100^{*}1.6 . S. Shows detailed calculations.

## Content

- In Year 1, closing rate value of capital is  150 = 100^{*}1.5  instead of historical rate  160 = 100^{*}1.6 . So we have to increase by 10 the translated amount of the capital. That means a credit of 10 on Capital account and a debit of 10 on the Translation currency account.

- In Year 2, the process is made in two steps. First, we carry forward the Year 1 historical adjustment of 10 and secondly we compare the closing value of capital in Year 2 with the corresponding value in Year 1, which is  20 = 170 - 150 . That amount becomes the adjustment of Year 2 as shown above: debit capital for 20 and credit Translation adjustments for 20.  
- In Year 3, we apply the same two processes. First, carry forward of both Year 1 and Year 2 translation adjustments and then compare closing value of capital between Year 3 and Year 2,  10 = 180 - 170 , which gives a debit capital for 10 and a credit Translation adjustments or 10.  
- Year 4 is a little bit complicated because of the capital increase. First, let's carry forward the historical adjustments related to Year 1, Year 2 and Year 3. Then, the capital amount of 120 CUR must be split into 100 CUR and 20 CUR. For the 100 CUR, we apply the same rule: closing rate value of Year 4 - closing rate value of Year 3 = (40) = 140 - 180 which becomes a debit translation adjustment for 40 and a credit capital for 40. Finally, the capital increase for 20 has been translated at closing rate 1.4 instead of transaction rate 1.55, giving a difference of  3 = 20^{*}  [1.55 - 1.41. So we have to debit the Translation adjustments for 3 and credit the capital for 3.

In most consolidation software, this kind of process is automatically provided, based on what has been explained in this section. None keeps tracks of individual rates. All of them are using adjustments.

We can easily understand that after a certain number of years, the number of translation adjustments increase. After audit, it is recommended to aggregate them in order to keep their number reasonable.


## Related Topics

- Currency translation

---
*Chunk 244 | 6.5 How to manage historical rates on the equity accounts?*