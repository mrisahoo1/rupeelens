# Parser Guide

Parsers return normalized transaction candidates with raw description, date, amount, direction, reference ID, source type, and payment mode. The pipeline cleans merchant strings, applies rule categorization, detects refunds, detects card payments/transfers, computes a duplicate hash, and stores preview rows in an import batch until confirmation.

Supported MVP inputs: CSV, XLS, XLSX, PDF text extraction, and manual templates. Unknown columns are inferred using common names such as date, description, merchant, debit, credit, amount, type, and reference.
