# Frontend Implementation Prompt for Cursor Agent

## 🎯 Task: Implement Diagnostics API Integration in Next.js Frontend

### Context
I need to integrate the Diagnostics API endpoint into my Next.js frontend application. The API documentation is available at `docs/api/DIAGNOSTICS_API_DOCUMENTATION.md` in the backend project.

### API Endpoint Details

**Endpoint**: `GET /api/diagnostics/features/<drug_code>`

**Base URL**: Use environment variable `NEXT_PUBLIC_API_URL` (default: `http://localhost:5000`)

**Query Parameters**:
- `department` (optional, number): Department ID filter
- `start_date` (optional, string): Start date in `YYYY-MM-DD` format
- `end_date` (optional, string): End date in `YYYY-MM-DD` format
- `use_cache` (optional, boolean): Whether to use cache (default: `true`)

**Response Structure**:
```typescript
{
  success: boolean;
  data: {
    drug_code: string;
    department: number | null;
    data_health: {
      history_length_days: number;
      missing_days: number;
      missing_percentage: number;
      zero_demand_frequency: number;
      zero_demand_count: number;
      data_completeness_score: number;
      date_range: { start: string; end: string };
      outlier_count: number;
      outlier_percentage: number;
    };
    time_series_characteristics: {
      mean_demand: number;
      std_demand: number;
      volatility: number;
      trend: "increasing" | "decreasing" | "stable";
      min_demand: number;
      max_demand: number;
      median_demand: number;
      stationarity: string;
      seasonality_detected: boolean;
      seasonal_periods: number[];
      seasonality_strength: {
        weekly: number;
        monthly: number;
      };
    };
    outliers: {
      count: number;
      percentage: number;
      indices: string[];
      values: number[];
    };
    decomposition: {
      model: string;
      period: number;
      trend: { direction: string; strength: number };
      seasonal_strength: number;
      residual_variance: number;
      decomposition_quality: string;
    };
    acf_pacf: {
      significant_lags: number[];
      seasonal_lags: number[];
      arima_suggested_orders: { ar: number; ma: number; seasonal: boolean };
      acf_summary: { max_acf_lag: number; max_acf_value: number };
    };
    classification: {
      category: string;
      confidence: number;
      characteristics: {
        regular: boolean;
        seasonal: boolean;
        erratic: boolean;
      };
      metrics: {
        demand_frequency: number;
        zero_frequency: number;
        volatility: number;
        mean_demand: number;
        seasonal_strength: number;
      };
    };
    risks: {
      data_quality_issues: string[];
      forecast_reliability: "high" | "medium" | "low";
      recommendations: string[];
    };
    profiled_at: string;
  };
  meta: { status_code: number };
}
```

### Implementation Requirements

#### 1. **Create API Client** (`lib/api/diagnostics.ts`)
- Create a TypeScript file with:
  - All TypeScript interfaces/types for the response structure
  - Function `getDrugDiagnostics(params)` that:
    - Accepts: `{ drug_code: string, department?: number, start_date?: string, end_date?: string, use_cache?: boolean }`
    - Returns: Promise with typed response
    - Handles errors properly
    - Uses `fetch` API
    - Constructs query parameters correctly

#### 2. **Create React Hook** (`hooks/useDiagnostics.ts`)
- Create a custom React hook that:
  - Uses `useState` and `useEffect`
  - Accepts the same parameters as the API client
  - Returns: `{ data, loading, error }`
  - Automatically refetches when parameters change
  - Handles loading and error states

#### 3. **Create Type Definitions** (`types/diagnostics.ts`)
- Export all TypeScript interfaces:
  - `DiagnosticsParams`
  - `DiagnosticsResponse`
  - `DataHealth`
  - `TimeSeriesCharacteristics`
  - `Outliers`
  - `Decomposition`
  - `AcfPacf`
  - `Classification`
  - `Risks`
- Make sure all types are properly exported

#### 4. **Create Main Component** (`components/DiagnosticsDashboard.tsx`)
- Create a Next.js component (use `'use client'` directive)
- Component should:
  - Accept props: `{ drugCode: string, department?: number }`
  - Use the `useDiagnostics` hook
  - Display loading state (skeleton or spinner)
  - Display error state with helpful message
  - Display the diagnostics data in a well-organized layout

#### 5. **Create Visualization Components**

Create separate components for different sections:

**a. Data Health Section** (`components/diagnostics/DataHealthSection.tsx`)
- Display:
  - Data completeness score as a gauge/progress indicator
  - Outlier count and percentage
  - Zero demand frequency
  - Date range

**b. Classification Section** (`components/diagnostics/ClassificationSection.tsx`)
- Display:
  - Drug category as a badge
  - Confidence level as a progress bar
  - Characteristics (regular, seasonal, erratic) as icons/badges

**c. Time Series Characteristics** (`components/diagnostics/TimeSeriesSection.tsx`)
- Display:
  - Trend indicator (increasing/decreasing/stable) with visual arrow
  - Volatility gauge
  - Mean, median, min, max demand values
  - Stationarity status

**d. Seasonality Section** (`components/diagnostics/SeasonalitySection.tsx`)
- Display:
  - Seasonality detected status
  - Weekly and monthly strength as bars or gauges
  - Seasonal periods as badges

**e. Risk Assessment Section** (`components/diagnostics/RiskAssessmentSection.tsx`)
- Display:
  - Forecast reliability badge (high/medium/low) with color coding
  - Data quality issues as warning cards
  - Recommendations as actionable list items

#### 6. **Styling Requirements**
- Use Tailwind CSS (if available) or CSS modules
- Make the dashboard responsive (mobile, tablet, desktop)
- Use appropriate color coding:
  - Green for positive/good metrics
  - Yellow for medium/warning metrics
  - Red for negative/critical metrics
- Add proper spacing and typography
- Use cards/sections to organize content

#### 7. **Error Handling**
- Handle all error cases:
  - Network errors
  - 404 (no data found)
  - 400 (invalid parameters)
  - 500 (server errors)
- Show user-friendly error messages
- Provide retry functionality for failed requests

#### 8. **Loading States**
- Show skeleton loaders or spinners during data fetch
- Don't show empty states while loading
- Provide smooth transitions

### Example Usage

The final component should be usable like this:

```tsx
import { DiagnosticsDashboard } from '@/components/DiagnosticsDashboard';

export default function Page() {
  return (
    <DiagnosticsDashboard 
      drugCode="P182054" 
      department={5} 
    />
  );
}
```

### File Structure Expected

```
frontend/
├── lib/
│   └── api/
│       └── diagnostics.ts
├── hooks/
│   └── useDiagnostics.ts
├── types/
│   └── diagnostics.ts
└── components/
    ├── DiagnosticsDashboard.tsx
    └── diagnostics/
        ├── DataHealthSection.tsx
        ├── ClassificationSection.tsx
        ├── TimeSeriesSection.tsx
        ├── SeasonalitySection.tsx
        └── RiskAssessmentSection.tsx
```

### Additional Notes

1. **Environment Variable**: Make sure to use `NEXT_PUBLIC_API_URL` for the base URL
2. **Type Safety**: Ensure all types are properly defined and used
3. **Code Quality**: Follow Next.js and React best practices
4. **Accessibility**: Add proper ARIA labels and semantic HTML
5. **Performance**: Consider memoization for expensive calculations
6. **Testing**: Add basic error boundaries if possible

### What NOT to Include

- Do NOT create actual chart implementations (just the data display components)
- Do NOT add complex chart libraries unless already in the project
- Do NOT create backend code
- Do NOT modify existing API endpoints

### Success Criteria

✅ All TypeScript types are properly defined  
✅ API client correctly calls the endpoint  
✅ React hook manages state properly  
✅ Components display all relevant data  
✅ Error handling works for all cases  
✅ Loading states are shown appropriately  
✅ UI is responsive and well-styled  
✅ Code follows Next.js best practices  

---

## 🚀 Implementation Steps

1. Start by creating the type definitions
2. Create the API client function
3. Create the React hook
4. Create the main dashboard component
5. Create individual section components
6. Add styling and responsive design
7. Test error cases and loading states
8. Polish UI/UX

---

**Reference Documentation**: See `docs/api/DIAGNOSTICS_API_DOCUMENTATION.md` for complete API details and chart visualization ideas.

