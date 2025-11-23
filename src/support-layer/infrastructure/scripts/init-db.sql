-- Corvus Corone Database Initialization
-- This script sets up the basic database structure

-- PostgreSQL database initialization

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create schemas for better organization
CREATE SCHEMA IF NOT EXISTS experiments;
CREATE SCHEMA IF NOT EXISTS algorithms;
CREATE SCHEMA IF NOT EXISTS benchmarks;
CREATE SCHEMA IF NOT EXISTS publications;
CREATE SCHEMA IF NOT EXISTS auth;

-- Grant permissions
GRANT ALL PRIVILEGES ON DATABASE corvus_corone TO postgres;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO postgres;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO postgres;
GRANT ALL PRIVILEGES ON ALL FUNCTIONS IN SCHEMA public TO postgres;

-- Create indexes for better performance (will be created by SQLAlchemy models)
-- These are just placeholders for manual optimization later

-- Log initialization
INSERT INTO public.system_log (message, timestamp) 
VALUES ('Database initialized for Corvus Corone', NOW())
ON CONFLICT DO NOTHING;