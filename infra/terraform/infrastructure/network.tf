# Network configuration to help with DNS resolution issues
# This file contains network-related configurations

# VPC Endpoint for STS (Security Token Service)
# This can help with authentication issues
resource "aws_vpc_endpoint" "sts" {
  count = var.enable_sts_endpoint ? 1 : 0

  vpc_id              = aws_vpc.main.id
  service_name        = "com.amazonaws.${var.aws_region}.sts"
  vpc_endpoint_type   = "Interface"
  subnet_ids          = aws_subnet.private[*].id
  security_group_ids  = [aws_security_group.vpc_endpoint[0].id]

  private_dns_enabled = true

  tags = merge(var.tags, {
    Name = "${var.project_name}-sts-endpoint"
  })

  depends_on = [aws_vpc.main]
}

# Security Group for VPC Endpoints
resource "aws_security_group" "vpc_endpoint" {
  count = var.enable_sts_endpoint ? 1 : 0

  name_prefix = "${var.project_name}-vpc-endpoint-"
  vpc_id      = aws_vpc.main.id

  ingress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = [var.vpc_cidr]
    description = "HTTPS access for VPC endpoints"
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
    description = "All outbound traffic"
  }

  tags = merge(var.tags, {
    Name = "${var.project_name}-vpc-endpoint-sg"
  })

  depends_on = [aws_vpc.main]
}
