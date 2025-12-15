# Ingestion API - Complete Examples

## Base URL
```
http://localhost:5000/api/ingestion
```

---

## 1. Upload File (Multipart Form Data)

### Endpoint
```
POST /api/ingestion/upload
```

### Using cURL
```bash
curl -X POST http://localhost:5000/api/ingestion/upload \
  -F "file=@/path/to/your/file.xlsx" \
  -F "file_name=pharmacy_data_2021.xlsx" \
  -F "file_year=2021"
```

### Using Python requests
```python
import requests

url = "http://localhost:5000/api/ingestion/upload"

# Prepare the file
with open('/path/to/your/file.xlsx', 'rb') as f:
    files = {'file': ('pharmacy_data_2021.xlsx', f, 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')}
    data = {
        'file_name': 'pharmacy_data_2021.xlsx',
        'file_year': 2021  # Optional
    }
    
    response = requests.post(url, files=files, data=data)
    print(response.json())
```

### Using JavaScript (Fetch API)
```javascript
const formData = new FormData();
formData.append('file', fileInput.files[0]); // fileInput is an <input type="file">
formData.append('file_name', 'pharmacy_data_2021.xlsx');
formData.append('file_year', '2021');

fetch('http://localhost:5000/api/ingestion/upload', {
    method: 'POST',
    body: formData
})
.then(response => response.json())
.then(data => console.log(data))
.catch(error => console.error('Error:', error));
```

### Request Parameters
- **file** (required): The file to upload (multipart/form-data)
- **file_name** (optional): Original file name (defaults to uploaded filename)
- **file_year** (optional): Year of the data (integer)

### Response Example
```json
{
  "success": true,
  "data": {
    "upload_id": "550e8400-e29b-41d4-a716-446655440000",
    "ingestion_log_id": "550e8400-e29b-41d4-a716-446655440000",
    "file_name": "pharmacy_data_2021.xlsx",
    "status": "pending",
    "message": "File uploaded successfully. Processing started."
  }
}
```

---

## 2. Ingest File from Path

### Endpoint
```
POST /api/ingestion/ingest-path
```

### Using cURL
```bash
curl -X POST http://localhost:5000/api/ingestion/ingest-path \
  -H "Content-Type: application/json" \
  -d '{
    "file_path": "/app/data/uploads/pharmacy_data_2021.xlsx",
    "file_year": 2021
  }'
```

### Using Python requests
```python
import requests

url = "http://localhost:5000/api/ingestion/ingest-path"

payload = {
    "file_path": "/app/data/uploads/pharmacy_data_2021.xlsx",
    "file_year": 2021  # Optional
}

response = requests.post(url, json=payload)
print(response.json())
```

### Request Body (JSON)
```json
{
  "file_path": "/app/data/uploads/pharmacy_data_2021.xlsx",
  "file_year": 2021
}
```

### Response Example
```json
{
  "success": true,
  "data": {
    "upload_id": "550e8400-e29b-41d4-a716-446655440000",
    "ingestion_log_id": "550e8400-e29b-41d4-a716-446655440000",
    "file_name": "pharmacy_data_2021.xlsx",
    "status": "pending",
    "message": "File ingestion started."
  }
}
```

---

## 3. Check Ingestion Status

### Endpoint
```
GET /api/ingestion/status/<ingestion_log_id>
```

### Using cURL
```bash
curl http://localhost:5000/api/ingestion/status/550e8400-e29b-41d4-a716-446655440000
```

### Using Python requests
```python
import requests

ingestion_log_id = "550e8400-e29b-41d4-a716-446655440000"
url = f"http://localhost:5000/api/ingestion/status/{ingestion_log_id}"

response = requests.get(url)
print(response.json())
```

### Response Example (Processing)
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

### Response Example (Completed)
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

---

## 4. List Ingestion History

### Endpoint
```
GET /api/ingestion/history
```

### Using cURL
```bash
# Get all ingestions
curl http://localhost:5000/api/ingestion/history

# Filter by status
curl "http://localhost:5000/api/ingestion/history?status=completed"

# With pagination
curl "http://localhost:5000/api/ingestion/history?limit=10&offset=0"
```

### Using Python requests
```python
import requests

url = "http://localhost:5000/api/ingestion/history"

# Query parameters
params = {
    "status": "completed",  # Optional: 'pending', 'processing', 'completed', 'failed', 'cancelled'
    "limit": 10,             # Optional: default 50, max 100
    "offset": 0              # Optional: default 0
}

response = requests.get(url, params=params)
print(response.json())
```

### Query Parameters
- **status** (optional): Filter by status (`pending`, `processing`, `completed`, `failed`, `cancelled`)
- **limit** (optional): Maximum results (default: 50, max: 100)
- **offset** (optional): Offset for pagination (default: 0)

### Response Example
```json
{
  "success": true,
  "data": {
    "ingestions": [
      {
        "id": "550e8400-e29b-41d4-a716-446655440000",
        "file_name": "pharmacy_data_2021.xlsx",
        "file_year": 2021,
        "ingestion_status": "completed",
        "total_records": 50000,
        "successful_records": 49850,
        "failed_records": 150,
        "created_at": "2025-12-13T10:30:00"
      }
    ],
    "pagination": {
      "limit": 50,
      "offset": 0,
      "total": 1
    }
  }
}
```

---

## 5. Cancel Ingestion

### Endpoint
```
DELETE /api/ingestion/<ingestion_log_id>/cancel
```

### Using cURL
```bash
curl -X DELETE http://localhost:5000/api/ingestion/550e8400-e29b-41d4-a716-446655440000/cancel
```

### Using Python requests
```python
import requests

ingestion_log_id = "550e8400-e29b-41d4-a716-446655440000"
url = f"http://localhost:5000/api/ingestion/{ingestion_log_id}/cancel"

response = requests.delete(url)
print(response.json())
```

### Response Example
```json
{
  "success": true,
  "data": {
    "message": "Ingestion 550e8400-e29b-41d4-a716-446655440000 cancelled successfully"
  }
}
```

---

## Complete Testing Workflow

### Step 1: Upload a file
```bash
curl -X POST http://localhost:5000/api/ingestion/upload \
  -F "file=@/path/to/pharmacy_data_2021.xlsx" \
  -F "file_year=2021"
```

**Save the `ingestion_log_id` from the response**

### Step 2: Check status (poll until completed)
```bash
INGESTION_ID="550e8400-e29b-41d4-a716-446655440000"

# Check status
curl http://localhost:5000/api/ingestion/status/$INGESTION_ID

# Poll every 5 seconds until status is 'completed' or 'failed'
while true; do
  STATUS=$(curl -s http://localhost:5000/api/ingestion/status/$INGESTION_ID | jq -r '.data.ingestion_status')
  echo "Status: $STATUS"
  if [ "$STATUS" = "completed" ] || [ "$STATUS" = "failed" ]; then
    break
  fi
  sleep 5
done
```

### Step 3: View ingestion history
```bash
curl "http://localhost:5000/api/ingestion/history?limit=10"
```

---

## Python Complete Example Script

```python
import requests
import time
import json

BASE_URL = "http://localhost:5000/api/ingestion"

def upload_file(file_path, file_year=None):
    """Upload a file for ingestion."""
    url = f"{BASE_URL}/upload"
    
    with open(file_path, 'rb') as f:
        files = {'file': f}
        data = {'file_year': file_year} if file_year else {}
        
        response = requests.post(url, files=files, data=data)
        response.raise_for_status()
        return response.json()['data']

def check_status(ingestion_log_id):
    """Check ingestion status."""
    url = f"{BASE_URL}/status/{ingestion_log_id}"
    response = requests.get(url)
    response.raise_for_status()
    return response.json()['data']

def wait_for_completion(ingestion_log_id, poll_interval=5):
    """Wait for ingestion to complete."""
    print(f"Waiting for ingestion {ingestion_log_id} to complete...")
    
    while True:
        status = check_status(ingestion_log_id)
        status_type = status['ingestion_status']
        
        print(f"Status: {status_type} | "
              f"Progress: {status.get('successful_records', 0)}/{status.get('total_records', 0)}")
        
        if status_type in ['completed', 'failed', 'cancelled']:
            return status
        
        time.sleep(poll_interval)

def list_history(status=None, limit=10):
    """List ingestion history."""
    url = f"{BASE_URL}/history"
    params = {'limit': limit}
    if status:
        params['status'] = status
    
    response = requests.get(url, params=params)
    response.raise_for_status()
    return response.json()['data']

# Example usage
if __name__ == "__main__":
    # 1. Upload file
    print("Uploading file...")
    upload_result = upload_file('/path/to/pharmacy_data_2021.xlsx', file_year=2021)
    ingestion_id = upload_result['ingestion_log_id']
    print(f"Uploaded! Ingestion ID: {ingestion_id}")
    
    # 2. Wait for completion
    final_status = wait_for_completion(ingestion_id)
    print(f"\nFinal status: {final_status['ingestion_status']}")
    print(f"Successful: {final_status.get('successful_records', 0)}")
    print(f"Failed: {final_status.get('failed_records', 0)}")
    
    # 3. List history
    print("\nRecent ingestions:")
    history = list_history(limit=5)
    for ingestion in history['ingestions']:
        print(f"  - {ingestion['file_name']}: {ingestion['ingestion_status']}")
```

---

## Supported File Formats

- **Excel**: `.xlsx`, `.xls`
- **CSV**: `.csv`, `.txt`, `.tsv`, `.dat`

---

## Error Responses

### Validation Error
```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "No file provided"
  }
}
```

### File Too Large
```json
{
  "error": {
    "code": "FILE_TOO_LARGE",
    "message": "File size exceeds maximum allowed size (500MB)"
  }
}
```

### Invalid File Type
```json
{
  "error": {
    "code": "INVALID_FILE_TYPE",
    "message": "File type not supported. Allowed: csv, txt, tsv, dat, xlsx, xls"
  }
}
```

---

## Notes

1. **File Upload**: Use `multipart/form-data` for file uploads
2. **File Path**: For `ingest-path`, the path must be accessible from within the Docker container
3. **Async Processing**: File ingestion is processed asynchronously. Use the status endpoint to check progress
4. **File Size Limit**: Maximum file size is 500MB
5. **Status Values**: `pending`, `processing`, `completed`, `failed`, `cancelled`

