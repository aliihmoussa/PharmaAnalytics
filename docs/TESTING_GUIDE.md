# Testing the Simplified Ingestion Pipeline

## Step 1: Verify Services Are Running

```bash
# Check if all services are up
docker compose ps

# Check logs for any errors
docker compose logs backend --tail=50
docker compose logs celery_worker --tail=50
```

## Step 2: Upload Your Excel File

### Option A: Using API (if you have a frontend/client)

```bash
# Upload file via curl
curl -X POST http://localhost:5000/api/ingestion/upload \
  -F "file=@/path/to/your/file.xlsx" \
  -F "file_year=2019"
```

### Option B: Using Python Script

```python
import requests

url = "http://localhost:5000/api/ingestion/upload"
files = {'file': open('path/to/your/file.xlsx', 'rb')}
data = {'file_year': 2019}

response = requests.post(url, files=files, data=data)
print(response.json())
```

### Option C: Using DBeaver or Database Client

You can also use the `/api/ingestion/ingest-path` endpoint if the file is accessible from the container.

## Step 3: Monitor the Ingestion Process

### Watch Logs in Real-Time

```bash
# Watch Celery worker logs (where ingestion happens)
docker compose logs -f celery_worker

# Or watch backend logs
docker compose logs -f backend
```

### What to Look For in Logs

#### ✅ Good Signs:
```
Step 2 - Column mapping: X rows, mapped columns: ['doc_id', 'transaction_date', ...]
Step 3 - Type coercion: X rows (no filtering, only conversion)
Step 4 - Validation: All X records passed validation
Cleaning pipeline summary: All X records preserved
Chunk 1: Inserting X records into database
```

#### ⚠️ Warning Signs (but may be OK):
```
Step 4 - Validation: Removed Y invalid records (Z%)
  - DOC_null: X records
  - DATE_null: Y records
```
*This is normal if some records have missing required fields*

#### 🔴 Critical Errors:
```
CRITICAL: Required field group [...] not found in dataframe columns!
CRITICAL: All X records have null [field]!
No columns were mapped! Original columns: [...]
```
*These indicate column mapping issues - check Excel headers*

## Step 4: Check Ingestion Status

### Via API

```bash
# Get status by ingestion_log_id
curl http://localhost:5000/api/ingestion/status/{ingestion_log_id}

# Get ingestion history
curl http://localhost:5000/api/ingestion/history
```

### Via Database

```sql
-- Check latest ingestion logs
SELECT 
    id,
    file_name,
    file_year,
    total_records,
    successful_records,
    failed_records,
    ingestion_status,
    error_message,
    started_at,
    completed_at
FROM data_ingestion_log
ORDER BY created_at DESC
LIMIT 5;

-- Check for errors
SELECT 
    error_type,
    error_message,
    COUNT(*) as count
FROM data_ingestion_errors
WHERE ingestion_log_id = 'your-log-id-here'
GROUP BY error_type, error_message
ORDER BY count DESC;
```

## Step 5: Verify Data in Database

### Check Total Records

```sql
SELECT COUNT(*) as total_records FROM drug_transactions;
```

### Check Bed Numbers (should have A, B, and numbers)

```sql
SELECT 
    bed_number, 
    COUNT(*) as count
FROM drug_transactions 
WHERE bed_number IS NOT NULL 
GROUP BY bed_number 
ORDER BY count DESC
LIMIT 20;
```

### Check Patient Ages

```sql
SELECT 
    patient_age,
    COUNT(*) as count
FROM drug_transactions 
WHERE patient_age IS NOT NULL 
GROUP BY patient_age 
ORDER BY count DESC
LIMIT 20;
```

### Check Admission Dates

```sql
-- Count records with admission dates
SELECT 
    COUNT(*) as total_records,
    COUNT(admission_date) as records_with_admission_date,
    COUNT(*) - COUNT(admission_date) as records_without_admission_date
FROM drug_transactions;

-- Check date distribution
SELECT 
    DATE_TRUNC('month', admission_date) as month,
    COUNT(*) as count
FROM drug_transactions 
WHERE admission_date IS NOT NULL
GROUP BY month
ORDER BY month DESC
LIMIT 12;
```

### Check Required Fields

```sql
-- Check for null values in required fields
SELECT 
    COUNT(*) as total,
    COUNT(doc_id) as has_doc_id,
    COUNT(transaction_date) as has_transaction_date,
    COUNT(movement_number) as has_movement_number,
    COUNT(drug_code) as has_drug_code,
    COUNT(drug_name) as has_drug_name,
    COUNT(quantity) as has_quantity,
    COUNT(unit_price) as has_unit_price,
    COUNT(total_price) as has_total_price
FROM drug_transactions;
```

## Step 6: Compare Results

### Expected Improvements

1. **More Records Preserved**: Should see higher `successful_records` count
2. **Better Logging**: Detailed step-by-step logs showing where data is processed
3. **Bed Numbers**: Should see A, B, and numeric values (108, 112, etc.)
4. **Patient Ages**: Should see extracted numeric ages
5. **Admission Dates**: Corrupted dates set to NULL, but records preserved

### If Issues Persist

1. **Check Column Mapping**:
   - Look for "Step 2 - Column mapping" in logs
   - Verify Excel headers match expected names (DOC, DATE, MOV #, etc.)

2. **Check Validation**:
   - Look for "Step 4 - Validation" in logs
   - See which fields are causing records to be filtered

3. **Check Type Coercion**:
   - Look for "Step 3 - Type coercion" in logs
   - Check if dates are being parsed correctly

4. **Review Error Logs**:
   ```sql
   SELECT * FROM data_ingestion_errors 
   WHERE ingestion_log_id = 'your-log-id'
   ORDER BY created_at DESC;
   ```

## Troubleshooting

### Issue: Still Getting 0 Successful Records

**Check:**
1. Column mapping logs - are columns being mapped?
2. Validation logs - which fields are null?
3. Excel file headers - do they match expected names?

**Solution:**
- Verify Excel file has correct column headers
- Check logs for "CRITICAL" messages
- Review `INGESTION_RULES_QUICK_REFERENCE.md` for expected column names

### Issue: Bed Numbers Still Empty

**Check:**
1. Is column 'U' present in Excel?
2. Are values in expected format (A, B, or numbers)?
3. Check normalization logs

**Solution:**
- Verify Excel has 'U' column
- Check column mapping logs
- Review bed_number normalization in logs

### Issue: Patient Ages Still Empty

**Check:**
1. Is column 'AGE' present in Excel?
2. Are values in expected format?
3. Check age normalization logs

**Solution:**
- Verify Excel has 'AGE' column
- Check column mapping logs
- Review age normalization in logs

## Next Steps After Testing

1. **If successful**: Review the data quality and consider:
   - Adjusting validation rules if too strict
   - Adding more normalization rules if needed
   - Optimizing performance for large files

2. **If issues persist**: 
   - Share logs with specific error messages
   - Check Excel file structure
   - Review column mappings in `schema.py`

