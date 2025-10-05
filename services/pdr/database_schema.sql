-- ========================================
-- PDR (Payment Decision Router) Database Schema
-- ========================================

-- Create database if not exists (for local development)
-- CREATE DATABASE IF NOT EXISTS railway;

-- ========================================
-- Intent Table (Input from user/system)
-- ========================================
CREATE TABLE IF NOT EXISTS intent (
    id SERIAL PRIMARY KEY,
    transaction_id VARCHAR(100) UNIQUE NOT NULL,
    payment_type VARCHAR(50) NOT NULL, -- 'payroll', 'vendor_payment', 'loan_disbursement', etc.
    
    -- Sender details
    sender_name VARCHAR(255) NOT NULL,
    sender_account_number VARCHAR(50) NOT NULL,
    sender_ifsc_code VARCHAR(11) NOT NULL,
    sender_bank_name VARCHAR(255) NOT NULL,
    
    -- Receiver details
    receiver_name VARCHAR(255) NOT NULL,
    receiver_account_number VARCHAR(50) NOT NULL,
    receiver_ifsc_code VARCHAR(11) NOT NULL,
    receiver_bank_name VARCHAR(255) NOT NULL,
    
    -- Transaction details
    amount DECIMAL(15,2) NOT NULL,
    currency VARCHAR(3) DEFAULT 'INR',
    method VARCHAR(50), -- 'NEFT', 'IMPS', 'RTGS', 'UPI', etc.
    purpose VARCHAR(500) NOT NULL,
    schedule_datetime TIMESTAMP NOT NULL,
    
    -- Location details
    location_city VARCHAR(100),
    location_latitude DECIMAL(10,8),
    location_longitude DECIMAL(11,8),
    
    -- Additional fields (JSON for flexibility)
    additional_fields JSONB DEFAULT '{}',
    
    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(20) DEFAULT 'PENDING' -- 'PENDING', 'PROCESSING', 'COMPLETED', 'FAILED'
);

-- ========================================
-- ACC (Anti-Compliance Check) Results Table
-- ========================================
CREATE TABLE IF NOT EXISTS acc_decisions (
    id SERIAL PRIMARY KEY,
    transaction_id VARCHAR(100) NOT NULL,
    line_id VARCHAR(100) NOT NULL, -- Same as transaction_id for single transactions
    decision VARCHAR(10) NOT NULL, -- 'PASS', 'FAIL', 'ERROR'
    policy_version VARCHAR(20) NOT NULL,
    reasons TEXT[], -- Array of violation reasons
    evidence_refs TEXT[], -- Array of evidence reference keys
    
    -- Compliance scoring details
    compliance_penalty DECIMAL(5,2) DEFAULT 0.0, -- 0-100 penalty score
    risk_score DECIMAL(5,2) DEFAULT 0.0, -- 0-100 risk score
    
    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Foreign key
    FOREIGN KEY (transaction_id) REFERENCES intent(transaction_id) ON DELETE CASCADE
);

-- ========================================
-- Rail Configuration Table
-- ========================================
CREATE TABLE IF NOT EXISTS rail_config (
    id SERIAL PRIMARY KEY,
    rail_name VARCHAR(50) UNIQUE NOT NULL, -- 'IMPS', 'NEFT', 'RTGS', 'UPI', 'IFT'
    rail_type VARCHAR(20) NOT NULL, -- 'INSTANT', 'BATCH', 'REALTIME'
    
    -- Amount constraints
    min_amount DECIMAL(15,2) NOT NULL DEFAULT 0,
    max_amount DECIMAL(15,2) NOT NULL DEFAULT 999999999,
    new_user_limit DECIMAL(15,2) DEFAULT 50000,
    
    -- Operational constraints
    working_hours_start TIME DEFAULT '00:00:00',
    working_hours_end TIME DEFAULT '23:59:59',
    working_days INTEGER[] DEFAULT '{1,2,3,4,5,6,7}', -- 1=Monday, 7=Sunday
    
    -- Performance characteristics
    avg_eta_ms INTEGER NOT NULL, -- Average ETA in milliseconds
    cost_bps DECIMAL(8,4) NOT NULL DEFAULT 0, -- Cost in basis points
    success_probability DECIMAL(5,4) DEFAULT 0.95, -- Historical success rate
    
    -- Settlement characteristics
    settlement_type VARCHAR(20) DEFAULT 'INSTANT', -- 'INSTANT', 'IMMEDIATE', 'BATCH', 'DELAYED'
    settlement_certainty DECIMAL(3,2) DEFAULT 1.0, -- 0-1 certainty score
    
    -- API configuration
    api_endpoint VARCHAR(500),
    api_method VARCHAR(10) DEFAULT 'POST',
    api_headers JSONB DEFAULT '{}',
    
    -- Status and metadata
    is_active BOOLEAN DEFAULT true,
    daily_limit DECIMAL(15,2) DEFAULT 999999999,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ========================================
-- Rail Performance Tracking
-- ========================================
CREATE TABLE IF NOT EXISTS rail_performance (
    id SERIAL PRIMARY KEY,
    rail_name VARCHAR(50) NOT NULL,
    transaction_id VARCHAR(100) NOT NULL,
    
    -- Performance metrics
    actual_eta_ms INTEGER,
    success BOOLEAN NOT NULL,
    error_code VARCHAR(20),
    error_message TEXT,
    
    -- Timestamps
    initiated_at TIMESTAMP NOT NULL,
    completed_at TIMESTAMP,
    
    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (rail_name) REFERENCES rail_config(rail_name) ON DELETE CASCADE,
    FOREIGN KEY (transaction_id) REFERENCES intent(transaction_id) ON DELETE CASCADE
);

-- ========================================
-- PDR Decisions Table (Output)
-- ========================================
CREATE TABLE IF NOT EXISTS pdr_decisions (
    id SERIAL PRIMARY KEY,
    transaction_id VARCHAR(100) NOT NULL,
    
    -- Primary rail selection
    primary_rail VARCHAR(50) NOT NULL,
    primary_rail_score DECIMAL(8,4) NOT NULL,
    
    -- Fallback rails (ordered by score)
    fallback_rails JSONB NOT NULL DEFAULT '[]', -- Array of {rail_name, score}
    
    -- Scoring details
    scoring_features JSONB NOT NULL DEFAULT '{}', -- All normalized features used
    scoring_weights JSONB NOT NULL DEFAULT '{}', -- Weights used in scoring
    
    -- Execution tracking
    execution_status VARCHAR(20) DEFAULT 'PENDING', -- 'PENDING', 'EXECUTING', 'SUCCESS', 'FAILED'
    current_rail_attempt VARCHAR(50), -- Which rail is currently being tried
    attempt_count INTEGER DEFAULT 0,
    
    -- Results
    final_rail_used VARCHAR(50),
    final_utr_number VARCHAR(50),
    final_status VARCHAR(20), -- 'SUCCESS', 'FAILED', 'TIMEOUT'
    
    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Foreign keys
    FOREIGN KEY (transaction_id) REFERENCES intent(transaction_id) ON DELETE CASCADE,
    FOREIGN KEY (primary_rail) REFERENCES rail_config(rail_name) ON DELETE RESTRICT
);

-- ========================================
-- Indexes for Performance
-- ========================================
CREATE INDEX IF NOT EXISTS idx_intent_transaction_id ON intent(transaction_id);
CREATE INDEX IF NOT EXISTS idx_intent_status ON intent(status);
CREATE INDEX IF NOT EXISTS idx_intent_schedule_datetime ON intent(schedule_datetime);

CREATE INDEX IF NOT EXISTS idx_acc_decisions_transaction_id ON acc_decisions(transaction_id);
CREATE INDEX IF NOT EXISTS idx_acc_decisions_decision ON acc_decisions(decision);

CREATE INDEX IF NOT EXISTS idx_rail_config_rail_name ON rail_config(rail_name);
CREATE INDEX IF NOT EXISTS idx_rail_config_is_active ON rail_config(is_active);

CREATE INDEX IF NOT EXISTS idx_rail_performance_rail_name ON rail_performance(rail_name);
CREATE INDEX IF NOT EXISTS idx_rail_performance_success ON rail_performance(success);
CREATE INDEX IF NOT EXISTS idx_rail_performance_created_at ON rail_performance(created_at);

CREATE INDEX IF NOT EXISTS idx_pdr_decisions_transaction_id ON pdr_decisions(transaction_id);
CREATE INDEX IF NOT EXISTS idx_pdr_decisions_execution_status ON pdr_decisions(execution_status);

-- ========================================
-- Sample Data Insertion
-- ========================================

-- Insert rail configurations
INSERT INTO rail_config (
    rail_name, rail_type, min_amount, max_amount, new_user_limit,
    working_hours_start, working_hours_end, working_days,
    avg_eta_ms, cost_bps, success_probability,
    settlement_type, settlement_certainty,
    api_endpoint, api_method, api_headers
) VALUES 
-- UPI
('UPI', 'INSTANT', 1, 100000, 25000, '00:00:00', '23:59:59', '{1,2,3,4,5,6,7}',
 1000, 0, 0.98, 'INSTANT', 1.0,
 'https://mock-upi-api.com/transfer', 'POST', '{"Content-Type": "application/json"}'),

-- IMPS  
('IMPS', 'INSTANT', 1, 500000, 50000, '00:00:00', '23:59:59', '{1,2,3,4,5,6,7}',
 2000, 5, 0.96, 'INSTANT', 0.95,
 'https://apiportal.axis.bank.in/gateway/openapi/v1/imps/funds-transfer', 'POST', 
 '{"X-IBM-Client-Id": "clientId", "X-IBM-Client-Secret": "clientSecret", "Content-Type": "application/json"}'),

-- NEFT
('NEFT', 'BATCH', 1, 10000000, 200000, '08:00:00', '19:00:00', '{1,2,3,4,5,6}',
 1800000, 2.5, 0.94, 'BATCH', 0.4,
 'https://apiportal.axis.bank.in/gateway/neo-banking/generic/api/v1/payment-intiation-neft', 'POST',
 '{"X-IBM-Client-Id": "clientId", "X-IBM-Client-Secret": "clientSecret", "Content-Type": "application/json"}'),

-- RTGS
('RTGS', 'REALTIME', 200000, 50000000, 1000000, '09:00:00', '16:30:00', '{1,2,3,4,5,6}',
 300000, 25, 0.99, 'IMMEDIATE', 0.9,
 'https://apiportal.axis.bank.in/gateway/rtgs-payment-initiation/payment-intiation-rtgs', 'POST',
 '{"X-IBM-Client-Id": "clientId", "X-IBM-Client-Secret": "clientSecret", "Content-Type": "application/json"}'),

-- IFT (Intra-bank Fund Transfer)
('IFT', 'INSTANT', 1, 10000000, 500000, '00:00:00', '23:59:59', '{1,2,3,4,5,6,7}',
 500, 0, 0.99, 'INSTANT', 1.0,
 'https://apiportal.axis.bank.in/gateway/neo-banking/generic/api/v1/payment-intiation-ift', 'POST',
 '{"X-IBM-Client-Id": "clientId", "X-IBM-Client-Secret": "clientSecret", "Content-Type": "application/json"}');

-- Sample intent data
INSERT INTO intent (
    transaction_id, payment_type, sender_name, sender_account_number, sender_ifsc_code, sender_bank_name,
    receiver_name, receiver_account_number, receiver_ifsc_code, receiver_bank_name,
    amount, currency, purpose, schedule_datetime, location_city, location_latitude, location_longitude,
    additional_fields
) VALUES 
('TXN001', 'payroll', 'Arealis Corp', '1234567890', 'UTIB0000123', 'Axis Bank',
 'John Doe', '9876543210', 'HDFC0001234', 'HDFC Bank',
 50000.00, 'INR', 'Salary payment for December 2024', '2024-12-15 10:00:00',
 'Mumbai', 19.0760, 72.8777, '{"employee_id": "EMP001", "department": "Engineering"}'),

('TXN002', 'vendor_payment', 'Arealis Corp', '1234567890', 'UTIB0000123', 'Axis Bank',
 'Tech Supplies Ltd', '5555666677', 'ICIC0001111', 'ICICI Bank',
 250000.00, 'INR', 'Payment for software licenses', '2024-12-15 14:30:00',
 'Bangalore', 12.9716, 77.5946, '{"invoice_number": "INV-2024-001", "gst_number": "29ABCDE1234A1Z5"}'),

('TXN003', 'loan_disbursement', 'Arealis Bank', '9999888877', 'UTIB0000456', 'Axis Bank',
 'Small Business Owner', '1111222233', 'SBIN0001234', 'State Bank of India',
 500000.00, 'INR', 'Business loan disbursement', '2024-12-15 16:00:00',
 'Delhi', 28.7041, 77.1025, '{"loan_account_number": "LOAN123456", "loan_type": "business_loan"}');

-- Sample ACC decisions (these would normally be generated by ACC service)
INSERT INTO acc_decisions (
    transaction_id, line_id, decision, policy_version, reasons, evidence_refs,
    compliance_penalty, risk_score
) VALUES 
('TXN001', 'TXN001', 'PASS', 'acc-1.4.2', '{}', '{"bank", "kyc"}', 0.0, 5.0),
('TXN002', 'TXN002', 'PASS', 'acc-1.4.2', '{}', '{"bank", "gstin"}', 10.0, 15.0),
('TXN003', 'TXN003', 'PASS', 'acc-1.4.2', '{}', '{"bank", "loan_verification"}', 5.0, 8.0);