-- =====================================================
-- Smart Career Recommendation System
-- Phase 3: Database Migration Script
-- Run AFTER database.sql and database_phase2.sql
-- =====================================================

USE smart_career_system;

-- =====================================================
-- Table: github_analysis
-- Stores the latest GitHub profile analysis per user.
-- One row per user (UPSERT on re-analysis).
-- =====================================================
CREATE TABLE IF NOT EXISTS github_analysis (
    id                    INT AUTO_INCREMENT PRIMARY KEY,
    user_id               INT          NOT NULL UNIQUE,
    github_username       VARCHAR(100) NOT NULL,

    -- Profile metadata
    github_name           VARCHAR(150) DEFAULT NULL,
    github_bio            TEXT         DEFAULT NULL,
    github_avatar_url     VARCHAR(255) DEFAULT NULL,
    github_profile_url    VARCHAR(255) DEFAULT NULL,
    github_location       VARCHAR(150) DEFAULT NULL,
    account_created_at    VARCHAR(30)  DEFAULT NULL,   -- ISO string from API

    -- Repo counts
    public_repos          INT          NOT NULL DEFAULT 0,
    total_stars           INT          NOT NULL DEFAULT 0,
    total_forks           INT          NOT NULL DEFAULT 0,
    total_watchers        INT          NOT NULL DEFAULT 0,

    -- Activity metrics
    followers             INT          NOT NULL DEFAULT 0,
    following             INT          NOT NULL DEFAULT 0,
    public_gists          INT          NOT NULL DEFAULT 0,

    -- Computed scores (0–100 scale)
    activity_score        DECIMAL(5,2) NOT NULL DEFAULT 0.00,
    repo_score            DECIMAL(5,2) NOT NULL DEFAULT 0.00,
    community_score       DECIMAL(5,2) NOT NULL DEFAULT 0.00,
    overall_score         DECIMAL(5,2) NOT NULL DEFAULT 0.00,

    -- Top languages JSON string e.g. '["Python","JavaScript","Go"]'
    top_languages_json    TEXT         DEFAULT NULL,

    -- Raw repo analysis JSON (top 10 repos summary)
    top_repos_json        TEXT         DEFAULT NULL,

    -- When we last fetched from GitHub
    analyzed_at           TIMESTAMP    DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    CONSTRAINT fk_github_user
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- =====================================================
-- Table: github_languages
-- Per-language byte counts from the latest analysis.
-- Cleared and re-inserted on every re-analysis.
-- =====================================================
CREATE TABLE IF NOT EXISTS github_languages (
    id           INT AUTO_INCREMENT PRIMARY KEY,
    user_id      INT          NOT NULL,
    language     VARCHAR(80)  NOT NULL,
    bytes_count  BIGINT       NOT NULL DEFAULT 0,
    repo_count   INT          NOT NULL DEFAULT 0,
    percentage   DECIMAL(5,2) NOT NULL DEFAULT 0.00,
    UNIQUE KEY uq_user_lang (user_id, language),
    CONSTRAINT fk_lang_user
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- =====================================================
-- Verify
-- =====================================================
-- SHOW TABLES;
-- DESCRIBE github_analysis;
-- DESCRIBE github_languages;
