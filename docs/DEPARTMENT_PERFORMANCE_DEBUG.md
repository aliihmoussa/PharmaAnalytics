# Department Performance Endpoint - Debug & Fix

## 🐛 Issue Found

The `/api/dashboard/department-performance` endpoint was returning **all zeros** for `total_dispensed` and `total_value`.

### **Problem:**
The query was using `.filter()` on aggregation functions, which doesn't work correctly in SQLAlchemy:

```python
# ❌ WRONG - Filter on aggregation
func.sum(func.abs(DrugTransaction.quantity)).filter(DrugTransaction.quantity < 0)
```

This doesn't filter the rows before aggregation - it tries to filter the aggregated result, which doesn't work.

---

## ✅ Fix Applied

### **Before (Broken):**
```python
results = self._session.query(
    DrugTransaction.cr.label('department_id'),
    func.count().label('transaction_count'),
    func.sum(func.abs(DrugTransaction.quantity))
        .filter(DrugTransaction.quantity < 0).label('total_dispensed'),  # ❌ Wrong
    func.sum(DrugTransaction.total_price)
        .filter(DrugTransaction.quantity < 0).label('total_value'),  # ❌ Wrong
    ...
).filter(
    DrugTransaction.transaction_date.between(start_date, end_date)
    # Missing: quantity filter here
)
```

### **After (Fixed):**
```python
results = self._session.query(
    DrugTransaction.cr.label('department_id'),
    func.count().filter(DrugTransaction.quantity < 0).label('transaction_count'),
    func.sum(func.abs(DrugTransaction.quantity)).label('total_dispensed'),  # ✅ Correct
    func.sum(DrugTransaction.total_price).label('total_value'),  # ✅ Correct
    ...
).filter(
    DrugTransaction.transaction_date.between(start_date, end_date),
    DrugTransaction.quantity < 0  # ✅ Filter base query first
)
```

---

## 📊 Results

### **Before Fix:**
```json
{
  "department_id": 10431,
  "total_dispensed": 0.0,  // ❌ Wrong
  "total_value": 0.0,      // ❌ Wrong
  "transaction_count": 1,
  "unique_drugs": 1
}
```

### **After Fix:**
```json
{
  "department_id": 86007,
  "total_dispensed": 20219.0,    // ✅ Correct
  "total_value": 75424692.0,     // ✅ Correct
  "transaction_count": 6197,
  "unique_drugs": 174
}
```

---

## 🔍 Root Cause

**SQLAlchemy Query Logic:**
- ❌ **Wrong**: `.filter()` on aggregation function filters the aggregated result (doesn't work)
- ✅ **Correct**: Filter the base query first, then aggregate

**Why it matters:**
- Negative quantities (`quantity < 0`) represent **consumption/dispensing**
- Positive quantities represent **receiving/stocking**
- We need to filter **before** aggregation to get correct totals

---

## ✅ Verification

Test the endpoint:
```bash
curl 'http://localhost:5000/api/dashboard/department-performance?start_date=2019-01-25&end_date=2019-02-25&limit=5'
```

**Expected**: Non-zero values for `total_dispensed` and `total_value`

---

## 📝 Key Lesson

**SQLAlchemy Best Practice:**
- Always filter the **base query** first
- Then apply aggregations
- Don't try to filter aggregated results

**Pattern:**
```python
# ✅ Correct
query.filter(condition).group_by(...).aggregate()

# ❌ Wrong  
query.group_by(...).aggregate().filter(condition)
```

---

**Status**: ✅ Fixed
**Date**: 2024-12-31

