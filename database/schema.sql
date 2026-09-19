-- ============================================
-- HSMS DATABASE SCHEMA
-- Healthcare Security Management System
-- ============================================


-- ============================================
-- USERS TABLE
-- ============================================

CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    full_name TEXT NOT NULL,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    role TEXT NOT NULL,
    department TEXT,
    ward TEXT,
    status TEXT DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


-- ============================================
-- PATIENTS TABLE
-- ============================================

CREATE TABLE IF NOT EXISTS patients (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    patient_number TEXT UNIQUE NOT NULL,
    full_name TEXT NOT NULL,
    date_of_birth TEXT,
    blood_group TEXT,
    allergies TEXT,
    medical_conditions TEXT,
    medication TEXT,
    ward TEXT,
    assigned_doctor_id INTEGER,
    status TEXT DEFAULT 'active',

    FOREIGN KEY (assigned_doctor_id)
        REFERENCES users(id)
);


-- ============================================
-- ACCESS REQUESTS TABLE
-- ============================================

CREATE TABLE IF NOT EXISTS access_requests (
    id INTEGER PRIMARY KEY AUTOINCREMENT,

    user_id INTEGER NOT NULL,
    patient_id INTEGER NOT NULL,

    data_requested TEXT NOT NULL,
    reason TEXT,

    decision TEXT NOT NULL,
    risk_score INTEGER DEFAULT 0,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (user_id)
        REFERENCES users(id),

    FOREIGN KEY (patient_id)
        REFERENCES patients(id)
);


-- ============================================
-- AUDIT LOGS TABLE
-- ============================================

CREATE TABLE IF NOT EXISTS audit_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,

    user_id INTEGER,
    action TEXT NOT NULL,
    patient_id INTEGER,

    details TEXT,

    previous_hash TEXT,
    current_hash TEXT NOT NULL,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (user_id)
        REFERENCES users(id),

    FOREIGN KEY (patient_id)
        REFERENCES patients(id)
);


-- ============================================
-- SECURITY ALERTS TABLE
-- ============================================

CREATE TABLE IF NOT EXISTS security_alerts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,

    user_id INTEGER,

    alert_type TEXT NOT NULL,
    severity TEXT NOT NULL,

    description TEXT NOT NULL,

    risk_score INTEGER DEFAULT 0,

    status TEXT DEFAULT 'open',

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (user_id)
        REFERENCES users(id)
);
CREATE TABLE IF NOT EXISTS emergency_access (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    patient_id INTEGER NOT NULL,
    reason TEXT NOT NULL,
    risk_score INTEGER DEFAULT 90,
    status TEXT DEFAULT 'ACTIVE',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP,
    FOREIGN KEY (user_id)
        REFERENCES users(id),
    FOREIGN KEY (patient_id)
        REFERENCES patients(id)
);
CREATE TABLE IF NOT EXISTS offline_emergency_access (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    patient_id INTEGER NOT NULL,
    reason TEXT NOT NULL,
    access_type TEXT DEFAULT 'OFFLINE_EMERGENCY',
    synced INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id)
        REFERENCES users(id),
    FOREIGN KEY (patient_id)
        REFERENCES patients(id)
);