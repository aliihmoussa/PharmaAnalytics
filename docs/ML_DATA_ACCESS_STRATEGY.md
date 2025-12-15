# ML Data Access Strategy: PostgreSQL Direct Access vs Alternatives

## Executive Summary

**Direct PostgreSQL access is acceptable for initial ML development**, but **not optimal for production ML systems**. This document outlines the trade-offs and recommends a **hybrid approach** that evolves with your needs.

## Current Architecture Assessment

Your current setup:
- ✅ PostgreSQL database with well-indexed `drug_transactions` table
- ✅ Existing DAL (Data Access Layer) pattern in `AnalyticsDAL`
- ✅ Efficient SQL queries with proper indexing
- ✅ 4 years of historical data already ingested

## Direct PostgreSQL Access: Pros & Cons

### ✅ Advantages

1. **Single Source of Truth**
   - No data duplication
   - Always up-to-date data
   - Simpler architecture initially

2. **Existing Infrastructure**
   - Already have DAL pattern
   - Can reuse existing queries
   - No additional infrastructure needed

3. **Real-time Data**
   - Models can use latest data immediately
   - Good for inference/prediction

4. **PostgreSQL Capabilities**
   - Efficient aggregations (GROUP BY, window functions)
   - Good for time-series queries
   - Can leverage existing indexes

### ❌ Disadvantages

1. **Performance Issues**
   - **Large dataset queries**: Loading 4 years of data can be slow
   - **Feature engineering**: Complex transformations in Python vs SQL
   - **Repeated queries**: Training requires multiple data passes
   - **Memory constraints**: Loading full dataset into memory

2. **Database Load**
   - **Production impact**: Heavy ML queries can slow down production DB
   - **Resource contention**: ML training competes with operational queries
   - **Lock issues**: Long-running queries may block other operations

3. **Reproducibility**
   - **Data versioning**: Hard to reproduce exact training datasets
   - **Data drift**: Training data changes between runs
   - **Snapshot issues**: Can't easily compare model performance on same data

4. **Scalability**
   - **Limited parallelization**: Single database connection bottleneck
   - **Feature computation**: Repeated calculations for same features
   - **Model iteration**: Slow feedback loop during development

5. **Feature Engineering Limitations**
   - **Complex features**: Lag features, rolling windows harder in SQL
   - **Python ecosystem**: ML libraries expect NumPy/Pandas/Polars
   - **Iterative development**: Changing features requires new queries

## Recommended Approach: Hybrid Strategy

### Phase 1: Direct Access (Current - Acceptable for MVP)

**Use direct PostgreSQL access for:**
- ✅ Initial model development and prototyping
- ✅ Small-scale predictions (single drug, short time periods)
- ✅ Real-time inference (when you need latest data)
- ✅ Proof of concept

**Implementation:**
```python
# Reuse existing DAL pattern
from backend.app.modules.dashboard.queries import AnalyticsDAL

class MLDataLoader:
    def __init__(self):
        self.dal = AnalyticsDAL()
    
    def load_training_data(self, drug_code: str, start_date: date, end_date: date):
        """Load data directly from PostgreSQL."""
        with self.dal:
            # Use existing efficient queries
            return self.dal.get_drug_demand_time_series(
                start_date=start_date,
                end_date=end_date,
                drug_code=drug_code,
                granularity='daily'
            )
```

**Optimizations:**
- Use existing indexed queries
- Limit data range (e.g., last 2 years for training)
- Use database aggregations (GROUP BY, DATE_TRUNC)
- Batch queries by drug/department

### Phase 2: Materialized Views (Intermediate Solution)

**Create pre-aggregated views for ML:**

```sql
-- Example: Daily drug demand materialized view
CREATE MATERIALIZED VIEW ml_daily_drug_demand AS
SELECT 
    transaction_date,
    drug_code,
    drug_name,
    cat as category_id,
    cr as department_id,
    SUM(ABS(quantity)) FILTER (WHERE quantity < 0) as daily_demand,
    SUM(total_price) FILTER (WHERE quantity < 0) as daily_value,
    COUNT(*) FILTER (WHERE quantity < 0) as transaction_count
FROM drug_transactions
WHERE quantity < 0
GROUP BY transaction_date, drug_code, drug_name, cat, cr;

-- Create index for fast queries
CREATE INDEX idx_ml_demand_date_drug ON ml_daily_drug_demand(transaction_date, drug_code);

-- Refresh periodically (e.g., daily via cron)
REFRESH MATERIALIZED VIEW CONCURRENTLY ml_daily_drug_demand;
```

**Benefits:**
- ✅ Faster queries (pre-aggregated)
- ✅ Reduced database load
- ✅ Still uses PostgreSQL (no new infrastructure)
- ✅ Can refresh incrementally

**Use for:**
- Training data preparation
- Feature engineering base
- Regular model retraining

### Phase 3: Feature Store / ML-Optimized Tables (Production)

**Create dedicated ML feature tables:**

```sql
-- ML feature table with pre-computed features
CREATE TABLE ml_drug_features (
    feature_date DATE NOT NULL,
    drug_code VARCHAR(50) NOT NULL,
    department_id INTEGER,
    
    -- Raw features
    daily_demand INTEGER,
    daily_value NUMERIC(12, 2),
    
    -- Lag features (pre-computed)
    demand_lag_7d INTEGER,
    demand_lag_14d INTEGER,
    demand_lag_30d INTEGER,
    
    -- Rolling statistics (pre-computed)
    demand_mean_7d NUMERIC(10, 2),
    demand_mean_30d NUMERIC(10, 2),
    demand_std_7d NUMERIC(10, 2),
    
    -- Time features
    day_of_week INTEGER,
    month INTEGER,
    quarter INTEGER,
    is_weekend BOOLEAN,
    
    PRIMARY KEY (feature_date, drug_code, department_id)
);

CREATE INDEX idx_ml_features_date ON ml_drug_features(feature_date);
CREATE INDEX idx_ml_features_drug ON ml_drug_features(drug_code, feature_date);
```

**Populate via ETL pipeline:**
- Daily batch job (Celery task)
- Computes all features once
- ML models read from this table

**Benefits:**
- ✅ Fast model training (pre-computed features)
- ✅ Consistent features across models
- ✅ Feature versioning possible
- ✅ Minimal production DB impact

### Phase 4: Separate Analytics Database (Advanced)

**For large-scale ML:**
- Read replica of production DB
- Or separate analytics database
- ETL pipeline populates analytics DB
- ML models read from analytics DB

**Benefits:**
- ✅ Zero production impact
- ✅ Can optimize for analytics workloads
- ✅ Can use columnar storage (e.g., TimescaleDB)
- ✅ Better for large-scale training

## Detailed Comparison

| Approach | Performance | Production Impact | Complexity | Cost | Best For |
|----------|------------|-------------------|------------|------|----------|
| **Direct PostgreSQL** | ⭐⭐ | ⚠️ High | ⭐ Low | $ Low | MVP, POC |
| **Materialized Views** | ⭐⭐⭐ | ⭐ Low | ⭐⭐ Medium | $ Low | Small-scale ML |
| **Feature Tables** | ⭐⭐⭐⭐ | ⭐ Very Low | ⭐⭐⭐ Medium | $ Low | Production ML |
| **Analytics DB** | ⭐⭐⭐⭐⭐ | ⭐⭐ None | ⭐⭐⭐⭐ High | $$ Medium | Large-scale ML |

## Recommended Implementation Plan

### Immediate (Week 1-2): Direct Access with Optimizations

```python
# backend/app/modules/ml/utils/data_loader.py
from backend.app.modules.dashboard.queries import AnalyticsDAL
from datetime import date, timedelta
import polars as pl

class MLDataLoader:
    """Load ML training data from PostgreSQL with optimizations."""
    
    def __init__(self):
        self.dal = AnalyticsDAL()
    
    def load_drug_demand_data(
        self,
        drug_code: str,
        training_months: int = 24,
        granularity: str = 'daily'
    ) -> pl.DataFrame:
        """
        Load optimized training data.
        
        Optimizations:
        - Limit to recent data (configurable)
        - Use existing efficient queries
        - Aggregate at database level
        """
        end_date = date.today()
        start_date = end_date - timedelta(days=training_months * 30)
        
        with self.dal:
            # Use existing optimized query
            raw_data = self.dal.get_drug_demand_time_series(
                start_date=start_date,
                end_date=end_date,
                drug_code=drug_code,
                granularity=granularity
            )
        
        # Convert to Polars DataFrame
        df = pl.DataFrame(raw_data)
        
        # Parse dates
        df = df.with_columns(
            pl.col('date').str.strptime(pl.Date, format="%Y-%m-%d")
        )
        
        return df.sort('date')
    
    def load_multiple_drugs(
        self,
        drug_codes: list[str],
        training_months: int = 24
    ) -> pl.DataFrame:
        """Load data for multiple drugs efficiently."""
        all_data = []
        
        for drug_code in drug_codes:
            df = self.load_drug_demand_data(drug_code, training_months)
            df = df.with_columns(pl.lit(drug_code).alias('drug_code'))
            all_data.append(df)
        
        return pl.concat(all_data)
```

**Key Optimizations:**
1. Limit training window (e.g., last 24 months)
2. Use existing indexed queries
3. Aggregate at database level
4. Batch multiple drugs if needed
5. Use Polars for efficient processing

### Short-term (Month 1-2): Add Materialized Views

```sql
-- migrations/versions/xxx_add_ml_materialized_views.py
"""Add materialized views for ML training."""

def upgrade():
    op.execute("""
        CREATE MATERIALIZED VIEW ml_daily_drug_demand AS
        SELECT 
            transaction_date,
            drug_code,
            drug_name,
            cat as category_id,
            cr as department_id,
            SUM(ABS(quantity)) FILTER (WHERE quantity < 0) as daily_demand,
            SUM(total_price) FILTER (WHERE quantity < 0) as daily_value,
            COUNT(*) FILTER (WHERE quantity < 0) as transaction_count
        FROM drug_transactions
        WHERE quantity < 0
        GROUP BY transaction_date, drug_code, drug_name, cat, cr;
        
        CREATE INDEX idx_ml_demand_date_drug 
        ON ml_daily_drug_demand(transaction_date, drug_code);
    """)

def downgrade():
    op.execute("DROP MATERIALIZED VIEW IF EXISTS ml_daily_drug_demand;")
```

**Update data loader:**
```python
def load_from_materialized_view(self, drug_code: str, start_date: date, end_date: date):
    """Load from materialized view (faster)."""
    query = """
        SELECT * FROM ml_daily_drug_demand
        WHERE transaction_date BETWEEN %s AND %s
        AND drug_code = %s
        ORDER BY transaction_date
    """
    with self.dal:
        return self.dal.execute_query(query, (start_date, end_date, drug_code))
```

**Schedule refresh:**
```python
# backend/app/modules/ml/tasks.py (Celery task)
from backend.app.extensions import celery
from backend.app.database.connection import get_db_connection

@celery.task
def refresh_ml_materialized_views():
    """Refresh ML materialized views (run daily)."""
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("REFRESH MATERIALIZED VIEW CONCURRENTLY ml_daily_drug_demand")
        conn.commit()
    finally:
        close_db_connection(conn)
```

### Medium-term (Month 3-4): Feature Store Tables

Create dedicated feature computation pipeline:

```python
# backend/app/modules/ml/features/compute_features.py
from backend.app.modules.ml.tasks import celery
from datetime import date, timedelta
import polars as pl

@celery.task
def compute_ml_features(target_date: date = None):
    """
    Compute ML features for a given date.
    Run daily to populate feature table.
    """
    if target_date is None:
        target_date = date.today() - timedelta(days=1)
    
    # Load raw data
    loader = MLDataLoader()
    df = loader.load_drug_demand_data(
        drug_code=None,  # All drugs
        training_months=3  # Last 3 months for features
    )
    
    # Compute features
    df = create_lag_features(df, 'daily_demand', [7, 14, 30])
    df = create_rolling_features(df, 'daily_demand', [7, 30])
    df = create_time_features(df)
    
    # Store in feature table
    store_features(df, target_date)
```

## Performance Benchmarks (Expected)

| Operation | Direct PostgreSQL | Materialized View | Feature Table |
|-----------|------------------|-------------------|---------------|
| Load 1 drug, 2 years | 2-5 seconds | 0.5-1 second | 0.1-0.3 seconds |
| Load 10 drugs, 2 years | 20-50 seconds | 5-10 seconds | 1-3 seconds |
| Feature computation | Per query | Per query | Pre-computed |
| DB load impact | High | Medium | Low |

## Decision Matrix

### Use Direct PostgreSQL When:
- ✅ Building MVP/prototype
- ✅ Training on small datasets (< 100k rows)
- ✅ Infrequent model training (weekly/monthly)
- ✅ Single drug/department predictions
- ✅ Real-time inference needs latest data

### Use Materialized Views When:
- ✅ Regular model retraining (daily/weekly)
- ✅ Multiple drugs/departments
- ✅ Want faster queries without new infrastructure
- ✅ Can schedule refresh jobs

### Use Feature Tables When:
- ✅ Production ML system
- ✅ Frequent model training
- ✅ Complex feature engineering
- ✅ Need feature versioning
- ✅ Multiple models sharing features

### Use Analytics Database When:
- ✅ Large-scale ML (millions of rows)
- ✅ Zero tolerance for production impact
- ✅ Advanced analytics needs
- ✅ Budget for additional infrastructure

## Recommendations for Your Project

### ✅ **Start with Direct PostgreSQL** (Phase 1)
**Rationale:**
- You already have efficient queries and DAL
- 4 years of data is manageable with proper indexing
- Faster to implement and validate approach
- Can optimize queries as needed

**Implementation:**
1. Reuse `AnalyticsDAL` pattern
2. Add ML-specific query methods
3. Limit training windows (e.g., last 24 months)
4. Use database aggregations
5. Batch queries efficiently

### 🔄 **Add Materialized Views** (Phase 2 - After 1-2 months)
**Rationale:**
- Easy upgrade path
- Significant performance improvement
- No new infrastructure
- Can refresh incrementally

### 🚀 **Consider Feature Tables** (Phase 3 - Production)
**Rationale:**
- Best performance for production
- Enables feature versioning
- Supports multiple models
- Minimal production impact

## Code Example: Optimized Direct Access

```python
# backend/app/modules/ml/utils/data_loader.py
from backend.app.modules.dashboard.queries import AnalyticsDAL
from datetime import date, timedelta
import polars as pl
from typing import Optional

class OptimizedMLDataLoader:
    """
    Optimized data loader for ML training.
    Uses direct PostgreSQL access with best practices.
    """
    
    def __init__(self):
        self.dal = AnalyticsDAL()
    
    def load_training_dataset(
        self,
        drug_code: Optional[str] = None,
        department_id: Optional[int] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        training_months: int = 24,
        granularity: str = 'daily'
    ) -> pl.DataFrame:
        """
        Load optimized training dataset.
        
        Optimizations:
        1. Limit training window (default: 24 months)
        2. Use existing indexed queries
        3. Aggregate at database level
        4. Return Polars DataFrame for efficiency
        """
        # Set defaults
        if end_date is None:
            end_date = date.today()
        if start_date is None:
            start_date = end_date - timedelta(days=training_months * 30)
        
        with self.dal:
            # Use existing optimized query
            if drug_code:
                raw_data = self.dal.get_drug_demand_time_series(
                    start_date=start_date,
                    end_date=end_date,
                    drug_code=drug_code,
                    granularity=granularity
                )
            else:
                # Load all drugs (for multi-drug models)
                raw_data = self.dal.get_drug_demand_time_series(
                    start_date=start_date,
                    end_date=end_date,
                    drug_code=None,
                    granularity=granularity
                )
        
        if not raw_data:
            return pl.DataFrame()
        
        # Convert to Polars DataFrame
        df = pl.DataFrame(raw_data)
        
        # Ensure date column is proper date type
        if 'date' in df.columns:
            if df['date'].dtype == pl.Utf8:
                df = df.with_columns(
                    pl.col('date').str.strptime(pl.Date, format="%Y-%m-%d")
                )
            df = df.sort('date')
        
        return df
    
    def load_with_filters(
        self,
        filters: dict,
        training_months: int = 24
    ) -> pl.DataFrame:
        """Load data with flexible filters."""
        return self.load_training_dataset(
            drug_code=filters.get('drug_code'),
            department_id=filters.get('department_id'),
            training_months=training_months,
            granularity=filters.get('granularity', 'daily')
        )
```

## Conclusion

**Direct PostgreSQL access is acceptable for your initial ML implementation**, especially given:
- Your existing efficient DAL pattern
- Well-indexed database
- Manageable data volume (4 years)
- Need for rapid development

**However, plan for evolution:**
1. **Start**: Direct access with optimizations
2. **Evolve**: Add materialized views for performance
3. **Scale**: Implement feature tables for production
4. **Advanced**: Consider analytics database if needed

The key is to **start simple and optimize based on actual needs** rather than over-engineering upfront.

---

**Next Steps:**
1. Implement optimized direct access loader
2. Monitor query performance
3. Add materialized views when needed
4. Plan feature store for production

