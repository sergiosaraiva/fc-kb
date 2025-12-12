# Local amounts

## Metadata
- **Index**: 0309
- **Topics**:  Financial Consolidation Data Entry, Intercompany Management, Local Amounts Management, Report Generation
- **Keywords**:  Financial Consolidation, Intercompany Management, Local Amounts, Bundle Reports, Data Entry, Adjustments

## Summary

 The documents provide detailed guidance on managing various aspects of Financial Consolidation, including entering and verifying data for local amounts, intercompany transactions, and generating bundle reports. They cover accessing specific pages, selecting input forms, entering data, reviewing adjusted amounts, and generating reports. Terminology has been standardized, and detailed instructions from images have been incorporated into the text.

---

## User Guide

Local Amounts - Input Form Selection
This Local Amounts entry page is used for selecting the input form or template needed to enter local amounts (statutory figures). The local amounts are entered on the Bundle Data Entry - Standard page or in an Advanced input page displayed after selecting the parameters on this page.

To access the Local Amounts entry page, click Data Entry > Manual Data Entry > Local Amounts.

Company - drop-down list of companies available to work on.

InputForm - drop-down list of available forms for data entry.

Note: The input form selected determines the options displayed in the Option field.

To enter local amounts, select one of the following:
Balance Sheet Input
Balance Sheet
Profit and Loss

Option - drop-down list of layout options for data entry in the Bundle Data Entry - Standard page. Available after clicking Select.

Note: The options available in this field are determined by the input form selected.

These options include:
Local Amounts - allows entering the local amounts including the Reference and the Current amounts, and the difference between both.

Note: This is the only option that allows data entry. The other options present data for view only.

Local Adjustments - shows the impact of the Local Adjustments including the Reference and the Current amounts, and the difference between both.

Adjusted Bundles - shows the local amounts, corrected with the local adjustments including the Reference and the Current amounts, and the difference between both.

Local + Adjustments N - shows the local amounts, the local adjustments, and the local adjusted amounts. Only the Current amount is displayed.

Local + Adjustments N-1 - shows the local amounts, the local adjustments, and the local adjusted amounts. Only the Reference amount is displayed.

Select - does the following:
if the Option selected is one of Local Amounts, Bundles, or Adjustments, opens the Bundle Data Entry - Standard page to enter the local amounts.
if the Option selected is Advanced input form, opens the BundleSpread page.

Start Data Entry in Local Amounts:
1. In the InputForm field, select an input form.
2. Select a company.
3. In the Option field, select Local Amounts.
4. Click Select. The Bundle Data Entry - Standard page is displayed for entering the local amount details.

Review Adjusted Amounts:
1. Select an input form.
2. Select a company.
3. Select Adjusted Bundles from the Option field.
4. Click Select. The adjusted amounts for both the current and reference periods are displayed for review.

View the impact of the local adjustments on the bundle amounts for the current consolidation:
1. Select an input form.
2. Select a company.
3. Select Adjusted Bundles from the Option field.
4. Click Select. The Bundle Data Entry - Standard page is displayed to view the impact.

Local Amounts - Manual Data Entry
The Bundle Data Entry - Standard page is used for entering local amounts in the input form selected on the Local Amounts page. It displays the list of accounts added to the Standard form for the selected company and available in the database. The page can show data if it was already filled in or imported, or it can show zeroes if there is no data available for the selected company and included accounts.

The input form pages typically display the reference period in read-only mode (presenting data from the opening period, typically the last month of the previous accounting year), and data for the selected working or current period in read/write mode (if the period is not locked), and the difference between both columns.

The top part of the page displays the following parameters selected on the Local Amounts page:
Company - information about the company. It shows the code, the name, and the local currency of the company.
Option - layout option selected for the form.
Currency - code for the currency in use.
InputForm - code and the name of the input form.

Below are the following:
See all lines - a drop-down list of filter options to display data in different ways.
Zero - replaces all selected values with zero. This button works only in combination with the checkboxes in the first column. It allows setting to zero one or more (or all) accounts within the form.
Copy - works only in combination with the checkboxes in the first column. It copies the selected amounts of the reference consolidation period into the current consolidation period. It allows copying one or more (or all) accounts within the form.

Note: While there is NO warning after clicking this button, it is necessary to confirm the modification by clicking the Update button.

Balance - opens a pop-up window showing the total debit and credit for the Balance Sheet, the Profit and Loss, and the Contingencies accounts, as well as the result of the year in the Balance Sheet and the Profit and Loss.
Print - allows printing the information on the page.
Grid - a toggle that adds Excel-like grid lines to the displayed data on the page when selected.

The data area contains the accounts available on the Input Form:
The first column contains checkboxes that allow selecting a row and later performing an action on it. To select all rows, select the checkbox in the header of the data area.

Code - account code.
Description - account description.
Reference - amount from the reference period.
Current - amount from the current period.
Difference - calculated difference between the reference amount displayed and the current amount entered.

Click any of the following icons to perform the associated actions:
Intercompany - opens a page to enter intercompany transactions, where applicable.
Import - shows imported data details.
Financial Flow - opens a page to enter the Financial Flow data. The flow button only appears for accounts defined to work with flows.
Participation - opens a page to enter participation information.
Partner - opens a page for entering partner information. This button appears only for accounts defined to work with partner information.
Dimension - opens a page to enter dimension information. This button appears only for accounts defined to work with dimension information.

Note: For any of the above, where there are differences to justify, the icon is highlighted with a yellow background. For example, this means there are outstanding differences waiting to be justified in the dimension.

Save - saves the modifications made to the amounts. When changing the contents of a field, this button will become red, and all affected totals will get borders around them.

Note: There is NO warning after clicking this button, but it is necessary to confirm the operation by clicking the Update button.

Reverse - reverses all modifications since the last save. A message will ask to confirm the cancellation of the modifications.

Use Filters to Display Data:
When first accessing this page, the default option is to See all lines. However, several options can filter and display data on this page.

In the filter box right above the table on the left side of the page, the following options are available:
Select one of the options to display data accordingly.

Change an Amount:
Note: Amounts can only be changed when the form is accessed with the Local Amounts option selected.
1. Place the cursor on the amount to be changed.
2. Change the amount. A border appears around all the subtotal and total amounts impacted by the change.
3. Click Save to save the changes.

Enter Partner Detail:
The Partner button appears on accounts defined to work with partner information such as intercompany accounts, participation accounts, or partner accounts. Click Partner to open the page and enter the partner company details.

Enter Financial Flow Data:
The Financial Flow button is available on the page if the account whose data is to be entered is defined to have flows (i.e., Balance Sheet accounts). Click Financial Flow to open the page and enter the flow data. Flow data can be Cash (C) and Non-Cash (NC).

Copy Data from the Reference Consolidation Period:
1. Do one of the following:
To copy all the lines, select the checkbox at the top left of the data area. All lines from the report will be selected.
To copy a line or a few lines, select only one or a few lines.
2. Click Copy to transfer the amounts from the reference to the current period. All totals and subtotals of the selected lines will get borders around them.
3. Click Update to confirm the update of the amounts.

Bundle Last Modified Report
The Bundle Last Modified page allows creating a report of recently modified bundles.

To access the Bundle Last Modified page, click Reports > Standard Reports > Bundle Last Modified.

Generate a Bundle Last Modified Report:
Note: By default, the Current and Reference Consolidation Periods are assigned by the application. However, either can be changed by clicking to look for the desired period.
1. In the Period field, click to search for and select the current consolidation period.
2. In the Ref Period field, click to search for and select a reference consolidation period.
3. In the File type field, select the output file type. Options include PDF, XLS, and XLSX.
4. Click Generate Report to generate the report. After the report is generated, a download link appears below for viewing it in the selected file type.

---

## Frequently Asked Questions

### Concepts

**What is the purpose of the Local Amounts entry page in financial consolidation?**
The Local Amounts entry page is used for selecting the input form or template needed to enter local amounts (statutory figures). The local amounts are entered on the Bundle Data Entry - Standard page or in an Advanced input page displayed after selecting the parameters on this page.

**What is displayed in the top part of the Bundle Data Entry - Standard page?**
The top part of the Bundle Data Entry - Standard page displays the following parameters selected on the Local Amounts page: Company, Option, Currency, and InputForm.

**What is the function of the Zero button on the Bundle Data Entry - Standard page?**
The Zero button replaces all selected values with zero. It works only in combination with the checkboxes in the first column, allowing you to set to zero one or more (or all) accounts within the form.

**What does the Balance button do on the Bundle Data Entry - Standard page?**
The Balance button opens a pop-up window showing the total debit and credit for the Balance Sheet, Profit and Loss, and Contingencies accounts, as well as the result of the year in the Balance Sheet and Profit and Loss.

**What does the Save button do on the Bundle Data Entry - Standard page?**
The Save button saves the modifications made to the amounts. When you change the contents of a field, this button will become red, and all affected totals will get borders around them.

**What is the purpose of the Bundle Last Modified page?**
The Bundle Last Modified page allows you to create a report of recently modified bundles.

**What does the Local Adjustments option show on the Local Amounts page?**
The Local Adjustments option shows the impact of the Local Adjustments, including the Reference and the Current amounts, and the difference between both.

**What does the Adjusted Bundles option show on the Local Amounts page?**
The Adjusted Bundles option shows the local amounts corrected with the local adjustments, including the Reference and the Current amounts, and the difference between both.

**What does the Financial Flow button do on the Bundle Data Entry - Standard page?**
The Financial Flow button opens a page to enter the Financial Flow data. The button only appears for accounts defined to work with flows.

**What does the Dimension button do on the Bundle Data Entry - Standard page?**
The Dimension button opens a page to enter dimension information. This button only appears for accounts defined to work with dimension information.

**What does the Grid button do on the Bundle Data Entry - Standard page?**
The Grid button is a toggle that adds Excel-like grid lines to the displayed data on the page when selected.

**What is the function of the Partner button on the Bundle Data Entry - Standard page?**
The Partner button opens a page to enter the partner company details. This button appears on accounts defined to work with partner information such as intercompany accounts, participation accounts, or partner accounts.

**What does the Zero button on the Bundle Data Entry - Standard page do?**
The Zero button replaces all selected values with zero. It works only in combination with the checkboxes in the first column, allowing you to set to zero one or more (or all) accounts within the form.

**What is the purpose of the Local Amounts entry page?**
The Local Amounts entry page is used for selecting the input form or template needed to enter local amounts (statutory figures). These amounts are entered on the Bundle Data Entry - Standard page or in an Advanced input page after selecting parameters.

**What does the Financial Flow button on the Bundle Data Entry - Standard page do?**
The Financial Flow button opens a page for entering flow data. It only appears for accounts defined to work with flows.

**What does the Copy button on the Bundle Data Entry - Standard page do?**
The Copy button transfers the amounts from the reference to the current period. It works only in combination with the checkboxes in the first column, allowing copying one or more (or all) accounts within the form.

**What is the purpose of the Balance button on the Bundle Data Entry - Standard page?**
The Balance button opens a pop-up window showing the total debit and credit for the Balance Sheet, Profit and Loss, and Contingencies accounts, as well as the result of the year in the Balance Sheet and Profit and Loss.

**What does the Save button on the Bundle Data Entry - Standard page do?**
The Save button saves the modifications made to the amounts. It becomes red when changes are made, and all affected totals get borders around them.

**What does the Copy button do on the Bundle Data Entry - Standard page?**
The Copy button transfers the amounts from the reference to the current period. It works only in combination with the checkboxes in the first column, allowing copying one or more (or all) accounts within the form.

**What is displayed in the data area of the Bundle Data Entry - Standard page?**
The data area of the Bundle Data Entry - Standard page contains the accounts available on the Input Form, including the account code, account description, amount from the reference period, amount from the current period, and the calculated difference between the reference amount and the current amount.

**What does the Zero button do on the Bundle Data Entry - Standard page?**
The Zero button replaces all selected values with zero. It works only in combination with the checkboxes in the first column, allowing you to set to zero one or more (or all) accounts within the form.

**What is the purpose of the Partner button on the Bundle Data Entry - Standard page?**
The Partner button opens a page to enter the partner company details. This button appears on accounts defined to work with partner information such as intercompany accounts, participation accounts, or partner accounts.

**What does the Grid button on the Bundle Data Entry - Standard page do?**
The Grid button is a toggle that adds Excel-like grid lines to the displayed data on the page when selected.

**What does the Partner button on the Bundle Data Entry - Standard page do?**
The Partner button opens a page to enter the partner company details. This button appears on accounts defined to work with partner information such as intercompany accounts, participation accounts, or partner accounts.

### Navigation

**How do you access the Local Amounts entry page?**
To access the Local Amounts entry page, click Data Entry > Manual Data Entry > Local Amounts.

**How do you access the Bundle Last Modified page?**
To access the Bundle Last Modified page, click Reports > Standard Reports > Bundle Last Modified.

**How do you access the Local Amounts entry page in financial consolidation?**
To access the Local Amounts entry page, click Data Entry > Manual Data Entry > Local Amounts.

### General

**What options are available in the Option field when entering local amounts?**
The options available in the Option field are determined by the selected input form and include Local Amounts, Local Adjustments, Adjusted Bundles, Local + Adjustments N, and Local + Adjustments N-1.

**What information does the Company parameter show on the Bundle Data Entry - Standard page?**
The Company parameter shows information about the company, including the code, name, and local currency.

**How can you filter and display data on the Bundle Data Entry - Standard page?**
To filter and display data on the Bundle Data Entry - Standard page, use the filter box right above the table on the left side of the page. Several options are available to display data accordingly.

**What information is displayed in the data area of the Bundle Data Entry - Standard page?**
The data area of the Bundle Data Entry - Standard page contains the accounts available on the Input Form, including the account code, account description, amount from the reference period, amount from the current period, and the calculated difference between the reference amount and the current amount.

**What information is provided by the Company parameter on the Bundle Data Entry - Standard page?**
The Company parameter provides information about the company, including the code, name, and local currency.

**What options can you choose from in the Option field on the Local Amounts page?**
In the Option field, you can choose from options such as Local Amounts, Local Adjustments, Adjusted Bundles, Local + Adjustments N, and Local + Adjustments N-1, based on the selected input form.

**What are the options in the Option field on the Local Amounts page?**
The options in the Option field include Local Amounts, Local Adjustments, Adjusted Bundles, Local + Adjustments N, and Local + Adjustments N-1, which are determined by the selected input form.

**How can you filter data on the Bundle Data Entry - Standard page?**
To filter data on the Bundle Data Entry - Standard page, use the filter box right above the table on the left side of the page. Several options are available to display data accordingly.

**What information does the Currency parameter show on the Bundle Data Entry - Standard page?**
The Currency parameter shows the code for the currency in use.

**What options are available in the Option field on the Local Amounts page?**
The options available in the Option field are determined by the selected input form and include Local Amounts, Local Adjustments, Adjusted Bundles, Local + Adjustments N, and Local + Adjustments N-1.

### How-To

**How do you start data entry in local amounts?**
To start data entry in local amounts: 1. In the InputForm field, select an input form. 2. Select a company. 3. In the Option field, select Local Amounts. 4. Click Select. The Bundle Data Entry - Standard page is displayed for entering the local amount details.

**How do you generate a Bundle Last Modified report?**
To generate a Bundle Last Modified report: 1. In the Period field, click to search for and select the current consolidation period. 2. In the Ref Period field, click to search for and select a reference consolidation period. 3. In the File type field, select the output file type (PDF, XLS, XLSX). 4. Click Generate Report.

**How do you view the impact of local adjustments on bundle amounts for the current consolidation?**
To view the impact of local adjustments on bundle amounts for the current consolidation: 1. Select an input form. 2. Select a company. 3. Select Adjusted Bundles from the Option field. 4. Click Select. The Bundle Data Entry - Standard page is displayed to view the impact.

**How do you copy data from the reference consolidation period?**
To copy data from the reference consolidation period: 1. Select the checkbox at the top left of the data area to copy all lines or select specific lines. 2. Click Copy to transfer the amounts from reference to current period. 3. Click Update to confirm the update of the amounts.

**How do you change an amount on the Bundle Data Entry - Standard page?**
To change an amount on the Bundle Data Entry - Standard page: 1. Place the cursor on the amount to be changed. 2. Change the amount. A border will appear around all the subtotal and total amounts impacted by this change. 3. Click Save to save the changes.

**How do you view adjusted amounts for both current and reference periods?**
To view adjusted amounts for both current and reference periods: 1. Select an input form. 2. Select a company. 3. Select Adjusted Bundles from the Option field. 4. Click Select to display the adjusted amounts.

**How do you save modifications made to amounts on the Bundle Data Entry - Standard page?**
To save modifications made to amounts: 1. Change the contents of a field. 2. Click the Save button, which will become red, and all affected totals will get borders around them. 3. Confirm the operation by clicking the Update button.

**How do you enter partner details on the Bundle Data Entry - Standard page?**
To enter partner details on the Bundle Data Entry - Standard page, click the Partner button, which appears on accounts defined to work with partner information such as intercompany accounts, participation accounts, or partner accounts.

**How do you filter data on the Bundle Data Entry - Standard page?**
To filter data on the Bundle Data Entry - Standard page, use the filter box right above the table on the left side of the page. Several options are available to display data accordingly.

---

*Help Topic 0309 | Category: Setup | Last Updated: 2024-12-03*