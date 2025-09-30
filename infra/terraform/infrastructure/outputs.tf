# VPC Outputs
output "vpc_id" {
  description = "ID of the VPC"
  value       = aws_vpc.main.id
}

output "vpc_cidr_block" {
  description = "CIDR block of the VPC"
  value       = aws_vpc.main.cidr_block
}

output "vpc_arn" {
  description = "ARN of the VPC"
  value       = aws_vpc.main.arn
}

# Internet Gateway Outputs
output "internet_gateway_id" {
  description = "ID of the Internet Gateway"
  value       = aws_internet_gateway.main.id
}

output "internet_gateway_arn" {
  description = "ARN of the Internet Gateway"
  value       = aws_internet_gateway.main.arn
}

# Public Subnet Outputs
output "public_subnet_ids" {
  description = "IDs of the public subnets"
  value       = aws_subnet.public[*].id
}

output "public_subnet_arns" {
  description = "ARNs of the public subnets"
  value       = aws_subnet.public[*].arn
}

output "public_subnet_cidrs" {
  description = "CIDR blocks of the public subnets"
  value       = aws_subnet.public[*].cidr_block
}

# Private Subnet Outputs
output "private_subnet_ids" {
  description = "IDs of the private subnets"
  value       = aws_subnet.private[*].id
}

output "private_subnet_arns" {
  description = "ARNs of the private subnets"
  value       = aws_subnet.private[*].arn
}

output "private_subnet_cidrs" {
  description = "CIDR blocks of the private subnets"
  value       = aws_subnet.private[*].cidr_block
}

# Database Subnet Outputs
output "database_subnet_ids" {
  description = "IDs of the database subnets"
  value       = aws_subnet.database[*].id
}

output "database_subnet_arns" {
  description = "ARNs of the database subnets"
  value       = aws_subnet.database[*].arn
}

output "database_subnet_cidrs" {
  description = "CIDR blocks of the database subnets"
  value       = aws_subnet.database[*].cidr_block
}

# NAT Gateway Outputs
output "nat_gateway_ids" {
  description = "IDs of the NAT Gateways"
  value       = aws_nat_gateway.main[*].id
}

output "nat_gateway_public_ips" {
  description = "Public IPs of the NAT Gateways"
  value       = aws_eip.nat[*].public_ip
}

output "nat_gateway_private_ips" {
  description = "Private IPs of the NAT Gateways"
  value       = aws_nat_gateway.main[*].private_ip
}

# Route Table Outputs
output "public_route_table_id" {
  description = "ID of the public route table"
  value       = aws_route_table.public.id
}

output "private_route_table_ids" {
  description = "IDs of the private route tables"
  value       = aws_route_table.private[*].id
}

output "database_route_table_id" {
  description = "ID of the database route table"
  value       = aws_route_table.database.id
}

# DB Subnet Group Outputs
output "db_subnet_group_name" {
  description = "Name of the DB subnet group"
  value       = aws_db_subnet_group.main.name
}

output "db_subnet_group_arn" {
  description = "ARN of the DB subnet group"
  value       = aws_db_subnet_group.main.arn
}

# VPC Endpoint Outputs
output "s3_endpoint_id" {
  description = "ID of the S3 VPC endpoint"
  value       = var.enable_s3_endpoint ? aws_vpc_endpoint.s3[0].id : null
}

output "dynamodb_endpoint_id" {
  description = "ID of the DynamoDB VPC endpoint"
  value       = var.enable_dynamodb_endpoint ? aws_vpc_endpoint.dynamodb[0].id : null
}

# Availability Zones
output "availability_zones" {
  description = "List of availability zones used"
  value       = var.availability_zones
}

# RDS Outputs
# PostgreSQL Outputs
output "postgres_endpoint" {
  description = "PostgreSQL RDS endpoint"
  value       = aws_db_instance.postgres.endpoint
}

output "postgres_address" {
  description = "PostgreSQL RDS address"
  value       = aws_db_instance.postgres.address
}

output "postgres_port" {
  description = "PostgreSQL RDS port"
  value       = aws_db_instance.postgres.port
}

output "postgres_db_name" {
  description = "PostgreSQL database name"
  value       = aws_db_instance.postgres.db_name
}

output "postgres_username" {
  description = "PostgreSQL username"
  value       = aws_db_instance.postgres.username
}

output "postgres_arn" {
  description = "PostgreSQL RDS ARN"
  value       = aws_db_instance.postgres.arn
}

# MySQL Outputs
output "mysql_endpoint" {
  description = "MySQL RDS endpoint"
  value       = aws_db_instance.mysql.endpoint
}

output "mysql_address" {
  description = "MySQL RDS address"
  value       = aws_db_instance.mysql.address
}

output "mysql_port" {
  description = "MySQL RDS port"
  value       = aws_db_instance.mysql.port
}

output "mysql_db_name" {
  description = "MySQL database name"
  value       = aws_db_instance.mysql.db_name
}

output "mysql_username" {
  description = "MySQL username"
  value       = aws_db_instance.mysql.username
}

output "mysql_arn" {
  description = "MySQL RDS ARN"
  value       = aws_db_instance.mysql.arn
}

# RDS Security Group Outputs
output "rds_security_group_id" {
  description = "ID of the RDS security group"
  value       = aws_security_group.rds.id
}

# Secrets Manager Outputs
output "postgres_secret_arn" {
  description = "ARN of the PostgreSQL secret"
  value       = aws_secretsmanager_secret.postgres.arn
}

output "mysql_secret_arn" {
  description = "ARN of the MySQL secret"
  value       = aws_secretsmanager_secret.mysql.arn
}

output "postgres_secret_name" {
  description = "Name of the PostgreSQL secret"
  value       = aws_secretsmanager_secret.postgres.name
}

output "mysql_secret_name" {
  description = "Name of the MySQL secret"
  value       = aws_secretsmanager_secret.mysql.name
}

# KMS Outputs
output "secrets_kms_key_id" {
  description = "ID of the Secrets Manager KMS key"
  value       = aws_kms_key.secrets.id
}

output "secrets_kms_key_arn" {
  description = "ARN of the Secrets Manager KMS key"
  value       = aws_kms_key.secrets.arn
}

output "secrets_kms_alias" {
  description = "Alias of the Secrets Manager KMS key"
  value       = aws_kms_alias.secrets.name
}

# EC2 Monitoring Outputs
output "monitoring_instance_id" {
  description = "ID of the monitoring EC2 instance"
  value       = aws_instance.monitoring.id
}

output "monitoring_public_ip" {
  description = "Public IP of the monitoring EC2 instance"
  value       = aws_instance.monitoring.public_ip
}

output "monitoring_public_dns" {
  description = "Public DNS of the monitoring EC2 instance"
  value       = aws_instance.monitoring.public_dns
}

output "monitoring_security_group_id" {
  description = "ID of the monitoring security group"
  value       = aws_security_group.monitoring.id
}

output "monitoring_key_name" {
  description = "Name of the monitoring key pair"
  value       = "us-east-1"  # Using existing keypair
}

output "monitoring_access_urls" {
  description = "Access URLs for monitoring services"
  value = {
    grafana       = "http://${aws_instance.monitoring.public_ip}:3000"
    prometheus    = "http://${aws_instance.monitoring.public_ip}:9090"
    jenkins       = "http://${aws_instance.monitoring.public_ip}:8080"
    node_exporter = "http://${aws_instance.monitoring.public_ip}:9100"
    sonarqube     = "http://${aws_instance.monitoring.public_ip}:9000"
  }
}

# Network Summary
output "network_summary" {
  description = "Summary of the network configuration"
  value = {
    vpc_id                = aws_vpc.main.id
    vpc_cidr             = aws_vpc.main.cidr_block
    public_subnets       = length(aws_subnet.public)
    private_subnets      = length(aws_subnet.private)
    database_subnets     = length(aws_subnet.database)
    nat_gateways         = var.enable_nat_gateway ? length(aws_nat_gateway.main) : 0
    availability_zones    = var.availability_zones
    rds_instances        = 2  # PostgreSQL and MySQL
    public_access        = true  # Both databases have public access
  }
}
