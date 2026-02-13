# Autocomplete Search Endpoints - Quick Reference

## Endpoints Overview

Two new autocomplete search endpoints have been added to the pharmacy analytics API:

### 1. Drug Search Endpoint
**URL:** `GET /api/analytics/drugs/search`

**Purpose:** Search for drugs by code or name for autocomplete functionality

**Query Parameters:**
- `q` (required): Search query - must be at least 3 characters
- `limit` (optional): Maximum number of results (default: 3, max: 50)

**Examples:**
```bash
# Search for drugs starting with "par"
curl "http://localhost:5000/api/analytics/drugs/search?q=par"

# Search with custom limit
curl "http://localhost:5000/api/analytics/drugs/search?q=par&limit=10"

# JavaScript/TypeScript fetch
fetch('/api/analytics/drugs/search?q=par&limit=5')
  .then(r => r.json())
  .then(data => console.log(data.data.results))
```

**Response Structure:**
```json
{
  "data": {
    "results": [
      {
        "id": "PAR001",
        "drug_code": "PAR001",
        "name": "Paracetamol 500mg"
      },
      {
        "id": "PAR002", 
        "drug_code": "PAR002",
        "name": "Paracetamol 1000mg"
      }
    ],
    "query": "par",
    "count": 2,
    "limit": 5
  },
  "meta": {
    "request_id": "123e4567-e89b-12d3-a456-426614174000",
    "status": "success"
  }
}
```

**Error Responses:**
```json
// Missing q parameter
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "q parameter is required"
  },
  "meta": {
    "status": "error"
  }
}

// Query too short
{
  "error": {
    "code": "VALIDATION_ERROR", 
    "message": "q parameter must be at least 3 characters"
  },
  "meta": {
    "status": "error"
  }
}
```

**Constraints:**
- ✅ Case-insensitive search
- ✅ Matches first 3+ characters of query
- ✅ Returns only active/available drugs (quantity < 0)
- ✅ Default limit: 3, Maximum limit: 50
- ✅ DISTINCT results (no duplicate drug codes)

---

### 2. Department Search Endpoint
**URL:** `GET /api/analytics/departments/search`

**Purpose:** Search for departments by ID or name for autocomplete functionality

**Query Parameters:**
- `q` (required): Search query
- `limit` (optional): Maximum number of results (default: 3, max: 50)

**Examples:**
```bash
# Search departments by ID
curl "http://localhost:5000/api/analytics/departments/search?q=1"

# Search departments by name
curl "http://localhost:5000/api/analytics/departments/search?q=ICU"

# With custom limit
curl "http://localhost:5000/api/analytics/departments/search?q=dept&limit=10"

# JavaScript/TypeScript
fetch('/api/analytics/departments/search?q=ICU')
  .then(r => r.json())
  .then(data => console.log(data.data.results))
```

**Response Structure:**
```json
{
  "data": {
    "results": [
      {
        "id": 5,
        "department_name": "Department 5"
      },
      {
        "id": 15,
        "department_name": "Department 15"
      }
    ],
    "query": "1",
    "count": 2,
    "limit": 3
  },
  "meta": {
    "request_id": "123e4567-e89b-12d3-a456-426614174000",
    "status": "success"
  }
}
```

**Error Response:**
```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "q parameter is required"
  },
  "meta": {
    "status": "error"
  }
}
```

**Constraints:**
- ✅ Searches by numeric ID first (exact match)
- ✅ Falls back to string prefix matching
- ✅ Case-insensitive search
- ✅ Default limit: 3, Maximum limit: 50
- ✅ DISTINCT department results

---

## Frontend Integration Example

### React/TypeScript Autocomplete Component

```typescript
import React, { useState, useEffect } from 'react';

interface Drug {
  id: string;
  drug_code: string;
  name: string;
}

interface DepartmentType {
  id: number;
  department_name: string;
}

export const DrugAutocomplete: React.FC = () => {
  const [input, setInput] = useState('');
  const [drugs, setDrugs] = useState<Drug[]>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (input.length < 3) {
      setDrugs([]);
      return;
    }

    setLoading(true);
    fetch(`/api/analytics/drugs/search?q=${encodeURIComponent(input)}&limit=5`)
      .then(r => r.json())
      .then(data => {
        if (data.data) {
          setDrugs(data.data.results);
        }
      })
      .finally(() => setLoading(false));
  }, [input]);

  return (
    <div>
      <input
        type="text"
        value={input}
        onChange={(e) => setInput(e.target.value)}
        placeholder="Search drugs (min 3 chars)..."
      />
      {loading && <p>Loading...</p>}
      <ul>
        {drugs.map(drug => (
          <li key={drug.id}>
            {drug.drug_code} - {drug.name}
          </li>
        ))}
      </ul>
    </div>
  );
};

export const DepartmentAutocomplete: React.FC = () => {
  const [input, setInput] = useState('');
  const [departments, setDepartments] = useState<DepartmentType[]>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!input) {
      setDepartments([]);
      return;
    }

    setLoading(true);
    fetch(`/api/analytics/departments/search?q=${encodeURIComponent(input)}&limit=5`)
      .then(r => r.json())
      .then(data => {
        if (data.data) {
          setDepartments(data.data.results);
        }
      })
      .finally(() => setLoading(false));
  }, [input]);

  return (
    <div>
      <input
        type="text"
        value={input}
        onChange={(e) => setInput(e.target.value)}
        placeholder="Search departments..."
      />
      {loading && <p>Loading...</p>}
      <ul>
        {departments.map(dept => (
          <li key={dept.id}>
            {dept.department_name}
          </li>
        ))}
      </ul>
    </div>
  );
};
```

---

## Testing

### Using cURL
```bash
# Test drug search
curl "http://localhost:5000/api/analytics/drugs/search?q=par&limit=3"

# Test department search  
curl "http://localhost:5000/api/analytics/departments/search?q=ICU"

# Test error case (query too short for drugs)
curl "http://localhost:5000/api/analytics/drugs/search?q=pa"
```

### Using Python requests
```python
import requests

# Drug search
response = requests.get(
    'http://localhost:5000/api/analytics/drugs/search',
    params={'q': 'par', 'limit': 5}
)
drugs = response.json()['data']['results']

# Department search
response = requests.get(
    'http://localhost:5000/api/analytics/departments/search',
    params={'q': '1', 'limit': 10}
)
departments = response.json()['data']['results']
```

### Run Test Suite
```bash
python test_search_endpoints.py
```

---

## Implementation Details

### Technologies Used
- **Framework:** Flask
- **Database ORM:** SQLAlchemy
- **Validation:** Pydantic
- **Database:** PostgreSQL (case-insensitive search using LOWER())

### Architecture
- **Request Models:** Pydantic models with validation
- **Data Access Layer:** AnalyticsDAL with context manager pattern
- **Service Layer:** DashboardService for business logic
- **Route Handlers:** Flask blueprints with error handling

### Performance Features
- ✅ Database-level case conversion (no Python overhead)
- ✅ DISTINCT clause prevents duplicates at query level
- ✅ Limit applied in SQL query (not in Python)
- ✅ Uses existing database indexes on drug_code, drug_name
- ✅ Efficient session management with context managers

---

## Support

For issues or questions about the endpoints:

1. Check the implementation details in `SEARCH_ENDPOINTS_IMPLEMENTATION.md`
2. Review the test script in `test_search_endpoints.py`
3. Check database connection in `backend/app/config.py`
4. Verify database has transaction data in `drug_transactions` table
