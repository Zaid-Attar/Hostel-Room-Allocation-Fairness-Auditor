-- Hostel Room Allocation Fairness Auditor Schema
-- MySQL 8.0 & SQLite compatible DDL

CREATE TABLE IF NOT EXISTS students (
    student_id VARCHAR(20) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    gender CHAR(1) NOT NULL,
    year TINYINT NOT NULL,
    cgpa DECIMAL(4,2) NOT NULL,
    category VARCHAR(20) NOT NULL,
    distance_km INT NOT NULL,
    special_needs TINYINT(1) NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS rooms (
    room_id VARCHAR(20) PRIMARY KEY,
    hostel VARCHAR(50) NOT NULL,
    gender CHAR(1) NOT NULL,
    floor TINYINT NOT NULL,
    mess_distance_m INT NOT NULL,
    accessible TINYINT(1) NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS allocations (
    student_id VARCHAR(20) PRIMARY KEY,
    room_id VARCHAR(20) NOT NULL UNIQUE,
    FOREIGN KEY (student_id) REFERENCES students(student_id) ON DELETE CASCADE,
    FOREIGN KEY (room_id) REFERENCES rooms(room_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS policy_rules (
    rule_key VARCHAR(40) PRIMARY KEY,
    value DECIMAL(6,3) NOT NULL
);

CREATE TABLE IF NOT EXISTS audit_results (
    student_id VARCHAR(20) PRIMARY KEY,
    priority_score DECIMAL(6,2),
    expected_room_id VARCHAR(20),
    actual_room_id VARCHAR(20),
    deviation INT,
    status VARCHAR(30),
    hard_rule_violation TINYINT(1),
    audited_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
