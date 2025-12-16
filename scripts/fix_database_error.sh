#!/bin/bash
# Quick fix script for "database 'pharma_user' does not exist" error
# This script resets the database and runs migrations

set -e  # Exit on error

echo "🔧 Fixing database error..."
echo ""

# Step 1: Stop all services
echo "📦 Stopping all services..."
docker compose down

# Step 2: Remove volumes (fresh start)
echo "🗑️  Removing old volumes (this deletes existing data)..."
docker compose down -v

# Step 3: Start services
echo "🚀 Starting services..."
docker compose up -d

# Step 4: Wait for PostgreSQL to be ready
echo "⏳ Waiting for PostgreSQL to be ready (this may take 30-60 seconds)..."
max_attempts=30
attempt=0
while [ $attempt -lt $max_attempts ]; do
    if docker compose exec -T postgres pg_isready -U pharma_user -d pharma_analytics_db > /dev/null 2>&1; then
        echo "✅ PostgreSQL is ready!"
        break
    fi
    attempt=$((attempt + 1))
    echo "   Attempt $attempt/$max_attempts..."
    sleep 2
done

if [ $attempt -eq $max_attempts ]; then
    echo "❌ PostgreSQL did not become ready in time. Please check logs:"
    echo "   docker compose logs postgres"
    exit 1
fi

# Step 5: Run migrations
echo "📊 Running database migrations..."
docker compose exec backend sh -c "cd /app/backend && alembic upgrade head"


# Step 6: Verify database
echo "✅ Verifying database setup..."
docker compose exec -T postgres psql -U pharma_user -d pharma_analytics_db -c "\dt" > /dev/null 2>&1

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ SUCCESS! Database is now set up correctly."
    echo ""
    echo "You can verify by running:"
    echo "  docker compose exec postgres psql -U pharma_user -d pharma_analytics_db -c \"\\dt\""
    echo ""
    echo "All services should now be running. Check with:"
    echo "  docker compose ps"
else
    echo "❌ Error verifying database. Please check logs:"
    echo "   docker compose logs backend"
    echo "   docker compose logs postgres"
    exit 1
fi

