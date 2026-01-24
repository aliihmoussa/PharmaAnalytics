#!/bin/bash
# Wait for PostgreSQL database to be ready
# This script ensures the database is fully initialized before other services start

set -e

DB_USER=${DB_USER:-pharma_user}
DB_NAME=${DB_NAME:-pharma_analytics_db}
MAX_ATTEMPTS=60
ATTEMPT=0

echo "Waiting for PostgreSQL database to be ready..."

while [ $ATTEMPT -lt $MAX_ATTEMPTS ]; do
    # Check if PostgreSQL is accepting connections
    if pg_isready -U ${DB_USER} -h postgres > /dev/null 2>&1; then
        # Check if we can connect to the specific database
        if PGPASSWORD=${DB_PASSWORD:-pharma_password} psql -U ${DB_USER} -h postgres -d ${DB_NAME} -c "SELECT 1;" > /dev/null 2>&1; then
            echo "PostgreSQL database is ready!"
            exit 0
        fi
    fi
    ATTEMPT=$((ATTEMPT + 1))
    sleep 2
done

echo "ERROR: PostgreSQL database did not become ready in time"
exit 1









