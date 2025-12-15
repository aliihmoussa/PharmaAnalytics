# Age Handling Locations

This document shows all places where patient age is handled in the ingestion pipeline.

## 1. Column Mapping (Schema Definition)

**File**: `backend/app/modules/ingestion/schema.py`

```python
FIELD_MAPPINGS = {
    'AGE': 'patient_age'  # Maps Excel column 'AGE' to database field 'patient_age'
}
```

**Purpose**: Maps the Excel column name `AGE` to the database field name `patient_age`

---

## 2. Database Model Definition

**File**: `backend/app/database/models.py`

```python
class DrugTransaction(Base):
    patient_age = Column(String(20), nullable=True)
```

**Purpose**: Defines the database column as `String(20)` and nullable (optional field)

---

## 3. Age Normalization (Main Processing)

**File**: `backend/app/modules/ingestion/cleaning.py`  
**Function**: `verify_data_consistency()`  
**Lines**: 774-879

**This is the MAIN place where age is processed:**

### What it does:

1. **Detects AGE column** - Looks for both `AGE` (original) and `patient_age` (mapped) columns

2. **Handles multiple formats**:
   - **Dates** (e.g., "6/28/1983") → Calculates age from birth date
   - **Arabic text** (e.g., "25 سنة") → Extracts numeric age
   - **Corrupted formats** (e.g., "ب 0000/00/00") → Sets to NULL
   - **Plain numbers** (e.g., "45") → Uses directly

3. **Date to Age Conversion**:
   - Parses dates in formats: MM/DD/YYYY, YYYY-MM-DD, MM/DD/YY
   - Calculates age using reference date: December 31, 2019
   - Formula: `age = (2019-12-31 - birth_date).days // 365`

4. **Arabic Text Processing**:
   - Removes Arabic words: سنة (year), عام (year), عمر (age)
   - Extracts numeric value from text

5. **Validation**:
   - Only accepts ages between 0-150
   - Returns NULL for invalid/corrupted values

6. **Logging**:
   - Logs sample values before normalization
   - Logs results after normalization
   - Shows count of null vs non-null values

### Code Location:
```python
# Line 774-879 in cleaning.py
def verify_data_consistency(df: pl.DataFrame):
    # ...
    age_fields = ['AGE', 'patient_age']
    for age_field in age_fields:
        if age_field in corrected_df.columns:
            def normalize_age(age_str):
                # Handles dates, Arabic text, corrupted formats
                # Returns age as string or None
```

---

## 4. Pipeline Flow

**File**: `backend/app/modules/ingestion/processors.py`  
**Function**: `_apply_cleaning_pipeline()`

**Order of operations**:

1. **Step 1**: Excel cleaning (remove empty rows)
2. **Step 2**: Column mapping (`AGE` → `patient_age`)
3. **Step 3**: Type coercion (convert data types)
4. **Step 4**: Data validation (filter invalid records)
5. **Step 5**: **Data consistency** ← **AGE normalization happens here**
   - Calls `verify_data_consistency()` which normalizes age

---

## Summary

### Age Processing Flow:

```
Excel File (AGE column)
    ↓
Column Mapping (AGE → patient_age)
    ↓
Type Coercion (preserves as string)
    ↓
Data Validation (no filtering for age - it's optional)
    ↓
Data Consistency Check ← AGE NORMALIZATION HAPPENS HERE
    ├─ Detects date formats → calculates age
    ├─ Detects Arabic text → extracts age
    ├─ Detects corrupted formats → sets to NULL
    └─ Validates age range (0-150)
    ↓
Database Insertion (patient_age field)
```

---

## Key Points

1. **Age is optional** - Records are NOT filtered if age is missing/null
2. **Age normalization happens in `verify_data_consistency()`** - This is called during Step 5 of the cleaning pipeline
3. **Age is stored as String** - Database column is `String(20)`, not Integer
4. **Multiple format support** - Handles dates, Arabic text, and plain numbers
5. **Date calculation** - Uses 2019-12-31 as reference date for age calculation

---

## To Debug Age Issues

Check logs for:
```
Normalizing AGE: X null values, sample values: [...]
After normalizing AGE: Y null values, Z non-null values
Sample normalized age values: [...]
```

These logs appear during Step 5 of the cleaning pipeline.

