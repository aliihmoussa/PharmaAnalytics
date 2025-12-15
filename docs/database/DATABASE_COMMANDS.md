# Database Command Line Interaction Guide

## Quick Connection Methods

### Method 1: Connect from Host Machine
```bash
psql -h localhost -p 5433 -U pharma_user -d pharma_analytics_db
# Password: pharma_password
```

### Method 2: Connect via Docker (Recommended - No password needed)
```bash
docker compose exec postgres psql -U pharma_user -d pharma_analytics_db
```

### Method 3: Execute Single SQL Command
```bash
docker compose exec postgres psql -U pharma_user -d pharma_analytics_db -c "SELECT COUNT(*) FROM drug_transactions;"
```

---

## Essential psql Commands

Once connected to psql, use these commands:

### Database Information
```sql
-- List all databases
\l

-- List all tables in current database
\dt

-- Describe a specific table structure
\d drug_transactions
\d+ drug_transactions  -- More detailed info

-- List all schemas
\dn

-- Show current database
SELECT current_database();

-- Show current user
SELECT current_user;
```

### Table Operations
```sql
-- View table data (first 10 rows)
SELECT * FROM drug_transactions LIMIT 10;

-- Count rows in a table
SELECT COUNT(*) FROM drug_transactions;

-- View table structure
\d drug_transactions

-- List all columns in a table
\d+ drug_transactions
```

### Query Examples
```sql
-- Count records by year
SELECT 
    EXTRACT(YEAR FROM transaction_date) as year,
    COUNT(*) as total_records
FROM drug_transactions
GROUP BY EXTRACT(YEAR FROM transaction_date)
ORDER BY year;

-- View ingestion logs
SELECT * FROM data_ingestion_log ORDER BY created_at DESC LIMIT 5;

-- Check for errors
SELECT COUNT(*) FROM data_ingestion_errors;

-- View recent transactions
SELECT 
    transaction_date,
    drug_name,
    quantity,
    total_price
FROM drug_transactions
ORDER BY transaction_date DESC
LIMIT 20;
```

### Useful psql Meta-Commands
```sql
-- List all tables
\dt

-- List tables with sizes
\dt+

-- Show table sizes
SELECT 
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;

-- Show database size
SELECT pg_size_pretty(pg_database_size('pharma_analytics_db'));

-- Show connection info
\conninfo

-- Show all settings
\dx

-- Exit psql
\q
```

### Export/Import Data
```bash
# Export table to CSV
docker compose exec postgres psql -U pharma_user -d pharma_analytics_db -c "\COPY drug_transactions TO '/tmp/drug_transactions.csv' CSV HEADER;"

# Export query results to CSV
docker compose exec postgres psql -U pharma_user -d pharma_analytics_db -c "\COPY (SELECT * FROM drug_transactions LIMIT 100) TO '/tmp/sample.csv' CSV HEADER;"

# Import CSV (from container)
docker compose exec postgres psql -U pharma_user -d pharma_analytics_db -c "\COPY drug_transactions FROM '/tmp/data.csv' CSV HEADER;"
```

### Migration Commands
```bash
# Check current migration version
docker compose exec backend alembic current

# View migration history
docker compose exec backend alembic history

# Apply all pending migrations
docker compose exec backend alembic upgrade head

# Rollback one migration
docker compose exec backend alembic downgrade -1
```

### Performance & Monitoring
```sql
-- Show active connections
SELECT * FROM pg_stat_activity;

-- Show table statistics
SELECT 
    schemaname,
    tablename,
    n_live_tup,
    n_dead_tup,
    last_vacuum,
    last_autovacuum
FROM pg_stat_user_tables;

-- Show index usage
SELECT 
    schemaname,
    tablename,
    indexname,
    idx_scan,
    idx_tup_read,
    idx_tup_fetch
FROM pg_stat_user_indexes
ORDER BY idx_scan DESC;
```

### Backup & Restore
```bash
# Create a backup
docker compose exec postgres pg_dump -U pharma_user pharma_analytics_db > backup.sql

# Create a compressed backup
docker compose exec postgres pg_dump -U pharma_user pharma_analytics_db | gzip > backup.sql.gz

# Restore from backup
docker compose exec -T postgres psql -U pharma_user pharma_analytics_db < backup.sql
```

---

## Quick Reference Card

| Command | Description |
|--------|-------------|
| `\l` | List databases |
| `\dt` | List tables |
| `\d table_name` | Describe table |
| `\du` | List users |
| `\conninfo` | Show connection info |
| `\q` | Quit psql |
| `\?` | Show help |
| `\h` | SQL help |
| `\timing` | Toggle query timing |
| `\x` | Toggle expanded display |

---

## Common Workflows

### Check if tables exist
```bash
docker compose exec postgres psql -U pharma_user -d pharma_analytics_db -c "\dt"
```

### Count records in all tables
```bash
docker compose exec postgres psql -U pharma_user -d pharma_analytics_db -c "
SELECT 
    'drug_transactions' as table_name, COUNT(*) as row_count FROM drug_transactions
UNION ALL
SELECT 
    'data_ingestion_log', COUNT(*) FROM data_ingestion_log
UNION ALL
SELECT 
    'data_ingestion_errors', COUNT(*) FROM data_ingestion_errors;
"
```

### View recent ingestion status
```bash
docker compose exec postgres psql -U pharma_user -d pharma_analytics_db -c "
SELECT 
    file_name,
    file_year,
    ingestion_status,
    total_records,
    successful_records,
    failed_records,
    started_at,
    completed_at
FROM data_ingestion_log
ORDER BY created_at DESC
LIMIT 5;
"
```

### Reset Database Data

**⚠️ WARNING: These commands will DELETE data. Use with caution!**

#### Reset Transaction Data Only (Recommended)
```bash
# Reset only transaction data, keep ingestion logs
python scripts/reset_database.py --transactions --confirm
```

#### Reset All Data (including logs)
```bash
# Reset everything (transactions, logs, errors)
python scripts/reset_database.py --all --confirm

# Reset all but keep ingestion logs for history
python scripts/reset_database.py --all --keep-logs --confirm
```

#### Reset Specific Tables
```bash
# Reset only ingestion logs
python scripts/reset_database.py --logs --confirm

# Reset only ingestion errors
python scripts/reset_database.py --errors --confirm
```

#### Using Docker
```bash
# Reset transactions via Docker
docker compose exec backend python scripts/reset_database.py --transactions --confirm

# Reset all data via Docker
docker compose exec backend python scripts/reset_database.py --all --confirm
```

#### Manual SQL Reset (Alternative)
```bash
# Connect to database
docker compose exec postgres psql -U pharma_user -d pharma_analytics_db

# Then run SQL commands:
TRUNCATE TABLE drug_transactions CASCADE;
-- Optional: Also reset logs
TRUNCATE TABLE data_ingestion_log CASCADE;
TRUNCATE TABLE data_ingestion_errors CASCADE;
```

