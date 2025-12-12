# Consolidation Reports

## Metadata
- **Index**: 0391
- **Topics**:  Comments Report, Consolidated Figures, Consolidated Flow, General Ledger
- **Keywords**:  Comments Report, Consolidated Figures, Consolidated Flow, General Ledger, Calculated Account, Adjustments, Data Analysis, Report Generation, Financial Transactions, Consolidation Summary, Entity Reports, Difference Analysis, Transfer of Reserves, Minority Report, Equity Report, Financial Transactions, Data Analysis, Report Generation
- **Theory Reference**: Elimination Reporting

## Summary

 The provided documentation for the Financial Consolidation product includes comprehensive instructions on generating various types of reports. The Comments Report section explains how to create reports with additional information or explanations on transactions. The Consolidated Figures section details generating reports on all figures converted into group currency, including closing amounts and currency conversion rates. The Consolidated Flow section provides instructions on generating comprehensive reports on total amounts in group currency for specific accounts and flows. The General Ledger section outlines the process for generating detailed reports on financial activities, including calculated accounts and adjustments, ensuring accurate financial data analysis and reporting. Also includes detailed instructions on generating various types of consolidation reports. The Consolidation Summary Reports section explains how to create concise overviews of data collected from multiple companies. The Consolidation Reports per Entity section details generating reports specific to each individual entity within the group. The Difference Analysis section provides steps for identifying and analyzing variations in financial data across periods. The Transfer of Reserves section explains how to document and include reserve transfers that impact the consolidation difference analysis. The documentation ensures accurate and comprehensive financial data reporting and analysis.

---

## User Guide

Comments report
The Comments page allows you to run reports that contain additional information or explanations on transactions.

To access the Comments report page, click Reports > Standard Reports > Comments.

The left-side panel displays the Accounts you can select to generate the report. The account information includes:
- Code
- Description
- Account Type
- Debit/Credit

Note: You can narrow down the list of accounts by filtering on Type and/or Debit/Credit, or by filtering on Account Code and/or Name.

The right-side panel displays the Companies you can select and include in the report along with their Code and Description.

Generate a comments report:
1. On the Account (left-side) panel, select an account.
2. On the Companies (right-side) panel, select a company.
3. In the Report group boxes below the panels, select options that you want to use to further specify the data you want on the report. For example, you can choose Balance Sheet and P&L, include Local Amounts, and include Debit balances only.
4. In the File type field, select the output file type. Options include PDF, XLS, and XLSX.
5. Click to generate the report. After the report is generated, a download link appears below for you to click and view it in the file type selected.

Consolidated figures report
The Consolidated Figures report presents all the figures converted into the group currency.

To access the Consolidated Figures Report page, click Reports > Standard Reports > Consolidated Figures.

Types of reports:
- Consolidated Amount report: Includes closing amounts in group currency per company.
- Currency Conversion report: Includes calculated conversion rates per company and account.
- Consolidated Amounts by dimension report: Includes dimension details for consolidated amounts per dimension group, company, and account.

Generate a consolidated figures report:
1. In the Ref Period field, enter a reference consolidation period or click to search for one. Note: By default, the Current and Reference Consolidation Periods are assigned by the application to the selected consolidation periods on top of the page. However, you can change the Reference Consolidation Period according to your need.
2. Select the type of data you want on the report.
3. From the Companies list, select the companies whose data you want to include on the report.
4. In the Journal Summation field, select an option. Consolidated Amounts can include Bundle Data, Local Adjustments, Group Adjustments (both Manual and Events), and Consolidation Adjustments, depending on the selected Journal Summation.
5. In the File type field, select the output file type. Options include PDF, XLS, and XLSX.
6. Click to generate the report. After the report is generated, a download link appears below for you to click and view it in the file type selected.

Consolidated flow report
A Consolidated Flow report provides a comprehensive overview of the total amounts in group currency for a specific account and flow. It includes the sum of all relevant amounts associated with that account and flow, considering the impact of any adjustments made.

To generate a consolidation flow report, click Reports > Standard Reports > Consolidation Flows.

The left-side panel displays the Accounts and corresponding information including:
- Code
- Description
- Account Type
- Debit/Credit

The right-side panel displays the Companies information including Code and Description.

Types of reports:
- Summary report: Includes balances and flows from Reference to Current Consolidation Period, per account.
- Contribution by Company report: A Summary Report broken further down to a contribution by Company.
- Contribution by Journal: A Summary Report broken further down to a contribution by Journal.
- Contribution by Company and Journal: A Summary Report broken further down to a contribution by Company and Journal.
- Net Variation – Summary: Balances and Net Variation flow from Reference to Current Consolidation Period, per account.
- Net Variation – by Company: A Net Variation – Summary broken further down to a contribution by Company.
- Net Variation – by Partner: Net Variation – Summary broken further down to a contribution by Partner.

Generate a consolidation flow report:
1. From the Accounts list, select the accounts. Note: You can narrow down the list of accounts by filtering on Type and/or Debit/Credit, or by filtering on Account Code and/or Name.
2. From the Companies list, select at least one company. Note: On top of this list you can use filters for Company Code and/or Name.
3. In the Report panel below, from the list on the left, select a report type.
4. In the Journal Summation drop-down, select how you want the transactions organized.
5. In the File type field, select the output file type. Options include PDF, XLS, and XLSX.
6. Click to generate the report. After the report is generated, a download link appears below for you to click and view it in the file type selected.

Consolidation adjustments report
The Consolidation Adjustments report offers a comprehensive breakdown of the adjustments made during the consolidation process of the group's accounts. This report provides detailed information about the specific adjustments applied to ensure accurate and consistent financial reporting across the group.

To access the Consolidation Adjustments report page, click Reports > Standard Reports > Consolidation Adjustments.

Types of reports:
- Summary (as an ‘index’) report: Contains only the P&L impact of the adjustments per account and per company. There will be no Debit or Credit figures.
- Detailed report: Includes the details of Debit and Credit amounts of the adjustments.
- Detailed with flows report: All the Debit/Credit details of the adjustments, as well as the flows, are included in the report.
- Detailed with dimensions report: All the Debit/Credit details of the adjustments, as well as the dimensions, are included in the report.

Create a consolidation adjustment report:
1. From the Report options, select a report type. Note: If you select either Detailed with flows or Detailed with dimension report, you can opt to display various Journal Types on separate sheets in the Excel output file, or have them separated by a page-break in the PDF output file.
2. In the Currency type field, select a type of currency — Local Currency or Group Currency.
3. In the Company field, select the company whose adjustments report you want to generate.
4. For Journal Summation, select the journal view(s) on which you want to base your report. A journal view is a summation or grouping of several journals. It is used in the reports to get information at different stages or levels in the consolidation process.
5. Select a Journal type. Options include: B - journals from the Bundle Adjustments, E - journals from the Events Adjustments, M - journals from the Manual Adjustments, T - journals from the Automatic Adjustments, L - journals from the Local Adjustments.
6. In the Journal category field, select the journal category or code you want to use to generate your report.
7. Optionally, in the Modified Date field, specify a date to include only adjustments that were modified on that date on the report.
8. In the Minority Flag field, select one of these options: After 3rd Parties (Post-minority Adjustments)- Adjustments are posted after the calculation of the minority interests. Before 3rd Parties- Adjustments are posted before the calculation of the minority interests. Both - Includes both before and after 3rd parties adjustments. Adjustments after 3rd parties have an indicator in the printout.
9. Optionally, in the Accounts field, enter an account code or click to search for one if you want only adjustments that impact the selected account to be included in the generated report.
10. Optionally, in the Partner Company field, select a partner company if you want only adjustments that impact the selected partner in the intercompany transactions to be included in the generated report.
11. Optionally, in the Flow field, enter a flow code or click to search for one if you want only adjustments that impact the selected flow to be included in the generated report.
12. You also have the options to specify the following: Minimum amount - if specified, only adjustments containing amounts up to and not lower than the specified amount will be included. Maximum amount - if specified, only adjustments containing amounts up to and not higher than the specified amount will be included.
13. In the Sorting field, specify how the adjustments on the report should be displayed. Available options are by: Company / Journal ID / Journal Number (based on the Company). Journal ID / Journal Number (based on the Journal Category). Modified Date / Journal Number (based on the Modification date).
14. In the Has attachment field, you have these options: Show All - adjustments with and without attachments are included on the report. Yes - only adjustments with attachments are included on the report. No - only adjustments that do not have attachments are included on the report.
15. In the File type field, select the output file type. Options include PDF, XLS, and XLSX.
16. Click to generate the report. After the report is generated, a download link appears below for you to click and view it in the file type selected.

Consolidation (summary) reports
The Consolidation Report (Summary) report provides a concise overview of data collected from multiple companies, presenting the outcomes in a condensed format.

To access the Consolidation Reports-Summary page, click Reports > Consolidation Reports > Consolidation Reports-Summary.

Types of reports:
- Consolidation difference report: This report includes the consolidation difference (or contribution in consolidated reserves) between one period and another.
- 3rd party interests analysis report: This report includes the interests of companies that are not in the group.
- Equity value of participations report: This report shows the equity method value analysis per company.
- Dividends (by Shareholders) report: This report shows the dividend received from each company's participation and how much has been declared paid by the participation itself.

Generate a consolidation (summary) report:
1. In the Ref Period field, if the period you want to use is different from the default one, click to select another reference consolidation period.
2. Select the type of consolidation summary report you want to generate.
3. In the File type field, select the output file type. Options include PDF, XLS, and XLSX.
4. Click to generate the report. After the report is generated, a download link appears below for you to click and view it in the file type selected.

Consolidation reports per entity
The Consolidation Reports per Entity page provides the functionality to generate consolidation reports that are grouped by entities. This means that you can generate reports that present consolidated financial information specifically for each individual entity within the group.

To access the Consolidation Reports-Entity page, click Reports > Consolidation Reports > Consolidation Reports-Entity.

Types of reports:
- Statutory in Local Currency report: Shows the statutory equity by company in the local currency of the company.
- Consolidated Equity report: Shows the consolidated equity by company.
- Shareholders report: Shows the details of the values of the shareholdings by parent companies in the selected companies.
- Consolidation Difference report: Shows the consolidation difference or contribution in consolidated reserves by company.
- Translation Adjustment Difference report: Shows the translation adjustment per company.
- 3rd Parties Analysis report: Shows the third parties analysis by company.
- Equity View Analysis report: Shows the equity value analysis by company.

Generate a consolidation report per entity:
1. In the Ref Period field, enter a reference consolidation period or click to select.
2. On the Companies list, select companies to include in the report.
3. On the Report list, select a report type.
4. In the File type field, select the output file type. Options include PDF, XLS, and XLSX.
5. Click to generate the report. After the report is generated, a download link appears below for you to click and view it in the file type selected.

Consolidation difference analysis summary report
The Consolidation Summary Equity Elimination Accounts page allows you to define and generate a report showing the differences or variations that arise when combining the financial data of the parent company and its subsidiaries, based on the accounts selected. These differences can occur due to several factors including intercompany transactions and consolidation adjustments.

To access the Consolidation Difference Analysis Summary report page, click Reports > Consolidation Reports > Consolidation Reports-Summary.

Generate a consolidation difference analysis summary report:
1. From the list of accounts displayed, select the accounts you want on your report.
2. Click to return to the Consolidation Reports-Summary page.
3. Click to generate the report. After the report is generated, a download link appears below for you to click and view it in the file type selected.

Minority or equity report
The Minority or Equity report assists you in configuring the columns within the 3rd Parties Interest Analysis report where each flow of the specific account will be displayed. This allows for the presentation of the evolution of the 3rd Parties Interest / Minority account per company, based on the different types of changes between the Last Period and This Period amounts.

To access the Minority Report page, on the Reports > Consolidation Reports > Consolidation Reports-Summary page, select the 3rd Parties interests option and click Define report.

Define a minority report:
1. On the Consolidation Report- Summary page, select the 3rd Parties interests option.
2. Click .
3. On the Minority Report page, for each flow type you want on the report, from the Column number drop-down, select a change type.
4. Click .
5. Click to return to the Consolidation Report- Summary page.
6. Ensure that the 3rd Parties interests option is still selected.
7. Click to generate the report. After the report is generated, a download link appears below for you to click and view it in the file type selected.

Define an equity report:
1. On the Consolidation Report - Summary page, select the Equity value of participations option.
2. Click .
3. On the Equity Report page, for each flow type you want on the report, from the Column number drop-down, select a change type.
4. Click .
5. Click to return to the Consolidation Report- Summary page.
6. Ensure that the Equity value of participations option is still selected.
7. Click to generate the report. After the report is generated, a download link appears below for you to click and view it in the file type selected.

Transfer of reserves
The Transfer of Reserves page allows you to include information about undisclosed transactions within the group. It provides an avenue for entering reserve transfers between companies that are not directly recorded in the local books but have an impact on the consolidation difference analysis report. By considering these additional data in addition to the consolidation data, the consolidation difference analysis reports can accurately reflect an evolution where the difference equals zero, ensuring a fully justified and balanced outcome.

To access the Transfer of Reserves page, click Reports > Consolidation Reports > Consolidation Reports-Summary and then click the button.

Post transfer of reserves:
1. In the Line Nr field, enter the line on which you want the transfer of reserve to appear.
2. From the Transfer type drop-down, select a type.
3. In the Amount field, enter the transaction amount.
4. In the Description field, enter a description for the transfer of reserve.
5. In the From and To Company fields, select the applicable companies. You can use to search for the companies.
6. Click .
7. To generate a report of the transfer of reserves, in the Report options select an output type.
8. Click to generate the report. After the report is generated, a download link appears below for you to click and view it in the file type selected.

---

## Frequently Asked Questions

### Concepts

**What does the Comments report page allow you to do?**
The Comments report page allows you to run reports that contain additional information or explanations on transactions.

**What does the Consolidated Figures report present?**
The Consolidated Figures report presents all the figures converted into the group currency.

**What does the Consolidated Amount report include?**
The Consolidated Amount report includes closing amounts in group currency per company.

**What does a Consolidated Flow report provide?**
A Consolidated Flow report provides a comprehensive overview of the total amounts in group currency for a specific account and flow.

**What is the purpose of the Journal Summation drop-down in the Consolidated Flow report?**
The Journal Summation drop-down is used to select how transactions are organized in the report.

**What does the Detailed report in the Consolidation Adjustments report include?**
The Detailed report includes the Debit and Credit amounts of the adjustments.

**What is the Has attachment field used for in the Consolidation Adjustments report?**
The Has attachment field specifies whether to include adjustments with attachments, without attachments, or both.

**What does the Consolidation Report (Summary) provide?**
The Consolidation Report (Summary) provides a concise overview of data collected from multiple companies, presenting the outcomes in a condensed format.

**What is the purpose of the Equity value of participations report?**
The Equity value of participations report shows the equity method value analysis per company.

**What does the Dividends (by Shareholders) report display?**
The Dividends (by Shareholders) report shows the dividend received from each company's participation and how much has been declared paid by the participation itself.

**What does the Consolidated Equity report display?**
The Consolidated Equity report shows the consolidated equity by company.

**What does the Consolidation Difference report include?**
The Consolidation Difference report includes the consolidation difference or contribution in consolidated reserves by company.

**What is shown in the Translation Adjustment Difference report?**
The Translation Adjustment Difference report shows the translation adjustment per company.

**What does the Equity View Analysis report show?**
The Equity View Analysis report shows the equity value analysis by company.

**What is the purpose of the Consolidation Summary Equity Elimination Accounts page?**
The purpose of the Consolidation Summary Equity Elimination Accounts page is to define and generate a report showing the differences or variations that arise when combining the financial data of the parent company and its subsidiaries, based on the accounts selected.

**What does the Minority or Equity report help you configure?**
The Minority or Equity report assists in configuring the columns within the 3rd Parties Interest Analysis report where each flow of the specific account will be displayed.

**What is the purpose of the Transfer of Reserves page?**
The Transfer of Reserves page allows you to include information about undisclosed transactions within the group, providing an avenue for entering reserve transfers between companies that impact the consolidation difference analysis report.

**What does the Consolidation Summary report provide?**
The Consolidation Summary report provides a concise overview of data collected from multiple companies, presenting the outcomes in a condensed format.

**What is included in the Consolidated Figures report?**
The Consolidated Figures report includes all figures converted into the group currency, such as closing amounts and currency conversion rates.

**What is the purpose of the Comments report page?**
The Comments report page allows you to run reports that contain additional information or explanations on transactions.

**What does the Currency Conversion report include?**
The Currency Conversion report includes calculated conversion rates per company and account.

**What does the Consolidated Amounts by dimension report include?**
The Consolidated Amounts by dimension report includes dimension details for consolidated amounts per dimension group, company, and account.

**What is the Journal Summation field used for in the Consolidated Figures report?**
The Journal Summation field is used to select options for including Bundle Data, Local Adjustments, Group Adjustments, and Consolidation Adjustments.

**What does the Summary report in the Consolidated Flow report include?**
The Summary report includes balances and flows from the Reference to Current Consolidation Period, per account.

**What does the Contribution by Company report include?**
The Contribution by Company report is a Summary Report broken down further to show contributions by each company.

**What does the Contribution by Journal report include?**
The Contribution by Journal report is a Summary Report broken down further to show contributions by each journal.

**What does the Contribution by Company and Journal report include?**
The Contribution by Company and Journal report is a Summary Report broken down further to show contributions by each company and journal.

**What does the Net Variation – Summary report include?**
The Net Variation – Summary report includes balances and net variation flow from the Reference to Current Consolidation Period, per account.

**What does the Net Variation – by Company report include?**
The Net Variation – by Company report is a Net Variation – Summary broken down further to show contributions by each company.

**What does the Net Variation – by Partner report include?**
The Net Variation – by Partner report is a Net Variation – Summary broken down further to show contributions by each partner.

**What is the Journal Summation drop-down used for in the Consolidated Flow report?**
The Journal Summation drop-down is used to select how you want the transactions organized in the report.

**What is the purpose of the Comments report?**
The Comments report provides additional information or explanations on transactions.

**What is included in the Consolidated Amount report?**
The Consolidated Amount report includes closing amounts in group currency per company.

**What is the Summary report in the Consolidated Flow report?**
The Summary report includes balances and flows from the Reference to Current Consolidation Period, per account.

**What does the Contribution by Journal report show?**
The Contribution by Journal report shows a breakdown of contributions by each journal.

**What is included in the Contribution by Company and Journal report?**
The Contribution by Company and Journal report includes contributions broken down by both company and journal.

**What is the Net Variation – by Company report?**
The Net Variation – by Company report provides a breakdown of contributions by each company.

**What is included in the Detailed with flows report in the Consolidation Adjustments report?**
The Detailed with flows report includes Debit/Credit details and flows of the adjustments.

**What does the Detailed with dimensions report in the Consolidation Adjustments report include?**
The Detailed with dimensions report includes Debit/Credit details and dimensions of the adjustments.

**What does the 3rd party interests analysis report show?**
The 3rd party interests analysis report shows the interests of companies that are not in the group.

**What does the Consolidation Reports per Entity page provide?**
The Consolidation Reports per Entity page provides the functionality to generate consolidation reports that are grouped by entities, presenting consolidated financial information specifically for each individual entity within the group.

**What does the 3rd Parties Analysis report display?**
The 3rd Parties Analysis report shows the third parties analysis by company.

**What is the purpose of the Consolidation Reports per Entity page?**
The purpose of the Consolidation Reports per Entity page is to provide the functionality to generate consolidation reports that are grouped by entities.

**What does the Statutory in Local Currency report show?**
The Statutory in Local Currency report shows the statutory equity by company in the local currency of the company.

**What does the Shareholders report include?**
The Shareholders report includes the details of the values of the shareholdings by parent companies in the selected companies.

**What is included in the Consolidation Difference report?**
The Consolidation Difference report includes the consolidation difference or contribution in consolidated reserves by company.

**What does the Consolidation Summary Equity Elimination Accounts page provide?**
The Consolidation Summary Equity Elimination Accounts page provides a way to define and generate a report showing the differences or variations that arise when combining the financial data of the parent company and its subsidiaries.

**What does the Minority or Equity report assist in configuring?**
The Minority or Equity report assists in configuring the columns within the 3rd Parties Interest Analysis report where each flow of the specific account will be displayed.

**What is the Transfer of Reserves page used for?**
The Transfer of Reserves page is used to include information about undisclosed transactions within the group, providing an avenue for entering reserve transfers between companies that impact the consolidation difference analysis report.

### General

**What information is displayed in the left-side panel on the Comments report page?**
The left-side panel displays the Accounts you can select to generate the report, including their Code, Description, Account Type, and Debit/Credit.

**How can you narrow down the list of accounts on the Comments report page?**
You can narrow down the list of accounts by filtering on Type, Debit/Credit, Account Code, or Name.

**What types of reports are included in the Consolidated Figures report?**
The types of reports include the Consolidated Amount report, Currency Conversion report, and Consolidated Amounts by dimension report.

**What information is included in the Currency Conversion report?**
The Currency Conversion report includes calculated conversion rates per company and account.

**What details are provided in the Consolidated Amounts by dimension report?**
The Consolidated Amounts by dimension report includes dimension details for consolidated amounts per dimension group, company, and account.

**What types of reports are available in the Consolidated Flow report?**
Types of reports include Summary report, Contribution by Company report, Contribution by Journal report, Contribution by Company and Journal report, Net Variation – Summary, Net Variation – by Company, and Net Variation – by Partner.

**What information is included in the Detailed with flows report in the Consolidation Adjustments report?**
The Detailed with flows report includes all the Debit/Credit details of the adjustments as well as the flows.

**What information does the Detailed with dimensions report in the Consolidation Adjustments report include?**
The Detailed with dimensions report includes all the Debit/Credit details of the adjustments as well as the dimensions.

**What options are available in the Currency type field for the Consolidation Adjustments report?**
Options include Local Currency and Group Currency.

**What are the available Journal types in the Consolidation Adjustments report?**
Journal types include B - Bundle Adjustments, E - Events Adjustments, M - Manual Adjustments, T - Automatic Adjustments, and L - Local Adjustments.

**What options are available in the Minority Flag field for the Consolidation Adjustments report?**
Options include After 3rd Parties, Before 3rd Parties, and Both.

**What options are available in the File type field for generating reports?**
Options include PDF, XLS, and XLSX.

**What information can you specify when generating a comments report?**
You can specify options such as Balance Sheet and P&L, including Local Amounts, and including Debit balances only.

**What information does the Currency Conversion report include?**
The Currency Conversion report includes calculated conversion rates per company and account.

**What information is included in the Detailed with dimensions report in the Consolidation Adjustments report?**
The Detailed with dimensions report includes all the Debit/Credit details of the adjustments as well as the dimensions.

**What options can you select in the Currency type field for the Consolidation Adjustments report?**
Options include Local Currency and Group Currency.

**What information does the Consolidation difference report include?**
The Consolidation difference report includes the consolidation difference (or contribution in consolidated reserves) between one period and another.

**What details are shown in the 3rd party interests analysis report?**
The 3rd party interests analysis report shows the interests of companies that are not in the group.

**What functionality does the Consolidation Reports per Entity page provide?**
The Consolidation Reports per Entity page provides the functionality to generate consolidation reports that are grouped by entities, presenting consolidated financial information specifically for each individual entity within the group.

**What information is included in the Statutory in Local Currency report?**
The Statutory in Local Currency report shows the statutory equity by company in the local currency of the company.

**What details are provided in the Shareholders report?**
The Shareholders report shows the details of the values of the shareholdings by parent companies in the selected companies.

**What information does the 3rd Parties Analysis report display?**
The 3rd Parties Analysis report shows the third parties analysis by company.

**What information can you filter on the Comments report page?**
You can filter accounts by Type, Debit/Credit, Account Code, and Name on the Comments report page.

**What types of reports are available in the Consolidated Figures report?**
Types of reports include Consolidated Amount report, Currency Conversion report, and Consolidated Amounts by dimension report.

**What information does the Consolidation Adjustments report provide?**
The Consolidation Adjustments report offers a detailed breakdown of adjustments made during the consolidation process, including Debit and Credit amounts and any associated flows and dimensions.

**What types of reports are available in the Consolidation Adjustments report?**
Types of reports include Summary report, Detailed report, Detailed with flows report, and Detailed with dimensions report.

**What options can you select when generating a comments report?**
Options include selecting Balance Sheet and P&L, including Local Amounts, and including Debit balances only.

**What information does the Detailed report in the Consolidation Adjustments report include?**
The Detailed report includes the details of Debit and Credit amounts of the adjustments.

**What information does the Detailed with flows report in the Consolidation Adjustments report include?**
The Detailed with flows report includes all the Debit/Credit details of the adjustments as well as the flows.

**What information does the Consolidated Amounts by dimension report include?**
The Consolidated Amounts by dimension report includes dimension details for consolidated amounts per dimension group, company, and account.

**What information does the Contribution by Company report provide?**
The Contribution by Company report provides a breakdown of contributions by each company.

**What types of reports are included in the Consolidation Report (Summary)?**
The types of reports included are the Consolidation difference report, 3rd party interests analysis report, Equity value of participations report, and Dividends (by Shareholders) report.

**What information does the Consolidation difference report provide?**
The Consolidation difference report includes the consolidation difference (or contribution in consolidated reserves) between one period and another.

**What details are included in the Equity value of participations report?**
The Equity value of participations report shows the equity method value analysis per company.

**What information does the Statutory in Local Currency report show?**
The Statutory in Local Currency report shows the statutory equity by company in the local currency of the company.

**What information is provided in the Shareholders report?**
The Shareholders report shows the details of the values of the shareholdings by parent companies in the selected companies.

**What information is included in the Equity View Analysis report?**
The Equity View Analysis report shows the equity value analysis by company.

**What types of data can cause differences in the Consolidation Summary Equity Elimination Accounts report?**
Differences can occur due to intercompany transactions and consolidation adjustments.

**What information is included in the Dividends (by Shareholders) report?**
The Dividends (by Shareholders) report includes details of dividends received from each company's participation and the amount declared paid by the participation itself.

**What information does the Consolidated Equity report display?**
The Consolidated Equity report displays the consolidated equity by company.

### How-To

**How do you generate a Consolidated Figures report?**
To generate a Consolidated Figures report, select a reference consolidation period, choose the type of data, select companies, choose a journal summation option, select the file type, and click to generate the report.

**How do you generate a Consolidated Flow report?**
To generate a Consolidated Flow report, select accounts, companies, a report type, a journal summation option, the file type, and click to generate the report.

**How do you generate a comments report?**
To generate a comments report, select an account from the left-side panel, a company from the right-side panel, specify additional report options, choose the file type, and click to generate the report.

**How do you generate a consolidation summary report?**
To generate a consolidation summary report, select a reference consolidation period, choose the type of report, select the file type, and click to generate the report.

**How do you generate a consolidation report per entity?**
To generate a consolidation report per entity, select a reference consolidation period, choose companies, select a report type, choose the file type, and click to generate the report.

**How do you generate a consolidation difference analysis summary report?**
To generate a consolidation difference analysis summary report, select the accounts you want on your report, click to return to the Consolidation Reports-Summary page, and then click to generate the report.

**How do you define a minority report?**
To define a minority report, select the 3rd Parties interests option, click to configure columns for each flow type, and then click to generate the report.

**How do you define an equity report?**
To define an equity report, select the Equity value of participations option, click to configure columns for each flow type, and then click to generate the report.

**How do you post a transfer of reserves?**
To post a transfer of reserves, enter the line number, select a transfer type, enter the amount and description, select the applicable companies, and click to confirm.

**How do you generate a report of the transfer of reserves?**
To generate a report of the transfer of reserves, select the report options, choose the output file type, and click to generate the report.

**How do you create a Consolidation Adjustments report?**
To create a Consolidation Adjustments report, select a report type, currency type, company, journal summation, journal type, journal category, optional parameters, sorting, attachment options, file type, and click to generate the report.

**How do you narrow down the list of accounts on the Comments report page?**
You can narrow down the list of accounts by filtering on Type, Debit/Credit, Account Code, or Name.

**How do you select the reference consolidation period for a Consolidated Figures report?**
Enter a reference consolidation period in the Ref Period field or search for one.

**How do you include undisclosed transactions within the group in the Transfer of Reserves page?**
To include undisclosed transactions within the group, enter the reserve transfer details on the Transfer of Reserves page.

### Navigation

**How do you access the Consolidation Reports-Summary page?**
To access the Consolidation Reports-Summary page, click Reports > Consolidation Reports > Consolidation Reports-Summary.

**How do you access the Consolidation Reports-Entity page?**
To access the Consolidation Reports-Entity page, click Reports > Consolidation Reports > Consolidation Reports-Entity.

**How do you access the Minority Report page?**
To access the Minority Report page, on the Reports > Consolidation Reports > Consolidation Reports-Summary page, select the 3rd Parties interests option and click Define report.

**How do you access the Transfer of Reserves page?**
To access the Transfer of Reserves page, click Reports > Consolidation Reports > Consolidation Reports-Summary and then click the button.

---

*Help Topic 0391 | Category: Reporting | Last Updated: 2024-12-03*