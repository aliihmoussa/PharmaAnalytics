# Quick Start Guide - Docker & Database Setup

**For detailed instructions, see [DOCKER_SETUP_GUIDE.md](./DOCKER_SETUP_GUIDE.md)**

## 🚀 Quick Setup (5 Minutes)

### 1. Prerequisites Check
```bash
docker --version
docker compose version
```

### 2. Build and Start Services
```bash
cd /path/to/PharmaAnalytics
docker compose build
docker compose up -d
```

### 3. Wait for Database (30 seconds)
```bash
docker compose exec postgres pg_isready -U pharma_user -d pharma_analytics_db
```

### 4. Run Migrations
```bash
docker compose exec backend alembic upgrade head
```

### 5. Verify Setup
```bash
# Check tables
docker compose exec postgres psql -U pharma_user -d pharma_analytics_db -c "\dt"

# Check services
docker compose ps
```

## ✅ Verification Commands

```bash
# All services running?
docker compose ps

# Database accessible?
docker compose exec postgres psql -U pharma_user -d pharma_analytics_db -c "SELECT 1;"

# Backend responding?
curl http://localhost:5000/health  # (if health endpoint exists)

# Redis working?
docker compose exec redis redis-cli ping
```

## 🔧 Common Commands

```bash
# View logs
docker compose logs -f backend

# Restart service
docker compose restart backend

# Stop everything
docker compose down

# Stop and delete data
docker compose down -v
```

## 📋 Default Configuration

- **Database**: PostgreSQL on port `5433`
- **Backend**: Flask API on port `5000`
- **Redis**: Port `6379`
- **Database Name**: `pharma_analytics_db`
- **Database User**: `pharma_user`
- **Database Password**: `pharma_password`

## ⚠️ Troubleshooting

**Port in use?**
```bash
# Change port in .env or docker-compose.yml
```

**Database not ready?**
```bash
docker compose restart postgres
# Wait 30 seconds, then retry migrations
```

**Migration errors?**
```bash
docker compose exec backend alembic current
docker compose exec backend alembic upgrade head
```

## 📚 Full Documentation

- **Complete Setup Guide**: [DOCKER_SETUP_GUIDE.md](./DOCKER_SETUP_GUIDE.md)
- **Database Commands**: [../database/DATABASE_COMMANDS.md](../database/DATABASE_COMMANDS.md)
- **API Examples**: [../api/](../api/)

