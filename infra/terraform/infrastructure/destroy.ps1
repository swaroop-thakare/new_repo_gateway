# PowerShell script to destroy Terraform infrastructure in proper order

Write-Host "Starting Terraform destroy process..." -ForegroundColor Green

# Step 1: Destroy RDS instances first
Write-Host "Step 1: Destroying RDS instances..." -ForegroundColor Yellow
terraform destroy -target="aws_db_instance.mysql" -target="aws_db_instance.postgres" -auto-approve

# Step 2: Destroy EC2 instances
Write-Host "Step 2: Destroying EC2 instances..." -ForegroundColor Yellow
terraform destroy -target="aws_instance.monitoring" -auto-approve

# Step 3: Destroy NAT Gateways and EIPs
Write-Host "Step 3: Destroying NAT Gateways and EIPs..." -ForegroundColor Yellow
terraform destroy -target="aws_nat_gateway.main" -target="aws_eip.nat" -auto-approve

# Step 4: Destroy Route Tables and Associations
Write-Host "Step 4: Destroying Route Tables..." -ForegroundColor Yellow
terraform destroy -target="aws_route_table_association.public" -target="aws_route_table_association.private" -target="aws_route_table_association.database" -auto-approve
terraform destroy -target="aws_route_table.public" -target="aws_route_table.private" -target="aws_route_table.database" -auto-approve

# Step 5: Destroy Subnets
Write-Host "Step 5: Destroying Subnets..." -ForegroundColor Yellow
terraform destroy -target="aws_subnet.public" -target="aws_subnet.private" -target="aws_subnet.database" -auto-approve

# Step 6: Destroy Security Groups
Write-Host "Step 6: Destroying Security Groups..." -ForegroundColor Yellow
terraform destroy -target="aws_security_group.monitoring" -target="aws_security_group.rds" -auto-approve

# Step 7: Destroy DB Subnet Group
Write-Host "Step 7: Destroying DB Subnet Group..." -ForegroundColor Yellow
terraform destroy -target="aws_db_subnet_group.main" -auto-approve

# Step 8: Destroy Internet Gateway
Write-Host "Step 8: Destroying Internet Gateway..." -ForegroundColor Yellow
terraform destroy -target="aws_internet_gateway.main" -auto-approve

# Step 9: Destroy VPC
Write-Host "Step 9: Destroying VPC..." -ForegroundColor Yellow
terraform destroy -target="aws_vpc.main" -auto-approve

# Step 10: Destroy remaining resources
Write-Host "Step 10: Destroying remaining resources..." -ForegroundColor Yellow
terraform destroy -auto-approve

Write-Host "Destroy process completed!" -ForegroundColor Green
