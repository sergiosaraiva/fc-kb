# Pivot Reports

## Metadata
- **Index**: 0394
- **Topics**:  Pivot Report Creation, Pivot Report Configuration, Data Analysis, Report Generation
- **Keywords**:  Pivot Report, Data Analysis, Report Configuration, Financial Data, User Reports, OLAP Export, Drill Analysis

## Summary

 The provided documentation for the Financial Consolidation product includes detailed instructions on creating and running pivot reports. The Pivot Report Creation section explains how to define and configure pivot reports, allowing for detailed data analysis and customization. The Run Pivot Reports section details the process of running and interacting with pivot reports, including options for filtering, sorting, and saving reports. These instructions ensure users can efficiently create and analyze pivot reports for comprehensive financial insights.

---

## User Guide

Create a pivot report
The Define Pivot Reports page offers the functionality to create a new code for a pivot report and define its configuration settings. This allows you to customize the pivot report according to your specific needs and requirements. Pivot reports offer the functionality to drill into the database, allowing you to explore the underlying data in more detail. These reports are built upon user reports, meaning that user reports are a prerequisite for defining a new pivot report.

To access the Define Pivot Reports page, click Reports > Pivot Reports > Define Pivot Reports.

The left-side panel displays a list of existing report definitions. You can select and modify an existing report. The right-side panel is the report definition area.

Duplicate a report:
1. On the left-side panel, select the report you want to duplicate and click .
2. In the Code field, enter a unique code.
3. Optionally, modify any or all of the other fields as needed.
4. Click .

Configure a pivot report:
1. Click .
2. Provide the following information in the fields:
- Code: Unique code to identify your definition on the list.
- Description: Text describing the use of the report.
- Type: Type of the custom report to use, for example, Closing, Flows, Dimensions, etc. Your selection impacts the content of the pivot.
- Custom Report: Code of the custom report to use. Only the accounts available directly or indirectly in the selected report type will be available in the pivot.
- Journal Summation: Journal to include in the output.
- POV1, POV2, POV3: If selected, the drop-down is activated and you can select a POV to include in the drill analysis.
- Cube Definitions: Links

the pivot to the output of an OLAP export in order to get better performance re-using previously processed data.
- Public: If selected, the report will be available for all users. Otherwise, the report is available for the current user only.
3. Click .
4. Click to open the Run Reports page where you actually generate the Pivot report.

Run pivot reports
The Run Reports page is where you actually run the reports that you configure on the Define Pivot Reports page. Pivot reports allow you to perform your own analysis from the bundle adjusted level to the consolidation data. You can drag and drop fields from the filter area to the row, the column, and the data area. Like in an Excel pivot table, you can select any dimension from the list in the filter section of the page, and put it in row or column and apply filters to that dimension. By adding dimensions, you can see the underlying elements that have impacted the final result displayed in some reports. The figures in the report are refreshed each time the data is updated in Financial Consolidation. You can save your pivot report in order to reuse it; and export it in an Excel format.

To access the Run Reports page, click Reports > Pivot Reports > Run Pivot Reports.

You can also access the Run Reports page when you click or on the Define Pivots Reports page.

Run a pivot report:
1. Select a report from the Choose your report field. Reports configured on the Define Pivot Reports page are listed in the drop-down.
2. From the All panel, drag fields to the Row panel, Column panel, or Data panel to split the figures.
3. For each of the dimensions you selected, you can click to display a drop-drop list that includes a Search function and selection options. Use the Search function to limit the data displayed. For example, to see account numbers beginning with 13, enter 13 in the Search field and press enter.
4. You have these options to view the selected dimensions:
- To see the dimension in a single field, click the arrow beside it to expand it.
- To see the selected dimension in all the fields, right-click on any of the fields and then select Expand All from the menu. To collapse the rows, right-click again and select Collapse All.
5. When you have finished defining the content, click . Saving your report allows you to reuse it. You can also click and save it with a different name.
6. Click . The report is generated and downloaded to your machine.

---

## Frequently Asked Questions

### Navigation

**How do you access the Define Pivot Reports page?**
To access the Define Pivot Reports page, click Reports > Pivot Reports > Define Pivot Reports.

**How do you access the right-side panel on the Define Pivot Reports page?**
Click on a report in the left-side panel to display its details in the right-side panel for modification.

### Concepts

**What is the purpose of the Define Pivot Reports page?**
The Define Pivot Reports page allows you to create a new code for a pivot report and define its configuration settings, enabling you to customize the pivot report according to your needs.

**What is the function of the POV fields when configuring a pivot report?**
The POV fields (POV1, POV2, POV3) allow you to select specific points of view to include in the drill analysis.

**What is the purpose of the Run Reports page?**
The Run Reports page is where you run the reports configured on the Define Pivot Reports page, allowing you to perform detailed data analysis from the bundle adjusted level to the consolidation data.

**What does configuring a pivot report allow you to do?**
Configuring a pivot report allows you to customize the report settings, including defining unique codes, descriptions, types, and other parameters to suit your specific analysis needs.

**What does the Cube Definitions field do when configuring a pivot report?**
The Cube Definitions field links the pivot to the output of an OLAP export for better performance by re-using previously processed data.

**What is the role of the Define Pivot Reports page?**
The Define Pivot Reports page allows you to create and configure pivot reports, enabling detailed data analysis and customization.

**What is the function of the Run Reports page?**
The Run Reports page allows you to run and interact with pivot reports, including filtering, sorting, and saving the reports for detailed data analysis.

**What is the benefit of using pivot reports in financial consolidation?**
Pivot reports allow for detailed data analysis, enabling you to explore underlying data and customize reports according to specific needs.

**What is the purpose of saving a pivot report?**
Saving a pivot report allows you to reuse the report configuration for future analysis without reconfiguring the settings.

**What is the benefit of the OLAP export link in a pivot report?**
Linking the pivot to an OLAP export improves performance by re-using previously processed data.

**What does the Public option do when configuring a pivot report?**
The Public option makes the report available to all users if selected. If not selected, the report is available only to the current user.

**What is the benefit of saving a pivot report configuration?**
Saving the configuration allows you to reuse the report setup for future analysis without needing to reconfigure the settings.

**What is the purpose of the right-side panel on the Define Pivot Reports page?**
The right-side panel displays the report definition area where you can configure the settings for a pivot report.

### General

**What can you do on the left-side panel of the Define Pivot Reports page?**
On the left-side panel, you can select and modify existing report definitions.

**What information do you need to provide when configuring a pivot report?**
When configuring a pivot report, provide a unique code, description, type, custom report code, journal summation, POV1, POV2, POV3 selections, cube definitions, and select if the report should be public.

**What can you do with the fields in the filter area on the Run Reports page?**
You can drag and drop fields from the filter area to the row, column, and data areas, similar to an Excel pivot table.

**What are the options for viewing dimensions on the Run Reports page?**
You can click the arrow beside a dimension to expand it, right-click and select Expand All to see all fields, or Collapse All to hide them.

**What types of custom reports can be selected when configuring a pivot report?**
You can select types such as Closing, Flows, Dimensions, etc., which impact the content of the pivot.

**What happens when you click on the Define Pivot Reports page?**
You can duplicate an existing report, modify the fields as needed, and save the new configuration.

**What options do you have after defining a pivot report?**
After defining a pivot report, you can save it, run it on the Run Reports page, and export the results.

**What can you do with the dimensions in a pivot report?**
You can expand, collapse, and filter dimensions to see the underlying elements impacting the final result.

**What should you do after configuring a pivot report?**
Click to save the configuration and open the Run Reports page to generate the pivot report.

**What options are available for expanding and collapsing dimensions in a pivot report?**
You can expand a single dimension field or right-click to select Expand All or Collapse All for multiple fields.

**What happens when you save a pivot report?**
The report configuration is saved, allowing you to reuse the report without reconfiguring the settings.

**How can you modify an existing pivot report?**
Select the report from the left-side panel on the Define Pivot Reports page, make changes in the right-side panel, and save the modifications.

**What types of analysis can be performed with pivot reports?**
Pivot reports allow for detailed data analysis, including filtering, sorting, and drilling into underlying data.

**What should you do after defining the content of a pivot report?**
Click to save the configuration and open the Run Reports page to generate the report.

### How-To

**How do you duplicate a pivot report?**
To duplicate a report, select the report you want to duplicate on the left-side panel, click , enter a unique code in the Code field, modify any other fields as needed, and click .

**How do you open the Run Reports page from the Define Pivot Reports page?**
After configuring the pivot report, click to open the Run Reports page.

**How do you run a pivot report?**
Select a report from the Choose your report field, drag fields from the All panel to the Row, Column, or Data panels, use the drop-down list to filter data, and click to run the report.

**How do you use the Search function in the dimension drop-down list on the Run Reports page?**
Click to display the drop-down list, use the Search function to limit the data displayed, and press enter to filter the results.

**How do you save a pivot report on the Run Reports page?**
After defining the content, click to save the report for reuse, or click and save it with a different name.

**How do you export a pivot report?**
Click to generate and download the report to your machine.

**How do you include a journal in the output of a pivot report?**
Select the Journal Summation field and choose the journal to include in the output.

**How do you make a pivot report public?**
Select the Public option to make the report available for all users. If not selected, the report is available for the current user only.

**How do you modify an existing report definition on the Define Pivot Reports page?**
Select the report from the left-side panel and make changes in the right-side panel.

**What are the steps to configure a new pivot report?**
Click , provide the necessary information (code, description, type, custom report, etc.), and click to save the configuration.

**How do you select a custom report for a pivot report?**
In the Custom Report field, enter or select the code of the custom report to use, which determines the accounts available in the pivot.

**How do you view the underlying data in a pivot report?**
By configuring the pivot report to drill into the database, you can explore the underlying data in more detail.

**How do you generate a pivot report?**
On the Run Reports page, select the report, drag fields to the desired panels, apply filters, and click to generate the report.

**How do you refresh the figures in a pivot report?**
The figures in the pivot report are refreshed each time the data is updated in Financial Consolidation.

**How do you duplicate an existing pivot report?**
Select the report to duplicate, click , enter a unique code, modify fields as needed, and save the new report.

**How do you select a POV for drill analysis in a pivot report?**
Select a POV in the POV1, POV2, or POV3 fields to include it in the drill analysis.

**How do you customize a pivot report to meet specific needs?**
Enter the necessary configuration settings such as code, description, type, custom report, and other parameters to customize the pivot report.

**How do you interact with fields on the Run Reports page?**
Drag fields from the All panel to the Row, Column, or Data panels, and use the drop-down list to filter data.

**How do you search for specific data in a pivot report?**
Use the Search function in the drop-down list to limit the data displayed based on specific criteria.

**How do you export a pivot report to Excel?**
Click on the Run Reports page to generate and download the report in Excel format.

**How do you create a new pivot report?**
On the Define Pivot Reports page, click , provide the required information, and save the new report configuration.

**How do you filter data in a pivot report?**
Use the drop-down list in the dimension fields to apply filters and limit the data displayed.

**How do you generate a report after configuring it?**
On the Run Reports page, select the report, drag fields to the desired panels, and click to generate the report.

**What are the steps to configure a pivot report?**
Click , provide the necessary details (code, description, type, etc.), and save the configuration.

**How do you configure a pivot report to include specific points of view?**
Select POV1, POV2, or POV3 fields to include specific points of view in the drill analysis.

**How do you expand a single dimension field in a pivot report?**
Click the arrow beside the dimension field to expand it and see the underlying elements.

**How do you save a pivot report with a different name?**
Click on the Run Reports page, then click and enter a new name to save the report configuration with a different name.

**How do you expand and collapse all fields in a dimension?**
Right-click on any field in the dimension and select Expand All to expand or Collapse All to collapse the rows.

**How do you configure the settings for a new pivot report?**
On the Define Pivot Reports page, click , provide the required information, and save the configuration settings for the new report.

---

*Help Topic 0394 | Category: Reporting | Last Updated: 2024-12-03*