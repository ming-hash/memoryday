-- MemoryDay Database Initialization Script
-- This script runs when the MySQL container starts

-- Create database if not exists
CREATE DATABASE IF NOT EXISTS `memoryday` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- Create application user with limited privileges
CREATE USER IF NOT EXISTS 'memoryday_user'@'%' IDENTIFIED BY 'memoryday_password';
GRANT SELECT, INSERT, UPDATE, DELETE, CREATE, DROP, INDEX, ALTER, CREATE TEMPORARY TABLES, LOCK TABLES 
ON `memoryday`.* TO 'memoryday_user'@'%';
FLUSH PRIVILEGES;

-- Set timezone
SET GLOBAL time_zone = '+8:00';
SET time_zone = '+8:00';

-- Set character set
SET NAMES utf8mb4;
SET CHARACTER SET utf8mb4;