-- Simple database initialization
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- System log table
CREATE TABLE IF NOT EXISTS system_log (
    id SERIAL PRIMARY KEY,
    message TEXT NOT NULL,
    timestamp TIMESTAMP DEFAULT NOW()
);

INSERT INTO system_log (message) VALUES ('Database initialized for Corvus Corone');