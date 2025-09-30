# General Configuration
variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "us-east-1"
}

variable "project_name" {
  description = "Name of the project (used for resource naming)"
  type        = string
  default     = "vpc-infrastructure"
}

variable "environment" {
  description = "Environment name"
  type        = string
  default     = "prod"
}

variable "tags" {
  description = "Tags to apply to all resources"
  type        = map(string)
  default = {
    Environment = "prod"
    Project     = "vpc-infrastructure"
    Owner       = "yaswanth"
    ManagedBy   = "terraform"
    CostCenter  = "engineering"
  }
}

# VPC Configuration
variable "vpc_cidr" {
  description = "CIDR block for VPC"
  type        = string
  default     = "10.0.0.0/16"
}

variable "availability_zones" {
  description = "List of availability zones"
  type        = list(string)
  default     = ["us-east-1a", "us-east-1b"]
}

# Public Subnet Configuration
variable "public_subnet_cidrs" {
  description = "CIDR blocks for public subnets"
  type        = list(string)
  default     = ["10.0.1.0/24", "10.0.2.0/24"]
}

# Private Subnet Configuration
variable "private_subnet_cidrs" {
  description = "CIDR blocks for private subnets"
  type        = list(string)
  default     = ["10.0.10.0/24", "10.0.20.0/24"]
}

# Database Subnet Configuration
variable "database_subnet_cidrs" {
  description = "CIDR blocks for database subnets"
  type        = list(string)
  default     = ["10.0.30.0/24", "10.0.40.0/24"]
}

# NAT Gateway Configuration
variable "enable_nat_gateway" {
  description = "Enable NAT Gateway for private subnets"
  type        = bool
  default     = true
}

variable "enable_vpn_gateway" {
  description = "Enable VPN Gateway"
  type        = bool
  default     = false
}

variable "enable_dns_hostnames" {
  description = "Enable DNS hostnames in VPC"
  type        = bool
  default     = true
}

variable "enable_dns_support" {
  description = "Enable DNS support in VPC"
  type        = bool
  default     = true
}

# Single NAT Gateway Configuration
variable "single_nat_gateway" {
  description = "Use a single NAT Gateway for all private subnets"
  type        = bool
  default     = false
}

# VPC Endpoints Configuration
variable "enable_s3_endpoint" {
  description = "Enable S3 VPC endpoint"
  type        = bool
  default     = false
}

variable "enable_dynamodb_endpoint" {
  description = "Enable DynamoDB VPC endpoint"
  type        = bool
  default     = false
}

# RDS Configuration
# PostgreSQL Configuration
variable "postgres_engine_version" {
  description = "PostgreSQL engine version"
  type        = string
  default     = "14.12"
}

variable "postgres_major_version" {
  description = "PostgreSQL major version for parameter group"
  type        = string
  default     = "postgres14"
}

variable "postgres_instance_class" {
  description = "PostgreSQL instance class"
  type        = string
  default     = "db.t3.medium"
}

variable "postgres_allocated_storage" {
  description = "PostgreSQL initial allocated storage in GB"
  type        = number
  default     = 20
}

variable "postgres_max_allocated_storage" {
  description = "PostgreSQL maximum allocated storage for autoscaling in GB"
  type        = number
  default     = 100
}

variable "postgres_storage_type" {
  description = "PostgreSQL storage type"
  type        = string
  default     = "gp3"
}

variable "postgres_storage_encrypted" {
  description = "Enable storage encryption for PostgreSQL"
  type        = bool
  default     = true
}

variable "postgres_multi_az" {
  description = "Enable Multi-AZ for PostgreSQL"
  type        = bool
  default     = true
}

variable "postgres_performance_insights" {
  description = "Enable Performance Insights for PostgreSQL"
  type        = bool
  default     = false
}

variable "postgres_db_name" {
  description = "PostgreSQL database name"
  type        = string
  default     = "postgresdb"
}

variable "postgres_username" {
  description = "PostgreSQL master username"
  type        = string
  default     = "postgres"
}

# MySQL Configuration
variable "mysql_engine_version" {
  description = "MySQL engine version"
  type        = string
  default     = "8.0.42"
}

variable "mysql_major_version" {
  description = "MySQL major version for parameter group"
  type        = string
  default     = "mysql8.0"
}

variable "mysql_instance_class" {
  description = "MySQL instance class"
  type        = string
  default     = "db.t3.medium"
}

variable "mysql_allocated_storage" {
  description = "MySQL initial allocated storage in GB"
  type        = number
  default     = 20
}

variable "mysql_max_allocated_storage" {
  description = "MySQL maximum allocated storage for autoscaling in GB"
  type        = number
  default     = 100
}

variable "mysql_storage_type" {
  description = "MySQL storage type"
  type        = string
  default     = "gp3"
}

variable "mysql_storage_encrypted" {
  description = "Enable storage encryption for MySQL"
  type        = bool
  default     = true
}

variable "mysql_multi_az" {
  description = "Enable Multi-AZ for MySQL"
  type        = bool
  default     = true
}

variable "mysql_performance_insights" {
  description = "Enable Performance Insights for MySQL"
  type        = bool
  default     = false
}

variable "mysql_db_name" {
  description = "MySQL database name"
  type        = string
  default     = "mysqldb"
}

variable "mysql_username" {
  description = "MySQL master username"
  type        = string
  default     = "admin"
}

# Database General Configuration
variable "backup_retention_period" {
  description = "Backup retention period in days"
  type        = number
  default     = 7
}

# EC2 Monitoring Configuration
variable "monitoring_instance_type" {
  description = "EC2 instance type for monitoring server"
  type        = string
  default     = "t3.large"
}

variable "monitoring_volume_size" {
  description = "Root volume size for monitoring server (GB)"
  type        = number
  default     = 50
}

variable "backup_window" {
  description = "Backup window"
  type        = string
  default     = "03:00-04:00"
}

variable "maintenance_window" {
  description = "Maintenance window"
  type        = string
  default     = "sun:04:00-sun:05:00"
}

variable "deletion_protection" {
  description = "Enable deletion protection for RDS instances"
  type        = bool
  default     = true
}

variable "skip_final_snapshot" {
  description = "Skip final snapshot on deletion"
  type        = bool
  default     = false
}

variable "apply_immediately" {
  description = "Apply changes immediately"
  type        = bool
  default     = false
}
