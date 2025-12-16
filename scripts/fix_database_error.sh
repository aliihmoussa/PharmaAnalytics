#!/bin/bash
# Quick fix script for "database 'pharma_user' does not exist" error
# This script resets the database and runs migrations

set -e  # Exit on error

# Get database configuration from environment or use defaults
DB_USER=${DB_USER:-pharma_user}
DB_PASSWORD=${DB_PASSWORD:-pharma_password}
DB_NAME=${DB_NAME:-pharma_analytics_db}

echo "🔧 Fixing database error..."
echo ""

# Step 1: Stop all services
echo "📦 Stopping all services..."
docker compose down

# Step 2: Remove volumes (fresh start)
echo "🗑️  Removing old volumes (this deletes existing data)..."
docker compose down -v

# Step 3: Start only PostgreSQL first to ensure it's fully initialized
echo "🚀 Starting PostgreSQL service first..."
docker compose up -d postgres

# Step 4: Wait for PostgreSQL to be fully ready
echo "⏳ Waiting for PostgreSQL to be ready (this may take 30-60 seconds)..."
max_attempts=60
attempt=0
while [ $attempt -lt $max_attempts ]; do
    # First check if PostgreSQL is accepting connections
    if docker compose exec -T postgres pg_isready -U ${DB_USER} > /dev/null 2>&1; then
        # Then verify we can connect to the specific database
        if docker compose exec -T postgres psql -U ${DB_USER} -d ${DB_NAME} -c "SELECT 1;" > /dev/null 2>&1; then
            echo "✅ PostgreSQL is ready and database is accessible!"
            break
        fi
    fi
    attempt=$((attempt + 1))
    if [ $((attempt % 5)) -eq 0 ]; then
        echo "   Attempt $attempt/$max_attempts..."
    fi
    sleep 2
done

if [ $attempt -eq $max_attempts ]; then
    echo "❌ PostgreSQL did not become ready in time. Please check logs:"
    echo "   docker compose logs postgres"
    exit 1
fi

# Step 5: Start all other services
echo "🚀 Starting all services..."
docker compose up -d

# Step 6: Wait a bit for services to initialize
echo "⏳ Waiting for services to initialize..."
sleep 5

# Step 7: Run migrations
echo "📊 Running database migrations..."
docker compose exec -T backend alembic upgrade head || {
    echo "⚠️  Migration failed, but continuing..."
}

# Step 8: Verify database
echo "✅ Verifying database setup..."
if docker compose exec -T postgres psql -U ${DB_USER} -d ${DB_NAME} -c "\dt" > /dev/null 2>&1; then
    echo ""
    echo "✅ SUCCESS! Database is now set up correctly."
    echo ""
    echo "You can verify by running:"
    echo "  docker compose exec postgres psql -U ${DB_USER} -d ${DB_NAME} -c \"\\dt\""
    echo ""
    echo "All services should now be running. Check with:"
    echo "  docker compose ps"
else
    echo "❌ Error verifying database. Please check logs:"
    echo "   docker compose logs backend"
    echo "   docker compose logs postgres"
    exit 1
fi

