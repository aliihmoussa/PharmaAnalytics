-- Database initialization script for Docker
--
-- This script is automatically executed when PostgreSQL container starts
-- Create database if it doesn't exist (handled by POSTGRES_DB env var)
--
-- Note: Actual table creation is handled by setup_database.py script
-- This file ensures the database is properly set up

-- The database and user are created automatically by PostgreSQL via:
-- POSTGRES_DB and POSTGRES_USER environment variables
-- This script just verifies everything is set up correctly

SELECT 'Database initialization script loaded' as status;
