# Bundle validation

## Metadata
- **Index**: 0332
- **Topics**:  User Settings, Workflow Management, Data Import and Export, Validation Reports
- **Keywords**:  Profile, Consolidation Period, Task Management, Gantt Chart, Pie Chart, Status Board, Validation, Document Storage, File Upload, User Access, Import Data, Export Data, Mapping Tables, Adjustments, Data Report, CSV, Excel, HUB, Validation Report, Group Validation, Bundle Validation
- **Theory Reference**: Data Validation

## Summary

 The provided documentation for the Financial Consolidation product includes comprehensive instructions on user settings, workflow management, data import and export, and validation reports. The User Settings section covers profile customization, period selection, and language settings. Workflow Management explains how to manage tasks, view Gantt and Pie charts, and export data. The Data Import and Export sections detail handling different file structures, specifying import/export parameters, and validating data quality. The Validation Reports section provides steps to generate and analyze validation reports, including bundle and group validation, and offers detailed guidance on resolving data validation issues.

---

## User Guide

User settings
The User Settings page allows you to view your profile and edit settings such as your language and working consolidation period to match your preferences or needs. Access the user settings page by clicking the Profile icon or a Current or Reference consolidation period on top of any page.

Access through profile icon: Click and then select the User Profile option. This displays both your user profile and consolidation period selection areas.

Access through a consolidation period: Click either the Current or Reference consolidation period on top of the page. This hides the user profile area and displays only the period selection area.

Select a different consolidation period: Access the User Settings page by clicking the consolidation period you want to change. The User Settings page displays the consolidation periods including their codes, reference period codes, and names. A red lock indicates a locked period, and a black lock indicates an open period. To limit the number of consolidation periods in view, you can hide locked periods or filter the list. From this list, click on the period you want to use. In the Select Period column, click to set the period as both the current and reference period, to set the period as the current period, or to set the period as the reference period. The selected periods are reflected in the Current Period and Reference Period fields. Click to confirm.

Change application or data languages: Access the User Settings page through your Profile icon. To change your Application or Data Language, go to the appropriate field and select another language from the drop-down. Click to confirm.

Download PDF files: To download generated PDF files on your local hard drive, select the Download generated PDF files option. This option is available on the User Settings page accessed through the Profile icon. Click to confirm.

Workflow Management
The Workflow page displays tasks assigned to you, each with a description, owner, start and end date, and status. To access the Workflow page, click Workflows > Workflow. The Task list field contains a list of tasks assigned to the task owner. Select a task to see the individual tasks in the chart below. The Gantt chart displays tasks in a selected list, including the Description, Owner, Start and End dates, and Status.

Set your preferences: You can set preferences to control how information is displayed on the Workflow page, such as showing/hiding the Gantt chart, Pie chart, or Companies list.

Show/Hide Gantt chart: The Gantt chart displays tasks according to the set timeline and scale. You can change this by using the Gantt timeline and Gantt scale drop-down fields. To hide the Gantt chart, click to cancel the selection.

Show/Hide Pie chart: To display tasks in a pie chart, select the Show/Hide the Pie Chart icon. Hover over the color to see the status and count of tasks. To hide the pie chart, click to cancel the selection.

Show/Hide the companies: To show or hide the list of companies, select the Show/Hide the companies icon. To hide the companies, click to cancel the selection.

Export tasks: To work with your task list in Excel, click the Export to Excel icon on the Workflow page. Select the list you want to export and click to export the list to an Excel file.

Start work on a task: Select the company you want to work on from the table of companies. In the Task list field, select a task. The tasks are displayed in the chart below. Click on a task to see the details. In the Status field, change from Not started to In progress. Click to navigate to the task page or to start an automated task. Use the Comment text box to add additional information and click to save.

Complete a task: After completing a task, update your progress by selecting the company, task, and changing the status to Completed in the Task details panel. Optionally, add comments and click to confirm. An automatic email is sent to the approver/administrator.

Reject a task: To reject a task, select the company, task, and change the status to Rejected in the Task details panel. Add comments and click to confirm. An automatic email is sent to the approver/administrator.

View task history: The history of a task shows its life cycle stages. To view the history, select the company, task, and go to the History tab. Use filters to narrow results.

Update company task status: Depending on your role, you can use buttons below the Companies table to confirm, approve, audit, or reject tasks. Confirming triggers an email to the auditor/administrator, who verifies the work. Approved work notifies the end user, while rejected work requires corrections. Monitor work progress on the Dashboard.

Status Board
The status board provides an at-a-glance view of all companies in the consolidation, including the status of the data entry process for each company. Authorized users can generate status reports, run validation rules, review error details, and update data entry status. The board includes columns for Company Code, Company Name, Modified date and time, Number of Warnings and Errors, Validation Status, Confirmed, Approved, and Audited statuses. Click column headers to sort the table.

Generate status report: Go to the Status Report panel, select the output file type, and click to generate the report. A download link appears below for viewing.

Run validation rules: Select the companies for validation, go to the Run the validation panel, and click Validate. The validation status is reflected in the column for each company. Click beside the status to see details.

Review error details: Click to review specifics of balance errors or data loaded for better insight into issues.

Change a company's data entry status: Select the company, and in the Change status panel, select the new status. End-users can select Confirmation status, Consolidators can Accept or Refuse data, Auditors can Accept data, and Administrators have all options. Click to change the status.

File Repository
The Documents Repository serves as a collaborative storage area accessible to all authorized users. Administrators can organize, maintain, and govern the documents stored. To access the repository, click Reports > Document Repository. The page is divided into a folder tree on the left and a file section on the right. The folder tree allows navigation through the structure created by the Administrator/Consolidator. The application administrator can grant rights to specific roles to access folders.

Depending on your rights, you can view files, download single or multiple files, refresh folder content, delete files, and upload files. To upload a file, select a folder and click to upload. Enter a description and click to confirm. Administrators can specify user access and permissions.

Select a consolidation period
In the Financial Consolidation application, the Current and Reference Consolidation Periods are displayed on top of every page. If the consolidation default period is not what you want, you can change to a different consolidation period.

Change a consolidation period: Click the Select Period icon beside the consolidation period you want to change. The User Settings page displays the consolidation periods with their codes, reference period codes, and names. A red lock indicates a locked period, and a black lock indicates an open period. To limit the number of consolidation periods in view, hide locked periods or filter the list. From this list, click on the desired period. In the Select Period column, click to set the period as both the current and reference period, to set the period as the current period, or to set the period as the reference period. The selected periods are reflected in the Current Period and Reference Period fields. Click to confirm.

Filter the list of consolidation periods: Use filters to narrow down the list of consolidation periods with wildcards like ? and *. This is useful for viewing all periods of one year, or all periods with the same nature or sequence. Examples include typing 20* to see all periods from the 21st century, ACT to see all periods with the nature ACT, or 20 12ACT to see all periods from the 12th month of the 21st century with the nature ACT.

Period locking
The Define Period Locking page allows you to set dates after which the import or input of specific types of data will be disabled. When you lock a period, it restricts any modifications to the selected data type for that period across all companies within the group. Administrators and Consolidators can modify locked data types after the period lock date has commenced. Six data types are available for locking: Closing Amounts, Intercompany, Flows, Intercompany Flows, Analytical Dimensions, and Adjustments.

Lock data: When data is locked, it is locked for all companies in the group and prevents changes to the selected data type for that period. Locking data type is different from when an administrator locks a period, which locks all data types for that period for all companies. Access the Define Period Locking page, click in the Data Locking Date field to specify a date, and select a date from the calendar. The default time of 12:00 AM appears in the time field, which can be changed. Optionally, select another data type and enter a lock date. Click to confirm

. On the set date, import or input of the locked data types is disabled in that period.

Unlock data: On the Define Period Locking page, click the data you want to unlock. In the Data Locking Date field, click to clear the lock date. Click to confirm.

Currency Exchange Rates
In the Financial Consolidation application, every account is set up to use a specific rate individually on an account-by-account basis. During the consolidation process, the application examines each account's configuration and selects the appropriate currency rate based on the company's currency and the period's currency. To access the Exchange Rates page, click Group > Exchange Rates. On this page, you can enter, import, or export currency exchange rates.

Enter a currency exchange rate: The Exchange Rates page is used for manually entering currency exchange rates for a consolidation period. These rates convert values from one currency to another in a selected period. The Exchange Rates tab presents the page divided into two panels: the Period Code panel on the left, showing a list of all consolidation periods, and the details panel on the right, showing details of available currencies for a selected period. The Currency table includes columns for CurrCode, Close, Average, and Month rates for both the Current and Reference Consolidation Periods, along with Modified By and Modified date and time.

To add a currency exchange rate: Select the consolidation period and currency. Optionally, display all currencies with or without amounts. Enter the Close, Average, and Month currency rates. Ensure the correct decimal symbol is used according to local or regional settings. Click to save changes. Errors will display a notification with details.

Print currency exchange rate report: The Currencies Reports tab contains the exchange rates of active currencies for the given period. Report types include Standard, Reporting, Statutory, and Current Period reports. To generate a report, select the type, base currency, and output file type. Click to generate the report and download the file.

Import exchange rates: To access the Import Exchange Rates page, click Transfers > Exchange Rates > Import Exchange Rates. You can import exchange rates from CSV, Excel, ECB (SDMX European Central Bank), and NBS (SDMX National Bank of Slovakia). The file format determines the parameters needed for the import. For CSV, specify the CSV Separator, Decimal Separator, Thousand Separator, and Text delimiter. Upload the file, view it, and transfer the data into the database. For Excel, specify the Sheet Name and Currency, upload the file, view it, and transfer the data into the database. For ECB/NBS, select the data source, currency pairs, period year, and month, then validate and import the rates. Ensure the import file meets the specified format.

Export currency exchange rates: To access the Export Exchange Rates page, click Transfers > Exchange Rates > Export Exchange Rates. In the Period field, select the consolidation period. In the File Type field, select the file format (XLS or CSV). Specify parameters based on the file type, such as Sheet Name for XLS or separators for CSV. Click to export the currency exchange rates for the selected period. A download link will appear for viewing the data.

Company Management
Add companies: The Companies page is used for adding, reviewing, or editing companies. This is where you add and maintain all the various subsidiaries and divisions of the parent company. To access the Companies page, click Group > Companies. The default settings for a new company include currency code, number of decimals, consolidation method, group percentage, minority percentage, group control percentage, and number of financial and voting rights. The left-side panel lists all available companies, and the right-side panel displays the details of any selected company, including code, description, and country code. To add a company, click , enter the required information, and save.

Additional company data: The Companies Additional Info page enables users to add supplementary details for companies. Administrators can create various fields, and users can then input corresponding values for their associated companies. For example, an administrator can establish a field to collect VAT numbers for subsidiaries. To access this page, click Group > Companies and then click . To add an additional parameter, specify the line number, label, and description, then save.

Create the group structure: The Group Structure page defines the interconnected relationships between all companies within the group. This page is used to input and manage direct relationships among entities, determining the appropriate consolidation method. The left-side panel displays existing companies with their codes and names. The right-side panel shows details for any selected company, including company code, name, financial rights, voting rights, group percentage, minority percentage, and group control percentage. The Shareholders tab is used to enter the number of shares held by other companies in the group, while the Participations tab is used to enter the number of shares held in other companies. To update the consolidation method and percentages, save changes and proceed with caution as it can have significant consequences.

Local Adjustments
View local adjustments: To access the Local Adjustments View page, click Data Entry > Manual Data Entry > Local Adjustments > View. The top panel displays the list of local adjustments available in the consolidation by type, entry number, company code/name, description, and modification date. You can preview, create, modify, or delete adjustments. Details of selected adjustments are displayed in the lower panel.

Create a new adjustment: Click to add a new local adjustment. Enter the required information on the Manual Input page, including company, journal, and account details, then save.

Modify an adjustment: Select an adjustment and click to open the Manual Input page for modifications.

Local adjustments - manual input: To access the Local Adjustments Manual Input page, click Data Entry > Manual Data Entry > Local Adjustments > Manual Input. Enter general adjustment-related information such as company, journal, behavior, and attachment. In the data area, enter account codes, debit/credit amounts, and other details. Save the adjustment, and use additional functions such as multiply/divide for efficient reporting.

Flow Management
The Flow Management page allows you to manage flows for a selected company. You can recalculate or adjust specific flows within the company’s financial records, update historical exchange rates or other rates used in financial calculations based on the flow of money or the prevailing rate at a specific point in time; and reconcile and account for any discrepancies or differences in flows. In addition, you can reset flow values based on specific requirements.

Manage Flows: Select the options you want to use and provide all the information required for the selected options. Book all remaining differences on flow allows you to account and record any unresolved discrepancies in the flow, using one of the options below. Set to zero allows you reset flow values to zero based on one of these options: All flows - sets all flows within the company to zero, essentially resetting the flow values to eliminate any existing values or transactions. Only flows - sets the value of selected flows to zero, while leaving other flows unaffected. All flows except - sets all flows to zero except for a specified subset of flows. Merge company allows you to combine the financial data of a selected company. Recalculate specific flows allows you to recalculate or adjust specific flows within the company’s financial records. Update historical rates allows you to update historical exchange rates or other rates used in financial calculations based on a selected flow code and the prevailing rate at a specific point in time.

Analytical Dimensions
The Analytical Dimensions page lets you capture financial transactions in more detail than just using account numbers in the Chart of Accounts. With analytical dimensions, you can enter data that breaks down the values of any account associated with dimensions across different groups.

Enter analytical dimensions: In the Company field, enter the company code or click to select it in the selection pop-up window. In the Account field, enter the account code or click to select it in the selection pop-up window. In the Dimensions Group field, if the group is not automatically selected, select an applicable group. Click to display data based on the selections (valid combination of company/account/dimension group) you made in the fields above. How the data is displayed is dependent on the number of dimensions linked to the account. By default, dimensions are displayed as follows: dimension 1 is displayed in rows, dimension 2 (if any) is displayed in columns, dimension 3 (if any) is displayed as a combo list. Optionally, use any one of these options to filter the data displayed: See all lines (default), See only lines with amounts, See only lines without amounts. In the table, enter the values for the dimensions. The sum of the values you enter in each row and column is displayed at the end of the corresponding dimension. The following amounts are displayed (as applicable) in their respective fields below: Adjusted amount - amount from local books including local adjustments done in Financial Consolidation. This amount should be justified by dimension, so it should be equal to the total of all values from the detail area. Local amount - amount from local books excluding local adjustments done in Financial Consolidation. This amount comes from the ERP, so it can be controlled by the end user with the local books. The difference between Adjusted amount and Local amount comes from the local journals. Justified amount - the total of all values filled in for the combination of company /account /dimension group, including values that are not directly visible (when there is a dimension 3 for instance or a long list of codes not directly displayed in rows /columns). Difference to justify - the difference between the Justified amount and the Adjusted amount. Click to save.

Intercompany Transactions
Intercompany data entry: The Intercompanies page is where you record the transactions conducted with other companies within the group. Here, you enter transaction details for each account and partner involved.

Enter intercompany transactions: Select the company for which you want to enter intercompany transactions from the drop-down list on top of the left-side panel. For the selected company, all its intercompany accounts that are used for reporting intercompany transactions are displayed in the panel below. From the list of accounts, select the account

that is applicable to the transaction. From the intercompany partners displayed on the right, select the one with which the transaction was done. In the Current Local Amount field, enter the intercompany transaction amount in the local currency of the parent. In the Current Transaction Amount field, enter the current transaction amount. You can click to access the Intercompany viewer to see the existing intercompany transactions entered on a specific account by the company on the left, and on the right, the corresponding transactions entered by the counterpart. If you need to enter Flow or Dimension information, the applicable buttons are activated. Click on the activated button to provide the required Flow or Dimension information and return to the main page. Click to save.

Define mapping tables
The Define Mapping Tables page enables you to define mapping tables for the different structures used during an import: Accounts, Companies, Dimension Groups, Dimension Detail Codes, and Flows. A mapping table is used to establish a relationship between two or more sets of data, containing information about the data fields in the source and target systems and defining how data from the source should be transformed and mapped to the target system.

To access the Define Mapping Tables page, click Transfers > Data > Define Mapping Tables. The left-side panel displays a list of all the available mapping tables, including their Code and Name. The right-side panel displays the parameters of the mapping selected on the left side panel, including the following: Code - ID of the selected mapping table, Name - Name of the mapping table, Period - Consolidation period in which you want to work, Created by - creator of the mapping table, Modified by - name of the user who last modified the selected mapping table, Created On - date on which the mapping table was created, Modified On - date on which the mapping table was last modified. The structures you can use to create your mapping table are listed under the Period field and include Accounts, Companies, Dimension Groups, Dimension Detail Codes, and Flows.

Define a mapping table: Click . Enter the Code and Name of the mapping table in their respective fields. The Current Period is the default period in this field and can only be edited when you select an existing mapping to duplicate. Select a structure: Accounts, Companies, Flows, Dimension Groups, or Dimension Detail Codes. Click . All the items applicable to the structure you selected display in the Target table below, showing their Composed Code and Description. You can filter the list to display items With Source Only (with mapping data only), or the items Without Source Only (with no mapping data).

To map an item, click on the code in the Target table, enter a Code to identify that item on the source mapping table, the Mapping Factor (optional), and a Description. Click to add the item to the Source table. To duplicate a mapping table, select a mapping table from the list on the left-side panel, click , enter the Code and Name for the mapping table, select a different Period if needed, and click .

Define import/export file structure
On the Import File Structure and Export File Structure pages, you can define the structure of your file to match the files you want to import/export. This requires defining the general properties of the file structure, specifying the type of data and other parameters. To access the Import or Export File structure, click Transfers > Data > Define File Structure and then select Import or Export.

Import file structure: Specify general file properties, type of data, import options, parameters, and mapping tables. Create an import file structure by entering the file ID, selecting the Type of Amount (Net Amounts, Debit/Credit amounts), summarizing Interco, signed amounts, calculating profit, negative charges, and scale of amounts. Specify the file type (XLS, CSV, HUB), type of data, and additional options. For parameters, map the columns to the attributes and use functions like Substr/Merge/Prefix/Suffix/Fix. Enable import rules to transform the imported information.

Export file structure: Specify general export file properties, type of data, export options, parameters, and export rules. Create an export file structure by entering the file ID, selecting the Type of Amount (Net Amounts, Debit/Credit amounts), and file type (XLS, CSV, HUB). Specify the additional options and parameters. Enable export rules to transform the exported information.

Import data
Using the Import Data page, you can import bundle data. The system checks the format and quality of the data to ensure its effectiveness. To access the Import Data page, click Transfers > Data > Import Data. Select a structure from the File Structure drop-down list, upload the file, expand the Details section, fill in the parameters required, and specify the type of data to overwrite during import. Options include discarding errors on rows with zero amounts, replacing imported types, and replacing imported accounts. Select the different types of interfaces to use during import. Click to save.

Import adjustments
Through the Import Adjustments page, you can import adjustments from an external source into the application. To access the Import Adjustments page, click Transfers > Adjustments > Import Adjustments. Select the file type (CSV, Excel, HUB) and specify supplementary parameters like Sheet Name, CSV Separator, Decimal Separator, and Thousand Separator. Upload the file, specify overwrite options, and click to start the import. The required structure of the import file includes columns like CompanyID, JournalType, JournalCategory, JournalEntry, AccountNbr, PartnerId, Currency, Amount, and more.

Export adjustments
Through the Export Adjustments page, you can export adjustment data from the application to an external system. To access the Export Adjustments page, click Transfers > Adjustments > Export Adjustments. Select the consolidation period, file type (XLS, CSV, HUB), and specify parameters for the export. Select the companies and journal types to export. Click to export the adjustments and download the data.

Export data
Through the Export Data page, you can export consolidated data and bundle data from individual companies. To access the Export Data page, click Transfers > Data > Export Data. Select the consolidation period, file structure (XLS, CSV, HUB), and specify parameters for the export. Select the data to export, including local amounts, contribution, and consolidated amounts. Click to export the selected data and download it.

Import data report
The Import Data Report page is used to generate reports of data (ledger accounts) imported into the Financial Consolidation application. To access the Import Data Report page, click Transfers > Data > Import Data Report. Select the accounts and companies for the report, enter a Calc Account code, select the sort order, data type, and output file type (PDF, XLS, XLSX). Click to generate the report and download it.

Bundle data validation
The Bundle Validation page displays the contents of a chosen validation report, showcasing the identified issues within the data (whether filled-in or imported). Additionally, it provides a platform for you to delve into and resolve the encountered issues effectively. To access the Bundle Validation page, click Data Entry > Validation Reports > Bundle Validation. You can select a validation report, view the output (including the validation types in groups and any errors or warnings), and click on an error or warning to investigate it further. You also have the option to download the report.

To view and investigate a bundle validation report:
1. From the Company list, select a company.
2. From the Validation Report list, select the report you want to display.
3. Click View report. The report is displayed below. A summary of the errors and warnings found in reports are displayed in two groups: Group Validation and System Validation.
4. Optionally, use the All, Errors, and Warnings buttons to sort the records displayed on the page as follows:
- All: Displays all bundle validation rule codes, including those processed successfully, those with errors, and those with warnings.
- Errors: Displays only the validation rules that failed and were significant enough to halt the validation process.
- Warnings: Displays the validation rules that encountered some validation issues that were not significant enough to halt the validation process.
5. Click on the issue (error or warning) that you want to investigate. All the details that caused the warning or error are displayed.
6. To dig deeper, click to display a data entry page relevant to the type of account. On the data entry page, you can investigate the cause of the issue and make necessary corrections.

Download a bundle validation report:
1. Select a Company and the Validation report you want to download.
2. Click .
3. In the Report Settings pop-up window, provide the required information:
- In the File type field, select the output file type. Options include PDF, XLS, and XLSX.
- In the Included in the report field, select the options you want included in the report:
- Show all rules: If selected, the report will show all rules. Unselected, the report shows only rules in error.
- Show details: If selected, the report will show the details of every rule. Unselected, it shows only the summary of the rules.
- Show zeros: If selected, it shows all rules, including the ones where every item has an amount of zero.
4. Click to generate the report.

---

## Frequently Asked Questions

### Concepts

**What is the purpose of the User Settings page?**
The User Settings page allows you to view and edit your profile settings, such as language and consolidation period preferences.

**What is period locking?**
Period locking restricts modifications to specific data types for a period across all companies within the group.

**What is the purpose of the Group Structure page?**
The Group Structure page defines relationships between companies in the group, managing shareholding and consolidation methods.

**What is the purpose of the Flow Management page?**
The Flow Management page allows you to manage flows, including recalculating flows, updating rates, and reconciling discrepancies.

**What is the purpose of the Intercompanies page?**
The Intercompanies page records transactions conducted with other companies within the group.

**What is the purpose of the Export File Structure page?**
The Export File Structure page defines the structure of files to match the data you want to export.

**What is the purpose of the Import Data Report page?**
The Import Data Report page generates reports of data imported into the Financial Consolidation application.

**What does the Workflow page display?**
The Workflow page displays tasks assigned to you, each with a description, owner, start and end date, and status.

**What is the function of the Status Board?**
The Status Board provides an overview of the data entry status for all companies in the consolidation, including validation status and error details.

**What is the purpose of the Companies page?**
The Companies page is used for adding, reviewing, or editing companies within the group, including maintaining subsidiary and division information.

**What is the Group Structure page used for?**
The Group Structure page defines the interconnected relationships between all companies within the group, determining the appropriate consolidation method.

**What is the purpose of the Analytical Dimensions page?**
The Analytical Dimensions page allows you to capture financial transactions in more detail by breaking down account values associated with different dimensions.

**What is the purpose of the Define Mapping Tables page?**
The Define Mapping Tables page allows you to define mapping tables for different structures used during data import and export.

**What is the purpose of the Import File Structure page?**
The Import File Structure page allows you to define the structure of files to match the data you want to import, ensuring compatibility and accurate data transfer.

**What is the process to export data?**
To export data, select the consolidation period, file structure, specify parameters, select data to export, and start the export.

**What do the red and black locks indicate on the User Settings page?**
On the User Settings page, a red lock indicates a locked period, while a black lock indicates an open period.

**What is the purpose of the Gantt chart on the Workflow page?**
The Gantt chart on the Workflow page displays tasks according to the set timeline and scale.

**What does the Pie chart on the Workflow page represent?**
The Pie chart on the Workflow page represents tasks, showing their status and count.

**What is the purpose of the Document Repository?**
The Document Repository serves as a collaborative storage area for authorized users to view, download, upload, and manage documents.

**What is the purpose of the Select Period icon?**
The Select Period icon is used to change the consolidation period displayed on top of every page.

**What is the purpose of the Exchange Rates page?**
The Exchange Rates page is used to enter, import, or export currency exchange rates for a consolidation period.

**What is the purpose of the Local Adjustments View page?**
The Local Adjustments View page allows you to access and review details of local adjustments available in the consolidation.

**What is the purpose of the Bundle Validation page?**
The Bundle Validation page displays the contents of a validation report, showcasing identified issues within the data and providing a platform to resolve them.

**What is the function of the Gantt chart on the Workflow page?**
The Gantt chart on the Workflow page displays tasks according to a timeline, helping you manage and track progress visually.

**What is the process to lock a data type for a period?**
To lock a data type for a period, go to the Define Period Locking page, specify the lock date in the Data Locking Date field, and click to confirm.

**What is the purpose of the Intercompany Matching page?**
The Intercompany Matching page is used for reconciling and eliminating transactions between companies in a group.

**What is the purpose of the Intercompany Elimination page?**
The Intercompany Elimination page establishes automated eliminations for intercompany variances below a specified threshold.

**What is the purpose of the Consolidation Events page?**
The Consolidation Events page manages events like eliminations, adjustments, and other configurable activities during consolidation.

### How-To

**How do you download generated PDF files?**
To download generated PDF files, select the option on the User Settings page accessed through the Profile icon, and click to confirm.

**How do you show or hide the Gantt chart?**
To show or hide the Gantt chart, click the corresponding icon to toggle the display.

**How do you start work on a task?**
To start work on a task, select the company and task, change the status to In progress, and click to navigate to the task page.

**How do you complete a task?**
To complete a task, select the company and task, change the status to Completed, optionally add comments, and click to confirm.

**How do you run validation rules from the Status Board?**
To run validation rules, select the companies, go to the validation panel, and click Validate.

**How do you change the consolidation period?**
To change the consolidation period, click the Select Period icon, choose the desired period, and click to confirm.

**How do you enter a currency exchange rate?**
To enter a currency exchange rate, select the period and currency, enter the rates, and click to save changes.

**How do you add a company?**
To add a company, click the add icon on the Companies page, enter the required information, and save.

**How do you create a local adjustment?**
To create a local adjustment, click the add icon on the Local Adjustments View page, enter information on the Manual Input page, and save.

**How do you enter analytical dimensions?**
Select the company, account, and dimension group, then enter values for the dimensions in the table.

**How do you define a mapping table?**
To define a mapping table, click the add icon, enter the Code and Name, select a structure, and map items in the Target table.

**How do you create an import file structure?**
To create an import file structure, enter the file ID, select data type, import options, parameters, and mapping tables, then save.

**How do you import bundle data?**
Select the structure from the File Structure list, upload the file, fill in parameters, and click to start the import.

**What steps are involved in importing adjustments?**
Select the file type, upload the file, specify parameters, and click to start the import.

**How do you export data?**
Select the consolidation period, file structure, specify parameters, select data to export, and click to start the export.

**How do you view a bundle validation report?**
Select a company and report, click View report, and investigate issues by clicking on errors or warnings.

**How do you download a bundle validation report?**
Select a company and report, click the download icon, provide required information, and click to generate the report.

**How do you set a lock date for data?**
On the Define Period Locking page, click in the Data Locking Date field to specify a date, and click to confirm.

**How do you change the working consolidation period?**
To change the working consolidation period, access the User Settings page, select the desired period, and click to confirm.

**How do you start work on a task in the Workflow page?**
Select the company and task, change the status to 'In progress' in the Task details panel, and click to navigate to the task page.

**How do you complete a task in the Workflow page?**
After completing a task, update the status to 'Completed' in the Task details panel, optionally add comments, and click to confirm.

**How do you review error details on the Status Board?**
Click beside the validation status to see the details of balance errors or data loaded for better insight into issues.

**How do you set a lock date for data types?**
On the Define Period Locking page, specify a lock date in the Data Locking Date field and click to confirm.

**How do you unlock data types?**
To unlock data types, clear the lock date in the Data Locking Date field on the Define Period Locking page and click to confirm.

**How do you manually enter currency exchange rates?**
On the Exchange Rates page, select the period and currency, enter the Close, Average, and Month rates, and click to save changes.

**How do you view local adjustments?**
To view local adjustments, go to the Local Adjustments View page, where you can preview, create, modify, or delete adjustments.

**How do you manage flows in the Flow Management page?**
Select the options you want to use, provide required information, and click to save.

**How do you enter intercompany transactions?**
To enter intercompany transactions, select the company, account, and partner, enter transaction amounts, and save the details.

**How do you create an export file structure?**
To create an export file structure, enter the file ID, select data type, export options, parameters, and export rules, then save.

**How do you import adjustments?**
To import adjustments, select the file type, upload the file, specify parameters, and click to start the import.

**How do you export adjustments?**
To export adjustments, select the consolidation period, file type, specify parameters, select companies and journal types, and start the export.

**How do you change the current consolidation period?**
To change the current consolidation period, click the consolidation period you want to change, then select it from the list and click to confirm.

**How do you change the application or data language?**
To change the application or data language, go to the User Settings page through the Profile icon, select another language from the drop-down, and click to confirm.

**How do you hide the Gantt chart on the Workflow page?**
To hide the Gantt chart, click the corresponding icon to cancel the selection.

**How do you export tasks to Excel from the Workflow page?**
To export tasks to Excel, click the Export to Excel icon on the Workflow page, select the list you want to export, and click to export the list to an Excel file.

**What steps do you follow to start work on a task?**
To start work on a task, select the company from the table of companies, select a task from the Task list field, change the status to In progress, and click to navigate to the task page.

**How do you complete a task on the Workflow page?**
To complete a task, select the company, task, change the status to Completed in the Task details panel, optionally add comments, and click to confirm.

**How do you reject a task on the Workflow page?**
To reject a task, select the company, task, change the status to Rejected in the Task details panel, add comments, and click to confirm.

**How do you generate a status report from the Status Board?**
To generate a status report, go to the Status Report panel, select the output file type, and click to generate the report. A download link appears for viewing.

**How do you change a company's data entry status?**
To change a company's data entry status, select the company, choose the new status from the Change status panel, and click to confirm.

**How do you upload a file to the Document Repository?**
To upload a file, select a folder in the Document Repository, click the upload icon, enter a description, and click to confirm.

**How do you lock data in a consolidation period?**
To lock data, access the Define Period Locking page, specify a lock date for the data type, and click to confirm.

**How do you unlock data in a consolidation period?**
To unlock data, access the Define Period Locking page, click the data you want to unlock, clear the lock date, and click to confirm.

**How do you manually enter a currency exchange rate?**
To manually enter a currency exchange rate, select the consolidation period and currency, enter the rates, and click to save changes.

**How do you import exchange rates?**
To import exchange rates, access the Import Exchange Rates page, select the file type, upload the file, and transfer the data into the database.

**How do you export exchange rates?**
To export exchange rates, access the Export Exchange Rates page, select the consolidation period and file type, specify parameters, and click to export the rates.

**How do you add a company in the Companies page?**
To add a company, click the add icon on the Companies page, enter the required information, and save.

**How do you manage direct relationships among entities on the Group Structure page?**
On the Group Structure page, manage direct relationships by entering and updating the consolidation method and shareholding details.

**How do you create a new local adjustment?**
To create a new local adjustment, click the add icon on the Local Adjustments View page, enter the required information on the Manual Input page, and save.

**How do you modify a local adjustment?**
To modify a local adjustment, select the adjustment on the Local Adjustments View page, click the edit icon, make changes on the Manual Input page, and save.

**How do you manage flows on the Flow Management page?**
On the Flow Management page, select options to book differences, set flows to zero, merge companies, recalculate specific flows, or update historical rates.

**How do you generate an import data report?**
To generate an import data report, select the accounts and companies, enter the Calc Account code, sort order, data type, and output file type, then click to generate the report.

**How do you change your application language?**
To change your application language, go to the User Settings page through your Profile icon, select a new language from the drop-down, and click to confirm.

**How do you show or hide the Pie chart on the Workflow page?**
To show or hide the Pie chart, click the Show/Hide the Pie Chart icon on the Workflow page.

**How do you export tasks to Excel?**
To export tasks to Excel, click the Export to Excel icon on the Workflow page, select the task list, and click to export.

**How do you update the status of a task to 'In progress'?**
Select the company and task, change the status to 'In progress' in the Task details panel, and click to save.

**How do you reject a task in the Workflow page?**
To reject a task, select the company and task, change the status to 'Rejected' in the Task details panel, add comments, and click to confirm.

**How do you unlock data in a locked period?**
To unlock data, go to the Define Period Locking page, clear the lock date in the Data Locking Date field, and click to confirm.

**How do you import currency exchange rates?**
To import currency exchange rates, access the Import Exchange Rates page, select the file type, upload the file, and transfer the data into the database.

**How do you export currency exchange rates?**
To export currency exchange rates, access the Export Exchange Rates page, select the consolidation period, file type, and click to export. A download link will appear for viewing.

**How do you add a company on the Companies page?**
To add a company, click the add icon, enter the required information such as currency code, consolidation method, and group percentage, then save.

**How do you enter shareholding details on the Group Structure page?**
Use the Shareholders tab to enter the number of shares held by other companies in the group and the Participations tab for shares held in other companies.

**How do you book differences on the Flow Management page?**
To book differences, select the options for booking differences on flows and provide the required information, then click to save.

**How do you set a threshold on the Intercompany Matching page?**
To set a threshold, enter the threshold amount in the field provided, specify the amounts for different rules, and save.

**How do you correct intercompany details?**
To correct intercompany details, search for the account, enter the correction amount in group or local currency, and save the changes.

**How do you print intercompany differences or matched transactions?**
To print intercompany differences or matched transactions, select companies and criteria, choose file type, and generate the report.

**How do you set up automatic intercompany eliminations?**
To set up automatic intercompany eliminations, select the account, choose the elimination rule, and save the settings.

**How do you generate an IC validation report?**
To generate an IC validation report, select companies and partner companies, choose rules, apply filters, and generate the report.

**How do you generate a consolidation event?**
To generate a consolidation event, select the event and company, display the list of events, select events to generate, and confirm adjustments.

**How do you create custom events?**
To create custom events, enter details such as code, name, and description, define criteria and parameters, save the event, and execute as needed.

### General

**What can you do on the Workflow page?**
On the Workflow page, you can view and manage tasks, set preferences, export tasks to Excel, and update task statuses.

**What information is shown in the Pie chart on the Workflow page?**
The Pie chart shows the status and count of tasks, with different colors representing different statuses.

**What information is displayed on the Status Board?**
The Status Board displays company data entry status, including warnings, errors, validation status, and confirmation status.

**What can you do in the Document Repository?**
In the Document Repository, you can view, download, upload, and manage documents based on your access rights.

**What functions are available on the Local Adjustments Manual Input page?**
Functions include multiply/divide for efficient reporting, along with entering general adjustment-related information.

**What can you do in the Documents Repository?**
In the Documents Repository, you can view, download, upload, refresh, and delete files, depending on your access rights.

**What can you do on the Local Adjustments Manual Input page?**
On the Local Adjustments Manual Input page, you can enter general adjustment-related information, account codes, debit/credit amounts, and use functions like multiply/divide.

**What information is displayed on the User Settings page?**
The User Settings page displays your profile, consolidation periods including their codes, reference period codes, names, and options to change application or data languages.

**How can you filter the list of consolidation periods?**
You can filter the list of consolidation periods using wildcards like ? and * to narrow down the list based on criteria such as year, nature, or sequence.

**What options are available in the Task list field on the Workflow page?**
The Task list field on the Workflow page contains a list of tasks assigned to the task owner, and selecting a task shows individual tasks in the chart below.

**How can you set your preferences on the Workflow page?**
You can set your preferences on the Workflow page by controlling the display of the Gantt chart, Pie chart, or Companies list.

**What actions can you perform on the Status Board?**
On the Status Board, you can generate status reports, run validation rules, review error details, and update data entry status.

**What happens when you lock a data type?**
Locking a data type prevents modifications to the selected data type for that period across all companies within the group.

**What additional information can be added to companies?**
Additional information such as VAT numbers can be added through the Companies Additional Info page.

**What information is entered on the Local Adjustments Manual Input page?**
On the Local Adjustments Manual Input page, enter general adjustment-related information such as company, journal, behavior, attachment, account codes, and debit/credit amounts.

**What additional functions are available on the Local Adjustments Manual Input page?**
Additional functions on the Local Adjustments Manual Input page include multiply/divide for efficient reporting.

**What amounts are displayed on the Analytical Dimensions page?**
Amounts displayed include Adjusted amount, Local amount, Justified amount, and Difference to justify.

**What can you customize on the User Settings page?**
On the User Settings page, you can customize your profile, change your language settings, and select your working consolidation period.

**What information does the Status Board display?**
The Status Board displays company data entry status, including company code, name, modified date and time, number of warnings and errors, validation status, and data entry status.

**What actions can you perform in the Document Repository?**
In the Document Repository, you can view files, download files, upload files, refresh folder content, delete files, and manage documents based on your access rights.

**What information is shown in the Period Code panel on the Exchange Rates page?**
The Period Code panel on the Exchange Rates page shows a list of all consolidation periods, including their codes and names.

**What options are available for resetting flow values?**
Options for resetting flow values include setting all flows to zero, setting only selected flows to zero, and setting all flows except specific ones to zero.

**What options are available for viewing validation rules?**
Options for viewing validation rules include All, Errors, and Warnings, to display rules processed successfully, with errors, or with warnings.

**What information is displayed on the left-side panel of the Intercompany Matching page?**
The left-side panel displays details on intercompany matching/unmatching transactions, including company codes, names, local currency, accounts, journals, entries, descriptions, and amounts.

**What are the types of adjustments available for intercompany differences?**
Types of adjustments include Transfer Difference, Reclassify Difference, and Book Difference.

**What are IC Rules?**
IC Rules are intercompany rules that manage transactions between companies during consolidation.

**What are custom events in consolidation?**
Custom events are tailored adjustments created to address specific consolidation needs.

### Navigation

**How can you access the User Settings page?**
To access the User Settings page, click the Profile icon or the Current or Reference consolidation period on top of any page.

**How can administrators manage user access to folders in the Document Repository?**
Administrators can specify user access and permissions to folders in the Document Repository.

**How do you access the Document Repository?**
To access the Document Repository, click Reports > Document Repository.

---

*Help Topic 0332 | Category: Validation | Last Updated: 2024-12-03*