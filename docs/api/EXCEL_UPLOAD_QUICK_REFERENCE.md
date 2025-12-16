# Excel Upload API - Quick Reference

**For detailed documentation, see [EXCEL_UPLOAD_API.md](./EXCEL_UPLOAD_API.md)**

## 🚀 Quick Upload

### cURL
```bash
curl -X POST http://localhost:5000/api/ingestion/upload \
  -F "file=@pharmacy_data.xlsx" \
  -F "file_year=2021"
```

### Python
```python
import requests

with open('pharmacy_data.xlsx', 'rb') as f:
    response = requests.post(
        'http://localhost:5000/api/ingestion/upload',
        files={'file': f},
        data={'file_year': 2021}
    )
    ingestion_id = response.json()['data']['ingestion_log_id']
    print(f"Ingestion ID: {ingestion_id}")
```

### JavaScript
```javascript
const formData = new FormData();
formData.append('file', fileInput.files[0]);
formData.append('file_year', '2021');

const response = await fetch('http://localhost:5000/api/ingestion/upload', {
    method: 'POST',
    body: formData
});
const result = await response.json();
const ingestionId = result.data.ingestion_log_id;
```

## ✅ Required Excel Columns

| Column | Required | Notes |
|--------|----------|-------|
| DOC | ✅ | Document ID (Integer) |
| DATE | ✅ | Transaction date (DD/MM/YY) |
| MOV # | ✅ | Movement number |
| CODE | ✅ | Drug code |
| ARTICLE | ✅ | Drug name |
| QTY | ✅ | Quantity (> 0) |
| U.P | ✅ | Unit price |
| T.P | ✅ | Total price |

## 📊 Check Status

```bash
# Get status
curl http://localhost:5000/api/ingestion/status/<ingestion_log_id>
```

**Status Values**: `pending` → `processing` → `completed` / `failed`

## 📝 Supported Formats

- ✅ `.xlsx` (Excel 2007+)
- ✅ `.xls` (Excel 97-2003)
- ❌ `.csv` (use CSV upload endpoint)

## ⚙️ Limits

- **Max File Size**: 500 MB
- **Processing**: Asynchronous
- **Chunk Size**: 10,000 rows per batch

## 🔍 Common Errors

| Error | Solution |
|-------|----------|
| "No file provided" | Include `file` parameter |
| "Invalid file type" | Use `.xlsx` or `.xls` only |
| "File too large" | Split file or compress |
| "Missing required column" | Check column names match |

## 📚 Full Documentation

- **Excel Upload Guide**: [EXCEL_UPLOAD_API.md](./EXCEL_UPLOAD_API.md)
- **All API Examples**: [INGESTION_API_EXAMPLES.md](./INGESTION_API_EXAMPLES.md)
- **Column Mapping**: [../INGESTION_RULES_QUICK_REFERENCE.md](../INGESTION_RULES_QUICK_REFERENCE.md)

