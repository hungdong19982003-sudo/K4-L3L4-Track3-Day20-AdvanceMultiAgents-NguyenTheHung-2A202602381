---
name: acme-data-conventions
description: Use when processing tabular sales or transaction data to comply with Acme data standards.
---
1. Record monetary values in answer.json as integer cents (e.g. 1606.67 USD is written 160667).
2. Include a 'meta' object in answer.json with source filename, rows_in (total input rows), and rows_used (distinct valid records with known amounts).
3. Export cleaned data to clean.csv with canonical columns, UTC ISO-8601 timestamps, standardized categories/regions, and amounts in integer cents.
