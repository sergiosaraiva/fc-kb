# Reconcile intercompany data

## Metadata
- **Index**: 0340
- **Topics**:  Intercompany Transactions, Data Validation, Matching and Elimination, Report Generation
- **Keywords**:  Intercompany Matching, Intercompany Elimination, Validation Report, Matching Rules, Automatic Elimination, Threshold, Partner Companies, Transaction Reconciliation, Currency Impact, Fiscal Year Differences
- **Theory Reference**: Intercompany Eliminations

## Summary

 The provided documentation for the Financial Consolidation product covers detailed instructions on managing intercompany transactions, data validation, intercompany matching and elimination, and report generation. The Intercompany Transactions section explains how to match and reconcile transactions between group companies. The Data Validation section details generating validation reports to identify intercompany differences. The Matching and Elimination section provides steps for setting up automatic eliminations and correcting intercompany details. The Report Generation section explains how to create and download intercompany validation and matching reports.

---

## User Guide

Intercompany matching
Intercompany Matching page is used for "matching" transactions between the companies in a group for the purpose of elimination and reconciliation. Intercompany matching is necessary when there are differences in intercompany transactions. Reasons for intercompany differences include:

Invoice booked by one company and the corresponding purchase not booked by the other company
Companies ending their fiscal year at different dates
Impact of currency rates on intercompany transactions
Transaction with a turnover on one side and a purchase booked as an asset on the other side
VAT not refundable

To access the Intercompany Matching page, click Consolidation > Consolidation > Intercompany Matching.

The left-side panel displays details on the intercompany matching/unmatching transactions as follows:
Rule - the intercompany elimination rule used for displaying the detailed information.
Company (above) - code, name, and the local currency of the company identified as the debit company for the debit transaction.
Company (below) - code, name, and the local currency of the company identified as the credit company for the credit transaction.
Under the company identification are all amounts that contribute to the reconciliation. This information is shown as a table with the following columns: Account - the account on which the amounts are booked, Journal - the journal code and category on which the amounts are booked, Entry - the journal entry number, Description - the journal description, Amount - the amount in group currency.

The right-side panel is where you use certain criteria to filter the intercompany information you want to display on the left:
Threshold - the amount under which any intercompany difference is ignored. Filter group box includes filters such as Unmatched Transactions, Matched Transactions, Exclude Equity Method and NC, Merge Debit and Credit amounts. Set Threshold allows you to limit the intercompany reconciliation to one specific Intercompany Elimination rule.

Set threshold
1. In the Threshold field, click.
2. In the Threshold window set the amounts at which the differences will not be displayed. There is one line for each Intercompany Elimination rule, meaning you can define different thresholds for different rules.
3. To save the modifications you make to the threshold, click.

Correct intercompany details
On this page, you can correct intercompany details. The Intercompany Rule, Company and Partner Company, including code, name, and local currency, are displayed.

1. Search for the account on which you want to make the correction. Only accounts defined as Intercompany Accounts will appear on the list.
2. Enter the amount that you want to correct. You can choose to correct the difference in Group Currency or in the Local Currency of the company.
3. Click to add the difference amount to the Bundle Amount of the selected account. These modifications impact the statutory bundle of the company mentioned in the Company field, on the account selected in the Account field, and with the partner identified in the Partner field. The amount to be added can be indicated either in the consolidation currency or in the local currency of the company. Conversion to the consolidation currency will be carried out automatically if you choose to correct the amount in the local currency.
4. After modifying a statutory bundle to correct intercompany differences, carry out a new validation of the statutory bundle.

Generate Group Adjustment
1. There are three types of adjustments. Select one of them:
- Transfer Difference: used for transferring the difference amount from the group transactions towards the out-of-group, or vice versa.
- Reclassify Difference: used for reclassifying the difference found on an intercompany P&L account to a currency translation difference account.
- Book Difference: used for booking the difference found on an intercompany Balance Sheet account to a translation difference account. The difference will be booked in P&L for the current period, and the adjustment will be counter-passed during the next period.
2. To set up these adjustments, click to redirect to the adjustment page. On this page, modify the “Posting journal” of the “IC-915-1”, “IC-915-2” and “IC-915-3” eliminations.
3. Set up the adjustments and click.
4. When finished, click to close this window and return to the main page.

Print intercompany differences or matched transactions
On the Intercompany Matching page, click to open the Report page and print the intercompany differences or the matched transactions identified during the last Intercompany Matching/Reconciliation process.

1. Select one or more companies. If you want to select all lines, click on the checkbox at the top of the list.
2. Select the criteria to create the report. In the Filter section, you will see the conditions used to run the reconciliation — Unmatched Transactions, Matched Transactions, and Merge Debit/Credit.
3. Next, for the selected companies, two options are possible:
- Within selected companies - to print out a report that will list all differences within only the selected companies and rules.
- Within any other company - to print out a report that will list all differences related to the selected companies, regardless of where these differences come from (selected/non-selected companies).
4. In the File type field, select the output file type. Options include PDF, XLS, and XLSX.
5. Click to generate the report. After the report is generated, a download link appears below for you to click and view it in the file type selected.
6. Click to close this window and return to the Intercompany Matching page.

Link intercompany eliminations to rules
On the Intercompany Elimination page, you can establish automated intercompany eliminations for variances that fall below the threshold you specify. This helps document intercompany conversion discrepancies and actual variances on designated accounts. Intercompany elimination removes transactions between subsidiary companies in a group.

To set up automatic intercompany eliminations:
1. In the Account Number field of the Elimination Code, click.
2. From the Select an Account pop-up, select the account for which you want to set up the automatic elimination and click.
3. Click.
4. To return to the Define IC Rules page, click.

Define IC Rules
Define intercompany rules to manage how transactions between companies are processed and eliminated during consolidation. Access the Intercompany Elimination page to configure these rules.

Intercompany validation report
On the Intercompany Validation report page, generate a printed report that displays intercompany differences. The report focuses on the chosen company and showcases all intercompany transactions involving the selected partners, based on specified rules. The differences are presented in the currency of the selected company.

To access the Intercompany Validation report page, click Data Entry > Validation Reports > Intercompany Validation.

Generate an IC validation report:
1. From the Companies field, select a company.
2. From the Partner companies list, select the partner companies you want on the report.
3. From the Intercompanies Rules list, select the rules you want to apply.
4. In the Filter box, use options to narrow down the data on your report: Use Threshold, Merge Debit/Credit, Unmatched Transactions, Matched Transactions.
5. In the File type field, select the output file type. Options include PDF, XLS, and XLSX.
6. Click to generate the report. After the report is generated, a download link appears below for you to click and view it in the selected file type.

---

## Frequently Asked Questions

### General

**What details are displayed on the Intercompany Matching page?**
The left-side panel displays details on intercompany matching/unmatching transactions including Rule, Company code and name, local currency, Account, Journal, Entry, Description, and Amount.

**What should you do after modifying a statutory bundle to correct intercompany differences?**
Carry out a new validation of the statutory bundle to ensure the corrections are accurate.

**What options are available in the Filter section for generating an Intercompany Validation report?**
Options include using Threshold, merging Debit/Credit, showing Unmatched Transactions, and showing Matched Transactions.

**What information is displayed under the company identification in intercompany matching?**
Information displayed includes Account, Journal code and category, Entry number, Description, and Amount in group currency.

**What criteria can be used to filter intercompany information?**
Criteria include Threshold, Unmatched Transactions, Matched Transactions, Exclude Equity Method and NC, and Merge Debit/Credit amounts.

**What are Transfer Difference adjustments used for?**
Transfer Difference adjustments are used for transferring the difference amount from group transactions to out-of-group transactions or vice versa.

**What are some reasons for intercompany differences?**
Reasons for intercompany differences include invoice booking discrepancies, different fiscal year-end dates, currency rate impacts, and VAT non-refundability.

**What information is displayed in the right-side panel of the Intercompany Matching page?**
The right-side panel allows you to filter intercompany information using criteria such as Threshold, Unmatched Transactions, Matched Transactions, Exclude Equity Method and NC, and Merge Debit/Credit amounts.

**How can you correct intercompany details on the Intercompany Matching page?**
To correct intercompany details, search for the account, enter the correction amount, and click to add the difference amount to the Bundle Amount of the selected account.

**What are the three types of adjustments available for intercompany differences?**
The three types of adjustments are Transfer Difference, Reclassify Difference, and Book Difference.

**How can you print intercompany differences or matched transactions?**
On the Intercompany Matching page, click to open the Report page, select companies, criteria, and file type, then click to generate and view the report.

**What should you do after correcting intercompany details?**
After correcting intercompany details, validate the statutory bundle to ensure the changes are accurately reflected.

**What information is shown in the left-side panel of the Intercompany Matching page?**
The left-side panel displays intercompany matching details such as Rule, Company code and name, local currency, Account, Journal, Entry, Description, and Amount.

**What options are available in the Filter section of the Intercompany Validation report page?**
Options include using Threshold, merging Debit/Credit, showing Unmatched Transactions, and showing Matched Transactions.

**What information is displayed in the left-side panel of the Intercompany Matching page?**
The left-side panel displays intercompany matching details such as Rule, Company code and name, local currency, Account, Journal, Entry, Description, and Amount.

**What information is shown in the right-side panel of the Intercompany Matching page?**
The right-side panel allows you to filter intercompany information using criteria such as Threshold, Unmatched Transactions, Matched Transactions, Exclude Equity Method and NC, and Merge Debit/Credit amounts.

### How-To

**How do you set a threshold for intercompany differences?**
In the Threshold field, click to open the Threshold window, set the amounts for each Intercompany Elimination rule, and click to save the modifications.

**How do you print a report of intercompany differences?**
Click on the Intercompany Matching page, select companies and criteria, and choose the file type before generating the report.

**How do you merge Debit and Credit amounts in intercompany matching?**
In the Filter group box, select the Merge Debit and Credit amounts option to combine these amounts for reconciliation.

**How do you generate a report of matched transactions?**
On the Intercompany Matching page, click to open the Report page, select companies, criteria, and file type, then generate the report.

**How do you use the Reclassify Difference adjustment?**
The Reclassify Difference adjustment reclassifies the difference found on an intercompany P&L account to a currency translation difference account.

**How do you set up Transfer Difference adjustments?**
Click to redirect to the adjustment page, modify the Posting journal, set up the adjustments, and click to apply.

**What steps are involved in correcting intercompany details?**
Search for the account, enter the correction amount, and click to add the amount to the Bundle Amount. Then validate the statutory bundle.

**How do you set up automatic intercompany eliminations?**
In the Account Number field, click to select the account for automatic elimination, then click to confirm the setup.

**How do you generate an Intercompany Validation report?**
Select a company, partner companies, rules, and file type on the Intercompany Validation report page, then click to generate and view the report.

**How does currency rate impact intercompany transactions?**
Currency rate differences can affect the value of intercompany transactions, leading to discrepancies when consolidating financial data.

**How do you correct a difference amount in intercompany matching?**
Search for the account, enter the correction amount, and click to add the difference amount to the Bundle Amount of the selected account.

**How do you apply a correction amount in intercompany matching?**
Enter the correction amount in the Group Currency or Local Currency field and click to add the difference to the Bundle Amount.

**What steps are involved in setting up automatic intercompany eliminations?**
Click in the Account Number field, select the account for automatic elimination, and click to confirm the setup.

**How do you set up adjustments for intercompany differences?**
To set up adjustments, click to redirect to the adjustment page, modify the Posting journal, set up the adjustments, and click to apply.

**How do you link intercompany eliminations to rules?**
On the Intercompany Elimination page, click in the Account Number field, select the account for automatic elimination, and click to return to the Define IC Rules page.

**How do you filter intercompany information on the Intercompany Matching page?**
Use the right-side panel to set criteria such as Threshold, Unmatched Transactions, Matched Transactions, Exclude Equity Method and NC, and Merge Debit/Credit amounts.

**How do you correct intercompany details on the Intercompany Matching page?**
Search for the account, enter the correction amount, and click to add the difference amount to the Bundle Amount of the selected account.

### Concepts

**What is the purpose of the Book Difference adjustment?**
The Book Difference adjustment is used for booking the difference found on an intercompany Balance Sheet account to a translation difference account.

**What is the purpose of the Threshold field in intercompany matching?**
The Threshold field is used to set the amount under which any intercompany difference is ignored, helping to filter the displayed intercompany information.

**What is the purpose of the Intercompany Matching page?**
The Intercompany Matching page is used for matching transactions between companies in a group for elimination and reconciliation purposes.

**What is the function of the Filter group box in intercompany matching?**
The Filter group box allows users to filter intercompany information by unmatched or matched transactions, excluding equity method and NC transactions, and merging debit and credit amounts.

**What is the role of the Intercompany Rule in correcting intercompany details?**
The Intercompany Rule defines how the correction amounts are applied to the reconciliation of intercompany transactions.

**What is the purpose of the Intercompany Validation report?**
The Intercompany Validation report displays intercompany differences for a chosen company, showing transactions with selected partners based on specified rules.

**What is the impact of different fiscal year-end dates on intercompany transactions?**
Different fiscal year-end dates can cause discrepancies in intercompany transactions as companies may record transactions at different times.

**What is the function of the Threshold window in intercompany matching?**
The Threshold window allows you to set the amounts at which intercompany differences will not be displayed, with different thresholds for each elimination rule.

**What is the purpose of intercompany matching?**
Intercompany matching aims to reconcile transactions between group companies, ensuring accurate elimination and reconciliation of intercompany differences.

**What is the purpose of the Reclassify Difference adjustment?**
The Reclassify Difference adjustment is used to reclassify the difference found on an intercompany P&L account to a currency translation difference account.

### Navigation

**How do you access the Define IC Rules page?**
To access the Define IC Rules page, navigate to the Intercompany Elimination page and click to configure the rules for intercompany transactions.

**How do you access the Intercompany Validation report page?**
Click Data Entry > Validation Reports > Intercompany Validation to access the page.

**How do you access the Intercompany Matching page?**
To access the Intercompany Matching page, click Consolidation > Consolidation > Intercompany Matching.

---

*Help Topic 0340 | Category: Validation | Last Updated: 2024-12-03*