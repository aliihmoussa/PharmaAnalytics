# Department Performance Metrics Explanation

## 📊 Metrics Overview

The `/api/dashboard/department-performance` endpoint returns these key metrics for each department:

---

## 1. **total_dispensed** (Quantity)

### **What it is:**
- **Total number of drug units dispensed** by the department
- Sum of absolute values of quantities for consumption transactions

### **Calculation:**
```python
func.sum(func.abs(DrugTransaction.quantity))
# Where quantity < 0 (consumption/dispensing)
```

### **Example:**
If a department dispensed:
- 50 units of Drug A
- 30 units of Drug B
- 20 units of Drug C

**total_dispensed** = 50 + 30 + 20 = **100 units**

### **Unit:**
- **Integer** (number of units)
- Represents physical quantity

### **Business Meaning:**
- How many drug units did this department consume/dispense?
- Useful for inventory planning
- Shows department activity level

---

## 2. **total_value** (Monetary Value)

### **What it is:**
- **Total monetary value** of drugs dispensed by the department
- Sum of `total_price` for all consumption transactions

### **Calculation:**
```python
func.sum(DrugTransaction.total_price)
# Where quantity < 0 (consumption/dispensing)
```

### **How `total_price` is calculated:**
```
total_price = unit_price × quantity
```

**Note**: Since `quantity` is negative for consumption, `total_price` is also negative. The query sums these values directly.

### **Example:**
If a department dispensed:
- Drug A: 50 units × 100 DZD/unit = 5,000 DZD
- Drug B: 30 units × 200 DZD/unit = 6,000 DZD
- Drug C: 20 units × 150 DZD/unit = 3,000 DZD

**total_value** = 5,000 + 6,000 + 3,000 = **14,000 DZD**

### **Unit:**
- **Decimal/Currency** (monetary value)
- Typically in DZD (Algerian Dinar) or local currency

### **Business Meaning:**
- What is the total cost/value of drugs consumed by this department?
- Useful for budget analysis
- Shows department spending

---

## 📋 Complete Response Example

```json
{
  "data": {
    "departments": [
      {
        "department_id": 86007,
        "total_dispensed": 20219.0,        // 20,219 units dispensed
        "total_value": 75424692.0,         // 75,424,692 DZD total value
        "transaction_count": 6197,         // 6,197 transactions
        "unique_drugs": 174                // 174 different drugs
      }
    ]
  }
}
```

---

## 🔍 Understanding the Data Model

### **Quantity Sign Convention:**
- **Negative (`quantity < 0`)**: Consumption/dispensing to patients
- **Positive (`quantity > 0`)**: Receiving/stocking from suppliers

### **Why Filter `quantity < 0`?**
The endpoint only counts **consumption** (dispensing to patients), not receiving/stocking, because:
- We want to measure **department activity** (how much they use)
- We want to measure **cost of operations** (how much they spend)
- Receiving/stocking is inventory management, not department performance

---

## 💡 Key Insights

### **total_dispensed** tells you:
- ✅ **Volume**: How many units are being used
- ✅ **Activity**: Which departments are most active
- ✅ **Demand**: Relative demand levels across departments

### **total_value** tells you:
- ✅ **Cost**: How much money is being spent
- ✅ **Budget**: Department spending levels
- ✅ **Efficiency**: Cost per unit (if you divide value by dispensed)

### **Together they show:**
- **High dispensed, High value**: Active department with expensive drugs
- **High dispensed, Low value**: Active department with cheap drugs
- **Low dispensed, High value**: Small volume but expensive drugs
- **Low dispensed, Low value**: Low activity department

---

## 📊 Example Analysis

### **Department A:**
```json
{
  "department_id": 86007,
  "total_dispensed": 20219.0,      // High volume
  "total_value": 75424692.0,       // High cost
  "transaction_count": 6197
}
```
**Interpretation**: Very active department, dispenses many units, high spending

### **Department B:**
```json
{
  "department_id": 1041,
  "total_dispensed": 9349.0,        // Medium volume
  "total_value": 49188993.0,       // Medium cost
  "transaction_count": 3909
}
```
**Interpretation**: Moderate activity, moderate spending

### **Cost per Unit:**
```
Department A: 75,424,692 / 20,219 = 3,728 DZD per unit
Department B: 49,188,993 / 9,349 = 5,260 DZD per unit
```
**Insight**: Department B uses more expensive drugs per unit

---

## 🎯 Use Cases

### **1. Budget Planning**
- Use `total_value` to allocate budgets
- Identify high-spending departments

### **2. Inventory Management**
- Use `total_dispensed` to forecast demand
- Plan stock levels per department

### **3. Performance Comparison**
- Compare departments by volume (`total_dispensed`)
- Compare departments by cost (`total_value`)
- Identify outliers

### **4. Cost Analysis**
- Calculate cost per unit: `total_value / total_dispensed`
- Identify departments using expensive drugs

---

## 📝 Summary

| Metric | What It Measures | Unit | Use Case |
|--------|-----------------|------|----------|
| **total_dispensed** | Total units consumed | Integer (units) | Volume analysis, demand forecasting |
| **total_value** | Total monetary value | Decimal (currency) | Budget analysis, cost management |
| **transaction_count** | Number of transactions | Integer | Activity level |
| **unique_drugs** | Number of different drugs | Integer | Drug diversity |

---

## 🔗 Related Fields

- **unit_price**: Cost per unit of a drug
- **total_price**: `unit_price × quantity` (for a single transaction)
- **quantity**: Number of units (negative for consumption)
- **department_id (cr)**: Consuming department identifier

---

**In Simple Terms:**
- **total_dispensed** = "How many units?"
- **total_value** = "How much money?"

---

**Last Updated**: 2024-12-31

