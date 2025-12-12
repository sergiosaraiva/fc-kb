# User Reports

## Metadata
- **Index**: 0392
- **Topics**:  Cash-Flow Report Creation, Flow Report Creation, Multi-Period Report Creation, Standard Report Creation
- **Keywords**:  Cash-Flow Report, Flow Report, Multi-Period Report, Standard Report, User Reports, Report Generation, Financial Data, Data Analysis

## Summary

 The provided documentation for the Financial Consolidation product includes detailed instructions on creating various types of reports. The Cash-Flow Report Creation section explains how to define and generate reports for cash flow statements. The Flow Report Creation section details the process of creating reports based on flow structures across different periods, journals, and accounts. The Multi-Period Report Creation section provides steps for generating reports that span multiple periods, allowing comprehensive financial analysis over time. The Standard Report Creation section outlines the creation of linear reports based on account structures. These instructions ensure accurate and efficient financial reporting and analysis.

---

## User Guide

Create a cash-flow report
The User Report Definition - Cash Flow page allows you to create a linear report for the cash flow statement, using the Account and Calculated Account structure, the Flow structure, and the Journal structure. These structures enable you to organize and categorize the different types of financial activities related to cash flow.

The User Report Definition - Cash Flow page is accessed from the page when you select a Cash Flow type report and then, click the Define this report button.

On this page, you will see the following layout for each line:
- Line Number: each line of the report has a Line Number that allows you to identify it in the report.
- Group Number: the Group of the selected lines in the report.
- Type: displays one of the following Line Types: T - Text Line, C - Cash-Flow Line, S - Summation data, P - Page Break.
- Description: the description of the line: T - Text, C - Cash-Flow Combination, S - Summation.
- Account: code of the Account or Summation Account being used.
- Flow: code of Flow or Summation Flows being used.
- Journal: applicable Journal or Journal View.
- Sign: shows the amount presented as negative or positive.
- Period: amounts from the Current C or Reference R Consolidation Period.
- Visible: option to show or hide the line on the report.

Parameters for adding a new line:
1. Click . A Details pop-up appears for you to enter the required information for the line.
2. Enter the line number where you want the new line to appear.
3. Select a Line Type used in a Cash-Flow User Report.
4. Enter a Group Number to regroup the lines from the Cash-Flow User Report.
5. Enter a description for the line.
6. Adjust Indentation, Font, and Layout as needed.
7. Change the Sign if necessary.
8. Select where the amounts come from, either the Current or Reference Consolidation Period.
9. Select either Account or Calculated Account Code.
10. Select either the Flow or Calculated Flow Code.
11. Select either the Journal or Journal View Code.
12. Decide whether to show or hide the line on the report.
13. Click .
14. Click to return to the Define User Reports page and click to view the report containing the parameters you just added.

Modify an existing line:
1. To modify an existing line on this page, click on the line. The Details pop-up is displayed.
2. Make your changes.
3. Click to save your modifications.

Create a flow report
The User Report Definition - Flow page enables you to create a linear report based on the Flow structure across different Periods, Journals, and Accounts.

The User Report Definition - Flow page is accessed from the page when you select a Flow type report and then, click the Define this report button.

Within the page, you will notice the following column layout:
- Line Number: each line of the report has a Line Number that allows you to identify it in the report.
- Type: displays one of the following Line Types: T - Text line, H - Header line, F - Flow data, X - Calculated Flow data, S - Summation data, P - Page Break.
- Code: this column shows the F - Flow or X - Calculated Flow Code.
- Description: describes content of line number.
- Sign: shows the amount presented as negative or positive.
- Period: amounts from the Current (C) or Reference (R) Consolidation Period.
- Journal: applicable Journal or Journal View. If this column is blank, then all journals are used.
- Col1 to Col3: each column displays an Account or Calculated Account per line.

Parameters for adding a new line:
1. Click . A Details pop-up appears for you to enter the required information for the line.
2. Enter the line number where you want the new line to appear.
3. Select a Line Type used in a Flow User Report.
4. Enter or select a Flow or Calculated Flow. The description of the selected Flow or Calculated Flow appears below the field.
5. Adjust Indentation, Font, and Layout as needed.
6. Change the Sign if necessary.
7. Select where the amounts come from, either the Current or Reference Consolidation Period.
8. Select the Journal or Journal View to be used for this line.
9. Select up to three different accounts to display on the report.
10. Click .
11. Click to return to the Define User Reports page and click to view the report containing the parameters you just added.

Modify an existing line:
1. To modify an existing line on this page, click on the line. The Details pop-up is displayed.
2. Make your changes.
3. Click to save your modifications.

Create a multi-period report
The User Report Definition - MultiPeriod page enables you to create a report based on the Account structure across different Flows, Journals, and Periods.

The User Report Definition - MultiPeriod page is accessed from the page when you select a Multi-period type report and then, click the Define this report button.

This page has two tabs: Rows and Columns.

Row definition:
- Line Number: each line of the report has a Line Number that allows you to identify it in the report.
- Type: displays one of the following Line Types: T - Text line, A - Account data, S - Summation Account data, P - Page Break.
- Account: code of the Account or Summation Account being used.
- Description: describes content of line number.
- Sign: shows the amount presented as negative or positive.

Parameters for adding a new line (row):
1. Click . A Details pop-up appears for you to enter the required information for the line.
2. Enter the line number where you want the new line to appear.
3. Select the Line Type used in a Multi-Period User Report.
4. Enter or select the Account or Calculated Account Code.
5. Adjust Indentation, Font, and Layout as needed.
6. Change the Sign if necessary.
7. Click .
8. Click the Columns tab to proceed to the next step.

Column definition:
- Column Number: the position or number of the selected Column within the report.
- Month: select an option from the drop-down.
- Month Offset: the number of months before or after, relatively from the Period defined within the Category and Cur/Ref fields.
- Fixed Month: if selected, you must select a fixed month for the column.
- Last Sequence: if selected, the last existing sequence for that period will be automatically used.
- Sequence: use this to define the sequence of the selected consolidation period.
- Same Category: if selected, the same Category / Nature as your Current or Reference Consolidation Period will be used.
- Category: select a category from the drop-down.
- Type: indicates the selected amounts as Year to Date (cumulative) amounts or Monthly amounts.
- Cur/Ref: the Period you want to display on the column, either the Current or the Reference Consolidation Period.

Parameters for adding a new column:
1. Click . A Details pop-up appears for you to enter the required information for the column.
2. Define the Column Number.
3. Select Month and Month Offset.
4. Define the Sequence and Category.
5. Select the Type and Cur/Ref.
6. Click .
7. Click to return to the Define User Reports page and click to view the report containing the parameters you just added.

Modify an existing line:
1. To modify an existing line on this page, click on the line. The Details pop-up is displayed.
2. Make your changes.
3. Click to save your modifications.

Create a standard report
The User Report Definition - Standard page enables you to create a linear report based on the Account structure.

The User Report Definition - Standard page is accessed from the page when you select a Standard type report and then, click the Define this report button.

On this page, you will see the following layout for each line:
- Line Number: each line of the report has a Line Number that allows you to quickly identify it in the report.
- Type: displays one of the following Line Types: T - Text line, A - Account data, S - Summation Account data, P - Page Break.
- Code: this column shows the A- Account or S - Calculated Account Code.
- Description: describes content of line number.
- Sign: shows the amount presented as negative or positive.

Parameters for adding a new line:
1. Click . A Details pop-up appears for you to enter the required information for the line.
2. Enter the line number where you want the new line to appear.
3. Select a Line Type used in a Standard User Report.
4. Enter or select the Account or Calculated Account Code.
5. Adjust Indentation, Font, and Layout as needed.
6. Change the Sign if necessary.
7. Click .
8. Click to return to the Define User Reports page and click to view the report containing the parameters you just added.

Modify an existing line:
1. To modify an existing line on this page, click on the line. The Details pop-up is displayed.
2. Make your changes.
3. Click to save your modifications.

Run user reports
On the User Reports page, you can select and run the user reports defined on the page.

To access the User Reports page, click Reports > User Reports > User Reports.

Generate a user report:
1. From the Report drop-down list, select a report.
2. In the Ref Period field, enter a reference consolidation period or click to search for one.
3. Select the type of data you want to use for the report from the Data drop-down list.
4. Select a company.
5. In the Journal Summation field, select a journal view.
6. In the Contribution by field, specify how the contribution should be shown.
7. Select a Point of View.
8. In the File type field, select the output file type.
9. Click to generate the report. After the report is generated, a download link appears below for you to click and view it in the selected file type.

Drill down a user report
The User Reports page provides the functionality to drill down into a user report, allowing you to navigate through the data presented from a broad overview to a more detailed perspective. With this report, you have the flexibility to drill down into multiple hierarchies, including POV (Point of View), companies, accounts, journals, and more.

To access the User Reports page, click Reports > Drill-Down Analysis > User Reports.

Drill down a report:
1. In the Report field, select a user report.
2. In the Journal Summation field, select a journal view.
3. Click . The selected report is displayed.
4. Identify the line you want to analyze on the report, and click the plus sign (+) beside the Description.
5. In the pop-up, select the structure you want to analyze and drill down into the selected structure.
6. After drilling down the selected structure, you can drill down on the detail even further using other structures.

---

## Frequently Asked Questions

### Navigation

**How do you access the User Report Definition - Cash Flow page?**
The User Report Definition - Cash Flow page is accessed from the page when you select a Cash Flow type report and then, click the Define this report button.

**How do you access the User Report Definition - Flow page?**
Access the User Report Definition - Flow page from the page when you select a Flow type report and then, click the Define this report button.

**How do you access the User Report Definition - MultiPeriod page?**
Access the User Report Definition - MultiPeriod page from the page when you select a Multi-period type report and then, click the Define this report button.

**How do you access the User Report Definition - Standard page?**
Access the User Report Definition - Standard page from the page when you select a Standard type report and then, click the Define this report button.

**How do you access the User Reports page?**
To access the User Reports page, click Reports > User Reports > User Reports.

**How do you access the Drill-Down Analysis section?**
To access the Drill-Down Analysis section, click Reports > Drill-Down Analysis > User Reports.

### General

**What structures are used in the User Report Definition - Cash Flow page?**
The structures used are Account and Calculated Account structure, the Flow structure, and the Journal structure.

**What information is required to add a new line to a cash-flow report?**
You need to enter the line number, select a Line Type, enter a Group Number, provide a description, adjust Indentation, Font, and Layout, change the Sign if necessary, select the Period, Account or Calculated Account Code, Flow or Calculated Flow Code, Journal or Journal View Code, and decide whether to show or hide the line.

**What columns are displayed in the User Report Definition - Flow page?**
The columns displayed are Line Number, Type, Code, Description, Sign, Period, Journal, and Col1 to Col3.

**What information is required to add a new line to a flow report?**
You need to enter the line number, select a Line Type, provide a Flow or Calculated Flow, adjust Indentation, Font, and Layout, change the Sign if necessary, select the Period, Journal or Journal View, and select up to three accounts.

**What are the two tabs available in the User Report Definition - MultiPeriod page?**
The two tabs available are Rows and Columns.

**What information is required to add a new line (row) in a multi-period report?**
You need to enter the line number, select a Line Type, provide an Account or Calculated Account Code, adjust Indentation, Font, and Layout, and change the Sign if necessary.

**What information is required to add a new column in a multi-period report?**
You need to define the Column Number, select Month and Month Offset, define the Sequence and Category, select the Type and Cur/Ref.

**What columns are displayed in the User Report Definition - Standard page?**
The columns displayed are Line Number, Type, Code, Description, and Sign.

**What information is required to add a new line to a standard report?**
You need to enter the line number, select a Line Type, provide an Account or Calculated Account Code, adjust Indentation, Font, and Layout, and change the Sign if necessary.

**What are the key components of the User Report Definition - Cash Flow page?**
The key components include Line Number, Group Number, Type, Description, Account, Flow, Journal, Sign, Period, and Visible option.

**What are the different Line Types available in a cash-flow report?**
The Line Types are T - Text Line, C - Cash-Flow Line, S - Summation data, and P - Page Break.

**What parameters are adjusted for each line in a cash-flow report?**
Parameters include Line Number, Group Number, Type, Description, Indentation, Font, Layout, Sign, Period, Account, Flow, Journal, and Visible option.

**What are the Line Types available in a flow report?**
The Line Types are T - Text line, H - Header line, F - Flow data, X - Calculated Flow data, S - Summation data, and P - Page Break.

**What do Col1 to Col3 represent in a flow report?**
Col1 to Col3 represent the accounts or calculated accounts displayed per line.

**What are the Line Types available in a multi-period report?**
The Line Types are T - Text line, A - Account data, S - Summation Account data, and P - Page Break.

**What information is displayed in the Column Number column of a multi-period report?**
The Column Number column displays the position or number of the selected Column within the report.

**What are the Line Types available in a standard report?**
The Line Types are T - Text line, A - Account data, S - Summation Account data, and P - Page Break.

**What options are available in the Data drop-down list on the User Reports page?**
The Data drop-down list allows you to select the type of data to use for the report.

**What options are available in the File type field on the User Reports page?**
The File type field allows you to select the output file type for the report.

**What happens after you click on the User Reports page?**
After clicking , the report is generated and a download link appears below for you to click and view it in the selected file type.

**What do you click to drill down a line in a user report?**
Click the plus sign (+) beside the Description to drill down a line in a user report.

**How can you drill down further after the initial drill-down?**
After drilling down the selected structure, you can drill down on the detail even further using other structures.

### How-To

**How do you add a new line to a cash-flow report?**
Click . A Details pop-up appears for you to enter the required information for the line, then click .

**How do you modify an existing line in a cash-flow report?**
To modify an existing line, click on the line, make your changes in the Details pop-up, and click .

**How do you create a flow report?**
To create a flow report, access the User Report Definition - Flow page from the page when you select a Flow type report and click the Define this report button.

**How do you add a new line to a flow report?**
Click . A Details pop-up appears for you to enter the required information for the line, then click .

**How do you modify an existing line in a flow report?**
To modify an existing line, click on the line, make your changes in the Details pop-up, and click .

**How do you create a multi-period report?**
To create a multi-period report, access the User Report Definition - MultiPeriod page from the page when you select a Multi-period type report and click the Define this report button.

**How do you add a new column in a multi-period report?**
Click . A Details pop-up appears for you to enter the required information for the column, then click .

**How do you modify an existing line in a multi-period report?**
To modify an existing line, click on the line, make your changes in the Details pop-up, and click .

**How do you create a standard report?**
To create a standard report, access the User Report Definition - Standard page from the page when you select a Standard type report and click the Define this report button.

**How do you add a new line to a standard report?**
Click . A Details pop-up appears for you to enter the required information for the line, then click .

**How do you modify an existing line in a standard report?**
To modify an existing line, click on the line, make your changes in the Details pop-up, and click .

**How do you generate a user report?**
To generate a user report, select a report from the Report drop-down list, enter a reference consolidation period in the Ref Period field, select the type of data from the Data drop-down list, select a company, select a journal view in the Journal Summation field, specify how the contribution should be shown in the Contribution by field, select a Point of View, and select the output file type in the File type field, then click .

**How do you drill down a user report?**
To drill down a user report, select a user report in the Report field, select a journal view in the Journal Summation field, click , identify the line to analyze and click the plus sign (+) beside the Description, select the structure to analyze in the pop-up, and drill down into the selected structure.

**How do you define the layout for each line in a cash-flow report?**
Each line has a Line Number, Group Number, Type, Description, Account, Flow, Journal, Sign, Period, and Visible option to define its layout.

**How do you add a new line (row) to a multi-period report?**
Click . A Details pop-up appears for you to enter the required information for the line, then click .

**How do you select a company for the report on the User Reports page?**
Select a company from the available options.

**How do you specify the contribution in the User Reports page?**
In the Contribution by field, specify how the contribution should be shown.

**How do you start the drill-down analysis in the Drill-Down Analysis section?**
Click to display the selected report and identify the line to analyze.

### Concepts

**What is the purpose of the Line Number in a cash-flow report?**
The Line Number allows you to identify each line in the report.

**What is the purpose of the Cash-Flow Report Creation section?**
The Cash-Flow Report Creation section explains how to define and generate reports for cash flow statements.

**What is the purpose of the Flow Report Creation section?**
The Flow Report Creation section details the process of creating reports based on flow structures across different periods, journals, and accounts.

**What is the purpose of the Multi-Period Report Creation section?**
The Multi-Period Report Creation section provides steps for generating reports that span multiple periods, allowing comprehensive financial analysis over time.

**What is the purpose of the Standard Report Creation section?**
The Standard Report Creation section outlines the creation of linear reports based on account structures.

**What does the Line Number represent in a report?**
The Line Number represents the identifier for each line in the report.

**What is the purpose of the Visible option in a report line?**
The Visible option allows you to show or hide the line on the report.

**What is the purpose of the User Report Definition - Flow page?**
The User Report Definition - Flow page enables you to create a linear report based on the Flow structure across different Periods, Journals, and Accounts.

**What is displayed in the Code column of a flow report?**
The Code column shows the F - Flow or X - Calculated Flow Code.

**What is the purpose of the Sign column in a flow report?**
The Sign column shows the amount presented as negative or positive.

**What is the purpose of the Period column in a flow report?**
The Period column shows the amounts from the Current (C) or Reference (R) Consolidation Period.

**What does the Journal column indicate in a flow report?**
The Journal column indicates the applicable Journal or Journal View used for the line.

**What is the purpose of the User Report Definition - MultiPeriod page?**
The User Report Definition - MultiPeriod page enables you to create a report based on the Account structure across different Flows, Journals, and Periods.

**What is displayed in the Line Number column of a multi-period report?**
The Line Number column displays the identifier for each line in the report.

**What does the Description column show in a multi-period report?**
The Description column shows the content of the line number.

**What is the purpose of the Sign column in a multi-period report?**
The Sign column shows the amount presented as negative or positive.

**What does the Month column show in a multi-period report?**
The Month column shows the selected option from the drop-down.

**What is the purpose of the Month Offset column in a multi-period report?**
The Month Offset column shows the number of months before or after, relatively from the Period defined within the Category and Cur/Ref fields.

**What does the Fixed Month column indicate in a multi-period report?**
The Fixed Month column indicates if a fixed month is selected for the column.

**What is the purpose of the Last Sequence column in a multi-period report?**
The Last Sequence column shows if the last existing sequence for that period is automatically used.

**What does the Sequence column define in a multi-period report?**
The Sequence column defines the sequence of the selected consolidation period.

**What is the Same Category column used for in a multi-period report?**
The Same Category column shows if the same Category/Nature as your Current or Reference Consolidation Period is used.

**What does the Category column show in a multi-period report?**
The Category column shows the selected category from the drop-down.

**What does the Type column indicate in a multi-period report?**
The Type column indicates the selected amounts as Year to Date (cumulative) amounts or Monthly amounts.

**What does the Cur/Ref column show in a multi-period report?**
The Cur/Ref column shows the Period you want to display on the column, either the Current or the Reference Consolidation Period.

**What is the purpose of the User Report Definition - Standard page?**
The User Report Definition - Standard page enables you to create a linear report based on the Account structure.

**What is displayed in the Line Number column of a standard report?**
The Line Number column displays the identifier for each line in the report.

**What does the Code column show in a standard report?**
The Code column shows the A - Account or S - Calculated Account Code.

**What is the purpose of the Description column in a standard report?**
The Description column describes the content of the line number.

**What is the purpose of the Sign column in a standard report?**
The Sign column shows the amount presented as negative or positive.

**What is the purpose of the User Reports page?**
The User Reports page allows you to select and run the user reports defined on the page.

**What does the Report drop-down list in the User Reports page allow you to do?**
The Report drop-down list allows you to select a user report to generate.

**What is the purpose of the Ref Period field in the User Reports page?**
The Ref Period field allows you to enter a reference consolidation period or search for one.

**What does the Journal Summation field allow you to do on the User Reports page?**
The Journal Summation field allows you to select a journal view for the report.

**What is the purpose of the Point of View field in the User Reports page?**
The Point of View field allows you to select a specific point of view for the report.

**What is the purpose of the Drill-Down Analysis section?**
The Drill-Down Analysis section allows you to drill down into multiple hierarchies in a user report, including POV (Point of View), companies, accounts, journals, and more.

**What does the Report field allow you to do in the Drill-Down Analysis section?**
The Report field allows you to select a user report to drill down into.

**What is the purpose of the Journal Summation field in the Drill-Down Analysis section?**
The Journal Summation field allows you to select a journal view for the drill-down analysis.

**What is the next step after clicking the plus sign (+) in a user report?**
In the pop-up, select the structure to analyze and drill down into the selected structure.

---

*Help Topic 0392 | Category: Reporting | Last Updated: 2024-12-03*