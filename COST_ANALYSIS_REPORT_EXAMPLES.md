# Cost Analysis Report API - Response Examples & Integration Guide

## 📌 Overview

The Cost Analysis Report API generates downloadable professional reports in DOCX or PDF format. This document provides practical examples and integration patterns.

## 🎯 Endpoint

```
GET /api/analytics/cost-analysis/report
```

## 📨 HTTP Response Details

### Success Response (200)

```
HTTP/1.1 200 OK
Content-Type: application/pdf
Content-Disposition: attachment; filename="Cost_Analysis_Report_20240214_143022.pdf"
Content-Length: 245891
Cache-Control: no-cache, no-store, must-revalidate
Pragma: no-cache
Expires: 0

[Binary PDF content]
```

**For DOCX Format:**
```
HTTP/1.1 200 OK
Content-Type: application/vnd.openxmlformats-officedocument.wordprocessingml.document
Content-Disposition: attachment; filename="Cost_Analysis_Report_20240214_143022.docx"
Content-Length: 385642
Cache-Control: no-cache, no-store, must-revalidate
Pragma: no-cache
Expires: 0

[Binary DOCX content]
```

### Error Response (400 - Invalid Format)

```json
HTTP/1.1 400 Bad Request
Content-Type: application/json

{
  "error": "Invalid format. Must be \"docx\" or \"pdf\""
}
```

### Error Response (400 - Missing Parameters)

```json
HTTP/1.1 400 Bad Request
Content-Type: application/json

{
  "error": "Missing required field: start_date"
}
```

### Error Response (404 - No Data Found)

```json
HTTP/1.1 404 Not Found
Content-Type: application/json

{
  "error": "No cost data found for the specified filters"
}
```

### Error Response (500 - Server Error)

```json
HTTP/1.1 500 Internal Server Error
Content-Type: application/json

{
  "error": "Internal server error occurred during report generation"
}
```

---

## 💻 Frontend Integration Examples

### 1. Vanilla JavaScript - Basic Download

```javascript
async function downloadReport() {
  const params = new URLSearchParams({
    start_date: '2019-01-01',
    end_date: '2019-12-31',
    format: 'pdf'
  });

  const response = await fetch(`/api/analytics/cost-analysis/report?${params}`);
  
  if (!response.ok) {
    const error = await response.json();
    console.error('Error:', error.error);
    return;
  }

  const blob = await response.blob();
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = 'report.pdf';
  a.click();
  URL.revokeObjectURL(url);
}
```

### 2. Vanilla JavaScript - With Error Handling

```javascript
async function downloadReportWithErrorHandling(format = 'docx', startDate, endDate) {
  try {
    if (!startDate || !endDate) {
      throw new Error('Please provide both start and end dates');
    }

    if (!['docx', 'pdf'].includes(format)) {
      throw new Error('Format must be "docx" or "pdf"');
    }

    const params = new URLSearchParams({
      start_date: startDate,
      end_date: endDate,
      format: format
    });

    console.log(`Downloading report: ${params.toString()}`);
    
    const response = await fetch(`/api/analytics/cost-analysis/report?${params}`);

    if (!response.ok) {
      const contentType = response.headers.get('content-type');
      if (contentType && contentType.includes('application/json')) {
        const error = await response.json();
        throw new Error(error.error || `HTTP ${response.status}`);
      } else {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }
    }

    const blob = await response.blob();
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `Cost_Analysis_Report_${Date.now()}.${format}`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);

    console.log('Report downloaded successfully');
  } catch (error) {
    console.error('Report download failed:', error.message);
    alert(`Error: ${error.message}`);
  }
}
```

### 3. React Component - With Loading State

```jsx
import React, { useState } from 'react';

function CostReportDownloader() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [dates, setDates] = useState({
    startDate: '2019-01-01',
    endDate: '2019-12-31'
  });

  const handleDownload = async (format) => {
    setLoading(true);
    setError(null);

    try {
      const params = new URLSearchParams({
        start_date: dates.startDate,
        end_date: dates.endDate,
        format: format
      });

      const response = await fetch(
        `/api/analytics/cost-analysis/report?${params}`
      );

      if (!response.ok) {
        const contentType = response.headers.get('content-type');
        if (contentType?.includes('application/json')) {
          const error = await response.json();
          throw new Error(error.error);
        }
        throw new Error(`HTTP ${response.status}`);
      }

      const blob = await response.blob();
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `report.${format}`;
      a.click();
      URL.revokeObjectURL(url);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ padding: '20px' }}>
      <h2>Generate Cost Analysis Report</h2>

      <div>
        <label>
          Start Date:
          <input
            type="date"
            value={dates.startDate}
            onChange={(e) =>
              setDates({ ...dates, startDate: e.target.value })
            }
            disabled={loading}
          />
        </label>
      </div>

      <div>
        <label>
          End Date:
          <input
            type="date"
            value={dates.endDate}
            onChange={(e) =>
              setDates({ ...dates, endDate: e.target.value })
            }
            disabled={loading}
          />
        </label>
      </div>

      <div style={{ marginTop: '20px' }}>
        <button
          onClick={() => handleDownload('pdf')}
          disabled={loading}
        >
          {loading ? 'Generating...' : 'Download PDF'}
        </button>
        <button
          onClick={() => handleDownload('docx')}
          disabled={loading}
          style={{ marginLeft: '10px' }}
        >
          {loading ? 'Generating...' : 'Download DOCX'}
        </button>
      </div>

      {error && (
        <div style={{ color: 'red', marginTop: '20px' }}>
          Error: {error}
        </div>
      )}
    </div>
  );
}

export default CostReportDownloader;
```

### 4. React Hook - Reusable

```jsx
import { useState, useCallback } from 'react';

export function useCostAnalysisReport() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const generateReport = useCallback(async (options) => {
    const {
      startDate,
      endDate,
      format = 'pdf',
      departments = null,
      priceMin = null,
      priceMax = null,
      drugCategories = null
    } = options;

    setLoading(true);
    setError(null);

    try {
      const params = new URLSearchParams({
        start_date: startDate,
        end_date: endDate,
        format
      });

      if (departments) {
        params.append('departments', Array.isArray(departments) ? departments.join(',') : departments);
      }
      if (priceMin) params.append('price_min', priceMin);
      if (priceMax) params.append('price_max', priceMax);
      if (drugCategories) {
        params.append('drug_categories', Array.isArray(drugCategories) ? drugCategories.join(',') : drugCategories);
      }

      const response = await fetch(
        `/api/analytics/cost-analysis/report?${params}`
      );

      if (!response.ok) {
        const contentType = response.headers.get('content-type');
        if (contentType?.includes('application/json')) {
          const { error } = await response.json();
          throw new Error(error);
        }
        throw new Error(`HTTP ${response.status}`);
      }

      const blob = await response.blob();
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `Cost_Analysis_Report_${Date.now()}.${format}`;
      a.click();
      URL.revokeObjectURL(url);

      return { success: true };
    } catch (err) {
      const message = err.message || 'Failed to generate report';
      setError(message);
      return { success: false, error: message };
    } finally {
      setLoading(false);
    }
  }, []);

  return { generateReport, loading, error };
}

// Usage:
function MyComponent() {
  const { generateReport, loading } = useCostAnalysisReport();

  return (
    <button
      onClick={() =>
        generateReport({
          startDate: '2019-01-01',
          endDate: '2019-12-31',
          format: 'pdf',
          departments: [1, 2, 3]
        })
      }
      disabled={loading}
    >
      {loading ? 'Generating...' : 'Download Report'}
    </button>
  );
}
```

### 5. Vue 3 Composable

```javascript
import { ref } from 'vue';

export function useCostAnalysisReport() {
  const loading = ref(false);
  const error = ref(null);

  const generateReport = async (options) => {
    const {
      startDate,
      endDate,
      format = 'pdf',
      departments = null,
      priceMin = null,
      priceMax = null,
      drugCategories = null
    } = options;

    loading.value = true;
    error.value = null;

    try {
      const params = new URLSearchParams({
        start_date: startDate,
        end_date: endDate,
        format
      });

      if (departments) {
        params.append('departments', Array.isArray(departments) ? departments.join(',') : departments);
      }
      if (priceMin) params.append('price_min', priceMin);
      if (priceMax) params.append('price_max', priceMax);
      if (drugCategories) {
        params.append('drug_categories', Array.isArray(drugCategories) ? drugCategories.join(',') : drugCategories);
      }

      const response = await fetch(
        `/api/analytics/cost-analysis/report?${params}`
      );

      if (!response.ok) {
        const contentType = response.headers.get('content-type');
        if (contentType?.includes('application/json')) {
          const { error } = await response.json();
          throw new Error(error);
        }
        throw new Error(`HTTP ${response.status}`);
      }

      const blob = await response.blob();
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `Cost_Analysis_Report_${Date.now()}.${format}`;
      a.click();
      URL.revokeObjectURL(url);

      return { success: true };
    } catch (err) {
      const message = err.message || 'Failed to generate report';
      error.value = message;
      return { success: false, error: message };
    } finally {
      loading.value = false;
    }
  };

  return { generateReport, loading, error };
}
```

### 6. Vue Component

```vue
<template>
  <div class="report-generator">
    <h2>Generate Cost Analysis Report</h2>

    <div class="date-inputs">
      <input
        v-model="dates.startDate"
        type="date"
        :disabled="loading"
      />
      <input
        v-model="dates.endDate"
        type="date"
        :disabled="loading"
      />
    </div>

    <div class="filters">
      <input
        v-model="filters.departments"
        type="text"
        placeholder="Departments (comma-separated)"
        :disabled="loading"
      />
      <input
        v-model="filters.priceMin"
        type="number"
        placeholder="Min Price"
        :disabled="loading"
      />
      <input
        v-model="filters.priceMax"
        type="number"
        placeholder="Max Price"
        :disabled="loading"
      />
    </div>

    <div class="buttons">
      <button
        @click="handleDownload('pdf')"
        :disabled="loading"
      >
        {{ loading ? 'Generating...' : 'Download PDF' }}
      </button>
      <button
        @click="handleDownload('docx')"
        :disabled="loading"
      >
        {{ loading ? 'Generating...' : 'Download DOCX' }}
      </button>
    </div>

    <div v-if="error" class="error">
      Error: {{ error }}
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { useCostAnalysisReport } from './composables/useCostAnalysisReport';

const { generateReport, loading, error } = useCostAnalysisReport();

const dates = ref({
  startDate: '2019-01-01',
  endDate: '2019-12-31'
});

const filters = ref({
  departments: null,
  priceMin: null,
  priceMax: null
});

const handleDownload = async (format) => {
  await generateReport({
    startDate: dates.value.startDate,
    endDate: dates.value.endDate,
    format,
    departments: filters.value.departments,
    priceMin: filters.value.priceMin,
    priceMax: filters.value.priceMax
  });
};
</script>

<style scoped>
.report-generator {
  max-width: 500px;
  padding: 20px;
}

.date-inputs,
.buttons {
  display: flex;
  gap: 10px;
  margin: 20px 0;
}

input {
  padding: 8px;
  border: 1px solid #ddd;
  border-radius: 4px;
  flex: 1;
}

button {
  padding: 8px 16px;
  background: #1f4788;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.error {
  color: red;
  margin-top: 20px;
}
</style>
```

### 7. Angular Service

```typescript
import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, throwError } from 'rxjs';
import { catchError } from 'rxjs/operators';

@Injectable({
  providedIn: 'root'
})
export class CostAnalysisReportService {
  private apiUrl = '/api/analytics/cost-analysis/report';

  constructor(private http: HttpClient) {}

  downloadReport(options: {
    startDate: string;
    endDate: string;
    format?: 'pdf' | 'docx';
    departments?: string;
    priceMin?: number;
    priceMax?: number;
    drugCategories?: string;
  }): Observable<Blob> {
    let params = `start_date=${options.startDate}&end_date=${options.endDate}&format=${options.format || 'pdf'}`;

    if (options.departments) {
      params += `&departments=${options.departments}`;
    }
    if (options.priceMin) {
      params += `&price_min=${options.priceMin}`;
    }
    if (options.priceMax) {
      params += `&price_max=${options.priceMax}`;
    }
    if (options.drugCategories) {
      params += `&drug_categories=${options.drugCategories}`;
    }

    return this.http
      .get(`${this.apiUrl}?${params}`, { responseType: 'blob' })
      .pipe(catchError(this.handleError));
  }

  private handleError(error: any) {
    console.error('API Error:', error);
    return throwError(() => new Error('Failed to download report'));
  }
}
```

---

## 🎯 Common Use Cases

### 1. Report for Entire Year
```javascript
downloadReport({
  startDate: '2019-01-01',
  endDate: '2019-12-31',
  format: 'pdf'
});
```

### 2. Department-Specific Report
```javascript
downloadReport({
  startDate: '2019-06-01',
  endDate: '2019-12-31',
  format: 'docx',
  departments: '1,2,3'
});
```

### 3. High-Cost Drugs Only
```javascript
downloadReport({
  startDate: '2019-01-01',
  endDate: '2019-12-31',
  format: 'pdf',
  priceMin: 100
});
```

### 4. Specific Category Analysis
```javascript
downloadReport({
  startDate: '2019-01-01',
  endDate: '2019-12-31',
  format: 'docx',
  drugCategories: '5,6,7'
});
```

---

## ✅ Checklist for Integration

- [ ] Install required packages: `pip install -r requirements.txt`
- [ ] Verify backend server is running: `python run.py`
- [ ] Test API endpoint with test script: `python test_report_api.py`
- [ ] Copy appropriate code example for your framework
- [ ] Integrate into your frontend component
- [ ] Test with various date ranges and filters
- [ ] Verify file downloads work correctly
- [ ] Test error handling scenarios
- [ ] Deploy to production

---

Done! Your reports are ready to generate! 🎉
