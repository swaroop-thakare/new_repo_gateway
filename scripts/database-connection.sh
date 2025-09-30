#!/bin/bash

# Database Connection Script for Arealis Gateway
# This script helps connect to PostgreSQL and MySQL RDS instances from EC2

# Database connection details
POSTGRES_HOST="vpc-infrastructure-postgres.c4xq00w00uyw.us-east-1.rds.amazonaws.com"
POSTGRES_PORT="5432"
POSTGRES_DB="postgresdb"
POSTGRES_USER="postgres"
POSTGRES_PASSWORD="arealisgateway"

MYSQL_HOST="vpc-infrastructure-mysql.c4xq00w00uyw.us-east-1.rds.amazonaws.com"
MYSQL_PORT="3306"
MYSQL_DB="mysqldb"
MYSQL_USER="admin"
MYSQL_PASSWORD="arealisgateway"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}=== Arealis Gateway Database Connection Script ===${NC}"
echo ""

# Function to check if required tools are installed
check_dependencies() {
    echo -e "${YELLOW}Checking dependencies...${NC}"
    
    # Check for PostgreSQL client
    if ! command -v psql &> /dev/null; then
        echo -e "${RED}PostgreSQL client (psql) not found. Installing...${NC}"
        sudo yum update -y
        sudo yum install -y postgresql15
    else
        echo -e "${GREEN}✓ PostgreSQL client found${NC}"
    fi
    
    # Check for MySQL client
    if ! command -v mysql &> /dev/null; then
        echo -e "${RED}MySQL client not found. Installing...${NC}"
        sudo yum install -y mysql
    else
        echo -e "${GREEN}✓ MySQL client found${NC}"
    fi
    
    echo ""
}

# Function to test PostgreSQL connection
test_postgres_connection() {
    echo -e "${YELLOW}Testing PostgreSQL connection...${NC}"
    
    export PGPASSWORD="$POSTGRES_PASSWORD"
    
    if psql -h "$POSTGRES_HOST" -p "$POSTGRES_PORT" -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c "SELECT version();" &> /dev/null; then
        echo -e "${GREEN}✓ PostgreSQL connection successful!${NC}"
        echo "Host: $POSTGRES_HOST"
        echo "Port: $POSTGRES_PORT"
        echo "Database: $POSTGRES_DB"
        echo "User: $POSTGRES_USER"
        return 0
    else
        echo -e "${RED}✗ PostgreSQL connection failed${NC}"
        return 1
    fi
}

# Function to test MySQL connection
test_mysql_connection() {
    echo -e "${YELLOW}Testing MySQL connection...${NC}"
    
    if mysql -h "$MYSQL_HOST" -P "$MYSQL_PORT" -u "$MYSQL_USER" -p"$MYSQL_PASSWORD" -e "SELECT VERSION();" &> /dev/null; then
        echo -e "${GREEN}✓ MySQL connection successful!${NC}"
        echo "Host: $MYSQL_HOST"
        echo "Port: $MYSQL_PORT"
        echo "Database: $MYSQL_DB"
        echo "User: $MYSQL_USER"
        return 0
    else
        echo -e "${RED}✗ MySQL connection failed${NC}"
        return 1
    fi
}

# Function to create connection environment file
create_env_file() {
    echo -e "${YELLOW}Creating environment file for applications...${NC}"
    
    cat > /home/ec2-user/.env << EOF
# PostgreSQL Configuration
POSTGRES_HOST=$POSTGRES_HOST
POSTGRES_PORT=$POSTGRES_PORT
POSTGRES_DB=$POSTGRES_DB
POSTGRES_USER=$POSTGRES_USER
POSTGRES_PASSWORD=$POSTGRES_PASSWORD
POSTGRES_URL=postgresql://$POSTGRES_USER:$POSTGRES_PASSWORD@$POSTGRES_HOST:$POSTGRES_PORT/$POSTGRES_DB

# MySQL Configuration
MYSQL_HOST=$MYSQL_HOST
MYSQL_PORT=$MYSQL_PORT
MYSQL_DB=$MYSQL_DB
MYSQL_USER=$MYSQL_USER
MYSQL_PASSWORD=$MYSQL_PASSWORD
MYSQL_URL=mysql://$MYSQL_USER:$MYSQL_PASSWORD@$MYSQL_HOST:$MYSQL_PORT/$MYSQL_DB

# Application Configuration
NODE_ENV=production
LOG_LEVEL=info
EOF

    echo -e "${GREEN}✓ Environment file created at /home/ec2-user/.env${NC}"
}

# Function to create Python connection script
create_python_script() {
    echo -e "${YELLOW}Creating Python database connection script...${NC}"
    
    cat > /home/ec2-user/db_connection.py << 'EOF'
#!/usr/bin/env python3
"""
Database Connection Script for Arealis Gateway
Supports both PostgreSQL and MySQL connections
"""

import os
import sys
from urllib.parse import urlparse

# Database configuration
DB_CONFIG = {
    'postgres': {
        'host': 'vpc-infrastructure-postgres.c4xq00w00uyw.us-east-1.rds.amazonaws.com',
        'port': 5432,
        'database': 'postgresdb',
        'user': 'postgres',
        'password': 'arealisgateway'
    },
    'mysql': {
        'host': 'vpc-infrastructure-mysql.c4xq00w00uyw.us-east-1.rds.amazonaws.com',
        'port': 3306,
        'database': 'mysqldb',
        'user': 'admin',
        'password': 'arealisgateway'
    }
}

def test_postgres_connection():
    """Test PostgreSQL connection"""
    try:
        import psycopg2
        conn = psycopg2.connect(
            host=DB_CONFIG['postgres']['host'],
            port=DB_CONFIG['postgres']['port'],
            database=DB_CONFIG['postgres']['database'],
            user=DB_CONFIG['postgres']['user'],
            password=DB_CONFIG['postgres']['password']
        )
        cursor = conn.cursor()
        cursor.execute("SELECT version();")
        version = cursor.fetchone()
        print(f"✓ PostgreSQL connection successful!")
        print(f"  Version: {version[0]}")
        cursor.close()
        conn.close()
        return True
    except ImportError:
        print("✗ psycopg2 not installed. Install with: pip install psycopg2-binary")
        return False
    except Exception as e:
        print(f"✗ PostgreSQL connection failed: {e}")
        return False

def test_mysql_connection():
    """Test MySQL connection"""
    try:
        import pymysql
        conn = pymysql.connect(
            host=DB_CONFIG['mysql']['host'],
            port=DB_CONFIG['mysql']['port'],
            database=DB_CONFIG['mysql']['database'],
            user=DB_CONFIG['mysql']['user'],
            password=DB_CONFIG['mysql']['password']
        )
        cursor = conn.cursor()
        cursor.execute("SELECT VERSION();")
        version = cursor.fetchone()
        print(f"✓ MySQL connection successful!")
        print(f"  Version: {version[0]}")
        cursor.close()
        conn.close()
        return True
    except ImportError:
        print("✗ pymysql not installed. Install with: pip install pymysql")
        return False
    except Exception as e:
        print(f"✗ MySQL connection failed: {e}")
        return False

def main():
    print("=== Arealis Gateway Database Connection Test ===")
    print()
    
    # Test PostgreSQL
    print("Testing PostgreSQL connection...")
    postgres_ok = test_postgres_connection()
    print()
    
    # Test MySQL
    print("Testing MySQL connection...")
    mysql_ok = test_mysql_connection()
    print()
    
    if postgres_ok and mysql_ok:
        print("✓ All database connections successful!")
        return 0
    else:
        print("✗ Some database connections failed!")
        return 1

if __name__ == "__main__":
    sys.exit(main())
EOF

    chmod +x /home/ec2-user/db_connection.py
    echo -e "${GREEN}✓ Python script created at /home/ec2-user/db_connection.py${NC}"
}

# Main execution
main() {
    echo "Starting database connection setup..."
    echo ""
    
    # Check dependencies
    check_dependencies
    
    # Test connections
    echo -e "${BLUE}=== Testing Database Connections ===${NC}"
    test_postgres_connection
    echo ""
    test_mysql_connection
    echo ""
    
    # Create configuration files
    echo -e "${BLUE}=== Creating Configuration Files ===${NC}"
    create_env_file
    create_python_script
    
    echo ""
    echo -e "${GREEN}=== Setup Complete! ===${NC}"
    echo "Environment file: /home/ec2-user/.env"
    echo "Python script: /home/ec2-user/db_connection.py"
    echo ""
    echo "To test connections manually:"
    echo "  PostgreSQL: psql -h $POSTGRES_HOST -p $POSTGRES_PORT -U $POSTGRES_USER -d $POSTGRES_DB"
    echo "  MySQL: mysql -h $MYSQL_HOST -P $MYSQL_PORT -u $MYSQL_USER -p$MYSQL_PASSWORD"
    echo "  Python: python3 /home/ec2-user/db_connection.py"
}

# Run main function
main
