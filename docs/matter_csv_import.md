# Matter CSV import

Firm administrators can import matters from the Cases page using **Import CSV**. The import is restricted to the authenticated active firm; a request cannot select another firm.

## Limits and behavior

- UTF-8 CSV, with or without a BOM.
- Comma or semicolon delimiter.
- Maximum file size: 1 MB.
- Maximum data rows: 500.
- All rows are parsed and validated before any matter is written. A malformed row rejects the entire import.
- Duplicate matters within the file and matters already in the firm are skipped. Re-importing the same file is idempotent.
- Multiple matters can share one client profile. A missing client profile is created from the supplied client name.
- Each imported matter is assigned to the importing firm administrator as its initial case lead.
- The audit event records only created/skipped counts; it does not record matter titles or client names.

## Supported columns

The title column is required. Other columns are optional.

| English header | Accepted Arabic header examples |
|---|---|
| `title`, `case_title`, `matter`, `matter_title` | `عنوان القضية`, `عنوان الدعوى` |
| `client`, `client_name` | `اسم العميل`, `اسم العميل/الشركة` |
| `stage`, `case_stage` | `نوع القضية`, `المرحلة` |
| `case_number`, `number` | `رقم القضية`, `رقم الدعوى` |
| `case_year`, `year` | `السنة`, `سنة القضية` |
| `court` | `المحكمة` |
| `circuit` | `المحكمة/الدائرة`, `الدائرة` |
| `opposing_party`, `opposing party`, `opponent` | `الخصم`, `الطرف المقابل` |

## Example

```csv
title,client,stage,case_number,case_year,court,circuit,opposing_party
Employment claim,Example Client,Labour,100/2025,2025,Cairo Court,Labour Circuit,Example Employer
Contract dispute,Example Client,Civil,101/2025,2025,Cairo Court,Civil Circuit,Example Supplier
```

For Excel workbooks, save the worksheet as **CSV UTF-8** before importing. Native XLSX upload is not currently supported. Review the import summary and open the imported matters to confirm client linkage and case metadata.
