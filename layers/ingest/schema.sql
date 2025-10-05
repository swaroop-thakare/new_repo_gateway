-- PostgreSQL Schema for Arealis Gateway v2 Ingest Layer
-- Supports frontend-uploaded invoice processing and storage

-- Create database (run as superuser)
-- CREATE DATABASE arealis_gateway;

-- Connect to database
-- \c arealis_gateway;

-- Invoices table - stores batch-level metadata
CREATE TABLE IF NOT EXISTS invoices (
    batch_id VARCHAR(50) PRIMARY KEY,
    tenant_id VARCHAR(10) NOT NULL,
    invoice_ref VARCHAR(50) NOT NULL,
    source VARCHAR(20) NOT NULL,
    policy_version VARCHAR(20) NOT NULL,
    upload_ts TIMESTAMP NOT NULL,
    validation_status VARCHAR(10) NOT NULL DEFAULT 'PENDING',
    issues JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Invoice lines table - stores individual transaction lines
CREATE TABLE IF NOT EXISTS invoice_lines (
    id SERIAL PRIMARY KEY,
    batch_id VARCHAR(50) REFERENCES invoices(batch_id) ON DELETE CASCADE,
    line_id VARCHAR(50) NOT NULL,
    transaction_type VARCHAR(20),
    amount DECIMAL(15, 2),
    currency VARCHAR(3),
    purpose VARCHAR(50),
    debit_account_number VARCHAR(50),
    credit_account_number VARCHAR(50),
    credit_ifsc VARCHAR(11),
    source_reference_number VARCHAR(50),
    remarks VARCHAR(200),
    transaction_date TIMESTAMP,
    evidence_ref VARCHAR(200),
    status VARCHAR(20) DEFAULT 'PENDING',
    validation_status VARCHAR(10) DEFAULT 'VALID',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Composite unique constraint
    UNIQUE(batch_id, line_id)
);

-- Intent classification results table
CREATE TABLE IF NOT EXISTS intent_results (
    id SERIAL PRIMARY KEY,
    batch_id VARCHAR(50) REFERENCES invoices(batch_id),
    line_id VARCHAR(50) NOT NULL,
    intent VARCHAR(50),
    risk_score DECIMAL(3, 2),
    confidence DECIMAL(3, 2),
    decision VARCHAR(20),
    workflow_id VARCHAR(50),
    agent_pipeline JSONB,
    axis_validation JSONB,
    evidence_ref VARCHAR(200),
    reasons JSONB,
    override BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Composite unique constraint
    UNIQUE(batch_id, line_id)
);

-- Audit log table for RBI compliance
CREATE TABLE IF NOT EXISTS audit_log (
    id SERIAL PRIMARY KEY,
    batch_id VARCHAR(50),
    line_id VARCHAR(50),
    action VARCHAR(50) NOT NULL,
    actor VARCHAR(50),
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    details JSONB,
    ip_address INET,
    user_agent TEXT
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_invoices_tenant_id ON invoices(tenant_id);
CREATE INDEX IF NOT EXISTS idx_invoices_upload_ts ON invoices(upload_ts);
CREATE INDEX IF NOT EXISTS idx_invoices_validation_status ON invoices(validation_status);

CREATE INDEX IF NOT EXISTS idx_invoice_lines_batch_id ON invoice_lines(batch_id);
CREATE INDEX IF NOT EXISTS idx_invoice_lines_line_id ON invoice_lines(line_id);
CREATE INDEX IF NOT EXISTS idx_invoice_lines_status ON invoice_lines(status);
CREATE INDEX IF NOT EXISTS idx_invoice_lines_purpose ON invoice_lines(purpose);

CREATE INDEX IF NOT EXISTS idx_intent_results_batch_id ON intent_results(batch_id);
CREATE INDEX IF NOT EXISTS idx_intent_results_line_id ON intent_results(line_id);
CREATE INDEX IF NOT EXISTS idx_intent_results_intent ON intent_results(intent);
CREATE INDEX IF NOT EXISTS idx_intent_results_decision ON intent_results(decision);

CREATE INDEX IF NOT EXISTS idx_audit_log_batch_id ON audit_log(batch_id);
CREATE INDEX IF NOT EXISTS idx_audit_log_timestamp ON audit_log(timestamp);
CREATE INDEX IF NOT EXISTS idx_audit_log_action ON audit_log(action);

-- Triggers for updated_at timestamps
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_invoices_updated_at 
    BEFORE UPDATE ON invoices 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_invoice_lines_updated_at 
    BEFORE UPDATE ON invoice_lines 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Views for common queries
CREATE OR REPLACE VIEW invoice_summary AS
SELECT 
    i.batch_id,
    i.tenant_id,
    i.invoice_ref,
    i.source,
    i.upload_ts,
    i.validation_status,
    COUNT(il.id) as line_count,
    SUM(il.amount) as total_amount,
    COUNT(CASE WHEN il.status = 'PENDING' THEN 1 END) as pending_lines,
    COUNT(CASE WHEN il.status = 'PROCESSED' THEN 1 END) as processed_lines
FROM invoices i
LEFT JOIN invoice_lines il ON i.batch_id = il.batch_id
GROUP BY i.batch_id, i.tenant_id, i.invoice_ref, i.source, i.upload_ts, i.validation_status;

CREATE OR REPLACE VIEW intent_classification_summary AS
SELECT 
    ir.batch_id,
    ir.line_id,
    ir.intent,
    ir.risk_score,
    ir.confidence,
    ir.decision,
    ir.workflow_id,
    il.amount,
    il.currency,
    il.purpose,
    il.status as line_status
FROM intent_results ir
JOIN invoice_lines il ON ir.batch_id = il.batch_id AND ir.line_id = il.line_id;

-- Sample data insertion (for testing)
INSERT INTO invoices (
    batch_id, tenant_id, invoice_ref, source, policy_version, upload_ts, validation_status
) VALUES (
    'B-2025-10-03-01', 'AXIS', 'INV-2025-10-03-001', 'FRONTEND_UPLOAD', 'intent-2.0.0', 
    '2025-10-03T23:06:00Z', 'VALID'
) ON CONFLICT (batch_id) DO NOTHING;

INSERT INTO invoice_lines (
    batch_id, line_id, transaction_type, amount, currency, purpose,
    debit_account_number, credit_account_number, credit_ifsc,
    source_reference_number, remarks, transaction_date, evidence_ref, status
) VALUES (
    'B-2025-10-03-01', 'L-1', 'MANUAL_INVOICE', 250000.00, 'INR', 'VENDOR_PAYMENT',
    '91402004****3081', '0052050****597', 'BARB0RAEBAR',
    'SRC20251003230600001', 'Supplier Payment', '2025-10-03T23:06:00Z',
    's3://arealis-invoices/invoices/processed/AXIS/B-2025-10-03-01/L-1.json', 'PENDING'
) ON CONFLICT (batch_id, line_id) DO NOTHING;

-- Grant permissions (adjust as needed for your setup)
-- GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO arealis_user;
-- GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO arealis_user;
