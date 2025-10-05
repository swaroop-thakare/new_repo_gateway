-- MCP Database Schema for Arealis Gateway v2
-- Supports Master Control Process workflow management and agent coordination

-- Workflow states table
CREATE TABLE IF NOT EXISTS workflow_states (
    workflow_id VARCHAR(100) PRIMARY KEY,
    batch_id VARCHAR(50) NOT NULL,
    tenant_id VARCHAR(10) NOT NULL,
    status VARCHAR(20) NOT NULL,
    current_layer VARCHAR(20),
    current_agent VARCHAR(50),
    data JSONB,
    errors JSONB,
    start_time TIMESTAMP NOT NULL,
    last_update TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Agent registry table
CREATE TABLE IF NOT EXISTS agent_registry (
    agent_name VARCHAR(50) PRIMARY KEY,
    layer VARCHAR(20) NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'IDLE',
    dependencies JSONB,
    config JSONB,
    last_run TIMESTAMP,
    error_count INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Event log table for MCP coordination
CREATE TABLE IF NOT EXISTS event_log (
    id SERIAL PRIMARY KEY,
    workflow_id VARCHAR(100),
    event_name VARCHAR(50) NOT NULL,
    event_data JSONB,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    processed BOOLEAN DEFAULT FALSE
);

-- Workflow execution history
CREATE TABLE IF NOT EXISTS workflow_history (
    id SERIAL PRIMARY KEY,
    workflow_id VARCHAR(100) NOT NULL,
    batch_id VARCHAR(50) NOT NULL,
    tenant_id VARCHAR(10) NOT NULL,
    status VARCHAR(20) NOT NULL,
    layer VARCHAR(20),
    agent VARCHAR(50),
    duration_ms INTEGER,
    error_message TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Agent performance metrics
CREATE TABLE IF NOT EXISTS agent_metrics (
    id SERIAL PRIMARY KEY,
    agent_name VARCHAR(50) NOT NULL,
    layer VARCHAR(20) NOT NULL,
    execution_count INTEGER DEFAULT 0,
    success_count INTEGER DEFAULT 0,
    failure_count INTEGER DEFAULT 0,
    avg_duration_ms DECIMAL(10, 2),
    last_execution TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- System health monitoring
CREATE TABLE IF NOT EXISTS system_health (
    id SERIAL PRIMARY KEY,
    component VARCHAR(50) NOT NULL,
    status VARCHAR(20) NOT NULL,
    health_score DECIMAL(3, 2),
    metrics JSONB,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_workflow_states_batch_id ON workflow_states(batch_id);
CREATE INDEX IF NOT EXISTS idx_workflow_states_tenant_id ON workflow_states(tenant_id);
CREATE INDEX IF NOT EXISTS idx_workflow_states_status ON workflow_states(status);
CREATE INDEX IF NOT EXISTS idx_workflow_states_last_update ON workflow_states(last_update);

CREATE INDEX IF NOT EXISTS idx_agent_registry_layer ON agent_registry(layer);
CREATE INDEX IF NOT EXISTS idx_agent_registry_status ON agent_registry(status);
CREATE INDEX IF NOT EXISTS idx_agent_registry_last_run ON agent_registry(last_run);

CREATE INDEX IF NOT EXISTS idx_event_log_workflow_id ON event_log(workflow_id);
CREATE INDEX IF NOT EXISTS idx_event_log_event_name ON event_log(event_name);
CREATE INDEX IF NOT EXISTS idx_event_log_timestamp ON event_log(timestamp);
CREATE INDEX IF NOT EXISTS idx_event_log_processed ON event_log(processed);

CREATE INDEX IF NOT EXISTS idx_workflow_history_workflow_id ON workflow_history(workflow_id);
CREATE INDEX IF NOT EXISTS idx_workflow_history_batch_id ON workflow_history(batch_id);
CREATE INDEX IF NOT EXISTS idx_workflow_history_status ON workflow_history(status);
CREATE INDEX IF NOT EXISTS idx_workflow_history_timestamp ON workflow_history(timestamp);

CREATE INDEX IF NOT EXISTS idx_agent_metrics_agent_name ON agent_metrics(agent_name);
CREATE INDEX IF NOT EXISTS idx_agent_metrics_layer ON agent_metrics(layer);
CREATE INDEX IF NOT EXISTS idx_agent_metrics_last_execution ON agent_metrics(last_execution);

CREATE INDEX IF NOT EXISTS idx_system_health_component ON system_health(component);
CREATE INDEX IF NOT EXISTS idx_system_health_status ON system_health(status);
CREATE INDEX IF NOT EXISTS idx_system_health_timestamp ON system_health(timestamp);

-- Triggers for updated_at timestamps
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_agent_registry_updated_at 
    BEFORE UPDATE ON agent_registry 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_agent_metrics_updated_at 
    BEFORE UPDATE ON agent_metrics 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Views for monitoring and reporting
CREATE OR REPLACE VIEW workflow_summary AS
SELECT 
    ws.workflow_id,
    ws.batch_id,
    ws.tenant_id,
    ws.status,
    ws.current_layer,
    ws.current_agent,
    ws.start_time,
    ws.last_update,
    EXTRACT(EPOCH FROM (ws.last_update - ws.start_time)) as duration_seconds,
    CASE 
        WHEN ws.status = 'COMPLETED' THEN 'SUCCESS'
        WHEN ws.status = 'FAILED' THEN 'FAILED'
        WHEN ws.status IN ('INGESTING', 'VALIDATING', 'CLASSIFYING', 'ROUTING', 'EXECUTING', 'AUDITING') THEN 'IN_PROGRESS'
        ELSE 'UNKNOWN'
    END as workflow_status
FROM workflow_states ws;

CREATE OR REPLACE VIEW agent_performance AS
SELECT 
    am.agent_name,
    am.layer,
    am.execution_count,
    am.success_count,
    am.failure_count,
    CASE 
        WHEN am.execution_count > 0 THEN 
            ROUND((am.success_count::DECIMAL / am.execution_count) * 100, 2)
        ELSE 0
    END as success_rate_percent,
    am.avg_duration_ms,
    am.last_execution
FROM agent_metrics am;

CREATE OR REPLACE VIEW system_health_summary AS
SELECT 
    component,
    status,
    health_score,
    timestamp,
    ROW_NUMBER() OVER (PARTITION BY component ORDER BY timestamp DESC) as rn
FROM system_health
WHERE timestamp >= CURRENT_TIMESTAMP - INTERVAL '1 hour';

-- Sample data insertion for testing
INSERT INTO agent_registry (agent_name, layer, status, dependencies, config) VALUES
('FrontendIngestor', 'ingest', 'IDLE', '[]', '{"api_port": 8001}'),
('InvoiceValidator', 'ingest', 'IDLE', '["FrontendIngestor"]', '{"validation_timeout": 300}'),
('IntentClassifier', 'intent-router', 'IDLE', '["InvoiceValidator"]', '{"risk_threshold": 0.5}'),
('WorkflowSelector', 'intent-router', 'IDLE', '["IntentClassifier"]', '{"workflow_mappings": {}}'),
('Orchestrator', 'orchestration', 'IDLE', '["WorkflowSelector"]', '{"max_concurrent": 5}'),
('PDR', 'orchestration', 'IDLE', '["Orchestrator"]', '{"routing_timeout": 60}'),
('Execution', 'orchestration', 'IDLE', '["PDR"]', '{"execution_timeout": 120}'),
('ARL', 'orchestration', 'IDLE', '["Execution"]', '{"arl_timeout": 30}'),
('CRRAK', 'orchestration', 'IDLE', '["ARL"]', '{"crrak_timeout": 30}'),
('AuditLogger', 'audit', 'IDLE', '[]', '{"audit_retention_days": 365}'),
('ComplianceChecker', 'audit', 'IDLE', '["AuditLogger"]', '{"rbi_compliance": true}'),
('ContextMemory', 'memory', 'IDLE', '[]', '{"memory_retention_hours": 24}'),
('Monitor', 'observability', 'IDLE', '[]', '{"metrics_interval": 60}'),
('Debugger', 'observability', 'IDLE', '["Monitor"]', '{"debug_level": "INFO"}'),
('PromptGenerator', 'prompt', 'IDLE', '[]', '{"prompt_templates": {}}'),
('PromptValidator', 'prompt', 'IDLE', '["PromptGenerator"]', '{"validation_rules": {}}'),
('SanctionScanner', 'security', 'IDLE', '[]', '{"sanction_lists": []}')
ON CONFLICT (agent_name) DO NOTHING;

-- Grant permissions (adjust as needed for your setup)
-- GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO arealis_user;
-- GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO arealis_user;
