#!/bin/bash
# Terraform destroy script with proper order

echo "Starting Terraform destroy process..."

# Step 1: Destroy RDS instances first
echo "Step 1: Destroying RDS instances..."
terraform destroy -target=aws_db_instance.mysql -target=aws_db_instance.postgres -auto-approve

# Step 2: Destroy EC2 instances
echo "Step 2: Destroying EC2 instances..."
terraform destroy -target=aws_instance.monitoring -auto-approve

# Step 3: Destroy NAT Gateways and EIPs
echo "Step 3: Destroying NAT Gateways and EIPs..."
terraform destroy -target=aws_nat_gateway.main -target=aws_eip.nat -auto-approve

# Step 4: Destroy Route Tables and Associations
echo "Step 4: Destroying Route Tables..."
terraform destroy -target=aws_route_table_association.public -target=aws_route_table_association.private -target=aws_route_table_association.database -auto-approve
terraform destroy -target=aws_route_table.public -target=aws_route_table.private -target=aws_route_table.database -auto-approve

# Step 5: Destroy Subnets
echo "Step 5: Destroying Subnets..."
terraform destroy -target=aws_subnet.public -target=aws_subnet.private -target=aws_subnet.database -auto-approve

# Step 6: Destroy Security Groups
echo "Step 6: Destroying Security Groups..."
terraform destroy -target=aws_security_group.monitoring -target=aws_security_group.rds -auto-approve

# Step 7: Destroy DB Subnet Group
echo "Step 7: Destroying DB Subnet Group..."
terraform destroy -target=aws_db_subnet_group.main -auto-approve

# Step 8: Destroy Internet Gateway
echo "Step 8: Destroying Internet Gateway..."
terraform destroy -target=aws_internet_gateway.main -auto-approve

# Step 9: Destroy VPC
echo "Step 9: Destroying VPC..."
terraform destroy -target=aws_vpc.main -auto-approve

# Step 10: Destroy remaining resources
echo "Step 10: Destroying remaining resources..."
terraform destroy -auto-approve

echo "Destroy process completed!"
