"""
MCP Configuration - Arealis Gateway v2

Configuration management for Master Control Process including agent settings,
workflow parameters, and system monitoring configuration.
"""

import os
from typing import Dict, List, Any, Optional
from pydantic_settings import BaseSettings
from pydantic import Field
from enum import Enum

class AgentStatus(str, Enum):
    """Agent status enumeration."""
    IDLE = "IDLE"
    RUNNING = "RUNNING"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    HOLD = "HOLD"

class WorkflowStatus(str, Enum):
    """Workflow status enumeration."""
    INITIALIZED = "INITIALIZED"
    INGESTING = "INGESTING"
    VALIDATING = "VALIDATING"
    CLASSIFYING = "CLASSIFYING"
    ROUTING = "ROUTING"
    EXECUTING = "EXECUTING"
    AUDITING = "AUDITING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    HOLD = "HOLD"

class MCPConfig(BaseSettings):
    """Configuration settings for Master Control Process."""
    
    # Application Settings
    app_name: str = "Arealis Gateway v2 MCP"
    app_version: str = "2.0.0"
    debug: bool = Field(default=False, env="MCP_DEBUG")
    
    # MCP Core Settings
    mcp_host: str = Field(default="0.0.0.0", env="MCP_HOST")
    mcp_port: int = Field(default=8000, env="MCP_PORT")
    mcp_timeout: int = Field(default=300, env="MCP_TIMEOUT")
    max_concurrent_workflows: int = Field(default=50, env="MAX_CONCURRENT_WORKFLOWS")
    
    # Agent Configuration
    agent_timeout: int = Field(default=60, env="AGENT_TIMEOUT")
    agent_retry_count: int = Field(default=3, env="AGENT_RETRY_COUNT")
    agent_retry_delay: int = Field(default=5, env="AGENT_RETRY_DELAY")
    agent_health_check_interval: int = Field(default=30, env="AGENT_HEALTH_CHECK_INTERVAL")
    
    # Workflow Configuration
    workflow_timeout: int = Field(default=1800, env="WORKFLOW_TIMEOUT")  # 30 minutes
    workflow_cleanup_interval: int = Field(default=3600, env="WORKFLOW_CLEANUP_INTERVAL")  # 1 hour
    workflow_retention_hours: int = Field(default=24, env="WORKFLOW_RETENTION_HOURS")
    
    # Event Processing
    event_batch_size: int = Field(default=100, env="EVENT_BATCH_SIZE")
    event_processing_interval: int = Field(default=1, env="EVENT_PROCESSING_INTERVAL")
    event_retry_count: int = Field(default=3, env="EVENT_RETRY_COUNT")
    
    # Database Configuration
    db_host: str = Field(default="localhost", env="DB_HOST")
    db_port: int = Field(default=5432, env="DB_PORT")
    db_name: str = Field(default="arealis_gateway", env="DB_NAME")
    db_user: str = Field(default="postgres", env="DB_USER")
    db_password: str = Field(default="password", env="DB_PASSWORD")
    db_pool_size: int = Field(default=20, env="DB_POOL_SIZE")
    db_max_overflow: int = Field(default=30, env="DB_MAX_OVERFLOW")
    
    # S3 Configuration
    s3_bucket_name: str = Field(default="arealis-invoices", env="S3_BUCKET_NAME")
    s3_region: str = Field(default="us-east-1", env="S3_REGION")
    s3_access_key: Optional[str] = Field(default=None, env="AWS_ACCESS_KEY_ID")
    s3_secret_key: Optional[str] = Field(default=None, env="AWS_SECRET_ACCESS_KEY")
    
    # Layer Configuration
    ingest_layer_config: Dict[str, Any] = Field(default={
        "FrontendIngestor": {"api_port": 8001, "timeout": 30},
        "InvoiceValidator": {"validation_timeout": 300, "max_file_size": 10485760}
    })
    
    intent_router_layer_config: Dict[str, Any] = Field(default={
        "IntentClassifier": {"risk_threshold": 0.5, "confidence_threshold": 0.85},
        "WorkflowSelector": {"workflow_mappings": {}}
    })
    
    orchestration_layer_config: Dict[str, Any] = Field(default={
        "Orchestrator": {"max_concurrent": 5, "timeout": 120},
        "PDR": {"routing_timeout": 60, "max_routes": 3},
        "Execution": {"execution_timeout": 120, "retry_count": 2},
        "ARL": {"arl_timeout": 30, "check_interval": 10},
        "CRRAK": {"crrak_timeout": 30, "compliance_check": True}
    })
    
    audit_layer_config: Dict[str, Any] = Field(default={
        "AuditLogger": {"audit_retention_days": 365, "log_level": "INFO"},
        "ComplianceChecker": {"rbi_compliance": True, "audit_trail": True}
    })
    
    memory_layer_config: Dict[str, Any] = Field(default={
        "ContextMemory": {"memory_retention_hours": 24, "max_memory_size": 1000000}
    })
    
    observability_layer_config: Dict[str, Any] = Field(default={
        "Monitor": {"metrics_interval": 60, "health_check_interval": 30},
        "Debugger": {"debug_level": "INFO", "log_retention_days": 7}
    })
    
    prompt_layer_config: Dict[str, Any] = Field(default={
        "PromptGenerator": {"prompt_templates": {}, "max_tokens": 1000},
        "PromptValidator": {"validation_rules": {}, "strict_mode": True}
    })
    
    security_layer_config: Dict[str, Any] = Field(default={
        "SanctionScanner": {"sanction_lists": [], "scan_interval": 3600}
    })
    
    # Monitoring Configuration
    enable_metrics: bool = Field(default=True, env="ENABLE_METRICS")
    metrics_port: int = Field(default=9090, env="METRICS_PORT")
    metrics_interval: int = Field(default=60, env="METRICS_INTERVAL")
    
    # Logging Configuration
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    log_format: str = Field(default="json", env="LOG_FORMAT")
    log_file: Optional[str] = Field(default=None, env="LOG_FILE")
    log_retention_days: int = Field(default=30, env="LOG_RETENTION_DAYS")
    
    # Security Configuration
    jwt_secret: Optional[str] = Field(default=None, env="JWT_SECRET")
    jwt_algorithm: str = Field(default="HS256", env="JWT_ALGORITHM")
    jwt_expiration: int = Field(default=3600, env="JWT_EXPIRATION")
    
    # Rate Limiting
    rate_limit_requests: int = Field(default=1000, env="RATE_LIMIT_REQUESTS")
    rate_limit_window: int = Field(default=3600, env="RATE_LIMIT_WINDOW")
    
    # RBI Compliance
    audit_retention_days: int = Field(default=365, env="AUDIT_RETENTION_DAYS")
    data_retention_days: int = Field(default=1095, env="DATA_RETENTION_DAYS")
    compliance_mode: bool = Field(default=True, env="COMPLIANCE_MODE")
    
    # Performance Tuning
    thread_pool_size: int = Field(default=10, env="THREAD_POOL_SIZE")
    async_pool_size: int = Field(default=20, env="ASYNC_POOL_SIZE")
    memory_limit_mb: int = Field(default=1024, env="MEMORY_LIMIT_MB")
    
    # Error Handling
    error_notification_email: Optional[str] = Field(default=None, env="ERROR_NOTIFICATION_EMAIL")
    error_notification_webhook: Optional[str] = Field(default=None, env="ERROR_NOTIFICATION_WEBHOOK")
    critical_error_threshold: int = Field(default=5, env="CRITICAL_ERROR_THRESHOLD")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False

# Global configuration instance
mcp_config = MCPConfig()

# Database URL for SQLAlchemy
DATABASE_URL = f"postgresql://{mcp_config.db_user}:{mcp_config.db_password}@{mcp_config.db_host}:{mcp_config.db_port}/{mcp_config.db_name}"

# S3 Configuration for boto3
S3_CONFIG = {
    "region_name": mcp_config.s3_region,
    "aws_access_key_id": mcp_config.s3_access_key,
    "aws_secret_access_key": mcp_config.s3_secret_key
}

# Remove None values for boto3
S3_CONFIG = {k: v for k, v in S3_CONFIG.items() if v is not None}

# Agent dependency graph
AGENT_DEPENDENCIES = {
    "FrontendIngestor": [],
    "InvoiceValidator": ["FrontendIngestor"],
    "IntentClassifier": ["InvoiceValidator"],
    "WorkflowSelector": ["IntentClassifier"],
    "Orchestrator": ["WorkflowSelector"],
    "PDR": ["Orchestrator"],
    "Execution": ["PDR"],
    "ARL": ["Execution"],
    "CRRAK": ["ARL"],
    "AuditLogger": [],
    "ComplianceChecker": ["AuditLogger"],
    "ContextMemory": [],
    "Monitor": [],
    "Debugger": ["Monitor"],
    "PromptGenerator": [],
    "PromptValidator": ["PromptGenerator"],
    "SanctionScanner": []
}

# Layer to agent mapping
LAYER_AGENTS = {
    "ingest": ["FrontendIngestor", "InvoiceValidator"],
    "intent-router": ["IntentClassifier", "WorkflowSelector"],
    "orchestration": ["Orchestrator", "PDR", "Execution", "ARL", "CRRAK"],
    "audit": ["AuditLogger", "ComplianceChecker"],
    "memory": ["ContextMemory"],
    "observability": ["Monitor", "Debugger"],
    "prompt": ["PromptGenerator", "PromptValidator"],
    "security": ["SanctionScanner"]
}

# Workflow status transitions
WORKFLOW_TRANSITIONS = {
    WorkflowStatus.INITIALIZED: [WorkflowStatus.INGESTING, WorkflowStatus.FAILED],
    WorkflowStatus.INGESTING: [WorkflowStatus.VALIDATING, WorkflowStatus.FAILED],
    WorkflowStatus.VALIDATING: [WorkflowStatus.CLASSIFYING, WorkflowStatus.FAILED],
    WorkflowStatus.CLASSIFYING: [WorkflowStatus.ROUTING, WorkflowStatus.FAILED],
    WorkflowStatus.ROUTING: [WorkflowStatus.EXECUTING, WorkflowStatus.FAILED],
    WorkflowStatus.EXECUTING: [WorkflowStatus.AUDITING, WorkflowStatus.FAILED],
    WorkflowStatus.AUDITING: [WorkflowStatus.COMPLETED, WorkflowStatus.FAILED],
    WorkflowStatus.COMPLETED: [],
    WorkflowStatus.FAILED: [WorkflowStatus.INGESTING],  # Allow retry
    WorkflowStatus.HOLD: [WorkflowStatus.INGESTING, WorkflowStatus.FAILED]
}

# Event routing configuration
EVENT_ROUTING = {
    "invoice_received": ["ingest"],
    "validated_invoice": ["intent-router"],
    "workflow_selected": ["orchestration"],
    "pdr_result": ["orchestration"],
    "execution_result": ["orchestration"],
    "workflow_complete_v2": ["audit"],
    "audit_report_generated": ["memory", "observability"],
    "agent_failed": ["observability", "security"]
}
