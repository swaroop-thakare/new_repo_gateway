# VPC Infrastructure with Terraform

This Terraform project creates a complete VPC infrastructure in the `us-east-1` region with all necessary networking components and dependencies for the vpc-infrastructure project.

## Architecture Overview

The infrastructure includes:

- **VPC**: Main Virtual Private Cloud with DNS support
- **Public Subnets**: 2 public subnets across 2 AZs with Internet Gateway access
- **Private Subnets**: 2 private subnets across 2 AZs with NAT Gateway access
- **Database Subnets**: 2 database subnets across 2 AZs for RDS instances
- **Internet Gateway**: For public internet access
- **NAT Gateway(s)**: For private subnet internet access (configurable)
- **Route Tables**: Separate routing for public, private, and database subnets
- **DB Subnet Group**: For RDS instances
- **VPC Endpoints**: Optional S3 and DynamoDB endpoints
- **RDS Databases**: PostgreSQL and MySQL with **PUBLIC ACCESS**
- **Security Groups**: Configured for public database access
- **Secrets Manager**: Database credentials stored securely
- **KMS Encryption**: Customer-managed keys for secrets encryption
- **Monitoring Server**: EC2 with Prometheus, Grafana, Jenkins, and CloudWatch
- **Development Tools**: Git, Jenkins CI/CD, Docker, and AWS CLI

## Project Structure

```
vpc-infrastructure/
├── main.tf                    # Main VPC configuration
├── rds.tf                     # RDS instances (PostgreSQL & MySQL)
├── secrets.tf                 # Secrets Manager for database credentials
├── ec2.tf                     # EC2 monitoring server with tools
├── user_data.sh               # EC2 initialization script
├── provider.tf                 # Provider configuration
├── variables.tf                # Input variables with defaults
├── outputs.tf                  # Output values
└── README.md                  # This file
```

## Key Features

- **Multi-AZ Deployment**: Subnets across 2 availability zones (us-east-1a, us-east-1b)
- **Flexible NAT Gateway**: Single or multiple NAT Gateways for cost optimization
- **Database Ready**: Dedicated database subnets with DB subnet group for RDS
- **VPC Endpoints**: Optional S3 and DynamoDB endpoints for cost optimization
- **Proper Dependencies**: All resources have correct dependency chains
- **Comprehensive Outputs**: All important resource information exposed
- **Owner Tagging**: All resources tagged with Owner: "yaswanth"
- **Production Ready**: Designed for production workloads with high availability
- **Public Database Access**: PostgreSQL and MySQL with internet access
- **High Availability**: Multi-AZ RDS instances with automated backups
- **Secrets Management**: Database credentials stored in AWS Secrets Manager
- **KMS Encryption**: Customer-managed keys for secure credential storage
- **Comprehensive Monitoring**: Prometheus + Grafana + CloudWatch integration
- **CI/CD Ready**: Jenkins with Git and Docker support
- **AWS Account Monitoring**: CloudWatch agent for full AWS account visibility

## Prerequisites

- Terraform >= 1.5
- AWS CLI configured with appropriate credentials
- AWS account with necessary permissions

## Quick Start

1. **Clone and navigate to the project**:
   ```bash
   cd vpc-infrastructure
   ```

2. **Initialize Terraform**:
   ```bash
   terraform init
   ```

3. **Plan the deployment**:
   ```bash
   terraform plan
   ```

4. **Apply the configuration**:
   ```bash
   terraform apply
   ```

**Note**: All configuration is set with default values in `variables.tf`. No additional configuration files needed!

## Configuration Options

### VPC Configuration
- **VPC CIDR**: Default `10.0.0.0/16` (65,536 IP addresses)
- **DNS Support**: Enabled by default for internal DNS resolution
- **DNS Hostnames**: Enabled by default for public DNS hostnames
- **Region**: us-east-1 (N. Virginia)

### Subnet Configuration
- **Public Subnets**: `10.0.1.0/24`, `10.0.2.0/24` (512 IPs each)
- **Private Subnets**: `10.0.10.0/24`, `10.0.20.0/24` (512 IPs each)
- **Database Subnets**: `10.0.30.0/24`, `10.0.40.0/24` (512 IPs each)
- **Availability Zones**: us-east-1a, us-east-1b

### NAT Gateway Options
- **Multiple NAT Gateways**: One per AZ (default, high availability)
- **Single NAT Gateway**: Cost optimization option (~$45/month savings)
- **No NAT Gateway**: For private-only workloads (no internet access)

### VPC Endpoints
- **S3 Endpoint**: Optional for cost optimization (no data transfer charges)
- **DynamoDB Endpoint**: Optional for cost optimization (no data transfer charges)

### Resource Tagging
- **Default Tags**: Environment=prod, Project=vpc-infrastructure, Owner=yaswanth
- **Custom Tags**: Configurable via variables
- **Cost Tracking**: All resources tagged for cost allocation

## Terraform Commands

### Initialize
```bash
terraform init
```

### Plan
```bash
terraform plan
```

### Apply
```bash
# Apply the changes to disable deletion protection
terraform apply -auto-approve

# Then destroy everything
terraform destroy -auto-ap|
prove
terraform apply
```

### Validate
```bash
terraform validate
```

### Format
```bash
terraform fmt
```

### Destroy
```bash
terraform destroy
```

## Outputs

The configuration provides comprehensive outputs:

- **VPC Information**: ID, CIDR, ARN
- **Subnet Information**: IDs, ARNs, CIDRs for all subnet types
- **Gateway Information**: Internet Gateway, NAT Gateways
- **Route Tables**: All route table IDs
- **DB Subnet Group**: Name and ARN
- **VPC Endpoints**: S3 and DynamoDB endpoint IDs
- **Network Summary**: Complete network overview

## Cost Considerations

### Estimated Monthly Costs (us-east-1)
- **NAT Gateway**: ~$45 per gateway
- **EIP for NAT**: ~$3.65 per IP
- **VPC Endpoints**: ~$7.20 per endpoint (if enabled)
- **RDS PostgreSQL (db.t3.medium)**: ~$50-70
- **RDS MySQL (db.t3.medium)**: ~$50-70
- **Data Transfer**: Varies based on usage

**Total**: ~$150-200/month depending on configuration

### Cost Optimization Tips
- Use `single_nat_gateway = true` for development (~$45/month savings)
- Enable VPC endpoints for S3/DynamoDB access (eliminates data transfer charges)
- Use smaller CIDR blocks if fewer IPs needed
- Consider reserved NAT Gateway capacity for production workloads
- Use smaller RDS instance classes for development (`db.t3.small`)
- Disable Multi-AZ for development environments

### Development vs Production
- **Development**: Single NAT Gateway, VPC endpoints enabled, smaller RDS instances
- **Production**: Multiple NAT Gateways, high availability configuration, Multi-AZ RDS

## Database Connectivity

### Public Access Configuration

Both PostgreSQL and MySQL databases are configured for public access:

- **PostgreSQL**: Accessible on port 5432 from anywhere (0.0.0.0/0)
- **MySQL**: Accessible on port 3306 from anywhere (0.0.0.0/0)
- **Public Endpoints**: Both databases will have public DNS endpoints
- **Security Groups**: Configured to allow traffic from any IP address

### Connection Information

After deployment, you can find the database endpoints in the Terraform outputs:
- `postgres_endpoint` - PostgreSQL connection string
- `mysql_endpoint` - MySQL connection string
- `postgres_address` - PostgreSQL hostname
- `mysql_address` - MySQL hostname

### Quick Connection Examples

**PostgreSQL Connection:**
```bash
# Get the endpoint
terraform output postgres_endpoint
terraform output postgres_address

# Connect using psql
psql -h <postgres_endpoint> -p 5432 -U postgres -d postgresdb
# Password: arealisgateway
```

**MySQL Connection:**
```bash
# Get the endpoint
terraform output mysql_endpoint
terraform output mysql_address

# Connect using mysql client
mysql -h <mysql_endpoint> -P 3306 -u mysql -p mysqldb
# Password: arealisgateway
```

**Note**: Database passwords are set to "arealisgateway" for both PostgreSQL and MySQL. Credentials are also stored securely in AWS Secrets Manager.

## Monitoring Server

### EC2 Monitoring Instance

The infrastructure includes a comprehensive monitoring server with the following tools:

#### **Installed Services:**
- **Grafana** (Port 3000): Advanced monitoring dashboards
- **Prometheus** (Port 9090): Metrics collection and storage
- **Jenkins** (Port 8080): CI/CD pipeline automation
- **Node Exporter** (Port 9100): System metrics collection
- **SonarQube** (Port 9000): Code quality analysis
- **MariaDB** (Port 3306): Database server
- **PostgreSQL** (Port 5432): Database server
- **CloudWatch Agent**: AWS account monitoring
- **Docker & Docker Compose**: Container orchestration
- **Git**: Version control system
- **AWS CLI v2**: AWS service management
- **Terraform**: Infrastructure as Code
- **Maven**: Build automation
- **Ansible**: Configuration management
- **kubectl**: Kubernetes CLI
- **eksctl**: EKS cluster management
- **Helm**: Kubernetes package manager
- **Trivy**: Security vulnerability scanner
- **Vault**: Secrets management
- **ArgoCD**: GitOps continuous delivery
- **Node.js & npm**: JavaScript runtime and package manager

#### **Access URLs:**
After deployment, access the services using the monitoring server's public IP:

```bash
# Get monitoring server details
terraform output monitoring_access_urls
terraform output monitoring_public_ip
```

**Service URLs:**
- **Grafana Dashboard**: `http://<public-ip>:3000` (admin/admin)
- **Prometheus**: `http://<public-ip>:9090`
- **Jenkins**: `http://<public-ip>:8080`
- **Node Exporter**: `http://<public-ip>:9100`
- **SonarQube**: `http://<public-ip>:9000` (admin/admin)
- **MariaDB**: `mysql://<public-ip>:3306`
- **PostgreSQL**: `postgresql://<public-ip>:5432`

#### **SSH Access:**
```bash
# SSH to monitoring server using your existing keypair
ssh -i ~/.ssh/us-east-1.pem ec2-user@<monitoring-public-ip>

# Check service status
systemctl status amazon-cloudwatch-agent jenkins prometheus node_exporter grafana-server

# View monitoring information
cat /home/ec2-user/monitoring-info.txt
```

#### **CloudWatch Integration:**
- **Metrics**: CPU, Memory, Disk, Network metrics sent to CloudWatch
- **Logs**: Application logs forwarded to CloudWatch Logs
- **Custom Dashboards**: Create CloudWatch dashboards for AWS account monitoring
- **Alarms**: Set up CloudWatch alarms for critical metrics

#### **Jenkins Setup:**
1. Access Jenkins at `http://<public-ip>:8080`
2. Get initial admin password:
   ```bash
   ssh -i ~/.ssh/us-east-1.pem ec2-user@<public-ip> "sudo cat /var/lib/jenkins/secrets/initialAdminPassword"
   ```
3. Complete Jenkins setup wizard
4. Install recommended plugins
5. Create admin user

#### **Grafana Setup:**
1. Access Grafana at `http://<public-ip>:3000`
2. Login with admin/admin (change password on first login)
3. Add Prometheus as data source: `http://localhost:9090`
4. Import monitoring dashboards
5. Configure AWS CloudWatch data source for AWS account monitoring

#### **Monitoring Capabilities:**
- **System Metrics**: CPU, Memory, Disk, Network usage
- **Application Metrics**: Custom application monitoring
- **AWS Account Monitoring**: CloudWatch integration for AWS services
- **Log Aggregation**: Centralized logging with CloudWatch Logs
- **Alerting**: Prometheus alerting rules and Grafana notifications
- **Dashboard Creation**: Custom dashboards for different use cases

## Secrets Manager Integration

### Retrieving Database Credentials

Database credentials are automatically stored in AWS Secrets Manager:

- **PostgreSQL Secret**: `/{project_name}/rds/postgres`
- **MySQL Secret**: `/{project_name}/rds/mysql`

### Using AWS CLI to Retrieve Credentials

**Get PostgreSQL credentials:**
```bash
aws secretsmanager get-secret-value \
  --secret-id /vpc-infrastructure/rds/postgres-20250930-1716 \
  --region us-east-1 \
  --query SecretString --output text | jq .

```

**Get MySQL credentials:**
```bash
aws secretsmanager get-secret-value \
  --secret-id /vpc-infrastructure/rds/mysql-20250930-1716 \
  --region us-east-1 \
  --query SecretString --output text | jq .

```

### Using Terraform Outputs

```bash
# Get secret ARNs
terraform output postgres_secret_arn
terraform output mysql_secret_arn

# Get secret names
terraform output postgres_secret_name
terraform output mysql_secret_name
```

## Database Credentials

### Default Credentials
- **PostgreSQL**: 
  - Username: `postgres`
  - Password: `arealisgateway`
  - Database: `postgresdb`
  - Port: `5432`

- **MySQL**:
  - Username: `admin`
  - Password: `arealisgateway`
  - Database: `mysqldb`
  - Port: `3306`

## Security Features

- **Network Isolation**: Proper separation of public/private/database subnets
- **Route Control**: Granular routing for different subnet types
- **Database Security**: Dedicated database subnets with public access
- **VPC Endpoints**: Secure access to AWS services
- **⚠️ Public Database Access**: Both databases are accessible from the internet
- **Fixed Passwords**: Both databases use "arealisgateway" as the password

## Dependencies

The configuration includes proper resource dependencies:

1. **VPC** → **Internet Gateway**
2. **VPC** → **Subnets**
3. **Internet Gateway** → **NAT Gateways**
4. **NAT Gateways** → **Private Route Tables**
5. **Subnets** → **Route Table Associations**
6. **Database Subnets** → **DB Subnet Group**

## Example Usage

### Basic VPC
```hcl
# Use default values
terraform apply
```

### Cost-Optimized VPC (Development)
```hcl
# In terraform.tfvars
single_nat_gateway = true
enable_s3_endpoint = true
enable_dynamodb_endpoint = true
```

### High Availability VPC (Production)
```hcl
# In terraform.tfvars
single_nat_gateway = false
enable_nat_gateway = true
```

### Custom VPC Configuration
```hcl
# In terraform.tfvars
vpc_cidr = "172.16.0.0/16"
public_subnet_cidrs = ["172.16.1.0/24", "172.16.2.0/24"]
private_subnet_cidrs = ["172.16.10.0/24", "172.16.20.0/24"]
database_subnet_cidrs = ["172.16.30.0/24", "172.16.40.0/24"]
```

## Resource Dependencies

The infrastructure follows proper dependency chains:

1. **VPC** → **Internet Gateway**
2. **VPC** → **Subnets** (Public, Private, Database)
3. **Internet Gateway** → **NAT Gateways**
4. **NAT Gateways** → **Private Route Tables**
5. **Subnets** → **Route Table Associations**
6. **Database Subnets** → **DB Subnet Group**

## Troubleshooting

### Common Issues

1. **Subnet CIDR conflicts**: Ensure CIDR blocks don't overlap
2. **Availability zone issues**: Verify AZs are available in your region
3. **NAT Gateway costs**: Use single NAT Gateway for development

### Useful Commands

```bash
# Check Terraform state
terraform state list

# View specific resource
terraform state show aws_vpc.main

# Refresh state
terraform refresh
```

## Support and Documentation

- [Terraform AWS Provider Documentation](https://registry.terraform.io/providers/hashicorp/aws/latest/docs)
- [AWS VPC Documentation](https://docs.aws.amazon.com/vpc/)
- [AWS Subnet Documentation](https://docs.aws.amazon.com/vpc/latest/userguide/VPC_Subnets.html)

## License

This project is provided as-is for educational and development purposes. Please review and customize according to your organization's requirements.



---
#example:


# psql command

```bash
psql \
  -h vpc-infrastructure-postgres.c4xq00w00uyw.us-east-1.rds.amazonaws.com \
  -p 5432 \
  -U postgres \
  -d postgresdb
```
```bash
arealisgateway
```
Test the connection

(or)

```bash
PGPASSWORD=arealisgateway psql \
  -h vpc-infrastructure-postgres.c4xq00w00uyw.us-east-1.rds.amazonaws.com \
  -p 5432 \
  -U postgres \
  -d postgresdb

```
Once inside psql, you can run:
```bash
SELECT current_database();
SELECT version();
```

That confirms you’re connected to postgresdb and shows the PostgreSQL version.



# 1. Using the MySQL CLI

If you have the mysql client installed:
```bash
mysql -h vpc-infrastructure-mysql.c4xq00w00uyw.us-east-1.rds.amazonaws.com \
      -P 3306 \
      -u admin \
      -p mysqldb

```
It will prompt for the password — enter:
```bash
arealisgateway
```
(or)

```bash
mysql -h vpc-infrastructure-mysql.c4xq00w00uyw.us-east-1.rds.amazonaws.com \
      -P 3306 \
      -u admin \
      -parealisgateway mysqldb
```

2. Test the connection inside MySQL

Once connected, run:
```bash
SELECT DATABASE();
SELECT VERSION();
SHOW TABLES;
```
This will confirm:

You’re connected to mysqldb.

The MySQL engine version.

Any existing tables.