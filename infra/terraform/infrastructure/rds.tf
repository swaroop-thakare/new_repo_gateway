# Database passwords
locals {
  postgres_password = "arealisgateway"
  mysql_password    = "arealisgateway"
}

# PostgreSQL DB Parameter Group
resource "aws_db_parameter_group" "postgres" {
  family = var.postgres_major_version
  name   = "${var.project_name}-postgres-param-group"

  parameter {
    name         = "log_min_duration_statement"
    value        = "1000"  # Log statements taking longer than 1 second
    apply_method = "pending-reboot"
  }

  parameter {
    name         = "max_connections"
    value        = "100"    # Adjust based on instance class
    apply_method = "pending-reboot"
  }

  parameter {
    name         = "shared_preload_libraries"
    value        = "pg_stat_statements"  # Enable query statistics
    apply_method = "pending-reboot"       # Requires database restart
  }

  tags = merge(var.tags, {
    Name = "${var.project_name}-postgres-param-group"
  })
}

# MySQL DB Parameter Group
resource "aws_db_parameter_group" "mysql" {
  family = var.mysql_major_version
  name   = "${var.project_name}-mysql-param-group"

  parameter {
    name  = "max_connections"
    value = "100"    # Adjust based on instance class
  }

  parameter {
    name  = "innodb_buffer_pool_size"
    value = "{DBInstanceClassMemory*3/4}"  # Use 75% of instance memory
  }

  parameter {
    name  = "slow_query_log"
    value = "1"      # Enable slow query log
  }

  parameter {
    name  = "long_query_time"
    value = "2"      # Log queries taking longer than 2 seconds
  }

  tags = merge(var.tags, {
    Name = "${var.project_name}-mysql-param-group"
  })
}

# Security Group for RDS Databases
resource "aws_security_group" "rds" {
  name_prefix = "${var.project_name}-rds-"
  vpc_id      = aws_vpc.main.id

  # PostgreSQL access from anywhere
  ingress {
    from_port   = 5432
    to_port     = 5432
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
    description = "PostgreSQL access from anywhere"
  }

  # MySQL access from anywhere
  ingress {
    from_port   = 3306
    to_port     = 3306
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
    description = "MySQL access from anywhere"
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
    description = "All outbound traffic"
  }

  tags = merge(var.tags, {
    Name = "${var.project_name}-rds-sg"
  })

  depends_on = [aws_vpc.main]
}

# PostgreSQL RDS Instance
resource "aws_db_instance" "postgres" {
  identifier = "${var.project_name}-postgres"

  # Engine configuration
  engine         = "postgres"
  engine_version = var.postgres_engine_version

  # Instance configuration
  instance_class    = var.postgres_instance_class
  allocated_storage = var.postgres_allocated_storage
  storage_type      = var.postgres_storage_type
  storage_encrypted = var.postgres_storage_encrypted

  # Storage autoscaling
  max_allocated_storage = var.postgres_max_allocated_storage

  # Database configuration
  db_name  = var.postgres_db_name
  username = var.postgres_username
  password = local.postgres_password

  # Network configuration
  db_subnet_group_name   = aws_db_subnet_group.main.name
  vpc_security_group_ids = [aws_security_group.rds.id]
  publicly_accessible    = true  # Public access enabled

  # Backup configuration
  backup_retention_period = var.backup_retention_period
  backup_window          = var.backup_window
  maintenance_window     = var.maintenance_window

  # High availability
  multi_az = var.postgres_multi_az

  # Parameter group
  parameter_group_name = aws_db_parameter_group.postgres.name

  # Security and monitoring
  deletion_protection = var.deletion_protection
  skip_final_snapshot = var.skip_final_snapshot
  final_snapshot_identifier = var.skip_final_snapshot ? null : "${var.project_name}-postgres-final-snapshot-${formatdate("YYYY-MM-DD-hhmm", timestamp())}"

  # Performance insights
  performance_insights_enabled = var.postgres_performance_insights

  # Apply changes
  apply_immediately = var.apply_immediately

  tags = merge(var.tags, {
    Name = "${var.project_name}-postgres"
  })

  depends_on = [aws_db_parameter_group.postgres, aws_db_subnet_group.main, aws_security_group.rds]
}

# MySQL RDS Instance
resource "aws_db_instance" "mysql" {
  identifier = "${var.project_name}-mysql"

  # Engine configuration
  engine         = "mysql"
  engine_version = var.mysql_engine_version

  # Instance configuration
  instance_class    = var.mysql_instance_class
  allocated_storage = var.mysql_allocated_storage
  storage_type      = var.mysql_storage_type
  storage_encrypted = var.mysql_storage_encrypted

  # Storage autoscaling
  max_allocated_storage = var.mysql_max_allocated_storage

  # Database configuration
  db_name  = var.mysql_db_name
  username = var.mysql_username
  password = local.mysql_password

  # Network configuration
  db_subnet_group_name   = aws_db_subnet_group.main.name
  vpc_security_group_ids = [aws_security_group.rds.id]
  publicly_accessible    = true  # Public access enabled

  # Backup configuration
  backup_retention_period = var.backup_retention_period
  backup_window          = var.backup_window
  maintenance_window     = var.maintenance_window

  # High availability
  multi_az = var.mysql_multi_az

  # Parameter group
  parameter_group_name = aws_db_parameter_group.mysql.name

  # Security and monitoring
  deletion_protection = var.deletion_protection
  skip_final_snapshot = var.skip_final_snapshot
  final_snapshot_identifier = var.skip_final_snapshot ? null : "${var.project_name}-mysql-final-snapshot-${formatdate("YYYY-MM-DD-hhmm", timestamp())}"

  # Performance insights
  performance_insights_enabled = var.mysql_performance_insights

  # Apply changes
  apply_immediately = var.apply_immediately

  tags = merge(var.tags, {
    Name = "${var.project_name}-mysql"
  })

  depends_on = [aws_db_parameter_group.mysql, aws_db_subnet_group.main, aws_security_group.rds]
}
