-- =====================================================
-- Smart Career Recommendation System
-- Phase 2: Database Migration Script
-- Run this AFTER database.sql (Phase 1)
-- =====================================================

USE smart_career_system;

-- =====================================================
-- Table: student_profile
-- One-to-one extension of the users table.
-- user_id is both PK and FK so ON DUPLICATE KEY UPDATE
-- works as a true upsert in the Flask backend.
-- =====================================================
CREATE TABLE IF NOT EXISTS student_profile (
    user_id         INT PRIMARY KEY,
    phone           VARCHAR(20)     DEFAULT NULL,
    date_of_birth   DATE            DEFAULT NULL,
    gender          ENUM('Male','Female','Other','Prefer not to say') DEFAULT NULL,
    education_level ENUM('High School','Diploma','Undergraduate','Postgraduate','PhD','Other') DEFAULT NULL,
    institution_name VARCHAR(150)   DEFAULT NULL,
    field_of_study  VARCHAR(100)    DEFAULT NULL,
    graduation_year SMALLINT        DEFAULT NULL,
    bio             TEXT            DEFAULT NULL,
    linkedin_url    VARCHAR(255)    DEFAULT NULL,
    github_url      VARCHAR(255)    DEFAULT NULL,
    updated_at      TIMESTAMP       DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT fk_profile_user
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- =====================================================
-- Table: skills
-- Multiple skills per user, each with a proficiency level.
-- =====================================================
CREATE TABLE IF NOT EXISTS skills (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    user_id     INT         NOT NULL,
    skill_name  VARCHAR(100) NOT NULL,
    proficiency ENUM('Beginner','Intermediate','Advanced','Expert') NOT NULL DEFAULT 'Beginner',
    created_at  TIMESTAMP   DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY uq_user_skill (user_id, skill_name),
    CONSTRAINT fk_skill_user
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- =====================================================
-- Table: interests
-- Free-form interest tags per user.
-- =====================================================
CREATE TABLE IF NOT EXISTS interests (
    id            INT AUTO_INCREMENT PRIMARY KEY,
    user_id       INT         NOT NULL,
    interest_name VARCHAR(100) NOT NULL,
    created_at    TIMESTAMP   DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY uq_user_interest (user_id, interest_name),
    CONSTRAINT fk_interest_user
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- =====================================================
-- Table: certifications
-- Professional certifications per user.
-- =====================================================
CREATE TABLE IF NOT EXISTS certifications (
    id                    INT AUTO_INCREMENT PRIMARY KEY,
    user_id               INT          NOT NULL,
    certification_name    VARCHAR(150) NOT NULL,
    issuing_organization  VARCHAR(150) DEFAULT NULL,
    issue_date            DATE         DEFAULT NULL,
    expiry_date           DATE         DEFAULT NULL,
    credential_url        VARCHAR(255) DEFAULT NULL,
    created_at            TIMESTAMP    DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_cert_user
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- =====================================================
-- Table: projects
-- Portfolio projects per user.
-- =====================================================
CREATE TABLE IF NOT EXISTS projects (
    id                INT AUTO_INCREMENT PRIMARY KEY,
    user_id           INT          NOT NULL,
    project_title     VARCHAR(150) NOT NULL,
    description       TEXT         DEFAULT NULL,
    technologies_used VARCHAR(255) DEFAULT NULL,
    project_url       VARCHAR(255) DEFAULT NULL,
    start_date        DATE         DEFAULT NULL,
    end_date          DATE         DEFAULT NULL,
    is_ongoing        TINYINT(1)   NOT NULL DEFAULT 0,
    created_at        TIMESTAMP    DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_project_user
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- =====================================================
-- Verify
-- =====================================================
-- SHOW TABLES;
-- DESCRIBE student_profile;
-- DESCRIBE skills;
-- DESCRIBE interests;
-- DESCRIBE certifications;
-- DESCRIBE projects;
