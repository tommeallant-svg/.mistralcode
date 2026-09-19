-- Road Application Database Initialization Script
-- PostgreSQL

-- Enable UUID extension if not already enabled
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Drop tables if they exist (for fresh start)
DROP TABLE IF EXISTS shared_trips CASCADE;
DROP TABLE IF EXISTS steps CASCADE;
DROP TABLE IF EXISTS trips CASCADE;
DROP TABLE IF EXISTS users CASCADE;

-- Create users table
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(100),
    email VARCHAR(100) UNIQUE,
    is_active BOOLEAN DEFAULT TRUE,
    is_superuser BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create trips table
CREATE TABLE trips (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    start_date TIMESTAMP WITH TIME ZONE NOT NULL,
    end_date TIMESTAMP WITH TIME ZONE NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'brouillon',
    latitude FLOAT,
    longitude FLOAT,
    owner_id INTEGER NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT fk_trips_owner FOREIGN KEY (owner_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Create steps table
CREATE TABLE steps (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    category VARCHAR(20) NOT NULL,
    type VARCHAR(50),
    start_datetime TIMESTAMP WITH TIME ZONE NOT NULL,
    end_datetime TIMESTAMP WITH TIME ZONE,
    location_start VARCHAR(200),
    location_end VARCHAR(200),
    latitude_start FLOAT,
    longitude_start FLOAT,
    latitude_end FLOAT,
    longitude_end FLOAT,
    notes TEXT,
    order_index INTEGER DEFAULT 0,
    color VARCHAR(20),
    trip_id INTEGER NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT fk_steps_trip FOREIGN KEY (trip_id) REFERENCES trips(id) ON DELETE CASCADE
);

-- Create shared_trips table
CREATE TABLE shared_trips (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    shared_with_user_id INTEGER NOT NULL,
    trip_id INTEGER NOT NULL,
    can_edit BOOLEAN DEFAULT FALSE,
    can_delete BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT fk_shared_trips_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    CONSTRAINT fk_shared_trips_shared_with FOREIGN KEY (shared_with_user_id) REFERENCES users(id) ON DELETE CASCADE,
    CONSTRAINT fk_shared_trips_trip FOREIGN KEY (trip_id) REFERENCES trips(id) ON DELETE CASCADE,
    
    UNIQUE (user_id, shared_with_user_id, trip_id)
);

-- Create indexes for better performance
CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_trips_owner ON trips(owner_id);
CREATE INDEX idx_trips_status ON trips(status);
CREATE INDEX idx_trips_dates ON trips(start_date, end_date);
CREATE INDEX idx_steps_trip ON steps(trip_id);
CREATE INDEX idx_steps_category ON steps(category);
CREATE INDEX idx_steps_order ON steps(trip_id, order_index);
CREATE INDEX idx_shared_trips_user ON shared_trips(user_id);
CREATE INDEX idx_shared_trips_shared ON shared_trips(shared_with_user_id);
CREATE INDEX idx_shared_trips_trip ON shared_trips(trip_id);

-- Create the hardcoded user 'Paloma'
-- Password: 'laBest' hashed with SHA-256
INSERT INTO users (username, password_hash, full_name, email, is_active, is_superuser) 
VALUES ('Paloma', '500801f70d62c073596d6161798d6f5254277491843202262b499353247739', 'Paloma User', 'paloma@example.com', TRUE, TRUE)
ON CONFLICT (username) DO NOTHING;

-- Add updated_at trigger function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create triggers for updated_at
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_trips_updated_at BEFORE UPDATE ON trips FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_steps_updated_at BEFORE UPDATE ON steps FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_shared_trips_updated_at BEFORE UPDATE ON shared_trips FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Create updated_at trigger for trips when steps are updated
CREATE OR REPLACE FUNCTION update_trip_updated_at_on_step_change()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE trips SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.trip_id;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_trip_on_step_update AFTER UPDATE ON steps FOR EACH ROW EXECUTE FUNCTION update_trip_updated_at_on_step_change();
CREATE TRIGGER update_trip_on_step_insert AFTER INSERT ON steps FOR EACH ROW EXECUTE FUNCTION update_trip_updated_at_on_step_change();
CREATE TRIGGER update_trip_on_step_delete AFTER DELETE ON steps FOR EACH ROW EXECUTE FUNCTION update_trip_updated_at_on_step_change();

-- Commit
COMMIT;
