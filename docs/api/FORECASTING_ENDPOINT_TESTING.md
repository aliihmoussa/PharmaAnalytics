# Forecasting Endpoint Testing Guide

## ✅ Correct Endpoint URL

Your Postman request URL is **correct**:
```
GET http://localhost:5000/api/forecasting/P182054?forecast_days=10&test_size=30&start_date=2024-01-01&end_date=2024-08-17&department=7030
```

---

## ❌ Error: `ECONNREFUSED`

**Error**: `connect ECONNREFUSED 127.0.0.1:5000`

**Meaning**: The Flask server is not running on port 5000.

---

## 🚀 How to Start the Server

### **Option 1: Using Docker (Recommended)**

```bash
# Navigate to project root
cd /home/alimoussa/Documents/M2-\ 2026/Projects2026/PharmaAnalytics

# Start all services (PostgreSQL, Redis, Flask, Celery)
docker compose up -d

# Check if backend is running
docker compose ps

# View backend logs
docker compose logs -f backend
```

### **Option 2: Run Locally**

```bash
# Navigate to project root
cd /home/alimoussa/Documents/M2-\ 2026/Projects2026/PharmaAnalytics

# Make sure Redis is running (required for Celery)
redis-server

# In a separate terminal, start Celery worker (optional, only if using async tasks)
celery -A celery_worker worker --loglevel=info

# Start Flask server
python run.py
```

**Expected output:**
```
 * Running on http://0.0.0.0:5000
 * Debug mode: on
```

---

## 🧪 Test the Endpoint

### **1. Test Health Endpoint First**

```bash
curl http://localhost:5000/api/forecasting/health
```

**Expected response:**
```json
{
  "success": true,
  "data": {
    "status": "healthy",
    "module": "forecasting",
    "endpoint": "forecast",
    "available_algorithms": ["xgboost"]
  }
}
```

### **2. Test Forecast Endpoint**

```bash
curl "http://localhost:5000/api/forecasting/P182054?forecast_days=10&test_size=30"
```

### **3. Test in Postman**

Once server is running:
1. **Method**: `GET`
2. **URL**: `http://localhost:5000/api/forecasting/P182054`
3. **Query Parameters**:
   - `forecast_days`: `10`
   - `test_size`: `30`
   - `start_date`: `2024-01-01` (optional)
   - `end_date`: `2024-08-17` (optional)
   - `department`: `7030` (optional)
   - `algorithm`: `xgboost` (optional, defaults to xgboost)

---

## 🔍 Verify Server is Running

### **Check if port 5000 is in use:**

```bash
# Linux/Mac
lsof -i :5000
# or
netstat -an | grep 5000

# Should show Flask process listening on port 5000
```

### **Check Docker containers:**

```bash
docker compose ps

# Should show:
# - backend (Up)
# - postgres (Up)
# - redis (Up)
# - celery_worker (Up)
```

### **Check backend logs:**

```bash
# Docker
docker compose logs backend

# Local
# Check terminal where you ran `python run.py`
```

---

## 📋 Postman Request Setup

### **Request Configuration:**

1. **Method**: `GET`
2. **URL**: `http://localhost:5000/api/forecasting/P182054`
3. **Params Tab**:
   ```
   forecast_days: 10
   test_size: 30
   start_date: 2024-01-01
   end_date: 2024-08-17
   department: 7030
   algorithm: xgboost (optional)
   ```

### **Expected Response (200 OK):**

```json
{
  "success": true,
  "data": {
    "algorithm": "xgboost",
    "drug_code": "P182054",
    "drug_name": "...",
    "historical": [
      {
        "date": "2024-01-01",
        "demand": 45.2,
        "type": "actual"
      },
      ...
    ],
    "forecast": [
      {
        "date": "2024-08-18",
        "predicted": 52.3,
        "lower": 45.1,
        "upper": 59.5,
        "type": "predicted"
      },
      ...
    ],
    "test_predictions": [...],
    "metrics": {
      "rmse": 5.2,
      "mae": 4.1,
      "mape": 8.5,
      "r2": 0.85
    },
    "feature_importance": {...},
    ...
  }
}
```

---

## ⚠️ Common Issues

### **1. Port 5000 Already in Use**

**Error**: `Address already in use`

**Solution**:
```bash
# Find process using port 5000
lsof -i :5000

# Kill the process
kill -9 <PID>

# Or change port in run.py
app.run(host='0.0.0.0', port=5001, ...)
```

### **2. Database Connection Error**

**Error**: `could not connect to database`

**Solution**:
```bash
# Make sure PostgreSQL is running
docker compose ps postgres

# Check database connection
docker compose exec postgres psql -U pharma_user -d pharma_analytics_db -c "SELECT 1;"
```

### **3. Redis Connection Error**

**Error**: `Error connecting to Redis`

**Solution**:
```bash
# Make sure Redis is running
docker compose ps redis

# Test Redis
docker compose exec redis redis-cli ping
# Should return: PONG
```

---

## ✅ Quick Verification Checklist

- [ ] Server is running (`python run.py` or `docker compose up`)
- [ ] Port 5000 is accessible
- [ ] Health endpoint works: `GET /api/forecasting/health`
- [ ] Database is connected
- [ ] Redis is running (if using Celery)
- [ ] Postman URL is correct: `http://localhost:5000/api/forecasting/{drug_code}`

---

## 🎯 Your Specific Request

**Your Postman request is correct:**
```
GET http://localhost:5000/api/forecasting/P182054?forecast_days=10&test_size=30&start_date=2024-01-01&end_date=2024-08-17&department=7030
```

**Just need to start the server!**

---

**Quick Start Command:**
```bash
cd /home/alimoussa/Documents/M2-\ 2026/Projects2026/PharmaAnalytics
python run.py
```

Then retry your Postman request! 🚀

