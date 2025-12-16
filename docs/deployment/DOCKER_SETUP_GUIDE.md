# Docker Setup and Database Migration Guide

Complete guide for setting up the PharmaAnalytics platform on a new machine using Docker and running database migrations.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Initial Setup](#initial-setup)
3. [Docker Setup](#docker-setup)
4. [Database Creation and Migrations](#database-creation-and-migrations)
5. [Verifying the Setup](#verifying-the-setup)
6. [Troubleshooting](#troubleshooting)
7. [Common Operations](#common-operations)

---

## Prerequisites

Before starting, ensure you have the following installed on your machine:

### Required Software

1. **Docker** (version 20.10 or later)
   ```bash
   # Check Docker installation
   docker --version
   docker compose version
   ```

2. **Docker Compose** (version 2.0 or later)
   - Usually included with Docker Desktop
   - For Linux, install separately if needed:
   ```bash
   sudo apt-get update
   sudo apt-get install docker-compose-plugin
   ```

3. **Git** (to clone the repository)
   ```bash
   git --version
   ```

### System Requirements

- **OS**: Linux, macOS, or Windows (with WSL2 for Windows)
- **RAM**: Minimum 4GB (8GB recommended)
- **Disk Space**: At least 5GB free space
- **Ports**: Ensure ports 5000, 5433, and 6379 are available

---

## Initial Setup

### Step 1: Clone or Copy the Project

If using Git:
```bash
git clone <repository-url>
cd PharmaAnalytics
```

If copying from another location:
```bash
# Copy the entire project directory to the new machine
# Ensure all files are preserved, including hidden files
```

### Step 2: Verify Project Structure

Ensure the following key files and directories exist:

```
PharmaAnalytics/
├── docker-compose.yml          # Docker Compose configuration
├── docker/
│   └── Dockerfile.backend      # Backend Dockerfile
├── backend/                     # Backend application code
├── migrations/                  # Alembic migration files
│   ├── env.py
│   └── versions/
├── scripts/
│   ├── init_db.sql            # Database initialization script
│   └── setup_database.py      # Database setup script
├── requirements.txt            # Python dependencies
├── alembic.ini                 # Alembic configuration
└── run.py                      # Application entry point
```

### Step 3: (Optional) Configure Environment Variables

The project uses default values, but you can customize them by creating a `.env` file in the project root:

```bash
# Create .env file (optional)
cat > .env << EOF
# Database Configuration
DB_USER=pharma_user
DB_PASSWORD=pharma_password
DB_NAME=pharma_analytics_db
DB_PORT=5433

# Backend Configuration
BACKEND_PORT=5000
FLASK_ENV=development

# Redis Configuration
REDIS_PORT=6379
EOF
```

**Note**: If you don't create a `.env` file, the system will use default values defined in `docker-compose.yml`.

---

## Docker Setup

### Step 1: Build Docker Images

Build the Docker images for the backend services:

```bash
# Navigate to project root
cd /path/to/PharmaAnalytics

# Build all services
docker compose build

# Or build specific service
docker compose build backend
```

**Expected Output**: Docker will download base images and install dependencies. This may take several minutes on first run.

### Step 2: Start Docker Services

Start all services (PostgreSQL, Redis, Backend, Celery):

```bash
# Start all services in detached mode
docker compose up -d

# Or start with logs visible
docker compose up
```

**What this starts**:
- `postgres`: PostgreSQL 15 database server
- `redis`: Redis server for Celery task queue
- `backend`: Flask application server
- `celery_worker`: Celery worker for background tasks

### Step 3: Verify Services are Running

Check that all containers are running:

```bash
# List all containers
docker compose ps

# Expected output should show all 4 services as "Up"
```

Check service logs:

```bash
# View all logs
docker compose logs

# View specific service logs
docker compose logs postgres
docker compose logs backend
docker compose logs redis
docker compose logs celery_worker

# Follow logs in real-time
docker compose logs -f backend
```

**Expected Status**: All services should show as "Up" and healthy.

---

## Database Creation and Migrations

The database is automatically created by PostgreSQL when the container starts (via `POSTGRES_DB` environment variable). However, you need to run migrations to create the tables.

### Step 1: Verify Database Container is Ready

Wait for PostgreSQL to be fully initialized:

```bash
# Check PostgreSQL health
docker compose exec postgres pg_isready -U pharma_user -d pharma_analytics_db

# Expected output: pharma_analytics_db:5432 - accepting connections
```

### Step 2: Check Current Migration Status

Before running migrations, check the current state:

```bash
# Check current Alembic version (may show error if no migrations run yet)
docker compose exec backend alembic current

# View migration history
docker compose exec backend alembic history
```

### Step 3: Run Database Migrations

Apply all pending migrations to create/update database schema:

```bash
# Run all migrations up to the latest version
docker compose exec backend alembic upgrade head
```

**Expected Output**:
```
INFO  [alembic.runtime.migration] Context impl PostgresqlImpl.
INFO  [alembic.runtime.migration] Will assume transactional DDL.
INFO  [alembic.runtime.migration] Running upgrade  -> b589ede1cdad, initial migration create drug transactions
INFO  [alembic.runtime.migration] Running upgrade b589ede1cdad -> 8b226e1e7c95, change patient age to date of birth
INFO  [alembic.runtime.migration] Running upgrade 8b226e1e7c95 -> 74124f429c6e, change bed number to string
```

### Step 4: Verify Database Tables

Verify that tables were created successfully:

```bash
# Connect to database and list tables
docker compose exec postgres psql -U pharma_user -d pharma_analytics_db -c "\dt"

# Expected output should show:
# - drug_transactions
# - data_ingestion_log
# - data_ingestion_errors
# - alembic_version
```

### Step 5: (Optional) Run Additional Database Setup

The project includes a setup script that creates additional indexes:

```bash
# Run database setup script (creates indexes and additional columns)
docker compose exec backend python scripts/setup_database.py
```

**Note**: This step is optional as migrations handle table creation. The setup script adds performance indexes.

---

## Verifying the Setup

### Step 1: Verify Database Connection

Test database connectivity:

```bash
# Connect to PostgreSQL
docker compose exec postgres psql -U pharma_user -d pharma_analytics_db

# Once connected, run:
SELECT current_database(), current_user;
\dt  # List tables
\q   # Exit
```

### Step 2: Verify Backend API

Check if the backend is responding:

```bash
# Test backend health (if health endpoint exists)
curl http://localhost:5000/health

# Or check backend logs
docker compose logs backend | tail -20
```

### Step 3: Verify Celery Worker

Check Celery worker status:

```bash
# View Celery worker logs
docker compose logs celery_worker | tail -20

# Should show: "celery@<hostname> ready"
```

### Step 4: Verify Redis

Test Redis connection:

```bash
# Test Redis
docker compose exec redis redis-cli ping

# Expected output: PONG
```

---

## Troubleshooting

### Issue: Docker Compose Command Not Found

**Solution**:
```bash
# Use 'docker compose' (with space) instead of 'docker-compose'
# Or install docker-compose-plugin:
sudo apt-get install docker-compose-plugin
```

### Issue: Port Already in Use

**Error**: `Bind for 0.0.0.0:5000 failed: port is already allocated`

**Solution**:
```bash
# Option 1: Change port in docker-compose.yml or .env
# Edit BACKEND_PORT in .env file

# Option 2: Stop conflicting service
sudo lsof -ti:5000 | xargs kill -9
```

### Issue: Database Connection Failed

**Error**: `could not connect to server: Connection refused`

**Solution**:
```bash
# Wait for PostgreSQL to be ready
docker compose exec postgres pg_isready -U pharma_user

# Check PostgreSQL logs
docker compose logs postgres

# Restart PostgreSQL service
docker compose restart postgres
```

### Issue: Migration Errors

**Error**: `Target database is not up to date`

**Solution**:
```bash
# Check current migration version
docker compose exec backend alembic current

# View migration history
docker compose exec backend alembic history

# If needed, downgrade and re-apply
docker compose exec backend alembic downgrade base
docker compose exec backend alembic upgrade head
```

### Issue: Tables Not Created After Migration

**Solution**:
```bash
# Verify migrations ran successfully
docker compose exec backend alembic current

# Manually run setup script
docker compose exec backend python scripts/setup_database.py

# Verify tables exist
docker compose exec postgres psql -U pharma_user -d pharma_analytics_db -c "\dt"
```

### Issue: Permission Denied Errors

**Solution**:
```bash
# On Linux, ensure Docker has proper permissions
sudo usermod -aG docker $USER
# Log out and log back in

# Or run with sudo (not recommended)
sudo docker compose up -d
```

### Issue: Out of Disk Space

**Solution**:
```bash
# Clean up Docker resources
docker system prune -a

# Remove unused volumes (WARNING: deletes data)
docker volume prune
```

---

## Common Operations

### Stop All Services

```bash
docker compose down
```

### Stop and Remove Volumes (⚠️ Deletes Data)

```bash
docker compose down -v
```

### Restart a Specific Service

```bash
docker compose restart backend
docker compose restart postgres
```

### View Real-time Logs

```bash
# All services
docker compose logs -f

# Specific service
docker compose logs -f backend
```

### Rebuild After Code Changes

```bash
# Rebuild and restart
docker compose build backend
docker compose up -d backend
```

### Access Container Shell

```bash
# Backend container
docker compose exec backend bash

# PostgreSQL container
docker compose exec postgres bash
```

### Backup Database

```bash
# Create backup
docker compose exec postgres pg_dump -U pharma_user pharma_analytics_db > backup_$(date +%Y%m%d).sql

# Create compressed backup
docker compose exec postgres pg_dump -U pharma_user pharma_analytics_db | gzip > backup_$(date +%Y%m%d).sql.gz
```

### Restore Database

```bash
# Restore from backup
docker compose exec -T postgres psql -U pharma_user pharma_analytics_db < backup.sql
```

### Reset Database (⚠️ Deletes All Data)

```bash
# Stop services
docker compose down

# Remove volumes
docker compose down -v

# Restart and re-run migrations
docker compose up -d
docker compose exec backend alembic upgrade head
```

---

## Quick Reference Checklist

Use this checklist when setting up on a new machine:

- [ ] Install Docker and Docker Compose
- [ ] Clone/copy project to new machine
- [ ] Verify project structure
- [ ] (Optional) Create `.env` file with custom settings
- [ ] Build Docker images: `docker compose build`
- [ ] Start services: `docker compose up -d`
- [ ] Verify all services are running: `docker compose ps`
- [ ] Wait for PostgreSQL to be ready
- [ ] Run migrations: `docker compose exec backend alembic upgrade head`
- [ ] Verify tables created: `docker compose exec postgres psql -U pharma_user -d pharma_analytics_db -c "\dt"`
- [ ] (Optional) Run setup script: `docker compose exec backend python scripts/setup_database.py`
- [ ] Test backend API
- [ ] Verify Celery worker is running
- [ ] Test Redis connection

---

## Next Steps

After successful setup:

1. **Ingest Data**: Use the ingestion API to upload data files
   - See `docs/api/INGESTION_API_EXAMPLES.md`

2. **Access Dashboard**: Use the dashboard API to retrieve analytics
   - See `docs/api/DASHBOARD_API_EXAMPLES.md`

3. **Database Operations**: Use database commands for queries and maintenance
   - See `docs/database/DATABASE_COMMANDS.md`

---

## Additional Resources

- **Database Commands**: `docs/database/DATABASE_COMMANDS.md`
- **API Examples**: `docs/api/`
- **Architecture**: `docs/ARCHITECTURE.md`
- **Main README**: `README.md`

---

## Support

If you encounter issues not covered in this guide:

1. Check service logs: `docker compose logs <service_name>`
2. Verify environment variables match your setup
3. Ensure all required ports are available
4. Check Docker and Docker Compose versions meet requirements

