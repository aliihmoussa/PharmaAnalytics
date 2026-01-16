# Domain Features Explanation

## 🎯 What is `domain_features.py`?

`domain_features.py` is a **feature engineering module** that creates **domain-specific business features** for drug transaction forecasting. Unlike generic time-series features (lags, rolling means, etc.), these features capture **business context** specific to pharmaceutical operations.

---

## 📋 What It Does

Creates **6 categories of domain-specific features**:

### **1. Department Features** (`create_department_features`)
- **Department demand ratio**: Ratio of demand from top consuming department
- **Department diversity**: Number of unique consuming departments per day
- **Supply department ratio**: Ratio of demand from top supplying department

**Purpose**: Captures which departments drive demand and supply patterns

### **2. Category Features** (`create_category_features`)
- **Category trend**: Rolling mean of category demand (7-day, 30-day)
- **Category stability**: Coefficient of variation (volatility measure)

**Purpose**: Captures drug category-level demand patterns and stability

### **3. Room/Bed Features** (`create_room_bed_features`)
- **Room diversity**: Number of unique rooms per day
- **Bed diversity**: Number of unique beds per day
- **Average demand per room**: Demand divided by room count

**Purpose**: Captures spatial distribution of drug consumption

### **4. Transaction Features** (`create_transaction_features`)
- **Transaction count**: Number of transactions per day
- **Average transaction size**: Average quantity per transaction
- **Transaction size variability**: Rolling standard deviation of transaction sizes

**Purpose**: Captures transaction patterns and variability

### **5. Price Features** (`create_price_features`)
- **Unit price**: Average unit price
- **Price stability**: Coefficient of variation of prices
- **Price trends**: Rolling mean of prices (7-day, 30-day)

**Purpose**: Captures pricing patterns and their relationship to demand

### **6. Admission Features** (`create_admission_features`)
- **Admission lag**: Days between patient admission and transaction
- **Has admission date**: Binary indicator
- **Admission lag statistics**: Rolling mean of admission lags

**Purpose**: Captures relationship between patient admissions and drug demand

---

## 🔄 Where It's Used

### **Call Chain:**

```
1. API Request
   ↓
2. ForecastService.forecast()
   ↓
3. prepare_features(use_domain_features=True)
   ↓
4. create_domain_features()  ← domain_features.py
```

### **1. In `service_enhanced.py` (Line 114)**
```python
features_df = prepare_features(
    daily_data,
    target_col='QTY',
    use_domain_features=True  # ← Enables domain features
)
```

### **2. In `xgboost_features.py` (Lines 203-209)**
```python
# Add domain-specific features if requested
if use_domain_features:
    try:
        from backend.app.modules.forecasting.features.domain_features import create_domain_features
        logger.info("Creating domain-specific features...")
        features_df = create_domain_features(features_df, target_col=target_col)
    except Exception as e:
        logger.warning(f"Could not create domain features: {str(e)}")
```

---

## 📊 Feature Engineering Pipeline

### **Complete Feature Creation Flow:**

```
1. Time-based features (day, month, year, etc.)
   ↓
2. Cyclical features (sin/cos of day of week, month, etc.)
   ↓
3. Lag features (demand 1 day ago, 7 days ago, etc.)
   ↓
4. Rolling statistics (7-day mean, 30-day std, etc.)
   ↓
5. Difference features (day-over-day change, etc.)
   ↓
6. Binary features (is_weekend, is_month_end, etc.)
   ↓
7. Domain features ← domain_features.py (if enabled)
   ├── Department features
   ├── Category features
   ├── Room/bed features
   ├── Transaction features
   ├── Price features
   └── Admission features
```

---

## 🎯 Why Domain Features Matter

### **Generic Features (from `xgboost_features.py`):**
- ✅ Work for any time-series
- ✅ Capture temporal patterns
- ❌ Don't understand business context

### **Domain Features (from `domain_features.py`):**
- ✅ Understand pharmaceutical operations
- ✅ Capture business relationships (departments, categories, rooms)
- ✅ Improve forecast accuracy with business context
- ✅ Help model understand "why" demand changes

### **Example:**
- **Generic feature**: "Demand 7 days ago = 50"
- **Domain feature**: "Top department demand ratio = 0.8" (80% of demand from one department)

The domain feature tells the model that demand is concentrated, which is valuable business context.

---

## 🔧 How It Works

### **Input:**
- DataFrame with daily aggregated transaction data
- Must include metadata columns: `cr`, `cs`, `cat`, `unit_price`, `ad_date`, etc.

### **Process:**
1. Creates features for each category (department, category, room, etc.)
2. Handles missing columns gracefully (sets defaults)
3. Removes non-numeric columns (XGBoost requirement)
4. Fills NaN values with 0

### **Output:**
- DataFrame with all domain-specific features added
- All features are numeric (ready for XGBoost)

---

## 📝 Example Features Created

### **Department Features:**
- `dept_demand_ratio`: 0.0 to 1.0 (ratio of top department demand)
- `dept_diversity`: Integer (number of unique departments)
- `supply_dept_ratio`: 0.0 to 1.0 (ratio of top supply department)

### **Category Features:**
- `category_trend`: Float (7-day rolling mean)
- `category_trend_30`: Float (30-day rolling mean)
- `category_stability`: Float (coefficient of variation)

### **Transaction Features:**
- `txn_count`: Integer (transactions per day)
- `avg_transaction_size`: Float (average quantity per transaction)
- `txn_size_std_7`: Float (7-day rolling std of transaction sizes)

### **Price Features:**
- `unit_price`: Float (average unit price)
- `price_stability`: Float (coefficient of variation)
- `price_trend_7`: Float (7-day rolling mean)
- `price_trend_30`: Float (30-day rolling mean)

### **Admission Features:**
- `admission_lag`: Integer (days between admission and transaction)
- `has_admission_date`: 0 or 1 (binary indicator)
- `admission_lag_mean_7`: Float (7-day rolling mean)

---

## ✅ Current Usage

**Status**: ✅ **Active and Enabled**

- Used in: `ForecastService.forecast()` method
- Enabled by default: `use_domain_features=True`
- Location: `backend/app/modules/forecasting/features/domain_features.py`

---

## 🔍 Key Functions

### **Main Function:**
```python
create_domain_features(
    daily_data: pd.DataFrame,
    target_col: str = 'QTY'
) -> pd.DataFrame
```

### **Helper Functions:**
- `create_department_features(df)` - Department-related features
- `create_category_features(df)` - Category-related features
- `create_room_bed_features(df)` - Room/bed-related features
- `create_transaction_features(df)` - Transaction pattern features
- `create_price_features(df)` - Price-related features
- `create_admission_features(df)` - Admission date features

---

## 📚 Related Files

- **`xgboost_features.py`**: Generic time-series features (lags, rolling stats, etc.)
- **`service_enhanced.py`**: Calls `prepare_features()` with `use_domain_features=True`
- **`enhanced_data_preparation.py`**: Loads transaction data with metadata needed for domain features

---

## 🎯 Summary

**`domain_features.py`** creates **business-specific features** that help the forecasting model understand:
- Which departments drive demand
- How categories behave
- Spatial patterns (rooms/beds)
- Transaction patterns
- Pricing relationships
- Patient admission patterns

These features **complement** generic time-series features to create a more accurate, context-aware forecasting model.

---

**Location**: `backend/app/modules/forecasting/features/domain_features.py`
**Status**: ✅ Active
**Enabled**: Yes (by default in `ForecastService`)

