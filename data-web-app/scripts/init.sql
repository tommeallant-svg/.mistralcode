-- Database initialization script for PostgreSQL
-- This script will be executed when the container starts

-- Create database if it doesn't exist
SELECT 'CREATE DATABASE data_app' WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'data_app')\gexec

-- Connect to the database
\c data_app

-- Create extension for UUID if needed
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create schema for application
CREATE SCHEMA IF NOT EXISTS app;

-- Set search path
SET search_path TO app, public;

-- Create datasets metadata table
CREATE TABLE IF NOT EXISTS datasets_metadata (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) UNIQUE NOT NULL,
    description TEXT,
    table_name VARCHAR(255) NOT NULL,
    source VARCHAR(500),
    row_count INTEGER DEFAULT 0,
    column_info TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create index on name for faster lookups
CREATE INDEX IF NOT EXISTS idx_datasets_metadata_name ON datasets_metadata(name);

-- Create function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create trigger for datasets_metadata
DROP TRIGGER IF EXISTS update_datasets_metadata_updated_at ON datasets_metadata;
CREATE TRIGGER update_datasets_metadata_updated_at
    BEFORE UPDATE ON datasets_metadata
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Log initialization
INSERT INTO datasets_metadata (name, description, table_name, source) 
VALUES ('init', 'Database initialized', 'datasets_metadata', 'init.sql')
ON CONFLICT (name) DO NOTHING;

-- Output success message
SELECT 'Database initialization completed successfully' AS message;
