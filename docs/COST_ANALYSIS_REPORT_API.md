# Cost Analysis Report Generation API

## Overview

The Cost Analysis Report Generation API allows you to generate professional DOCX and PDF reports containing pharmaceutical cost analysis data. The reports include comprehensive summaries, charts, tables, and detailed analysis.

## Endpoint

```
GET /api/analytics/cost-analysis/report
```

## Query Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `start_date` | string (YYYY-MM-DD) | Yes | Start date for analysis period |
| `end_date` | string (YYYY-MM-DD) | Yes | End date for analysis period |
| `format` | string | No | Report format: `docx` or `pdf` (default: `docx`) |
| `departments` | integer[] | No | Filter by department IDs (comma-separated) |
| `price_min` | float | No | Minimum unit price filter |
| `price_max` | float | No | Maximum unit price filter |
| `drug_categories` | integer[] | No | Filter by drug category IDs (comma-separated) |

## Response

The endpoint returns a downloadable file (binary data) in the requested format:
- **DOCX**: Microsoft Word document (.docx)
- **PDF**: Adobe PDF document (.pdf)

### HTTP Headers

```
Content-Type: application/vnd.openxmlformats-officedocument.wordprocessingml.document (for DOCX)
Content-Type: application/pdf (for PDF)
Content-Disposition: attachment; filename="Cost_Analysis_Report_YYYYMMDD_HHMMSS.docx|pdf"
```

## Report Contents

### 1. Cover Page
- Report title
- Report generation date and time
- Analysis period

### 2. Executive Summary
- Total pharmaceutical cost during the period
- Top cost driver drug
- Key insights

### 3. Analysis Parameters
- Applied filters in a structured table format
- Search criteria used for the report

### 4. Cost Overview
- Cost breakdown by department
- Number of drugs in each department
- Cost per department

### 5. Top 20 Cost Drivers
- Ranked list of drugs by total cost
- Drug name, total cost, units, average price
- Professional table formatting

### 6. Cost Trends
- Monthly cost progression
- Cost-to-cost comparison (% change)
- Trend analysis

### 7. Department Analysis
- Department-wise cost breakdown
- Number of drugs per department
- Average cost calculations

### 8. Drug Category Analysis
- Category-wise cost distribution
- Percentage of total cost per category
- Drug count per category

## Usage Examples

### JavaScript/Frontend

#### Generate DOCX Report
```javascript
async function downloadCostAnalysisReportDocx() {
  const params = new URLSearchParams({
    start_date: '2019-01-01',
    end_date: '2019-12-31',
    format: 'docx',
    departments: '1,2,3',
    price_min: 10.0,
    price_max: 1000.0
  });
  
  try {
    const response = await fetch(`/api/analytics/cost-analysis/report?${params}`, {
      method: 'GET',
    });
    
    if (!response.ok) {
      throw new Error('Failed to generate report');
    }
    
    // Create blob from response
    const blob = await response.blob();
    
    // Create download link
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `Cost_Analysis_Report_${new Date().getTime()}.docx`;
    document.body.appendChild(link);
    link.click();
    
    // Cleanup
    document.body.removeChild(link);
    window.URL.revokeObjectURL(url);
  } catch (error) {
    console.error('Error downloading report:', error);
  }
}
```

#### Generate PDF Report
```javascript
async function downloadCostAnalysisReportPdf() {
  const params = new URLSearchParams({
    start_date: '2019-01-01',
    end_date: '2019-12-31',
    format: 'pdf',
    departments: '1,2,3'
  });
  
  try {
    const response = await fetch(`/api/analytics/cost-analysis/report?${params}`, {
      method: 'GET',
    });
    
    if (!response.ok) {
      throw new Error('Failed to generate report');
    }
    
    const blob = await response.blob();
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `Cost_Analysis_Report_${new Date().getTime()}.pdf`;
    document.body.appendChild(link);
    link.click();
    
    document.body.removeChild(link);
    window.URL.revokeObjectURL(url);
  } catch (error) {
    console.error('Error downloading report:', error);
  }
}
```

#### React Component Example
```jsx
import React, { useState } from 'react';

export function CostAnalysisReportDownloader() {
  const [isLoading, setIsLoading] = useState(false);
  const [format, setFormat] = useState('docx');
  const [dateRange, setDateRange] = useState({
    startDate: '2019-01-01',
    endDate: '2019-12-31'
  });

  const handleDownload = async () => {
    setIsLoading(true);
    try {
      const params = new URLSearchParams({
        start_date: dateRange.startDate,
        end_date: dateRange.endDate,
        format: format,
        departments: '1,2,3'
      });

      const response = await fetch(
        `/api/analytics/cost-analysis/report?${params}`,
        { method: 'GET' }
      );

      if (!response.ok) throw new Error('Failed to generate report');

      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `Cost_Analysis_Report_${new Date().getTime()}.${format}`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      window.URL.revokeObjectURL(url);
    } catch (error) {
      alert(`Error: ${error.message}`);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div style={{ padding: '20px', border: '1px solid #ccc', borderRadius: '8px' }}>
      <h2>Generate Cost Analysis Report</h2>
      
      <div style={{ marginBottom: '10px' }}>
        <label>
          Start Date:
          <input
            type="date"
            value={dateRange.startDate}
            onChange={(e) => setDateRange({ ...dateRange, startDate: e.target.value })}
          />
        </label>
      </div>

      <div style={{ marginBottom: '10px' }}>
        <label>
          End Date:
          <input
            type="date"
            value={dateRange.endDate}
            onChange={(e) => setDateRange({ ...dateRange, endDate: e.target.value })}
          />
        </label>
      </div>

      <div style={{ marginBottom: '10px' }}>
        <label>
          Format:
          <select value={format} onChange={(e) => setFormat(e.target.value)}>
            <option value="docx">Word Document (DOCX)</option>
            <option value="pdf">PDF Document</option>
          </select>
        </label>
      </div>

      <button 
        onClick={handleDownload} 
        disabled={isLoading}
        style={{
          padding: '10px 20px',
          backgroundColor: '#1f4788',
          color: 'white',
          border: 'none',
          borderRadius: '4px',
          cursor: isLoading ? 'not-allowed' : 'pointer',
          opacity: isLoading ? 0.6 : 1
        }}
      >
        {isLoading ? 'Generating Report...' : 'Download Report'}
      </button>
    </div>
  );
}

export default CostAnalysisReportDownloader;
```

#### Vue Component Example
```vue
<template>
  <div class="report-downloader">
    <h2>Generate Cost Analysis Report</h2>
    
    <div class="form-group">
      <label>Start Date:</label>
      <input 
        type="date" 
        v-model="dateRange.startDate"
      />
    </div>

    <div class="form-group">
      <label>End Date:</label>
      <input 
        type="date" 
        v-model="dateRange.endDate"
      />
    </div>

    <div class="form-group">
      <label>Format:</label>
      <select v-model="format">
        <option value="docx">Word Document (DOCX)</option>
        <option value="pdf">PDF Document</option>
      </select>
    </div>

    <button 
      @click="handleDownload" 
      :disabled="isLoading"
      class="download-btn"
    >
      {{ isLoading ? 'Generating Report...' : 'Download Report' }}
    </button>
  </div>
</template>

<script>
export default {
  data() {
    return {
      isLoading: false,
      format: 'docx',
      dateRange: {
        startDate: '2019-01-01',
        endDate: '2019-12-31'
      }
    };
  },
  methods: {
    async handleDownload() {
      this.isLoading = true;
      try {
        const params = new URLSearchParams({
          start_date: this.dateRange.startDate,
          end_date: this.dateRange.endDate,
          format: this.format,
          departments: '1,2,3'
        });

        const response = await fetch(
          `/api/analytics/cost-analysis/report?${params}`,
          { method: 'GET' }
        );

        if (!response.ok) throw new Error('Failed to generate report');

        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.download = `Cost_Analysis_Report_${new Date().getTime()}.${this.format}`;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        window.URL.revokeObjectURL(url);
      } catch (error) {
        alert(`Error: ${error.message}`);
      } finally {
        this.isLoading = false;
      }
    }
  }
};
</script>

<style scoped>
.report-downloader {
  padding: 20px;
  border: 1px solid #ccc;
  border-radius: 8px;
  max-width: 400px;
}

.form-group {
  margin-bottom: 15px;
}

.form-group label {
  display: block;
  margin-bottom: 5px;
  font-weight: bold;
}

.form-group input,
.form-group select {
  width: 100%;
  padding: 8px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
}

.download-btn {
  width: 100%;
  padding: 12px;
  background-color: #1f4788;
  color: white;
  border: none;
  border-radius: 4px;
  font-size: 16px;
  font-weight: bold;
  cursor: pointer;
  transition: background-color 0.3s;
}

.download-btn:hover:not(:disabled) {
  background-color: #163a60;
}

.download-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}
</style>
```

### cURL Examples

#### DOCX Report
```bash
curl -X GET "http://localhost:5000/api/analytics/cost-analysis/report?start_date=2019-01-01&end_date=2019-12-31&format=docx" \
  -o Cost_Analysis_Report.docx
```

#### PDF Report
```bash
curl -X GET "http://localhost:5000/api/analytics/cost-analysis/report?start_date=2019-01-01&end_date=2019-12-31&format=pdf&departments=1,2,3" \
  -o Cost_Analysis_Report.pdf
```

### Python Example

```python
import requests
from datetime import datetime

def download_cost_analysis_report(
    start_date='2019-01-01',
    end_date='2019-12-31',
    format='pdf',
    departments=None
):
    """Download cost analysis report."""
    
    params = {
        'start_date': start_date,
        'end_date': end_date,
        'format': format
    }
    
    if departments:
        params['departments'] = ','.join(map(str, departments))
    
    response = requests.get(
        'http://localhost:5000/api/analytics/cost-analysis/report',
        params=params
    )
    
    if response.status_code == 200:
        # Save to file
        filename = f"Cost_Analysis_Report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{format}"
        with open(filename, 'wb') as f:
            f.write(response.content)
        print(f"Report saved as {filename}")
    else:
        print(f"Error: {response.status_code} - {response.text}")

# Usage
download_cost_analysis_report(
    start_date='2019-01-01',
    end_date='2019-12-31',
    format='pdf',
    departments=[1, 2, 3]
)
```

## Error Handling

### Possible Error Responses

| Status Code | Error | Description |
|-------------|-------|-------------|
| 400 | Invalid format | Format must be "docx" or "pdf" |
| 400 | Invalid date format | Dates must be in YYYY-MM-DD format |
| 404 | No data found | No cost data found for the specified filters |
| 500 | Internal server error | Server error during report generation |

### Example Error Response

```json
{
  "error": "Invalid format. Must be \"docx\" or \"pdf\""
}
```

## Performance Notes

- Reports are generated on-demand and may take 5-30 seconds depending on data volume
- For large date ranges and multiple filters, report generation may take longer
- Consider implementing progress indicators in your frontend during generation
- Reports are not cached; each request generates a new report

## Best Practices

1. **User Experience**
   - Show a loading indicator while the report is being generated
   - Disable the download button during generation
   - Provide feedback on generation progress if possible

2. **Error Handling**
   - Handle network errors gracefully
   - Validate user inputs before sending requests
   - Show user-friendly error messages

3. **Performance**
   - Consider limiting date ranges for initial loads
   - Implement caching on the frontend if generating the same report frequently
   - Use appropriate file formats based on user needs (DOCX for editing, PDF for sharing)

4. **Security**
   - Validate all date parameters
   - Ensure proper authentication/authorization
   - Sanitize any user-provided parameters
