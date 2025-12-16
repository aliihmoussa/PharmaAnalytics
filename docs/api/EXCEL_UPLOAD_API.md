# Excel File Upload API Documentation

Complete guide for uploading Excel files (.xlsx, .xls) to the PharmaAnalytics ingestion API.

## Table of Contents

1. [Overview](#overview)
2. [Excel File Requirements](#excel-file-requirements)
3. [Upload Endpoint](#upload-endpoint)
4. [Examples](#examples)
5. [Status Checking](#status-checking)
6. [Error Handling](#error-handling)
7. [Best Practices](#best-practices)
8. [Complete Workflow](#complete-workflow)

---

## Overview

The ingestion API accepts Excel files (`.xlsx` and `.xls`) for processing pharmacy transaction data. Files are processed asynchronously using Celery, allowing you to upload large files without blocking.

**Base URL**: `http://localhost:5000/api/ingestion`

**Supported Excel Formats**:
- `.xlsx` (Excel 2007+)
- `.xls` (Excel 97-2003)

**Maximum File Size**: 500 MB

**Processing**: Asynchronous (non-blocking)

---

## Excel File Requirements

### Required Columns

Your Excel file must contain the following columns (case-insensitive):

| Excel Column Name | Database Field | Required? | Data Type | Notes |
|------------------|---------------|-----------|-----------|-------|
| `DOC` | doc_id | ✅ Yes | Integer | Document ID |
| `DATE` | transaction_date | ✅ Yes | Date | Format: DD/MM/YY |
| `MOV #` or `MOV#` | movement_number | ✅ Yes | Integer | Movement number |
| `CODE` | drug_code | ✅ Yes | String | Drug code (uppercase) |
| `ARTICLE` | drug_name | ✅ Yes | String | Drug name |
| `QTY` | quantity | ✅ Yes | Integer | Quantity (cannot be 0) |
| `U.P` | unit_price | ✅ Yes | Numeric | Unit price |
| `T.P` | total_price | ✅ Yes | Numeric | Total price |

### Optional Columns

| Excel Column Name | Database Field | Data Type | Notes |
|------------------|---------------|-----------|-------|
| `LINE` | line_number | Integer | Line number |
| `CAT` | drug_category | Integer | Drug category |
| `C.R` | consuming_dept | Integer | Consuming department |
| `MOV DES` | movement_description | String | May contain Arabic text |
| `M` | m_field | String | M field |
| `C.S` | supplying_dept | Integer | Supplying department |
| `AD DATE` | admission_date | Date | Admission date (optional) |
| `R` | room_number | Integer | Room number |
| `U` | bed_number | String | Bed number (A/B/numbers) |
| `AGE` | patient_age | String | Patient age (may contain Arabic) |

### Excel File Structure

1. **Header Row**: First row should contain column names
2. **Data Rows**: All subsequent rows contain transaction data
3. **Sheet Selection**: If multiple sheets exist, the first sheet is used by default
4. **Empty Rows**: Completely empty rows are automatically removed

### Column Name Variations

The system handles these variations automatically:
- `MOV #` vs `MOV#` (with/without space)
- Case-insensitive matching (e.g., `DOC`, `doc`, `Doc` all work)
- Whitespace variations

---

## Upload Endpoint

### POST /api/ingestion/upload

Upload an Excel file for processing.

**Content-Type**: `multipart/form-data`

**Request Parameters**:

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `file` | File | ✅ Yes | The Excel file to upload (.xlsx or .xls) |
| `file_name` | String | ❌ No | Original file name (defaults to uploaded filename) |
| `file_year` | Integer | ❌ No | Year of the data (e.g., 2021, 2022) |

**Response** (HTTP 202 Accepted):

```json
{
  "success": true,
  "data": {
    "upload_id": "550e8400-e29b-41d4-a716-446655440000",
    "ingestion_log_id": "550e8400-e29b-41d4-a716-446655440000",
    "file_name": "pharmacy_data_2021.xlsx",
    "status": "pending",
    "message": "File uploaded and queued for processing"
  }
}
```

**Important**: Save the `ingestion_log_id` from the response to check processing status later.

---

## Examples

### cURL

```bash
# Basic upload
curl -X POST http://localhost:5000/api/ingestion/upload \
  -F "file=@/path/to/pharmacy_data_2021.xlsx" \
  -F "file_year=2021"

# With custom file name
curl -X POST http://localhost:5000/api/ingestion/upload \
  -F "file=@/path/to/pharmacy_data_2021.xlsx" \
  -F "file_name=pharmacy_data_2021.xlsx" \
  -F "file_year=2021"

# Upload .xls file (older Excel format)
curl -X POST http://localhost:5000/api/ingestion/upload \
  -F "file=@/path/to/pharmacy_data_2020.xls" \
  -F "file_year=2020"
```

### Python (requests)

```python
import requests

url = "http://localhost:5000/api/ingestion/upload"

# Upload Excel file
with open('/path/to/pharmacy_data_2021.xlsx', 'rb') as f:
    files = {
        'file': ('pharmacy_data_2021.xlsx', f, 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    }
    data = {
        'file_name': 'pharmacy_data_2021.xlsx',
        'file_year': 2021  # Optional
    }
    
    response = requests.post(url, files=files, data=data)
    response.raise_for_status()
    
    result = response.json()
    ingestion_log_id = result['data']['ingestion_log_id']
    print(f"Upload successful! Ingestion ID: {ingestion_log_id}")
```

### Python (with error handling)

```python
import requests
import sys

def upload_excel_file(file_path, file_year=None):
    """Upload Excel file and return ingestion_log_id."""
    url = "http://localhost:5000/api/ingestion/upload"
    
    try:
        with open(file_path, 'rb') as f:
            files = {'file': (file_path, f)}
            data = {'file_year': file_year} if file_year else {}
            
            response = requests.post(url, files=files, data=data)
            response.raise_for_status()
            
            result = response.json()
            if result.get('success'):
                return result['data']['ingestion_log_id']
            else:
                raise Exception(f"Upload failed: {result.get('error', 'Unknown error')}")
    
    except requests.exceptions.RequestException as e:
        print(f"Error uploading file: {e}", file=sys.stderr)
        raise
    except FileNotFoundError:
        print(f"File not found: {file_path}", file=sys.stderr)
        raise

# Usage
ingestion_id = upload_excel_file('/path/to/pharmacy_data_2021.xlsx', file_year=2021)
print(f"Ingestion ID: {ingestion_id}")
```

### JavaScript (Fetch API)

```javascript
async function uploadExcelFile(file, fileYear = null) {
    const formData = new FormData();
    formData.append('file', file);
    
    if (fileYear) {
        formData.append('file_year', fileYear.toString());
    }
    
    try {
        const response = await fetch('http://localhost:5000/api/ingestion/upload', {
            method: 'POST',
            body: formData
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error?.message || 'Upload failed');
        }
        
        const result = await response.json();
        return result.data.ingestion_log_id;
    } catch (error) {
        console.error('Upload error:', error);
        throw error;
    }
}

// Usage with file input
const fileInput = document.querySelector('input[type="file"]');
fileInput.addEventListener('change', async (event) => {
    const file = event.target.files[0];
    if (file) {
        try {
            const ingestionId = await uploadExcelFile(file, 2021);
            console.log('Upload successful! Ingestion ID:', ingestionId);
        } catch (error) {
            console.error('Upload failed:', error);
        }
    }
});
```

### JavaScript (with React)

```jsx
import React, { useState } from 'react';

function ExcelUploader() {
    const [uploading, setUploading] = useState(false);
    const [ingestionId, setIngestionId] = useState(null);
    const [error, setError] = useState(null);
    
    const handleFileUpload = async (event) => {
        const file = event.target.files[0];
        if (!file) return;
        
        setUploading(true);
        setError(null);
        
        const formData = new FormData();
        formData.append('file', file);
        formData.append('file_year', '2021');
        
        try {
            const response = await fetch('http://localhost:5000/api/ingestion/upload', {
                method: 'POST',
                body: formData
            });
            
            const result = await response.json();
            
            if (result.success) {
                setIngestionId(result.data.ingestion_log_id);
            } else {
                setError(result.error?.message || 'Upload failed');
            }
        } catch (err) {
            setError(err.message);
        } finally {
            setUploading(false);
        }
    };
    
    return (
        <div>
            <input 
                type="file" 
                accept=".xlsx,.xls" 
                onChange={handleFileUpload}
                disabled={uploading}
            />
            {uploading && <p>Uploading...</p>}
            {ingestionId && <p>Upload successful! ID: {ingestionId}</p>}
            {error && <p style={{color: 'red'}}>Error: {error}</p>}
        </div>
    );
}
```

### PowerShell (Windows)

```powershell
# Upload Excel file using PowerShell
$filePath = "C:\path\to\pharmacy_data_2021.xlsx"
$url = "http://localhost:5000/api/ingestion/upload"

$formData = @{
    file = Get-Item $filePath
    file_year = 2021
}

try {
    $response = Invoke-RestMethod -Uri $url -Method Post -Form $formData
    Write-Host "Upload successful! Ingestion ID: $($response.data.ingestion_log_id)"
} catch {
    Write-Host "Upload failed: $($_.Exception.Message)" -ForegroundColor Red
}
```

---

## Status Checking

After uploading, check the processing status using the `ingestion_log_id`.

### GET /api/ingestion/status/<ingestion_log_id>

**Example**:

```bash
# Check status
curl http://localhost:5000/api/ingestion/status/550e8400-e29b-41d4-a716-446655440000
```

**Response (Processing)**:

```json
{
  "success": true,
  "data": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "file_name": "pharmacy_data_2021.xlsx",
    "file_year": 2021,
    "ingestion_status": "processing",
    "total_records": 50000,
    "successful_records": 25000,
    "failed_records": 0,
    "error_message": null,
    "started_at": "2025-12-13T10:30:00",
    "completed_at": null,
    "created_at": "2025-12-13T10:30:00"
  }
}
```

**Response (Completed)**:

```json
{
  "success": true,
  "data": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "file_name": "pharmacy_data_2021.xlsx",
    "file_year": 2021,
    "ingestion_status": "completed",
    "total_records": 50000,
    "successful_records": 49850,
    "failed_records": 150,
    "error_message": null,
    "started_at": "2025-12-13T10:30:00",
    "completed_at": "2025-12-13T10:35:00",
    "created_at": "2025-12-13T10:30:00"
  }
}
```

**Status Values**:
- `pending`: File uploaded, waiting to be processed
- `processing`: Currently being processed
- `completed`: Processing finished successfully
- `failed`: Processing failed (check `error_message`)
- `cancelled`: Processing was cancelled

### Python Status Checker

```python
import requests
import time

def check_status(ingestion_log_id, poll_interval=5):
    """Poll status until completion."""
    url = f"http://localhost:5000/api/ingestion/status/{ingestion_log_id}"
    
    while True:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()['data']
        
        status = data['ingestion_status']
        successful = data.get('successful_records', 0)
        total = data.get('total_records', 0)
        
        print(f"Status: {status} | Progress: {successful}/{total}")
        
        if status in ['completed', 'failed', 'cancelled']:
            return data
        
        time.sleep(poll_interval)

# Usage
ingestion_id = "550e8400-e29b-41d4-a716-446655440000"
final_status = check_status(ingestion_id)
print(f"Final status: {final_status['ingestion_status']}")
```

---

## Error Handling

### Common Errors

#### 1. No File Provided

**Status Code**: 400

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "No file provided"
  }
}
```

**Solution**: Ensure the `file` parameter is included in the request.

#### 2. Invalid File Type

**Status Code**: 400

```json
{
  "error": {
    "code": "INVALID_FILE_TYPE",
    "message": "File type 'pdf' not allowed. Allowed: csv, txt, tsv, dat, xlsx, xls"
  }
}
```

**Solution**: Upload only `.xlsx` or `.xls` files.

#### 3. File Too Large

**Status Code**: 400

```json
{
  "error": {
    "code": "FILE_TOO_LARGE",
    "message": "File size (600.00MB) exceeds maximum (500.00MB)"
  }
}
```

**Solution**: Split large files or compress them.

#### 4. Empty File

**Status Code**: 400

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "File is empty"
  }
}
```

**Solution**: Ensure the Excel file contains data.

#### 5. Duplicate File

**Status Code**: 400

```json
{
  "error": {
    "code": "DUPLICATE_FILE",
    "message": "File 'pharmacy_data_2021.xlsx' has already been ingested"
  }
}
```

**Solution**: Use a different filename or check ingestion history.

#### 6. Processing Error

**Status Code**: 500 (during processing)

Check status endpoint for details:

```json
{
  "success": true,
  "data": {
    "ingestion_status": "failed",
    "error_message": "Missing required column: DOC",
    "successful_records": 0,
    "failed_records": 50000
  }
}
```

**Solution**: Fix the Excel file structure and re-upload.

### Error Handling Example (Python)

```python
import requests

def upload_with_error_handling(file_path, file_year=None):
    """Upload file with comprehensive error handling."""
    url = "http://localhost:5000/api/ingestion/upload"
    
    try:
        with open(file_path, 'rb') as f:
            files = {'file': f}
            data = {'file_year': file_year} if file_year else {}
            
            response = requests.post(url, files=files, data=data)
            
            # Check for HTTP errors
            if response.status_code == 400:
                error_data = response.json()
                error_msg = error_data.get('error', {}).get('message', 'Unknown error')
                raise ValueError(f"Validation error: {error_msg}")
            
            response.raise_for_status()
            return response.json()['data']['ingestion_log_id']
    
    except FileNotFoundError:
        raise FileNotFoundError(f"File not found: {file_path}")
    except requests.exceptions.HTTPError as e:
        raise Exception(f"HTTP error: {e}")
    except Exception as e:
        raise Exception(f"Upload failed: {e}")
```

---

## Best Practices

### 1. File Preparation

- ✅ **Check column names**: Ensure required columns exist (case-insensitive)
- ✅ **Remove empty rows**: System removes them, but cleaner files process faster
- ✅ **Validate dates**: Use DD/MM/YY format for DATE column
- ✅ **Check data types**: Ensure numeric columns contain valid numbers
- ✅ **File size**: Keep files under 500MB for optimal performance

### 2. Upload Process

- ✅ **Save ingestion_log_id**: Always save the ID from upload response
- ✅ **Poll status**: Check status periodically until completion
- ✅ **Handle errors**: Implement proper error handling
- ✅ **Use file_year**: Specify the year for better organization

### 3. Performance

- ✅ **Large files**: Files are processed in chunks (10k rows), so large files are supported
- ✅ **Multiple files**: Upload files sequentially or use separate API calls
- ✅ **Status polling**: Poll every 5-10 seconds, not continuously

### 4. Data Quality

- ✅ **Required fields**: Ensure DOC, DATE, MOV #, CODE, ARTICLE, QTY, U.P, T.P are present
- ✅ **Valid quantities**: QTY must be > 0
- ✅ **Date format**: Use DD/MM/YY format
- ✅ **Special characters**: Arabic text in MOV DES and AGE is supported

---

## Complete Workflow

### Step-by-Step Example

```python
import requests
import time

def complete_excel_upload_workflow(file_path, file_year):
    """Complete workflow: upload, monitor, and verify."""
    
    # Step 1: Upload file
    print(f"Uploading {file_path}...")
    url = "http://localhost:5000/api/ingestion/upload"
    
    with open(file_path, 'rb') as f:
        files = {'file': f}
        data = {'file_year': file_year}
        response = requests.post(url, files=files, data=data)
        response.raise_for_status()
    
    result = response.json()
    ingestion_id = result['data']['ingestion_log_id']
    print(f"✓ Upload successful! Ingestion ID: {ingestion_id}")
    
    # Step 2: Monitor status
    print("Monitoring processing status...")
    status_url = f"http://localhost:5000/api/ingestion/status/{ingestion_id}"
    
    while True:
        response = requests.get(status_url)
        response.raise_for_status()
        data = response.json()['data']
        
        status = data['ingestion_status']
        successful = data.get('successful_records', 0)
        total = data.get('total_records', 0)
        failed = data.get('failed_records', 0)
        
        print(f"  Status: {status} | Successful: {successful} | Failed: {failed} | Total: {total}")
        
        if status == 'completed':
            print(f"✓ Processing completed successfully!")
            print(f"  - Successful records: {successful}")
            print(f"  - Failed records: {failed}")
            return data
        elif status == 'failed':
            error_msg = data.get('error_message', 'Unknown error')
            raise Exception(f"Processing failed: {error_msg}")
        elif status == 'cancelled':
            raise Exception("Processing was cancelled")
        
        time.sleep(5)  # Poll every 5 seconds

# Usage
try:
    result = complete_excel_upload_workflow(
        '/path/to/pharmacy_data_2021.xlsx',
        file_year=2021
    )
    print("\n✓ Upload and processing completed successfully!")
except Exception as e:
    print(f"\n✗ Error: {e}")
```

### Shell Script Example

```bash
#!/bin/bash

# Excel Upload Workflow Script

FILE_PATH="$1"
FILE_YEAR="$2"
BASE_URL="http://localhost:5000/api/ingestion"

if [ -z "$FILE_PATH" ]; then
    echo "Usage: $0 <excel_file> [year]"
    exit 1
fi

# Step 1: Upload
echo "Uploading $FILE_PATH..."
UPLOAD_RESPONSE=$(curl -s -X POST "$BASE_URL/upload" \
    -F "file=@$FILE_PATH" \
    -F "file_year=$FILE_YEAR")

INGESTION_ID=$(echo $UPLOAD_RESPONSE | jq -r '.data.ingestion_log_id')

if [ "$INGESTION_ID" == "null" ] || [ -z "$INGESTION_ID" ]; then
    echo "Upload failed!"
    echo $UPLOAD_RESPONSE | jq .
    exit 1
fi

echo "✓ Upload successful! Ingestion ID: $INGESTION_ID"

# Step 2: Monitor status
echo "Monitoring processing status..."
while true; do
    STATUS_RESPONSE=$(curl -s "$BASE_URL/status/$INGESTION_ID")
    STATUS=$(echo $STATUS_RESPONSE | jq -r '.data.ingestion_status')
    SUCCESSFUL=$(echo $STATUS_RESPONSE | jq -r '.data.successful_records // 0')
    FAILED=$(echo $STATUS_RESPONSE | jq -r '.data.failed_records // 0')
    TOTAL=$(echo $STATUS_RESPONSE | jq -r '.data.total_records // 0')
    
    echo "  Status: $STATUS | Successful: $SUCCESSFUL | Failed: $FAILED | Total: $TOTAL"
    
    if [ "$STATUS" == "completed" ]; then
        echo "✓ Processing completed!"
        break
    elif [ "$STATUS" == "failed" ]; then
        ERROR=$(echo $STATUS_RESPONSE | jq -r '.data.error_message')
        echo "✗ Processing failed: $ERROR"
        exit 1
    fi
    
    sleep 5
done
```

---

## Additional Resources

- **Full API Examples**: See [INGESTION_API_EXAMPLES.md](./INGESTION_API_EXAMPLES.md)
- **Column Mapping**: See [INGESTION_RULES_QUICK_REFERENCE.md](../INGESTION_RULES_QUICK_REFERENCE.md)
- **Database Commands**: See [DATABASE_COMMANDS.md](../database/DATABASE_COMMANDS.md)

---

## Quick Reference

| Action | Endpoint | Method |
|--------|----------|--------|
| Upload Excel | `/api/ingestion/upload` | POST |
| Check Status | `/api/ingestion/status/<id>` | GET |
| List History | `/api/ingestion/history` | GET |
| Cancel | `/api/ingestion/<id>/cancel` | DELETE |

**Supported Formats**: `.xlsx`, `.xls`  
**Max File Size**: 500 MB  
**Processing**: Asynchronous  
**Required Columns**: DOC, DATE, MOV #, CODE, ARTICLE, QTY, U.P, T.P

