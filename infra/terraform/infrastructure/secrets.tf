# KMS Key for Secrets Manager encryption
resource "aws_kms_key" "secrets" {
  description             = "KMS key for Secrets Manager encryption"
  deletion_window_in_days = 7
  enable_key_rotation     = true

  tags = merge(var.tags, {
    Name = "${var.project_name}-secrets-kms-key"
  })
}

# KMS Key Alias
resource "aws_kms_alias" "secrets" {
  name          = "alias/${var.project_name}-secrets"
  target_key_id = aws_kms_key.secrets.key_id
}

# PostgreSQL Secret
resource "aws_secretsmanager_secret" "postgres" {
  name                    = "/${var.project_name}/rds/postgres-${formatdate("YYYYMMDD-hhmm", timestamp())}"
  description             = "PostgreSQL database credentials"
  kms_key_id              = aws_kms_key.secrets.arn
  recovery_window_in_days = 7

  tags = merge(var.tags, {
    Name = "${var.project_name}-postgres-secret"
  })
}

# MySQL Secret
resource "aws_secretsmanager_secret" "mysql" {
  name                    = "/${var.project_name}/rds/mysql-${formatdate("YYYYMMDD-hhmm", timestamp())}"
  description             = "MySQL database credentials"
  kms_key_id              = aws_kms_key.secrets.arn
  recovery_window_in_days = 7

  tags = merge(var.tags, {
    Name = "${var.project_name}-mysql-secret"
  })
}

# PostgreSQL Secret Version
resource "aws_secretsmanager_secret_version" "postgres" {
  secret_id = aws_secretsmanager_secret.postgres.id
  secret_string = jsonencode({
    username = var.postgres_username
    password = local.postgres_password
    host     = aws_db_instance.postgres.address
    port     = aws_db_instance.postgres.port
    dbname   = var.postgres_db_name
    engine   = "postgres"
    endpoint = aws_db_instance.postgres.endpoint
  })

  depends_on = [aws_db_instance.postgres]
}

# MySQL Secret Version
resource "aws_secretsmanager_secret_version" "mysql" {
  secret_id = aws_secretsmanager_secret.mysql.id
  secret_string = jsonencode({
    username = var.mysql_username
    password = local.mysql_password
    host     = aws_db_instance.mysql.address
    port     = aws_db_instance.mysql.port
    dbname   = var.mysql_db_name
    engine   = "mysql"
    endpoint = aws_db_instance.mysql.endpoint
  })

  depends_on = [aws_db_instance.mysql]
}
