# Cost Analysis Report API - Quick Reference

## Endpoint

```
GET /api/analytics/cost-analysis/report
```

## Quick Usage

### Download DOCX Report (Default)
```javascript
// Vanilla JavaScript
fetch('/api/analytics/cost-analysis/report?start_date=2019-01-01&end_date=2019-12-31')
  .then(r => r.blob())
  .then(blob => {
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'report.docx';
    a.click();
  });
```

### Download PDF Report
```javascript
fetch('/api/analytics/cost-analysis/report?start_date=2019-01-01&end_date=2019-12-31&format=pdf')
  .then(r => r.blob())
  .then(blob => {
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'report.pdf';
    a.click();
  });
```

## Query Parameters

| Param | Type | Required | Default | Example |
|-------|------|----------|---------|---------|
| `start_date` | date | ✓ | - | `2019-01-01` |
| `end_date` | date | ✓ | - | `2019-12-31` |
| `format` | string | - | `docx` | `pdf` |
| `departments` | csv | - | all | `1,2,3` |
| `price_min` | float | - | 0 | `10.0` |
| `price_max` | float | - | unlimited | `1000.0` |
| `drug_categories` | csv | - | all | `1,2,3` |

## Report Contents

✓ Executive Summary
✓ Analysis Parameters (Filters Applied)
✓ Cost Overview by Department
✓ Top 20 Cost Drivers (with tables)
✓ Monthly Cost Trends
✓ Department-level Analysis
✓ Drug Category Breakdown

## Response Format

- **DOCX**: `application/vnd.openxmlformats-officedocument.wordprocessingml.document`
- **PDF**: `application/pdf`

Both are returned as downloadable file attachments.

## Frontend Integration Patterns

### React Hook
```jsx
const useCostAnalysisReport = () => {
  const [loading, setLoading] = useState(false);

  const downloadReport = async (startDate, endDate, format = 'docx') => {
    setLoading(true);
    try {
      const params = new URLSearchParams({ start_date: startDate, end_date: endDate, format });
      const response = await fetch(`/api/analytics/cost-analysis/report?${params}`);
      const blob = await response.blob();
      
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `report_${Date.now()}.${format}`;
      a.click();
      window.URL.revokeObjectURL(url);
    } catch (error) {
      console.error('Report download failed:', error);
    } finally {
      setLoading(false);
    }
  };

  return { downloadReport, loading };
};
```

### Vue Composable
```javascript
import { ref } from 'vue';

export const useCostAnalysisReport = () => {
  const loading = ref(false);

  const downloadReport = async (startDate, endDate, format = 'docx') => {
    loading.value = true;
    try {
      const params = new URLSearchParams({ start_date: startDate, end_date: endDate, format });
      const response = await fetch(`/api/analytics/cost-analysis/report?${params}`);
      const blob = await response.blob();
      
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `report_${Date.now()}.${format}`;
      a.click();
      window.URL.revokeObjectURL(url);
    } finally {
      loading.value = false;
    }
  };

  return { downloadReport, loading };
};
```

## Common Scenarios

### 1. Download Report for Entire Year
```
GET /api/analytics/cost-analysis/report?start_date=2019-01-01&end_date=2019-12-31&format=pdf
```

### 2. Download Report for Specific Department
```
GET /api/analytics/cost-analysis/report?start_date=2019-01-01&end_date=2019-12-31&departments=1&format=docx
```

### 3. Download Report for High-Cost Drugs Only
```
GET /api/analytics/cost-analysis/report?start_date=2019-01-01&end_date=2019-12-31&price_min=100.0&format=pdf
```

### 4. Download Report for Specific Category
```
GET /api/analytics/cost-analysis/report?start_date=2019-01-01&end_date=2019-12-31&drug_categories=5&format=docx
```

### 5. Download Report with Multiple Filters
```
GET /api/analytics/cost-analysis/report?start_date=2019-01-01&end_date=2019-12-31&departments=1,2,3&drug_categories=5,6&price_min=10.0&price_max=500.0&format=pdf
```

## Error Codes

| Code | Message | Solution |
|------|---------|----------|
| 400 | Invalid format | Use `docx` or `pdf` |
| 400 | Invalid date format | Use `YYYY-MM-DD` format |
| 404 | No data found | Check filters and date range |
| 500 | Server error | Check server logs |

## Performance Tips

1. **Smaller Reports**: Use date ranges ≤ 3 months for faster generation
2. **Caching**: Cache frequently requested reports in localStorage
3. **Async Loading**: Show loading indicator during generation (typically 5-30 seconds)
4. **Batch Downloads**: Generate multiple formats in sequence, not parallel

## Report File Naming

Reports are automatically named with timestamps:
- `Cost_Analysis_Report_20240214_143022.docx`
- `Cost_Analysis_Report_20240214_143022.pdf`

## Supported Filters

All filters are **optional** and combine with AND logic:
- **Date range**: Required for analysis period
- **Departments**: Filter by specific departments (IDs)
- **Price range**: Filter by unit price (min/max)
- **Drug categories**: Filter by specific categories (IDs)

Multiple selections use comma-separated values:
```
departments=1,2,3
drug_categories=5,6,7
```
