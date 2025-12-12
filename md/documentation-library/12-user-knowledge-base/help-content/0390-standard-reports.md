# Standard Reports

## Metadata
- **Index**: 0390
- **Topics**:  Company Reports, Intercompany Reconciliation, Local Bundle Reports, Shareholders and Partners
- **Keywords**:  Company Reports, Intercompany Reconciliation, Local Bundle, Shareholders, Partners, Financial Rights, Control Rights, Adjusted Amounts, Transactions, Data Analysis
- **Theory Reference**: Consolidated Financial Statements

## Summary

 The documentation for the Financial Consolidation product covers comprehensive instructions on generating various types of reports, including company reports, intercompany reconciliation, local bundle reports, and shareholders/partners reports. The Company Reports section explains how to generate standard and detailed reports on company information. The Intercompany Reconciliation section details the process of identifying and resolving unmatched intercompany transactions. The Local Bundle Reports section provides instructions on generating reports for local amounts, adjusted amounts, and various related financial details. The Shareholders and Partners section outlines generating reports on financial and control rights of shareholders and partners, along with participation details.

---

## User Guide

Company reports
The Companies page allows you to create company reports that contain information about the companies within a group.

To access the Companies page, click Reports > Standard Reports > Companies.

Types of reports
These report types are available:
- Standard (user) report: This report gives a summary of the most important parameters of the companies, including the local currency, the deferred tax settings, the consolidation method, the number of issued shares, the percentage of financial interest of the group, and the third parties. This report shows multiple companies per page.
- Detailed report: This report gives an overview of all parameters of the company. This report shows one company per page.

Generate a report of companies:
1. In the Period and Ref Period fields, leave the default consolidation periods, or click to select the consolidation period you want.
2. Select a Report type.
3. In the Sorting field, specify how the companies should be displayed on the report — by company code or company name.
4. In the Filtering field, select an option to either include all the companies in the group in the report or only the consolidated companies.
5. In the File type field, select the output file type. Options include PDF, XLS, and XLSX.
6. Click to generate the report. After the report is generated, a download link appears below for you to click and view it in the selected file type.

Intercompany reconciliation report
The Intercompany Reconciliation report is designed to identify unmatched intercompany transactions, which refers to paired transactions that have inconsistencies in terms of amounts, currencies, or those that have not been matched with their corresponding transactions. By running this report, you can effectively address any discrepancies found in sales and billing information between intercompany partners.

To access the Intercompany Reconciliation Report page, click Reports > Standard Reports > Intercompany Reconciliation report.

Generate an intercompany reconciliation report:
1. In the Companies table, select the companies.
2. In the Intercompany rules table, select the rule/rules to run on the report.
3. In the Filter section, specify:
- the type of transactions to include on the report. You can select Matched Transactions or Unmatched Transactions, or both.
- whether to Exclude Equity Method and Non-Cash (NC) transactions.
- whether to Merge Debit/Credit transactions on the report. If this option is not selected, debit/credit transactions will be listed in separate columns.
4. In the For the selected companies print differences panel, choose how you want differences to be printed.
5. From the Journal Summation drop-down list, select an option to specify how you want the accounting codes and ledger entries organized on the report.
6. To include a Point of View, click to search for and select one.
7. In the File type field, select the output file type. Options include PDF, XLS, and XLSX.
8. Click to generate the report. After the report is generated, a download link appears below for you to click and view it in the selected file type.

Local bundle report
On the Local Bundles page, you have the ability to generate reports of local amounts.

To access the Local Bundles page, click Reports > Standard Reports > Local Bundles.

Types of reports:
- Local Amounts report: This report is based on the statutory accounts (before local adjustments). The first column of the report displays the data of the current environment, the second column displays the data of the reference environment, and the third column calculates the difference between both.
- Adjusted Amounts report: This report is based on the adjusted accounts (after local adjustments). The first column of the report displays the data of the current environment, the second column displays the data of the reference environment, and the third column calculates the difference between both.
- Local Amounts and Adjustments report: This report provides details of the statutory accounts in the first column, the details of the local adjustments in the second column, and the details of the adjusted accounts in the third column.
- Local Adjustments report: This report provides an overview of the local adjustments.
- Participations report: This report gives details of the shareholding accounts.
- Intercompanies report: This report provides a detailed breakdown of all intercompany-related accounts for both actual and reference Consolidation Periods.
- Partners report: This report provides a detailed breakdown of all partner-related accounts for both actual and reference Consolidation Periods.
- Dimensions report: This report provides a detailed breakdown of all dimension-related accounts for both actual and reference Consolidation Periods.
- Flows report: This report gives the details of the financial flows. You can restrict what type of flows you want to display in your report.
- Manual Flows: Balance Sheet accounts consisting of flows that have been input manually.
- Automatic Flows: Balance Sheet accounts consisting of flows automatically generated by Financial Consolidation.

Generate a local bundle report:
1. In the Ref Period field, enter a reference consolidation period or click to search for one.
2. Select the type of report you want to run.
3. In the Companies selection box, select the company you want to use to generate the report. You can select one, multiple, or all companies.
4. In the File type field, select the output file type.
5. Click to generate the report. After the report is generated, a download link appears below for you to click and view it in the selected file type.

Participations, shareholders, and partners report
The Participations / Shareholders / Partners report shows the allocation of shares held by participation, shareholders, and partners in the group.

To access the Participations / Shareholders / Partners page, click Reports > Standard Reports > Participations / Shareholders / Partners.

Types of reports:
- Shareholders - Financial Rights: This report shows the direct shareholders of the companies in terms of financial rights.
- Shareholders - Control Rights: This report shows the direct shareholders of the companies in terms of control rights.
- Shareholding - Financial Rights: This report shows a company’s shareholdings in other companies in terms of financial rights.
- Shareholding - Control Rights: This report shows a company’s shareholdings in other companies in terms of control rights.

Generate a shareholding report:
1. In the Period and Ref Period fields, leave the default consolidation periods, or click to select the consolidation period you want.
2. Select a report type.
3. Optionally, select Show changes only to only show changes in shareholders/shareholding rights on the report.
4. In the File type field, select the output file type. Options include PDF, XLS, and XLSX.
5. Click to generate the report. After the report is generated, a download link appears below for you to click and view it in the selected file type.

General ledger by calculated account report
The Ledger by Calculated Account page allows you to generate reports on selected calculated accounts and companies.

To access the Ledger by Calculated Account report page, click Reports > Standard Reports > Ledger by Calculated Account.

The left-side panel displays the Accounts you can include in the report including their Code and Description.

The right-side panel displays the Companies you can include in your report, including their Code and Description.

Generate a ledger by calculated account report:
1. From the Accounts list, select the account(s) you want on the report.
2. From the Companies list, select the companies you want.
3. Point of View: a dimension setting that controls data displayed in the report. Select a point of view.
4. Sort order: how the report is arranged. Select either by accounts or by companies.
5. Period: consolidation periods. Select either the Current consolidation period or the Reference consolidation period.
6. Journal View: different stages or levels in the consolidation by which you can view the report. Select a journal view.
7. In the File type field, select the output file type. Options include PDF, XLS, and XLSX.
8. Click to generate the report. After the report is generated, a download link appears below for you to click and view it in the selected file type.

General ledger report
The General Ledger report page allows you to create reports of financial activities of companies in the group.

To access the General Ledger report page, click Reports > Standard Reports > General Ledger.

The left-side panel displays the Accounts you can include in the report and their Code and Description, Account Type, Debit/Credit.

The right-side panel displays the Companies you can include in your report, including their Code and Description.

Generate a general ledger report:
1. From the Accounts list, select the account code(s).
2. From the Companies list, select the companies you want on the report.
3. In the Calc Account field, enter the calculated account or click to find a calculated account to include on the report.
4. From the Point of View drop-down, select a point of view (the dimension setting that will control the data displayed in the report) and then, click to select a Point of View detail.
5. For Sort Order, specify how you want the report to be arranged.
6. For Period, select either Current consolidation period or Reference consolidation period.


7. From the Journal View drop-down, select a view.
8. In the File type field, select the output file type. Options include PDF, XLS, and XLSX.
9. Click to generate the report. After the report is generated, a download link appears below for you to click and view it in the selected file type.

Bundle last modified report
The Bundle Last Modified page allows you to create a report of recently modified bundles.

To access the Bundle Last Modified page, click Reports > Standard Reports > Bundle Last Modified.

Generate a bundle last modified report:
1. In the Period field, click to search for and select the current consolidation period.
2. In the Ref Period field, click to search for and select a reference consolidation period.
3. In the File type field, select the output file type. Options include PDF, XLS, and XLSX.
4. Click to generate the report. After the report is generated, a download link appears below for you to click and view it in the selected file type.

---

## Frequently Asked Questions

### Navigation

**How do you access the General Ledger report page?**
To access the General Ledger report page, click Reports > Standard Reports > General Ledger.

**How do you access the Bundle Last Modified page?**
To access the Bundle Last Modified page, click Reports > Standard Reports > Bundle Last Modified.

**How do you access the Equity Analysis page?**
To access the Equity Analysis page, click Reports > Drill-Down Analysis > Equity Analysis.

**How do you access the Shareholders Analysis page?**
To access the Shareholders Analysis page, click Reports > Drill-Down Analysis > Shareholder Analysis.

**How do you navigate across companies in the Shareholders Analysis page?**
Click to navigate back and forward across companies.

**How do you access the Companies page?**
To access the Companies page, click Reports > Standard Reports > Companies.

**How do you access the Intercompany Reconciliation Report page?**
To access the Intercompany Reconciliation Report page, click Reports > Standard Reports > Intercompany Reconciliation report.

**How do you access the Local Bundles page?**
To access the Local Bundles page, click Reports > Standard Reports > Local Bundles.

**How do you access the Participations / Shareholders / Partners page?**
To access the Participations / Shareholders / Partners page, click Reports > Standard Reports > Participations / Shareholders / Partners.

**How do you access the Ledger by Calculated Account report page?**
To access the Ledger by Calculated Account report page, click Reports > Standard Reports > Ledger by Calculated Account.

**How do you access the Drill-Down Analysis page?**
To access the Drill-Down Analysis page, click Reports > Drill-Down Analysis.

**How do you access the Bundle Last Modified report page?**
To access the Bundle Last Modified report page, click Reports > Standard Reports > Bundle Last Modified.

### General

**What information does the General Ledger report provide?**
The General Ledger report provides details of financial activities of companies in the group, including account codes, descriptions, and debit/credit information.

**What details are provided for each line in the Equity Analysis page?**
For each line, you get the Account, Journal Code, Journal Entry Number, Journal Description, and the Amount.

**How are debit and credit amounts presented in the Equity Analysis page?**
Debit amounts are presented as positive values, while credit amounts are presented as negative values.

**What details are provided for each line in the Shareholders Analysis page?**
For each line, you get the Account, Journal Code, Journal Entry Number, Journal Description, Company Name, and the Amount.

**How are amounts presented in the Shareholders Analysis page?**
Debit amounts are presented as positive values, while credit amounts are presented as negative values.

**What information does the Local Amounts and Adjustments report provide?**
The Local Amounts and Adjustments report provides details of the statutory accounts, local adjustments, and adjusted accounts.

**What types of reports are available on the Companies page?**
The available report types are Standard (user) report and Detailed report.

**What information does the Standard company report include?**
The Standard company report includes local currency, deferred tax settings, consolidation method, number of issued shares, percentage of financial interest of the group, and third parties.

**What filtering options are available when generating a company report?**
You can filter to include all companies in the group or only the consolidated companies.

**What file types can you select for generating a company report?**
The available file types are PDF, XLS, and XLSX.

**What options can you specify in the Filter section of the Intercompany Reconciliation report?**
You can specify the type of transactions (Matched or Unmatched), exclude Equity Method and Non-Cash transactions, and choose to merge debit/credit transactions.

**What information does the Intercompany Reconciliation report provide?**
The report provides details of paired transactions with inconsistencies in terms of amounts, currencies, or unmatched transactions.

**What types of reports can you generate from the Local Bundles page?**
You can generate Local Amounts report, Adjusted Amounts report, Local Amounts and Adjustments report, Local Adjustments report, Participations report, Intercompanies report, Partners report, Dimensions report, and Flows report.

**What information does the Adjusted Amounts report provide?**
The Adjusted Amounts report provides data of the current environment, data of the reference environment, and the difference between both after local adjustments.

**What information does the Local Adjustments report provide?**
The Local Adjustments report provides an overview of the local adjustments.

**What information does the Participations report provide?**
The Participations report gives details of the shareholding accounts.

**What information does the Intercompanies report provide?**
The Intercompanies report provides a detailed breakdown of all intercompany-related accounts for both actual and reference Consolidation Periods.

**What information does the Partners report provide?**
The Partners report provides a detailed breakdown of all partner-related accounts for both actual and reference Consolidation Periods.

**What information does the Dimensions report provide?**
The Dimensions report provides a detailed breakdown of all dimension-related accounts for both actual and reference Consolidation Periods.

**What information does the Flows report provide?**
The Flows report gives the details of the financial flows, including Manual Flows and Automatic Flows.

**What types of reports can you generate from the Participations / Shareholders / Partners page?**
You can generate Shareholders - Financial Rights, Shareholders - Control Rights, Shareholding - Financial Rights, and Shareholding - Control Rights reports.

**What information does the Shareholders - Financial Rights report provide?**
The Shareholders - Financial Rights report shows the direct shareholders of the companies in terms of financial rights.

**What information does the Shareholders - Control Rights report provide?**
The Shareholders - Control Rights report shows the direct shareholders of the companies in terms of control rights.

**What information does the Shareholding - Financial Rights report provide?**
The Shareholding - Financial Rights report shows a company’s shareholdings in other companies in terms of financial rights.

**What information does the Shareholding - Control Rights report provide?**
The Shareholding - Control Rights report shows a company’s shareholdings in other companies in terms of control rights.

**What option can you select to show changes only in a shareholding report?**
You can select the Show changes only option to only show changes in shareholders/shareholding rights on the report.

**What file types can you select for generating a shareholding report?**
The available file types are PDF, XLS, and XLSX.

**What information can you include in the Ledger by Calculated Account report?**
You can include selected calculated accounts, companies, point of view, sort order, period, and journal view.

**What information can you include in the General Ledger report?**
You can include selected accounts, companies, calculated account, point of view, sort order, period, and journal view.

**What information can you include in the Bundle Last Modified report?**
You can include the current consolidation period, reference consolidation period, and select the output file type.

**What information is displayed in the top panel of the Equity Analysis page?**
The top panel contains the equity from the Current Consolidation Period for the selected company.

**What information is displayed in the bottom panel of the Equity Analysis page?**
The bottom panel contains the equity from the Reference Consolidation Period for the selected company.

**What file types can you select for generating an Equity Analysis report?**
The available file types are PDF, XLS, and XLSX.

**What options are available for sorting data in the Drill-Down Analysis page?**
Go to the Sort on box and make a selection.

**What options are available for viewing contributions by company in the Drill-Down Analysis page?**
Go to the Navigation box and select contributions by company.

**What options are available for viewing local amounts in the Drill-Down Analysis page?**
Go to the Navigation box and select local amounts.

**What options can you specify for data analysis on the Drill-Down Analysis page?**
You can sort data and view contributions by company or local amounts for detailed analysis.

### How-To

**How do you generate a general ledger report?**
1. Select the accounts. 2. Select the companies. 3. Enter a calculated account. 4. Select a point of view. 5. Specify sort order. 6. Select the period. 7. Select a journal view. 8. Select the output file type. 9. Click to generate the report.

**How do you generate a bundle last modified report?**
1. Select the current consolidation period. 2. Select the reference consolidation period. 3. Select the output file type. 4. Click to generate the report.

**How do you justify the equity on the Equity Analysis page?**
1. Enter the company name. 2. Click . 3. Analyze the lines displayed. 4. Select lines to analyze. 5. Click to launch the justification process. 6. Click to remove selected lines. 7. Repeat until all lines are justified.

**How do you justify shareholders on the Shareholders Analysis page?**
1. Enter the company code. 2. Click . 3. Analyze the lines displayed. 4. Click to remove unnecessary lines. 5. Review account, journal, and amount details. 6. Total amounts are displayed for Current and Reference periods. 7. Click to remove selected lines. 8. Click to refresh the page. 9. Click to open the Shareholders Report page.

**How do you generate a report on the Shareholders Analysis page?**
Click to open the Shareholders Report page.

**How do you address discrepancies in shareholder investments?**
Use the Shareholders Analysis page to compare investments across different periods and identify variations due to local book entries or adjustments.

**How do you compare ownership changes in equity analysis?**
Use the Equity Analysis page to compare the ownership stake of a company across two different consolidation periods and justify the changes.

**How do you track equity and shareholder changes?**
Use the Equity Analysis and Shareholders Analysis pages to compare ownership and investments across different consolidation periods.

**How do you analyze changes in bundle data?**
Generate a Bundle Last Modified report to create a report of recently modified bundles and analyze the changes.

**How do you compare equity ownership across consolidation periods?**
Use the Equity Analysis page to compare the equity owned by a specific company across two different consolidation periods.

**How do you compare shareholder investments across periods?**
Use the Shareholders Analysis page to compare investments of all shareholders in a specific company during two different periods.

**How do you include a Point of View in a report?**
Click to search for and select a Point of View.

**How do you perform a detailed analysis of local amounts?**
Generate a Local Amounts report from the Local Bundles page to analyze data of the current and reference environments and their differences.

**How do you generate a company report?**
1. Select the consolidation periods. 2. Select a Report type. 3. Specify Sorting and Filtering options. 4. Select the output file type. 5. Click to generate the report.

**How do you generate an intercompany reconciliation report?**
1. Select the companies. 2. Select the intercompany rules. 3. Specify Filter options. 4. Select Journal Summation and Point of View. 5. Select the output file type. 6. Click to generate the report.

**How do you generate a local bundle report?**
1. Enter a reference consolidation period. 2. Select the type of report. 3. Select the companies. 4. Select the output file type. 5. Click to generate the report.

**How do you generate a shareholding report?**
1. Select the consolidation periods. 2. Select a report type. 3. Optionally, select Show changes only. 4. Select the output file type. 5. Click to generate the report.

**How do you generate a ledger by calculated account report?**
1. Select the accounts. 2. Select the companies. 3. Select a point of view. 4. Specify sort order. 5. Select the period. 6. Select a journal view. 7. Select the output file type. 8. Click to generate the report.

**How do you remove lines from the overview in the Equity Analysis page?**
Click to remove the selected lines. Note: Removing lines does not delete them; they are just removed from the overview.

**How do you perform a drill-down analysis for equity changes?**
Use the Equity Analysis page to compare equity owned by a company across two consolidation periods and justify the changes.

**How do you perform a drill-down analysis for shareholder investments?**
Use the Shareholders Analysis page to compare shareholder investments across two periods and identify variations due to local book entries or adjustments.

**How do you analyze fluctuations in equity ownership?**
Use the Equity Analysis page to justify equity changes and analyze fluctuations in ownership between consolidation periods.

**How do you compare shareholder investments?**
Use the Shareholders Analysis page to compare investments across different periods and identify variations due to local book entries or adjustments.

**How do you address discrepancies in intercompany transactions?**
Generate an Intercompany Reconciliation report to identify and resolve unmatched intercompany transactions.

**How do you filter transactions in the Intercompany Reconciliation report?**
You can filter transactions by type (Matched or Unmatched), exclude Equity Method and Non-Cash transactions, and choose to merge debit/credit transactions.

**How do you view changes in shareholders/shareholding rights?**
Generate a shareholding report and select the Show changes only option to view changes in shareholders/shareholding rights.

**How do you include calculated accounts in a report?**
From the Accounts list, select the account(s) you want on the report, including calculated accounts.

**How do you arrange a report by accounts or companies?**
Select the sort order as either by accounts or by companies when generating the report.

**How do you include a journal view in a report?**
Select a journal view from the Journal Summation drop-down list.

**How do you view contributions by company in a report?**
Select the contributions by company option in the Navigation box on the Drill-Down Analysis page.

**How do you analyze control rights of shareholders?**
Generate a Shareholders - Control Rights report to analyze the direct shareholders of the companies in terms of control rights.

**How do you analyze financial rights of shareholders?**
Generate a Shareholders - Financial Rights report to analyze the direct shareholders of the companies in terms of financial rights.

**How do you analyze financial rights of a company’s shareholdings?**
Generate a Shareholding - Financial Rights report to analyze a company’s shareholdings in other companies in terms of financial rights.

**How do you analyze control rights of a company’s shareholdings?**
Generate a Shareholding - Control Rights report to analyze a company’s shareholdings in other companies in terms of control rights.

**How do you generate an audit trail report?**
1. Select the consolidation periods. 2. Select a journal view. 3. Choose the report to generate. 4. Select the output file type. 5. Click to generate the report.

### Concepts

**What is the purpose of the Company Reports section?**
The Company Reports section explains how to generate standard and detailed reports on company information.

**What is the purpose of the Intercompany Reconciliation section?**
The Intercompany Reconciliation section details the process of identifying and resolving unmatched intercompany transactions.

**What is the purpose of the Local Bundle Reports section?**
The Local Bundle Reports section provides instructions on generating reports for local amounts, adjusted amounts, and various related financial details.

**What is the purpose of the Shareholders and Partners section?**
The Shareholders and Partners section outlines generating reports on financial and control rights of shareholders and partners, along with participation details.

**What does the Equity Analysis page provide?**
The Equity Analysis page provides a way to compare the equity owned by a specific company across two different consolidation periods.

**What does the Shareholders Analysis page provide?**
The Shareholders Analysis page provides a way to compare the investments of all shareholders in a specific company during two different periods.

**What is the purpose of the Equity Analysis section?**
The Equity Analysis section explains how to justify equity changes and analyze fluctuations in equity ownership.

**What is the purpose of the Shareholders Analysis section?**
The Shareholders Analysis section provides guidance on comparing shareholder investments and identifying variations due to local book entries or adjustments.

**What is the purpose of the Detailed company report?**
The Detailed company report provides an overview of all parameters of the company, showing one company per page.

**What is the purpose of the Intercompany Reconciliation report?**
The Intercompany Reconciliation report identifies unmatched intercompany transactions, addressing discrepancies in sales and billing information between intercompany partners.

**What does the Local Amounts report provide?**
The Local Amounts report provides data of the current environment, data of the reference environment, and the difference between both.

**What is displayed in the Difference field in the Equity Analysis page?**
The Difference field shows the difference between the equity of the Current and Reference Consolidation Periods.

**What is displayed in the Selected Amount field in the Equity Analysis page?**
The Selected Amount field shows the total for the selected lines in the Current and Reference periods.

**What is displayed in the Current field in the Equity Analysis page?**
The Current field shows the total for all the lines for the Current Consolidation Period.

**What is displayed in the Reference field in the Equity Analysis page?**
The Reference field shows the total for all the lines for the Reference Consolidation Period.

**What is the purpose of the Drill-Down Analysis page?**
The Drill-Down Analysis page allows for detailed data analysis and viewing contributions by company or local amounts.

**What is the purpose of the Reporting section?**
The Reporting section provides instructions for generating various types of financial reports, including company reports, intercompany reconciliation, local bundle reports, and shareholders/partners reports.

**What is displayed in the Selected Amount field in the Shareholders Analysis page?**
The Selected Amount field shows the total for the selected lines in the Current and Reference periods.

**What is displayed in the Difference field in the Shareholders Analysis page?**
The Difference field shows the difference between the total amounts of the Current and Reference periods.

**What is the purpose of the Audit Trail section?**
The Audit Trail section provides steps for creating reports designed for auditing consolidated data, ensuring thorough examination and analysis of financial information.

---

*Help Topic 0390 | Category: Reporting | Last Updated: 2024-12-03*