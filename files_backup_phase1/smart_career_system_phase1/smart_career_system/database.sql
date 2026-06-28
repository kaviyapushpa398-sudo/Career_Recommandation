-- =====================================================
-- Smart Career Recommendation System
-- Phase 1: Database Creation Script
-- =====================================================

-- Create the database
CREATE DATABASE IF NOT EXISTS smart_career_system;

-- Select the database to use
USE smart_career_system;

-- =====================================================
-- Table: users
-- Stores registered user details with hashed passwords
-- =====================================================
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    full_name VARCHAR(100) NOT NULL,
    email VARCHAR(120) NOT NULL UNIQUE,
    username VARCHAR(50) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- =====================================================
-- Optional: Verify table creation
-- =====================================================
-- DESCRIBE users;
-- SELECT * FROM users;
