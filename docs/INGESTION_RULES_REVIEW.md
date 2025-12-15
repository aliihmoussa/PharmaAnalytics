# Ingestion Rules Review - Complete List

## Overview
This document lists ALL rules, validations, filters, and transformations applied during Excel file ingestion.

**Goal**: Review and simplify to preserve maximum data (805,930 records in 2019 file)

---

## 1. Column Mapping Rules

### Field Mappings (schema.py)
| Original Column | Mapped To | Notes |
|----------------|-----------|-------|
| DOC | doc_id | Required (Integer) |
| LINE | line_number | Optional (Integer) |
| CAT | drug_category | Optional (Integer) |
| C.R | consuming_dept | Optional (Integer) |
| DATE | transaction_date | Required (Date) |
| MOV # | movement_number | Required (Integer) |
| MOV DES | movement_description | Optional (String) |
| CODE | drug_code | Required (String) |
| ARTICLE | drug_name | Required (String) |
| M | m_field | Optional (String) |
| C.S | supplying_dept | Optional (Integer) |
| QTY | quantity | Required (Integer) |
| U.P | unit_price | Required (Numeric) |
| T.P | total_price | Required (Numeric) |
| AD DATE | admission_date | Optional (Date) |
| R | room_number | Optional (Integer) |
| U | bed_number | Optional (String) - Now supports A/B/numbers |
| AGE | patient_age | Optional (String) |

**Variations Handled:**
- 'MOV #' vs 'MOV#' (with/without space)
- Case-insensitive matching
- Column name variations

---

## 2. Excel Cleaning Rules (clean_excel_dataframe)

### Rule 1: Remove Completely Empty Rows
- **Action**: Filter out rows where ALL values are null
- **Impact**: Removes truly empty rows
- **Keep**: ✅ (Necessary)

### Rule 2: Strip Whitespace
- **Action**: Strip whitespace from all string columns
- **Impact**: Cleans data, no data loss
- **Keep**: ✅ (Necessary)

### Rule 3: Convert Empty Strings to Null
- **Action**: Convert empty strings ("") to NULL
- **Impact**: Standardizes null representation
- **Keep**: ✅ (Necessary)

---

## 3. Data Type Coercion Rules (coerce_data_types)

### Date Fields

#### AD DATE Cleaning
- **Rule**: Detect corrupted values like "7412 00/00/00" (T.P value + invalid date)
- **Action**: Set to NULL if corrupted pattern detected
- **Impact**: Preserves records, sets invalid dates to NULL
- **Keep**: ✅ (Necessary - prevents invalid dates)

#### DATE (transaction_date) Standardization
- **Rule**: Parse dates in formats: DD/MM/YY, DD/MM/YYYY, YYYY-MM-DD
- **Action**: Convert to datetime, return None if invalid
- **Impact**: Standardizes date format
- **Keep**: ✅ (Necessary)

### Integer Fields
- **Fields**: LINE, CAT, C.R, MOV #, C.S, QTY, R
- **Rule**: Cast to Int64 (strict=False allows nulls)
- **Impact**: Type conversion, preserves nulls
- **Keep**: ✅ (Necessary)

### Special Fields

#### DOC (doc_id) Normalization
- **Rule**: Convert to integer, extract numeric part if string
- **Action**: Try int conversion, extract digits if needed, return None if fails
- **Impact**: May filter records if doc_id cannot be extracted
- **Review**: ⚠️ (Should preserve original value if not numeric?)

#### Bed Number (U) Normalization
- **Rule**: Convert Arabic letters (أ→A, ب→B), preserve numbers
- **Action**: Map Arabic to English, keep numbers as strings
- **Impact**: Preserves all bed numbers
- **Keep**: ✅ (Necessary)

### Float Fields
- **Fields**: U.P, T.P, unit_price, total_price
- **Rule**: Extract numeric values, cast to Float64
- **Impact**: Type conversion
- **Keep**: ✅ (Necessary)

---

## 4. Data Validation Rules (validate_data_integrity)

### Required Field Validation
- **Fields Checked**: DOC/doc_id, DATE/transaction_date, MOV #/movement_number, CODE/drug_code, ARTICLE/drug_name, QTY/quantity, U.P/unit_price, T.P/total_price
- **Rule**: Filter out records where ANY required field is null
- **Impact**: HIGH - May filter many records
- **Review**: ⚠️ **CRITICAL** - This is likely filtering out all records!

### Date Range Validation
- **Rule**: Filter dates outside 2010-2030 range
- **Fields**: DATE/transaction_date (required), AD DATE/admission_date (optional)
- **Action**: 
  - Required dates: Filter records
  - Optional dates: Set to NULL (don't filter)
- **Impact**: May filter records with invalid dates
- **Review**: ⚠️ Check if date parsing is working correctly

### Quantity Validation
- **Rule**: Filter out records where quantity = 0
- **Impact**: Removes zero-quantity records
- **Keep**: ✅ (Database constraint requires this)

### Suspicious Pattern Detection (Logging Only)
- **Rule**: Detect very high quantities (>10,000) or prices (>100,000)
- **Action**: Log warning, don't filter
- **Keep**: ✅ (Information only)

---

## 5. Data Consistency Rules (verify_data_consistency)

### Price Consistency
- **Rule**: Verify total_price = unit_price × quantity
- **Action**: Auto-correct mismatches (tolerance ±0.01)
- **Impact**: Fixes data errors, no data loss
- **Keep**: ✅ (Helpful)

### Age Normalization
- **Rule**: Extract numeric age from Arabic text (e.g., "25 سنة", "ب 0000/00/00")
- **Action**: Extract first number, remove Arabic words, handle corrupted formats
- **Impact**: Preserves age data
- **Keep**: ✅ (Necessary)

### Date Consistency Check (Logging Only)
- **Rule**: Check if admission_date > transaction_date
- **Action**: Log warning, don't filter
- **Keep**: ✅ (Information only)

---

## 6. Transformation Rules (prepare_for_database)

### Column Name Transformation
- **Rule**: Transform column names if original names exist
- **Action**: Map DOC→doc_id, CODE→drug_code, etc.
- **Impact**: Standardizes column names
- **Keep**: ✅ (Necessary)

### Required Field Filtering
- **Fields**: doc_id, transaction_date, movement_number, drug_code, drug_name, quantity
- **Rule**: Filter out records where ANY required field is null
- **Impact**: HIGH - Duplicate of validate_data_integrity
- **Review**: ⚠️ **DUPLICATE** - This is redundant!

### Zero Quantity Filtering
- **Rule**: Filter out records where quantity = 0
- **Impact**: Duplicate of validate_data_integrity
- **Review**: ⚠️ **DUPLICATE** - This is redundant!

---

## 7. Derived Field Calculation

### Total Price Calculation
- **Rule**: Calculate total_price = unit_price × quantity if missing
- **Action**: Auto-calculate, no filtering
- **Impact**: Fills missing values
- **Keep**: ✅ (Helpful)

---

## 8. Database Insertion Rules

### COPY Method Validation
- **Rule**: Validate doc_id and movement_number before insertion
- **Action**: Skip records with null doc_id or movement_number
- **Impact**: Final safeguard
- **Keep**: ✅ (Necessary)

### SQLAlchemy Fallback Validation
- **Rule**: Same validation as COPY method
- **Action**: Skip records with null doc_id
- **Impact**: Final safeguard
- **Keep**: ✅ (Necessary)

---

## Summary of Filtering Points

### Records Are Filtered At:

1. **clean_excel_dataframe**: Remove completely empty rows ✅
2. **validate_data_integrity**: 
   - Required fields null ❌ (MAJOR ISSUE)
   - Date out of range ❌ (May be too strict)
   - Quantity = 0 ✅ (Database constraint)
3. **prepare_for_database**: 
   - Required fields null ❌ (DUPLICATE - REDUNDANT!)
   - Quantity = 0 ❌ (DUPLICATE - REDUNDANT!)
4. **Database insertion**: Final validation ✅

---

## Issues Identified

### 🔴 CRITICAL ISSUES

1. **Duplicate Filtering**: `validate_data_integrity` and `prepare_for_database` both filter the same fields
2. **Required Field Validation Too Strict**: May be filtering valid records if column mapping fails
3. **Date Validation**: May filter records if date parsing fails

### ⚠️ POTENTIAL ISSUES

1. **Column Name Matching**: May not match if Excel has different column names
2. **doc_id Normalization**: Returns None if not numeric, causing filtering
3. **Date Range**: 2010-2030 may be too restrictive

---

## Recommendations

### Immediate Actions:

1. **Remove duplicate filtering** in `prepare_for_database` (already done in `validate_data_integrity`)
2. **Make required field validation more lenient** - only filter truly critical fields
3. **Add better column name matching** - handle variations
4. **Preserve doc_id as string** if not numeric (or extract better)
5. **Log all filtering reasons** for debugging

### Fields That Should NEVER Be Filtered:

- Optional fields: line_number, cat, consuming_dept, movement_description, m_field, supplying_dept, admission_date, room_number, bed_number, patient_age

### Fields That Can Be Filtered (Database Constraints):

- doc_id: Required, but should extract better
- transaction_date: Required, but should parse better
- movement_number: Required
- drug_code: Required
- drug_name: Required
- quantity: Required, and cannot be 0 (database constraint)
- unit_price: Required
- total_price: Required (can be calculated)

---

## Next Steps

1. Review this document
2. Decide which rules to keep/remove
3. Simplify the code to preserve more data
4. Test with sample data

