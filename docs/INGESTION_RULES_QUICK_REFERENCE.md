# Ingestion Rules - Quick Reference

## Column Mappings (Excel → Database)

| Excel Column | Database Field | Required? | Notes |
|-------------|----------------|-----------|-------|
| DOC | doc_id | ✅ Yes | Integer, extracted from string if needed |
| LINE | line_number | ❌ No | Integer |
| CAT | drug_category | ❌ No | Integer |
| C.R | consuming_dept | ❌ No | Integer |
| DATE | transaction_date | ✅ Yes | Date (DD/MM/YY format) |
| MOV # | movement_number | ✅ Yes | Integer |
| MOV DES | movement_description | ❌ No | String (may contain Arabic) |
| CODE | drug_code | ✅ Yes | String (uppercase) |
| ARTICLE | drug_name | ✅ Yes | String |
| M | m_field | ❌ No | String |
| C.S | supplying_dept | ❌ No | Integer |
| QTY | quantity | ✅ Yes | Integer, cannot be 0 |
| U.P | unit_price | ✅ Yes | Float |
| T.P | total_price | ✅ Yes | Float (can be calculated) |
| AD DATE | admission_date | ❌ No | Date (optional, corrupted values set to NULL) |
| R | room_number | ❌ No | Integer |
| U | bed_number | ❌ No | String (A/B/numbers preserved) |
| AGE | patient_age | ❌ No | String (age extracted from Arabic text) |

---

## Data Cleaning Rules

### 1. Excel Cleaning
- ✅ Remove rows where ALL values are null
- ✅ Strip whitespace from all string columns
- ✅ Convert empty strings ("") to NULL

### 2. Special Field Handling

#### doc_id (DOC)
- Extract integer from string if needed
- If extraction fails, set to NULL (record may be filtered)

#### bed_number (U)
- Convert Arabic letters: أ → A, ب → B
- Preserve numeric values as strings (e.g., "108", "112")
- If invalid, set to NULL (record preserved)

#### patient_age (AGE)
- Extract numeric age from Arabic text (e.g., "25 سنة" → 25)
- Remove invalid date patterns (e.g., "ب 0000/00/00")
- If no valid age found, set to NULL (record preserved)

#### admission_date (AD DATE)
- Detect corrupted values like "7412 00/00/00" (T.P value + invalid date)
- Set corrupted dates to NULL (record preserved)
- Parse valid dates in formats: DD/MM/YY, DD/MM/YYYY, YYYY-MM-DD

---

## Validation Rules (Records Filtered Here)

### Required Fields (Must Not Be Null)
If ANY of these are null, the record is filtered:
- doc_id
- transaction_date
- movement_number
- drug_code
- drug_name
- quantity
- unit_price
- total_price

### Date Range Validation
- transaction_date: Must be between 2010-01-01 and 2030-12-31
- admission_date: Invalid dates set to NULL (record preserved)

### Quantity Validation
- quantity: Cannot be 0 (database constraint)
- Negative quantities are preserved (returns, refunds)

---

## Data Preservation Rules

### Fields That Are NEVER Filtered
These fields are preserved even if null or invalid:
- line_number
- drug_category
- consuming_dept
- movement_description
- m_field
- supplying_dept
- admission_date (set to NULL if invalid)
- room_number
- bed_number (normalized but preserved)
- patient_age (normalized but preserved)

### Auto-Corrections (No Filtering)
- **Price Mismatches**: Auto-correct total_price = unit_price × quantity
- **Age Normalization**: Extract age from Arabic text
- **Date Standardization**: Convert dates to YYYY-MM-DD format

---

## Pipeline Steps

1. **Load Excel** (chunked processing)
2. **Excel Cleaning** (remove empty rows)
3. **Column Mapping** (DOC → doc_id, etc.)
4. **Type Coercion** (convert types, normalize dates)
5. **Validation** ⚠️ **ONLY FILTERING POINT**
6. **Consistency** (auto-correct prices, normalize age)
7. **Normalize** (normalize drug codes, dates)
8. **Prepare** (calculate derived fields)
9. **Insert** (batch insert to database)

---

## Common Issues & Solutions

### Issue: All Records Filtered (0 successful, 0 failed)
**Possible Causes:**
1. Column mapping failed (check logs for "No columns were mapped")
2. All required fields are null (check logs for null counts)
3. Date parsing failed (check logs for date validation errors)

**Solution:**
- Check logs for "Step 2 - Column mapping" - verify columns are mapped
- Check logs for "Step 4 - Validation" - see which fields are null
- Verify Excel file has correct column headers

### Issue: bed_number is Empty
**Possible Causes:**
1. Column 'U' not mapped correctly
2. Values are in unexpected format

**Solution:**
- Check logs for column mapping
- Verify Excel has 'U' column
- Check normalization logs

### Issue: patient_age is Empty
**Possible Causes:**
1. Column 'AGE' not mapped correctly
2. Age values are in unexpected format

**Solution:**
- Check logs for column mapping
- Verify Excel has 'AGE' column
- Check age normalization logs

### Issue: admission_date is Corrupted
**Expected Behavior:**
- Corrupted dates like "7412 00/00/00" are set to NULL
- Records are preserved (not filtered)
- This is correct behavior

---

## Log Messages to Watch For

### Good Signs ✅
```
Step 2 - Column mapping: X rows, mapped columns: [...]
Step 4 - Validation: All X records passed validation
Cleaning pipeline summary: All X records preserved
```

### Warning Signs ⚠️
```
Step 4 - Validation: Removed Y invalid records (Z%)
  - DOC_null: X records
  - DATE_null: Y records
```

### Critical Errors 🔴
```
CRITICAL: Required field group [...] not found in dataframe columns!
CRITICAL: All X records have null [field]!
No columns were mapped! Original columns: [...]
```

---

## Testing Commands

### Check Database Records
```sql
-- Total records
SELECT COUNT(*) FROM drug_transactions;

-- Records by bed_number
SELECT bed_number, COUNT(*) 
FROM drug_transactions 
WHERE bed_number IS NOT NULL 
GROUP BY bed_number 
ORDER BY COUNT(*) DESC;

-- Records with admission_date
SELECT COUNT(*) 
FROM drug_transactions 
WHERE admission_date IS NOT NULL;

-- Records with patient_age
SELECT COUNT(*) 
FROM drug_transactions 
WHERE patient_age IS NOT NULL;
```

### Check Ingestion Logs
```sql
SELECT 
    file_name,
    total_records,
    successful_records,
    failed_records,
    ingestion_status,
    error_message
FROM data_ingestion_log
ORDER BY created_at DESC
LIMIT 10;
```

