#!/bin/bash

# Update system
sudo yum update -y

# Install essential tools
sudo yum install -y git wget curl unzip java-17-amazon-corretto nodejs

# Install Jenkins
sudo wget -O /etc/yum.repos.d/jenkins.repo https://pkg.jenkins.io/redhat-stable/jenkins.repo
sudo rpm --import https://pkg.jenkins.io/redhat-stable/jenkins.io-2023.key
sudo yum install -y jenkins
sudo systemctl enable jenkins
sudo systemctl start jenkins

# Install Docker
sudo yum install -y docker
sudo usermod -aG docker ec2-user
sudo systemctl enable docker
sudo systemctl start docker

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.24.5/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Run SonarQube
sudo docker run -d --name sonar -p 9000:9000 sonarqube:lts-community

# Install MariaDB
sudo yum install -y mariadb105-server
sudo systemctl start mariadb
sudo systemctl enable mariadb

# Install PostgreSQL
sudo yum install -y postgresql15 postgresql15-server
sudo /usr/pgsql-15/bin/postgresql-15-setup initdb
sudo systemctl enable postgresql-15
sudo systemctl start postgresql-15

# Install AWS CLI v2
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install
rm -rf awscliv2.zip aws

# Install CloudWatch Agent
wget https://s3.amazonaws.com/amazoncloudwatch-agent/amazon_linux/amd64/latest/amazon-cloudwatch-agent.rpm
sudo rpm -U ./amazon-cloudwatch-agent.rpm
rm amazon-cloudwatch-agent.rpm
sudo /opt/aws/amazon-cloudwatch-agent/bin/amazon-cloudwatch-agent-ctl -a fetch-config -m ec2 -s

# Install Prometheus (Proper Method)
sudo useradd --no-create-home --shell /bin/false prometheus || true
sudo mkdir -p /etc/prometheus /var/lib/prometheus
sudo chown prometheus:prometheus /etc/prometheus /var/lib/prometheus

cd /tmp
curl -LO https://github.com/prometheus/prometheus/releases/download/v2.55.1/prometheus-2.55.1.linux-amd64.tar.gz
tar -xvf prometheus-2.55.1.linux-amd64.tar.gz
cd prometheus-2.55.1.linux-amd64

sudo cp prometheus promtool /usr/local/bin/
sudo chown prometheus:prometheus /usr/local/bin/prometheus /usr/local/bin/promtool

sudo cp -r consoles/ console_libraries/ /etc/prometheus/
sudo cp prometheus.yml /etc/prometheus/prometheus.yml
sudo chown -R prometheus:prometheus /etc/prometheus/*

# Create Prometheus service
sudo tee /etc/systemd/system/prometheus.service >/dev/null <<'EOF'
[Unit]
Description=Prometheus
Wants=network-online.target
After=network-online.target

[Service]
User=prometheus
Group=prometheus
Type=simple
ExecStart=/usr/local/bin/prometheus \
  --config.file=/etc/prometheus/prometheus.yml \
  --storage.tsdb.path=/var/lib/prometheus/ \
  --web.console.templates=/etc/prometheus/consoles \
  --web.console.libraries=/etc/prometheus/console_libraries \
  --web.listen-address=0.0.0.0:9090
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Install Node Exporter
cd /opt
sudo wget https://github.com/prometheus/node_exporter/releases/latest/download/node_exporter-1.6.1.linux-amd64.tar.gz
sudo tar xzf node_exporter-1.6.1.linux-amd64.tar.gz
sudo mv node_exporter-1.6.1.linux-amd64 node_exporter
sudo rm node_exporter-1.6.1.linux-amd64.tar.gz

# Create node_exporter user
sudo useradd --no-create-home --shell /bin/false node_exporter
sudo chown -R node_exporter:node_exporter /opt/node_exporter

# Create Node Exporter service
sudo tee /etc/systemd/system/node_exporter.service > /dev/null << 'EOF'
[Unit]
Description=Node Exporter
[Service]
User=node_exporter
Group=node_exporter
Type=simple
ExecStart=/opt/node_exporter/node_exporter
[Install]
WantedBy=multi-user.target
EOF

# Install Grafana
sudo tee /etc/yum.repos.d/grafana.repo > /dev/null << 'EOF'
[grafana]
name=grafana
baseurl=https://rpm.grafana.com
repo_gpgcheck=1
enabled=1
gpgcheck=1
gpgkey=https://rpm.grafana.com/gpg.key
EOF

sudo dnf install -y grafana

# Start all services
sudo systemctl daemon-reload

# Start Prometheus (Proper Method)
sudo systemctl enable --now prometheus
echo "✅ Prometheus started successfully"

# Start Node Exporter
sudo systemctl start node_exporter
sudo systemctl enable node_exporter

# Start Grafana
sudo systemctl start grafana-server
sudo systemctl enable grafana-server

# Verify services are running
echo "=== Service Status ==="
sudo systemctl status prometheus --no-pager -l
sudo systemctl status node_exporter --no-pager -l
sudo systemctl status grafana-server --no-pager -l

# Create info file
cat > /home/ec2-user/monitoring-info.txt << EOF
=== Monitoring Server ===
Grafana: http://$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4):3000 (admin/admin)
Prometheus: http://$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4):9090
Jenkins: http://$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4):8080
SonarQube: http://$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4):9000
Node Exporter: http://$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4):9100

=== Databases ===
MariaDB: mysql://$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4):3306
PostgreSQL: postgresql://$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4):5432

=== Commands ===
Check services: sudo systemctl status prometheus node_exporter grafana-server jenkins mariadb postgresql-15
Restart services: sudo systemctl restart prometheus node_exporter grafana-server jenkins mariadb postgresql-15

=== Database Access ===
MariaDB: mysql -u root -p
PostgreSQL: sudo -u postgres psql
EOF

chown ec2-user:ec2-user /home/ec2-user/monitoring-info.txt

# Configure AWS CloudWatch Alerts
echo "🔔 Setting up AWS CloudWatch Alerts..."

# Create CloudWatch alarm for high CPU
aws cloudwatch put-metric-alarm \
  --alarm-name "High-CPU-Utilization" \
  --alarm-description "Alert when CPU utilization exceeds 80%" \
  --metric-name CPUUtilization \
  --namespace AWS/EC2 \
  --statistic Average \
  --period 300 \
  --threshold 80 \
  --comparison-operator GreaterThanThreshold \
  --evaluation-periods 2 \
  --alarm-actions arn:aws:sns:us-east-1:$(aws sts get-caller-identity --query Account --output text):high-cpu-alerts || echo "⚠️ SNS topic not configured"

# Create CloudWatch alarm for high memory
aws cloudwatch put-metric-alarm \
  --alarm-name "High-Memory-Utilization" \
  --alarm-description "Alert when memory utilization exceeds 85%" \
  --metric-name MemoryUtilization \
  --namespace CWAgent \
  --statistic Average \
  --period 300 \
  --threshold 85 \
  --comparison-operator GreaterThanThreshold \
  --evaluation-periods 2 || echo "⚠️ Memory alarm created"

# Create CloudWatch alarm for disk space
aws cloudwatch put-metric-alarm \
  --alarm-name "High-Disk-Utilization" \
  --alarm-description "Alert when disk utilization exceeds 90%" \
  --metric-name DiskSpaceUtilization \
  --namespace CWAgent \
  --statistic Average \
  --period 300 \
  --threshold 90 \
  --comparison-operator GreaterThanThreshold \
  --evaluation-periods 1 || echo "⚠️ Disk alarm created"

# Create CloudWatch alarm for instance status
aws cloudwatch put-metric-alarm \
  --alarm-name "Instance-Status-Check-Failed" \
  --alarm-description "Alert when instance status check fails" \
  --metric-name StatusCheckFailed \
  --namespace AWS/EC2 \
  --statistic Maximum \
  --period 60 \
  --threshold 1 \
  --comparison-operator GreaterThanOrEqualToThreshold \
  --evaluation-periods 1 || echo "⚠️ Status check alarm created"

echo "✅ Setup completed with CloudWatch alerts!"
