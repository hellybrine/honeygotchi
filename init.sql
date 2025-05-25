-- Initialize database schema
CREATE DATABASE IF NOT EXISTS rassh_db;
USE rassh_db;

-- Sessions table
CREATE TABLE IF NOT EXISTS sessions (
    id VARCHAR(36) PRIMARY KEY,
    start_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    end_time DATETIME NULL,
    client_ip VARCHAR(45),
    client_version VARCHAR(255),
    INDEX idx_client_ip (client_ip),
    INDEX idx_start_time (start_time)
);

-- Commands table
CREATE TABLE IF NOT EXISTS commands (
    id INT AUTO_INCREMENT PRIMARY KEY,
    session_id VARCHAR(36),
    command TEXT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    action_taken INT,
    reward FLOAT,
    INDEX idx_session_id (session_id),
    INDEX idx_timestamp (timestamp),
    FOREIGN KEY (session_id) REFERENCES sessions(id) ON DELETE CASCADE
);

-- RL training cases
CREATE TABLE IF NOT EXISTS cases (
    id INT AUTO_INCREMENT PRIMARY KEY,
    initial_cmd TEXT,
    action INT,
    next_cmd TEXT,
    cmd_profile VARCHAR(100),
    rl_params TEXT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_timestamp (timestamp)
);

-- Fake command outputs
CREATE TABLE IF NOT EXISTS fake_commands (
    id INT AUTO_INCREMENT PRIMARY KEY,
    command_pattern VARCHAR(255),
    fake_output TEXT,
    INDEX idx_pattern (command_pattern)
);

-- Insert some default fake outputs
INSERT IGNORE INTO fake_commands (command_pattern, fake_output) VALUES
('wget %', 'Connecting to server... Download completed successfully.\n'),
('curl %', '<!DOCTYPE html><html><head><title>Success</title></head><body><h1>Request completed</h1></body></html>\n'),
('python %', 'Python script executed successfully.\n'),
('bash %', 'Script completed with exit code 0.\n');

-- Insult messages by location
CREATE TABLE IF NOT EXISTS messages (
    id INT AUTO_INCREMENT PRIMARY KEY,
    location VARCHAR(100) DEFAULT 'DEFAULT',
    message TEXT,
    INDEX idx_location (location)
);

-- Insert default messages
INSERT IGNORE INTO messages (location, message) VALUES
('DEFAULT', 'Access denied! Your activities have been logged.\n'),
('CN', '访问被拒绝！您的活动已被记录。\n'),
('RU', 'Доступ запрещен! Ваши действия зарегистрированы.\n'),
('US', 'Access denied! Law enforcement has been notified.\n');