-- ======================================================
--  Database Schema Definition - LSS Project
--  This file initializes the relational storage structure
--  required to persist time-series IoT telemetry data.
-- ======================================================

-- Create the target data table if it does not already exist in the catalog
CREATE TABLE IF NOT EXISTS sensor_data (
    -- Auto-incrementing integer sequence serving as the unique primary key identifier
    id SERIAL PRIMARY KEY,
    
    -- Alpha-numerical identifier mapping the physical edge device generating the payload
    sensor_id VARCHAR(50) NOT NULL,
    
    -- Categorical field specifying the telemetry metric type (e.g., temperature, humidity)
    sensor_type VARCHAR(50) NOT NULL,
    
    -- Floating-point column storing the exact numerical telemetry reading value
    value FLOAT NOT NULL,
    
    -- High-precision timestamp payload injected directly from the edge sensor node
    timestamp TIMESTAMP NOT NULL
);