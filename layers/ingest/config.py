"""
Configuration for Arealis Gateway v2 Ingest Layer

Environment-based configuration for S3, PostgreSQL, and other services.
"""

import os
from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import Field

class IngestConfig(BaseSettings):
    """Configuration settings for the Ingest Layer."""
    
    # Application Settings
    app_name: str = "Arealis Gateway v2 Ingest Layer"
    app_version: str = "2.0.0"
    debug: bool = Field(default=False, env="DEBUG")
    
    # API Settings
    api_host: str = Field(default="0.0.0.0", env="API_HOST")
    api_port: int = Field(default=8001, env="API_PORT")
    api_prefix: str = Field(default="/api/v1", env="API_PREFIX")
    
    # S3 Configuration
    s3_bucket_name: str = Field(default="arealis-invoices", env="S3_BUCKET_NAME")
    s3_region: str = Field(default="us-east-1", env="S3_REGION")
    s3_access_key: Optional[str] = Field(default=None, env="AWS_ACCESS_KEY_ID")
    s3_secret_key: Optional[str] = Field(default=None, env="AWS_SECRET_ACCESS_KEY")
    s3_kms_key_id: Optional[str] = Field(default=None, env="S3_KMS_KEY_ID")
    
    # S3 Paths
    s3_raw_prefix: str = "invoices/raw"
    s3_processed_prefix: str = "invoices/processed"
    s3_evidence_prefix: str = "evidence"
    
    # PostgreSQL Configuration
    db_host: str = Field(default="localhost", env="DB_HOST")
    db_port: int = Field(default=5432, env="DB_PORT")
    db_name: str = Field(default="arealis_gateway", env="DB_NAME")
    db_user: str = Field(default="postgres", env="DB_USER")
    db_password: str = Field(default="password", env="DB_PASSWORD")
    db_ssl_mode: str = Field(default="prefer", env="DB_SSL_MODE")
    
    # Database Connection Pool
    db_pool_size: int = Field(default=10, env="DB_POOL_SIZE")
    db_max_overflow: int = Field(default=20, env="DB_MAX_OVERFLOW")
    db_pool_timeout: int = Field(default=30, env="DB_POOL_TIMEOUT")
    
    # File Processing
    max_file_size: int = Field(default=10485760, env="MAX_FILE_SIZE")  # 10MB
    supported_file_types: list = ["text/csv", "application/json", "text/plain"]
    chunk_size: int = Field(default=8192, env="CHUNK_SIZE")
    
    # Validation Settings
    validation_timeout: int = Field(default=300, env="VALIDATION_TIMEOUT")  # 5 minutes
    max_validation_retries: int = Field(default=3, env="MAX_VALIDATION_RETRIES")
    
    # Intent Classification
    intent_classification_timeout: int = Field(default=600, env="INTENT_CLASSIFICATION_TIMEOUT")  # 10 minutes
    risk_score_threshold: float = Field(default=0.5, env="RISK_SCORE_THRESHOLD")
    confidence_threshold: float = Field(default=0.85, env="CONFIDENCE_THRESHOLD")
    
    # Logging
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    log_format: str = Field(default="json", env="LOG_FORMAT")
    log_file: Optional[str] = Field(default=None, env="LOG_FILE")
    
    # Security
    jwt_secret: Optional[str] = Field(default=None, env="JWT_SECRET")
    jwt_algorithm: str = Field(default="HS256", env="JWT_ALGORITHM")
    jwt_expiration: int = Field(default=3600, env="JWT_EXPIRATION")  # 1 hour
    
    # Rate Limiting
    rate_limit_requests: int = Field(default=100, env="RATE_LIMIT_REQUESTS")
    rate_limit_window: int = Field(default=3600, env="RATE_LIMIT_WINDOW")  # 1 hour
    
    # Monitoring
    enable_metrics: bool = Field(default=True, env="ENABLE_METRICS")
    metrics_port: int = Field(default=9090, env="METRICS_PORT")
    
    # RBI Compliance
    audit_retention_days: int = Field(default=365, env="AUDIT_RETENTION_DAYS")
    data_retention_days: int = Field(default=1095, env="DATA_RETENTION_DAYS")  # 3 years
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False

# Global configuration instance
config = IngestConfig()

# Database URL for SQLAlchemy
DATABASE_URL = f"postgresql://{config.db_user}:{config.db_password}@{config.db_host}:{config.db_port}/{config.db_name}"

# S3 Configuration for boto3
S3_CONFIG = {
    "region_name": config.s3_region,
    "aws_access_key_id": config.s3_access_key,
    "aws_secret_access_key": config.s3_secret_key
}

# Remove None values for boto3
S3_CONFIG = {k: v for k, v in S3_CONFIG.items() if v is not None}
