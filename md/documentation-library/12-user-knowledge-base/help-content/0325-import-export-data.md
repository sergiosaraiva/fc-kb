# Import export data

## Metadata
- **Index**: 0325
- **Topics**:  Data Import and Export, Mapping Tables, Adjustments, Data Reporting
- **Keywords**:  Import Data, Export Data, Mapping Tables, Adjustments, File Structure, Data Report, CSV, Excel, HUB, Validation, Overwrite, Parameters, Journal, Period

## Summary

 The provided documentation for the Financial Consolidation product includes comprehensive instructions on importing and exporting data, defining mapping tables, managing adjustments, and generating data reports. The Data Import and Export sections explain how to handle different file structures, specify import/export parameters, and validate data quality. The Mapping Tables section details how to define and manage mappings between source and target data structures. The Adjustments section covers importing and exporting adjustment data, specifying file types, and setting overwrite options. The Data Reporting section provides steps to generate import data reports, detailing account and company selections, sorting options, and output formats.

---

## User Guide

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

---

## Frequently Asked Questions

### General

**What are mapping tables used for in financial consolidation?**
Mapping tables establish relationships between different sets of data, defining how data from the source system should be transformed and mapped to the target system.

**What structures can be used to create mapping tables?**
The structures available for creating mapping tables include Accounts, Companies, Dimension Groups, Dimension Detail Codes, and Flows.

**How can you import data into the Financial Consolidation application?**
To import data, go to Transfers > Data > Import Data, select a structure from the File Structure drop-down list, upload the file, fill in the parameters, and specify the data type to overwrite. Options include discarding errors and replacing imported types and accounts.

**What options are available when importing adjustments?**
Options for importing adjustments include selecting the file type (CSV, Excel, HUB), specifying Sheet Name, CSV Separator, Decimal Separator, Thousand Separator, and setting overwrite options before uploading the file.

**What details are shown in the parameters of a mapping table?**
The parameters of a mapping table include Code, Name, Period, Created by, Modified by, Created On, and Modified On. These details help track and manage the mapping table.

**What general properties can you specify for an import file structure?**
General properties for an import file structure include file ID, Type of Amount (Net Amounts, Debit/Credit amounts), file type (XLS, CSV, HUB), and additional options like summarizing Interco, signed amounts, calculating profit, and scale of amounts.

**What options are available for defining an export file structure?**
Options for defining an export file structure include specifying the Type of Amount (Net Amounts, Debit/Credit amounts), file type (XLS, CSV, HUB), and additional options and parameters for data transformation.

**What parameters can you set when importing adjustments?**
When importing adjustments, you can specify parameters like file type (CSV, Excel, HUB), Sheet Name, CSV Separator, Decimal Separator, Thousand Separator, and overwrite options. Upload the file and start the import.

**How can I export consolidated data from the Financial Consolidation application?**
To export consolidated data, go to Transfers > Data > Export Data, select the consolidation period, file structure (XLS, CSV, HUB), and parameters. Select the data to export, including local amounts, contribution, and consolidated amounts.

**How can I define mapping tables in the Financial Consolidation application?**
To define mapping tables, go to Transfers > Data > Define Mapping Tables. You can create mappings for Accounts, Companies, Dimension Groups, Dimension Detail Codes, and Flows by specifying the Code, Name, and mapping details.

**What information is displayed on the Define Mapping Tables page?**
The Define Mapping Tables page displays a list of available mapping tables with their Code and Name. The right-side panel shows parameters like Code, Name, Period, Created by, Modified by, Created On, and Modified On for the selected mapping.

**How can I duplicate an existing mapping table?**
To duplicate a mapping table, select an existing table, click the duplicate button, enter the new Code and Name, select a different Period if needed, and save the new mapping table.

**How can I import data into the Financial Consolidation application?**
To import data, go to Transfers > Data > Import Data, select a structure from the File Structure drop-down list, upload the file, fill in the parameters, and specify the data type to overwrite. Options include discarding errors, replacing imported types, and accounts.

**What parameters can you specify when importing adjustments?**
When importing adjustments, you can specify parameters like file type (CSV, Excel, HUB), Sheet Name, CSV Separator, Decimal Separator, Thousand Separator, and overwrite options. Upload the file and start the import.

**How can you import data using the Import Data page?**
To import data, select a structure from the File Structure drop-down list, upload the file, expand the Details section, fill in the parameters, and specify the data type to overwrite. Options include discarding errors and replacing imported types and accounts.

**How can you export consolidated data?**
To export consolidated data, select the consolidation period, file structure (XLS, CSV, HUB), and parameters. Choose the data to export, including local amounts, contribution, and consolidated amounts, then click to download.

**What information is displayed for each mapping table?**
For each mapping table, the information displayed includes Code, Name, Period, Created by, Modified by, Created On, and Modified On. These details help manage the mapping table effectively.

**What general properties can be specified for an import file structure?**
General properties for an import file structure include file ID, Type of Amount (Net Amounts, Debit/Credit amounts), file type (XLS, CSV, HUB), and additional options like summarizing Interco, signed amounts, calculating profit, and scale of amounts.

**What options can be defined in an export file structure?**
Options for an export file structure include specifying the Type of Amount (Net Amounts, Debit/Credit amounts), file type (XLS, CSV, HUB), and additional options and parameters for data transformation.

**What details are shown for each mapping table?**
Details shown for each mapping table include Code, Name, Period, Created by, Modified by, Created On, and Modified On. These details help track and manage the mapping table effectively.

**What parameters can be set when importing adjustments?**
Parameters include file type (CSV, Excel, HUB), Sheet Name, CSV Separator, Decimal Separator, Thousand Separator, and overwrite options. Then upload the file and start the import.

### Navigation

**How do you access the Define Mapping Tables page?**
To access the Define Mapping Tables page, click Transfers > Data > Define Mapping Tables. The page allows you to define and manage mapping tables for various structures.

### How-To

**How do you map an item in a mapping table?**
To map an item, click on the code in the Target table, enter a Code to identify the item on the source mapping table, add a Mapping Factor (optional), and a Description. Click to add the item to the Source table.

**What are the steps to create an export file structure?**
To create an export file structure, specify general export file properties, type of data, export options, and parameters. Enable export rules to transform the exported data.

**How do you export adjustment data to an external system?**
To export adjustment data, go to Transfers > Adjustments > Export Adjustments, select the consolidation period, file type (XLS, CSV, HUB), and parameters. Choose the companies and journal types to export, then download the data.

**What are the steps to export consolidated data?**
To export consolidated data, go to Transfers > Data > Export Data, select the consolidation period, file structure (XLS, CSV, HUB), and parameters. Select the data to export, including local amounts, contribution, and consolidated amounts.

**How do you create a new mapping table?**
To create a new mapping table, click the add button on the Define Mapping Tables page, enter the Code and Name, select a structure (Accounts, Companies, Flows, Dimension Groups, or Dimension Detail Codes), and map items by entering a Code and Description.

**How do you filter items in a mapping table?**
To filter items in a mapping table, use the options to display items With Source Only (with mapping data) or Without Source Only (without mapping data). This helps focus on specific items during mapping.

**How do you enable import rules for data transformation?**
To enable import rules, specify the parameters and mapping tables for the import file structure. Use functions like Substr, Merge, Prefix, Suffix, and Fix to transform the imported data according to the rules.

**How do you import data into the Financial Consolidation application?**
To import data, select a structure from the File Structure drop-down list, upload the file, fill in the parameters, and specify the data type to overwrite. Options include discarding errors and replacing imported types and accounts.

**How do you export adjustment data?**
To export adjustment data, go to Transfers > Adjustments > Export Adjustments, select the consolidation period, file type (XLS, CSV, HUB), and parameters. Select the companies and journal types to export, then download the data.

**How do you generate an import data report?**
To generate an import data report, go to Transfers > Data > Import Data Report, select accounts and companies, enter a Calc Account code, choose sort order, data type, and output file type (PDF, XLS, XLSX), then click to generate.

**How do you define an import file structure?**
To define an import file structure, go to Transfers > Data > Define File Structure, select Import, and specify file properties like Type of Amount, file type (XLS, CSV, HUB), and parameters. Map columns to attributes and enable import rules for data transformation.

**What steps should I follow to define an export file structure?**
To define an export file structure, go to Transfers > Data > Define File Structure, select Export, specify general properties like Type of Amount, file type (XLS, CSV, HUB), and parameters. Enable export rules to transform the exported information.

**How do you import bundle data into the Financial Consolidation application?**
To import bundle data, go to Transfers > Data > Import Data, select a structure from the File Structure drop-down list, upload the file, fill in the parameters, and specify the type of data to overwrite during import.

**How do you export adjustments from the Financial Consolidation application?**
To export adjustments, go to Transfers > Adjustments > Export Adjustments, select the consolidation period, file type (XLS, CSV, HUB), and parameters. Choose the companies and journal types to export, then download the data.

**How do mapping tables ensure data consistency?**
Mapping tables ensure data consistency by defining how data from the source system should be transformed and mapped to the target system, aligning data structures and formats between systems.

**What steps are involved in creating a mapping table?**
To create a mapping table, click the add button, enter the Code and Name, select a structure (Accounts, Companies, Flows, Dimension Groups, or Dimension Detail Codes), and map items by entering a Code and Description for each item.

**How do you enable import rules for transforming data?**
Enable import rules by specifying the parameters and mapping tables for the import file structure. Use functions like Substr, Merge, Prefix, Suffix, and Fix to transform the imported data according to the rules.

**How do you export adjustment data from the Financial Consolidation application?**
To export adjustment data, select the consolidation period, file type (XLS, CSV, HUB), and parameters. Choose the companies and journal types to export, then click to download the data.

**How do mapping tables ensure data alignment?**
Mapping tables ensure data alignment by defining how data from the source system should be transformed and mapped to the target system, ensuring consistency and accuracy during import and export.

**What steps are required to create a new mapping table?**
To create a new mapping table, click the add button, enter the Code and Name, select a structure (Accounts, Companies, Flows, Dimension Groups, or Dimension Detail Codes), and map items by entering a Code and Description for each item.

**How do you filter items during mapping?**
To filter items during mapping, use the options to display items With Source Only (with mapping data) or Without Source Only (without mapping data). This helps in managing and focusing on specific items.

### Concepts

**What is the process for defining an import file structure?**
To define an import file structure, specify general file properties, type of data, import options, and parameters. Map the columns to attributes and enable import rules to transform the imported data.

**What is the purpose of the Import Data Report page?**
The Import Data Report page is used to generate reports of data (ledger accounts) imported into the Financial Consolidation application. Select accounts and companies, enter a Calc Account code, choose sort order, data type, and output file type (PDF, XLS, XLSX).

**What is the role of mapping tables in data import and export?**
Mapping tables define how data from the source system should be transformed and mapped to the target system, ensuring data consistency and accuracy during import and export.

**What is the process for generating an import data report?**
To generate an import data report, go to Transfers > Data > Import Data Report, select accounts and companies, enter a Calc Account code, choose sort order, data type, and output file type (PDF, XLS, XLSX), then click to generate the report.

---

*Help Topic 0325 | Category: Data Entry | Last Updated: 2024-12-03*