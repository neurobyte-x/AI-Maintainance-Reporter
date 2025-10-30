-- Neon (PostgreSQL) schema for AI Maintenance Reporter
-- Copy and paste this entire script into Neon SQL Editor and click "Run"

-- Drop existing tables if you need a fresh start (optional, uncomment if needed)
-- DROP TABLE IF EXISTS tickets CASCADE;
-- DROP TABLE IF EXISTS users CASCADE;

-- Users table
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(255),
    role VARCHAR(50) DEFAULT 'student',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tickets table
CREATE TABLE IF NOT EXISTS tickets (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    student_name VARCHAR(255),
    location VARCHAR(255),
    issue_type VARCHAR(100),
    description TEXT,
    image_path TEXT,
    status VARCHAR(50) DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    priority VARCHAR(50) DEFAULT 'medium',
    CONSTRAINT fk_user FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
);

-- Create indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_tickets_user_id ON tickets(user_id);
CREATE INDEX IF NOT EXISTS idx_tickets_created_at ON tickets(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_tickets_status ON tickets(status);
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);

-- Verify tables were created
SELECT 'Users table created' AS status, COUNT(*) AS row_count FROM users
UNION ALL
SELECT 'Tickets table created' AS status, COUNT(*) AS row_count FROM tickets;
