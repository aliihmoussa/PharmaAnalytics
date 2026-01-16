# Cursor Agent Prompt: Diagnostics API Integration

Copy and paste this prompt into Cursor:

---

**Implement Diagnostics API integration for Next.js frontend:**

1. **API Endpoint**: `GET {NEXT_PUBLIC_API_URL}/api/diagnostics/features/<drug_code>`
   - Query params: `department?`, `start_date?`, `end_date?`, `use_cache?` (default: true)
   - Full docs: `docs/api/DIAGNOSTICS_API_DOCUMENTATION.md`

2. **Create these files:**
   - `lib/api/diagnostics.ts` - API client with TypeScript types
   - `hooks/useDiagnostics.ts` - React hook for data fetching
   - `types/diagnostics.ts` - All TypeScript interfaces
   - `components/DiagnosticsDashboard.tsx` - Main dashboard component
   - `components/diagnostics/DataHealthSection.tsx` - Data health metrics
   - `components/diagnostics/ClassificationSection.tsx` - Drug classification
   - `components/diagnostics/TimeSeriesSection.tsx` - Time series stats
   - `components/diagnostics/SeasonalitySection.tsx` - Seasonality analysis
   - `components/diagnostics/RiskAssessmentSection.tsx` - Risk & recommendations

3. **Response structure includes:**
   - `data_health`: completeness, outliers, zero demand frequency
   - `time_series_characteristics`: trend, volatility, seasonality
   - `classification`: category, confidence, characteristics
   - `risks`: forecast reliability, data quality issues, recommendations
   - `outliers`, `decomposition`, `acf_pacf`: detailed analysis

4. **Requirements:**
   - Full TypeScript type safety
   - Loading states (skeletons/spinners)
   - Error handling (404, 400, 500, network errors)
   - Responsive design (mobile/tablet/desktop)
   - Color coding: green (good), yellow (warning), red (critical)
   - Use Tailwind CSS or CSS modules

5. **Component usage:**
   ```tsx
   <DiagnosticsDashboard drugCode="P182054" department={5} />
   ```

6. **Display all metrics from the API response in organized sections with proper formatting and visual indicators.**

See full documentation at: `docs/api/DIAGNOSTICS_API_DOCUMENTATION.md`

---

