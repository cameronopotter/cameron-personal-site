-- Digital Greenhouse Database Initialization
-- This script sets up the initial database configuration

-- Enable necessary extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- Create custom functions for garden ecosystem

-- Function to generate random UUID (if uuid-ossp is not available)
CREATE OR REPLACE FUNCTION gen_random_uuid()
RETURNS UUID AS $$
BEGIN
    RETURN uuid_generate_v4();
END;
$$ LANGUAGE plpgsql;